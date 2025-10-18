import { useRef, useState, Suspense, memo, useCallback } from 'react'
import { Canvas, invalidate } from '@react-three/fiber'
import {
  OrbitControls,
  Grid,
  PerspectiveCamera,
  useProgress,
  Html,
  Environment
} from '@react-three/drei'
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib'
import * as THREE from 'three'
import GLBModel from '../GLBModel/GLBModel'
import './Viewport.css'
import { useActions } from '../../store/designStore'
import { featureFlags } from '../../config/featureFlags'

interface SceneObject {
  id: string
  name: string
  type: string
  url?: string
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
  source?: 'ai' | 'uploaded'
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
      onClick={onSelect}
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={isSelected ? '#ffcc00' : object.material.color} wireframe={false} />
    </mesh>
  )
})

function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div className="loading-overlay">
        <div className="spinner"></div>
        <div className="loading-text">Loading {progress.toFixed(0)}%</div>
      </div>
    </Html>
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
  const actions = useActions()
  const [cameraPosition, _setCameraPosition] = useState<[number, number, number]>([1.2, 1.2, 1.2])
  const [showWireframe, setShowWireframe] = useState(false)
  const [showGrid, setShowGrid] = useState(true)
  const [renderMode, setRenderMode] = useState<'realistic' | 'studio' | 'night'>('realistic')
  const forcedSafe = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('safe') === '1'
  const [rendererMode, setRendererMode] = useState<'normal' | 'safe'>(forcedSafe ? 'safe' : 'normal')
  const isEffectiveSafe = forcedSafe || rendererMode === 'safe'
  const [canvasKey, setCanvasKey] = useState(0)
  const [glDiag, setGlDiag] = useState<{
    webglVersion?: string,
    vendor?: string,
    renderer?: string,
    maxTextureSize?: number,
    maxCubeMapSize?: number,
    antialias?: boolean
  }>({})

  // Refs to camera and controls for programmatic framing
  const controlsRef = useRef<OrbitControlsImpl | null>(null)
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)

  // Compute a camera position and target so that the object fits the view
  const frameObjectToView = useCallback((object: THREE.Object3D | null) => {
    if (!object || !cameraRef.current) return
    const camera = cameraRef.current
    const box = new THREE.Box3().setFromObject(object)
    if (!box.isEmpty()) {
      const size = box.getSize(new THREE.Vector3())
      const center = box.getCenter(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z)
      const padding = 1.2 // add some breathing room
      const fov = (camera.fov * Math.PI) / 180
  const cameraZ = Math.abs((maxDim * padding) / (2 * Math.tan(fov / 2)))
      // Keep camera above ground slightly and off-axis for depth
      const offset = Math.max(maxDim * 0.5, 0.5)
      const newPos = new THREE.Vector3(center.x + offset, center.y + offset, center.z + cameraZ)
      camera.position.copy(newPos)
      camera.near = Math.max(0.001, cameraZ / 1000)
      camera.far = Math.max(50, cameraZ * 10)
      camera.updateProjectionMatrix()
      // Update orbit controls target if available
      if (controlsRef.current) {
        controlsRef.current.target.copy(center)
        controlsRef.current.update()
      }
      invalidate()
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log('[Viewport] Auto-framed camera:', { maxDim: maxDim.toFixed(4), near: camera.near.toFixed(4), far: camera.far.toFixed(2), pos: camera.position.toArray(), target: center.toArray() })
      }
    }
  }, [])

  const remountCanvas = useCallback(() => setCanvasKey((k) => k + 1), [])

  const handleCanvasClick = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement
    if (target.classList && target.classList.contains('webgl-canvas')) {
      onObjectSelect(null)
    }
  }, [onObjectSelect])

  const handleGLBLayersDetected = useCallback((layers: Array<{ id: string, name: string, mesh: THREE.Mesh }>) => {
    const glbModel = objects.find(obj => obj.type === 'glb_model')
    if (glbModel) {
      onGLBLayersDetected(glbModel.id, layers)
      // Auto-frame to the group of detected layers (first mesh as proxy)
      if (featureFlags.enableAutoFrameOnModelLoad && layers.length > 0) {
        // Create a temporary group to compute bounding box across all layer meshes
        const tempGroup = new THREE.Group()
        layers.forEach(l => tempGroup.add(l.mesh))
        // Use a microtask to ensure scene graph updates are applied before measuring
        queueMicrotask(() => {
          frameObjectToView(tempGroup)
          // Detach to avoid mutating the scene graph
          tempGroup.clear()
        })
      }
    }
  }, [objects, onGLBLayersDetected, frameObjectToView])

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

  const glbModels = objects.filter(obj => obj.type === 'glb_model')
  const regularObjects = objects.filter(obj => obj.type !== 'glb_model' && !obj.isLayer)
  const highFidelityLighting = featureFlags.enableHighFidelityViewportLighting

  return (
    <div className="viewport">
      <Canvas
        key={canvasKey}
        className="webgl-canvas"
        onClick={handleCanvasClick}
        onCreated={({ gl }) => {
          const overlayId = 'webgl-lost-overlay'
          gl.domElement.addEventListener('webglcontextlost', (e) => {
            e.preventDefault()
            // eslint-disable-next-line no-console
            console.error('WebGL context lost!')
            if (!document.getElementById(overlayId)) {
              const overlay = document.createElement('div')
              overlay.id = overlayId
              overlay.className = 'webgl-lost-overlay'
              overlay.innerHTML = '<h2>WebGL context lost!</h2><p>Please close other GPU-intensive tabs or apps and reload this page.</p>'
              document.body.appendChild(overlay)
            }
            // Auto-switch to safe mode and remount the Canvas (unless already forced safe via URL)
            if (!forcedSafe) {
              setRendererMode((prev) => {
                if (prev !== 'safe') {
                  // Remount after state update
                  setTimeout(() => remountCanvas(), 0)
                }
                return 'safe'
              })
            }
          })
          gl.domElement.addEventListener('webglcontextrestored', () => {
            const overlay = document.getElementById(overlayId)
            if (overlay) overlay.remove()
            invalidate()
          })

          // Diagnostics: collect renderer info
          try {
            const renderer = gl as THREE.WebGLRenderer
            const ctx = renderer.getContext() as WebGLRenderingContext | WebGL2RenderingContext
            const isWebGL2 = (ctx as WebGL2RenderingContext).createVertexArray !== undefined
            const debugInfo = (ctx.getExtension('WEBGL_debug_renderer_info') as unknown as { UNMASKED_VENDOR_WEBGL: number; UNMASKED_RENDERER_WEBGL: number } | null)
            const vendor = debugInfo ? (ctx.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) as string) : undefined
            const rendererStr = debugInfo ? (ctx.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) as string) : undefined
            setGlDiag({
              webglVersion: isWebGL2 ? 'WebGL2' : 'WebGL1',
              vendor,
              renderer: rendererStr,
              maxTextureSize: ctx.getParameter(ctx.MAX_TEXTURE_SIZE),
              maxCubeMapSize: ctx.getParameter(ctx.MAX_CUBE_MAP_TEXTURE_SIZE),
              antialias: ctx.getContextAttributes()?.antialias ?? undefined
            })
            // eslint-disable-next-line no-console
            console.log('WebGL diagnostics:', {
              webglVersion: isWebGL2 ? 'WebGL2' : 'WebGL1', vendor, renderer: rendererStr,
              maxTextureSize: ctx.getParameter(ctx.MAX_TEXTURE_SIZE),
              maxCubeMapSize: ctx.getParameter(ctx.MAX_CUBE_MAP_TEXTURE_SIZE),
              antialias: ctx.getContextAttributes()?.antialias
            })
          } catch (err) {
            // eslint-disable-next-line no-console
            console.warn('WebGL diagnostics collection failed:', err)
          }

          if (featureFlags.enableHighFidelityViewportLighting) {
            const renderer = gl as THREE.WebGLRenderer
            renderer.toneMapping = THREE.ACESFilmicToneMapping
            renderer.toneMappingExposure = 1.0
            renderer.outputColorSpace = THREE.SRGBColorSpace
            renderer.shadowMap.enabled = true
            renderer.shadowMap.type = THREE.PCFSoftShadowMap
          }
        }}
        shadows={true}
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
          preserveDrawingBuffer: false,
          failIfMajorPerformanceCaveat: false,
          stencil: false,
          depth: true,
          logarithmicDepthBuffer: true
        }}
        dpr={[1, 2]}
        frameloop="demand"
        performance={{ min: 0.5, max: 1 }}
        camera={{ position: cameraPosition, fov: 35, near: 0.01, far: 100 }}
      >
        <PerspectiveCamera 
          makeDefault 
          position={cameraPosition} 
          fov={35} 
          near={0.01} 
          far={50}
          // capture underlying THREE.PerspectiveCamera instance
          ref={(node) => {
            // Drei forwards the underlying Three camera
            // node can be null during unmount
            cameraRef.current = (node as unknown as THREE.PerspectiveCamera) || null
          }}
        />
        <Suspense fallback={<Loader />}>
          {/* Professional Dark Studio Environment - Eye-friendly */}
          {renderMode === 'studio' && <color attach="background" args={['#1a1b23']} />}
          {renderMode === 'realistic' && <color attach="background" args={['#242530']} />}
          {renderMode === 'night' && <color attach="background" args={['#0f0f14']} />}
          
          {/* Studio Lighting Setup */}
          {renderMode === 'studio' && (
            <>
              {/* HDRI Environment for realistic reflections */}
              <Environment 
                preset="studio"
                background={false}
                environmentIntensity={highFidelityLighting ? 1.0 : undefined}
              />
              
              {/* Key light - main directional lighting with warmer temperature */}
              <directionalLight 
                position={highFidelityLighting ? [5, 6, 3] : [3, 5, 2]} 
                intensity={highFidelityLighting ? 2.5 : 1.2} 
                color={highFidelityLighting ? '#fff5e6' : '#fff8e7'}
                castShadow
                shadow-mapSize-width={highFidelityLighting ? 4096 : 2048}
                shadow-mapSize-height={highFidelityLighting ? 4096 : 2048}
                shadow-camera-far={highFidelityLighting ? 50 : 30}
                shadow-camera-left={highFidelityLighting ? -10 : -8}
                shadow-camera-right={highFidelityLighting ? 10 : 8}
                shadow-camera-top={highFidelityLighting ? 10 : 8}
                shadow-camera-bottom={highFidelityLighting ? -10 : -8}
                shadow-bias={highFidelityLighting ? -0.00005 : -0.0001}
              />
              
              {/* Fill light - cooler secondary lighting */}
              <directionalLight 
                position={highFidelityLighting ? [-3, 4, 2] : [-2, 3, 1]} 
                intensity={highFidelityLighting ? 1.0 : 0.4} 
                color={highFidelityLighting ? '#e3f2ff' : '#e8f2ff'}
              />
              
              {/* Rim light for edge definition and material separation */}
              <directionalLight 
                position={highFidelityLighting ? [0, 3, -4] : [0, 2, -3]} 
                intensity={highFidelityLighting ? 0.8 : 0.3} 
                color={highFidelityLighting ? '#ffeedd' : '#ddeeff'}
              />
              
              {/* Ambient light for shadow fill */}
              <ambientLight intensity={highFidelityLighting ? 0.25 : 0.15} color={highFidelityLighting ? '#b3c8dc' : '#7c8db5'} />

              {highFidelityLighting && (
                <>
                  <pointLight position={[2, 2, 2]} intensity={0.5} color="#ffffff" />
                  <pointLight position={[-2, 2, 2]} intensity={0.3} color="#fff8f0" />
                </>
              )}
            </>
          )}
          
          {/* Realistic Lighting Setup */}
          {renderMode === 'realistic' && (
            <>
              {/* Natural environment mapping */}
              <Environment 
                preset="city"
                background={false}
                environmentIntensity={highFidelityLighting ? 1.2 : undefined}
              />
              
              {/* Natural key light */}
              <directionalLight 
                position={highFidelityLighting ? [6, 8, 4] : [4, 6, 3]} 
                intensity={highFidelityLighting ? 2.0 : 1.0} 
                color={highFidelityLighting ? '#fffaf0' : '#ffffff'}
                castShadow
                shadow-mapSize-width={highFidelityLighting ? 4096 : 2048}
                shadow-mapSize-height={highFidelityLighting ? 4096 : 2048}
                shadow-camera-far={highFidelityLighting ? 40 : 25}
                shadow-camera-left={highFidelityLighting ? -8 : -6}
                shadow-camera-right={highFidelityLighting ? 8 : 6}
                shadow-camera-top={highFidelityLighting ? 8 : 6}
                shadow-camera-bottom={highFidelityLighting ? -8 : -6}
                shadow-bias={highFidelityLighting ? -0.00005 : undefined}
              />
              
              {/* Environmental fill */}
              <directionalLight 
                position={highFidelityLighting ? [-2, 5, 3] : [-1, 4, 2]} 
                intensity={highFidelityLighting ? 0.8 : 0.35} 
                color={highFidelityLighting ? '#e6f2ff' : '#f0f4ff'}
              />
              
              {/* Ambient environmental lighting */}
              <ambientLight intensity={highFidelityLighting ? 0.4 : 0.25} color={highFidelityLighting ? '#c8dce8' : '#b8c5e0'} />

              {highFidelityLighting && (
                <rectAreaLight 
                  position={[0, 4, 0]} 
                  intensity={0.5} 
                  color="#ffffff"
                  width={10}
                  height={10}
                />
              )}
            </>
          )}
          
          {/* Night Mode Lighting Setup */}
          {renderMode === 'night' && (
            <>
              {/* Dark environment for night mood */}
              <Environment 
                preset="night"
                background={false}
                environmentIntensity={highFidelityLighting ? 0.5 : undefined}
              />
              
              {/* Moonlight key */}
              <directionalLight 
                position={highFidelityLighting ? [3, 10, 2] : [2, 8, 1]} 
                intensity={highFidelityLighting ? 1.5 : 0.8} 
                color={highFidelityLighting ? '#c0d8ff' : '#c8d4ff'}
                castShadow
                shadow-mapSize-width={highFidelityLighting ? 2048 : 1024}
                shadow-mapSize-height={highFidelityLighting ? 2048 : 1024}
                shadow-camera-far={highFidelityLighting ? 30 : 20}
                shadow-camera-left={highFidelityLighting ? -6 : -5}
                shadow-camera-right={highFidelityLighting ? 6 : 5}
                shadow-camera-top={highFidelityLighting ? 6 : 5}
                shadow-camera-bottom={highFidelityLighting ? -6 : -5}
                shadow-bias={highFidelityLighting ? -0.00005 : undefined}
              />
              
              {/* Subtle fill */}
              <directionalLight 
                position={highFidelityLighting ? [-2, 3, 3] : [-1, 2, 2]} 
                intensity={highFidelityLighting ? 0.4 : 0.2} 
                color={highFidelityLighting ? '#a0b8e0' : '#a8b8ff'}
              />
              
              {/* Minimal ambient */}
              <ambientLight intensity={highFidelityLighting ? 0.15 : 0.08} color={highFidelityLighting ? '#6080a8' : '#6272a4'} />

              {highFidelityLighting && (
                <spotLight 
                  position={[0, 5, -5]} 
                  intensity={0.6} 
                  color="#d0e0ff"
                />
              )}
            </>
          )}
          
          {/* Professional Grid - Adaptive to mode */}
          <Grid 
            args={[20, 20]} 
            cellColor={renderMode === 'night' ? '#2a2b35' : renderMode === 'realistic' ? '#3a3b45' : '#404155'} 
            sectionColor={renderMode === 'night' ? '#404155' : renderMode === 'realistic' ? '#5a5b65' : '#6a6b75'} 
            position={[0, -0.5, 0]} 
            fadeDistance={8} 
            fadeStrength={0.8} 
            cellSize={0.1} 
            sectionSize={1.0} 
            infiniteGrid 
            visible={showGrid} 
          />
          {glbModels.map(obj => {
            // Only render AI-generated models with valid URLs
            if (!obj.url) {
              console.warn(`⚠️ GLB model ${obj.id} has no URL, skipping render`)
              return null
            }
            
            // Ensure URL starts with /output (AI-generated) - no static models allowed
            if (!(obj.url.startsWith('/output/') || obj.url.startsWith('/uploads/'))) {
              console.warn(`⚠️ GLB model ${obj.id} URL ${obj.url} is not a recognized model source, skipping render`)
              return null
            }
            
            return (
              <GLBModel 
                key={obj.id} 
                url={obj.url} 
                parentModelId={obj.id} 
                source={obj.source}
                selectedLayerId={selectedObjectId} 
                onLayerSelect={onLayerSelect} 
                onLayersDetected={handleGLBLayersDetected} 
              />
            )
          }).filter(Boolean)}
          {regularObjects.map(obj => (
            <SceneObjectMesh key={obj.id} object={obj} isSelected={selectedObjectId === obj.id} onSelect={() => onObjectSelect(obj.id)} />
          ))}
          <OrbitControls 
            makeDefault 
            ref={(node) => { controlsRef.current = node }}
            enablePan 
            enableZoom 
            enableRotate 
            enableDamping 
            dampingFactor={0.05} 
            rotateSpeed={0.5} 
            zoomSpeed={1.2} 
            panSpeed={0.5} 
            minDistance={0.05} 
            maxDistance={50} 
            maxPolarAngle={Math.PI / 2} 
            target={[0, 0, 0]} 
          />
        </Suspense>
      </Canvas>
      <div className="viewport-debug-overlay">
        objects: {objects.length} | glbModels: {glbModels.length} | mode: {isEffectiveSafe ? 'safe' : 'normal'}{forcedSafe ? ' (forced)' : ''}
        {glDiag.webglVersion && (
          <>
            <br />
            {glDiag.webglVersion} | {glDiag.vendor || 'vendor?'} | {glDiag.renderer || 'renderer?'} | AA: {String(glDiag.antialias)} | maxTex: {glDiag.maxTextureSize} | maxCube: {glDiag.maxCubeMapSize}
          </>
        )}
      </div>
      {objects.length === 0 && !isGenerating && (
        <div className="viewport-empty">
          <div className="empty-icon">💎</div>
          <h3>Start a New Project</h3>
          <p>Use AI chat or load a GLB model to begin.</p>
        </div>
      )}
      <div className="viewport-controls">
        <div className="controls-group">
          <button className={`viewport-btn ${showWireframe ? 'active' : ''}`} onClick={handleToggleWireframe} title="Toggle Wireframe">▦ Wireframe</button>
          <button className={`viewport-btn ${showGrid ? 'active' : ''}`} onClick={handleToggleGrid} title="Toggle Grid">⊞ Grid</button>
          <button className="viewport-btn viewport-btn-trash" onClick={() => { void actions.initializeSession(); }} title="Delete current model and start new project">🗑️ New Project</button>
          <button
            className={`viewport-btn ${isEffectiveSafe ? 'active' : ''}`}
            onClick={() => { if (!forcedSafe) { setRendererMode(m => m === 'safe' ? 'normal' : 'safe'); remountCanvas(); } }}
            disabled={forcedSafe}
            title={forcedSafe ? 'Safe mode forced via URL (?safe=1)' : 'Toggle Performance Mode (Safe)'}
          >
            ⚡ Performance
          </button>
        </div>
        <div className="controls-group">
          <button className={`viewport-btn ${renderMode === 'realistic' ? 'active' : ''}`} onClick={() => handleSetRenderMode('realistic')} title="Realistic Rendering">✨ Real</button>
          <button className={`viewport-btn ${renderMode === 'studio' ? 'active' : ''}`} onClick={() => handleSetRenderMode('studio')} title="Studio Lighting">💡 Studio</button>
          <button className={`viewport-btn ${renderMode === 'night' ? 'active' : ''}`} onClick={() => handleSetRenderMode('night')} title="Night Mode">🌙 Night</button>
        </div>
      </div>
      <div className="performance-indicator"><div className="fps-badge"><span className="fps-label">Render:</span><span className="fps-value">60 FPS</span></div></div>
    </div>
  )
}
