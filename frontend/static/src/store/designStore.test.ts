import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDesignStore } from './designStore'
import type { SceneObject } from './designStore'

describe('Design Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    const { actions } = useDesignStore.getState()
    useDesignStore.setState({
      session: {
        id: 'test-session',
        objects: [],
        selectedObjectId: null,
        lastModified: Date.now(),
      },
      system: {
        status: 'online',
        isGenerating: false,
        lastSync: 0,
      },
      ui: {
        isLeftSidebarVisible: true,
        isRightSidebarVisible: true,
      },
    })
  })

  describe('Object Management', () => {
    it('should add object to session', () => {
      const { actions } = useDesignStore.getState()
      
      const testObject: SceneObject = {
        id: 'obj-1',
        name: 'Test Ring',
        type: 'mesh',
        visible: true,
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1],
        },
        material: {
          color: '#FFD700',
          roughness: 0.2,
          metallic: 1.0,
        },
      }

      actions.addObject(testObject)

      const { session } = useDesignStore.getState()
      expect(session.objects).toHaveLength(1)
      expect(session.objects[0]).toEqual(testObject)
    })

    it('should select object', () => {
      const { actions } = useDesignStore.getState()
      
      const testObject: SceneObject = {
        id: 'obj-1',
        name: 'Test Ring',
        type: 'mesh',
        visible: true,
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1],
        },
        material: {
          color: '#FFD700',
          roughness: 0.2,
          metallic: 1.0,
        },
      }

      actions.addObject(testObject)
      actions.selectObject('obj-1')

      const { session } = useDesignStore.getState()
      expect(session.selectedObjectId).toBe('obj-1')
    })

    it('should deselect object', () => {
      const { actions } = useDesignStore.getState()
      
      const testObject: SceneObject = {
        id: 'obj-1',
        name: 'Test Ring',
        type: 'mesh',
        visible: true,
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1],
        },
        material: {
          color: '#FFD700',
          roughness: 0.2,
          metallic: 1.0,
        },
      }

      actions.addObject(testObject)
      actions.selectObject('obj-1')
      actions.selectObject(null)

      const { session } = useDesignStore.getState()
      expect(session.selectedObjectId).toBeNull()
    })

    it('should toggle object visibility', () => {
      const { actions } = useDesignStore.getState()
      
      const testObject: SceneObject = {
        id: 'obj-1',
        name: 'Test Ring',
        type: 'mesh',
        visible: true,
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1],
        },
        material: {
          color: '#FFD700',
          roughness: 0.2,
          metallic: 1.0,
        },
      }

      actions.addObject(testObject)
      actions.toggleObjectVisibility('obj-1')

      const { session } = useDesignStore.getState()
      expect(session.objects[0].visible).toBe(false)
    })
  })

  describe('UI State Management', () => {
    it('should toggle left sidebar', () => {
      const { actions } = useDesignStore.getState()
      
      actions.toggleLeftSidebar()
      let { ui } = useDesignStore.getState()
      expect(ui.isLeftSidebarVisible).toBe(false)

      actions.toggleLeftSidebar()
      ui = useDesignStore.getState().ui
      expect(ui.isLeftSidebarVisible).toBe(true)
    })

    it('should toggle right sidebar', () => {
      const { actions } = useDesignStore.getState()
      
      actions.toggleRightSidebar()
      let { ui } = useDesignStore.getState()
      expect(ui.isRightSidebarVisible).toBe(false)

      actions.toggleRightSidebar()
      ui = useDesignStore.getState().ui
      expect(ui.isRightSidebarVisible).toBe(true)
    })

    it('should set left sidebar visible', () => {
      const { actions } = useDesignStore.getState()
      
      actions.setLeftSidebarVisible(false)
      const { ui } = useDesignStore.getState()
      expect(ui.isLeftSidebarVisible).toBe(false)
    })

    it('should set right sidebar visible', () => {
      const { actions } = useDesignStore.getState()
      
      actions.setRightSidebarVisible(false)
      const { ui } = useDesignStore.getState()
      expect(ui.isRightSidebarVisible).toBe(false)
    })
  })

  describe('System State Management', () => {
    it('should set system status', () => {
      const { actions } = useDesignStore.getState()
      
      actions.setSystemStatus('error')
      const { system } = useDesignStore.getState()
      expect(system.status).toBe('error')
    })

    it('should set generating state', () => {
      const { actions } = useDesignStore.getState()
      
      actions.setGenerating(true)
      let { system } = useDesignStore.getState()
      expect(system.isGenerating).toBe(true)

      actions.setGenerating(false)
      system = useDesignStore.getState().system
      expect(system.isGenerating).toBe(false)
    })
  })

  describe('GLB Model Management', () => {
    it('should load GLB model', () => {
      const { actions } = useDesignStore.getState()
      
      actions.loadGLBModel('/models/test.glb', 'Test Model')
      
      const { session } = useDesignStore.getState()
      expect(session.objects).toHaveLength(1)
      expect(session.objects[0].name).toBe('Test Model')
      expect(session.objects[0].type).toBe('glb-model')
    })

    it('should add GLB layers', () => {
      const { actions } = useDesignStore.getState()
      
      // First load the model
      actions.loadGLBModel('/models/test.glb', 'Test Model')
      const modelId = useDesignStore.getState().session.objects[0].id
      
      // Add layers
      const layers = [
        { id: 'layer-1', name: 'Band', mesh: {} },
        { id: 'layer-2', name: 'Stone', mesh: {} },
      ]
      actions.addGLBLayers(modelId, layers)
      
      const { session } = useDesignStore.getState()
      expect(session.objects).toHaveLength(3) // Model + 2 layers
    })
  })

  describe('API Integration', () => {
    it('should handle API errors gracefully during session init', async () => {
      // Mock fetch to return error
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          json: async () => ({ error: 'Server error' }),
        } as Response)
      )

      const { actions } = useDesignStore.getState()
      await actions.initializeSession()

      const { system } = useDesignStore.getState()
      expect(system.status).toBe('error')
    })
  })
})
