import CollapsibleNotes from '../components/CollapsibleNotes'
import CalloutCard from '../components/CalloutCard'
import DiagramSVG from '../components/DiagramSVG'
import { DevicePhoneMobileIcon, SignalIcon, DocumentTextIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'

export default function Telephony() {
  return (
    <div role="tabpanel" id="telephony-panel" aria-labelledby="telephony-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-4">
          Phone Support — The Same Agent Answers the Phone
        </h2>
        <p className="text-xl text-gray-600 mb-12">
          Extend your multi-agent pipeline to PSTN callers via Azure Communication Services
        </p>

        <DiagramSVG
          title="Telephony Architecture"
          description="Caller dials a real phone number, ACS bridges audio through backend to Azure OpenAI Realtime API and 3-agent pipeline"
          viewBox="0 0 800 400"
        >
          {/* Caller */}
          <circle cx="60" cy="70" r="35" fill="#0078D4" />
          <text x="60" y="75" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">
            Caller
          </text>
          <text x="60" y="120" textAnchor="middle" fontSize="10" fill="#666">
            dials phone
          </text>

          {/* Arrow to PSTN */}
          <path d="M 100 70 L 155 70" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />
          <text x="128" y="62" textAnchor="middle" fontSize="9" fill="#666">PSTN</text>

          {/* ACS */}
          <rect x="160" y="45" width="110" height="50" fill="#0078D4" stroke="#323130" strokeWidth="2" rx="6" />
          <text x="215" y="67" textAnchor="middle" fontSize="11" fill="white" fontWeight="bold">
            ACS
          </text>
          <text x="215" y="82" textAnchor="middle" fontSize="9" fill="white">
            Call Automation
          </text>

          {/* Arrow to Event Grid */}
          <path d="M 275 70 L 325 70" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Event Grid */}
          <rect x="330" y="45" width="100" height="50" fill="#F3F2F1" stroke="#0078D4" strokeWidth="2" rx="6" />
          <text x="380" y="67" textAnchor="middle" fontSize="11" fill="#323130" fontWeight="bold">
            Event Grid
          </text>
          <text x="380" y="82" textAnchor="middle" fontSize="9" fill="#666">
            webhook
          </text>

          {/* Arrow down to Backend */}
          <path d="M 380 100 L 380 140" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* Backend */}
          <rect x="310" y="145" width="140" height="55" fill="#F3F2F1" stroke="#990000" strokeWidth="3" rx="8" />
          <text x="380" y="170" textAnchor="middle" fontSize="13" fill="#323130" fontWeight="bold">
            Backend
          </text>
          <text x="380" y="186" textAnchor="middle" fontSize="10" fill="#666">
            WebSocket Bridge
          </text>

          {/* Arrow from ACS audio down to Backend */}
          <path d="M 215 100 L 215 172 L 305 172" stroke="#0078D4" strokeWidth="2" strokeDasharray="5,3" markerEnd="url(#arrowhead)" />
          <text x="225" y="140" textAnchor="start" fontSize="9" fill="#0078D4">/ws/acs-media</text>

          {/* Arrow to Azure OpenAI */}
          <path d="M 455 172 L 530 172" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />
          <text x="492" y="165" textAnchor="middle" fontSize="9" fill="#666">audio</text>

          {/* Azure OpenAI Realtime API */}
          <rect x="535" y="145" width="160" height="55" fill="#0078D4" stroke="#323130" strokeWidth="2" rx="8" />
          <text x="615" y="170" textAnchor="middle" fontSize="13" fill="white" fontWeight="bold">
            Azure OpenAI
          </text>
          <text x="615" y="186" textAnchor="middle" fontSize="11" fill="white">
            Realtime API
          </text>

          {/* Arrow down to 3-Agent Pipeline */}
          <path d="M 615 205 L 615 250" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />
          <text x="630" y="230" textAnchor="start" fontSize="9" fill="#666">Tool calls</text>

          {/* 3-Agent Pipeline */}
          <rect x="525" y="255" width="180" height="55" fill="#F3F2F1" stroke="#990000" strokeWidth="3" rx="8" />
          <text x="615" y="280" textAnchor="middle" fontSize="13" fill="#323130" fontWeight="bold">
            3-Agent Pipeline
          </text>
          <text x="615" y="296" textAnchor="middle" fontSize="10" fill="#666">
            (same as text &amp; voice)
          </text>

          {/* Arrow from pipeline back to backend for response */}
          <path d="M 520 282 L 455 200" stroke="#323130" strokeWidth="2" markerEnd="url(#arrowhead)" />

          {/* SSE arrow down from Backend */}
          <path d="M 380 205 L 380 320" stroke="#0078D4" strokeWidth="2" strokeDasharray="5,3" markerEnd="url(#arrowhead)" />
          <text x="395" y="265" textAnchor="start" fontSize="9" fill="#0078D4">SSE</text>

          {/* LivePage */}
          <rect x="320" y="325" width="120" height="45" fill="#0078D4" stroke="#323130" strokeWidth="2" rx="6" />
          <text x="380" y="345" textAnchor="middle" fontSize="11" fill="white" fontWeight="bold">
            LivePage
          </text>
          <text x="380" y="360" textAnchor="middle" fontSize="9" fill="white">
            audience view
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
              <DevicePhoneMobileIcon className="w-6 h-6 text-microsoft-blue" />
              <h3 className="font-semibold text-lg text-dark-text">Real Phone Number</h3>
            </div>
            <p className="text-gray-700">
              PSTN callers dial a real number — no app install, no browser, no Wi-Fi required.
              Any phone works, from anywhere.
            </p>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <SignalIcon className="w-6 h-6 text-microsoft-blue" />
              <h3 className="font-semibold text-lg text-dark-text">Same Pipeline</h3>
            </div>
            <p className="text-gray-700">
              Identical 3-agent architecture as text and browser voice. Same tools, same boundaries,
              same constitutional principles. Only the transport changes.
            </p>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <DocumentTextIcon className="w-6 h-6 text-microsoft-blue" />
              <h3 className="font-semibold text-lg text-dark-text">Live Transcript</h3>
            </div>
            <p className="text-gray-700">
              The audience sees a real-time transcript on the LivePage as the phone call happens.
              Every word, every tool call, every routing decision — visible in real time.
            </p>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheckIcon className="w-6 h-6 text-microsoft-blue" />
              <h3 className="font-semibold text-lg text-dark-text">No Audio Storage</h3>
            </div>
            <p className="text-gray-700">
              PII-filtered transcripts only. Raw audio is never persisted to disk or storage.
              Audio streams through memory and is discarded after processing.
            </p>
          </div>
        </div>

        <CalloutCard variant="accent" title="Production Update — April 21, 2026">
          <strong>🎉 Phone bridge is production-verified.</strong> Caller transcripts render on <code>/live</code> during 
          active ACS phone calls. The full 3-agent pipeline works identically for PSTN callers as it does for browser 
          voice and text chat. Deployed as revision azd-1776792457.
        </CalloutCard>

        <CalloutCard variant="accent" title="Protocol Bridging">
          ACS can&apos;t authenticate to Azure OpenAI directly — they speak different WebSocket protocols.
          The backend&apos;s <strong>managed identity</strong> bridges the gap, maintaining two concurrent WebSocket
          connections: one to ACS for telephony audio, one to Azure OpenAI Realtime for AI processing.
          Audio frames are relayed between them in real time.
        </CalloutCard>

        <div className="card mt-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">📞 How It Works</h3>
          <ol className="space-y-4">
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-sm">1</span>
              <div>
                <p className="text-gray-700">Caller dials <strong>+1-913-217-1946</strong></p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-sm">2</span>
              <div>
                <p className="text-gray-700">Event Grid fires webhook to <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">POST /api/phone/incoming</code></p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-sm">3</span>
              <div>
                <p className="text-gray-700">Backend answers via <strong>ACS Call Automation</strong></p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-sm">4</span>
              <div>
                <p className="text-gray-700">ACS streams audio to backend WebSocket <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">/ws/acs-media</code></p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-sm">5</span>
              <div>
                <p className="text-gray-700">Backend bridges audio to <strong>Azure OpenAI Realtime API</strong></p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-sm">6</span>
              <div>
                <p className="text-gray-700">AI responds; tools execute through the same 3-agent pipeline</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-sm">7</span>
              <div>
                <p className="text-gray-700">Live transcript published via <strong>SSE</strong> (Server-Sent Events)</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-microsoft-blue text-white flex items-center justify-center font-bold text-sm">8</span>
              <div>
                <p className="text-gray-700">Audience watches on <strong>LivePage</strong> in real time</p>
              </div>
            </li>
          </ol>
        </div>

        <CalloutCard variant="accent" title="Production Requirements">
          Deploying phone support requires: an <strong>Azure Communication Services</strong> resource,
          a purchased <strong>phone number</strong>, an <strong>Event Grid</strong> subscription,
          a <strong>public HTTPS endpoint</strong> for webhooks, and a <strong>managed identity</strong> with
          appropriate RBAC roles for both ACS and Azure OpenAI.
        </CalloutCard>

        <div className="card mt-8 border-l-4 border-microsoft-blue">
          <h3 className="font-semibold text-lg mb-4 text-dark-text flex items-center gap-2">
            <span>🎯</span> Demo Quick Reference
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm font-semibold text-dark-text">📞 Phone Number</p>
              <p className="font-mono text-sm text-microsoft-blue">+1-913-217-1946</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm font-semibold text-dark-text">📺 LivePage</p>
              <p className="font-mono text-sm text-microsoft-blue">/live</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm font-semibold text-dark-text">📋 Runbook</p>
              <p className="font-mono text-sm text-microsoft-blue">/runbook</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm font-semibold text-dark-text">💚 Health Check</p>
              <p className="font-mono text-sm text-microsoft-blue">/api/phone/health</p>
            </div>
          </div>
        </div>

        <div className="card mt-8">
          <h3 className="font-semibold text-lg mb-4 text-dark-text">Browser Voice vs Phone — Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="text-left p-3 font-semibold text-dark-text border-b">Aspect</th>
                  <th className="text-left p-3 font-semibold text-dark-text border-b">🌐 Browser Voice</th>
                  <th className="text-left p-3 font-semibold text-dark-text border-b">📞 Phone</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-semibold text-dark-text">Transport</td>
                  <td className="p-3 text-gray-700">WebRTC (peer-to-peer)</td>
                  <td className="p-3 text-gray-700">PSTN → ACS → WebSocket bridge</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-semibold text-dark-text">Authentication</td>
                  <td className="p-3 text-gray-700">Ephemeral token (60s TTL)</td>
                  <td className="p-3 text-gray-700">Managed identity (backend-to-backend)</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-semibold text-dark-text">Latency</td>
                  <td className="p-3 text-gray-700">~200ms (direct to Azure)</td>
                  <td className="p-3 text-gray-700">~400ms (extra hop through backend)</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-semibold text-dark-text">Audience View</td>
                  <td className="p-3 text-gray-700">User sees own chat transcript</td>
                  <td className="p-3 text-gray-700">Audience sees LivePage real-time transcript</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-semibold text-dark-text">Requirements</td>
                  <td className="p-3 text-gray-700">Browser + microphone</td>
                  <td className="p-3 text-gray-700">Any phone</td>
                </tr>
                <tr className="border-b hover:bg-blue-50">
                  <td className="p-3 font-semibold text-dark-text">AI Backend</td>
                  <td className="p-3 text-gray-700">Azure OpenAI Realtime API</td>
                  <td className="p-3 text-gray-700">Azure OpenAI Realtime API (same)</td>
                </tr>
                <tr className="hover:bg-blue-50">
                  <td className="p-3 font-semibold text-dark-text">Pipeline</td>
                  <td className="p-3 text-gray-700">3-agent, 4 tools</td>
                  <td className="p-3 text-gray-700">3-agent, 4 tools (identical)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-microsoft-blue/5 border-l-4 border-microsoft-blue p-6 rounded-r-lg mt-8">
          <h3 className="font-semibold text-lg mb-3 text-dark-text">What to Notice</h3>
          <p className="text-gray-700 leading-relaxed">
            The phone doesn&apos;t create a new agent or a new pipeline. It&apos;s a new <strong>transport</strong> to
            the same trusted system. Text, browser voice, and phone all converge on the identical 3-agent
            pipeline with the same 4 tools. The trust model is transport-independent.
          </p>
        </div>

        <div className="card mt-8 border-l-4 border-amber-500 bg-amber-50">
          <h3 className="font-semibold text-lg mb-3 text-dark-text flex items-center gap-2">
            <span>⚙️</span> Technical Note: Realtime API Schema
          </h3>
          <p className="text-gray-700 mb-3 text-sm">
            Azure OpenAI&apos;s Realtime API has <strong>two endpoints with different <code>session.update</code> schemas</strong>:
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1 text-sm text-gray-700">
            <li>
              <strong>WebRTC calls</strong> (browser voice): uses nested <code>audio: &#123; input: &#123;...&#125;, output: &#123;...&#125; &#125;</code> shape
            </li>
            <li>
              <strong>Direct WebSocket</strong> (phone bridge): uses flat top-level fields like <code>input_audio_format</code>, <code>output_audio_format</code>
            </li>
          </ul>
          <p className="text-gray-700 text-sm">
            The two schemas are <strong>not interchangeable</strong>. Using the wrong shape for an endpoint causes silent 
            <code>unknown_parameter</code> errors. The phone bridge regression (empty caller transcripts) was caused by 
            sending the nested schema to the direct-WS endpoint. See <code>.squad/skills/azure-realtime-api-schema/SKILL.md</code> for details.
          </p>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            <strong>Azure resources needed for phone support:</strong>
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li><strong>Azure Communication Services (ACS)</strong> — telephony resource with a purchased phone number</li>
            <li><strong>Event Grid</strong> — routes incoming call events to backend webhook</li>
            <li><strong>Azure OpenAI</strong> — Realtime API deployment (same as browser voice)</li>
            <li><strong>Public HTTPS endpoint</strong> — for Event Grid webhook delivery</li>
            <li><strong>Managed Identity</strong> — RBAC for ACS and Azure OpenAI access</li>
          </ul>
          <p className="mb-3">
            <strong>Mock mode:</strong> In development, the phone subsystem can run in mock mode without
            real ACS credentials. Mock mode simulates incoming calls and audio streams, allowing you to
            test the WebSocket bridge and LivePage transcript without a real phone number.
          </p>
          <p className="mb-3">
            <strong>Security model:</strong>
          </p>
          <ul className="list-disc pl-6 mb-3 space-y-1">
            <li>Ephemeral tokens for ACS WebSocket authentication</li>
            <li>Managed identity for backend-to-Azure OpenAI authentication</li>
            <li>No PII stored — audio is ephemeral, only filtered transcripts are persisted</li>
            <li>Event Grid webhook validation prevents spoofed incoming call events</li>
          </ul>
          <p>
            Browser Voice uses WebRTC for direct peer-to-peer audio with Azure OpenAI.
            Phone calls use a WebSocket bridge because ACS can&apos;t authenticate directly to Azure OpenAI.
            Both use the same Realtime API and the same 4 tools.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
