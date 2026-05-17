import { useEffect, useRef } from 'react'

interface Tab {
  id: string
  label: string
}

interface TabNavigationProps {
  tabs: Tab[]
  activeTab: string
  onTabChange: (tabId: string) => void
}

export default function TabNavigation({ tabs, activeTab, onTabChange }: TabNavigationProps) {
  const tabRefs = useRef<{ [key: string]: HTMLButtonElement | null }>({})

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const currentIndex = tabs.findIndex(tab => tab.id === activeTab)
      
      if (e.key === 'ArrowRight' && currentIndex < tabs.length - 1) {
        const nextTab = tabs[currentIndex + 1]
        onTabChange(nextTab.id)
        tabRefs.current[nextTab.id]?.focus()
      } else if (e.key === 'ArrowLeft' && currentIndex > 0) {
        const prevTab = tabs[currentIndex - 1]
        onTabChange(prevTab.id)
        tabRefs.current[prevTab.id]?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [activeTab, tabs, onTabChange])

  return (
    <nav 
      className="border-b border-gray-200 overflow-x-auto"
      role="tablist"
      aria-label="Workshop sections"
    >
      <div className="max-w-7xl mx-auto px-4 flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            ref={(el) => { tabRefs.current[tab.id] = el }}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`${tab.id}-panel`}
            id={`${tab.id}-tab`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            className={`tab-button whitespace-nowrap ${
              activeTab === tab.id ? 'tab-button-active' : ''
            }`}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </nav>
  )
}
