import React from 'react'
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
  onObjectUpdate: (objectId: string, updates: Partial&lt;SceneObject&gt;) => void
}

export default function PropertiesInspector({ selectedObject, onObjectUpdate }: PropertiesInspectorProps) {
  
  if (!selectedObject) {
    return (
      &lt;div className="properties"&gt;
        &lt;div className="panel-title"&gt;Properties Inspector&lt;/div&gt;
        &lt;div className="no-selection"&gt;
          &lt;p&gt;No object selected&lt;/p&gt;
          &lt;span&gt;Select an object to view and edit its properties&lt;/span&gt;
        &lt;/div&gt;
      &lt;/div&gt;
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
    &lt;div className="properties"&gt;
      &lt;div className="panel-title"&gt;Properties Inspector&lt;/div&gt;
      
      {/* Object Info */}
      &lt;div className="property-section"&gt;
        &lt;div className="section-title"&gt;Object Information&lt;/div&gt;
        
        &lt;div className="control-group"&gt;
          &lt;label className="control-label"&gt;Name&lt;/label&gt;
          &lt;input
            type="text"
            className="control-input"
            value={selectedObject.name}
            onChange={(e) =&gt; handleNameChange(e.target.value)}
          /&gt;
        &lt;/div&gt;

        &lt;div className="control-group"&gt;
          &lt;label className="control-label"&gt;Type&lt;/label&gt;
          &lt;input
            type="text"
            className="control-input"
            value={selectedObject.type}
            disabled
          /&gt;
        &lt;/div&gt;

        &lt;div className="control-group"&gt;
          &lt;label className="control-label"&gt;ID&lt;/label&gt;
          &lt;input
            type="text"
            className="control-input"
            value={selectedObject.id}
            disabled
          /&gt;
        &lt;/div&gt;
      &lt;/div&gt;

      {/* Transform Properties */}
      &lt;div className="property-section"&gt;
        &lt;div className="section-title"&gt;Transform&lt;/div&gt;
        
        {/* Position */}
        &lt;div className="transform-group"&gt;
          &lt;div className="transform-label"&gt;Position&lt;/div&gt;
          &lt;div className="vector-input"&gt;
            &lt;input
              type="number"
              step="0.1"
              value={selectedObject.transform.position[0]}
              onChange={(e) =&gt; handleTransformChange('position', 0, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="X"
            /&gt;
            &lt;input
              type="number"
              step="0.1"
              value={selectedObject.transform.position[1]}
              onChange={(e) =&gt; handleTransformChange('position', 1, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="Y"
            /&gt;
            &lt;input
              type="number"
              step="0.1"
              value={selectedObject.transform.position[2]}
              onChange={(e) =&gt; handleTransformChange('position', 2, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="Z"
            /&gt;
          &lt;/div&gt;
        &lt;/div&gt;

        {/* Rotation */}
        &lt;div className="transform-group"&gt;
          &lt;div className="transform-label"&gt;Rotation&lt;/div&gt;
          &lt;div className="vector-input"&gt;
            &lt;input
              type="number"
              step="1"
              value={(selectedObject.transform.rotation[0] * 180 / Math.PI).toFixed(1)}
              onChange={(e) =&gt; handleTransformChange('rotation', 0, parseFloat(e.target.value) * Math.PI / 180)}
              className="vector-component"
              placeholder="X°"
            /&gt;
            &lt;input
              type="number"
              step="1"
              value={(selectedObject.transform.rotation[1] * 180 / Math.PI).toFixed(1)}
              onChange={(e) =&gt; handleTransformChange('rotation', 1, parseFloat(e.target.value) * Math.PI / 180)}
              className="vector-component"
              placeholder="Y°"
            /&gt;
            &lt;input
              type="number"
              step="1"
              value={(selectedObject.transform.rotation[2] * 180 / Math.PI).toFixed(1)}
              onChange={(e) =&gt; handleTransformChange('rotation', 2, parseFloat(e.target.value) * Math.PI / 180)}
              className="vector-component"
              placeholder="Z°"
            /&gt;
          &lt;/div&gt;
        &lt;/div&gt;

        {/* Scale */}
        &lt;div className="transform-group"&gt;
          &lt;div className="transform-label"&gt;Scale&lt;/div&gt;
          &lt;div className="vector-input"&gt;
            &lt;input
              type="number"
              step="0.1"
              min="0.1"
              value={selectedObject.transform.scale[0]}
              onChange={(e) =&gt; handleTransformChange('scale', 0, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="X"
            /&gt;
            &lt;input
              type="number"
              step="0.1"
              min="0.1"
              value={selectedObject.transform.scale[1]}
              onChange={(e) =&gt; handleTransformChange('scale', 1, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="Y"
            /&gt;
            &lt;input
              type="number"
              step="0.1"
              min="0.1"
              value={selectedObject.transform.scale[2]}
              onChange={(e) =&gt; handleTransformChange('scale', 2, parseFloat(e.target.value))}
              className="vector-component"
              placeholder="Z"
            /&gt;
          &lt;/div&gt;
        &lt;/div&gt;
      &lt;/div&gt;

      {/* Material Properties */}
      &lt;div className="property-section"&gt;
        &lt;div className="section-title"&gt;Material&lt;/div&gt;
        
        &lt;div className="control-group"&gt;
          &lt;label className="control-label"&gt;Color&lt;/label&gt;
          &lt;div className="color-input-group"&gt;
            &lt;input
              type="color"
              value={selectedObject.material.color}
              onChange={(e) =&gt; handleMaterialChange('color', e.target.value)}
              className="color-picker"
            /&gt;
            &lt;input
              type="text"
              value={selectedObject.material.color}
              onChange={(e) =&gt; handleMaterialChange('color', e.target.value)}
              className="color-text"
              placeholder="#FFD700"
            /&gt;
          &lt;/div&gt;
        &lt;/div&gt;

        &lt;div className="control-group"&gt;
          &lt;label className="control-label"&gt;Roughness&lt;/label&gt;
          &lt;div className="slider-group"&gt;
            &lt;input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={selectedObject.material.roughness}
              onChange={(e) =&gt; handleMaterialChange('roughness', parseFloat(e.target.value))}
              className="slider"
            /&gt;
            &lt;span className="slider-value"&gt;{selectedObject.material.roughness.toFixed(2)}&lt;/span&gt;
          &lt;/div&gt;
        &lt;/div&gt;

        &lt;div className="control-group"&gt;
          &lt;label className="control-label"&gt;Metallic&lt;/label&gt;
          &lt;div className="slider-group"&gt;
            &lt;input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={selectedObject.material.metallic}
              onChange={(e) =&gt; handleMaterialChange('metallic', parseFloat(e.target.value))}
              className="slider"
            /&gt;
            &lt;span className="slider-value"&gt;{selectedObject.material.metallic.toFixed(2)}&lt;/span&gt;
          &lt;/div&gt;
        &lt;/div&gt;
      &lt;/div&gt;

      {/* Actions */}
      &lt;div className="property-section"&gt;
        &lt;div className="section-title"&gt;Actions&lt;/div&gt;
        &lt;button className="btn btn-secondary"&gt;Reset Transform&lt;/button&gt;
        &lt;button className="btn btn-secondary"&gt;Duplicate Object&lt;/button&gt;
        &lt;button className="btn" style={{background: '#f56565'}}&gt;Delete Object&lt;/button&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  )
}