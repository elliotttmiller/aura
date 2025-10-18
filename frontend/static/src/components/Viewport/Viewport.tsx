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
import * as THREE from 'three'
import GLBModel from '../GLBModel/GLBModel'
import './Viewport.css'
import { useActions } from '../../store/designStore'

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
    }
  }, [objects, onGLBLayersDetected])

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

  return (
    <div className="viewport">
      <Canvas
        key={canvasKey}
        className="webgl-canvas"
        onClick={handleCanvasClick}
        onCreated={({ gl }) => {
          // Enhanced render settings for better quality
          gl.toneMapping = THREE.ACESFilmicToneMapping
          gl.toneMappingExposure = 1.0
          gl.outputColorSpace = THREE.SRGBColorSpace
          gl.shadowMap.enabled = true
          gl.shadowMap.type = THREE.PCFSoftShadowMap
          
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
        }}
        shadows={true}
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
          preserveDrawingBuffer: false,
          failIfMajorPerformanceCaveat: false,
          stencil: true,
          depth: true,
          logarithmicDepthBuffer: true,
        }}
        dpr={[1, 2]}
        frameloop="demand"
        performance={{ min: 0.5, max: 1 }}
        camera={{ position: cameraPosition, fov: 35, near: 0.01, far: 100 }}
      >
        <PerspectiveCamera makeDefault position={cameraPosition} fov={35} near={0.01} far={50} />
        <Suspense fallback={<Loader />}>
          {/* Professional Dark Studio Environment - Eye-friendly */}
          {renderMode === 'studio' && <color attach="background" args={['#1a1b23']} />}
          {renderMode === 'realistic' && <color attach="background" args={['#242530']} />}
          {renderMode === 'night' && <color attach="background" args={['#0f0f14']} />}
          
          {/* Studio Lighting Setup - Professional 3-Point Setup */}
          {renderMode === 'studio' && (
            <>
              {/* HDRI Environment for realistic reflections and global illumination */}
              <Environment 
                preset="studio"
                background={false}
                environmentIntensity={1.0}
              />
              
              {/* Key Light - Main directional lighting with proper color temperature (5500K - daylight) */}
              <directionalLight 
                position={[5, 6, 3]} 
                intensity={2.5} 
                color="#fff5e6"
                castShadow
                shadow-mapSize-width={4096}
                shadow-mapSize-height={4096}
                shadow-camera-far={50}
                shadow-camera-left={-10}
                shadow-camera-right={10}
                shadow-camera-top={10}
                shadow-camera-bottom={-10}
                shadow-bias={-0.00005}
                shadow-normalBias={0.02}
                shadow-radius={2}
              />
              
              {/* Fill Light - Softer, cooler secondary lighting (6500K - cool daylight) */}
              <directionalLight 
                position={[-3, 4, 2]} 
                intensity={1.0} 
                color="#e3f2ff"
              />
              
              {/* Back/Rim Light - Edge definition and material separation (4000K - warm) */}
              <directionalLight 
                position={[0, 3, -4]} 
                intensity={0.8} 
                color="#ffeedd"
              />
              
              {/* Ambient light for shadow fill - subtle blue sky color */}
              <ambientLight intensity={0.25} color="#b3c8dc" />
              
              {/* Additional accent lights for jewelry highlights */}
              <pointLight position={[2, 2, 2]} intensity={0.5} color="#ffffff" distance={5} decay={2} />
              <pointLight position={[-2, 2, 2]} intensity={0.3} color="#fff8f0" distance={5} decay={2} />
            </>
          )}
          
          {/* Realistic Lighting Setup - Natural outdoor lighting with global illumination */}
          {renderMode === 'realistic' && (
            <>
              {/* Natural HDRI environment for global illumination and accurate reflections */}
              <Environment 
                preset="city"
                background={false}
                environmentIntensity={1.2}
              />
              
              {/* Sun Light - Natural key light (5800K - natural sunlight) */}
              <directionalLight 
                position={[6, 8, 4]} 
                intensity={2.0} 
                color="#fffaf0"
                castShadow
                shadow-mapSize-width={4096}
                shadow-mapSize-height={4096}
                shadow-camera-far={40}
                shadow-camera-left={-8}
                shadow-camera-right={8}
                shadow-camera-top={8}
                shadow-camera-bottom={-8}
                shadow-bias={-0.00005}
                shadow-normalBias={0.02}
                shadow-radius={1.5}
              />
              
              {/* Sky Light - Environmental fill from sky (7500K - clear sky) */}
              <directionalLight 
                position={[-2, 5, 3]} 
                intensity={0.8} 
                color="#e6f2ff"
              />
              
              {/* Ambient environmental lighting - indirect light bounces */}
              <ambientLight intensity={0.4} color="#c8dce8" />
              
              {/* Soft area light for additional fill */}
              <rectAreaLight 
                position={[0, 4, 0]} 
                intensity={0.5} 
                color="#ffffff"
                width={10}
                height={10}
              />
            </>
          )}
          
          {/* Night Mode Lighting Setup - Cinematic moonlight with volumetric feel */}
          {renderMode === 'night' && (
            <>
              {/* Dark environment for night mood with subtle starlight */}
              <Environment 
                preset="night"
                background={false}
                environmentIntensity={0.5}
              />
              
              {/* Moonlight Key - Cool, dramatic main light (4100K - moonlight) */}
              <directionalLight 
                position={[3, 10, 2]} 
                intensity={1.5} 
                color="#c0d8ff"
                castShadow
                shadow-mapSize-width={2048}
                shadow-mapSize-height={2048}
                shadow-camera-far={30}
                shadow-camera-left={-6}
                shadow-camera-right={6}
                shadow-camera-top={6}
                shadow-camera-bottom={-6}
                shadow-bias={-0.00005}
                shadow-normalBias={0.02}
                shadow-radius={2}
              />
              
              {/* Subtle atmospheric fill - night sky ambient */}
              <directionalLight 
                position={[-2, 3, 3]} 
                intensity={0.4} 
                color="#a0b8e0"
              />
              
              {/* Minimal ambient - deep night atmosphere */}
              <ambientLight intensity={0.15} color="#6080a8" />
              
              {/* Accent rim light for cinematic edge definition */}
              <spotLight 
                position={[0, 5, -5]} 
                intensity={0.6} 
                color="#d0e0ff"
                angle={0.6}
                penumbra={0.5}
                distance={10}
                decay={2}
              />
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
            if (!obj.url.startsWith('/output/')) {
              console.warn(`⚠️ GLB model ${obj.id} URL ${obj.url} is not an AI-generated model, skipping render`)
              return null
            }
            
            return (
              <GLBModel key={obj.id} url={obj.url} parentModelId={obj.id} selectedLayerId={selectedObjectId} onLayerSelect={onLayerSelect} onLayersDetected={handleGLBLayersDetected} />
            )
          }).filter(Boolean)}
          {regularObjects.map(obj => (
            <SceneObjectMesh key={obj.id} object={obj} isSelected={selectedObjectId === obj.id} onSelect={() => onObjectSelect(obj.id)} />
          ))}
          <OrbitControls 
            makeDefault 
            enablePan 
            enableZoom 
            enableRotate 
            enableDamping 
            dampingFactor={0.05} 
            rotateSpeed={0.5} 
            zoomSpeed={1.2} 
            panSpeed={0.5} 
            minDistance={0.1} 
            maxDistance={5} 
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
