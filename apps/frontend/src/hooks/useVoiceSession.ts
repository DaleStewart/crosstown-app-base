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
};

type Action =
  | { type: "status"; status: SessionStatus }
  | { type: "error"; message: string }
  | { type: "frame"; frame: ServerMessage }
  | { type: "recording"; value: boolean }
  | { type: "reset" }
  | { type: "append_user"; text: string }
  | { type: "append_assistant"; text: string; citations: Citation[]; warnings: string[] };

const initial: State = {
  status: "idle",
  transcripts: [],
  toolCalls: [],
  error: null,
  recording: false,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "status":
      return { ...state, status: action.status };
    case "error":
      return { ...state, status: "error", error: action.message };
    case "recording":
      return { ...state, recording: action.value };
    case "reset":
      return initial;
    case "frame":
      return applyFrame(state, action.frame);
    case "append_user":
      return {
        ...state,
        transcripts: [
          ...state.transcripts,
          { id: cryptoId(), role: "user", text: action.text, final: true },
        ],
      };
    case "append_assistant": {
      const newToolCalls =
        action.citations.length > 0 || action.warnings.length > 0
          ? [
              ...state.toolCalls,
              {
                call_id: cryptoId(),
                name: "api/turn",
                args: {},
                citations: action.citations,
                warnings: action.warnings,
                pending: false,
              },
            ]
          : state.toolCalls;
      return {
        ...state,
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
      const last = state.transcripts[state.transcripts.length - 1];
      if (last && last.role === frame.role && !last.final) {
        const merged: TranscriptLine = {
          ...last,
          text: frame.final ? frame.text || last.text : last.text + frame.text,
          final: frame.final,
        };
        return {
          ...state,
          transcripts: [...state.transcripts.slice(0, -1), merged],
        };
      }
      return {
        ...state,
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
                citations: frame.citations,
                warnings: frame.warnings,
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
          transcripts: [
            ...state.transcripts.slice(0, -1),
            { ...last, text: frame.text, final: true },
          ],
        };
      }
      if (frame.text) {
        return {
          ...state,
          transcripts: [
            ...state.transcripts,
            { id: cryptoId(), role: "assistant", text: frame.text, final: true },
          ],
        };
      }
      return state;
    }
    case "error":
      return { ...state, error: frame.message, status: "error" };
    case "audio_delta":
      return state;
    case "user_transcript": {
      // Append a finalized user-turn line from Wanda's server-side transcription.
      if (!frame.text) return state;
      return {
        ...state,
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
    (text: string): void => send({ type: "text", text }),
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
  }, [send]);

  const disconnect = useCallback(async (): Promise<void> => {
    await stopTalking();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    dispatch({ type: "reset" });
  }, [stopTalking]);

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
