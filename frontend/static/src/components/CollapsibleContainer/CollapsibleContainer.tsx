import { useState, ReactNode } from 'react'
import './CollapsibleContainer.css'

interface CollapsibleContainerProps {
  title: string
  children: ReactNode
  defaultOpen?: boolean
  className?: string
  icon?: string
}

export default function CollapsibleContainer({ 
  title, 
  children, 
  defaultOpen = true, 
  className = '', 
  icon 
}: CollapsibleContainerProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  const toggleOpen = () => {
    setIsOpen(!isOpen)
  }

  return (
    <div className={`collapsible-container ${className} ${isOpen ? 'open' : 'collapsed'}`}>
      <div className="collapsible-header" onClick={toggleOpen}>
        <div className="header-content">
          {icon && <span className="header-icon">{icon}</span>}
          <span className="header-title">{title}</span>
        </div>
        <div className="toggle-icon">
          {isOpen ? '▼' : '▶'}
        </div>
      </div>
      <div className={`collapsible-content ${isOpen ? 'expanded' : 'collapsed'}`}>
        <div className="content-inner">
          {children}
        </div>
      </div>
    </div>
  )
}