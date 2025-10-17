import { useRef, useState, useEffect } from 'react'
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
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
  const [hoverLayerId, setHoverLayerId] = useState<string | null>(null)

  useEffect(() => {
    if (scene) {
      // Extract all meshes from the scene and enhance materials
      const meshes: Array<{id: string, name: string, mesh: Mesh, originalMaterial: Material | Material[]}> = []
      
      scene.traverse((child) => {
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
      
      console.log('✨ Enhanced GLB model with', meshes.length, 'layers')
    }
  }, [scene, onLayersDetected])

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
      console.log('✨ Layer selected:', clickedLayer.name)
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

// Preload the GLB model
useGLTF.preload('/3d_models/diamond_ring_example.glb')