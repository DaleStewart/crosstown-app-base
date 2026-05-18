import { type ReactNode } from "react";
import { Header } from "@/components/Header";
import { PushToTalkButton } from "@/components/PushToTalkButton";
import { StopButton } from "@/components/StopButton";
import { Transcript } from "@/components/Transcript";
import { DisruptionBanner } from "@/components/DisruptionBanner";
import { AlternateRouteCard } from "@/components/AlternateRouteCard";
import { ToolCallPanel } from "@/components/ToolCallPanel";
import { TextInput } from "@/components/TextInput";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { useVoiceSession } from "@/hooks/useVoiceSession";

const MODE = (import.meta.env.VITE_VOICE_MODE === "continuous"
  ? "continuous"
  : "push_to_talk") as "continuous" | "push_to_talk";

export default function App(): ReactNode {
  const { state, startTalking, stopTalking, cancelResponse, appendUserTurn, appendAssistantTurn } = useVoiceSession({ mode: MODE });

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <Header />
      <main className="grid flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-[1fr_360px]">
        <ErrorBoundary>
          <section className="flex flex-col gap-4">
            <div className="flex flex-1 items-center justify-center gap-6 rounded-lg border border-slate-200 bg-white p-8">
              <PushToTalkButton
                recording={state.recording}
                onStart={() => void startTalking()}
                onStop={() => void stopTalking()}
              />
              <StopButton
                visible={state.streaming}
                onClick={cancelResponse}
              />
            </div>
            <DisruptionBanner entries={state.toolCalls} />
            <AlternateRouteCard entries={state.toolCalls} />
            <Transcript lines={state.transcripts} thinking={state.awaitingResponse} />
            <TextInput onUserTurn={appendUserTurn} onAssistantTurn={appendAssistantTurn} />
          </section>
        </ErrorBoundary>
        <aside className="lg:row-span-1">
          <ErrorBoundary>
            <ToolCallPanel entries={state.toolCalls} />
          </ErrorBoundary>
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
