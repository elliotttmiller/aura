/**
 * Aura Sentient Design Studio - Central State Store
 * ================================================
 * 
 * This store implements the "Digital Twin" architecture - maintaining perfect
 * synchronization between frontend UI state and backend design session.
 * 
 * Part of V29 Sentient Interface Implementation.
 */

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

// Core types for the design system
export interface SceneObject {
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
  // URL for GLB models (AI-generated or loaded)
  url?: string
  // New properties for GLB layers
  isLayer?: boolean
  parentModelId?: string
  meshData?: import('three').Mesh // THREE.Mesh reference for GLB layers
}

export interface DesignSession {
  id: string
  objects: SceneObject[]
  selectedObjectId: string | null
  lastModified: number
}

export interface SystemState {
  status: 'online' | 'error' | 'connecting'
  isGenerating: boolean
  lastSync: number
}

export interface UIState {
  isLeftSidebarVisible: boolean
  isRightSidebarVisible: boolean
}

// Complete application state
interface DesignStoreState {
  // Session data (Digital Twin of backend)
  session: DesignSession
  // History stacks for undo/redo
  history: {
    past: Array<{ objects: SceneObject[]; selectedObjectId: string | null }>
    future: Array<{ objects: SceneObject[]; selectedObjectId: string | null }>
  }
  
  // System state
  system: SystemState
  
  // UI state for adaptive layout
  ui: UIState
  
  // Actions for state mutations
  actions: {
    // Session management
    initializeSession: (sessionId?: string) => Promise<void>
    loadSceneFromBackend: () => Promise<void>
    
    // Object management
    addObject: (object: SceneObject) => void
    updateObject: (objectId: string, updates: Partial<SceneObject>) => Promise<void>
    selectObject: (objectId: string | null) => void
    toggleObjectVisibility: (objectId: string) => void
  // History
  undo: () => void
  redo: () => void
    
    // GLB Model management
    loadGLBModel: (modelPath: string, modelName: string) => void
  addGLBLayers: (modelId: string, layers: Array<{id: string, name: string, mesh: import('three').Mesh}>) => void
    selectLayer: (layerId: string | null) => void
    
    // AI integration
    executeAIPrompt: (prompt: string) => Promise<void>
    
    // System management
    setSystemStatus: (status: SystemState['status']) => void
    setGenerating: (isGenerating: boolean) => void
    syncWithBackend: () => Promise<void>
    
    // UI management for adaptive layout
    toggleLeftSidebar: () => void
    toggleRightSidebar: () => void
    setLeftSidebarVisible: (visible: boolean) => void
    setRightSidebarVisible: (visible: boolean) => void
    // Persistence helpers
    saveProject: () => void
    exportSceneJSON: () => void
  }
}

// Base API URL for backend communication
const API_BASE = '/api'

