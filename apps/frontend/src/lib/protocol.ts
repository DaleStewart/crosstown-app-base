export type ClientStart = {
  type: "start";
  conversationId: string | null;
  mode: "push_to_talk" | "continuous";
};

export type ClientText = { type: "text"; text: string };
export type ClientStop = { type: "stop" };
export type ClientMessage = ClientStart | ClientText | ClientStop;

export type Citation = {
  source?: string;
  url?: string;
  snippet?: string;
  [k: string]: unknown;
};

export type TranscriptDelta = {
  type: "transcript_delta";
  role: "user" | "assistant";
  text: string;
  final: boolean;
};

export type AudioDelta = {
  type: "audio_delta";
  audio_b64: string;
};

export type ToolCall = {
  type: "tool_call";
  name: string;
  args: Record<string, unknown>;
  call_id: string;
};

export type ToolResult = {
  type: "tool_result";
  name: string;
  citations: Citation[];
  warnings: string[];
};

export type Final = {
  type: "final";
  text: string;
  citations: Citation[];
};

export type ErrorFrame = {
  type: "error";
  message: string;
};

export type ServerMessage =
  | TranscriptDelta
  | AudioDelta
  | ToolCall
  | ToolResult
  | Final
  | ErrorFrame;

export function isServerMessage(value: unknown): value is ServerMessage {
  if (typeof value !== "object" || value === null) return false;
  const t = (value as { type?: unknown }).type;
  return (
    t === "transcript_delta" ||
    t === "audio_delta" ||
    t === "tool_call" ||
    t === "tool_result" ||
    t === "final" ||
    t === "error"
  );
}

export function parseServerMessage(raw: string): ServerMessage | null {
  try {
    const value: unknown = JSON.parse(raw);
    return isServerMessage(value) ? value : null;
  } catch {
    return null;
  }
}
