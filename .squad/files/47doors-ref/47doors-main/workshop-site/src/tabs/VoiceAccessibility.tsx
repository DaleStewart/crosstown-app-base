import CollapsibleNotes from '../components/CollapsibleNotes'
import CalloutCard from '../components/CalloutCard'
import DiagramSVG from '../components/DiagramSVG'
import { MicrophoneIcon, SpeakerWaveIcon, CircleStackIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'

export default function VoiceAccessibility() {
  return (
    <div role="tabpanel" id="voice-panel" aria-labelledby="voice-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-4">
          The Same Agent, Now It Speaks
        </h2>
        <p className="text-xl text-gray-600 mb-12">
          Voice interaction via Azure OpenAI Realtime API — same pipeline, new interface
        </p>

        <DiagramSVG 
          title="Voice Architecture"
          description="Student voice flows through browser to Azure OpenAI, tool calls route to 3-agent pipeline"
          viewBox="0 0 800 350"
        >
          {/* Student speaks */}
          <circle cx="80" cy="80" r="35" fill="#0078D4" />
          <text x="80" y="85" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">
            Student
          </text>
          <text x="80" y="135" textAnchor="middle" fontSize="10" fill="#666">
            speaks
          </text>

          {/* Arrow down */}
          <path d="M 80 120 L 80 155" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Browser mic */}
          <rect x="40" y="160" width="80" height="50" fill="#F3F2F1" stroke="#0078D4" strokeWidth="2" rx="6" />
          <text x="80" y="190" textAnchor="middle" fontSize="11" fill="#323130" fontWeight="bold">
            Browser mic
          </text>

          {/* Arrow to WebRTC */}
          <path d="M 125 185 L 185 185" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />
          <text x="155" y="178" textAnchor="middle" fontSize="9" fill="#666">WebRTC</text>

          {/* Azure OpenAI Realtime API */}
          <rect x="190" y="150" width="160" height="70" fill="#0078D4" stroke="#323130" strokeWidth="2" rx="8" />
          <text x="270" y="180" textAnchor="middle" fontSize="13" fill="white" fontWeight="bold">
            Azure OpenAI
          </text>
          <text x="270" y="198" textAnchor="middle" fontSize="11" fill="white">
            Realtime API
          </text>

          {/* Arrow down from Azure to Tool calls */}
          <path d="M 270 225 L 270 260" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />
          <text x="300" y="245" textAnchor="start" fontSize="9" fill="#666">Tool calls via</text>
          <text x="300" y="255" textAnchor="start" fontSize="9" fill="#666">WebSocket</text>

          {/* 3-Agent Pipeline */}
          <rect x="180" y="265" width="180" height="60" fill="#F3F2F1" stroke="#990000" strokeWidth="3" rx="8" />
          <text x="270" y="290" textAnchor="middle" fontSize="13" fill="#323130" fontWeight="bold">
            3-Agent Pipeline
          </text>
          <text x="270" y="308" textAnchor="middle" fontSize="10" fill="#666">
            (same as text)
          </text>

          {/* Arrow back up */}
          <path d="M 365 295 L 430 240" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* AI speaks response */}
          <rect x="380" y="150" width="150" height="70" fill="#0078D4" stroke="#323130" strokeWidth="2" rx="8" />
          <text x="455" y="180" textAnchor="middle" fontSize="13" fill="white" fontWeight="bold">
            AI speaks
          </text>
          <text x="455" y="198" textAnchor="middle" fontSize="11" fill="white">
            response back
          </text>

          {/* Arrow marker */}
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
              <polygon points="0 0, 10 3, 0 6" fill="#323130" />
            </marker>
          </defs>
        </DiagramSVG>

        <div className="grid md:grid-cols-2 gap-6 my-12">
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <MicrophoneIcon className="w-6 h-6 text-microsoft-blue" />
              <h3 className="font-semibold text-lg text-dark-text">One Button</h3>
            </div>
            <p className="text-gray-700">
              No commands, no keywords. Press the mic button and speak naturally. The agent understands 
              conversational language just like it does with text.
            </p>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <SpeakerWaveIcon className="w-6 h-6 text-microsoft-blue" />
              <h3 className="font-semibold text-lg text-dark-text">Spoken AND Shown</h3>
            </div>
            <p className="text-gray-700">
              Responses are both spoken aloud and displayed as text transcript. Students can listen, read, 
              or both — whatever works best for them.
            </p>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <CircleStackIcon className="w-6 h-6 text-microsoft-blue" />
              <h3 className="font-semibold text-lg text-dark-text">Same Session</h3>
            </div>
            <p className="text-gray-700">
              Voice and text share the same session context. Switch between typing and talking — the agent 
              remembers everything across both modalities.
            </p>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheckIcon className="w-6 h-6 text-microsoft-blue" />
              <h3 className="font-semibold text-lg text-dark-text">No Audio Stored</h3>
            </div>
            <p className="text-gray-700">
              Only PII-filtered transcripts are saved. Raw audio never touches the backend or storage. 
              This meets institutional privacy requirements by design.
            </p>
          </div>
        </div>

        <CalloutCard variant="accent" title="Ephemeral Token Security">
          <strong>API Key → Backend → Ephemeral Token (60s TTL) → Client.</strong> The Azure OpenAI API key 
          never touches the browser. The backend generates a short-lived token with WebRTC credentials that 
          expires in 60 seconds. Even if intercepted, it's useless after one minute.
        </CalloutCard>

        <div className="card mt-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">♿ Accessibility Features</h3>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start gap-3">
              <span className="text-microsoft-blue font-bold">⌨️</span>
              <div>
                <strong>Keyboard accessible:</strong> Press Enter to start/stop recording, Escape to cancel. 
                No mouse required.
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-microsoft-blue font-bold">🔊</span>
              <div>
                <strong>ARIA labels:</strong> Screen readers announce voice status (listening, processing, 
                speaking) and provide full context.
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-microsoft-blue font-bold">📝</span>
              <div>
                <strong>Transcript always visible:</strong> Every spoken word appears as text. Students 
                with hearing impairments get full access.
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-microsoft-blue font-bold">✅</span>
              <div>
                <strong>Additive, not replacement:</strong> Voice is optional. When unavailable or disabled, 
                text chat works perfectly. No feature loss.
              </div>
            </li>
          </ul>
        </div>

        <div className="bg-microsoft-blue/5 border-l-4 border-microsoft-blue p-6 rounded-r-lg mt-8">
          <h3 className="font-semibold text-lg mb-3 text-dark-text">What to Notice</h3>
          <p className="text-gray-700 leading-relaxed">
            Voice doesn't create a new agent. It's a new <strong>interface</strong> to the same trusted pipeline. 
            That's the point — trust doesn't change when the modality changes. Same boundaries, same tools, 
            same constitutional principles. Just a different way to interact.
          </p>
        </div>

        <div className="card mt-8 bg-green-50 border-l-4 border-green-500">
          <h3 className="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span>📞</span> Phone Integration Is Live
          </h3>
          <p className="text-gray-700 mb-3">
            <strong>Production-verified as of April 21, 2026.</strong> The same architecture now extends to phone calls—real
            PSTN numbers that anyone can dial (+1-913-217-1946). Caller transcripts render on <code>/live</code> during active calls.
          </p>
          <p className="text-gray-700">
            See the <strong>Phone Integration</strong> tab for the full telephony architecture. Same 3-agent pipeline, same 4 tools, 
            same constitutional principles—just a different transport.
          </p>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>The most important design decision:</strong> Voice is additive, not replacement.
          </p>
          <p className="mb-3">
            When voice is unavailable (no mic, browser doesn't support WebRTC, Azure service down), text 
            works perfectly. When voice is available, it uses the <strong>same 3-agent pipeline</strong> as text.
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li>No new authority</li>
            <li>No new data access</li>
            <li>No new risk surface</li>
          </ul>
          <p className="mb-3">
            The agent has exactly the same four tools whether you type or talk:
          </p>
          <ol className="list-decimal pl-6 mb-3 space-y-1">
            <li><code>analyze_and_route_query</code></li>
            <li><code>search_knowledge_base</code></li>
            <li><code>create_ticket</code></li>
            <li><code>escalate_to_human</code></li>
          </ol>
          <p className="mb-3">
            This is constitutional consistency. The modality changes. The trust model does not.
          </p>
          <p className="mb-3">
            <strong>Browser Voice vs Phone:</strong>
          </p>
          <p className="mb-3">
            Browser Voice uses WebRTC for direct peer-to-peer audio with Azure OpenAI.
            Phone calls use a WebSocket bridge because ACS can't authenticate directly to Azure OpenAI.
            Both use the same Realtime API and the same 4 tools.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
