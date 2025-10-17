import { lazy, Suspense, useEffect } from 'react';
import './App.css';
import './fullpage-container.css';
import { useSession, useSystemState, useUIState, useActions } from './store/designStore';

const Viewport = lazy(() => import('./components/Viewport/Viewport'));
const SceneOutliner = lazy(() => import('./components/SceneOutliner/SceneOutliner'));
const PropertiesInspector = lazy(() => import('./components/PropertiesInspector/PropertiesInspector'));
const AIChatSidebar = lazy(() => import('./components/AIChatSidebar/AIChatSidebar'));
const ViewportControls = lazy(() => import('./components/ViewportControls/ViewportControls'));

function App() {
  // Ensure a valid session is always initialized on mount
  useEffect(() => {
    if (!session.id || session.id === 'new-session') {
      actions.initializeSession();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const ui = useUIState();
  const system = useSystemState();
  const session = useSession();
  const actions = useActions();
  const selectedObject = session.objects.find(obj => obj.id === session.selectedObjectId) || undefined;

  return (
    <div className="fullpage-container">
      <Suspense fallback={<div className="loading">Loading...</div>}>
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

          {/* Left Sidebar (Scene Outliner) */}
          {ui.isLeftSidebarVisible && (
            <div className="sidebar">
              <SceneOutliner 
                objects={session.objects}
                selectedObjectId={session.selectedObjectId}
                onObjectSelect={actions.selectObject}
                onObjectUpdate={(objectId, updates) => { void actions.updateObject(objectId, updates); }}
              />
            </div>
          )}

          {/* Main 3D Viewport */}
          <div className="main-viewport">
            <Viewport 
              objects={session.objects}
              selectedObjectId={session.selectedObjectId}
              onObjectSelect={actions.selectObject}
              onLayerSelect={actions.selectLayer}
              onGLBLayersDetected={actions.addGLBLayers}
              isGenerating={system.isGenerating}
            />
          </div>

          {/* AI Chat Sidebar (right sidebar, styled like left sidebar) */}
          {ui.isRightSidebarVisible && (
            <div className="sidebar ai-chat-sidebar">
              <AIChatSidebar 
                onPromptSubmit={actions.executeAIPrompt}
                isGenerating={system.isGenerating}
              />
            </div>
          )}

          {/* Properties Inspector (only when object selected) */}
          {selectedObject && (
            <div className="properties-inspector">
              <PropertiesInspector 
                selectedObject={selectedObject}
                onObjectUpdate={actions.updateObject}
              />
            </div>
          )}
        </div>
      </Suspense>
    </div>
  );
}

export default App;
