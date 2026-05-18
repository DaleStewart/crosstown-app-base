import { useState, type FormEvent, type ReactNode } from "react";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";

export interface TextInputProps {
  /** Submits the typed text through useVoiceSession.sendUserText so the
   *  StopButton, audio drain, and cancel path all hang off the same state.
   *  Returns a promise that resolves when the assistant turn is appended
   *  (or null if the user cancelled). */
  onSubmit: (text: string) => Promise<string | null>;
  /** When true, the form input is disabled (a response is in flight or the
   *  request is being cancelled). Driven by state.streaming in App.tsx. */
  busy?: boolean;
}

export function TextInput({ onSubmit, busy }: TextInputProps): ReactNode {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);

  async function handleSubmit(e: FormEvent): Promise<void> {
    e.preventDefault();
    const message = text.trim();
    if (!message || sending || busy) return;
    setSending(true);
    setText("");
    try {
      await onSubmit(message);
    } finally {
      setSending(false);
    }
  }

  const disabled = sending || busy;

  return (
    <form
      onSubmit={(e) => void handleSubmit(e)}
      className="flex gap-2 border-t border-slate-200 bg-white px-4 py-3"
    >
      <label htmlFor="text-turn-input" className="sr-only">
        Type your question
      </label>
      <input
        id="text-turn-input"
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={disabled ? "Sending…" : "Type a question…"}
        disabled={disabled}
        className={cn(
          "flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm",
          "placeholder:text-slate-400",
          "focus:border-subway-blue focus:outline-none focus:ring-2 focus:ring-subway-blue/20",
          "disabled:cursor-not-allowed disabled:bg-slate-50"
        )}
        aria-label="Type your question"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className={cn(
          "flex items-center gap-1.5 rounded-md px-4 py-2 text-sm font-medium transition",
          "bg-subway-blue text-white hover:bg-subway-ink",
          "focus:outline-none focus-visible:ring-2 focus-visible:ring-subway-yellow",
          "disabled:cursor-not-allowed disabled:opacity-50"
        )}
        aria-label="Send"
      >
        <Send className="h-4 w-4" />
        Send
      </button>
    </form>
  );
}
