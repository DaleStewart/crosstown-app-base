import { useState } from 'react'
import CollapsibleNotes from '../components/CollapsibleNotes'

export default function YourFirstAgent() {
  const [agentName, setAgentName] = useState('')
  const [agentOwns, setAgentOwns] = useState('')
  const [agentNever, setAgentNever] = useState('')

  const exampleOwns = [
    'IT Password Resets',
    'Financial Aid FAQs',
    'Housing Applications',
    'Library Resources',
    'Course Registration'
  ]

  const exampleNever = [
    'Change grades',
    'Access financial records',
    'Share student PII',
    'Override faculty decisions',
    'Approve refunds'
  ]

  return (
    <div role="tabpanel" id="your-first-agent-panel" aria-labelledby="your-first-agent-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-2">
          Design Your First Agent — Right Now
        </h2>
        <p className="text-xl text-gray-600 mb-8">
          Three decisions. Five minutes. No code required.
        </p>

        <div className="bg-microsoft-blue/5 border-l-4 border-microsoft-blue p-6 rounded-r-lg mb-12">
          <p className="text-lg text-dark-text">
            This exercise captures the three most important design decisions for any agent: 
            <strong> identity</strong>, <strong>scope</strong>, and <strong>boundaries</strong>.
          </p>
        </div>

        <div className="space-y-8 mb-12">
          {/* Step 1 */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold">
                1
              </div>
              <h3 className="font-semibold text-xl text-dark-text">Name Your Agent</h3>
            </div>
            <input
              type="text"
              value={agentName}
              onChange={(e) => setAgentName(e.target.value)}
              placeholder="e.g., Advisr, FinAidBot, LibraryGuide"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-microsoft-blue focus:outline-none text-lg"
              aria-label="Agent name"
            />
            <p className="text-sm text-gray-600 mt-2">
              💡 <strong>Hint:</strong> Pick a name that tells students what it does
            </p>
          </div>

          {/* Step 2 */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold">
                2
              </div>
              <h3 className="font-semibold text-xl text-dark-text">One Thing It Owns</h3>
            </div>
            <input
              type="text"
              value={agentOwns}
              onChange={(e) => setAgentOwns(e.target.value)}
              placeholder="e.g., Course registration questions"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-microsoft-blue focus:outline-none text-lg mb-3"
              aria-label="What the agent owns"
            />
            <p className="text-sm text-gray-600 mb-3">
              💡 <strong>Hint:</strong> Agents work best with focused scope
            </p>
            <div className="flex flex-wrap gap-2">
              {exampleOwns.map((example, i) => (
                <button
                  key={i}
                  onClick={() => setAgentOwns(example)}
                  className="px-3 py-1 bg-gray-100 hover:bg-microsoft-blue hover:text-white rounded-full text-sm transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Step 3 */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold">
                3
              </div>
              <h3 className="font-semibold text-xl text-dark-text">One Thing It Must Never Do</h3>
            </div>
            <input
              type="text"
              value={agentNever}
              onChange={(e) => setAgentNever(e.target.value)}
              placeholder="e.g., Access student grades"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-microsoft-blue focus:outline-none text-lg mb-3"
              aria-label="What the agent must never do"
            />
            <p className="text-sm text-gray-600 mb-3">
              💡 <strong>Hint:</strong> This is your constitutional boundary
            </p>
            <div className="flex flex-wrap gap-2">
              {exampleNever.map((example, i) => (
                <button
                  key={i}
                  onClick={() => setAgentNever(example)}
                  className="px-3 py-1 bg-gray-100 hover:bg-iu-crimson hover:text-white rounded-full text-sm transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Agent Card */}
        {(agentName || agentOwns || agentNever) && (
          <div className="card border-2 border-microsoft-blue bg-microsoft-blue/5 mb-8">
            <h3 className="font-semibold text-lg mb-4 text-dark-text text-center">Your Agent Card</h3>
            <div className="bg-white rounded-lg p-6 font-mono text-sm border-2 border-gray-200">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-2xl">🤖</span>
                <span className="font-bold text-lg text-microsoft-blue">
                  {agentName || '[Agent Name]'}
                </span>
              </div>
              <div className="space-y-2 text-gray-700">
                <div>
                  <span className="font-semibold text-dark-text">Owns:</span>{' '}
                  {agentOwns || '[What it owns]'}
                </div>
                <div>
                  <span className="font-semibold text-dark-text">Never:</span>{' '}
                  {agentNever || '[What it must never do]'}
                </div>
              </div>
              <div className="border-t border-gray-200 mt-4 pt-4 space-y-1 text-xs text-gray-600">
                <div>Trust Model: Constitutional</div>
                <div>Architecture: 3-Agent Pipeline</div>
              </div>
            </div>
          </div>
        )}

        {/* What's Next */}
        <div className="card bg-gray-50">
          <h3 className="font-semibold text-xl mb-6 text-dark-text">What's Next?</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-3xl mb-3">🛠️</div>
              <h4 className="font-semibold text-sm mb-2 text-dark-text">Build It</h4>
              <p className="text-xs text-gray-700 mb-3">
                Clone the 47 Doors repo and customize the routing table with your agent's scope
              </p>
              <code className="text-xs bg-gray-900 text-green-400 p-2 rounded block">
                git clone 47doors
              </code>
            </div>

            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-3xl mb-3">🧪</div>
              <h4 className="font-semibold text-sm mb-2 text-dark-text">Test It</h4>
              <p className="text-xs text-gray-700 mb-3">
                Run the mock mode locally — no Azure credentials needed
              </p>
              <code className="text-xs bg-gray-900 text-green-400 p-2 rounded block">
                npm run dev
              </code>
            </div>

            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-3xl mb-3">☁️</div>
              <h4 className="font-semibold text-sm mb-2 text-dark-text">Deploy It</h4>
              <p className="text-xs text-gray-700 mb-3">
                azd up — live on Azure in 5 minutes
              </p>
              <code className="text-xs bg-gray-900 text-green-400 p-2 rounded block">
                azd up
              </code>
            </div>
          </div>
        </div>

        <div className="mt-8 p-6 bg-microsoft-blue text-white rounded-lg">
          <h3 className="font-semibold text-lg mb-3">🎓 Ready to Learn More?</h3>
          <p className="text-sm mb-4">
            The 47 Doors project is open source and production-ready. Whether you're piloting with a single 
            department or deploying campus-wide, the architecture is designed to scale.
          </p>
          <div className="flex gap-4">
            <a 
              href="https://github.com/microsoft/47doors" 
              className="px-4 py-2 bg-white text-microsoft-blue rounded-md font-medium hover:bg-gray-100 transition-colors text-sm"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
            <a 
              href="https://aka.ms/47doors" 
              className="px-4 py-2 bg-white/20 text-white rounded-md font-medium hover:bg-white/30 transition-colors text-sm"
              target="_blank"
              rel="noopener noreferrer"
            >
              Documentation
            </a>
          </div>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>This exercise captures the essence of agent design.</strong> Every agent — whether 
            it's for IT support, financial aid, or library services — needs these three elements:
          </p>
          <ol className="list-decimal pl-6 mb-3 space-y-2">
            <li>
              <strong>Identity (Name):</strong> What do students call it? The name should be clear, 
              memorable, and descriptive of its purpose.
            </li>
            <li>
              <strong>Scope (Owns):</strong> What specific domain does it handle? Narrow scope makes the 
              agent more accurate and easier to test. "IT password resets" is better than "all IT questions."
            </li>
            <li>
              <strong>Boundaries (Never):</strong> What must it never do? This is your constitutional 
              constraint. It's enforced architecturally — the tools to violate this boundary don't exist.
            </li>
          </ol>
          <p className="mb-3">
            These three decisions map directly to the 47 Doors architecture:
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li><strong>Identity</strong> → System prompt and voice persona</li>
            <li><strong>Scope</strong> → Routing table and intent classification</li>
            <li><strong>Boundaries</strong> → Tool inventory and constitutional principles</li>
          </ul>
          <p>
            Once you've defined these three things, you're ready to build, test, and deploy your agent 
            using the 47 Doors architecture.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
