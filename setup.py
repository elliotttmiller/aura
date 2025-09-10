
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
    """Create the dedicated 'Aura V24 Studio' workspace with clean, focused UI."""
    print("Creating Aura V24 Autonomous Design Studio workspace...")
    
    # Create new workspace
    workspace_name = "Aura V24 Studio"
    if workspace_name not in bpy.data.workspaces:
        workspace = bpy.data.workspaces.new(workspace_name)
        
        # Get the first screen from the workspace
        screen = workspace.screens[0]
        
        # Clear existing areas and create clean layout
        for area in screen.areas:
            area.type = 'VIEW_3D'
            
        # Split screen to add sidebar
        bpy.context.window.workspace = workspace
        bpy.context.area.type = 'VIEW_3D'
        
        # Ensure the sidebar is visible and set to Aura category
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.show_region_ui = True
                        space.shading.type = 'MATERIAL'
                        break
                break
    
    # Set Aura V24 Studio workspace as active
    bpy.context.window.workspace = bpy.data.workspaces[workspace_name]
    print("Aura V24 Autonomous Design Studio workspace created and activated")

def install():
    print("Installing Aura V24 Autonomous Design Engine...")
    
    # Perform dependency check
    if not check_dependencies(report_error=False):
        print("Aura V24 Warning: Critical dependencies not found. Some AI features may be disabled.")

    install_settings()
    install_preferences()
    
    # Register all classes
    for cls in ALL_CLASSES:
        bpy.utils.register_class(cls)
    
    # Create the Aura V24 Studio workspace
    bpy.app.timers.register(create_design_workspace, first_interval=0.1)
    
    print("Aura V24 Autonomous Design Engine installed successfully")

def uninstall():
    print("Uninstalling Aura V24 Autonomous Design Engine...")
    
    # Unregister classes in reverse order
    for cls in reversed(ALL_CLASSES):
        bpy.utils.unregister_class(cls)
        
    uninstall_preferences()
    uninstall_settings()
    
    # Remove Aura V24 Studio workspace
    workspace_name = "Aura V24 Studio"
    if workspace_name in bpy.data.workspaces:
        bpy.data.workspaces.remove(bpy.data.workspaces[workspace_name])
    
    print("Aura V24 Autonomous Design Engine uninstalled successfully")
