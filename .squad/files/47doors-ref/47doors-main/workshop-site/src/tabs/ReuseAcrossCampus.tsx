import CollapsibleNotes from '../components/CollapsibleNotes'
import CalloutCard from '../components/CalloutCard'
import DiagramSVG from '../components/DiagramSVG'

export default function ReuseAcrossCampus() {
  const departments = [
    'IT Support', 'Financial Aid', 'Housing', 'Registration',
    'Library', 'Health Services', 'Career Services', 'Advising'
  ]

  return (
    <div role="tabpanel" id="reuse-panel" aria-labelledby="reuse-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-4">
          One Architecture, Every Department
        </h2>
        <p className="text-xl text-gray-600 mb-12">
          How this architecture maps to any university
        </p>

        <DiagramSVG 
          title="Reuse Across Departments"
          description="Central agent pipeline with spokes to all university departments"
          viewBox="0 0 600 500"
        >
          {/* Central hub */}
          <circle cx="300" cy="250" r="70" fill="#0078D4" stroke="#323130" strokeWidth="3" />
          <text x="300" y="245" textAnchor="middle" fontSize="14" fill="white" fontWeight="bold">
            Agent
          </text>
          <text x="300" y="262" textAnchor="middle" fontSize="12" fill="white">
            Pipeline
          </text>

          {/* Department spokes */}
          {departments.map((dept, i) => {
            const angle = (i / departments.length) * 2 * Math.PI - Math.PI / 2
            const x = 300 + Math.cos(angle) * 180
            const y = 250 + Math.sin(angle) * 180
            
            return (
              <g key={i}>
                <line 
                  x1="300" 
                  y1="250" 
                  x2={x} 
                  y2={y} 
                  stroke="#0078D4" 
                  strokeWidth="2"
                  strokeDasharray="5,5"
                />
                <circle cx={x} cy={y} r="45" fill="#F3F2F1" stroke="#323130" strokeWidth="2" />
                <text 
                  x={x} 
                  y={y + 4} 
                  textAnchor="middle" 
                  fontSize="10" 
                  fill="#323130"
                  fontWeight="600"
                >
                  {dept}
                </text>
              </g>
            )
          })}
        </DiagramSVG>

        <div className="grid md:grid-cols-2 gap-8 my-12">
          <div className="card border-l-4 border-microsoft-blue">
            <h3 className="font-semibold text-lg mb-4 text-dark-text">
              What Changes Per Institution
            </h3>
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-microsoft-blue font-bold">📋</span>
                <div>
                  <strong>Department routing table</strong> — JSON config mapping intents to departments
                </div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-microsoft-blue font-bold">📚</span>
                <div>
                  <strong>Knowledge base articles</strong> — Institution-specific FAQs and help content
                </div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-microsoft-blue font-bold">⚠️</span>
                <div>
                  <strong>Escalation triggers</strong> — Customizable keywords and urgency thresholds
                </div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-microsoft-blue font-bold">🎨</span>
                <div>
                  <strong>Branding</strong> — Colors, logo, voice persona (friendly vs. formal)
                </div>
              </li>
            </ul>
          </div>

          <div className="card border-l-4 border-iu-crimson bg-microsoft-blue/5">
            <h3 className="font-semibold text-lg mb-4 text-dark-text">
              What Stays the Same
            </h3>
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✅</span>
                <div>The 3-agent pipeline architecture</div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✅</span>
                <div>The seven constitutional boundaries</div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✅</span>
                <div>The trust model and governance</div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✅</span>
                <div>The audit trail and logging</div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✅</span>
                <div>The voice/text modality flexibility</div>
              </li>
            </ul>
          </div>
        </div>

        <div className="card mb-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">Deployment: One Command</h3>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm mb-4">
            $ azd up
          </div>
          <p className="text-gray-700 mb-3">
            Deploy to Azure Container Apps with infrastructure as code (Bicep). Provisions:
          </p>
          <ul className="text-sm text-gray-600 space-y-1 ml-4">
            <li>• Azure OpenAI resource with GPT-4o + GPT-4o Realtime deployments</li>
            <li>• Backend container app (FastAPI) with managed identity auth</li>
            <li>• Frontend container app (React) served via Azure CDN</li>
            <li>• Azure AI Search for knowledge base indexing</li>
            <li>• Cosmos DB for session persistence (optional)</li>
            <li>• Application Insights for monitoring and logging</li>
          </ul>
        </div>

        <CalloutCard variant="accent" title="The Pitch">
          You're not buying a chatbot. You're giving every student a <strong>trusted digital colleague</strong> who 
          is always available, always accurate, and always gets them to the right place — whether they type or talk.
        </CalloutCard>

        <div className="bg-white rounded-lg shadow-sm p-8 mt-8 border-2 border-microsoft-blue">
          <h3 className="font-semibold text-xl mb-4 text-dark-text text-center">
            From Demo to Production
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-3">🧪</div>
              <h4 className="font-semibold text-sm mb-2">Try It Now</h4>
              <p className="text-xs text-gray-600">
                Clone the repo, run in mock mode (no Azure credentials needed)
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">☁️</div>
              <h4 className="font-semibold text-sm mb-2">Deploy to Azure</h4>
              <p className="text-xs text-gray-600">
                azd up — live deployment in 5 minutes with your Azure subscription
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">🎓</div>
              <h4 className="font-semibold text-sm mb-2">Customize & Scale</h4>
              <p className="text-xs text-gray-600">
                Add your departments, knowledge base, branding — ready for production
              </p>
            </div>
          </div>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>The architecture is institution-agnostic.</strong> The 3-agent pipeline doesn't know 
            or care whether you're a small liberal arts college or a large research university.
          </p>
          <p className="mb-3">
            It maps to <strong>any university's department taxonomy</strong>. The routing table is a simple 
            JSON config file:
          </p>
          <pre className="bg-gray-900 text-green-400 p-3 rounded text-xs font-mono mb-3 overflow-x-auto">
{`{
  "it_support": {
    "department": "IT Support",
    "ticket_system": "ServiceNow",
    "sla_hours": 24
  },
  "financial_aid": {
    "department": "Financial Aid Office",
    "ticket_system": "BannerSIS",
    "sla_hours": 48
  },
  ...
}`}
          </pre>
          <p className="mb-3">
            <strong>Knowledge base integration</strong> uses Azure AI Search with your institution's FAQs, 
            help articles, and policy documents. Index once, search instantly.
          </p>
          <p className="mb-3">
            <strong>With live Azure deployment via <code>azd up</code></strong>, any institution can:
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li>Demo it today with their own branding</li>
            <li>Test with their own knowledge base</li>
            <li>Pilot with a single department (e.g., IT Support)</li>
            <li>Scale to all departments once validated</li>
          </ul>
          <p>
            This isn't a proof-of-concept. This is production-ready architecture designed for institutional deployment.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
