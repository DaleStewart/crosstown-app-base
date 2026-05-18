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
};

type Action =
  | { type: "status"; status: SessionStatus }
  | { type: "error"; message: string }
  | { type: "frame"; frame: ServerMessage }
  | { type: "recording"; value: boolean }
  | { type: "reset" }
  | { type: "awaiting"; value: boolean }
  | { type: "append_user"; text: string }
  | { type: "append_assistant"; text: string; citations: Citation[]; warnings: string[] };

const initial: State = {
  status: "idle",
  transcripts: [],
  toolCalls: [],
  error: null,
  recording: false,
  awaitingResponse: false,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "status":
      return { ...state, status: action.status };
    case "error":
      return { ...state, status: "error", error: action.message, awaitingResponse: false };
    case "recording":
      return { ...state, recording: action.value };
    case "reset":
      return initial;
    case "awaiting":
      return { ...state, awaitingResponse: action.value };
    case "frame":
      return applyFrame(state, action.frame);
    case "append_user":
      return {
        ...state,
        awaitingResponse: true,
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
          transcripts: [...state.transcripts.slice(0, -1), merged],
        };
      }
      return {
        ...state,
        awaitingResponse: awaitingAfterUser,
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
        return { ...state, awaitingResponse: false };
      }
      if (frame.text) {
        return {
          ...state,
          awaitingResponse: false,
          transcripts: [
            ...state.transcripts,
            { id: cryptoId(), role: "assistant", text: frame.text, final: true },
          ],
        };
      }
      return { ...state, awaitingResponse: false };
    }
    case "error":
      return { ...state, error: frame.message, status: "error", awaitingResponse: false };
    case "audio_delta":
      // First audio chunk from the assistant also implies streaming has begun.
      return state.awaitingResponse ? { ...state, awaitingResponse: false } : state;
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

  return { state, connect, disconnect, startTalking, stopTalking, sendText, appendUserTurn, appendAssistantTurn };
}
