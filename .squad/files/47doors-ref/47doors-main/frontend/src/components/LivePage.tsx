/**
 * Live transcript page: audience-facing view projected during demos.
 * Dark theme, large text, auto-scrolling transcript. No demo script visible.
 */

import { useEffect, useRef, useCallback } from 'react';
import { PhoneIcon, ArrowLeftIcon } from '@heroicons/react/24/solid';
import { useTranscriptStream } from '../hooks/useTranscriptStream';
import type { TranscriptEvent } from '../types/demo';

const PHONE_NUMBER = '+1 (913) 217-1946';

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    return '';
  }
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

// ─── Transcript Event Rendering (dark-theme, large text) ─────────────────────

function LiveBubble({ event }: { event: TranscriptEvent }) {
  if (event.type === 'call_started') {
    return (
      <div className="flex justify-center my-4">
        <span className="inline-flex items-center gap-2 text-sm font-medium text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 rounded-full px-5 py-2">
          📞 Call connected
          <span className="text-emerald-600">•</span>
          {formatTimestamp(event.timestamp)}
        </span>
      </div>
    );
  }

  if (event.type === 'call_ended') {
    return (
      <div className="flex justify-center my-4">
        <span className="inline-flex items-center gap-2 text-sm font-medium text-slate-400 bg-slate-800/60 border border-slate-700/50 rounded-full px-5 py-2">
          Call ended • {formatDuration(event.duration_seconds)}
        </span>
      </div>
    );
  }

  if (event.type === 'tool_call') {
    return (
      <div className="flex justify-center my-3">
        <span className="inline-flex items-center gap-2 text-sm font-medium text-cyan-400/80 bg-cyan-950/40 border border-cyan-800/30 rounded-lg px-4 py-1.5 animate-pulse">
          🔍 {event.summary}
        </span>
      </div>
    );
  }

  const isUser = event.type === 'user_speech';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-3`}>
      <div
        className={`max-w-[75%] px-6 py-4 ${
          isUser
            ? 'bg-slate-700/80 text-slate-100 rounded-2xl rounded-br-md'
            : 'bg-cyan-900/50 border border-cyan-700/30 text-cyan-50 rounded-2xl rounded-bl-md'
        }`}
      >
        <p className={`text-xs font-semibold mb-1 ${isUser ? 'text-slate-400' : 'text-cyan-400'}`}>
          {isUser ? '📱 Caller' : '🤖 AI Agent'}
        </p>
        <p className="text-lg leading-relaxed whitespace-pre-wrap">{event.text}</p>
        <p className={`mt-2 text-xs ${isUser ? 'text-slate-500' : 'text-cyan-700'}`}>
          {formatTimestamp(event.timestamp)}
        </p>
      </div>
    </div>
  );
}

// ─── Status Badge ────────────────────────────────────────────────────────────

function StatusBadge({ status, durationSeconds }: { status: string; durationSeconds: number | null }) {
  switch (status) {
    case 'active':
      return (
        <span className="inline-flex items-center gap-2 text-sm text-emerald-400 font-medium">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          📞 Call in progress
        </span>
      );
    case 'ended':
      return (
        <span className="inline-flex items-center gap-2 text-sm text-slate-500">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-600" />
          Call ended{durationSeconds != null ? ` (${formatDuration(durationSeconds)})` : ''}
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-2 text-sm text-slate-500">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-600 animate-pulse" />
          Waiting for call…
        </span>
      );
  }
}

// ─── Main Export ─────────────────────────────────────────────────────────────

export function LivePage({ onExit }: { onExit?: () => void }) {
  const { callState } = useTranscriptStream();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Escape key exits Live view
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape' && onExit) onExit();
  }, [onExit]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Smooth auto-scroll on new events
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [callState.events]);

  return (
    <div className="fixed inset-0 bg-slate-950 text-slate-100 flex flex-col overflow-hidden">
      {/* Top bar — subtle branding + phone number + status */}
      <div className="flex items-center justify-between px-8 py-4 border-b border-slate-800/80 bg-slate-900/50 backdrop-blur-sm flex-shrink-0">
        <div className="flex items-center gap-4">
          {onExit && (
            <button
              onClick={onExit}
              className="p-1.5 rounded-lg text-slate-600 hover:text-slate-400 hover:bg-slate-800 transition-colors"
              aria-label="Exit Live view (Escape)"
              title="Back to Runbook (Esc)"
            >
              <ArrowLeftIcon className="w-4 h-4" />
            </button>
          )}
          <span className="text-lg font-bold text-slate-300 tracking-tight">
            47 Doors
          </span>
          <span className="text-slate-700">|</span>
          <div className="flex items-center gap-2 text-slate-400">
            <PhoneIcon className="w-4 h-4" />
            <span className="font-mono text-sm">{PHONE_NUMBER}</span>
          </div>
        </div>
        <StatusBadge status={callState.status} durationSeconds={callState.durationSeconds} />
      </div>

      {/* Transcript area — fills remaining space */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-8 py-6"
        role="log"
        aria-live="polite"
        aria-label="Live phone transcript"
      >
        {callState.events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-20 h-20 bg-slate-800/80 rounded-full flex items-center justify-center mb-6">
              <PhoneIcon className="w-10 h-10 text-slate-600" />
            </div>
            <p className="text-2xl font-light text-slate-500 mb-2">Waiting for call…</p>
            <p className="text-sm text-slate-600">
              Dial <span className="font-mono font-semibold text-slate-400">{PHONE_NUMBER}</span> to begin
            </p>
          </div>
        ) : (
          callState.events.map((evt, i) => (
            <LiveBubble key={`${evt.call_id}-${i}`} event={evt} />
          ))
        )}
      </div>

      {/* Subtle bottom bar */}
      <div className="flex-shrink-0 px-8 py-2 border-t border-slate-800/50 bg-slate-900/30">
        <p className="text-xs text-slate-700 text-center">
          47 Doors — Universal Front Door Support Agent
        </p>
      </div>
    </div>
  );
}
