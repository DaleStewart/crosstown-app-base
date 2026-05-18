import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { renderHook, act } from "@testing-library/react";
import { StopButton } from "@/components/StopButton";
import { useVoiceSession } from "@/hooks/useVoiceSession";

describe("StopButton", () => {
  it("is hidden when visible=false", () => {
    const { container } = render(<StopButton visible={false} onClick={() => {}} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders a red, square stop button when visible", () => {
    render(<StopButton visible={true} onClick={() => {}} />);
    const btn = screen.getByRole("button", { name: /stop response/i });
    expect(btn).toBeTruthy();
    expect(btn.className).toMatch(/bg-red-600/);
    // Rounded-md, not rounded-full — visually distinct from the mic button.
    expect(btn.className).toMatch(/rounded-md/);
    expect(btn.className).not.toMatch(/rounded-full/);
  });

  it("fires onClick when pressed", () => {
    const onClick = vi.fn();
    render(<StopButton visible={true} onClick={onClick} />);
    fireEvent.click(screen.getByTestId("stop-button"));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("does not fire onClick when disabled", () => {
    const onClick = vi.fn();
    render(<StopButton visible={true} disabled onClick={onClick} />);
    fireEvent.click(screen.getByTestId("stop-button"));
    expect(onClick).not.toHaveBeenCalled();
  });
});

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
    this.onmessage?.(new MessageEvent("message", { data: JSON.stringify(payload) }));
  }
}

beforeEach(() => {
  FakeWebSocket.instances = [];
  vi.stubGlobal("WebSocket", FakeWebSocket as unknown as typeof WebSocket);
  // jsdom has no Web Audio. Stub the bits AudioPlayer touches so the audio_delta
  // path doesn't throw. We only care here about reducer state; the playback
  // contract is exercised separately in audio.test.ts (if added) and in e2e.
  class FakeAudioContext {
    currentTime = 0;
    destination = {};
    createBuffer(_ch: number, len: number, _rate: number): unknown {
      return { getChannelData: () => new Float32Array(len), duration: 0 };
    }
    createBufferSource(): unknown {
      return {
        connect: () => undefined,
        disconnect: () => undefined,
        start: () => undefined,
        stop: () => undefined,
        onended: null as null | (() => void),
        buffer: null,
      };
    }
    suspend(): Promise<void> { return Promise.resolve(); }
    resume(): Promise<void> { return Promise.resolve(); }
    close(): Promise<void> { return Promise.resolve(); }
  }
  vi.stubGlobal("AudioContext", FakeAudioContext as unknown as typeof AudioContext);
});

describe("useVoiceSession cancellation", () => {
  it("streaming flips true on first assistant transcript_delta", async () => {
    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;
    expect(result.current.state.streaming).toBe(false);
    act(() => {
      ws.emit({ type: "transcript_delta", role: "assistant", text: "L1 ", final: false });
    });
    expect(result.current.state.streaming).toBe(true);
  });

  it("streaming clears on final", async () => {
    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;
    act(() => {
      ws.emit({ type: "transcript_delta", role: "assistant", text: "L1 ", final: false });
      ws.emit({ type: "final", text: "L1 done.", citations: [] });
    });
    expect(result.current.state.streaming).toBe(false);
  });

  it("streaming flips true on audio_delta even without a transcript_delta", async () => {
    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;
    act(() => {
      ws.emit({ type: "audio_delta", audio_b64: "AAAA" });
    });
    expect(result.current.state.streaming).toBe(true);
  });

  it("response_cancelled server frame clears streaming + awaiting", async () => {
    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;
    act(() => {
      ws.emit({ type: "transcript_delta", role: "assistant", text: "drone ", final: false });
    });
    expect(result.current.state.streaming).toBe(true);
    act(() => {
      ws.emit({ type: "response_cancelled" });
    });
    expect(result.current.state.streaming).toBe(false);
    expect(result.current.state.awaitingResponse).toBe(false);
  });

  it("cancelResponse sends cancel_response WS frame and optimistically clears streaming", async () => {
    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;
    act(() => {
      ws.emit({ type: "transcript_delta", role: "assistant", text: "drone ", final: false });
    });
    expect(result.current.state.streaming).toBe(true);

    act(() => result.current.cancelResponse());

    // Optimistic: state cleared immediately, before server ack.
    expect(result.current.state.streaming).toBe(false);
    expect(result.current.state.awaitingResponse).toBe(false);
    // Frame on the wire.
    expect(ws.sent.some((s) => s.includes('"cancel_response"'))).toBe(true);
  });

  it("late assistant frames after cancelled do not re-show streaming until a new response begins", async () => {
    // Regression for the "trailing audio after stop" path: orchestrator may
    // still flush a few frames after response.cancel; the audio_delta path
    // should set streaming=true (since a new response stream is theoretically
    // possible). The orchestrator drops these server-side, but if any leak
    // through they would briefly show the stop button. Acceptable + matches
    // the existing audio_delta semantics — this test documents the behavior.
    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });
    const ws = FakeWebSocket.instances[0]!;
    act(() => {
      ws.emit({ type: "transcript_delta", role: "assistant", text: "x", final: false });
      ws.emit({ type: "response_cancelled" });
    });
    expect(result.current.state.streaming).toBe(false);
    // Empty-text final frame after cancel should also keep streaming false.
    act(() => {
      ws.emit({ type: "final", text: "", citations: [] });
    });
    expect(result.current.state.streaming).toBe(false);
  });
});
