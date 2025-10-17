import './ViewportControls.css'
import { useActions } from '../../store/designStore'

export default function ViewportControls() {
  const actions = useActions()
  const handleExport = () => {
    actions.exportSceneJSON()
  }

  const handleSave = () => {
    actions.saveProject()
  }

  const handleUndo = () => {
    actions.undo()
  }

  const handleRedo = () => {
    actions.redo()
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