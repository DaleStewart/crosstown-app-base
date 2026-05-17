import CollapsibleNotes from '../components/CollapsibleNotes'
import CalloutCard from '../components/CalloutCard'
import { LightBulbIcon } from '@heroicons/react/24/outline'

export default function ChatbotsToAgents() {
  return (
    <div role="tabpanel" id="chatbots-to-agents-panel" aria-labelledby="chatbots-to-agents-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-8">
          From Chatbots to Agents
        </h2>

        <div className="overflow-x-auto mb-12">
          <table className="w-full bg-white rounded-lg shadow-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-dark-text">Capability</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-dark-text">Chatbot</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-microsoft-blue">Agent</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Intent</td>
                <td className="px-6 py-4 text-sm text-gray-700">Pattern match</td>
                <td className="px-6 py-4 text-sm text-gray-700 font-medium">Understands context</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Memory</td>
                <td className="px-6 py-4 text-sm text-gray-700">None/session only</td>
                <td className="px-6 py-4 text-sm text-gray-700 font-medium">Persistent, shared</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Actions</td>
                <td className="px-6 py-4 text-sm text-gray-700">Pre-scripted responses</td>
                <td className="px-6 py-4 text-sm text-gray-700 font-medium">Tool-calling, dynamic</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Boundaries</td>
                <td className="px-6 py-4 text-sm text-gray-700">Rule-based</td>
                <td className="px-6 py-4 text-sm text-gray-700 font-medium">Constitutional</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Trust</td>
                <td className="px-6 py-4 text-sm text-gray-700">"Hope it works"</td>
                <td className="px-6 py-4 text-sm text-gray-700 font-medium">Architecturally enforced</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="mb-12">
          <h3 className="font-semibold text-xl mb-6 text-dark-text text-center">Evolution Timeline</h3>
          <div className="flex items-center justify-between bg-white rounded-lg shadow-sm p-8">
            <div className="text-center flex-1">
              <div className="text-3xl mb-2">📄</div>
              <div className="text-sm font-medium text-gray-900">FAQ Bot</div>
              <div className="text-xs text-gray-500 mt-1">Static answers</div>
            </div>
            <div className="text-2xl text-gray-400">→</div>
            <div className="text-center flex-1">
              <div className="text-3xl mb-2">💬</div>
              <div className="text-sm font-medium text-gray-900">Chatbot</div>
              <div className="text-xs text-gray-500 mt-1">Pattern matching</div>
            </div>
            <div className="text-2xl text-gray-400">→</div>
            <div className="text-center flex-1">
              <div className="text-3xl mb-2">🤝</div>
              <div className="text-sm font-medium text-gray-900">Copilot</div>
              <div className="text-xs text-gray-500 mt-1">Assisted work</div>
            </div>
            <div className="text-2xl text-gray-400">→</div>
            <div className="text-center flex-1 bg-microsoft-blue/5 rounded-lg p-4">
              <div className="text-3xl mb-2">🤖</div>
              <div className="text-sm font-medium text-microsoft-blue">Agent</div>
              <div className="text-xs text-gray-600 mt-1">Autonomous action</div>
            </div>
          </div>
        </div>

        <CalloutCard icon={<LightBulbIcon className="w-6 h-6" />} title="What to Notice">
          Agents don't just answer questions — they take actions with boundaries. An agent can create 
          a ticket, search a knowledge base, route to the right department, and escalate to a human when 
          needed. The difference is autonomy within architectural constraints.
        </CalloutCard>

        <div className="card mt-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">Key Insight</h3>
          <p className="text-gray-700 text-lg leading-relaxed">
            An agent is software that can <strong>perceive</strong> (understand what the student needs), 
            <strong>decide</strong> (route to the right department), and <strong>act</strong> (create tickets, 
            search knowledge bases) — all within defined constitutional boundaries.
          </p>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            Most universities have tried chatbots. They answer FAQs like "What are library hours?" or 
            "How do I reset my password?" That's useful, but limited.
          </p>
          <p className="mb-3">
            Agents go further. They don't just answer — they <strong>do</strong>. An agent can:
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li>Create a support ticket in the right department's system</li>
            <li>Search the knowledge base for relevant articles</li>
            <li>Route complex queries to the appropriate human expert</li>
            <li>Remember context across conversations (text and voice)</li>
            <li>Escalate when it encounters something it cannot safely handle</li>
          </ul>
          <p>
            But with that power comes the need for <strong>architectural trust</strong>. The next tab 
            explains how we build that trust through constitutional principles, not hope.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
