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

/** Normalized user-turn transcript from the orchestrator.
 *  Wanda may send this under several event names — all are normalized here. */
export type UserTranscript = {
  type: "user_transcript";
  text: string;
  item_id?: string;
};

/** Raw event names Wanda's server side may emit for user speech transcripts. */
const USER_TRANSCRIPT_ALIASES = new Set([
  "user_transcript",
  "user_transcript_completed",
  "input_audio_transcription_completed",
  "transcript_user_final",
]);

export type ServerMessage =
  | TranscriptDelta
  | AudioDelta
  | ToolCall
  | ToolResult
  | Final
  | ErrorFrame
  | UserTranscript;

export function isServerMessage(value: unknown): value is ServerMessage {
  if (typeof value !== "object" || value === null) return false;
  const t = (value as { type?: unknown }).type;
  return (
    t === "transcript_delta" ||
    t === "audio_delta" ||
    t === "tool_call" ||
    t === "tool_result" ||
    t === "final" ||
    t === "error" ||
    t === "user_transcript" ||
    (typeof t === "string" && USER_TRANSCRIPT_ALIASES.has(t))
  );
}

export function parseServerMessage(raw: string): ServerMessage | null {
  try {
    const value: unknown = JSON.parse(raw);
    if (typeof value !== "object" || value === null) return null;
    const obj = value as Record<string, unknown>;
    // Normalize all Wanda event name aliases to the canonical "user_transcript" type.
    if (typeof obj.type === "string" && USER_TRANSCRIPT_ALIASES.has(obj.type)) {
      const normalized: UserTranscript = {
        type: "user_transcript",
        text: typeof obj.text === "string" ? obj.text : "",
        ...(typeof obj.item_id === "string" ? { item_id: obj.item_id } : {}),
      };
      return normalized;
    }
    return isServerMessage(value) ? value : null;
  } catch {
    return null;
  }
}
