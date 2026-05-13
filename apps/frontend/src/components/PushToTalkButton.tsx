import { useCallback, useEffect, type ReactNode } from "react";
import { Mic, MicOff } from "lucide-react";
import { cn } from "@/lib/utils";

export interface PushToTalkButtonProps {
  recording: boolean;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
}

export function PushToTalkButton({
  recording,
  onStart,
  onStop,
  disabled,
}: PushToTalkButtonProps): ReactNode {
  const handleDown = useCallback(() => {
    if (!disabled) onStart();
  }, [disabled, onStart]);

  const handleUp = useCallback(() => {
    if (!disabled) onStop();
  }, [disabled, onStop]);

  useEffect(() => {
    const down = (ev: KeyboardEvent): void => {
      if (ev.code === "Space" && !ev.repeat && !disabled) {
        ev.preventDefault();
        onStart();
      }
    };
    const up = (ev: KeyboardEvent): void => {
      if (ev.code === "Space" && !disabled) {
        ev.preventDefault();
        onStop();
      }
    };
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    return () => {
      window.removeEventListener("keydown", down);
      window.removeEventListener("keyup", up);
    };
  }, [disabled, onStart, onStop]);

  return (
    <button
      type="button"
      aria-label="Push to talk"
      aria-pressed={recording}
      disabled={disabled}
      onMouseDown={handleDown}
      onMouseUp={handleUp}
      onMouseLeave={handleUp}
      onTouchStart={handleDown}
      onTouchEnd={handleUp}
      className={cn(
        "flex h-32 w-32 items-center justify-center rounded-full shadow-lg transition",
        "focus:outline-none focus-visible:ring-4 focus-visible:ring-subway-yellow",
        recording
          ? "bg-subway-yellow text-subway-ink scale-105"
          : "bg-subway-blue text-white hover:bg-subway-ink",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      {recording ? <MicOff className="h-12 w-12" /> : <Mic className="h-12 w-12" />}
    </button>
  );
}
