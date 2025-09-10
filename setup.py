
import bpy
from backend.aura_backend import check_dependencies

from .settings import install_settings, uninstall_settings
from .preferences import AddonPreferences, install_preferences, uninstall_preferences
from .frontend.aura_panel import AuraChatPanel, AuraGenerateOperator, AuraModalOperator
from .operators import AuraSentientOperator


ALL_CLASSES = [
    AddonPreferences,
    AuraChatPanel, 
    AuraGenerateOperator,
    AuraModalOperator,
    AuraSentientOperator,
]

def create_aura_workspace():
    """Create the dedicated 'Aura' workspace with clean, focused UI."""
    print("Creating Aura Mode workspace...")
    
    # Create new workspace
    if "Aura" not in bpy.data.workspaces:
        workspace = bpy.data.workspaces.new("Aura")
        
        # Get the first screen from the workspace
        screen = workspace.screens[0]
        
        # Clear existing areas and create clean layout
        for area in screen.areas:
            area.type = 'VIEW_3D'
            
        # Split screen to add sidebar
        bpy.context.window.workspace = workspace
        bpy.context.area.type = 'VIEW_3D'
        
        # Ensure the sidebar is visible and set to Design category
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.show_region_ui = True
                        space.shading.type = 'MATERIAL'
                        break
                break
    
    # Set Aura workspace as active
    bpy.context.window.workspace = bpy.data.workspaces["Aura"]
    print("Aura Mode workspace created and activated")

def install():
    print("Installing Aura V14.0 Sentient Artisan Environment...")
    
    # Perform dependency check
    if not check_dependencies(report_error=False):
        print("Aura Warning: Critical dependencies not found. Some AI features may be disabled.")

    install_settings()
    install_preferences()
    
    # Register all classes
    for cls in ALL_CLASSES:
        bpy.utils.register_class(cls)
    
    # Create the Aura workspace
    bpy.app.timers.register(create_aura_workspace, first_interval=0.1)
    
    print("Aura V14.0 Sentient Artisan Environment installed successfully")

def uninstall():
    print("Uninstalling Aura V14.0 Sentient Artisan Environment...")
    
    # Unregister classes in reverse order
    for cls in reversed(ALL_CLASSES):
        bpy.utils.unregister_class(cls)
        
    uninstall_preferences()
    uninstall_settings()
    
    # Remove Aura workspace
    if "Aura" in bpy.data.workspaces:
        bpy.data.workspaces.remove(bpy.data.workspaces["Aura"])
    
    print("Aura V14.0 uninstalled successfully")
