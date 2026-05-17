import { useState } from 'react'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'

type SectionCategory = 'narrative' | 'demo' | 'exercise'

interface ActionCue {
  icon: string
  text: string
}

interface ScriptSection {
  id: string
  timeStart: string
  timeEnd: string
  durationMin: number
  elapsedEnd: number
  title: string
  category: SectionCategory
  talkTrack: string[]
  actions: ActionCue[]
  showTarget: string
}

const categoryStyles: Record<SectionCategory, { border: string; badge: string; badgeText: string; label: string }> = {
  narrative: {
    border: 'border-microsoft-blue',
    badge: 'bg-blue-100 text-blue-800',
    badgeText: '🔵 Narrative',
    label: 'Narrative section',
  },
  demo: {
    border: 'border-green-500',
    badge: 'bg-green-100 text-green-800',
    badgeText: '🟢 Live Demo',
    label: 'Live demo section',
  },
  exercise: {
    border: 'border-amber-500',
    badge: 'bg-amber-100 text-amber-800',
    badgeText: '🟡 Exercise',
    label: 'Exercise section',
  },
}

const sections: ScriptSection[] = [
  {
    id: 'opening',
    timeStart: '0:00',
    timeEnd: '5:00',
    durationMin: 5,
    elapsedEnd: 5,
    title: 'Opening & Context',
    category: 'narrative',
    talkTrack: [
      '"Welcome to 47 Doors. Today we\'re going to rethink how universities deliver student support — not with another chatbot, but with a trusted digital colleague."',
      '"Imagine being a first-year student. You have a password problem — but is that IT? Your course portal? Your library login? At most universities, there are literally 47 different front doors for support. Students don\'t know which door to knock on, so they knock on all of them — and wait."',
      '"47 Doors is the answer: one front door. One place where any student question — regardless of department — is heard, understood, and routed correctly."',
    ],
    actions: [
      { icon: '👀', text: 'Show the workshop site Overview tab on the projector' },
      { icon: '🗣️', text: 'Introduce yourself and the workshop format (45 min, interactive)' },
      { icon: '🗣️', text: 'Set the hook: "By the end, you\'ll design your own agent"' },
    ],
    showTarget: 'Workshop site → Overview tab',
  },
  {
    id: 'chatbots-to-agents',
    timeStart: '5:00',
    timeEnd: '10:00',
    durationMin: 5,
    elapsedEnd: 10,
    title: 'From Chatbots to Agents',
    category: 'narrative',
    talkTrack: [
      '"Let\'s talk about the evolution. First there were FAQ bots — keyword matching, decision trees. Then came chatbots — LLMs that could hold a conversation. Then copilots — AI that helps you do your work."',
      '"Agents are the next step. An agent doesn\'t just answer questions — it takes actions. It creates tickets, searches knowledge bases, routes requests. But here\'s the key distinction: agents take actions with boundaries. They have a defined set of tools and they cannot invent new capabilities."',
      '"This is the difference between \'we told the AI not to do this\' and \'the AI physically cannot do this — the tool doesn\'t exist.\'"',
    ],
    actions: [
      { icon: '👀', text: 'Navigate to the "Chatbots to Agents" tab' },
      { icon: '🗣️', text: 'Walk through the evolution diagram on screen' },
      { icon: '🗣️', text: 'Emphasize: "Agents take actions with boundaries"' },
    ],
    showTarget: 'Workshop site → Chatbots to Agents tab',
  },
  {
    id: 'trust-constitutional',
    timeStart: '10:00',
    timeEnd: '15:00',
    durationMin: 5,
    elapsedEnd: 15,
    title: 'Trust & Constitutional AI',
    category: 'narrative',
    talkTrack: [
      '"If agents can take actions, how do we trust them? This is the central question. And the answer is: trust is architecture, not policy."',
      '"We built 47 Doors on 7 constitutional principles — things like bounded authority, graceful degradation, audit transparency. These aren\'t suggestions in a system prompt. They\'re enforced by the architecture itself."',
      '"The agent has exactly 4 tools. It cannot invent a 5th. When a student asks to change their grade, the agent doesn\'t refuse because it was told not to — it refuses because the tool to do that does not exist in its inventory."',
    ],
    actions: [
      { icon: '👀', text: 'Navigate to the "Trust & Boundaries" tab' },
      { icon: '🗣️', text: 'Walk through the 7 constitutional principles' },
      { icon: '🗣️', text: 'Repeat the key phrase: "Trust is architecture, not policy"' },
    ],
    showTarget: 'Workshop site → Trust & Boundaries tab',
  },
  {
    id: 'architecture',
    timeStart: '15:00',
    timeEnd: '20:00',
    durationMin: 5,
    elapsedEnd: 20,
    title: 'Architecture Deep Dive',
    category: 'narrative',
    talkTrack: [
      '"Let me show you how this works under the hood. The system uses a 3-agent pipeline: QueryAgent detects intent, RouterAgent selects the right department, and ActionAgent executes — creating tickets, searching the knowledge base, checking SLAs."',
      '"The entire system has exactly 4 tools: create_ticket, search_knowledge_base, check_sla, and escalate_to_human. That\'s it. Bounded authority means bounded risk."',
      '"This architecture is the same whether a student types or speaks. Voice and text share the same pipeline, the same session, the same audit trail."',
    ],
    actions: [
      { icon: '👀', text: 'Navigate to the "Architecture" tab' },
      { icon: '🗣️', text: 'Walk through the 3-agent pipeline diagram' },
      { icon: '🗣️', text: 'Count the 4 tools on screen — "That\'s it. Four tools."' },
    ],
    showTarget: 'Workshop site → Architecture tab',
  },
  {
    id: 'demo-text',
    timeStart: '20:00',
    timeEnd: '23:00',
    durationMin: 3,
    elapsedEnd: 23,
    title: 'Live Demo — Text Chat',
    category: 'demo',
    talkTrack: [
      '"Let me show you what this looks like in action. I\'m going to type a real student request."',
      '"Notice what happened: one input — intent detected, ticket created, knowledge base article surfaced, SLA communicated. The student doesn\'t need to know which department handles this."',
      '"This is what we built for text. Now I\'m going to show you the same experience — but spoken out loud."',
    ],
    actions: [
      { icon: '👀', text: 'Switch to the live app (text chat interface)' },
      { icon: '⌨️', text: 'Type: "I forgot my password and can\'t log into Canvas"' },
      { icon: '👀', text: 'Point out: ticket ID, KB articles, SLA estimate' },
      { icon: '🗣️', text: 'Explain: "One input → intent → ticket → KB → SLA"' },
    ],
    showTarget: 'Live app → Text chat',
  },
  {
    id: 'demo-voice',
    timeStart: '23:00',
    timeEnd: '30:00',
    durationMin: 7,
    elapsedEnd: 30,
    title: 'Live Demo — Voice',
    category: 'demo',
    talkTrack: [
      '"One button. That\'s the entire voice interface."',
      '"The browser asks for mic permission — we request it, the student grants it, and we\'re live. Notice the status: it says Listening…"',
      '"Speak naturally. No commands, no keywords — just say what you need."',
      '"The agent heard me finish speaking. Now it\'s running the same 3-agent pipeline — intent detection, routing, action. Same pipeline, voice input."',
      '"The agent speaks the answer back AND adds it to the chat thread with a speaker icon. No audio is stored — only the PII-filtered transcript."',
    ],
    actions: [
      { icon: '🖱️', text: 'Click the 🎤 microphone button — it pulses green' },
      { icon: '🗣️', text: 'Speak: "I forgot my password and can\'t log into Canvas"' },
      { icon: '👀', text: 'Point to: spinner state, then transcript appearing with 🔊 icon' },
      { icon: '🗣️', text: 'Ask follow-up verbally: "Can you check the status of that ticket?"' },
      { icon: '🖱️', text: 'Click mic button again to stop — show seamless return to text' },
      { icon: '👀', text: 'Open new tab → /api/realtime/health to show health endpoint' },
      { icon: '👀', text: 'Show: voice and text share the same session ID' },
    ],
    showTarget: 'Live app → Voice demo + Health endpoints',
  },
  {
    id: 'demo-degradation',
    timeStart: '30:00',
    timeEnd: '33:00',
    durationMin: 3,
    elapsedEnd: 33,
    title: 'Live Demo — Graceful Degradation',
    category: 'demo',
    talkTrack: [
      '"The most important thing about a feature like this is what happens when it doesn\'t work."',
      '"When voice isn\'t available, we don\'t show a broken button — we remove it. The student sees a normal, fully functional text chat."',
      '"Text chat is completely unaffected. Voice uses separate WebRTC and WebSocket connections — zero coupling to the text pipeline."',
      '"Graceful degradation isn\'t just a buzzword here. It\'s a constitutional requirement baked into the architecture from day one."',
    ],
    actions: [
      { icon: '🖱️', text: 'In Azure portal: set VOICE_ENABLED=false on the Container App' },
      { icon: '🖱️', text: 'Refresh the frontend — mic button disappears entirely' },
      { icon: '⌨️', text: 'Type a message — show text chat works perfectly' },
      { icon: '🖱️', text: 'Re-enable: set VOICE_ENABLED=true — mic button reappears' },
    ],
    showTarget: 'Live app + Azure portal',
  },
  {
    id: 'responsible-ai',
    timeStart: '33:00',
    timeEnd: '38:00',
    durationMin: 5,
    elapsedEnd: 38,
    title: 'Responsible AI & Reuse',
    category: 'narrative',
    talkTrack: [
      '"Everything we just saw maps to Microsoft\'s Responsible AI principles. Fairness — the agent treats every query the same. Transparency — every action is logged. Accountability — there\'s always a human escalation path."',
      '"And this architecture isn\'t locked to one university. The 3-agent pipeline maps to any institution\'s department taxonomy. Replace the routing table and knowledge base, and you have your own front door."',
      '"The deployment is one command: azd up. Live on Azure in 5 minutes."',
    ],
    actions: [
      { icon: '👀', text: 'Navigate to "Responsible AI" tab in the workshop site' },
      { icon: '🗣️', text: 'Walk through the RAI principles mapping' },
      { icon: '👀', text: 'Navigate to "Reuse Across Campus" tab' },
      { icon: '🗣️', text: 'Emphasize: "Replace the routing table → your own front door"' },
    ],
    showTarget: 'Workshop site → Responsible AI & Reuse tabs',
  },
  {
    id: 'exercise',
    timeStart: '38:00',
    timeEnd: '43:00',
    durationMin: 5,
    elapsedEnd: 43,
    title: 'Workshop Exercise',
    category: 'exercise',
    talkTrack: [
      '"Now it\'s your turn. In the next 5 minutes, you\'re going to design your first agent. Three decisions, no code required."',
      '"First: name your agent. Pick a name that tells students what it does. Second: define one thing it owns — its scope. Narrow is better. Third: define one thing it must never do — that\'s your constitutional boundary."',
      '"These three decisions — identity, scope, boundaries — map directly to the 47 Doors architecture. Name becomes the system prompt. Scope becomes the routing table. Boundaries become the tool inventory."',
    ],
    actions: [
      { icon: '👀', text: 'Navigate to "Your First Agent" tab in the workshop site' },
      { icon: '🗣️', text: 'Walk the audience through the 3 steps on screen' },
      { icon: '🖱️', text: 'Fill in an example live: "LibraryGuide" / "Library resource help" / "Access student records"' },
      { icon: '🗣️', text: 'Give audience 3 minutes to fill in their own' },
      { icon: '🗣️', text: 'Ask 2-3 volunteers to share their agent design' },
    ],
    showTarget: 'Workshop site → Your First Agent tab',
  },
  {
    id: 'closing',
    timeStart: '43:00',
    timeEnd: '45:00',
    durationMin: 2,
    elapsedEnd: 45,
    title: 'Closing & Q&A',
    category: 'narrative',
    talkTrack: [
      '"Let me recap what we covered. You saw a 3-agent pipeline that detects intent, routes requests, and takes actions — with exactly 4 tools and 7 constitutional principles. You saw it work in text and voice. You saw it degrade gracefully. And you designed your own agent."',
      '"You\'re not buying a chatbot — you\'re giving every student a trusted digital colleague who is always available, always accurate, and always gets them to the right place — whether they type or talk."',
      '"The repo is open source. Clone it, run it in mock mode with no Azure credentials, or deploy it live with azd up. Questions?"',
    ],
    actions: [
      { icon: '👀', text: 'Return to the Overview tab as visual anchor' },
      { icon: '🗣️', text: 'Deliver the closing line with conviction' },
      { icon: '🗣️', text: 'Share repo link and documentation URL' },
      { icon: '🗣️', text: 'Open the floor for Q&A' },
    ],
    showTarget: 'Workshop site → Overview tab',
  },
]

