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
    <div className="viewport-controls-header">
      <button className="control-btn" onClick={handleUndo} title="Undo">
        ↶
      </button>
      <button className="control-btn" onClick={handleRedo} title="Redo">
        ↷
      </button>
      <div className="control-divider" />
      <button className="control-btn" onClick={handleSave} title="Save Project">
        💾
      </button>
      <button className="control-btn" onClick={handleExport} title="Export STL">
        📁
      </button>
    </div>
  )
}