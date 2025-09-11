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
      console.log('Creating new design session...')
      const response = await fetch('/api/session/new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('✅ Session created:', data.session_id)
        setSession(prev => ({
          ...prev,
          id: data.session_id
        }))
      } else {
        console.error('Failed to create session')
      }
    } catch (error) {
      console.error('Failed to initialize session:', error)
    }
  }

  const checkSystemHealth = async () => {
    try {
      const response = await fetch('/api/health')
      const health = await response.json()
      setSystemStatus(health.status === 'healthy' ? 'online' : 'error')
      console.log('System health:', health)
    } catch (error) {
      console.error('Health check failed:', error)
      setSystemStatus('error')
    }
  }

  const loadSceneFromBackend = async () => {
    try {
      const response = await fetch(`/api/scene/${session.id}`)
      if (response.ok) {
        const data = await response.json()
        setSession(prev => ({
          ...prev,
          objects: data.scene.objects
        }))
      }
    } catch (error) {
      console.error('Failed to load scene:', error)
    }
  }

  const handleObjectSelection = (objectId: string | null) => {
    setSession(prev => ({
      ...prev,
      selectedObjectId: objectId
    }))
  }

  const handleObjectUpdate = async (objectId: string, updates: Partial<SceneObject>) => {
    // Optimistically update UI first
    setSession(prev => ({
      ...prev,
      objects: prev.objects.map(obj => 
        obj.id === objectId ? { ...obj, ...updates } : obj
      )
    }))

    // Then sync with backend
    try {
      if (updates.transform) {
        await fetch(`/api/object/${session.id}/${objectId}/transform`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updates.transform)
        })
      }
      
      if (updates.material) {
        await fetch(`/api/object/${session.id}/${objectId}/material`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updates.material)
        })
      }
      
      console.log('✅ Object updated on backend')
    } catch (error) {
      console.error('Failed to update object on backend:', error)
      // Could revert optimistic update here
    }
  }

  const handleAIPrompt = async (prompt: string) => {
    setIsGenerating(true)
    try {
      console.log('🤖 Processing AI prompt:', prompt)
      
      const response = await fetch(`/api/session/${session.id}/execute_prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt })
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('✅ AI prompt executed:', data)
        
        // Add the new object to our scene
        const newObject = data.object
        setSession(prev => ({
          ...prev,
          objects: [...prev.objects, newObject],
          selectedObjectId: newObject.id
        }))
      } else {
        throw new Error('AI prompt failed')
      }
      
    } catch (error) {
      console.error('AI prompt failed:', error)
      throw error // Re-throw for chat component to handle
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