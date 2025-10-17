import { useRef, useState, Suspense, memo, useCallback } from 'react'
import { invalidate } from '@react-three/fiber'
import React from 'react'
import { Canvas } from '@react-three/fiber'
import { 
  OrbitControls, 
  Grid, 
  Environment,
  ContactShadows,
  PerspectiveCamera,
  useProgress,
  Html,
  Sky,
  Stars,
  Sparkles,
  Center,
  BakeShadows
} from '@react-three/drei'
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
  meshData?: import('three').Mesh // THREE.Mesh reference for GLB layers
}

interface ViewportProps {
  objects: SceneObject[]
  selectedObjectId: string | null
  onObjectSelect: (objectId: string | null) => void
  onLayerSelect: (layerId: string | null) => void
  onGLBLayersDetected: (modelId: string, layers: Array<{id: string, name: string, mesh: import('three').Mesh}>) => void
  isGenerating: boolean
}

// 3D Object Component with enhanced materials - optimized with memo
const SceneObjectMesh = memo(function SceneObjectMesh({ object, isSelected, onSelect }: { 
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
      castShadow
      receiveShadow
    >
      {/* For now, render as a torus (ring-like shape) */}
      <torusGeometry args={[2, 0.5, 32, 100]} />
      <meshStandardMaterial
        color={object.material.color}
        roughness={object.material.roughness}
        metalness={object.material.metallic}
        emissive={isSelected ? '#667eea' : '#000000'}
        emissiveIntensity={isSelected ? 0.3 : 0}
        envMapIntensity={1.5}
      />
      {/* Selection outline effect */}
      {isSelected && (
        <mesh scale={1.05}>
          <torusGeometry args={[2, 0.5, 32, 100]} />
          <meshBasicMaterial 
            color="#667eea" 
            wireframe 
            transparent 
            opacity={0.3}
          />
        </mesh>
      )}
    </mesh>
  )
})

// Advanced Lighting Setup - optimized with memo
const SceneLighting = memo(function SceneLighting() {
  return (
    <>
      {/* Ambient light for base illumination */}
      <ambientLight intensity={0.3} />
      
      {/* Key light - main directional light */}
      <directionalLight 
        position={[10, 10, 5]} 
        intensity={1.2} 
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={50}
        shadow-camera-left={-10}
        shadow-camera-right={10}
        shadow-camera-top={10}
        shadow-camera-bottom={-10}
        shadow-bias={-0.0001}
      />
      
      {/* Fill light - softer from opposite side */}
      <directionalLight 
        position={[-5, 5, -5]} 
        intensity={0.4}
      />
      
      {/* Rim light - for edge highlighting */}
      <pointLight position={[0, 10, -10]} intensity={0.5} color="#667eea" />
      
      {/* Accent lights for jewelry sparkle */}
      <pointLight position={[5, 0, 5]} intensity={0.3} color="#ffd700" />
      <pointLight position={[-5, 0, -5]} intensity={0.3} color="#fff" />
    </>
  )
})

// Progressive loader for 3D assets
function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div className="loader-container">
        <div className="loader-ring"></div>
        <div className="loader-text">{progress.toFixed(0)}%</div>
        <p className="loader-subtitle">Loading 3D Assets...</p>
      </div>
    </Html>
  )
}

