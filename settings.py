import bpy

class SceneSettings(bpy.types.PropertyGroup):
    """Stores all session settings for the add-on. Accessed via 'context.scene.aura_settings'."""
    
    prompt_text = bpy.props.StringProperty(
        name="Prompt",
        description="Describe the detail you want to add or the object to create",
        default="Swirling floral patterns"
    )
    
    analysis_report = bpy.props.StringProperty(
        name="Analysis Report",
        description="Results from the manufacturing quality check",
        default="Select an object and run a check."
    )
    
    # --- For async operations ---
    is_processing = bpy.props.BoolProperty(default=False)
    progress = bpy.props.IntProperty(subtype='PERCENTAGE', min=0, max=100, default=0)
    status_message = bpy.props.StringProperty(default="Ready")

def install_settings():
    bpy.utils.register_class(SceneSettings)
    bpy.types.Scene.aura_settings = bpy.props.PointerProperty(type=SceneSettings)

def uninstall_settings():
    del bpy.types.Scene.aura_settings
    bpy.utils.unregister_class(SceneSettings)
