import { useRef, useState, useEffect } from 'react'
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { Group, Mesh, Material, MeshStandardMaterial, Object3D } from 'three'
import { ThreeEvent } from '@react-three/fiber'


interface GLBModelProps {
  url: string
  parentModelId: string
  selectedLayerId: string | null
  onLayerSelect: (layerId: string) => void
  onLayersDetected: (layers: Array<{id: string, name: string, mesh: import('three').Mesh}>) => void
}

export default function GLBModel({ url, parentModelId, selectedLayerId, onLayerSelect, onLayersDetected }: GLBModelProps) {
  const groupRef = useRef<Group>(null)
  const [layers, setLayers] = useState<Array<{id: string, name: string, mesh: Mesh, originalMaterial: Material | Material[]}>>([])
  const [hoverLayerId, setHoverLayerId] = useState<string | null>(null)
  const [layersProcessed, setLayersProcessed] = useState(false) // Prevent re-processing

  // Always call useGLTF hook - let Three.js handle loading errors
  const gltf = useGLTF(url);
  const scene = gltf?.scene;

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
            child.material.envMapIntensity = 1.5
            child.material.needsUpdate = true
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
  }, [scene, onLayersDetected, parentModelId, layersProcessed])

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

  const handleClick = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation()
    
    // Find which mesh was clicked
    const clickedObject = event.object
    const clickedLayer = layers.find(layer => layer.mesh === clickedObject)
    
    if (clickedLayer) {
  // ...existing code...
      onLayerSelect(clickedLayer.id)
    }
  }

  const handlePointerOver = (event: ThreeEvent<PointerEvent>) => {
    event.stopPropagation()
    const hoveredObject = event.object
    const hoveredLayer = layers.find(layer => layer.mesh === hoveredObject)
    
    if (hoveredLayer) {
      setHoverLayerId(hoveredLayer.id)
      document.body.style.cursor = 'pointer'
    }
  }

  const handlePointerOut = () => {
    setHoverLayerId(null)
    document.body.style.cursor = 'default'
  }

  // Don't render if no scene is available
  if (!scene) {
    console.warn(`⚠️ GLBModel cannot render: No scene loaded for ${url}`)
    return null
  }

  return (
    <group 
      ref={groupRef} 
      onClick={handleClick}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
    >
      <primitive object={scene} />
    </group>
  )
}

// Note: GLB models are loaded dynamically based on AI-generated URLs
// No preloading of static models - everything is AI-generated