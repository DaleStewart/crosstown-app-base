import { useState, type FormEvent, type ReactNode } from "react";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Citation } from "@/lib/protocol";

export interface TextInputProps {
  onUserTurn: (text: string) => void;
  onAssistantTurn: (payload: { text: string; citations: Citation[]; warnings: string[] }) => void;
}

export function TextInput({ onUserTurn, onAssistantTurn }: TextInputProps): ReactNode {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);

  async function handleSubmit(e: FormEvent): Promise<void> {
    e.preventDefault();
    const message = text.trim();
    if (!message || sending) return;
    setSending(true);
    onUserTurn(message);
    setText("");
    try {
      const res = await fetch("/api/turn", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: message }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      const data = (await res.json()) as {
        text: string;
        citations?: Citation[];
        warnings?: string[];
      };
      onAssistantTurn({
        text: data.text,
        citations: data.citations ?? [],
        warnings: data.warnings ?? [],
      });
    } catch (err) {
      onAssistantTurn({
        text: `[Error] ${err instanceof Error ? err.message : String(err)}`,
        citations: [],
        warnings: ["error"],
      });
    } finally {
      setSending(false);
    }
  }

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
        placeholder={sending ? "Sending…" : "Type a question…"}
        disabled={sending}
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
        disabled={sending || !text.trim()}
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