function SectionCard({ section }: { section: ScriptSection }) {
  const [isOpen, setIsOpen] = useState(true)
  const style = categoryStyles[section.category]

  return (
    <div
      className={`card border-l-4 ${style.border}`}
      role="region"
      aria-label={`${section.title} — ${section.timeStart} to ${section.timeEnd}`}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full text-left focus:outline-none focus:ring-2 focus:ring-microsoft-blue focus:ring-offset-2 rounded"
        aria-expanded={isOpen}
        aria-controls={`section-${section.id}`}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4 flex-1">
            {/* Time marker */}
            <div className="flex-shrink-0 text-center min-w-[5rem]">
              <div className="text-lg font-bold text-dark-text leading-tight">{section.timeStart}</div>
              <div className="text-xs text-gray-500">to {section.timeEnd}</div>
              <div className="mt-1 inline-block px-2 py-0.5 bg-gray-100 rounded text-xs font-medium text-gray-600">
                {section.durationMin} min
              </div>
            </div>

            {/* Title + badge */}
            <div className="flex-1">
              <div className="flex items-center gap-3 flex-wrap">
                <h3 className="text-xl font-semibold text-dark-text">{section.title}</h3>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${style.badge}`}>
                  {style.badgeText}
                </span>
              </div>
              {/* Show target teaser */}
              <p className="text-sm text-gray-500 mt-1">📺 {section.showTarget}</p>
            </div>
          </div>

          {/* Collapse toggle */}
          <div className="flex-shrink-0 mt-1 text-gray-400">
            {isOpen ? <ChevronUpIcon className="w-5 h-5" /> : <ChevronDownIcon className="w-5 h-5" />}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3 flex items-center gap-2">
          <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                section.category === 'demo'
                  ? 'bg-green-400'
                  : section.category === 'exercise'
                  ? 'bg-amber-400'
                  : 'bg-microsoft-blue'
              }`}
              style={{ width: `${(section.elapsedEnd / 45) * 100}%` }}
            />
          </div>
          <span className="text-xs text-gray-500 flex-shrink-0">{section.elapsedEnd}/45 min</span>
        </div>
      </button>

      {isOpen && (
        <div id={`section-${section.id}`} className="mt-5 space-y-4">
          {/* Talk track */}
          <div>
            <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
              🗣️ Talk Track
            </h4>
            <div className="space-y-2">
              {section.talkTrack.map((line, i) => (
                <p key={i} className="text-gray-700 italic bg-gray-50 rounded p-3 text-sm leading-relaxed border-l-2 border-gray-300">
                  {line}
                </p>
              ))}
            </div>
          </div>

          {/* Action cues */}
          <div>
            <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Action Cues
            </h4>
            <div className="space-y-1.5">
              {section.actions.map((action, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-sm bg-blue-50 rounded px-3 py-2 border-l-2 border-microsoft-blue"
                >
                  <span className="flex-shrink-0">{action.icon}</span>
                  <span className="text-gray-800">{action.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Show target callout */}
          <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-3 border border-gray-200">
            <span className="text-lg">📺</span>
            <div>
              <span className="text-xs font-semibold text-gray-500 uppercase">What to show</span>
              <p className="text-sm font-medium text-dark-text">{section.showTarget}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function PresenterScript() {
  return (
    <div role="tabpanel" id="presenter-script-panel" aria-labelledby="presenter-script-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-2">
          Presenter Script
        </h2>
        <p className="text-xl text-gray-600 mb-4">
          Timed, step-by-step guide for delivering the 45-minute workshop
        </p>

        {/* Legend + overview strip */}
        <div className="card mb-8">
          <div className="flex flex-wrap items-center gap-6 mb-4">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-microsoft-blue inline-block" />
              <span className="text-sm text-gray-700">Narrative</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-green-500 inline-block" />
              <span className="text-sm text-gray-700">Live Demo</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500 inline-block" />
              <span className="text-sm text-gray-700">Exercise</span>
            </div>
          </div>

          {/* Visual timeline bar */}
          <div className="flex h-3 rounded-full overflow-hidden" aria-label="Workshop timeline overview">
            {sections.map((s) => (
              <div
                key={s.id}
                className={`${
                  s.category === 'demo'
                    ? 'bg-green-400'
                    : s.category === 'exercise'
                    ? 'bg-amber-400'
                    : 'bg-microsoft-blue'
                }`}
                style={{ width: `${(s.durationMin / 45) * 100}%` }}
                title={`${s.title} (${s.durationMin} min)`}
              />
            ))}
          </div>
          <div className="flex justify-between mt-1 text-xs text-gray-500">
            <span>0:00</span>
            <span>15:00</span>
            <span>30:00</span>
            <span>45:00</span>
          </div>
        </div>

        {/* Section cards */}
        <div className="space-y-6">
          {sections.map((section) => (
            <SectionCard key={section.id} section={section} />
          ))}
        </div>

        {/* Quick-reference footer */}
        <div className="mt-10 card bg-gray-50">
          <h3 className="font-semibold text-lg text-dark-text mb-4">⏱️ Quick Reference</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-dark-text mb-2">Key Phrases to Repeat</h4>
              <ul className="space-y-1 text-gray-700">
                <li>• "Trust is architecture, not policy"</li>
                <li>• "The tool doesn't exist"</li>
                <li>• "One front door"</li>
                <li>• "Trusted digital colleague"</li>
                <li>• "4 tools, 7 principles"</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-dark-text mb-2">If Things Go Wrong</h4>
              <ul className="space-y-1 text-gray-700">
                <li>• Voice fails → "This is graceful degradation in action"</li>
                <li>• Slow response → "Cold start — just like a real colleague getting coffee"</li>
                <li>• Unexpected answer → "The audit trail shows exactly what happened"</li>
                <li>• Demo crashes → Switch to workshop site Demo Walkthrough tab</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
