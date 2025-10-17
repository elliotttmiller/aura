import { memo, useCallback } from 'react'
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

const PropertiesInspector = memo(function PropertiesInspector({ selectedObject, onObjectUpdate }: PropertiesInspectorProps) {
  
  const handleTransformChange = useCallback((
    property: 'position' | 'rotation' | 'scale',
    axis: 0 | 1 | 2,
    value: number
  ) => {
    if (!selectedObject) return
    const newTransform = { ...selectedObject.transform }
    newTransform[property][axis] = value
    onObjectUpdate(selectedObject.id, { transform: newTransform })
  }, [selectedObject, onObjectUpdate])

  const handleMaterialChange = useCallback((property: 'color' | 'roughness' | 'metallic', value: string | number) => {
    if (!selectedObject) return
    const newMaterial = { ...selectedObject.material }
    if (property === 'color') {
      newMaterial.color = value as string
    } else {
      newMaterial[property] = value as number
    }
    onObjectUpdate(selectedObject.id, { material: newMaterial })
  }, [selectedObject, onObjectUpdate])

  const handleNameChange = useCallback((newName: string) => {
    if (!selectedObject) return
    onObjectUpdate(selectedObject.id, { name: newName })
  }, [selectedObject, onObjectUpdate])
  
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
            id="object-name-input"
            title="Object Name"
            placeholder="Enter object name"
            aria-label="Object Name"
          />
        </div>

        <div className="control-group">
          <label className="control-label">Type</label>
          <input
            type="text"
            className="control-input"
            value={selectedObject.type}
            disabled
            id="object-type-input"
            title="Object Type"
            aria-label="Object Type"
          />
        </div>

        <div className="control-group">
          <label className="control-label">ID</label>
          <input
            type="text"
            className="control-input"
            value={selectedObject.id}
            disabled
            id="object-id-input"
            title="Object ID"
            aria-label="Object ID"
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
              id="position-x"
              title="Position X"
              placeholder="X"
              aria-label="Position X"
            />
            <input
              type="number"
              step="0.1"
              value={selectedObject.transform.position[1]}
              onChange={(e) => handleTransformChange('position', 1, parseFloat(e.target.value))}
              className="vector-component"
              id="position-y"
              title="Position Y"
              placeholder="Y"
              aria-label="Position Y"
            />
            <input
              type="number"
              step="0.1"
              value={selectedObject.transform.position[2]}
              onChange={(e) => handleTransformChange('position', 2, parseFloat(e.target.value))}
              className="vector-component"
              id="position-z"
              title="Position Z"
              placeholder="Z"
              aria-label="Position Z"
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
              id="material-color-picker"
              title="Material Color"
              aria-label="Material Color"
            />
            <input
              type="text"
              value={selectedObject.material.color}
              onChange={(e) => handleMaterialChange('color', e.target.value)}
              className="color-text"
              id="material-color-text"
              title="Material Color Hex"
              placeholder="#FFD700"
              aria-label="Material Color Hex"
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
              id="material-roughness"
              title="Material Roughness"
              aria-label="Material Roughness"
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
              id="material-metallic"
              title="Material Metallic"
              aria-label="Material Metallic"
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
  <button className="btn btn-danger">Delete Object</button>
      </div>
    </div>
  )
})

export default PropertiesInspector