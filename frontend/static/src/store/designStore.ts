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
  // New properties for GLB layers
  isLayer?: boolean
  parentModelId?: string
  meshData?: any // THREE.Mesh reference for GLB layers
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
    
    // GLB Model management
    loadGLBModel: (modelPath: string, modelName: string) => void
    addGLBLayers: (modelId: string, layers: Array<{id: string, name: string, mesh: any}>) => void
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
  }
}

// Base API URL for backend communication
const API_BASE = '/api'

export const useDesignStore = create<DesignStoreState>((set, get) => ({
  // Initial state
  session: {
    id: 'new-session',
    objects: [],
    selectedObjectId: null,
    lastModified: Date.now()
  },
  
  system: {
    status: 'connecting',
    isGenerating: false,
    lastSync: 0
  },

  ui: {
    isLeftSidebarVisible: true,
    isRightSidebarVisible: true
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
              ...state.session,
              id: data.session_id,
              lastModified: Date.now()
            },
            system: { ...state.system, status: 'online', lastSync: Date.now() }
          }))
          console.log('✅ Design session initialized:', data.session_id)
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
          console.log('✅ Scene state synchronized with backend')
        }
      } catch (error) {
        console.error('Failed to load scene from backend:', error)
      }
    },

    // Add new object to scene
    addObject: (object: SceneObject) => {
      set((state) => ({
        session: {
          ...state.session,
          objects: [...state.session.objects, object],
          selectedObjectId: object.id,
          lastModified: Date.now()
        }
      }))
      console.log('✅ Object added to scene:', object.name)
    },

    // Update object with optimistic UI + backend sync
    updateObject: async (objectId: string, updates: Partial<SceneObject>) => {
      const { session } = get()
      
      // Optimistic update
      set((state) => ({
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
        
        console.log('✅ Object updated on backend')
      } catch (error) {
        console.error('Failed to update object on backend:', error)
        // Could implement rollback here if needed
      }
    },

    // Select object in scene
    selectObject: (objectId: string | null) => {
      set((state) => ({
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
      const modelId = `model_${Date.now()}`
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
        session: {
          ...state.session,
          objects: [...state.session.objects, modelObject],
          lastModified: Date.now()
        }
      }))
      
      console.log('✅ GLB Model loaded:', modelName)
    },

    // Add GLB Layers as individual objects
    addGLBLayers: (modelId: string, layers: Array<{id: string, name: string, mesh: any}>) => {
      const layerObjects: SceneObject[] = layers.map(layer => ({
        id: layer.id,
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
        session: {
          ...state.session,
          objects: [...state.session.objects, ...layerObjects],
          lastModified: Date.now()
        }
      }))
      
      console.log('✅ GLB Layers added to scene:', layers.map(l => l.name))
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
        console.log('🎯 Layer selected in store:', layer.name)
      }
    },

    // Execute AI prompt with context awareness
    executeAIPrompt: async (prompt: string) => {
      const { session } = get()
      
      set((state) => ({
        system: { ...state.system, isGenerating: true }
      }))
      
      try {
        console.log('🤖 Processing AI prompt with scene context:', prompt)
        
        const response = await fetch(`${API_BASE}/session/${session.id}/execute_prompt`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            prompt,
            current_scene: {
              objects: session.objects,
              selected_object_id: session.selectedObjectId
            }
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          console.log('✅ AI prompt executed:', data)
          
          // Add the new object to scene
          if (data.object) {
            get().actions.addObject(data.object)
          }
          
          // If modifications were made to existing objects, sync
          if (data.modifications) {
            await get().actions.loadSceneFromBackend()
          }
          
        } else {
          throw new Error('AI prompt execution failed')
        }
      } catch (error) {
        console.error('AI prompt failed:', error)
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
    }
  }
}))

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