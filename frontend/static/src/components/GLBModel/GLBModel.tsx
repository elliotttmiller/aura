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
      const center = box.getCenter(new Vector3())
      
      // Calculate scale to fit model nicely in view (target size around 0.5 units for better initial zoom)
      const maxDimension = Math.max(size.x, size.y, size.z)
      const targetSize = 0.5  // Reduced from 0.8 to 0.5 for less zoom
      const scale = maxDimension > 0 ? targetSize / maxDimension : 1
      
      // Apply scaling and centering
      scene.scale.setScalar(scale)
      scene.position.copy(center.negate().multiplyScalar(scale))
      
      setIsAutoFramed(true)
      
      // Log auto-framing info in development
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log(`📏 Auto-framed GLB model: size=${size.x.toFixed(3)}, ${size.y.toFixed(3)}, ${size.z.toFixed(3)}, scale=${scale.toFixed(3)}`)
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