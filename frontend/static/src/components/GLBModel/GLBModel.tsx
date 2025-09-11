import { useRef, useState, useEffect } from 'react'
import { useGLTF } from '@react-three/drei'
import { Group, Mesh, Material, MeshStandardMaterial } from 'three'
import { ThreeEvent } from '@react-three/fiber'

interface GLBModelProps {
  url: string
  selectedLayerId: string | null
  onLayerSelect: (layerId: string) => void
  onLayersDetected: (layers: Array<{id: string, name: string, mesh: Mesh}>) => void
}

export default function GLBModel({ url, selectedLayerId, onLayerSelect, onLayersDetected }: GLBModelProps) {
  const { scene } = useGLTF(url)
  const groupRef = useRef<Group>(null)
  const [layers, setLayers] = useState<Array<{id: string, name: string, mesh: Mesh, originalMaterial: Material | Material[]}>>([])

  useEffect(() => {
    if (scene) {
      // Extract all meshes from the scene
      const meshes: Array<{id: string, name: string, mesh: Mesh, originalMaterial: Material | Material[]}> = []
      
      scene.traverse((child) => {
        if (child instanceof Mesh) {
          // Store original material for restoration
          const originalMaterial = Array.isArray(child.material) ? child.material : child.material
          
          meshes.push({
            id: `layer_${child.uuid}`,
            name: child.name || `Layer ${meshes.length + 1}`,
            mesh: child,
            originalMaterial: originalMaterial
          })
        }
      })
      
      setLayers(meshes)
      
      // Notify parent of detected layers
      onLayersDetected(meshes.map(({ id, name, mesh }) => ({ id, name, mesh })))
      
      console.log('🔍 Detected layers in GLB model:', meshes.map(m => m.name))
    }
  }, [scene, onLayersDetected])

  useEffect(() => {
    // Apply selection highlighting
    layers.forEach(({ id, mesh }) => {
      if (id === selectedLayerId) {
        // Apply highlight material
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach(mat => {
            if (mat instanceof MeshStandardMaterial) {
              mat.emissive.setHex(0x4299e1)
              mat.emissiveIntensity = 0.3
            }
          })
        } else {
          if (mesh.material instanceof MeshStandardMaterial) {
            mesh.material.emissive.setHex(0x4299e1)
            mesh.material.emissiveIntensity = 0.3
          }
        }
      } else {
        // Restore original material
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach(mat => {
            if (mat instanceof MeshStandardMaterial) {
              mat.emissive.setHex(0x000000)
              mat.emissiveIntensity = 0
            }
          })
        } else {
          if (mesh.material instanceof MeshStandardMaterial) {
            mesh.material.emissive.setHex(0x000000)
            mesh.material.emissiveIntensity = 0
          }
        }
      }
    })
  }, [selectedLayerId, layers])

  const handleClick = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation()
    
    // Find which mesh was clicked
    const clickedObject = event.object
    const clickedLayer = layers.find(layer => layer.mesh === clickedObject)
    
    if (clickedLayer) {
      console.log('🎯 Layer selected:', clickedLayer.name)
      onLayerSelect(clickedLayer.id)
    }
  }

  return (
    <group ref={groupRef} onClick={handleClick}>
      <primitive object={scene} />
    </group>
  )
}

// Preload the GLB model
useGLTF.preload('/3d_models/diamond_ring_example.glb')