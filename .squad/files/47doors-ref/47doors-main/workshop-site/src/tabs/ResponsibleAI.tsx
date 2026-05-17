import CollapsibleNotes from '../components/CollapsibleNotes'
import { MagnifyingGlassIcon, ShieldCheckIcon, UserGroupIcon } from '@heroicons/react/24/outline'

export default function ResponsibleAI() {
  return (
    <div role="tabpanel" id="responsible-ai-panel" aria-labelledby="responsible-ai-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-4">
          Responsible AI in Practice
        </h2>
        <p className="text-xl text-gray-600 mb-12">
          Concrete governance, not abstract principles
        </p>

        <div className="bg-microsoft-blue/5 border-l-4 border-microsoft-blue p-6 rounded-r-lg mb-12">
          <p className="text-xl font-medium text-dark-text">
            Responsible AI Is a Build Decision, Not a Review Step
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <MagnifyingGlassIcon className="w-8 h-8 text-microsoft-blue" />
              <h3 className="font-semibold text-xl text-dark-text">Transparency</h3>
            </div>
            <p className="text-gray-700 mb-3">
              Every decision is auditable. Every tool call, routing decision, and escalation is logged 
              with input_modality, session ID, and filtered content.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Session traces for all interactions</li>
              <li>• Input modality logged (text/voice)</li>
              <li>• PII-filtered transcripts only</li>
              <li>• Tool call arguments and results</li>
            </ul>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheckIcon className="w-8 h-8 text-microsoft-blue" />
              <h3 className="font-semibold text-xl text-dark-text">Safety</h3>
            </div>
            <p className="text-gray-700 mb-3">
              Bounded tools, escalation triggers, and PII filtering enforce safety at the architecture level, 
              not just policy.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Exactly 4 tools (no more, no less)</li>
              <li>• Automatic escalation keywords</li>
              <li>• PII redaction before logging</li>
              <li>• No raw audio storage</li>
            </ul>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <UserGroupIcon className="w-8 h-8 text-microsoft-blue" />
              <h3 className="font-semibold text-xl text-dark-text">Equity</h3>
            </div>
            <p className="text-gray-700 mb-3">
              Voice AND text, keyboard navigation, screen reader support. Accessibility is not optional — 
              it's architectural.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Voice is additive, not replacement</li>
              <li>• Keyboard-only operation</li>
              <li>• ARIA labels for screen readers</li>
              <li>• Transcripts always visible</li>
            </ul>
          </div>
        </div>

        <div className="card mb-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">Audit Trail Visualization</h3>
          <p className="text-sm text-gray-600 mb-4">
            What a log entry looks like — every interaction is traceable:
          </p>
          <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-xs font-mono">
{`{
  "session_id": "abc-123",
  "timestamp": "2026-03-19T14:00:00Z",
  "input_modality": "voice",
  "user_input": "[PII filtered] password reset request",
  "intent": "it_support",
  "confidence": 0.95,
  "department": "IT Support",
  "priority": "high",
  "action": "create_ticket",
  "ticket_id": "IT-2024-0847",
  "kb_articles": ["KB-1234: Password Reset Guide"],
  "pii_filtered": true,
  "tool_calls": [
    {
      "tool": "analyze_and_route_query",
      "duration_ms": 234
    },
    {
      "tool": "create_ticket",
      "duration_ms": 189
    },
    {
      "tool": "search_knowledge_base",
      "duration_ms": 145
    }
  ]
}`}
          </pre>
        </div>

        <div className="card mb-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">Health Check Dashboard</h3>
          <p className="text-sm text-gray-600 mb-4">
            What administrators see — service status at a glance:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
              <div className="text-2xl mb-1">✅</div>
              <div className="text-xs font-semibold text-gray-900">LLM Service</div>
              <div className="text-xs text-green-600">Operational</div>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
              <div className="text-2xl mb-1">✅</div>
              <div className="text-xs font-semibold text-gray-900">Ticketing</div>
              <div className="text-xs text-green-600">Operational</div>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
              <div className="text-2xl mb-1">✅</div>
              <div className="text-xs font-semibold text-gray-900">Knowledge Base</div>
              <div className="text-xs text-green-600">Operational</div>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
              <div className="text-2xl mb-1">✅</div>
              <div className="text-xs font-semibold text-gray-900">Session Store</div>
              <div className="text-xs text-green-600">Operational</div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
            <div className="text-sm font-semibold mb-1 text-dark-text">
              Voice Availability: <span className="text-microsoft-blue">GET /api/realtime/availability</span>
            </div>
            <div className="text-xs text-gray-600">
              Returns <code>{"{ \"available\": true, \"reason\": \"\" }"}</code> when voice is enabled; 
              frontend hides mic button when unavailable
            </div>
          </div>
        </div>

        <div className="card mb-8 border-l-4 border-iu-crimson">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">Graceful Degradation Demo</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-4 p-3 bg-gray-50 rounded">
              <div className="text-2xl">🎤</div>
              <div className="flex-1">
                <div className="font-medium text-sm text-gray-900">Voice Enabled</div>
                <div className="text-xs text-gray-600">Mic button visible, WebRTC active</div>
              </div>
              <div className="text-green-600 font-bold">ON</div>
            </div>
            <div className="text-center text-gray-400">↓ Voice service unavailable</div>
            <div className="flex items-center gap-4 p-3 bg-gray-50 rounded">
              <div className="text-2xl">💬</div>
              <div className="flex-1">
                <div className="font-medium text-sm text-gray-900">Voice Disabled → Text Works</div>
                <div className="text-xs text-gray-600">Mic button hidden, chat interface fully functional</div>
              </div>
              <div className="text-microsoft-blue font-bold">DEGRADED</div>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-4 bg-blue-50 p-3 rounded">
            <strong>Constitutional Principle VI:</strong> Accessibility is additive. When voice is OFF, 
            the mic button disappears, but text chat works perfectly. No feature loss for core functionality.
          </p>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>University IT teams ask:</strong> "How do we know what the AI is doing?"
          </p>
          <p className="mb-3">
            The answer is <strong>architectural transparency</strong>. Every tool call, every routing decision, 
            every escalation is logged with:
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li>The modality (voice or text)</li>
            <li>The session ID (for tracing conversations)</li>
            <li>PII-filtered content (no raw audio, no SSNs, no sensitive data)</li>
            <li>Tool execution time and results</li>
            <li>Department routing and priority assignment</li>
          </ul>
          <p className="mb-3">
            This isn't a "trust us" model. It's a "verify everything" model. Administrators can:
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li>Audit any session by ID</li>
            <li>Search logs for specific tool calls or departments</li>
            <li>Track escalation patterns and response times</li>
            <li>Monitor PII filtering effectiveness</li>
            <li>Check service health in real-time</li>
          </ul>
          <p>
            This is what makes Responsible AI <strong>operational</strong>, not aspirational. It's built 
            into the architecture, logged at every step, and verified before deployment.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
