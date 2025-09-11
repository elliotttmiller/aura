import { useRef, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Grid } from '@react-three/drei'
import * as THREE from 'three'
import GLBModel from '../GLBModel/GLBModel'
import './Viewport.css'

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

interface ViewportProps {
  objects: SceneObject[]
  selectedObjectId: string | null
  onObjectSelect: (objectId: string | null) => void
  onLayerSelect: (layerId: string | null) => void
  onGLBLayersDetected: (modelId: string, layers: Array<{id: string, name: string, mesh: any}>) => void
  isGenerating: boolean
}

// 3D Object Component
function SceneObjectMesh({ object, isSelected, onSelect }: { 
  object: SceneObject
  isSelected: boolean
  onSelect: () => void 
}) {
  const meshRef = useRef<THREE.Mesh>(null)
  
  return (
    <mesh
      ref={meshRef}
      position={object.transform.position}
      rotation={object.transform.rotation}
      scale={object.transform.scale}
      visible={object.visible}
      onClick={onSelect}
    >
      {/* For now, render as a torus (ring-like shape) */}
      <torusGeometry args={[2, 0.5, 16, 100]} />
      <meshStandardMaterial
        color={object.material.color}
        roughness={object.material.roughness}
        metalness={object.material.metallic}
        emissive={isSelected ? '#4299e1' : '#000000'}
        emissiveIntensity={isSelected ? 0.2 : 0}
      />
    </mesh>
  )
}

// Loading/Generation Overlay
function GeneratingOverlay({ isVisible }: { isVisible: boolean }) {
  if (!isVisible) return null
  
  return (
    <div className="generating-overlay">
      <div className="spinner"></div>
      <h3>AI is creating your design...</h3>
      <p>This may take a few moments</p>
    </div>
  )
}

export default function Viewport({ 
  objects, 
  selectedObjectId, 
  onObjectSelect, 
  onLayerSelect, 
  onGLBLayersDetected,
  isGenerating 
}: ViewportProps) {
  const [cameraPosition, setCameraPosition] = useState<[number, number, number]>([5, 5, 5])

  const handleCanvasClick = (event: any) => {
    // If clicking on canvas background (not an object), deselect
    if (event.target.classList.contains('webgl-canvas')) {
      onObjectSelect(null)
      onLayerSelect(null)
    }
  }

  const handleGLBLayersDetected = (layers: Array<{id: string, name: string, mesh: any}>) => {
    // Find the GLB model object to get its ID
    const glbModel = objects.find(obj => obj.type === 'glb_model')
    if (glbModel) {
      onGLBLayersDetected(glbModel.id, layers)
    }
  }

  // Get GLB models and regular objects
  const glbModels = objects.filter(obj => obj.type === 'glb_model')
  const regularObjects = objects.filter(obj => obj.type !== 'glb_model' && !obj.isLayer)
  const selectedLayer = objects.find(obj => obj.id === selectedObjectId && obj.isLayer)

  return (
    <div className="viewport">
      <Canvas
        className="webgl-canvas"
        camera={{ position: cameraPosition, fov: 45 }}
        onClick={handleCanvasClick}
        shadows
      >
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight 
          position={[10, 10, 5]} 
          intensity={1} 
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />

        {/* Environment - Using simple background color instead of HDR */}
        <color attach="background" args={['#1a202c']} />
        
        {/* Grid */}
        <Grid 
          args={[10, 10]} 
          cellColor="#4a5568" 
          sectionColor="#2d3748" 
          position={[0, -2, 0]} 
        />

        {/* Render GLB Models */}
        {glbModels.map(model => (
          <GLBModel
            key={model.id}
            url="/3d_models/diamond_ring_example.glb"
            selectedLayerId={selectedLayer?.id || null}
            onLayerSelect={onLayerSelect}
            onLayersDetected={handleGLBLayersDetected}
          />
        ))}

        {/* Render regular scene objects (basic shapes) */}
        {regularObjects.map(object => (
          <SceneObjectMesh
            key={object.id}
            object={object}
            isSelected={object.id === selectedObjectId}
            onSelect={() => onObjectSelect(object.id)}
          />
        ))}

        {/* Camera Controls */}
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          target={[0, 0, 0]}
        />
      </Canvas>

      {/* Show empty state when no objects */}
      {objects.length === 0 && !isGenerating && (
        <div className="viewport-empty">
          <div className="empty-icon">💎</div>
          <h3>AI Design Studio Ready</h3>
          <p>Start by describing your jewelry vision in the AI chat</p>
          <p className="hint">Real-time rendering and AI collaboration active</p>
        </div>
      )}

      {/* Generation overlay */}
      <GeneratingOverlay isVisible={isGenerating} />
      
      {/* Viewport controls overlay */}
      <div className="viewport-controls">
        <button className="viewport-btn" onClick={() => setCameraPosition([5, 5, 5])}>
          Reset View
        </button>
        <button className="viewport-btn">Wireframe</button>
        <button className="viewport-btn">Materials</button>
      </div>
    </div>
  )
}