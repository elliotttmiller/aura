
import bpy
from backend.backend import check_dependencies

from .settings import install_settings, uninstall_settings
from .backend.preferences import AddonPreferences, install_preferences, uninstall_preferences
from .frontend.tool_panel import ChatPanel, GenerateOperator, ModalOperator, ToggleSidebarOperator, SwitchParadigmOperator
from .backend.operators import SentientOperator


ALL_CLASSES = [
    AddonPreferences,
    ChatPanel, 
    GenerateOperator,
    ModalOperator,
    ToggleSidebarOperator,
    SwitchParadigmOperator,
    SentientOperator,
]

def create_design_workspace():
    """
    V32 Pillar 1: Forging the "Unified Studio" Multi-Paradigm Experience
    
    Create the dedicated "Aura" workspace optimized for multi-paradigm design.
    - Clean, focused UI with tabbed paradigm switching
    - Leave only 3D Viewport and unified Design sidebar  
    - Optimized for seamless NURBS/Mesh paradigm transitions
    """
    print("V32: Creating Unified Studio multi-paradigm workspace...")
    
    # Create new workspace named "Aura" as specified
    workspace_name = "Aura"
    if workspace_name not in bpy.data.workspaces:
        workspace = bpy.data.workspaces.new(workspace_name)
        
        # Get the first screen from the workspace
        screen = workspace.screens[0]
        
        # V32 Enhancement: Create clean, multi-paradigm focused layout
        # Clear all existing areas and create single 3D viewport
        for area in screen.areas:
            area.type = 'VIEW_3D'
        
        # Set workspace as active to configure
        bpy.context.window.workspace = workspace
        
        # V32 Multi-Paradigm Mode: Configure 3D viewport for optimal design experience
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        # Show the "Design" sidebar (region_ui) 
                        space.show_region_ui = True
                        
                        # V32 Enhancement: Optimal shading for multi-paradigm work
                        space.shading.type = 'MATERIAL' 
                        space.shading.use_scene_lights_render = True
                        space.shading.use_scene_world_render = True
                        
                        # V32 Enhancement: Hide non-essential UI elements for paradigm focus
                        space.show_region_header = True  # Keep header for essential controls
                        space.show_region_toolbar = False  # Hide tool toolbar for clean experience
                        space.show_region_hud = False  # Hide HUD for minimalism
                        
                        # V32 Enhancement: Ensure Aura sidebar is visible and selected
                        for region in area.regions:
                            if region.type == 'UI':
                                # The sidebar will default to the Aura category due to bl_category = 'Aura'
                                break
                        break
                break
    
    # Set Aura workspace as active (this becomes the default)
    bpy.context.window.workspace = bpy.data.workspaces[workspace_name]
    print("V32: Unified Studio workspace created and activated - Multi-paradigm design experience ready")

def install():
    print("Installing Aura V22 Verifiable Artisan...")
    
    # Perform dependency check
    if not check_dependencies(report_error=False):
        print("Aura V22 Warning: Critical dependencies not found. Some AI features may be disabled.")

    install_settings()
    install_preferences()
    
    # Register all classes
    for cls in ALL_CLASSES:
        bpy.utils.register_class(cls)
    
    # V22 Pillar 1: Create the "Aura Mode" immersive workspace
    bpy.app.timers.register(create_design_workspace, first_interval=0.1)
    
    print("Aura V22 Verifiable Artisan installed successfully")

def uninstall():
    print("Uninstalling Aura V22 Verifiable Artisan...")
    
    # Unregister classes in reverse order
    for cls in reversed(ALL_CLASSES):
        bpy.utils.unregister_class(cls)
        
    uninstall_preferences()
    uninstall_settings()
    
    # Remove Aura workspace
    workspace_name = "Aura"
    if workspace_name in bpy.data.workspaces:
        bpy.data.workspaces.remove(bpy.data.workspaces[workspace_name])
    
    print("Aura V22 Verifiable Artisan uninstalled successfully")
