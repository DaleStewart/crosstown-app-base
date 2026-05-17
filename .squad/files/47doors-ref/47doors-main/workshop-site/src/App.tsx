import { useState } from 'react'
import TabNavigation from './components/TabNavigation'
import Footer from './components/Footer'

// Tab components
import Overview from './tabs/Overview'
import TheProblem from './tabs/TheProblem'
import ChatbotsToAgents from './tabs/ChatbotsToAgents'
import TrustBoundaries from './tabs/TrustBoundaries'
import Architecture from './tabs/Architecture'
import VoiceAccessibility from './tabs/VoiceAccessibility'
import Telephony from './tabs/Telephony'
import DemoWalkthrough from './tabs/DemoWalkthrough'
import ResponsibleAI from './tabs/ResponsibleAI'
import ReuseAcrossCampus from './tabs/ReuseAcrossCampus'
import YourFirstAgent from './tabs/YourFirstAgent'
import PresenterScript from './tabs/PresenterScript'

const tabs = [
  { id: 'overview', label: 'Overview', component: Overview },
  { id: 'problem', label: 'The Problem', component: TheProblem },
  { id: 'chatbots-to-agents', label: 'Chatbots to Agents', component: ChatbotsToAgents },
  { id: 'trust', label: 'Trust & Boundaries', component: TrustBoundaries },
  { id: 'architecture', label: 'Architecture', component: Architecture },
  { id: 'voice', label: 'Voice & Accessibility', component: VoiceAccessibility },
  { id: 'telephony', label: 'Phone Integration', component: Telephony },
  { id: 'demo', label: 'Demo Walkthrough', component: DemoWalkthrough },
  { id: 'responsible-ai', label: 'Responsible AI', component: ResponsibleAI },
  { id: 'reuse', label: 'Reuse Across Campus', component: ReuseAcrossCampus },
  { id: 'your-first-agent', label: 'Your First Agent', component: YourFirstAgent },
  { id: 'presenter-script', label: 'Presenter Script', component: PresenterScript },
]

function App() {
  const [activeTab, setActiveTab] = useState('overview')

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || Overview

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-semibold text-dark-text">
            Trustworthy Agentic AI in Higher Education
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            47 Doors Workshop Companion
          </p>
        </div>
        <TabNavigation tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        <ActiveComponent />
      </main>

      <Footer />
    </div>
  )
}

export default App
