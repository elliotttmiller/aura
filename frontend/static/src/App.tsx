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
  const ui = useUIState();
  const system = useSystemState();
  const session = useSession();
  const actions = useActions();
  
  // Ensure a valid session is always initialized on mount
  useEffect(() => {
    if (!session.id || session.id === 'new-session') {
      actions.initializeSession();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  const selectedObject = session.objects.find(obj => obj.id === session.selectedObjectId) || undefined;

  const leftWidth = ui.isLeftSidebarVisible ? 280 : 0;
  const rightWidth = ui.isRightSidebarVisible ? 340 : 0;
  // Handle position offsets: handle width (28) + inner margin (8) = 36
  const leftHandle = ui.isLeftSidebarVisible ? Math.max(8, leftWidth - 36) : 8;
  const rightHandle = ui.isRightSidebarVisible ? Math.max(8, rightWidth - 36) : 8;

  const gridStyle = {
    '--left-width': `${leftWidth}px`,
    '--right-width': `${rightWidth}px`,
  } as React.CSSProperties & Record<'--left-width' | '--right-width', string>

  return (
    <div className="fullpage-container">
      <Suspense fallback={<div className="loading">Loading...</div>}>
        <div className="design-studio-grid" style={gridStyle}>
          {/* Header */}
          <div className="header" style={{ gridArea: 'header' }}>
            <div className="header-left">
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
            </div>
          </div>

          {/* Left Sidebar (Scene Outliner) - always mounted for smooth close */}
          <div className={`sidebar sidebar-left ${ui.isLeftSidebarVisible ? '' : 'closed'}`} style={{ gridArea: 'sidebar-left' }}>
            <SceneOutliner 
              objects={session.objects}
              selectedObjectId={session.selectedObjectId}
              onObjectSelect={actions.selectObject}
              onObjectUpdate={(objectId: string, updates: Partial<import('./store/designStore').SceneObject>) => { void actions.updateObject(objectId, updates); }}
            />
          </div>

          {/* Main 3D Viewport */}
          <div className="main-viewport" style={{ gridArea: 'main' }}>
            <Viewport 
              objects={session.objects}
              selectedObjectId={session.selectedObjectId}
              onObjectSelect={actions.selectObject}
              onLayerSelect={actions.selectLayer}
              onGLBLayersDetected={actions.addGLBLayers}
              isGenerating={system.isGenerating}
            />
          </div>

          {/* AI Chat Sidebar (right sidebar) - always mounted for smooth close */}
          <div className={`sidebar sidebar-right ai-chat-sidebar ${ui.isRightSidebarVisible ? '' : 'closed'}`} style={{ gridArea: 'sidebar-right' }}>
            <AIChatSidebar 
              onPromptSubmit={(prompt: string) => actions.executeAIPrompt(prompt)}
              isGenerating={system.isGenerating}
            />
          </div>

          {/* Properties Inspector (only when object selected) */}
          {selectedObject && (
            <div className="properties-inspector">
              <PropertiesInspector 
                selectedObject={selectedObject}
                onObjectUpdate={(objectId: string, updates: Partial<import('./store/designStore').SceneObject>) => actions.updateObject(objectId, updates)}
              />
            </div>
          )}
          {/* Floating handles */}
          <button
            className="sidebar-handle left"
            style={{ left: `${leftHandle}px` }}
            onClick={actions.toggleLeftSidebar}
            aria-label="Toggle left panel"
            title="Toggle Scene Outliner"
          >
            <span className="icon">{ui.isLeftSidebarVisible ? '◀' : '▶'}</span>
          </button>

          <button
            className="sidebar-handle right"
            style={{ right: `${rightHandle}px` }}
            onClick={actions.toggleRightSidebar}
            aria-label="Toggle right panel"
            title="Toggle AI Chat"
          >
            <span className="icon">{ui.isRightSidebarVisible ? '▶' : '◀'}</span>
          </button>

        </div>
      </Suspense>
    </div>
  );
}

export default App;
