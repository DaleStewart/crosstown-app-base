import { useCallback, useEffect, useReducer, useRef } from "react";
import {
  type Citation,
  type ClientMessage,
  type ServerMessage,
  parseServerMessage,
} from "@/lib/protocol";
import { AudioPlayer, startMic, type MicSession } from "@/lib/audio";

export type TranscriptLine = {
  id: string;
  role: "user" | "assistant";
  text: string;
  final: boolean;
};

export type ToolCallEntry = {
  call_id: string;
  name: string;
  args: Record<string, unknown>;
  citations: Citation[];
  warnings: string[];
  pending: boolean;
};

export type SessionStatus = "idle" | "connecting" | "connected" | "error";

type State = {
  status: SessionStatus;
  transcripts: TranscriptLine[];
  toolCalls: ToolCallEntry[];
  error: string | null;
  recording: boolean;
  awaitingResponse: boolean;
  /** True from the first assistant frame of a response until the matching
   *  `final` arrives OR the user cancels. Drives the visibility of the on-
   *  screen stop button — see App.tsx. */
  streaming: boolean;
};

type Action =
  | { type: "status"; status: SessionStatus }
  | { type: "error"; message: string }
  | { type: "frame"; frame: ServerMessage }
  | { type: "recording"; value: boolean }
  | { type: "reset" }
  | { type: "awaiting"; value: boolean }
  | { type: "cancelled" }
  | { type: "append_user"; text: string }
  | { type: "append_assistant"; text: string; citations: Citation[]; warnings: string[] };

const initial: State = {
  status: "idle",
  transcripts: [],
  toolCalls: [],
  error: null,
  recording: false,
  awaitingResponse: false,
  streaming: false,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "status":
      return { ...state, status: action.status };
    case "error":
      return { ...state, status: "error", error: action.message, awaitingResponse: false, streaming: false };
    case "recording":
      return { ...state, recording: action.value };
    case "reset":
      return initial;
    case "awaiting":
      return { ...state, awaitingResponse: action.value };
    case "cancelled":
      // The orchestrator (or the user-side optimistic action) cancelled the
      // in-flight response. Clear both awaiting + streaming so the UI returns
      // to idle. We leave existing transcripts as-is — the partial assistant
      // text the user already saw is intentionally preserved so they have
      // context for what they cut off.
      return { ...state, awaitingResponse: false, streaming: false };
    case "frame":
      return applyFrame(state, action.frame);
    case "append_user":
      return {
        ...state,
        awaitingResponse: true,
        // For the TextInput path (where there is no WS streaming voice),
        // also flip `streaming` true so TextInput's `busy` prop becomes truthy
        // and blocks overlapping submits. Cleared in
        // `append_assistant` / `cancelled` / `error`.
        streaming: true,
        transcripts: [
          ...state.transcripts,
          { id: cryptoId(), role: "user", text: action.text, final: true },
        ],
      };
    case "append_assistant": {
      const citations = action.citations ?? [];
      const warnings = action.warnings ?? [];
      const newToolCalls =
        citations.length > 0 || warnings.length > 0
          ? [
              ...state.toolCalls,
              {
                call_id: cryptoId(),
                name: "api/turn",
                args: {},
                citations,
                warnings,
                pending: false,
              },
            ]
          : state.toolCalls;
      return {
        ...state,
        awaitingResponse: false,
        streaming: false,
        transcripts: [
          ...state.transcripts,
          { id: cryptoId(), role: "assistant", text: action.text, final: true },
        ],
        toolCalls: newToolCalls,
      };
    }
  }
}

