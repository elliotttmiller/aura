import { useRef, useState, Suspense, memo, useCallback } from 'react'
import { invalidate } from '@react-three/fiber'
import React from 'react'
import { Canvas } from '@react-three/fiber'
import {
  OrbitControls,
  Grid,
  Environment,
  PerspectiveCamera,
  useProgress,
  Html,
  Sky,
  Stars,
  BakeShadows
} from '@react-three/drei'
import * as THREE from 'three'
import GLBModel from '../GLBModel/GLBModel'
import MinimalWebGLTest from './MinimalWebGLTest'
import './Viewport.css'

interface SceneObject {
  id: string
  name: string
  type: string
  url?: string // Path to GLB file for model objects
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
  isLayer?: boolean
  parentModelId?: string
  meshData?: THREE.Mesh
}

interface ViewportProps {
  objects: SceneObject[]
  selectedObjectId: string | null
  onObjectSelect: (objectId: string | null) => void
  onLayerSelect: (layerId: string | null) => void
  onGLBLayersDetected: (modelId: string, layers: Array<{ id: string, name: string, mesh: THREE.Mesh }>) => void
  isGenerating: boolean
}

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
      <torusGeometry args={[2, 0.5, 32, 100]} />
      <meshStandardMaterial
        color={object.material.color}
        roughness={object.material.roughness}
        metalness={object.material.metallic}
        emissive={isSelected ? '#667eea' : '#000000'}
        emissiveIntensity={isSelected ? 0.3 : 0}
        envMapIntensity={1.5}
      />
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

const SceneLighting = memo(function SceneLighting() {
  return (
    <>
      <ambientLight intensity={0.3} />
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
      <directionalLight
        position={[-5, 5, -5]}
        intensity={0.4}
      />
      <pointLight position={[0, 10, -10]} intensity={0.5} color="#667eea" />
      <pointLight position={[5, 0, 5]} intensity={0.3} color="#ffd700" />
      <pointLight position={[-5, 0, -5]} intensity={0.3} color="#fff" />
    </>
  )
})

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
    const target = event.target as HTMLElement;
    if (target.classList && target.classList.contains('webgl-canvas')) {
      onObjectSelect(null)
      onLayerSelect(null)
    }
  }, [onObjectSelect, onLayerSelect])

  const handleGLBLayersDetected = useCallback((layers: Array<{ id: string, name: string, mesh: THREE.Mesh }>) => {
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

  // Render all GLB models and regular objects
  const glbModels = objects.filter(obj => obj.type === 'glb_model')
  const regularObjects = objects.filter(obj => obj.type !== 'glb_model' && !obj.isLayer)

  return (
    <div className="viewport">
      <Canvas
        className="webgl-canvas"
        onClick={handleCanvasClick}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener('webglcontextlost', (e) => {
            e.preventDefault();
            // eslint-disable-next-line no-console
            console.error('WebGL context lost!');
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            overlay.style.background = 'rgba(0,0,0,0.85)';
            overlay.style.color = '#fff';
            overlay.style.zIndex = '9999';
            overlay.style.display = 'flex';
            overlay.style.flexDirection = 'column';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.innerHTML = '<h2>WebGL context lost!</h2><p>Please close other GPU-intensive tabs or apps and reload this page.</p>';
            document.body.appendChild(overlay);
          });
        }}
        shadows
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
          preserveDrawingBuffer: true,
          stencil: false,
          depth: true
        }}
        dpr={1}
        frameloop="demand"
        performance={{ min: 0.5 }}
      >
      {/* Debug overlay for objects and glbModels length */}
  <div className="viewport-debug-overlay">
        objects: {objects.length} | glbModels: {glbModels.length}
      </div>
        <PerspectiveCamera makeDefault position={cameraPosition} fov={45} />
        <Suspense fallback={<Loader />}>
          <SceneLighting />
          <color attach="background" args={['#0f0f1e']} />
          {renderMode === 'realistic' && (
            <Environment preset="studio" background={false} />
          )}
          {renderMode === 'studio' && (
            <Environment preset="city" background={false} />
          )}
          {renderMode === 'night' && (
            <>
              <Sky sunPosition={[0, -1, 0]} />
              <Stars radius={100} depth={50} count={5000} factor={4} fade speed={1} />
            </>
          )}
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
            visible={showGrid}
          />
          {/* Render GLB models */}
          {glbModels.map(obj => (
            <GLBModel
              key={obj.id}
              url={obj.url || '/3d_models/diamond_ring_example.glb'}
              parentModelId={obj.id}
              selectedLayerId={selectedObjectId}
              onLayerSelect={onLayerSelect}
              onLayersDetected={handleGLBLayersDetected}
            />
          ))}
          {/* Render regular scene objects */}
          {regularObjects.map(obj => (
            <SceneObjectMesh
              key={obj.id}
              object={obj}
              isSelected={selectedObjectId === obj.id}
              onSelect={() => onObjectSelect(obj.id)}
            />
          ))}
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
          <BakeShadows />
        </Suspense>
      </Canvas>
      {objects.length === 0 && !isGenerating && (
        <MinimalWebGLTest />
      )}
      <GeneratingOverlay isVisible={isGenerating} />
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
      <div className="performance-indicator">
        <div className="fps-badge">
          <span className="fps-label">Render:</span>
          <span className="fps-value">60 FPS</span>
        </div>
      </div>
    </div>
  )
}