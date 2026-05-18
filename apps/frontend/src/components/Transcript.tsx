import { useEffect, useLayoutEffect, useRef, type ReactNode } from "react";
import type { TranscriptLine } from "@/hooks/useVoiceSession";
import { ScrollArea } from "@/ui/scroll-area";
import { ThinkingIndicator } from "@/components/ThinkingIndicator";
import { cn } from "@/lib/utils";

/** Pixel slack: if the user is within this many px of the bottom we treat them
 *  as "pinned" and continue to auto-scroll new content into view. If they've
 *  scrolled further up than this we leave the scroll position alone — that's
 *  the user actively reading something earlier in the conversation, and the
 *  old `scrollIntoView` on every token was yanking them back (Sean's 2026-05-18
 *  UAT). 80px ≈ one user message bubble of slack. */
const NEAR_BOTTOM_PX = 80;

export function Transcript({
  lines,
  thinking = false,
}: {
  lines: TranscriptLine[];
  thinking?: boolean;
}): ReactNode {
  const viewportRef = useRef<HTMLDivElement>(null);
  /** Tracks whether the user is currently "pinned" to the bottom. Starts true
   *  so the very first assistant turn does scroll into view. A scroll-event
   *  listener (below) flips it when the user scrolls away from the bottom. */
  const pinnedRef = useRef<boolean>(true);

  // Re-evaluate pin state whenever the user scrolls the viewport. Cheap +
  // passive; runs on the same element React already owns so there's no
  // wasted work when the component unmounts.
  useEffect(() => {
    const el = viewportRef.current;
    if (!el) return;
    const onScroll = (): void => {
      const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
      pinnedRef.current = distanceFromBottom <= NEAR_BOTTOM_PX;
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);

  // Layout effect so the scroll happens before the browser paints — avoids the
  // flicker where the page renders a longer transcript and *then* jumps. We
  // set scrollTop directly (instead of scrollIntoView) because scrollIntoView
  // can also nudge the window/document scroll position, which is what was
  // making the whole page lurch when the ThinkingIndicator / StopButton
  // mounted and changed page height.
  useLayoutEffect(() => {
    const el = viewportRef.current;
    if (!el) return;
    if (!pinnedRef.current) return;
    el.scrollTop = el.scrollHeight;
  }, [lines, thinking]);

  return (
    <ScrollArea
      ref={viewportRef}
      className="flex-1 min-h-[200px] max-h-[40vh] border-t border-slate-200 bg-white p-4"
      data-testid="transcript"
    >
      <div className="flex flex-col gap-2">
        {lines.length === 0 && !thinking && (
          <p className="text-sm text-slate-400 italic">No transcript yet. Hold to talk.</p>
        )}
        {lines.map((line) => (
          <div
            key={line.id}
            className={cn(
              "max-w-[80%] rounded-lg px-3 py-2 text-sm",
              line.role === "user"
                ? "self-end bg-subway-blue text-white"
                : "self-start bg-slate-100 text-subway-ink"
            )}
          >
            {line.text || (line.final ? "" : "…")}
          </div>
        ))}
        {thinking && <ThinkingIndicator />}
      </div>
    </ScrollArea>
  );
}
