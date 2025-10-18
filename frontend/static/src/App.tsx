import { lazy, Suspense, useEffect } from 'react';
import './App.css';
import './fullpage-container.css';
import { useSession, useSystemState, useUIState, useActions } from './store/designStore';

const Viewport = lazy(() => import('./components/Viewport/Viewport'));
const SceneOutliner = lazy(() => import('./components/SceneOutliner/SceneOutliner'));
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

  // No inline styles: sidebar widths and handle positions are controlled via CSS classes/variables in fullpage-container.css
  const gridClasses = [
    'design-studio-grid',
    ui.isLeftSidebarVisible ? 'left-open' : 'left-closed',
    ui.isRightSidebarVisible ? 'right-open' : 'right-closed',
  ].join(' ');

  return (
    <div className="fullpage-container">
      <Suspense fallback={<div className="loading">Loading...</div>}>
        <div className={gridClasses}>
          {/* Header - spans all three columns */}
          <header className="header">
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
          </header>

          {/* Left Sidebar (Scene Outliner) - MUST be second child to match grid order */}
          <aside className={`sidebar sidebar-left ${ui.isLeftSidebarVisible ? '' : 'closed'}`}>
            <SceneOutliner 
              objects={session.objects}
              selectedObjectId={session.selectedObjectId}
              onObjectSelect={actions.selectObject}
              onObjectUpdate={(objectId: string, updates: Partial<import('./store/designStore').SceneObject>) => { void actions.updateObject(objectId, updates); }}
            />
          </aside>

          {/* Main 3D Viewport - MUST be third child to match grid order */}
          <main className="main-viewport">
            <Viewport 
              objects={session.objects}
              selectedObjectId={session.selectedObjectId}
              onObjectSelect={actions.selectObject}
              onLayerSelect={actions.selectLayer}
              onGLBLayersDetected={actions.addGLBLayers}
              isGenerating={system.isGenerating}
            />
          </main>

          {/* Right Sidebar (AI Chat) - MUST be fourth child to match grid order */}
          <aside className={`sidebar sidebar-right ai-chat-sidebar ${ui.isRightSidebarVisible ? '' : 'closed'}`}>
            <AIChatSidebar 
              onPromptSubmit={(prompt: string) => actions.executeAIPrompt(prompt)}
              isGenerating={system.isGenerating}
            />
          </aside>

          {/* Floating toggle handles */}
          <button
            className="sidebar-handle left"
            onClick={actions.toggleLeftSidebar}
            aria-label="Toggle left panel"
            title="Toggle Scene Outliner"
          >
            <span className="icon">{ui.isLeftSidebarVisible ? '◀' : '▶'}</span>
          </button>

          <button
            className="sidebar-handle right"
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
