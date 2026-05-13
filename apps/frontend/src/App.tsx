import { type ReactNode } from "react";
import { Header } from "@/components/Header";
import { PushToTalkButton } from "@/components/PushToTalkButton";
import { Transcript } from "@/components/Transcript";
import { ToolCallPanel } from "@/components/ToolCallPanel";
import { useVoiceSession } from "@/hooks/useVoiceSession";

const MODE = (import.meta.env.VITE_VOICE_MODE === "continuous"
  ? "continuous"
  : "push_to_talk") as "continuous" | "push_to_talk";

export default function App(): ReactNode {
  const { state, startTalking, stopTalking } = useVoiceSession({ mode: MODE });

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <Header />
      <main className="grid flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-[1fr_360px]">
        <section className="flex flex-col gap-4">
          <div className="flex flex-1 items-center justify-center rounded-lg border border-slate-200 bg-white p-8">
            <PushToTalkButton
              recording={state.recording}
              onStart={() => void startTalking()}
              onStop={() => void stopTalking()}
            />
          </div>
          <Transcript lines={state.transcripts} />
        </section>
        <aside className="lg:row-span-1">
          <ToolCallPanel entries={state.toolCalls} />
        </aside>
      </main>
      <footer className="bg-subway-ink px-6 py-3 text-center text-xs text-slate-300">
        <a
          href="https://github.com/"
          className="underline hover:text-subway-yellow"
          target="_blank"
          rel="noreferrer"
        >
          README &amp; docs
        </a>
      </footer>
    </div>
  );
}
