import { ReactNode } from 'react'

interface DiagramSVGProps {
  children: ReactNode
  title: string
  description?: string
  viewBox?: string
  className?: string
}

export default function DiagramSVG({ 
  children, 
  title, 
  description, 
  viewBox = "0 0 800 400",
  className = "w-full h-auto"
}: DiagramSVGProps) {
  return (
    <figure className="my-6">
      <svg 
        viewBox={viewBox} 
        className={className}
        role="img"
        aria-labelledby="diagram-title diagram-desc"
      >
        <title id="diagram-title">{title}</title>
        {description && <desc id="diagram-desc">{description}</desc>}
        {children}
      </svg>
      {description && (
        <figcaption className="text-sm text-gray-600 mt-2 text-center">
          {description}
        </figcaption>
      )}
    </figure>
  )
}
