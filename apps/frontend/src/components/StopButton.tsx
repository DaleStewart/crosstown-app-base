import { type ReactNode } from "react";
import { Square } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StopButtonProps {
  /** True while a response is streaming. The button is hidden when false so
   *  the user only sees it when there is something TO stop. */
  visible: boolean;
  onClick: () => void;
  disabled?: boolean;
}

/** Sean's explicit "shut up" control (2026-05-17). Red, square, ⏹.
 *  Distinct from the round push-to-talk button on purpose: this is a
 *  destructive action and should look different at a glance. */
export function StopButton({ visible, onClick, disabled }: StopButtonProps): ReactNode {
  if (!visible) return null;
  return (
    <button
      type="button"
      aria-label="Stop response"
      data-testid="stop-button"
      disabled={disabled}
      onClick={onClick}
      className={cn(
        "flex h-16 w-16 items-center justify-center rounded-md shadow-lg transition",
        "focus:outline-none focus-visible:ring-4 focus-visible:ring-red-300",
        "bg-red-600 text-white hover:bg-red-700 active:scale-95",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <Square className="h-7 w-7" fill="currentColor" />
    </button>
  );
}