function applyFrame(state: State, frame: ServerMessage): State {
  switch (frame.type) {
    case "transcript_delta": {
      // Assistant began streaming — clear the thinking placeholder.
      const nextAwaiting =
        frame.role === "assistant" ? false : state.awaitingResponse;
      // A finalized user transcript means the user just committed a voice turn
      // and we're now waiting on the assistant. Flip awaiting on so the
      // thinking indicator appears even when no client-side commit happened
      // (e.g. continuous-mode voice with server VAD).
      const awaitingAfterUser =
        frame.role === "user" && frame.final ? true : nextAwaiting;
      // Streaming bit: any non-final assistant transcript_delta means a
      // response is actively flowing → show the stop button. A final assistant
      // delta also implies the response is winding down; the matching `final`
      // frame will clear `streaming` for good.
      const nextStreaming =
        frame.role === "assistant" && !frame.final ? true : state.streaming;
      const last = state.transcripts[state.transcripts.length - 1];
      if (last && last.role === frame.role && !last.final) {
        const merged: TranscriptLine = {
          ...last,
          text: frame.final ? frame.text || last.text : last.text + frame.text,
          final: frame.final,
        };
        return {
          ...state,
          awaitingResponse: awaitingAfterUser,
          streaming: nextStreaming,
          transcripts: [...state.transcripts.slice(0, -1), merged],
        };
      }
      return {
        ...state,
        awaitingResponse: awaitingAfterUser,
        streaming: nextStreaming,
        transcripts: [
          ...state.transcripts,
          {
            id: cryptoId(),
            role: frame.role,
            text: frame.text,
            final: frame.final,
          },
        ],
      };
    }
    case "tool_call":
      return {
        ...state,
        toolCalls: [
          ...state.toolCalls,
          {
            call_id: frame.call_id,
            name: frame.name,
            args: frame.args,
            citations: [],
            warnings: [],
            pending: true,
          },
        ],
      };
    case "tool_result":
      return {
        ...state,
        toolCalls: state.toolCalls.map((tc) =>
          tc.name === frame.name && tc.pending
            ? {
                ...tc,
                citations: frame.citations ?? [],
                warnings: frame.warnings ?? [],
                pending: false,
              }
            : tc
        ),
      };
    case "final": {
      const last = state.transcripts[state.transcripts.length - 1];
      if (last && last.role === "assistant" && !last.final && frame.text) {
        return {
          ...state,
          awaitingResponse: false,
          streaming: false,
          transcripts: [
            ...state.transcripts.slice(0, -1),
            { ...last, text: frame.text, final: true },
          ],
        };
      }
      // Belt-and-suspenders dedupe: if the last assistant bubble is already
      // finalized with matching text, this is the redundant `final` frame
      // Foundry GA emits after response.output_audio_transcript.done. The
      // orchestrator now strips the text in this case, but if any other
      // provider echoes the same text back we still avoid a duplicate bubble.
      if (
        frame.text &&
        last &&
        last.role === "assistant" &&
        last.final &&
        last.text === frame.text
      ) {
        return { ...state, awaitingResponse: false, streaming: false };
      }
      if (frame.text) {
        return {
          ...state,
          awaitingResponse: false,
          streaming: false,
          transcripts: [
            ...state.transcripts,
            { id: cryptoId(), role: "assistant", text: frame.text, final: true },
          ],
        };
      }
      return { ...state, awaitingResponse: false, streaming: false };
    }
    case "error":
      return { ...state, error: frame.message, status: "error", awaitingResponse: false, streaming: false };
    case "audio_delta":
      // First audio chunk from the assistant also implies streaming has begun.
      return state.streaming && !state.awaitingResponse
        ? state
        : { ...state, awaitingResponse: false, streaming: true };
    case "response_cancelled":
      // Server confirmed the cancel landed. Clear streaming/awaiting; the UI
      // returns to idle and the stop button hides.
      return { ...state, awaitingResponse: false, streaming: false };
    case "user_transcript": {
      // Append a finalized user-turn line from Wanda's server-side transcription.
      if (!frame.text) return state;
      return {
        ...state,
        awaitingResponse: true,
        transcripts: [
          ...state.transcripts,
          { id: cryptoId(), role: "user", text: frame.text, final: true },
        ],
      };
    }
  }
}

function cryptoId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2);
}

export type UseVoiceSession = {
  state: State;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  startTalking: () => Promise<void>;
  stopTalking: () => Promise<void>;
  sendText: (text: string) => void;
  /** Internal cancel: drains local audio and aborts any in-flight /api/turn
   *  fetch. Used by `sendUserText` as the abort plumbing — no longer wired to
   *  a UI control after the StopButton was removed (2026-05-18). The
   *  orchestrator's own auto-cancel-on-new-turn state machine handles
   *  barge-in cancellation server-side. */
  cancelResponse: () => void;
  /** Submit a text-input turn to /api/turn through the hook (instead of from
   *  TextInput directly). Owning this here lets cancelResponse() abort the
   *  in-flight fetch AND keeps `streaming` reflecting text requests too —
   *  TextInput's `busy` prop reads `streaming || awaitingResponse` to
   *  prevent overlapping submits. Resolves with the assistant text on
   *  success, with `null` if the request was cancelled. */
  sendUserText: (text: string) => Promise<string | null>;
  appendUserTurn: (text: string) => void;
  appendAssistantTurn: (payload: { text: string; citations: Citation[]; warnings: string[] }) => void;
};

