import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "ghost" | "outline";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", ...props }, ref) => {
    const styles: Record<NonNullable<ButtonProps["variant"]>, string> = {
      default: "bg-subway-blue text-white hover:bg-subway-ink",
      ghost: "bg-transparent text-subway-ink hover:bg-slate-100",
      outline: "border border-subway-blue text-subway-blue hover:bg-subway-blue/10",
    };
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-subway-yellow disabled:opacity-50",
          styles[variant],
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
