import bpy

class UniversalSceneSettings(bpy.types.PropertyGroup):
    """Stores all session settings for the add-on. Accessed via 'context.scene.universal_settings'."""
    
    prompt_text = bpy.props.StringProperty(
        name="Prompt",
        description="Describe the procedural asset you want to create or modify",
        default="Organic flowing patterns with geometric features"
    )
    
    analysis_report = bpy.props.StringProperty(
        name="Analysis Report",
        description="Results from the procedural quality analysis",
        default="Select an object and run analysis."
    )
    
    # V20.0 Mesh Quality Control for Marching Cubes - 8GB VRAM optimized
    mesh_quality = bpy.props.IntProperty(
        name="Mesh Quality",
        description="Resolution for Marching Cubes algorithm (32=low, 64=med, 128=high, 256=ultra)",
        default=64,
        min=16,
        max=256,  # Reduced max for 8GB VRAM optimization
        step=16   # Stepped intervals for better performance
    )
    
    # --- For async operations ---
    is_processing = bpy.props.BoolProperty(default=False)
    progress = bpy.props.IntProperty(subtype='PERCENTAGE', min=0, max=100, default=0)
    status_message = bpy.props.StringProperty(default="Ready")

def install_settings():
    bpy.utils.register_class(UniversalSceneSettings)
    bpy.types.Scene.universal_settings = bpy.props.PointerProperty(type=UniversalSceneSettings)

def uninstall_settings():
    del bpy.types.Scene.universal_settings
    bpy.utils.unregister_class(UniversalSceneSettings)
