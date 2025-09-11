import React, { useState, useRef, useEffect } from 'react'
import './AIChatSidebar.css'

interface ChatMessage {
  id: string
  type: 'user' | 'ai' | 'system'
  content: string
  timestamp: Date
}

interface AIChatSidebarProps {
  onPromptSubmit: (prompt: string) => Promise&lt;void&gt;
  isGenerating: boolean
}

export default function AIChatSidebar({ onPromptSubmit, isGenerating }: AIChatSidebarProps) {
  const [messages, setMessages] = useState&lt;ChatMessage[]&gt;([
    {
      id: 'welcome',
      type: 'ai',
      content: '🤖 Welcome to the Aura Sentient Design Studio! I\'m your AI design partner. Describe your jewelry vision and I\'ll create it for you in real-time.',
      timestamp: new Date()
    }
  ])
  const [currentPrompt, setCurrentPrompt] = useState('')
  const messagesEndRef = useRef&lt;HTMLDivElement&gt;(null)

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

    setMessages(prev =&gt; [...prev, userMessage])
    setCurrentPrompt('')

    // Show AI thinking message
    const thinkingMessage: ChatMessage = {
      id: `ai-thinking-${Date.now()}`,
      type: 'ai',
      content: '🧠 Analyzing your design request...',
      timestamp: new Date()
    }
    setMessages(prev =&gt; [...prev, thinkingMessage])

    try {
      await onPromptSubmit(userMessage.content)
      
      // Remove thinking message and add success message
      setMessages(prev =&gt; {
        const withoutThinking = prev.filter(msg =&gt; msg.id !== thinkingMessage.id)
        return [...withoutThinking, {
          id: `ai-success-${Date.now()}`,
          type: 'ai',
          content: '✨ Perfect! I\'ve created your design. You can now see it in the 3D viewport and adjust its properties in the inspector panel.',
          timestamp: new Date()
        }]
      })
    } catch (error) {
      // Remove thinking message and add error message
      setMessages(prev =&gt; {
        const withoutThinking = prev.filter(msg =&gt; msg.id !== thinkingMessage.id)
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

  return (
    &lt;div className="chat"&gt;
      &lt;div className="panel-title"&gt;AI Design Collaborator&lt;/div&gt;
      
      {/* Chat messages */}
      &lt;div className="chat-messages"&gt;
        {messages.map(message =&gt; (
          &lt;div key={message.id} className={`message ${message.type}`}&gt;
            &lt;div className="message-content"&gt;
              {message.content}
            &lt;/div&gt;
            &lt;div className="message-time"&gt;
              {formatTime(message.timestamp)}
            &lt;/div&gt;
          &lt;/div&gt;
        ))}
        &lt;div ref={messagesEndRef} /&gt;
      &lt;/div&gt;

      {/* Quick prompt suggestions */}
      &lt;div className="quick-prompts"&gt;
        &lt;div className="quick-prompts-label"&gt;Quick Ideas:&lt;/div&gt;
        &lt;button 
          className="quick-prompt-btn"
          onClick={() =&gt; handleQuickPrompt('Create an elegant engagement ring with a 1.5 carat diamond')}
        &gt;
          💍 Engagement Ring
        &lt;/button&gt;
        &lt;button 
          className="quick-prompt-btn"
          onClick={() =&gt; handleQuickPrompt('Design a vintage-style gold necklace with Art Deco patterns')}
        &gt;
          📿 Vintage Necklace
        &lt;/button&gt;
        &lt;button 
          className="quick-prompt-btn"
          onClick={() =&gt; handleQuickPrompt('Make a modern minimalist silver bracelet with geometric elements')}
        &gt;
          ⚡ Modern Bracelet
        &lt;/button&gt;
      &lt;/div&gt;

      {/* Chat input */}
      &lt;form className="chat-input-form" onSubmit={handleSubmit}&gt;
        &lt;div className="input-container"&gt;
          &lt;textarea
            value={currentPrompt}
            onChange={(e) =&gt; setCurrentPrompt(e.target.value)}
            placeholder="Describe your jewelry design vision..."
            className="chat-input"
            disabled={isGenerating}
            rows={3}
            onKeyDown={(e) =&gt; {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
          /&gt;
          &lt;button 
            type="submit" 
            className={`send-btn ${isGenerating ? 'generating' : ''}`}
            disabled={!currentPrompt.trim() || isGenerating}
          &gt;
            {isGenerating ? '🔄' : '🚀'}
          &lt;/button&gt;
        &lt;/div&gt;
        &lt;div className="input-hint"&gt;
          {isGenerating ? 'AI is creating your design...' : 'Press Enter to send, Shift+Enter for new line'}
        &lt;/div&gt;
      &lt;/form&gt;
    &lt;/div&gt;
  )
}