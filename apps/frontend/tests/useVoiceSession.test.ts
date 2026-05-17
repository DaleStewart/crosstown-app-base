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
});
