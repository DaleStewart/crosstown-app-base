import { useState } from 'react'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'

interface CollapsibleNotesProps {
  children: React.ReactNode
}

export default function CollapsibleNotes({ children }: CollapsibleNotesProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="mt-8 border-t border-gray-200 pt-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-microsoft-blue transition-colors focus:outline-none focus:ring-2 focus:ring-microsoft-blue focus:ring-offset-2 rounded px-2 py-1"
        aria-expanded={isOpen}
        aria-controls="presenter-notes"
      >
        {isOpen ? (
          <ChevronUpIcon className="w-4 h-4" />
        ) : (
          <ChevronDownIcon className="w-4 h-4" />
        )}
        Presenter Notes
      </button>
      
      {isOpen && (
        <div 
          id="presenter-notes"
          className="mt-4 bg-gray-50 rounded-lg p-4 text-sm text-gray-700 leading-relaxed"
        >
          {children}
        </div>
      )}
    </div>
  )
}
