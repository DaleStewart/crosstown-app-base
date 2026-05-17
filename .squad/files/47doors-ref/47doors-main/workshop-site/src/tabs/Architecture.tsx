import CollapsibleNotes from '../components/CollapsibleNotes'
import CalloutCard from '../components/CalloutCard'
import DiagramSVG from '../components/DiagramSVG'

export default function Architecture() {
  const agents = [
    {
      name: 'QueryAgent',
      role: 'Understands what the student needs',
      responsibility: 'Intent detection and context analysis',
      output: 'Classified intent (it_support, financial_aid, housing, etc.) with confidence score',
    },
    {
      name: 'RouterAgent',
      role: 'Knows where to send it',
      responsibility: 'Department routing and priority assignment',
      output: 'Target department, priority level (low/medium/high), and routing justification',
    },
    {
      name: 'ActionAgent',
      role: 'Gets it done',
      responsibility: 'Executes actions via tool calls',
      output: 'Ticket creation, knowledge base search, or escalation to human',
    },
  ]

  const tools = [
    { name: 'analyze_and_route_query', purpose: 'Intent detection and department routing' },
    { name: 'search_knowledge_base', purpose: 'Find relevant help articles' },
    { name: 'create_ticket', purpose: 'Generate support tickets in departmental systems' },
    { name: 'escalate_to_human', purpose: 'Connect student to human expert' },
  ]

  return (
    <div role="tabpanel" id="architecture-panel" aria-labelledby="architecture-tab">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-4">
          Architecture: The Three-Agent Pattern
        </h2>
        <p className="text-xl text-gray-600 mb-12">
          Separation of concerns makes the system testable, auditable, and safe
        </p>

        <DiagramSVG 
          title="Three-Agent Pipeline"
          description="Student query flows through three specialized agents before returning a response"
          viewBox="0 0 900 300"
        >
          {/* Student */}
          <circle cx="50" cy="150" r="30" fill="#0078D4" />
          <text x="50" y="155" textAnchor="middle" className="diagram-text" fill="white" fontSize="12">
            Student
          </text>

          {/* Arrow to QueryAgent */}
          <path d="M 85 150 L 130 150" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* QueryAgent */}
          <rect x="135" y="110" width="120" height="80" fill="#F3F2F1" stroke="#0078D4" strokeWidth="2" rx="8" />
          <text x="195" y="140" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#323130">
            QueryAgent
          </text>
          <text x="195" y="160" textAnchor="middle" fontSize="10" fill="#666">
            Intent
          </text>
          <text x="195" y="175" textAnchor="middle" fontSize="10" fill="#666">
            Detection
          </text>

          {/* Arrow to RouterAgent */}
          <path d="M 260 150 L 305 150" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* RouterAgent */}
          <rect x="310" y="110" width="120" height="80" fill="#F3F2F1" stroke="#0078D4" strokeWidth="2" rx="8" />
          <text x="370" y="140" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#323130">
            RouterAgent
          </text>
          <text x="370" y="160" textAnchor="middle" fontSize="10" fill="#666">
            Route
          </text>
          <text x="370" y="175" textAnchor="middle" fontSize="10" fill="#666">
            Selection
          </text>

          {/* Arrow to ActionAgent */}
          <path d="M 435 150 L 480 150" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* ActionAgent */}
          <rect x="485" y="110" width="120" height="80" fill="#F3F2F1" stroke="#0078D4" strokeWidth="2" rx="8" />
          <text x="545" y="140" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#323130">
            ActionAgent
          </text>
          <text x="545" y="160" textAnchor="middle" fontSize="10" fill="#666">
            Execute
          </text>
          <text x="545" y="175" textAnchor="middle" fontSize="10" fill="#666">
            (Tools)
          </text>

          {/* Arrow to Response */}
          <path d="M 610 150 L 655 150" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Response */}
          <rect x="660" y="125" width="100" height="50" fill="#0078D4" rx="8" />
          <text x="710" y="155" textAnchor="middle" fontSize="12" fontWeight="bold" fill="white">
            Response
          </text>

          {/* Service layer labels */}
          <text x="450" y="250" textAnchor="middle" fontSize="12" fill="#666" fontWeight="bold">
            Service Layer
          </text>
          <text x="200" y="270" textAnchor="start" fontSize="10" fill="#666">
            Sessions • Audit Logs • Tickets • Knowledge Base
          </text>

          {/* Arrow marker definition */}
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
              <polygon points="0 0, 10 3, 0 6" fill="#323130" />
            </marker>
          </defs>
        </DiagramSVG>

        <div className="grid md:grid-cols-3 gap-6 my-12">
          {agents.map((agent, index) => (
            <div key={index} className="card">
              <div className="text-2xl font-bold text-microsoft-blue mb-2">{agent.name}</div>
              <p className="text-sm font-semibold text-dark-text mb-2">{agent.role}</p>
              <p className="text-sm text-gray-600 mb-3">{agent.responsibility}</p>
              <div className="border-t border-gray-200 pt-3 mt-3">
                <p className="text-xs font-medium text-gray-500 mb-1">OUTPUT:</p>
                <p className="text-xs text-gray-700">{agent.output}</p>
              </div>
            </div>
          ))}
        </div>

        <CalloutCard title="Why Three Agents, Not One?">
          <strong>Separation of concerns.</strong> Each agent has a focused job. This makes the system 
          testable, auditable, and safe. The router doesn't create tickets. The action agent doesn't 
          classify intent. This separation is what makes the system trustworthy.
        </CalloutCard>

        <div className="card mt-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">Tool Inventory (4 Tools Only)</h3>
          <div className="space-y-3">
            {tools.map((tool, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded">
                <span className="text-microsoft-blue font-mono text-sm flex-shrink-0">
                  {index + 1}.
                </span>
                <div>
                  <code className="text-sm font-semibold text-dark-text">{tool.name}</code>
                  <p className="text-sm text-gray-600 mt-1">{tool.purpose}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mt-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">Service Layer</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded">
              <div className="text-2xl mb-1">📝</div>
              <div className="text-xs font-medium">Sessions</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded">
              <div className="text-2xl mb-1">🔍</div>
              <div className="text-xs font-medium">Audit Logs</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded">
              <div className="text-2xl mb-1">🎫</div>
              <div className="text-xs font-medium">Tickets</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded">
              <div className="text-2xl mb-1">📚</div>
              <div className="text-xs font-medium">Knowledge Base</div>
            </div>
          </div>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>This is not a monolithic LLM prompt.</strong> It's a pipeline where each stage has 
            clear inputs, outputs, and boundaries.
          </p>
          <p className="mb-3">
            The <strong>QueryAgent</strong> doesn't route. The <strong>RouterAgent</strong> doesn't create 
            tickets. The <strong>ActionAgent</strong> doesn't classify intent. Each agent has exactly one job.
          </p>
          <p className="mb-3">
            This separation is what makes the system:
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li><strong>Testable</strong> — Each agent can be tested independently</li>
            <li><strong>Auditable</strong> — Every stage logs its decision and reasoning</li>
            <li><strong>Safe</strong> — The ActionAgent is the only one with tool access</li>
            <li><strong>Maintainable</strong> — Changes to routing logic don't affect intent detection</li>
          </ul>
          <p>
            The service layer (Sessions, Audit Logs, Tickets, Knowledge Base) provides shared state and 
            persistence. This is where the agent remembers context across turns and modalities.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
