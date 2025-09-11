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
  onObjectUpdate: (objectId: string, updates: Partial&lt;SceneObject&gt;) => void
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
    &lt;div className="sidebar"&gt;
      &lt;div className="panel-title"&gt;Scene Outliner&lt;/div&gt;
      
      {/* Scene hierarchy tree */}
      &lt;div className="scene-tree"&gt;
        {objects.length === 0 ? (
          &lt;div className="empty-scene"&gt;
            &lt;p&gt;No objects in scene&lt;/p&gt;
            &lt;span&gt;Create objects using AI chat&lt;/span&gt;
          &lt;/div&gt;
        ) : (
          objects.map(object =&gt; (
            &lt;div 
              key={object.id}
              className={`scene-object ${object.id === selectedObjectId ? 'selected' : ''}`}
              onClick={() =&gt; onObjectSelect(object.id)}
            &gt;
              &lt;div className="object-info"&gt;
                &lt;span className="object-icon"&gt;
                  {object.type === 'mesh' ? '🔷' : '📦'}
                &lt;/span&gt;
                &lt;span className="object-name"&gt;{object.name}&lt;/span&gt;
              &lt;/div&gt;
              
              &lt;div className="object-controls"&gt;
                &lt;button
                  className={`visibility-btn ${object.visible ? 'visible' : 'hidden'}`}
                  onClick={(e) =&gt; {
                    e.stopPropagation()
                    handleVisibilityToggle(object.id, object.visible)
                  }}
                  title={object.visible ? 'Hide object' : 'Show object'}
                &gt;
                  {object.visible ? '👁️' : '🙈'}
                &lt;/button&gt;
              &lt;/div&gt;
            &lt;/div&gt;
          ))
        )}
      &lt;/div&gt;

      {/* Scene statistics */}
      &lt;div className="scene-stats"&gt;
        &lt;div className="panel-title"&gt;Scene Statistics&lt;/div&gt;
        &lt;div className="stats-grid"&gt;
          &lt;div className="stat-item"&gt;
            &lt;span className="stat-label"&gt;Objects:&lt;/span&gt;
            &lt;span className="stat-value"&gt;{objects.length}&lt;/span&gt;
          &lt;/div&gt;
          &lt;div className="stat-item"&gt;
            &lt;span className="stat-label"&gt;Visible:&lt;/span&gt;
            &lt;span className="stat-value"&gt;{objects.filter(obj =&gt; obj.visible).length}&lt;/span&gt;
          &lt;/div&gt;
          &lt;div className="stat-item"&gt;
            &lt;span className="stat-label"&gt;Selected:&lt;/span&gt;
            &lt;span className="stat-value"&gt;{selectedObjectId ? '1' : '0'}&lt;/span&gt;
          &lt;/div&gt;
        &lt;/div&gt;
      &lt;/div&gt;

      {/* Quick actions */}
      &lt;div className="quick-actions"&gt;
        &lt;div className="panel-title"&gt;Quick Actions&lt;/div&gt;
        &lt;button className="btn btn-secondary" onClick={() =&gt; onObjectSelect(null)}&gt;
          Clear Selection
        &lt;/button&gt;
        &lt;button className="btn btn-secondary"&gt;
          Focus Selected
        &lt;/button&gt;
        &lt;button className="btn btn-secondary"&gt;
          Frame All
        &lt;/button&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  )
}