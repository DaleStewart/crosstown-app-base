import { type HTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";

export function ScrollArea({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>): ReactNode {
  return <div className={cn("overflow-y-auto", className)} {...props} />;
}
