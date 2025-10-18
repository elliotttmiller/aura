import { useRef, useState, useEffect } from 'react'
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { Group, Mesh, Material, MeshStandardMaterial, Object3D, Box3, Vector3 } from 'three'
import { ThreeEvent } from '@react-three/fiber'
import { featureFlags } from '../../config/featureFlags'


interface GLBModelProps {
  url: string
  parentModelId: string
  source?: 'ai' | 'uploaded'
  selectedLayerId: string | null
  onLayerSelect: (layerId: string) => void
  onLayersDetected: (layers: Array<{id: string, name: string, mesh: import('three').Mesh}>) => void
}

export default function GLBModel({ url, parentModelId, source, selectedLayerId, onLayerSelect, onLayersDetected }: GLBModelProps) {
  const groupRef = useRef<Group>(null)
  const [layers, setLayers] = useState<Array<{id: string, name: string, mesh: Mesh, originalMaterial: Material | Material[]}>>([])
  const [hoverLayerId, setHoverLayerId] = useState<string | null>(null)
  const [layersProcessed, setLayersProcessed] = useState(false) // Prevent re-processing
  const [isAutoFramed, setIsAutoFramed] = useState(false) // Prevent re-framing
  // const { camera } = useThree() // Get camera for auto-framing (future use)

  // Always call useGLTF hook - let Three.js handle loading errors
  const gltf = useGLTF(url);
  const scene = gltf?.scene;

  // Auto-frame the model when it loads
  useEffect(() => {
    if (scene && !isAutoFramed) {
      const box = new Box3().setFromObject(scene)
      const size = box.getSize(new Vector3())
  // const center = box.getCenter(new Vector3()) // original center (not needed after grounding)
      
  // Calculate scale to fit model nicely in view
      const maxDimension = Math.max(size.x, size.y, size.z)
      
      // Adaptive target size based on original model scale
      // Professional jewelry models are often in real-world units (mm/cm)
      // AI models might be in arbitrary units
      let targetSize = 0.5  // Default visible size in viewport
      let scaleStrategy = 'default'
      
      if (maxDimension < 0.001) {
        // Extremely tiny (likely modeling error or microns)
        targetSize = 0.7
        scaleStrategy = 'micro'
      } else if (maxDimension < 0.1) {
        // Small models - likely jewelry in real-world mm/cm scale
        // These need significant scale-up to be visible
        targetSize = 0.6
        scaleStrategy = 'jewelry-realworld'
      } else if (maxDimension > 1000) {
        // Extremely large (likely modeling error or wrong units)
        targetSize = 0.3
        scaleStrategy = 'macro'
      } else if (maxDimension > 100) {
        // Large models - scale down significantly  
        targetSize = 0.35
        scaleStrategy = 'large'
      } else if (maxDimension > 10) {
        // Medium-large models
        targetSize = 0.45
        scaleStrategy = 'medium-large'
      } else {
        // Normal range (1-10 units)
        targetSize = 0.5
        scaleStrategy = 'normal'
      }
      
      const scale = maxDimension > 0 ? targetSize / maxDimension : 1
      
      // Apply scaling first
      scene.scale.setScalar(scale)

      // Recalculate bounds after scaling, then center in XZ and elevate above ground
      const scaledBox = new Box3().setFromObject(scene)
      const scaledSize = scaledBox.getSize(new Vector3())
      const scaledCenter = scaledBox.getCenter(new Vector3())
      
      // Calculate optimal elevation above grid (10% of model height minimum, 0.02 units minimum)
      const elevationHeight = Math.max(scaledSize.y * 0.1, 0.02)
      
      // XZ to origin, Y elevated above ground
      const elevatedY = -scaledBox.min.y + elevationHeight
      const posX = -scaledCenter.x
      const posZ = -scaledCenter.z
      scene.position.set(posX, elevatedY, posZ)

      // Store the visual center for camera/controls targeting
      // This is where the model appears to be centered after elevation
      const visualCenter = new Vector3(0, elevationHeight + scaledSize.y * 0.5, 0)
      scene.userData.visualCenter = visualCenter
      
      setIsAutoFramed(true)
      
      // Enhanced logging for debugging scale issues
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log(`📏 Auto-framing [${scaleStrategy}]: original=${maxDimension.toFixed(4)} units, target=${targetSize}, scale=${scale.toFixed(4)}x`)
        // eslint-disable-next-line no-console
        console.log(`   Dimensions (pre-scale): ${size.x.toFixed(4)} × ${size.y.toFixed(4)} × ${size.z.toFixed(4)}`)
        // eslint-disable-next-line no-console
  const finalSize = scaledBox.getSize(new Vector3())
  // eslint-disable-next-line no-console
  console.log(`   Final size: ${finalSize.x.toFixed(4)} × ${finalSize.y.toFixed(4)} × ${finalSize.z.toFixed(4)} | elevated @ y=${elevationHeight.toFixed(4)}`)
      }
    }
  }, [scene, isAutoFramed])

  useEffect(() => {
    if (scene && !layersProcessed) {
      // Extract all meshes from the scene and enhance materials
      const meshes: Array<{id: string, name: string, mesh: Mesh, originalMaterial: Material | Material[]}> = []
      let layerIndex = 0 // Track layer index for guaranteed uniqueness
      
      scene.traverse((child: Object3D) => {
        if (child instanceof Mesh) {
          // Store original material for restoration
          const originalMaterial = Array.isArray(child.material) ? child.material : child.material
          // Enable shadows for all meshes
          child.castShadow = true
          child.receiveShadow = true
          // Enhance material properties for jewelry
          if (child.material instanceof MeshStandardMaterial) {
            const shouldEnhanceMaterials = featureFlags.enableJewelryMaterialEnhancements && source === 'uploaded'
            const material = child.material as MeshStandardMaterial & { clearcoat?: number; clearcoatRoughness?: number }
            material.envMapIntensity = shouldEnhanceMaterials ? 2.0 : 1.5

            if (shouldEnhanceMaterials) {
              if (material.metalness === undefined || material.metalness === 0) {
                material.metalness = 0.8
              }
              if (material.roughness === undefined) {
                material.roughness = 0.2
              }
              material.clearcoat = 0.35
              material.clearcoatRoughness = 0.1
            }

            material.needsUpdate = true
          }
          // Use stable ID without timestamp to prevent re-processing
          const uniqueId = `${parentModelId}_layer_${layerIndex}_${child.uuid}`
          meshes.push({
            id: uniqueId,
            name: child.name || `Layer ${layerIndex + 1}`,
            mesh: child,
            originalMaterial: originalMaterial
          })
          layerIndex++
        }
      })
      
      setLayers(meshes)
      setLayersProcessed(true) // Mark as processed
      
      // Debug: Log layer detection in development
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log(`📋 GLBModel detected ${meshes.length} layers for model ${parentModelId}:`, meshes.map(m => m.id))
      }
      
  // Notify parent of detected layers
  onLayersDetected(meshes.map(({ id, name, mesh }) => ({ id, name, mesh })))
    }
  }, [scene, onLayersDetected, parentModelId, layersProcessed, source])

  useEffect(() => {
    // Apply selection and hover highlighting
    layers.forEach(({ id, mesh }) => {
      const isSelected = id === selectedLayerId
      const isHovered = id === hoverLayerId
      
      if (Array.isArray(mesh.material)) {
        mesh.material.forEach(mat => {
          if (mat instanceof MeshStandardMaterial) {
            if (isSelected) {
              mat.emissive.setHex(0x667eea)
              mat.emissiveIntensity = 0.4
            } else if (isHovered) {
              mat.emissive.setHex(0x764ba2)
              mat.emissiveIntensity = 0.2
            } else {
              mat.emissive.setHex(0x000000)
              mat.emissiveIntensity = 0
            }
          }
        })
      } else {
        if (mesh.material instanceof MeshStandardMaterial) {
          if (isSelected) {
            mesh.material.emissive.setHex(0x667eea)
            mesh.material.emissiveIntensity = 0.4
          } else if (isHovered) {
            mesh.material.emissive.setHex(0x764ba2)
            mesh.material.emissiveIntensity = 0.2
          } else {
            mesh.material.emissive.setHex(0x000000)
            mesh.material.emissiveIntensity = 0
          }
        }
      }
    })
  }, [selectedLayerId, hoverLayerId, layers])

  // Smooth rotation animation
  useFrame((state) => {
    if (groupRef.current && !selectedLayerId) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.2) * 0.1
    }
  })

  // Don't render if no scene is available
  if (!scene) {
    console.warn(`⚠️ GLBModel cannot render: No scene loaded for ${url}`)
    return null
  }

  return (
    <group ref={groupRef}>
      {layers.map(({ id, mesh }) => (
        <primitive 
          key={id}
          object={mesh.clone()} 
          onClick={(event: ThreeEvent<MouseEvent>) => {
            event.stopPropagation()
            onLayerSelect(id)
          }}
          onPointerOver={(event: ThreeEvent<PointerEvent>) => {
            event.stopPropagation()
            setHoverLayerId(id)
            document.body.style.cursor = 'pointer'
          }}
          onPointerOut={() => {
            setHoverLayerId(null)
            document.body.style.cursor = 'default'
          }}
        />
      ))}
    </group>
  )
}

// Note: GLB models are loaded dynamically based on AI-generated URLs
// No preloading of static models - everything is AI-generated