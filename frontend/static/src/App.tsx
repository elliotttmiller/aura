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
        // Check system health first
        const healthStatus = await checkSystemHealth()
        actions.setSystemStatus(healthStatus)
        
        // Initialize design session
        await actions.initializeSession()
        
        console.log('✅ Aura Sentient Design Studio initialized')
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