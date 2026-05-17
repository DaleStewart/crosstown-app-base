import { describe, it, expect } from "vitest";
import {
  isServerMessage,
  parseServerMessage,
  type ServerMessage,
} from "@/lib/protocol";

describe("protocol", () => {
  it("recognises valid server frames", () => {
    const frames: ServerMessage[] = [
      { type: "transcript_delta", role: "user", text: "hi", final: false },
      { type: "audio_delta", audio_b64: "abc" },
      { type: "tool_call", name: "search", args: {}, call_id: "c1" },
      { type: "tool_result", name: "search", citations: [], warnings: [] },
      { type: "final", text: "done", citations: [] },
      { type: "error", message: "boom" },
      { type: "user_transcript", text: "hello" },
    ];
    for (const f of frames) expect(isServerMessage(f)).toBe(true);
  });

  it("rejects junk", () => {
    expect(isServerMessage(null)).toBe(false);
    expect(isServerMessage({ type: "nope" })).toBe(false);
    expect(parseServerMessage("not json")).toBeNull();
    expect(parseServerMessage('{"type":"nope"}')).toBeNull();
  });

  it("parses a valid frame", () => {
    const out = parseServerMessage(
      JSON.stringify({ type: "final", text: "ok", citations: [] })
    );
    expect(out?.type).toBe("final");
  });

  it("normalizes Wanda alias event names to user_transcript", () => {
    const aliases = [
      "user_transcript",
      "user_transcript_completed",
      "input_audio_transcription_completed",
      "transcript_user_final",
    ];
    for (const alias of aliases) {
      const out = parseServerMessage(
        JSON.stringify({ type: alias, text: "my speech", item_id: "i1" })
      );
      expect(out?.type).toBe("user_transcript");
      expect((out as { text?: string }).text).toBe("my speech");
    }
  });
});
