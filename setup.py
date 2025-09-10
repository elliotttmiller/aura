
import bpy
from backend.backend import check_dependencies

from .settings import install_settings, uninstall_settings
from .preferences import AddonPreferences, install_preferences, uninstall_preferences
from .frontend.tool_panel import ChatPanel, GenerateOperator, ModalOperator
from .operators import SentientOperator


ALL_CLASSES = [
    AddonPreferences,
    ChatPanel, 
    GenerateOperator,
    ModalOperator,
    SentientOperator,
]

def create_design_workspace():
    """Create the dedicated 'Design Studio' workspace with clean, focused UI."""
    print("Creating Design Studio workspace...")
    
    # Create new workspace
    if "Design Studio" not in bpy.data.workspaces:
        workspace = bpy.data.workspaces.new("Design Studio")
        workspace = bpy.data.workspaces.new("Design Studio")
        
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
    
    # Set Design Studio workspace as active
    bpy.context.window.workspace = bpy.data.workspaces["Design Studio"]
    print("Design Studio workspace created and activated")

def install():
    print("Installing Design Engine V20.0...")
    
    # Perform dependency check
    if not check_dependencies(report_error=False):
        print("Design Engine Warning: Critical dependencies not found. Some AI features may be disabled.")

    install_settings()
    install_preferences()
    
    # Register all classes
    for cls in ALL_CLASSES:
        bpy.utils.register_class(cls)
    
    # Create the Design Studio workspace
    bpy.app.timers.register(create_design_workspace, first_interval=0.1)
    
    print("Design Engine V20.0 installed successfully")

def uninstall():
    print("Uninstalling Design Engine V20.0...")
    
    # Unregister classes in reverse order
    for cls in reversed(ALL_CLASSES):
        bpy.utils.unregister_class(cls)
        
    uninstall_preferences()
    uninstall_settings()
    
    # Remove Design Studio workspace
    if "Design Studio" in bpy.data.workspaces:
        bpy.data.workspaces.remove(bpy.data.workspaces["Design Studio"])
    
    print("Design Engine V20.0 uninstalled successfully")
