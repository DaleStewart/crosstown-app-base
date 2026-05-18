import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useVoiceSession } from "@/hooks/useVoiceSession";

class FakeWebSocket {
  public static instances: FakeWebSocket[] = [];
  public readyState = 1;
  public binaryType = "arraybuffer";
  public sent: string[] = [];
  public onopen: ((ev: Event) => void) | null = null;
  public onmessage: ((ev: MessageEvent) => void) | null = null;
  public onerror: ((ev: Event) => void) | null = null;
  public onclose: ((ev: CloseEvent) => void) | null = null;
  static OPEN = 1;

  constructor(public url: string) {
    FakeWebSocket.instances.push(this);
    queueMicrotask(() => this.onopen?.(new Event("open")));
  }

  send(data: string | ArrayBuffer): void {
    if (typeof data === "string") this.sent.push(data);
  }

  close(): void {
    this.readyState = 3;
    this.onclose?.(new CloseEvent("close"));
  }

  emit(payload: unknown): void {
    this.onmessage?.(
      new MessageEvent("message", { data: JSON.stringify(payload) })
    );
  }
}

beforeEach(() => {
  FakeWebSocket.instances = [];
  vi.stubGlobal("WebSocket", FakeWebSocket as unknown as typeof WebSocket);
});

describe("useVoiceSession", () => {
  it("connects, applies transcript + tool frames, and tears down", async () => {
    const { result, unmount } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );

    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });

    expect(FakeWebSocket.instances.length).toBe(1);
    const ws = FakeWebSocket.instances[0]!;
    expect(result.current.state.status).toBe("connected");
    expect(ws.sent[0]).toContain('"type":"start"');

    act(() => {
      ws.emit({ type: "transcript_delta", role: "user", text: "hi", final: true });
      ws.emit({
        type: "tool_call",
        name: "search_logs",
        args: { q: "doors" },
        call_id: "c1",
      });
      ws.emit({
        type: "tool_result",
        name: "search_logs",
        citations: [{ source: "log#1" }],
        warnings: [],
      });
      ws.emit({ type: "final", text: "done", citations: [] });
    });

    expect(result.current.state.transcripts.some((t) => t.text === "hi")).toBe(true);
    expect(result.current.state.toolCalls).toHaveLength(1);
    expect(result.current.state.toolCalls[0]!.citations).toHaveLength(1);
    expect(result.current.state.toolCalls[0]!.pending).toBe(false);

    unmount();
  });

  it("sendText writes a text frame to the socket", async () => {
    const { result } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;
    act(() => result.current.sendText("hello"));
    expect(ws.sent.some((s) => s.includes('"text":"hello"'))).toBe(true);
  });

  it("user_transcript event adds a role:user transcript line", async () => {
    const { result, unmount } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;

    act(() => {
      ws.emit({ type: "user_transcript", text: "Show me door faults", item_id: "item_1" });
    });

    const userLines = result.current.state.transcripts.filter((t) => t.role === "user");
    expect(userLines).toHaveLength(1);
    expect(userLines[0]!.text).toBe("Show me door faults");
    expect(userLines[0]!.final).toBe(true);
    unmount();
  });

  it("all Wanda alias event names are normalized to user transcript lines", async () => {
    const aliases = [
      "user_transcript",
      "user_transcript_completed",
      "input_audio_transcription_completed",
      "transcript_user_final",
    ];

    for (const alias of aliases) {
      FakeWebSocket.instances = [];
      const { result, unmount } = renderHook(() =>
        useVoiceSession({ url: "ws://test/ws/voice" })
      );
      await act(async () => {
        await result.current.connect();
        await new Promise((r) => setTimeout(r, 0));
      });
      const ws = FakeWebSocket.instances[0]!;
      act(() => {
        ws.emit({ type: alias, text: `speech via ${alias}` });
      });
      const userLines = result.current.state.transcripts.filter((t) => t.role === "user");
      expect(userLines).toHaveLength(1);
      expect(userLines[0]!.text).toBe(`speech via ${alias}`);
      unmount();
    }
  });

  it("appendUserTurn adds a user transcript line without WS", () => {
    const { result } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    act(() => result.current.appendUserTurn("hello from keyboard"));
    expect(result.current.state.transcripts).toHaveLength(1);
    expect(result.current.state.transcripts[0]).toMatchObject({
      role: "user",
      text: "hello from keyboard",
      final: true,
    });
  });

  it("appendAssistantTurn adds assistant transcript and tool entry with citations", () => {
    const { result } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    act(() =>
      result.current.appendAssistantTurn({
        text: "Here are the door faults.",
        citations: [{ source: "log#5", snippet: "door fault at Atlantic" }],
        warnings: [],
      })
    );
    expect(result.current.state.transcripts).toHaveLength(1);
    expect(result.current.state.transcripts[0]).toMatchObject({
      role: "assistant",
      text: "Here are the door faults.",
      final: true,
    });
    expect(result.current.state.toolCalls).toHaveLength(1);
    expect(result.current.state.toolCalls[0]!.citations).toHaveLength(1);
    expect(result.current.state.toolCalls[0]!.pending).toBe(false);
  });

  it("appendAssistantTurn with no citations does not create a tool entry", () => {
    const { result } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    act(() =>
      result.current.appendAssistantTurn({ text: "No data found.", citations: [], warnings: [] })
    );
    expect(result.current.state.transcripts).toHaveLength(1);
    expect(result.current.state.toolCalls).toHaveLength(0);
  });

  it("appendUserTurn flips awaitingResponse on, appendAssistantTurn clears it", () => {
    const { result } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    expect(result.current.state.awaitingResponse).toBe(false);
    act(() => result.current.appendUserTurn("any trains down?"));
    expect(result.current.state.awaitingResponse).toBe(true);
    act(() =>
      result.current.appendAssistantTurn({ text: "All clear.", citations: [], warnings: [] })
    );
    expect(result.current.state.awaitingResponse).toBe(false);
  });

  it("final user transcript_delta sets awaitingResponse; assistant delta clears it", async () => {
    const { result, unmount } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;

    act(() => {
      ws.emit({ type: "transcript_delta", role: "user", text: "doors at Atlantic?", final: true });
    });
    expect(result.current.state.awaitingResponse).toBe(true);

    act(() => {
      ws.emit({ type: "transcript_delta", role: "assistant", text: "Checking", final: false });
    });
    expect(result.current.state.awaitingResponse).toBe(false);
    unmount();
  });

  it("user_transcript event sets awaitingResponse and final clears it", async () => {
    const { result, unmount } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;
    act(() => {
      ws.emit({ type: "user_transcript", text: "next L train?" });
    });
    expect(result.current.state.awaitingResponse).toBe(true);
    act(() => {
      ws.emit({ type: "final", text: "Soon.", citations: [] });
    });
    expect(result.current.state.awaitingResponse).toBe(false);
    unmount();
  });

  it("dedupes a final frame whose text matches the already-finalized assistant line", async () => {
    // Regression for Sean's 2026-05-18 duplicate-assistant-turn bug. Foundry GA
    // emits BOTH `response.output_audio_transcript.done` (forwarded as a
    // transcript_delta final=true) AND `response.done` (forwarded as a final
    // frame). The orchestrator now strips the duplicate text, but the frontend
    // also defensively dedupes in case any other provider echoes it back.
    const { result, unmount } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;

    act(() => {
      ws.emit({
        type: "transcript_delta",
        role: "assistant",
        text: "L1 service is fully suspended right now.",
        final: true,
      });
    });
    act(() => {
      ws.emit({
        type: "final",
        text: "L1 service is fully suspended right now.",
        citations: [],
      });
    });

    const assistantLines = result.current.state.transcripts.filter(
      (t) => t.role === "assistant"
    );
    expect(assistantLines).toHaveLength(1);
    expect(result.current.state.awaitingResponse).toBe(false);
    unmount();
  });

  it("empty-text final frame after assistant transcript clears awaiting without adding a line", async () => {
    // Mirrors post-fix orchestrator behavior: when a transcript_delta final=true
    // was already sent, the orchestrator emits {type:"final", text:""}.
    const { result, unmount } = renderHook(() =>
      useVoiceSession({ url: "ws://test/ws/voice" })
    );
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;

    act(() => {
      ws.emit({
        type: "transcript_delta",
        role: "assistant",
        text: "Doors held cluster on L2.",
        final: true,
      });
    });
    act(() => {
      ws.emit({ type: "final", text: "", citations: [] });
    });

    const assistantLines = result.current.state.transcripts.filter(
      (t) => t.role === "assistant"
    );
    expect(assistantLines).toHaveLength(1);
    expect(assistantLines[0]!.text).toBe("Doors held cluster on L2.");
    expect(result.current.state.awaitingResponse).toBe(false);
    unmount();
  });
});
