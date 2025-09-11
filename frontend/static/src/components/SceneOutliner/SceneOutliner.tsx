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
  // New properties for GLB layers
  isLayer?: boolean
  parentModelId?: string
  meshData?: any // THREE.Mesh reference for GLB layers
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

  // Organize objects into models and their layers
  const glbModels = objects.filter(obj => obj.type === 'glb_model')
  const layersGroupedByModel: { [modelId: string]: typeof objects } = {}
  const regularObjects = objects.filter(obj => obj.type !== 'glb_model' && !obj.isLayer)

  // Group layers by their parent model
  objects.forEach(obj => {
    if (obj.isLayer && obj.parentModelId) {
      if (!layersGroupedByModel[obj.parentModelId]) {
        layersGroupedByModel[obj.parentModelId] = []
      }
      layersGroupedByModel[obj.parentModelId].push(obj)
    }
  })

  return (
    <div className="sidebar">
      <div className="panel-title">Scene Outliner</div>
      
      {/* Scene hierarchy tree */}
      <div className="scene-tree">
        {objects.length === 0 ? (
          <div className="empty-scene">
            <p>No objects in scene</p>
            <span>Load 3D models or create objects using AI chat</span>
          </div>
        ) : (
          <>
            {/* GLB Models with their layers */}
            {glbModels.map(model => (
              <div key={model.id} className="model-group">
                <div 
                  className={`scene-object model-header ${model.id === selectedObjectId ? 'selected' : ''}`}
                  onClick={() => onObjectSelect(model.id)}
                >
                  <div className="object-info">
                    <span className="object-icon">📁</span>
                    <span className="object-name">{model.name}</span>
                    <span className="object-type">({layersGroupedByModel[model.id]?.length || 0} layers)</span>
                  </div>
                  
                  <div className="object-controls">
                    <button
                      className={`visibility-btn ${model.visible ? 'visible' : 'hidden'}`}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleVisibilityToggle(model.id, model.visible)
                      }}
                      title={model.visible ? 'Hide model' : 'Show model'}
                    >
                      {model.visible ? '👁️' : '🙈'}
                    </button>
                  </div>
                </div>
                
                {/* Model layers */}
                {layersGroupedByModel[model.id] && (
                  <div className="layer-group">
                    {layersGroupedByModel[model.id].map(layer => (
                      <div 
                        key={layer.id}
                        className={`scene-object layer ${layer.id === selectedObjectId ? 'selected' : ''}`}
                        onClick={() => onObjectSelect(layer.id)}
                      >
                        <div className="object-info">
                          <span className="object-icon">🔷</span>
                          <span className="object-name">{layer.name}</span>
                          <span className="layer-indicator">layer</span>
                        </div>
                        
                        <div className="object-controls">
                          <button
                            className={`visibility-btn ${layer.visible ? 'visible' : 'hidden'}`}
                            onClick={(e) => {
                              e.stopPropagation()
                              handleVisibilityToggle(layer.id, layer.visible)
                            }}
                            title={layer.visible ? 'Hide layer' : 'Show layer'}
                          >
                            {layer.visible ? '👁️' : '🙈'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Regular objects */}
            {regularObjects.map(object => (
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
            ))}
          </>
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