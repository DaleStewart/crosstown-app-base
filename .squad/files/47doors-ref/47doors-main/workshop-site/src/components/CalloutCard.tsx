import { ReactNode } from 'react'

interface CalloutCardProps {
  title?: string
  children: ReactNode
  variant?: 'default' | 'accent'
  icon?: ReactNode
}

export default function CalloutCard({ title, children, variant = 'default', icon }: CalloutCardProps) {
  const borderClass = variant === 'accent' ? 'border-iu-crimson' : 'border-microsoft-blue'
  
  return (
    <div className={`callout ${borderClass}`}>
      {(title || icon) && (
        <div className="flex items-center gap-2 mb-2">
          {icon && <div className="text-microsoft-blue">{icon}</div>}
          {title && <h3 className="font-semibold text-dark-text">{title}</h3>}
        </div>
      )}
      <div className="text-gray-700 leading-relaxed">
        {children}
      </div>
    </div>
  )
}