// Persist only the UI slice (sidebar visibility) to localStorage
export const useDesignStore = create<DesignStoreState>()(
  persist(
    (set, get) => ({
  // Initial state
  session: {
    id: 'new-session',
    objects: [],
    selectedObjectId: null,
    lastModified: Date.now()
  },
  history: { past: [], future: [] },
  
  system: {
    status: 'connecting',
    isGenerating: false,
    lastSync: 0
  },

  ui: {
    isLeftSidebarVisible: true, // Always true on load
    isRightSidebarVisible: true // Show right sidebar (Properties Inspector & Chat) by default
  },

  actions: {
    // Initialize a new design session
    initializeSession: async () => {
      try {
        set((state) => ({
          system: { ...state.system, status: 'connecting' }
        }))
        
        const response = await fetch(`${API_BASE}/session/new`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          const data = await response.json()
          set((state) => ({
            session: {
              // Start fresh on new session
              id: data.session_id,
              objects: [],
              selectedObjectId: null,
              lastModified: Date.now()
            },
            history: { past: [], future: [] },
            system: { ...state.system, status: 'online', lastSync: Date.now() }
          }))
          // ...existing code...
        } else {
          throw new Error('Failed to create session')
        }
      } catch (error) {
        console.error('Session initialization failed:', error)
        set((state) => ({
          system: { ...state.system, status: 'error' }
        }))
        throw error
      }
    },

    // Load scene state from backend (Digital Twin sync)
    loadSceneFromBackend: async () => {
      try {
        const { session } = get()
        const response = await fetch(`${API_BASE}/scene/${session.id}`)
        
        if (response.ok) {
          const data = await response.json()
          set((state) => ({
            session: {
              ...state.session,
              objects: data.scene?.objects || [],
              lastModified: Date.now()
            },
            system: { ...state.system, lastSync: Date.now() }
          }))
          // ...existing code...
        }
      } catch (error) {
        console.error('Failed to load scene from backend:', error)
      }
    },

    // Add new object to scene
    addObject: (object: SceneObject) => {
      set((state) => ({
        history: { past: [...state.history.past, { objects: [...state.session.objects], selectedObjectId: state.session.selectedObjectId }], future: [] },
        session: {
          ...state.session,
          objects: [...state.session.objects, object],
          selectedObjectId: object.id,
          lastModified: Date.now()
        }
      }))
  // ...existing code...
    },

    // Update object with optimistic UI + backend sync
    updateObject: async (objectId: string, updates: Partial<SceneObject>) => {
      const { session } = get()
      
      // Optimistic update
      set((state) => ({
        history: { past: [...state.history.past, { objects: [...state.session.objects], selectedObjectId: state.session.selectedObjectId }], future: [] },
        session: {
          ...state.session,
          objects: state.session.objects.map(obj =>
            obj.id === objectId ? { ...obj, ...updates } : obj
          ),
          lastModified: Date.now()
        }
      }))

      // Sync with backend
      try {
        if (updates.transform) {
          await fetch(`${API_BASE}/object/${session.id}/${objectId}/transform`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates.transform)
          })
        }
        
        if (updates.material) {
          await fetch(`${API_BASE}/object/${session.id}/${objectId}/material`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates.material)
          })
        }
        
        set((state) => ({
          system: { ...state.system, lastSync: Date.now() }
        }))
        
  // ...existing code...
      } catch (error) {
        console.error('Failed to update object on backend:', error)
        // Could implement rollback here if needed
      }
    },

    // Select object in scene
    selectObject: (objectId: string | null) => {
      set((state) => ({
        history: { past: [...state.history.past, { objects: [...state.session.objects], selectedObjectId: state.session.selectedObjectId }], future: [] },
        session: {
          ...state.session,
          selectedObjectId: objectId
        }
      }))
    },

    // Toggle object visibility
    toggleObjectVisibility: (objectId: string) => {
      const { actions } = get()
      const { session } = get()
      const obj = session.objects.find(o => o.id === objectId)
      if (obj) {
        actions.updateObject(objectId, { visible: !obj.visible })
      }
    },

    // Load GLB Model - create a parent model object
    loadGLBModel: (_modelPath: string, modelName: string) => {
      // Use crypto.randomUUID for unique model IDs; fallback to Date.now if unavailable
      let modelId: string
      if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
        modelId = `model_${crypto.randomUUID()}`
      } else {
        modelId = `model_${Date.now()}_${Math.floor(Math.random() * 1e9)}`
      }
      const modelObject: SceneObject = {
        id: modelId,
        name: modelName,
        type: 'glb_model',
        visible: true,
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1]
        },
        material: {
          color: '#ffffff',
          roughness: 0.5,
          metallic: 0.5
        }
      }
      
      set((state) => ({
        history: { past: [...state.history.past, { objects: [...state.session.objects], selectedObjectId: state.session.selectedObjectId }], future: [] },
        session: {
          ...state.session,
          objects: [...state.session.objects, modelObject],
          lastModified: Date.now()
        }
      }))
      
  // ...existing code...
    },

    // Add GLB Layers as individual objects
    // Layer ids must be globally unique: `${modelId}_layer_${child.uuid}`
  addGLBLayers: (modelId: string, layers: Array<{id: string, name: string, mesh: import('three').Mesh}>) => {
      // Filter out any layers that already exist to prevent duplicates
      const existingLayerIds = new Set(get().session.objects.filter(obj => obj.isLayer && obj.parentModelId === modelId).map(obj => obj.id))
      const newLayers = layers.filter(layer => !existingLayerIds.has(layer.id))
      
      if (newLayers.length === 0) {
        // No new layers to add, all already exist
        return
      }
      
      const layerObjects: SceneObject[] = newLayers.map(layer => ({
        id: layer.id, // already unique from GLBModel
        name: layer.name,
        type: 'glb_layer',
        visible: true,
        isLayer: true,
        parentModelId: modelId,
        meshData: layer.mesh,
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1]
        },
        material: {
          color: '#ffffff',
          roughness: 0.5,
          metallic: 0.5
        }
      }))
      
      set((state) => ({
        history: { past: [...state.history.past, { objects: [...state.session.objects], selectedObjectId: state.session.selectedObjectId }], future: [] },
        session: {
          ...state.session,
          objects: [...state.session.objects, ...layerObjects],
          lastModified: Date.now()
        }
      }))
      
  // ...existing code...
    },

    // History controls
    undo: () => {
      const { history, session } = get()
      if (history.past.length === 0) return
      const previous = history.past[history.past.length - 1]
      const newPast = history.past.slice(0, -1)
      set({
        history: {
          past: newPast,
          future: [{ objects: [...session.objects], selectedObjectId: session.selectedObjectId }, ...history.future]
        },
        session: {
          ...session,
          objects: previous.objects,
          selectedObjectId: previous.selectedObjectId,
          lastModified: Date.now()
        }
      })
    },
    redo: () => {
      const { history, session } = get()
      if (history.future.length === 0) return
      const next = history.future[0]
      const newFuture = history.future.slice(1)
      set({
        history: {
          past: [...history.past, { objects: [...session.objects], selectedObjectId: session.selectedObjectId }],
          future: newFuture
        },
        session: {
          ...session,
          objects: next.objects,
          selectedObjectId: next.selectedObjectId,
          lastModified: Date.now()
        }
      })
    },

    // Select layer (same as selectObject but with additional logging for layers)
    selectLayer: (layerId: string | null) => {
      const { session } = get()
      const layer = session.objects.find(obj => obj.id === layerId)
      
      set((state) => ({
        session: {
          ...state.session,
          selectedObjectId: layerId
        }
      }))
      
      if (layer && layer.isLayer) {
  // ...existing code...
      }
    },

    // Execute AI prompt with context awareness
    executeAIPrompt: async (prompt: string) => {
      const { session } = get()
      // Guard: Only allow if session.id is valid
      if (!session.id || session.id === 'new-session') {
        set((state) => ({
          system: { ...state.system, isGenerating: false }
        }))
        console.error('Cannot execute prompt: No valid session established.')
        return
      }

      set((state) => ({
        system: { ...state.system, isGenerating: true }
      }))

      try {
        // Use the NEW Enhanced AI Orchestrator endpoint
        const response = await fetch(`${API_BASE}/ai/generate-3d-model`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            prompt,
            complexity: 'moderate',  // Can be made dynamic based on prompt analysis
            session_id: session.id,
            context: {
              existing_objects: Object.values(session.objects).map(obj => ({
                id: obj.id,
                name: obj.name,
                type: obj.type
              })),
              selected_object_id: session.selectedObjectId
            }
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          
          if (data.success) {
            // Create new object from AI generation result
            const newObject: SceneObject = {
              id: data.object_id || `ai-${Date.now()}`,
              name: `AI: ${prompt.substring(0, 30)}...`,
              type: 'glb_model',  // Use glb_model type so it renders as GLB file
              visible: true,
              transform: {
                position: [0, 0, 0],
                rotation: [0, 0, 0],
                scale: [1, 1, 1]
              },
              material: {
                color: data.material_specifications?.primary_material?.base_color || '#FFD700',
                roughness: data.material_specifications?.primary_material?.roughness || 0.2,
                metallic: data.material_specifications?.primary_material?.metallic || 0.8
              },
              // Convert full file path to relative URL for frontend serving
              url: (() => {
                if (data.model_url) {
                  return data.model_url // Use provided URL directly
                } else if (data.glb_file) {
                  // Convert full file path to relative URL
                  const fullPath = data.glb_file.replace(/\\/g, '/') // Normalize path separators
                  const outputIndex = fullPath.indexOf('/output/')
                  if (outputIndex !== -1) {
                    return fullPath.substring(outputIndex) // Extract "/output/ai_generated/filename.glb"
                  }
                  // Fallback: try to extract just the filename and assume it's in ai_generated
                  const filename = fullPath.split('/').pop()
                  return `/output/ai_generated/${filename}`
                }
                return null
              })()
            }
            
            // Add the AI-generated object to the scene
            get().actions.addObject(newObject)
            
            // eslint-disable-next-line no-console
            console.log('✅ AI-generated object added:', newObject)
            // eslint-disable-next-line no-console
            console.log('📝 User prompt:', prompt)
            // eslint-disable-next-line no-console
            console.log('📦 Construction plan:', data.construction_plan)
            // eslint-disable-next-line no-console
            console.log('💎 Materials:', data.material_specifications)
            if (data.blender_execution?.success) {
              // eslint-disable-next-line no-console
              console.log('🔨 Blender execution successful!')
              // eslint-disable-next-line no-console
              console.log('📁 GLB file:', data.glb_file)
              // eslint-disable-next-line no-console
              console.log('⏱️  Execution time:', data.blender_execution.execution_time, 's')
            } else if (data.blender_execution) {
              // eslint-disable-next-line no-console
              console.warn('⚠️ Blender execution failed:', data.blender_execution.error)
            }
          } else {
            throw new Error(data.error || 'AI generation failed')
          }
          
        } else {
          const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
          throw new Error(errorData.error || 'AI prompt execution failed')
        }
      } catch (error) {
        console.error('❌ AI prompt failed:', error)
        throw error
      } finally {
        set((state) => ({
          system: { ...state.system, isGenerating: false }
        }))
      }
    },

    // System status management
    setSystemStatus: (status: SystemState['status']) => {
      set((state) => ({
        system: { ...state.system, status }
      }))
    },

    setGenerating: (isGenerating: boolean) => {
      set((state) => ({
        system: { ...state.system, isGenerating }
      }))
    },

    // Force sync with backend
    syncWithBackend: async () => {
      await get().actions.loadSceneFromBackend()
    },

    // UI management for adaptive layout
    toggleLeftSidebar: () => {
      set((state) => ({
        ui: { ...state.ui, isLeftSidebarVisible: !state.ui.isLeftSidebarVisible }
      }))
    },

    toggleRightSidebar: () => {
      set((state) => ({
        ui: { ...state.ui, isRightSidebarVisible: !state.ui.isRightSidebarVisible }
      }))
    },

    setLeftSidebarVisible: (visible: boolean) => {
      set((state) => ({
        ui: { ...state.ui, isLeftSidebarVisible: visible }
      }))
    },

    setRightSidebarVisible: (visible: boolean) => {
      set((state) => ({
        ui: { ...state.ui, isRightSidebarVisible: visible }
      }))
    },
    // Persistence helpers (client-side JSON)
    saveProject: () => {
      const { session } = get()
      const blob = new Blob([JSON.stringify(session, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `aura_project_${session.id}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },
    exportSceneJSON: () => {
      const { session } = get()
      const scene = {
        id: session.id,
        objects: session.objects,
        selectedObjectId: session.selectedObjectId,
        lastModified: session.lastModified
      }
      const blob = new Blob([JSON.stringify(scene, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `aura_scene_${session.id}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }
    }),
    {
      name: 'aura-ui-v1',
      version: 1,
      storage: createJSONStorage(() => localStorage),
      // Only persist the lightweight UI slice
      partialize: (state) => ({ ui: state.ui })
    }
  )
)

// Convenience hooks for accessing specific parts of the store
export const useSession = () => useDesignStore((state) => state.session)
export const useSystemState = () => useDesignStore((state) => state.system)
export const useUIState = () => useDesignStore((state) => state.ui)
export const useActions = () => useDesignStore((state) => state.actions)

// Health check helper
export const checkSystemHealth = async () => {
  try {
    const response = await fetch(`${API_BASE}/health`)
    const health = await response.json()
    return health.status === 'healthy' ? 'online' : 'error'
  } catch (error) {
    console.error('Health check failed:', error)
    return 'error'
  }
}