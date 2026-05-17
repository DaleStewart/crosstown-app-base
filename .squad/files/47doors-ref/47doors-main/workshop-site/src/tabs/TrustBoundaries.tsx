import CollapsibleNotes from '../components/CollapsibleNotes'
import CalloutCard from '../components/CalloutCard'
import { 
  LockClosedIcon, 
  UserIcon, 
  ShieldCheckIcon, 
  CircleStackIcon,
  BeakerIcon,
  SignalIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

export default function TrustBoundaries() {
  const principles = [
    {
      icon: <LockClosedIcon className="w-8 h-8" />,
      title: 'Bounded Authority',
      description: 'Agent can only use approved tools. It has exactly 4 tools — no more, no less.',
    },
    {
      icon: <UserIcon className="w-8 h-8" />,
      title: 'Human Escalation',
      description: 'Agent knows when to step aside and connect the student to a human expert.',
    },
    {
      icon: <ShieldCheckIcon className="w-8 h-8" />,
      title: 'Privacy-First',
      description: 'No raw audio stored. PII filtered before logging. Audit-ready transcripts only.',
    },
    {
      icon: <CircleStackIcon className="w-8 h-8" />,
      title: 'Stateful Context',
      description: 'Remembers across turns and modalities. Voice and text share the same session.',
    },
    {
      icon: <BeakerIcon className="w-8 h-8" />,
      title: 'Test-First',
      description: 'Every behavior verified before deployment. 76+ voice tests, 50+ pipeline tests.',
    },
    {
      icon: <SignalIcon className="w-8 h-8" />,
      title: 'Accessibility',
      description: 'Additive, not replacement. Voice augments text — when voice fails, text works.',
    },
    {
      icon: <ArrowPathIcon className="w-8 h-8" />,
      title: 'Graceful Degradation',
      description: 'When features fail, core functionality remains. No single point of failure.',
    },
  ]

  return (
    <div role="tabpanel" id="trust-panel" aria-labelledby="trust-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-4">
          Trust & Boundaries
        </h2>
        <p className="text-xl text-gray-600 mb-12">
          Why trust is architectural, not just policy
        </p>

        <CalloutCard variant="accent" title="Central Metaphor">
          Trust is not a policy document. Trust is architecture.
        </CalloutCard>

        <div className="mt-12 mb-8">
          <h3 className="font-semibold text-2xl mb-6 text-dark-text text-center">
            Seven Constitutional Principles
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            {principles.map((principle, index) => (
              <div key={index} className="card">
                <div className="flex items-start gap-4">
                  <div className="text-microsoft-blue flex-shrink-0">
                    {principle.icon}
                  </div>
                  <div>
                    <h4 className="font-semibold text-lg mb-2 text-dark-text">
                      {index + 1}. {principle.title}
                    </h4>
                    <p className="text-gray-700 text-sm leading-relaxed">
                      {principle.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mt-12">
          <div className="card border-l-4 border-green-500">
            <h3 className="font-semibold text-lg mb-4 text-dark-text">✅ What the Agent CAN Do</h3>
            <ul className="space-y-2 text-gray-700">
              <li>• Create support tickets in departmental systems</li>
              <li>• Search the knowledge base for relevant articles</li>
              <li>• Route queries to the appropriate department</li>
              <li>• Escalate complex issues to human experts</li>
              <li>• Remember context across text and voice interactions</li>
              <li>• Provide SLA information and ticket status</li>
            </ul>
          </div>

          <div className="card border-l-4 border-red-500">
            <h3 className="font-semibold text-lg mb-4 text-dark-text">❌ What the Agent CANNOT Do</h3>
            <ul className="space-y-2 text-gray-700">
              <li>• Access student academic records directly</li>
              <li>• Store or replay raw audio recordings</li>
              <li>• Skip escalation when required by policy</li>
              <li>• Repeat PII in responses (filtered automatically)</li>
              <li>• Bypass constitutional boundaries</li>
              <li>• Invent new capabilities beyond its 4 tools</li>
            </ul>
          </div>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>Why This Matters:</strong> University IT teams often ask, "How do we know the AI won't 
            do something dangerous?" The answer is architectural constraints, not trust.
          </p>
          <p className="mb-3">
            The constitution isn't a suggestion — it's <strong>enforced in code</strong>. Every tool call, 
            every response, every escalation follows these seven principles. The agent cannot bypass them 
            because the tools to bypass them don't exist.
          </p>
          <p className="mb-3">
            <strong>Example:</strong> A student asks "Can you change my grade?" The agent doesn't refuse 
            because it was told not to — it refuses because the <code>change_grade</code> tool doesn't exist 
            in its tool inventory. That's architectural trust.
          </p>
          <p>
            This is what makes the 47 Doors agent trustworthy for institutional deployment. Policy documents 
            can be ignored. Architecture cannot.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
