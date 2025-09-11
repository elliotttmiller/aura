import React from 'react'
import './ViewportControls.css'

export default function ViewportControls() {
  const handleExport = () => {
    console.log('Export functionality would connect to backend STL generation')
  }

  const handleSave = () => {
    console.log('Save project to workspace')
  }

  const handleUndo = () => {
    console.log('Undo last action')
  }

  const handleRedo = () => {
    console.log('Redo last action')
  }

  return (
    &lt;div className="viewport-controls-header"&gt;
      &lt;button className="control-btn" onClick={handleUndo} title="Undo"&gt;
        ↶
      &lt;/button&gt;
      &lt;button className="control-btn" onClick={handleRedo} title="Redo"&gt;
        ↷
      &lt;/button&gt;
      &lt;div className="control-divider" /&gt;
      &lt;button className="control-btn" onClick={handleSave} title="Save Project"&gt;
        💾
      &lt;/button&gt;
      &lt;button className="control-btn" onClick={handleExport} title="Export STL"&gt;
        📁
      &lt;/button&gt;
    &lt;/div&gt;
  )
}