// Loading/Generation Overlay with enhanced design
function GeneratingOverlay({ isVisible }: { isVisible: boolean }) {
  if (!isVisible) return null
  
  return (
    <div className="generating-overlay">
      <div className="spinner-container">
        <div className="spinner-ring"></div>
        <div className="spinner-ring-2"></div>
        <div className="spinner-core"></div>
      </div>
      <h3>AI Design Generation</h3>
      <p>Creating your masterpiece...</p>
      <div className="progress-bar">
        <div className="progress-fill"></div>
      </div>
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
  const [showWireframe, setShowWireframe] = useState(false)
  const [showGrid, setShowGrid] = useState(true)
  const [renderMode, setRenderMode] = useState<'realistic' | 'studio' | 'night'>('realistic')

  const handleCanvasClick = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    // If clicking on canvas background (not an object), deselect
    const target = event.target as HTMLElement;
    if (target.classList && target.classList.contains('webgl-canvas')) {
      onObjectSelect(null)
      onLayerSelect(null)
    }
  }, [onObjectSelect, onLayerSelect])

  const handleGLBLayersDetected = useCallback((layers: Array<{id: string, name: string, mesh: import('three').Mesh}>) => {
    // Find the GLB model object to get its ID
    const glbModel = objects.find(obj => obj.type === 'glb_model')
    if (glbModel) {
      onGLBLayersDetected(glbModel.id, layers)
    }
  }, [objects, onGLBLayersDetected])

  const handleResetCamera = useCallback(() => {
    setCameraPosition([5, 5, 5])
    invalidate()
  }, [])

  const handleToggleWireframe = useCallback(() => {
    setShowWireframe(prev => {
      const next = !prev
      invalidate()
      return next
    })
  }, [])

  const handleToggleGrid = useCallback(() => {
    setShowGrid(prev => {
      const next = !prev
      invalidate()
      return next
    })
  }, [])

  const handleSetRenderMode = useCallback((mode: 'realistic' | 'studio' | 'night') => {
    setRenderMode(mode)
    invalidate()
  }, [])

  // Get GLB models and regular objects
  const glbModels = objects.filter(obj => obj.type === 'glb_model')
  const regularObjects = objects.filter(obj => obj.type !== 'glb_model' && !obj.isLayer)
  const selectedLayer = objects.find(obj => obj.id === selectedObjectId && obj.isLayer)

  return (
    <div className="viewport">
      <Canvas
        className="webgl-canvas"
        onClick={handleCanvasClick}
        shadows
        gl={{ 
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
          preserveDrawingBuffer: true,
          stencil: false,
          depth: true
        }}
        dpr={[1, 2]} // Adaptive pixel ratio for performance
        frameloop="demand" // Only render on demand for optimal performance
        performance={{ min: 0.5 }} // Adaptive performance scaling
      >
        {/* Camera with smooth controls */}
        <PerspectiveCamera makeDefault position={cameraPosition} fov={45} />
        
        <Suspense fallback={<Loader />}>
          {/* Advanced Lighting */}
          <SceneLighting />

          {/* HDR Environment for realistic reflections */}
          {renderMode === 'realistic' && (
            <Environment preset="studio" background={false} />
          )}
          
          {/* Studio environment for jewelry */}
          {renderMode === 'studio' && (
            <Environment preset="city" background={false} />
          )}
          
          {/* Night/Dark environment */}
          {renderMode === 'night' && (
            <>
              <Sky sunPosition={[0, -1, 0]} />
              <Stars radius={100} depth={50} count={5000} factor={4} fade speed={1} />
            </>
          )}

          {/* Premium Background */}
          <color attach="background" args={['#0f0f1e']} />
          
          {/* Grid with conditional rendering */}
          {showGrid && (
            <Grid 
              args={[20, 20]} 
              cellColor="#667eea" 
              sectionColor="#764ba2" 
              position={[0, -2, 0]}
              fadeDistance={30}
              fadeStrength={1}
              cellSize={0.5}
              sectionSize={2}
              infiniteGrid
            />
          )}

          {/* Contact shadows for realism */}
          <ContactShadows 
            position={[0, -1.99, 0]} 
            opacity={0.4} 
            scale={10} 
            blur={2} 
            far={4}
            resolution={256}
            color="#000000"
          />

          {/* Sparkles effect for jewelry */}
          {glbModels.length > 0 && (
            <Sparkles 
              count={100}
              scale={5}
              size={2}
              speed={0.3}
              opacity={0.5}
              color="#ffd700"
            />
          )}

          {/* Render GLB Models with centering */}
          {glbModels.map(model => (
            <Center key={model.id}>
              <GLBModel
                url="/3d_models/diamond_ring_example.glb"
                parentModelId={model.id}
                selectedLayerId={selectedLayer?.id || null}
                onLayerSelect={onLayerSelect}
                onLayersDetected={handleGLBLayersDetected}
              />
            </Center>
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

          {/* Advanced Camera Controls with damping */}
          <OrbitControls 
            makeDefault
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            enableDamping={true}
            dampingFactor={0.05}
            rotateSpeed={0.5}
            zoomSpeed={0.8}
            panSpeed={0.5}
            minDistance={2}
            maxDistance={20}
            maxPolarAngle={Math.PI / 2}
            target={[0, 0, 0]}
          />
          
          {/* Bake shadows for better performance */}
          <BakeShadows />
        </Suspense>
      </Canvas>

      {/* Show empty state when no objects */}
      {objects.length === 0 && !isGenerating && (
        <div className="viewport-empty">
          <div className="empty-icon">💎</div>
          <h3>AI Design Studio Ready</h3>
          <p>Start by describing your jewelry vision in the AI chat</p>
          <p className="hint">Real-time rendering with physically-based materials</p>
        </div>
      )}

      {/* Generation overlay */}
      <GeneratingOverlay isVisible={isGenerating} />
      
      {/* Enhanced Viewport controls overlay */}
      <div className="viewport-controls">
        <div className="controls-group">
          <button 
            className="viewport-btn"
            onClick={handleResetCamera}
            title="Reset Camera View"
          >
            🎯 Reset
          </button>
          <button 
            className={`viewport-btn ${showWireframe ? 'active' : ''}`}
            onClick={handleToggleWireframe}
            title="Toggle Wireframe"
          >
            📐 Wire
          </button>
          <button 
            className={`viewport-btn ${showGrid ? 'active' : ''}`}
            onClick={handleToggleGrid}
            title="Toggle Grid"
          >
            ⊞ Grid
          </button>
        </div>
        <div className="controls-group">
          <button 
            className={`viewport-btn ${renderMode === 'realistic' ? 'active' : ''}`}
            onClick={() => handleSetRenderMode('realistic')}
            title="Realistic Rendering"
          >
            ✨ Real
          </button>
          <button 
            className={`viewport-btn ${renderMode === 'studio' ? 'active' : ''}`}
            onClick={() => handleSetRenderMode('studio')}
            title="Studio Lighting"
          >
            💡 Studio
          </button>
          <button 
            className={`viewport-btn ${renderMode === 'night' ? 'active' : ''}`}
            onClick={() => handleSetRenderMode('night')}
            title="Night Mode"
          >
            🌙 Night
          </button>
        </div>
      </div>

      {/* Performance indicator */}
      <div className="performance-indicator">
        <div className="fps-badge">
          <span className="fps-label">Render:</span>
          <span className="fps-value">60 FPS</span>
        </div>
      </div>
    </div>
  )
}