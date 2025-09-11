import { useEffect } from 'react'
import './App.css'
import Viewport from './components/Viewport/Viewport'
import SceneOutliner from './components/SceneOutliner/SceneOutliner'
import PropertiesInspector from './components/PropertiesInspector/PropertiesInspector'
import AIChatSidebar from './components/AIChatSidebar/AIChatSidebar'
import ViewportControls from './components/ViewportControls/ViewportControls'

// Import the centralized store
import { useSession, useSystemState, useUIState, useActions, checkSystemHealth } from './store/designStore'

function App() {
  // Use the centralized store instead of local state
  const session = useSession()
  const system = useSystemState()
  const ui = useUIState()
  const actions = useActions()

  // Initialize the application
  useEffect(() => {
    const initialize = async () => {
      try {
        // Try to check system health first
        try {
          const healthStatus = await checkSystemHealth()
          actions.setSystemStatus(healthStatus)
        } catch (error) {
          console.log('Backend unavailable, running in demo mode')
          actions.setSystemStatus('error')
        }
        
        // Try to initialize design session
        try {
          await actions.initializeSession()
        } catch (error) {
          console.log('Session initialization failed, running in demo mode')
        }
        
        // Load the diamond ring example model for demonstration (works without backend)
        actions.loadGLBModel('/3d_models/diamond_ring_example.glb', 'Diamond Ring Example')
        
        console.log('✅ Aura Sentient Design Studio initialized (demo mode)')
      } catch (error) {
        console.error('Failed to initialize application:', error)
        actions.setSystemStatus('error')
      }
    }

    initialize()
  }, [actions])

  // Get selected object from session
  const selectedObject = session.objects.find(obj => obj.id === session.selectedObjectId)

  return (
    <div className={`design-studio ${!ui.isLeftSidebarVisible ? 'left-sidebar-hidden' : ''} ${!ui.isRightSidebarVisible ? 'right-sidebar-hidden' : ''}`}>
      {/* Header */}
      <div className="header">
        <div className="header-left">
          <button 
            className="sidebar-toggle-btn"
            onClick={actions.toggleLeftSidebar}
            title="Toggle Scene Outliner"
          >
            📋
          </button>
          <div className="logo">
            <span>💎</span>
            <span>Aura Sentient Design Studio</span>
          </div>
        </div>
        <div className="header-right">
          <div className="status">
            <div className={`status-indicator status-${system.status}`}></div>
            <span>{system.status === 'online' ? 'System Online' : system.status === 'connecting' ? 'Connecting...' : 'System Error'}</span>
            <ViewportControls />
          </div>
          <button 
            className="sidebar-toggle-btn"
            onClick={actions.toggleRightSidebar}
            title="Toggle Properties & Chat"
          >
            🔧
          </button>
        </div>
      </div>

      {/* Scene Outliner */}
      {ui.isLeftSidebarVisible && (
        <SceneOutliner 
          objects={session.objects}
          selectedObjectId={session.selectedObjectId}
          onObjectSelect={actions.selectObject}
          onObjectUpdate={actions.updateObject}
        />
      )}

      {/* Main 3D Viewport */}
      <Viewport 
        objects={session.objects}
        selectedObjectId={session.selectedObjectId}
        onObjectSelect={actions.selectObject}
        onLayerSelect={actions.selectLayer}
        onGLBLayersDetected={actions.addGLBLayers}
        isGenerating={system.isGenerating}
      />

      {/* AI Chat Sidebar */}
      {ui.isRightSidebarVisible && (
        <AIChatSidebar 
          onPromptSubmit={actions.executeAIPrompt}
          isGenerating={system.isGenerating}
        />
      )}

      {/* Properties Inspector */}
      {ui.isRightSidebarVisible && (
        <PropertiesInspector 
          selectedObject={selectedObject}
          onObjectUpdate={actions.updateObject}
        />
      )}
    </div>
  )
}

export default App