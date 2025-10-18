import React, { useState, useRef, useEffect } from 'react'
import './AIChatSidebar.css'
import ModelUploader from '../ModelUploader/ModelUploader'
import { useActions } from '../../store/designStore'

interface ChatMessage {
  id: string
  type: 'user' | 'ai' | 'system'
  content: string
  timestamp: Date
}

interface AIChatSidebarProps {
  onPromptSubmit: (prompt: string) => Promise<void>
  isGenerating: boolean
}

export default function AIChatSidebar({ onPromptSubmit, isGenerating }: AIChatSidebarProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      type: 'ai',
      content: '🤖 Welcome to the Aura Sentient Design Studio! I\'m your AI design partner. Describe your jewelry vision and I\'ll create it for you in real-time.',
      timestamp: new Date()
    }
  ])
  const [currentPrompt, setCurrentPrompt] = useState('')
  const [showUploader, setShowUploader] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const actions = useActions()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!currentPrompt.trim() || isGenerating) return

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: currentPrompt,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setCurrentPrompt('')

    // Show AI thinking message
    const thinkingMessage: ChatMessage = {
      id: `ai-thinking-${Date.now()}`,
      type: 'ai',
      content: '🧠 Analyzing your design request...',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, thinkingMessage])

    try {
      await onPromptSubmit(userMessage.content)
      
      // Remove thinking message and add success message
      setMessages(prev => {
        const withoutThinking = prev.filter(msg => msg.id !== thinkingMessage.id)
        return [...withoutThinking, {
          id: `ai-success-${Date.now()}`,
          type: 'ai',
          content: '✨ Perfect! I\'ve created your design. You can now see it in the 3D viewport and adjust its properties in the inspector panel.',
          timestamp: new Date()
        }]
      })
    } catch (error) {
      // Remove thinking message and add error message
      setMessages(prev => {
        const withoutThinking = prev.filter(msg => msg.id !== thinkingMessage.id)
        return [...withoutThinking, {
          id: `ai-error-${Date.now()}`,
          type: 'ai',
          content: '❌ Sorry, I encountered an error creating your design. Please try describing it differently.',
          timestamp: new Date()
        }]
      })
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const handleQuickPrompt = (prompt: string) => {
    setCurrentPrompt(prompt)
  }

  const handleUploadSuccess = (modelUrl: string, modelName: string) => {
    // Add uploaded model to scene with explicit 'uploaded' source
    actions.loadGLBModel(modelUrl, modelName, 'uploaded')
    setMessages(prev => [...prev, {
      id: `upload-success-${Date.now()}`,
      type: 'ai',
      content: `✨ "${modelName}" is ready in the viewport. Adjust it in the scene outliner when you're ready.`,
      timestamp: new Date()
    }])
    setShowUploader(false)
  }

  const handleUploadError = (errorMessage: string) => {
    setMessages(prev => [...prev, {
      id: `upload-error-${Date.now()}`,
      type: 'ai',
      content: `⚠️ Upload issue: ${errorMessage}`,
      timestamp: new Date()
    }])
  }

  return (
    <div className="chat">
      <div className="panel-title">AI Design Collaborator</div>

      <div className="upload-section">
        <button 
          className="upload-toggle-btn"
          type="button"
          onClick={() => setShowUploader(prev => !prev)}
        >
          {showUploader ? 'Close Upload' : '📁 Upload Model'}
        </button>
        {showUploader && (
          <ModelUploader 
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        )}
      </div>
      
      {/* Chat messages */}
      <div className="chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              {message.content}
            </div>
            <div className="message-time">
              {formatTime(message.timestamp)}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick prompt suggestions */}
      <div className="quick-prompts">
        <div className="quick-prompts-label">Quick Ideas:</div>
        <button 
          className="quick-prompt-btn"
          onClick={() => handleQuickPrompt('Create an elegant engagement ring with a 1.5 carat diamond')}
        >
          💍 Engagement Ring
        </button>
        <button 
          className="quick-prompt-btn"
          onClick={() => handleQuickPrompt('Design a vintage-style gold necklace with Art Deco patterns')}
        >
          📿 Vintage Necklace
        </button>
        <button 
          className="quick-prompt-btn"
          onClick={() => handleQuickPrompt('Make a modern minimalist silver bracelet with geometric elements')}
        >
          ⚡ Modern Bracelet
        </button>
      </div>

      {/* Chat input */}
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="input-container">
          <textarea
            value={currentPrompt}
            onChange={(e) => setCurrentPrompt(e.target.value)}
            placeholder="Describe your jewelry design vision..."
            className="chat-input"
            disabled={isGenerating}
            rows={3}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
          />
          <button 
            type="submit" 
            className={`send-btn ${isGenerating ? 'generating' : ''}`}
            disabled={!currentPrompt.trim() || isGenerating}
          >
            {isGenerating ? '🔄' : '🚀'}
          </button>
        </div>
        <div className="input-hint">
          {isGenerating ? 'AI is creating your design...' : 'Press Enter to send, Shift+Enter for new line'}
        </div>
      </form>
    </div>
  )
}