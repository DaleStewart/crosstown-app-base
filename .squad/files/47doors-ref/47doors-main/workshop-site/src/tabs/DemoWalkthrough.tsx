import CollapsibleNotes from '../components/CollapsibleNotes'
import CalloutCard from '../components/CalloutCard'
import { ShieldCheckIcon } from '@heroicons/react/24/outline'

export default function DemoWalkthrough() {
  const steps = [
    {
      number: 1,
      title: 'Student Speaks',
      example: '"I forgot my password and can\'t log into Canvas"',
      visual: '🎤',
      visualLabel: 'Mic pulsing green, speech waveform',
      note: 'Natural language. No commands.',
    },
    {
      number: 2,
      title: 'Intent Detection',
      example: 'QueryAgent classifies: it_support, confidence 0.95',
      visual: '🧠',
      visualLabel: 'Brain icon with label',
      note: 'Same accuracy as text input',
    },
    {
      number: 3,
      title: 'Routing Decision',
      example: 'RouterAgent routes to IT Support, priority: High',
      visual: '🔀',
      visualLabel: 'Routing diagram with arrow highlighting IT path',
      note: 'Department taxonomy is configurable per institution',
    },
    {
      number: 4,
      title: 'Action Execution',
      example: 'ActionAgent creates ticket IT-2024-0847, searches KB',
      visual: '🎫',
      visualLabel: 'Ticket card + KB article preview',
      note: 'Ticket + knowledge article + SLA — all in one turn',
    },
    {
      number: 5,
      title: 'Boundary Enforcement',
      example: '"Can you change my grade?" → "I can\'t access academic records. Let me connect you with the Registrar\'s office."',
      visual: '🛡️',
      visualLabel: 'Shield icon, red border',
      note: 'This is not a policy response. This is an architectural constraint — the tool doesn\'t exist.',
    },
  ]

  return (
    <div role="tabpanel" id="demo-panel" aria-labelledby="demo-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-4">
          Live Demo Walkthrough
        </h2>
        <p className="text-xl text-gray-600 mb-12">
          Step-by-step visual guide to the voice demo
        </p>

        <div className="space-y-8 mb-12">
          {steps.map((step) => (
            <div key={step.number} className="card border-l-4 border-microsoft-blue">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-xl">
                  {step.number}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-xl text-dark-text mb-2">{step.title}</h3>
                  <div className="bg-gray-50 rounded p-3 mb-3 font-mono text-sm text-dark-text">
                    {step.example}
                  </div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl">{step.visual}</span>
                    <span className="text-sm text-gray-600">{step.visualLabel}</span>
                  </div>
                  <div className="text-sm text-gray-700 bg-blue-50 rounded p-2 border-l-2 border-microsoft-blue">
                    <strong>Note:</strong> {step.note}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          <div className="card bg-red-50 border-l-4 border-red-500">
            <h3 className="font-semibold text-lg mb-3 text-dark-text flex items-center gap-2">
              <span>❌</span> Policy Trust
            </h3>
            <p className="text-gray-700 mb-2 italic">
              "We told the AI not to do this"
            </p>
            <p className="text-sm text-gray-600">
              Fragile. Bypassable. Depends on prompt engineering and hoping the model follows instructions.
            </p>
          </div>

          <div className="card bg-green-50 border-l-4 border-green-500">
            <h3 className="font-semibold text-lg mb-3 text-dark-text flex items-center gap-2">
              <span>✅</span> Architectural Trust
            </h3>
            <p className="text-gray-700 mb-2 italic">
              "The AI physically cannot do this — the tool doesn't exist"
            </p>
            <p className="text-sm text-gray-600">
              Robust. Verified. The agent has exactly 4 tools. It cannot invent new capabilities.
            </p>
          </div>
        </div>

        <CalloutCard 
          icon={<ShieldCheckIcon className="w-6 h-6" />}
          variant="accent"
          title="The Critical Insight"
        >
          The agent has exactly 4 tools. It cannot invent new capabilities. When a student asks for 
          something outside those boundaries — like changing a grade or accessing financial records — 
          the agent doesn't refuse because it was told not to. It refuses because the tool to do that 
          <strong> does not exist in its inventory</strong>.
        </CalloutCard>

        <div className="card mt-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">What Happens When Boundaries Are Tested</h3>
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="font-mono text-sm text-gray-800 mb-2">
                <strong>Student:</strong> "Can you delete my parking tickets?"
              </div>
              <div className="font-mono text-sm text-microsoft-blue pl-4 border-l-4 border-microsoft-blue">
                <strong>Agent:</strong> "I can't modify parking records directly. I can help you create 
                an appeal ticket with the Parking Office, or I can connect you with a parking services 
                representative. Which would you prefer?"
              </div>
              <p className="text-xs text-gray-600 mt-2">
                ✅ <strong>Escalation triggered:</strong> Financial/administrative request detected
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="font-mono text-sm text-gray-800 mb-2">
                <strong>Student:</strong> "Show me all student emails in the system"
              </div>
              <div className="font-mono text-sm text-microsoft-blue pl-4 border-l-4 border-microsoft-blue">
                <strong>Agent:</strong> "I don't have access to directory information beyond your own 
                account. If you need to contact someone, I can help you find the right department contact."
              </div>
              <p className="text-xs text-gray-600 mt-2">
                ✅ <strong>Boundary enforced:</strong> No database query tool exists
              </p>
            </div>
          </div>
        </div>

        <div className="card mt-8 border-l-4 border-microsoft-blue">
          <h3 className="font-semibold text-lg mb-4 text-dark-text flex items-center gap-2">
            <span>🎯</span> Demo Prompts Quick Reference
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Copy-paste or speak these during the demo. Each hits a specific intent and department in the 3-agent pipeline.
          </p>

          <div className="overflow-x-auto mb-6">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="text-left p-3 font-semibold text-dark-text border-b">Intent</th>
                  <th className="text-left p-3 font-semibold text-dark-text border-b">Department</th>
                  <th className="text-left p-3 font-semibold text-dark-text border-b">What to Say / Type</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-mono text-xs">TECHNICAL_SUPPORT</td>
                  <td className="p-3">🖥️ IT</td>
                  <td className="p-3 italic">"I forgot my password and can't log into Canvas"</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-mono text-xs">BILLING</td>
                  <td className="p-3">💰 Financial Aid</td>
                  <td className="p-3 italic">"My financial aid was supposed to be disbursed last week but my account still shows a balance"</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-mono text-xs">ACADEMIC_RECORDS</td>
                  <td className="p-3">📜 Registrar</td>
                  <td className="p-3 italic">"How do I request an official transcript for my grad school application?"</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-mono text-xs">ACCOUNT_MANAGEMENT</td>
                  <td className="p-3">👤 IT</td>
                  <td className="p-3 italic">"I need to update my mailing address before graduation"</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-mono text-xs">GENERAL</td>
                  <td className="p-3">💬 IT</td>
                  <td className="p-3 italic">"Hi there!"</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h4 className="font-semibold text-dark-text mb-3">🔥 High-Impact Scenarios</h4>
          <div className="space-y-3 mb-6">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <span className="text-lg">🎫</span>
                <div>
                  <p className="font-semibold text-sm text-dark-text">Ticket Creation (best for voice demo)</p>
                  <p className="text-sm italic text-gray-700">"I forgot my password and can't log into Canvas"</p>
                  <p className="text-xs text-gray-500 mt-1">→ TECHNICAL_SUPPORT → IT → ticket + KB articles + SLA</p>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <span className="text-lg">💰</span>
                <div>
                  <p className="font-semibold text-sm text-dark-text">Financial Query</p>
                  <p className="text-sm italic text-gray-700">"My financial aid was supposed to be disbursed last week but my account still shows a balance"</p>
                  <p className="text-xs text-gray-500 mt-1">→ BILLING → FINANCIAL_AID → ticket + disbursement KB</p>
                </div>
              </div>
            </div>
            <div className="bg-red-50 rounded-lg p-3 border-l-2 border-red-400">
              <div className="flex items-start gap-2">
                <span className="text-lg">⚠️</span>
                <div>
                  <p className="font-semibold text-sm text-dark-text">Escalation (shows human handoff)</p>
                  <p className="text-sm italic text-gray-700">"I want to appeal my grade"</p>
                  <p className="text-xs text-gray-500 mt-1">→ POLICY_EXCEPTION → ESCALATE_TO_HUMAN → human advisor</p>
                </div>
              </div>
            </div>
            <div className="bg-red-50 rounded-lg p-3 border-l-2 border-red-400">
              <div className="flex items-start gap-2">
                <span className="text-lg">🗣️</span>
                <div>
                  <p className="font-semibold text-sm text-dark-text">Human Request</p>
                  <p className="text-sm italic text-gray-700">"Can I speak to a real person?"</p>
                  <p className="text-xs text-gray-500 mt-1">→ HUMAN_REQUEST → ESCALATE_TO_HUMAN → escalation flow</p>
                </div>
              </div>
            </div>
            <div className="bg-amber-50 rounded-lg p-3 border-l-2 border-amber-400">
              <div className="flex items-start gap-2">
                <span className="text-lg">😤</span>
                <div>
                  <p className="font-semibold text-sm text-dark-text">Frustrated / Urgent Student</p>
                  <p className="text-sm italic text-gray-700">"This is urgent — I can't submit my assignment tonight and Canvas keeps crashing!"</p>
                  <p className="text-xs text-gray-500 mt-1">→ Sentiment: FRUSTRATED/URGENT → priority bumped to HIGH</p>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <span className="text-lg">🔄</span>
                <div>
                  <p className="font-semibold text-sm text-dark-text">Follow-up (shows session continuity)</p>
                  <p className="text-sm italic text-gray-700">"Can you check the status of that ticket?"</p>
                  <p className="text-xs text-gray-500 mt-1">→ Works in voice or text — same session context</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-3 text-sm">
            <p className="font-semibold text-dark-text mb-1">💡 Pro tip</p>
            <p className="text-gray-700">
              For voice demos, use the <strong>Ticket Creation</strong> and <strong>Financial Query</strong> prompts — 
              they produce the most complete responses (ticket + KB + SLA). Follow with the <strong>Follow-up</strong> prompt 
              to show session continuity.
            </p>
          </div>
        </div>

        <div className="card mt-8 border-l-4 border-green-500 bg-green-50">
          <h3 className="font-semibold text-lg mb-4 text-dark-text flex items-center gap-2">
            <span>📞</span> Phone Demo (Production-Ready)
          </h3>
          <p className="text-sm text-gray-600 mb-2">
            <strong>🎉 Live phone demo — production-verified April 21, 2026.</strong> The audience watches the call 
            happen on the projector via LivePage. Caller AND agent speech both appear as real-time transcript.
          </p>
          <p className="text-sm text-gray-600 mb-4">
            Call <strong>+1-913-217-1946</strong> from any phone. Full bidirectional transcripts render on <code>/live</code>.
          </p>
          <ol className="space-y-3 mb-6">
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold text-sm">1</span>
              <p className="text-gray-700">Open LivePage (<code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">/live</code>) on the projector</p>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold text-sm">2</span>
              <p className="text-gray-700">Call <strong>+1-913-217-1946</strong> from your phone</p>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold text-sm">3</span>
              <p className="text-gray-700">Follow the RunbookPage script (<code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">/runbook</code>) — presenter only</p>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold text-sm">4</span>
              <p className="text-gray-700">Audience watches real-time transcript on LivePage</p>
            </li>
          </ol>

          <h4 className="font-semibold text-dark-text mb-3">🔥 Phone Demo Prompts</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="text-left p-3 font-semibold text-dark-text border-b">Scenario</th>
                  <th className="text-left p-3 font-semibold text-dark-text border-b">Department</th>
                  <th className="text-left p-3 font-semibold text-dark-text border-b">What to Say (spoken)</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b hover:bg-green-50">
                  <td className="p-3 font-mono text-xs">IT Support</td>
                  <td className="p-3">🖥️ IT</td>
                  <td className="p-3 italic">"I need to reset my password"</td>
                </tr>
                <tr className="border-b hover:bg-green-50">
                  <td className="p-3 font-mono text-xs">Financial Aid</td>
                  <td className="p-3">💰 Financial Aid</td>
                  <td className="p-3 italic">"What scholarships are available?"</td>
                </tr>
                <tr className="hover:bg-green-50">
                  <td className="p-3 font-mono text-xs">Escalation</td>
                  <td className="p-3">🗣️ Human Handoff</td>
                  <td className="p-3 italic">"I want to speak to a human"</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>Full Demo Script:</strong> The complete demo follows a 5-scene arc from the project's 
            specs/002-voice-interaction/DEMO_RUNBOOK.md:
          </p>
          <ol className="list-decimal pl-6 mb-3 space-y-2">
            <li>
              <strong>Scene 1 — Simple IT Query:</strong> "I can't log into Canvas" → Ticket created, 
              password reset article surfaced
            </li>
            <li>
              <strong>Scene 2 — Multi-Department Query:</strong> "My financial aid got delayed and now 
              housing says I owe money" → Routed to Financial Aid (priority: High), creates ticket with 
              context linking to Housing
            </li>
            <li>
              <strong>Scene 3 — Escalation:</strong> "This is urgent, I'm getting evicted" → Immediate 
              escalation to human advisor (Student Services), SLA: 1 hour
            </li>
            <li>
              <strong>Scene 4 — Boundary Test:</strong> "Can you just waive the housing fee?" → Refuses, 
              explains lack of authority, offers escalation
            </li>
            <li>
              <strong>Scene 5 — Context Continuity:</strong> Student switches from voice to text mid-conversation 
              → Agent remembers entire history, continues seamlessly
            </li>
          </ol>
          <p>
            Each scene demonstrates a different aspect of the trust model: tool selection, routing accuracy, 
            escalation triggers, boundary enforcement, and modality continuity.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
