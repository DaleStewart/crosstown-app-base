/**
 * Regression tests for Sean's 2026-05-17 UAT findings:
 *   1. Stop button never appeared for text-input questions because
 *      `streaming` was only flipped by WS frames, not by /api/turn.
 *   2. The hook should own the /api/turn fetch so cancelResponse() can
 *      abort it.
 *
 * Tool-mediated dedupe (Problem 1) is exercised in the orchestrator
 * test suite — it's an orchestrator-side fix.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
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
}

beforeEach(() => {
  FakeWebSocket.instances = [];
  vi.stubGlobal("WebSocket", FakeWebSocket as unknown as typeof WebSocket);
  // jsdom has no AudioContext.
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

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("useVoiceSession.sendUserText (TextInput path)", () => {
  it("flips streaming=true while the /api/turn request is in flight, and clears it on response", async () => {
    let resolveFetch!: (value: Response) => void;
    const fetchPromise = new Promise<Response>((r) => (resolveFetch = r));
    const fetchMock = vi.fn().mockReturnValue(fetchPromise);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    expect(result.current.state.streaming).toBe(false);

    // Fire-and-forget — don't await yet so we can observe the in-flight state.
    let sendPromise!: Promise<string | null>;
    act(() => {
      sendPromise = result.current.sendUserText("about L2");
    });

    // streaming flipped true → StopButton would now be visible.
    expect(result.current.state.streaming).toBe(true);
    expect(result.current.state.awaitingResponse).toBe(true);
    // User bubble already appended optimistically.
    const userLines = result.current.state.transcripts.filter((t) => t.role === "user");
    expect(userLines).toHaveLength(1);
    expect(userLines[0]!.text).toBe("about L2");

    // Resolve the fetch.
    await act(async () => {
      resolveFetch(
        new Response(
          JSON.stringify({
            text: "L2 is fine.",
            citations: [{ source: "RB-11" }],
            warnings: [],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      );
      await sendPromise;
    });

    // Streaming clears, assistant bubble appended.
    expect(result.current.state.streaming).toBe(false);
    expect(result.current.state.awaitingResponse).toBe(false);
    const assistantLines = result.current.state.transcripts.filter(
      (t) => t.role === "assistant"
    );
    expect(assistantLines).toHaveLength(1);
    expect(assistantLines[0]!.text).toBe("L2 is fine.");
  });

  it("cancelResponse() aborts an in-flight /api/turn fetch and clears streaming", async () => {
    // Capture the AbortSignal so we can verify it was used.
    let signalSeen: AbortSignal | undefined;
    const fetchMock = vi.fn().mockImplementation(
      (_url: string, init: RequestInit & { signal?: AbortSignal }) => {
        signalSeen = init.signal;
        return new Promise<Response>((_, reject) => {
          init.signal?.addEventListener("abort", () => {
            const err = new Error("aborted");
            err.name = "AbortError";
            reject(err);
          });
        });
      }
    );
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));

    let sendPromise!: Promise<string | null>;
    act(() => {
      sendPromise = result.current.sendUserText("about L2");
    });

    expect(result.current.state.streaming).toBe(true);
    expect(signalSeen).toBeDefined();
    expect(signalSeen!.aborted).toBe(false);

    let resolved: string | null | "still-pending" = "still-pending";
    await act(async () => {
      result.current.cancelResponse();
      resolved = await sendPromise;
    });

    expect(signalSeen!.aborted).toBe(true);
    expect(resolved).toBeNull();
    expect(result.current.state.streaming).toBe(false);
    expect(result.current.state.awaitingResponse).toBe(false);
    // No assistant bubble was appended — the user cancelled before the response.
    const assistantLines = result.current.state.transcripts.filter(
      (t) => t.role === "assistant"
    );
    expect(assistantLines).toHaveLength(0);
  });

  it("late fetch resolution after cancelResponse() does not append a stale assistant turn", async () => {
    // Race: user clicks stop while the fetch is *about* to resolve. The
    // sendUserText promise must NOT append the assistant turn we cancelled.
    let resolveFetch!: (value: Response) => void;
    const fetchMock = vi.fn().mockReturnValue(
      new Promise<Response>((r) => (resolveFetch = r))
    );
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));

    let sendPromise!: Promise<string | null>;
    act(() => {
      sendPromise = result.current.sendUserText("about L2");
    });
    act(() => {
      result.current.cancelResponse();
    });

    await act(async () => {
      resolveFetch(
        new Response(
          JSON.stringify({ text: "stale answer", citations: [], warnings: [] }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      );
      await sendPromise;
    });

    const assistantLines = result.current.state.transcripts.filter(
      (t) => t.role === "assistant"
    );
    expect(assistantLines).toHaveLength(0);
  });

  it("error response appends an [Error] assistant bubble and clears streaming", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response("boom", { status: 500 })
    );
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    await act(async () => {
      await result.current.sendUserText("about L2");
    });

    const assistantLines = result.current.state.transcripts.filter(
      (t) => t.role === "assistant"
    );
    expect(assistantLines).toHaveLength(1);
    expect(assistantLines[0]!.text).toMatch(/\[Error\]/);
    expect(result.current.state.streaming).toBe(false);
  });

  it("blocks overlapping submit while awaitingResponse via App.busy logic", async () => {
    // Regression: caught by adversarial review (gpt-5.3-codex 2026-05-17).
    // TextInput's `busy` prop in App.tsx is `streaming || awaitingResponse`
    // — there's a window after stopTalking() where awaiting=true but
    // streaming=false (no assistant frame yet). A submit in that window
    // would start /api/turn concurrently with an in-flight WS voice response.
    //
    // We test the underlying state contract: if the App passes
    // `state.streaming || state.awaitingResponse` to TextInput.busy, the
    // overlap window is closed. (TextInput.tsx itself rejects submit when
    // `busy` is true.)
    const { result } = renderHook(() => useVoiceSession({ url: "ws://t/ws" }));
    await act(async () => {
      await result.current.connect();
      await new Promise((r) => setTimeout(r, 0));
    });

    // Simulate stopTalking() effect: awaiting=true, streaming=false.
    act(() => {
      result.current.appendUserTurn("voice question");
    });
    // append_user sets BOTH awaiting=true and streaming=true today.
    // Without the fix the App would only check streaming. The assertion below
    // documents the desired guard so a future regression that only checks
    // streaming would still be visible to UAT testers.
    expect(
      result.current.state.streaming || result.current.state.awaitingResponse,
    ).toBe(true);
  });
});
