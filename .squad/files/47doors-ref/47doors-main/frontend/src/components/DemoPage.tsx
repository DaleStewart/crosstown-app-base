/**
 * Demo page: runbook + live phone transcript viewer.
 * Built for executive demos — polished, single-page layout.
 */

import { useEffect, useRef } from 'react';
import { PhoneIcon } from '@heroicons/react/24/solid';
import { useTranscriptStream } from '../hooks/useTranscriptStream';
import type { TranscriptEvent } from '../types/demo';

// ─── Constants ───────────────────────────────────────────────────────────────

const PHONE_NUMBER = '+1 (913) 217-1946';

const DEMO_QUESTIONS: { emoji: string; question: string; shows: string }[] = [
  { emoji: '🎫', question: 'I forgot my password and can\'t log into Canvas', shows: 'Ticket creation' },
  { emoji: '💰', question: 'My financial aid was supposed to be disbursed last week but my account still shows a balance', shows: 'Financial routing' },
  { emoji: '📜', question: 'How do I request an official transcript for my grad school application?', shows: 'KB search + registrar' },
  { emoji: '👤', question: 'I need to update my mailing address before graduation', shows: 'Account management' },
  { emoji: '⚠️', question: 'I want to appeal my grade', shows: 'Escalation' },
  { emoji: '🤝', question: 'Can I speak to a real person?', shows: 'Human handoff' },
  { emoji: '😤', question: 'This is urgent — I can\'t submit my assignment tonight and Canvas keeps crashing!', shows: 'Urgent + sentiment' },
  { emoji: '🔄', question: 'Can you check the status of that ticket?', shows: 'Ticket lookup' },
  { emoji: '👋', question: 'Hi there!', shows: 'Greeting' },
];

// ─── Helper: format timestamp ────────────────────────────────────────────────

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

// ─── Runbook Section ─────────────────────────────────────────────────────────

function Runbook() {
  return (
    <section className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header bar */}
      <div className="bg-primary-600 px-6 py-4">
        <h2 className="text-xl font-bold text-white tracking-tight">
          47 Doors — Demo Runbook
        </h2>
      </div>

      <div className="p-6 space-y-6">
        {/* Phone number CTA */}
        <div className="flex items-center gap-4 bg-primary-50 border border-primary-200 rounded-xl px-6 py-5">
          <div className="flex-shrink-0 w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center">
            <PhoneIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-sm font-medium text-primary-700">Call this number:</p>
            <p className="text-3xl font-bold text-primary-900 tracking-tight font-mono">
              {PHONE_NUMBER}
            </p>
          </div>
        </div>

        <p className="text-sm text-gray-600">
          Call the number above and ask any of these questions:
        </p>

        {/* Questions table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm" role="table">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="py-2 pr-3 font-semibold text-gray-500 w-8">#</th>
                <th className="py-2 pr-3 font-semibold text-gray-500">Question</th>
                <th className="py-2 font-semibold text-gray-500 w-48">What it shows</th>
              </tr>
            </thead>
            <tbody>
              {DEMO_QUESTIONS.map((q, i) => (
                <tr key={i} className="border-b border-gray-100 last:border-0 hover:bg-gray-50 transition-colors">
                  <td className="py-3 pr-3 text-gray-400 font-mono text-xs">{i + 1}</td>
                  <td className="py-3 pr-3 text-gray-800">"{q.question}"</td>
                  <td className="py-3">
                    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-full px-3 py-1">
                      <span>{q.emoji}</span> {q.shows}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

// ─── Transcript Event Rendering ──────────────────────────────────────────────

function TranscriptBubble({ event }: { event: TranscriptEvent }) {
  if (event.type === 'call_started') {
    return (
      <div className="flex justify-center my-3">
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-success-700 bg-success-50 border border-success-200 rounded-full px-4 py-1.5">
          📞 Call connected
          <span className="text-success-500">•</span>
          {formatTimestamp(event.timestamp)}
        </span>
      </div>
    );
  }

  if (event.type === 'call_ended') {
    return (
      <div className="flex justify-center my-3">
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 bg-gray-100 border border-gray-200 rounded-full px-4 py-1.5">
          Call ended • {formatDuration(event.duration_seconds)}
        </span>
      </div>
    );
  }

  if (event.type === 'tool_call') {
    return (
      <div className="flex justify-center my-2">
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-primary-700 bg-primary-50 border border-primary-200 rounded-lg px-3 py-1.5">
          🔍 {event.summary}
        </span>
      </div>
    );
  }

  const isUser = event.type === 'user_speech';

  return (
    <div className={`message-bubble flex ${isUser ? 'justify-end' : 'justify-start'} my-1.5`}>
      <div
        className={`max-w-[80%] px-4 py-2.5 ${
          isUser
            ? 'bg-primary-600 text-white rounded-2xl rounded-br-md'
            : 'bg-white border border-gray-200 text-gray-900 rounded-2xl rounded-bl-md shadow-sm'
        }`}
      >
        <p className="text-xs font-semibold mb-0.5 opacity-70">
          {isUser ? '📱 Caller' : '🤖 AI Agent'}
        </p>
        <p className="text-sm whitespace-pre-wrap">{event.text}</p>
        <p className={`mt-1 text-xs ${isUser ? 'text-primary-200' : 'text-gray-400'}`}>
          {formatTimestamp(event.timestamp)}
        </p>
      </div>
    </div>
  );
}

// ─── Live Conversation Section ───────────────────────────────────────────────

function LiveConversation() {
  const { callState } = useTranscriptStream();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new events
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [callState.events]);

  const statusLabel = (() => {
    switch (callState.status) {
      case 'idle':
        return (
          <span className="inline-flex items-center gap-1.5 text-sm text-gray-500">
            <span className="w-2 h-2 rounded-full bg-gray-300 animate-pulse" />
            Waiting for call…
          </span>
        );
      case 'active':
        return (
          <span className="inline-flex items-center gap-1.5 text-sm text-success-600 font-medium">
            <span className="w-2 h-2 rounded-full bg-success-500 animate-pulse" />
            📞 Call in progress
          </span>
        );
      case 'ended':
        return (
          <span className="inline-flex items-center gap-1.5 text-sm text-gray-500">
            <span className="w-2 h-2 rounded-full bg-gray-400" />
            Call ended{callState.durationSeconds != null ? ` (${formatDuration(callState.durationSeconds)})` : ''}
          </span>
        );
    }
  })();

  return (
    <section className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden flex flex-col" style={{ minHeight: '400px' }}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">Live Phone Conversation</h2>
        {statusLabel}
      </div>

      {/* Transcript area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-6 py-4"
        role="log"
        aria-live="polite"
        aria-label="Live phone transcript"
      >
        {callState.events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-16">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <PhoneIcon className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-gray-500 text-sm">No active call.</p>
            <p className="text-gray-400 text-xs mt-1">
              Dial <span className="font-mono font-semibold text-gray-600">{PHONE_NUMBER}</span> to start a conversation.
            </p>
          </div>
        ) : (
          callState.events.map((evt, i) => (
            <TranscriptBubble key={`${evt.call_id}-${i}`} event={evt} />
          ))
        )}
      </div>
    </section>
  );
}

// ─── Main Export ─────────────────────────────────────────────────────────────

export function DemoPage() {
  return (
    <div className="px-4 py-6 space-y-6 w-full">
      <Runbook />
      <LiveConversation />
    </div>
  );
}
