import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "@/App";

class FakeWebSocket {
  public readyState = 1;
  public binaryType = "arraybuffer";
  public onopen: ((ev: Event) => void) | null = null;
  public onmessage: ((ev: MessageEvent) => void) | null = null;
  public onerror: ((ev: Event) => void) | null = null;
  public onclose: ((ev: CloseEvent) => void) | null = null;
  static OPEN = 1;
  constructor(public url: string) {
    queueMicrotask(() => this.onopen?.(new Event("open")));
  }
  send(): void {}
  close(): void {
    this.onclose?.(new CloseEvent("close"));
  }
}

beforeEach(() => {
  vi.stubGlobal("WebSocket", FakeWebSocket as unknown as typeof WebSocket);
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: true,
      json: async () => ({ status: "ok", voice_provider: "foundry_realtime" }),
    })) as unknown as typeof fetch
  );
});

describe("App", () => {
  it("renders header and push-to-talk button", () => {
    render(<App />);
    expect(screen.getByText(/MTA Hackathon/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/push to talk/i)).toBeInTheDocument();
  });
});
