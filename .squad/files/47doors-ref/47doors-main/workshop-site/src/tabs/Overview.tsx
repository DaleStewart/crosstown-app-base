import CollapsibleNotes from '../components/CollapsibleNotes'

export default function Overview() {
  return (
    <div role="tabpanel" id="overview-panel" aria-labelledby="overview-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-2">
          Trustworthy Agentic AI in Higher Education
        </h2>
        <p className="text-xl text-gray-600 mb-8">
          A 45-minute executive briefing on building AI agents that earn institutional trust
        </p>

        <div className="bg-microsoft-blue/5 border-l-4 border-microsoft-blue p-6 rounded-r-lg mb-8">
          <p className="text-lg font-medium text-dark-text">
            This is not a chatbot demo. This is an architecture lesson.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="card">
            <div className="text-4xl mb-3">🚪</div>
            <h3 className="font-semibold text-lg mb-2 text-dark-text">The Problem</h3>
            <p className="text-gray-700">
              Students don't know which of 47+ university portals to use for help. The routing problem is institutional, not individual.
            </p>
          </div>

          <div className="card">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="font-semibold text-lg mb-2 text-dark-text">The Architecture</h3>
            <p className="text-gray-700">
              A three-agent pipeline (Query → Router → Action) that routes students to the right department with ticket creation and knowledge base search.
            </p>
          </div>

          <div className="card">
            <div className="text-4xl mb-3">🔒</div>
            <h3 className="font-semibold text-lg mb-2 text-dark-text">The Trust Model</h3>
            <p className="text-gray-700">
              Trust built architecturally through constitutional boundaries, not policy documents. Seven principles enforced in code.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h3 className="font-semibold text-xl mb-6 text-dark-text text-center">The Journey</h3>
          <div className="flex items-center justify-center gap-4 text-5xl">
            <span role="img" aria-label="Many doors">🚪</span>
            <span className="text-2xl text-gray-400">→</span>
            <span role="img" aria-label="Agent">🤖</span>
            <span className="text-2xl text-gray-400">→</span>
            <span role="img" aria-label="Trust">🔒</span>
            <span className="text-2xl text-gray-400">→</span>
            <span role="img" aria-label="Voice">🎤</span>
            <span className="text-2xl text-gray-400">→</span>
            <span role="img" aria-label="University">🏫</span>
          </div>
          <p className="text-center text-gray-600 mt-6">
            From chaos to clarity: One front door for every student need
          </p>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>Workshop Context:</strong> This workshop is designed for university IT leadership, CIOs, 
            and technical decision-makers who need to understand how agentic AI differs from traditional 
            chatbots and how trust can be architected into AI systems.
          </p>
          <p className="mb-3">
            <strong>Goal:</strong> Demystify agentic AI and demonstrate that trust is not achieved through 
            policy documents alone — it must be built into the system architecture through bounded authority, 
            human escalation, privacy-first design, and graceful degradation.
          </p>
          <p>
            <strong>Key Takeaway:</strong> By the end of this workshop, attendees will understand the 
            three-agent pattern, the seven constitutional principles, and how voice interaction extends 
            the same trust model to a new modality.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
