import { type HTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "default" | "yellow" | "muted";
}

export function Badge({
  className,
  tone = "default",
  ...props
}: BadgeProps): ReactNode {
  const tones: Record<NonNullable<BadgeProps["tone"]>, string> = {
    default: "bg-subway-blue text-white",
    yellow: "bg-subway-yellow text-subway-ink",
    muted: "bg-slate-200 text-slate-700",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        tones[tone],
        className
      )}
      {...props}
    />
  );
}