const DEFAULT_ORCHESTRATOR_WS =
  typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws/voice`
    : "ws://localhost:8000/ws/voice";

export function useVoiceSession(
  options: { url?: string; mode?: "push_to_talk" | "continuous" } = {}
): UseVoiceSession {
  const [state, dispatch] = useReducer(reducer, initial);
  const wsRef = useRef<WebSocket | null>(null);
  const micRef = useRef<MicSession | null>(null);
  const playerRef = useRef<AudioPlayer>(new AudioPlayer());
  // AbortController for any in-flight /api/turn fetch. Held in a ref so
  // cancelResponse() can abort regardless of which call started the request.
  const textAbortRef = useRef<AbortController | null>(null);
  const mode = options.mode ?? "push_to_talk";
  const url = options.url ?? DEFAULT_ORCHESTRATOR_WS;

  const handleMessage = useCallback((data: string) => {
    const parsed = parseServerMessage(data);
    if (!parsed) return;
    if (parsed.type === "audio_delta") {
      playerRef.current.enqueuePcm16(parsed.audio_b64);
    }
    dispatch({ type: "frame", frame: parsed });
  }, []);

  const connect = useCallback(async (): Promise<void> => {
    if (wsRef.current) return;
    dispatch({ type: "status", status: "connecting" });
    const ws = new WebSocket(url);
    ws.binaryType = "arraybuffer";
    ws.onopen = (): void => {
      const start: ClientMessage = {
        type: "start",
        conversationId: null,
        mode,
      };
      ws.send(JSON.stringify(start));
      dispatch({ type: "status", status: "connected" });
    };
    ws.onmessage = (ev: MessageEvent): void => {
      if (typeof ev.data === "string") handleMessage(ev.data);
    };
    ws.onerror = (): void => {
      dispatch({ type: "error", message: "websocket error" });
    };
    ws.onclose = (): void => {
      wsRef.current = null;
      dispatch({ type: "status", status: "idle" });
    };
    wsRef.current = ws;
  }, [handleMessage, mode, url]);

  const send = useCallback((msg: ClientMessage): void => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify(msg));
  }, []);

  const sendText = useCallback(
    (text: string): void => {
      send({ type: "text", text });
      dispatch({ type: "awaiting", value: true });
    },
    [send]
  );

  const startTalking = useCallback(async (): Promise<void> => {
    if (!wsRef.current) await connect();
    if (micRef.current) return;
    dispatch({ type: "recording", value: true });
    micRef.current = await startMic((pcm) => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) ws.send(pcm);
    });
  }, [connect]);

  const stopTalking = useCallback(async (): Promise<void> => {
    if (micRef.current) {
      await micRef.current.stop();
      micRef.current = null;
    }
    send({ type: "stop" });
    dispatch({ type: "recording", value: false });
    // User just released the mic — we're now waiting on the assistant.
    // The indicator clears as soon as the first assistant frame arrives.
    dispatch({ type: "awaiting", value: true });
  }, [send]);

  const disconnect = useCallback(async (): Promise<void> => {
    await stopTalking();
    if (wsRef.current) {
      try {
        send({ type: "stop" });
      } catch {
        /* noop */
      }
      wsRef.current.close();
      wsRef.current = null;
    }
    dispatch({ type: "reset" });
  }, [send, stopTalking]);

  useEffect(() => {
    return () => {
      void disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const appendUserTurn = useCallback(
    (text: string): void => dispatch({ type: "append_user", text }),
    []
  );

  const appendAssistantTurn = useCallback(
    (payload: { text: string; citations: Citation[]; warnings: string[] }): void =>
      dispatch({ type: "append_assistant", ...payload }),
    []
  );

  const cancelResponse = useCallback((): void => {
    // Drain local audio so any buffered playback stops immediately.
    playerRef.current.stop();
    // Abort any in-flight /api/turn fetch (TextInput path). The fetch
    // rejection in sendUserText will be caught and treated as cancelled.
    if (textAbortRef.current) {
      textAbortRef.current.abort();
      textAbortRef.current = null;
    }
    // NOTE: we deliberately do NOT send `cancel_response` to the orchestrator
    // anymore (StopButton removed 2026-05-18). Server-side auto-cancel on the
    // next user turn handles barge-in. Keeping this function in the hook so
    // sendUserText's abort plumbing has a single entry point.
    dispatch({ type: "cancelled" });
  }, []);

  const sendUserText = useCallback(
    async (text: string): Promise<string | null> => {
      const trimmed = text.trim();
      if (!trimmed) return null;
      // Cancel any prior in-flight text request (the form prevents this in
      // normal use, but be defensive).
      if (textAbortRef.current) {
        textAbortRef.current.abort();
      }
      const controller = new AbortController();
      textAbortRef.current = controller;

      // Optimistic: append user line + flip streaming on (drives TextInput busy).
      dispatch({ type: "append_user", text: trimmed });
      try {
        const res = await fetch("/api/turn", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: trimmed }),
          signal: controller.signal,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
        const data = (await res.json()) as {
          text: string;
          citations?: Citation[];
          warnings?: string[];
        };
        // Race guard: if cancelResponse() fired while the fetch was resolving,
        // the controller is now null/replaced. Don't append the assistant
        // turn we cancelled.
        if (textAbortRef.current !== controller) return null;
        textAbortRef.current = null;
        dispatch({
          type: "append_assistant",
          text: data.text,
          citations: data.citations ?? [],
          warnings: data.warnings ?? [],
        });
        return data.text;
      } catch (err) {
        if (controller.signal.aborted) {
          // Cancelled by user; cancelResponse() already dispatched 'cancelled'.
          return null;
        }
        if (textAbortRef.current === controller) textAbortRef.current = null;
        dispatch({
          type: "append_assistant",
          text: `[Error] ${err instanceof Error ? err.message : String(err)}`,
          citations: [],
          warnings: ["error"],
        });
        return null;
      }
    },
    []
  );

  return { state, connect, disconnect, startTalking, stopTalking, sendText, cancelResponse, sendUserText, appendUserTurn, appendAssistantTurn };
}
