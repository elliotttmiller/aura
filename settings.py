import bpy

class AddonSettings(bpy.types.PropertyGroup):
    """Stores all session settings for the add-on."""
    
    prompt_text: bpy.props.StringProperty(
        name="Prompt",
        description="Describe the detail you want to add or the object to create",
        default="Swirling floral patterns"
    )
    
    analysis_report: bpy.props.StringProperty(
        name="Analysis Report",
        description="Results from the manufacturing quality check",
        default="Select an object and run a check."
    )

def install_settings():
    bpy.utils.register_class(AddonSettings)
    bpy.types.Scene.addon_settings = bpy.props.PointerProperty(type=AddonSettings)

def uninstall_settings():
    del bpy.types.Scene.addon_settings
    bpy.utils.unregister_class(AddonSettings)
