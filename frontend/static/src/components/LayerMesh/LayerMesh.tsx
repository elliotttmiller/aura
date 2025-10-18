import { useRef, useEffect, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh, MeshStandardMaterial } from 'three'
import { ThreeEvent } from '@react-three/fiber'

interface LayerMeshProps {
  meshData: Mesh
  layerId: string
  isSelected: boolean
  visible: boolean
  transform: {
    position: [number, number, number]
    rotation: [number, number, number]
    scale: [number, number, number]
  }
  onSelect: (layerId: string) => void
  onHover?: (layerId: string | null) => void
}

export default function LayerMesh({
  meshData,
  layerId,
  isSelected,
  visible,
  transform,
  onSelect,
  onHover
}: LayerMeshProps) {
  const meshRef = useRef<Mesh>(null)
  const [isHovered, setIsHovered] = useState(false)
  const [clonedMesh] = useState(() => {
    // Clone the mesh for independent rendering
    const cloned = meshData.clone()
    cloned.visible = true // Ensure the clone is visible
    
    // Debug: Log layer mesh creation in development
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.log(`🔷 LayerMesh created for ${layerId}:`, { 
        geometry: cloned.geometry, 
        material: cloned.material,
        visible: cloned.visible 
      })
    }
    
    return cloned
  })

  // Apply transform and visibility from store to mesh
  useEffect(() => {
    if (clonedMesh) {
      // Apply transforms
      clonedMesh.position.fromArray(transform.position)
      clonedMesh.rotation.fromArray(transform.rotation)  
      clonedMesh.scale.fromArray(transform.scale)
      
      // Apply visibility - make sure mesh is visible when LayerMesh is rendered
      clonedMesh.visible = visible
    }
  }, [transform, visible, clonedMesh])

  // Ensure mesh is visible when component mounts
  useEffect(() => {
    if (clonedMesh) {
      clonedMesh.visible = visible
    }
  }, [clonedMesh, visible])

  // Apply selection and hover highlighting
  useEffect(() => {
    if (clonedMesh) {
      const mesh = clonedMesh
      
      // Handle material highlighting for selection and hover
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
    }
  }, [isSelected, isHovered, clonedMesh])

  // Subtle animation for selected layers
  useFrame((state) => {
    if (clonedMesh && isSelected) {
      // Very subtle "breathing" animation
      const breathe = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.02
      clonedMesh.scale.setScalar(breathe)
    }
  })

  const handleClick = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation()
    onSelect(layerId)
  }

  const handlePointerOver = (event: ThreeEvent<PointerEvent>) => {
    event.stopPropagation()
    setIsHovered(true)
    onHover?.(layerId)
    document.body.style.cursor = 'pointer'
  }

  const handlePointerOut = () => {
    setIsHovered(false)
    onHover?.(null)
    document.body.style.cursor = 'default'
  }

  if (!visible) {
    return null
  }

  return (
    <primitive
      ref={meshRef}
      object={clonedMesh}
      onClick={handleClick}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
    />
  )
}