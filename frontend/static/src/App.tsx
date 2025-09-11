import React, { useState, useEffect } from 'react'
import './App.css'
import Viewport from './components/Viewport/Viewport'
import SceneOutliner from './components/SceneOutliner/SceneOutliner'
import PropertiesInspector from './components/PropertiesInspector/PropertiesInspector'
import AIChatSidebar from './components/AIChatSidebar/AIChatSidebar'
import ViewportControls from './components/ViewportControls/ViewportControls'

// Types for the design session state
interface SceneObject {
  id: string
  name: string
  type: string
  visible: boolean
  transform: {
    position: [number, number, number]
    rotation: [number, number, number]
    scale: [number, number, number]
  }
  material: {
    color: string
    roughness: number
    metallic: number
  }
}

interface DesignSession {
  id: string
  objects: SceneObject[]
  selectedObjectId: string | null
}

function App() {
  const [session, setSession] = useState<DesignSession>({
    id: 'new-session',
    objects: [],
    selectedObjectId: null
  })
  
  const [systemStatus, setSystemStatus] = useState('online')
  const [isGenerating, setIsGenerating] = useState(false)

  // Initialize session on component mount
  useEffect(() => {
    initializeSession()
    checkSystemHealth()
  }, [])

  const initializeSession = async () => {
    try {
      // TODO: Call backend to create new session
      console.log('Initializing new design session...')
    } catch (error) {
      console.error('Failed to initialize session:', error)
    }
  }

  const checkSystemHealth = async () => {
    try {
      const response = await fetch('/api/health')
      const health = await response.json()
      setSystemStatus(health.status === 'healthy' ? 'online' : 'error')
    } catch (error) {
      console.error('Health check failed:', error)
      setSystemStatus('error')
    }
  }

  const handleObjectSelection = (objectId: string | null) => {
    setSession(prev => ({
      ...prev,
      selectedObjectId: objectId
    }))
  }

  const handleObjectUpdate = (objectId: string, updates: Partial<SceneObject>) => {
    setSession(prev => ({
      ...prev,
      objects: prev.objects.map(obj => 
        obj.id === objectId ? { ...obj, ...updates } : obj
      )
    }))
  }

  const handleAIPrompt = async (prompt: string) => {
    setIsGenerating(true)
    try {
      // TODO: Call backend AI endpoint
      console.log('Processing AI prompt:', prompt)
      
      // Simulate AI response with mock object creation
      const newObject: SceneObject = {
        id: `obj-${Date.now()}`,
        name: 'AI Generated Design',
        type: 'mesh',
        visible: true,
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1]
        },
        material: {
          color: '#FFD700',
          roughness: 0.2,
          metallic: 0.8
        }
      }
      
      setSession(prev => ({
        ...prev,
        objects: [...prev.objects, newObject],
        selectedObjectId: newObject.id
      }))
      
    } catch (error) {
      console.error('AI prompt failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const selectedObject = session.objects.find(obj => obj.id === session.selectedObjectId)

  return (
    <div className="design-studio">
      {/* Header */}
      <div className="header">
        <div className="logo">
          <span>💎</span>
          <span>Aura Sentient Design Studio</span>
        </div>
        <div className="status">
          <div className={`status-indicator status-${systemStatus}`}></div>
          <span>{systemStatus === 'online' ? 'System Online' : 'System Error'}</span>
          <ViewportControls />
        </div>
      </div>

      {/* Scene Outliner */}
      <SceneOutliner 
        objects={session.objects}
        selectedObjectId={session.selectedObjectId}
        onObjectSelect={handleObjectSelection}
        onObjectUpdate={handleObjectUpdate}
      />

      {/* Main 3D Viewport */}
      <Viewport 
        objects={session.objects}
        selectedObjectId={session.selectedObjectId}
        onObjectSelect={handleObjectSelection}
        isGenerating={isGenerating}
      />

      {/* AI Chat Sidebar */}
      <AIChatSidebar 
        onPromptSubmit={handleAIPrompt}
        isGenerating={isGenerating}
      />

      {/* Properties Inspector */}
      <PropertiesInspector 
        selectedObject={selectedObject}
        onObjectUpdate={handleObjectUpdate}
      />
    </div>
  )
}

export default App