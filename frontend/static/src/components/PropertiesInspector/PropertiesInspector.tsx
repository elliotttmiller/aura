import './PropertiesInspector.css'

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

interface PropertiesInspectorProps {
  selectedObject: SceneObject | undefined
  onObjectUpdate: (objectId: string, updates: Partial<SceneObject>) => void
}

export default function PropertiesInspector({ selectedObject, onObjectUpdate }: PropertiesInspectorProps) {
  
  if (!selectedObject) {
    return (
      <div className="properties">
        <div className="panel-title">Properties Inspector</div>
        <div className="no-selection">
          <p>No object selected</p>
          <span>Select an object to view and edit its properties</span>
        </div>
      </div>
    )
  }

  const handleTransformChange = (
    property: 'position' | 'rotation' | 'scale',
    axis: 0 | 1 | 2,
    value: number
  ) => {
    const newTransform = { ...selectedObject.transform }
    newTransform[property][axis] = value
    onObjectUpdate(selectedObject.id, { transform: newTransform })
  }

  const handleMaterialChange = (property: 'color' | 'roughness' | 'metallic', value: string | number) => {
    const newMaterial = { ...selectedObject.material }
    if (property === 'color') {
      newMaterial.color = value as string
    } else {
      newMaterial[property] = value as number
    }
    onObjectUpdate(selectedObject.id, { material: newMaterial })
  }

  const handleNameChange = (newName: string) => {
    onObjectUpdate(selectedObject.id, { name: newName })
  }

  return (
    <div className="properties">
      <div className="panel-title">Properties Inspector</div>
      
      {/* Object Info */}
      <div className="property-section">
        <div className="section-title">Object Information</div>
        
        <div className="control-group">
          <label className="control-label">Name</label>
          <input
            type="text"
            className="control-input"
            value={selectedObject.name}
            onChange={(e) => handleNameChange(e.target.value)}
          />
        </div>

        <div className="control-group">
          <label className="control-label">Type</label>
          <input
            type="text"
            className="control-input"
            value={selectedObject.type}
            disabled
          />
        </div>

        <div className="control-group">
          <label className="control-label">ID</label>
          <input
            type="text"
            className="control-input"
            value={selectedObject.id}
            disabled
          />
        </div>
      </div>

      {/* Transform Properties */}
      <div className="property-section">
        <div className="section-title">Transform</div>
        
        {/* Position */}
        <div className="transform-group">
          <div className="transform-label">Position</div>
          <div className="vector-input">
            <input
              type="number"
              step="0.1"
              value={selectedObject.transform.position[0]}
              onChange={(e) => handleTransformChange('position', 0, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="X"
            />
            <input
              type="number"
              step="0.1"
              value={selectedObject.transform.position[1]}
              onChange={(e) => handleTransformChange('position', 1, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="Y"
            />
            <input
              type="number"
              step="0.1"
              value={selectedObject.transform.position[2]}
              onChange={(e) => handleTransformChange('position', 2, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="Z"
            />
          </div>
        </div>

        {/* Rotation */}
        <div className="transform-group">
          <div className="transform-label">Rotation</div>
          <div className="vector-input">
            <input
              type="number"
              step="1"
              value={(selectedObject.transform.rotation[0] * 180 / Math.PI).toFixed(1)}
              onChange={(e) => handleTransformChange('rotation', 0, parseFloat(e.target.value) * Math.PI / 180)}
              className="vector-component"
              placeholder="X°"
            />
            <input
              type="number"
              step="1"
              value={(selectedObject.transform.rotation[1] * 180 / Math.PI).toFixed(1)}
              onChange={(e) => handleTransformChange('rotation', 1, parseFloat(e.target.value) * Math.PI / 180)}
              className="vector-component"
              placeholder="Y°"
            />
            <input
              type="number"
              step="1"
              value={(selectedObject.transform.rotation[2] * 180 / Math.PI).toFixed(1)}
              onChange={(e) => handleTransformChange('rotation', 2, parseFloat(e.target.value) * Math.PI / 180)}
              className="vector-component"
              placeholder="Z°"
            />
          </div>
        </div>

        {/* Scale */}
        <div className="transform-group">
          <div className="transform-label">Scale</div>
          <div className="vector-input">
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={selectedObject.transform.scale[0]}
              onChange={(e) => handleTransformChange('scale', 0, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="X"
            />
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={selectedObject.transform.scale[1]}
              onChange={(e) => handleTransformChange('scale', 1, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="Y"
            />
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={selectedObject.transform.scale[2]}
              onChange={(e) => handleTransformChange('scale', 2, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="Z"
            />
          </div>
        </div>
      </div>

      {/* Material Properties */}
      <div className="property-section">
        <div className="section-title">Material</div>
        
        <div className="control-group">
          <label className="control-label">Color</label>
          <div className="color-input-group">
            <input
              type="color"
              value={selectedObject.material.color}
              onChange={(e) => handleMaterialChange('color', e.target.value)}
              className="color-picker"
            />
            <input
              type="text"
              value={selectedObject.material.color}
              onChange={(e) => handleMaterialChange('color', e.target.value)}
              className="color-text"
              placeholder="#FFD700"
            />
          </div>
        </div>

        <div className="control-group">
          <label className="control-label">Roughness</label>
          <div className="slider-group">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={selectedObject.material.roughness}
              onChange={(e) => handleMaterialChange('roughness', parseFloat(e.target.value))}
              className="slider"
            />
            <span className="slider-value">{selectedObject.material.roughness.toFixed(2)}</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label">Metallic</label>
          <div className="slider-group">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={selectedObject.material.metallic}
              onChange={(e) => handleMaterialChange('metallic', parseFloat(e.target.value))}
              className="slider"
            />
            <span className="slider-value">{selectedObject.material.metallic.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="property-section">
        <div className="section-title">Actions</div>
        <button className="btn btn-secondary">Reset Transform</button>
        <button className="btn btn-secondary">Duplicate Object</button>
        <button className="btn" style={{background: '#f56565'}}>Delete Object</button>
      </div>
    </div>
  )
}