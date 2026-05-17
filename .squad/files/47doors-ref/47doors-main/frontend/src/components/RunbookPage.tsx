/**
 * Runbook page: Sean's private cheat sheet during live demos.
 * Contains phone number, demo questions table, and presenter tips.
 * Audience does NOT see this — it stays on the presenter's laptop.
 */

import { PhoneIcon, LightBulbIcon } from '@heroicons/react/24/solid';

const PHONE_NUMBER = '+1 (913) 217-1946';

const DEMO_QUESTIONS: { emoji: string; question: string; shows: string }[] = [
  { emoji: '🎫', question: "I forgot my password and can't log into Canvas", shows: 'Ticket creation' },
  { emoji: '💰', question: 'My financial aid was supposed to be disbursed last week but my account still shows a balance', shows: 'Financial routing' },
  { emoji: '📜', question: 'How do I request an official transcript for my grad school application?', shows: 'KB search + registrar' },
  { emoji: '👤', question: 'I need to update my mailing address before graduation', shows: 'Account management' },
  { emoji: '⚠️', question: 'I want to appeal my grade', shows: 'Escalation' },
  { emoji: '🤝', question: 'Can I speak to a real person?', shows: 'Human handoff' },
  { emoji: '😤', question: "This is urgent — I can't submit my assignment tonight and Canvas keeps crashing!", shows: 'Urgent + sentiment' },
  { emoji: '🔄', question: 'Can you check the status of that ticket?', shows: 'Ticket lookup' },
  { emoji: '👋', question: 'Hi there!', shows: 'Greeting' },
];

const TIPS = [
  'Start with the greeting (#9) to warm up, then escalate complexity.',
  'Financial aid (#2) and transcript (#3) are the strongest KB demos.',
  'Use the urgent question (#7) to show sentiment detection.',
  'After creating a ticket, follow up with #8 to show ticket lookup.',
  'Human handoff (#6) is a great closer — shows graceful escalation.',
];

export function RunbookPage() {
  return (
    <div className="px-4 py-6 space-y-6 w-full">
      <section className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Header bar */}
        <div className="bg-primary-600 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white tracking-tight">
            📋 Demo Runbook — Private
          </h2>
          <span className="text-xs font-medium text-primary-200 bg-primary-700 rounded-full px-3 py-1">
            Presenter Only
          </span>
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
            Call the number above and ask any of these questions. The Live tab (on the projector) will show the transcript in real time.
          </p>

          {/* Questions table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm" role="table">
              <thead>
                <tr className="border-b border-gray-200 text-left">
                  <th className="py-2 pr-3 font-semibold text-gray-500 w-8">#</th>
                  <th className="py-2 pr-3 font-semibold text-gray-500">Question</th>
                  <th className="py-2 font-semibold text-gray-500 w-48">What it triggers</th>
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

      {/* Presenter tips */}
      <section className="bg-amber-50 rounded-2xl border border-amber-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-amber-200 flex items-center gap-2">
          <LightBulbIcon className="w-5 h-5 text-amber-600" />
          <h3 className="text-sm font-semibold text-amber-800">Demo Tips</h3>
        </div>
        <ul className="px-6 py-4 space-y-2">
          {TIPS.map((tip, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-amber-900">
              <span className="text-amber-500 mt-0.5 flex-shrink-0">•</span>
              {tip}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
