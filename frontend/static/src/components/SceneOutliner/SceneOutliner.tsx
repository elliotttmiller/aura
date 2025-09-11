import React from 'react'
import './SceneOutliner.css'

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

interface SceneOutlinerProps {
  objects: SceneObject[]
  selectedObjectId: string | null
  onObjectSelect: (objectId: string | null) => void
  onObjectUpdate: (objectId: string, updates: Partial<SceneObject>) => void
}

export default function SceneOutliner({ 
  objects, 
  selectedObjectId, 
  onObjectSelect, 
  onObjectUpdate 
}: SceneOutlinerProps) {

  const handleVisibilityToggle = (objectId: string, currentVisibility: boolean) => {
    onObjectUpdate(objectId, { visible: !currentVisibility })
  }

  const handleObjectRename = (objectId: string, newName: string) => {
    onObjectUpdate(objectId, { name: newName })
  }

  return (
    <div className="sidebar">
      <div className="panel-title">Scene Outliner</div>
      
      {/* Scene hierarchy tree */}
      <div className="scene-tree">
        {objects.length === 0 ? (
          <div className="empty-scene">
            <p>No objects in scene</p>
            <span>Create objects using AI chat</span>
          </div>
        ) : (
          objects.map(object => (
            <div 
              key={object.id}
              className={`scene-object ${object.id === selectedObjectId ? 'selected' : ''}`}
              onClick={() => onObjectSelect(object.id)}
            >
              <div className="object-info">
                <span className="object-icon">
                  {object.type === 'mesh' ? '🔷' : '📦'}
                </span>
                <span className="object-name">{object.name}</span>
              </div>
              
              <div className="object-controls">
                <button
                  className={`visibility-btn ${object.visible ? 'visible' : 'hidden'}`}
                  onClick={(e) => {
                    e.stopPropagation()
                    handleVisibilityToggle(object.id, object.visible)
                  }}
                  title={object.visible ? 'Hide object' : 'Show object'}
                >
                  {object.visible ? '👁️' : '🙈'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Scene statistics */}
      <div className="scene-stats">
        <div className="panel-title">Scene Statistics</div>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Objects:</span>
            <span className="stat-value">{objects.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Visible:</span>
            <span className="stat-value">{objects.filter(obj => obj.visible).length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Selected:</span>
            <span className="stat-value">{selectedObjectId ? '1' : '0'}</span>
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="quick-actions">
        <div className="panel-title">Quick Actions</div>
        <button className="btn btn-secondary" onClick={() => onObjectSelect(null)}>
          Clear Selection
        </button>
        <button className="btn btn-secondary">
          Focus Selected
        </button>
        <button className="btn btn-secondary">
          Frame All
        </button>
      </div>
    </div>
  )
}