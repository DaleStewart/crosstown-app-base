import { useEffect, useRef, type ReactNode } from "react";
import type { TranscriptLine } from "@/hooks/useVoiceSession";
import { ScrollArea } from "@/ui/scroll-area";
import { ThinkingIndicator } from "@/components/ThinkingIndicator";
import { cn } from "@/lib/utils";

export function Transcript({
  lines,
  thinking = false,
}: {
  lines: TranscriptLine[];
  thinking?: boolean;
}): ReactNode {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [lines, thinking]);

  return (
    <ScrollArea
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
        <div ref={endRef} />
      </div>
    </ScrollArea>
  );
}
