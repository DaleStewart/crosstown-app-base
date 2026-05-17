import type { ReactNode } from "react";

/** Three bouncing dots shown while the agent is processing a user turn.
 *  Pure CSS animation (no libs); inline keyframes so this component is
 *  self-contained. Visually mirrors an assistant chat bubble so it sits
 *  in the correct column of the transcript stream. */
export function ThinkingIndicator(): ReactNode {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Assistant is thinking"
      data-testid="thinking-indicator"
      className="self-start max-w-[80%] rounded-lg bg-slate-100 px-3 py-2 text-sm text-subway-ink"
    >
      <span className="sr-only">Thinking…</span>
      <span className="inline-flex items-end gap-1" aria-hidden="true">
        <span className="thinking-dot" />
        <span className="thinking-dot" style={{ animationDelay: "150ms" }} />
        <span className="thinking-dot" style={{ animationDelay: "300ms" }} />
      </span>
    </div>
  );
}
