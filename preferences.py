import bpy

class AddonPreferences(bpy.types.AddonPreferences):
    """User-configurable settings saved across Blender sessions."""
    bl_idname = __package__

    model_path = bpy.props.StringProperty(
        name="AI Models Folder",
        description="Path to the folder containing your .onnx AI models",
        subtype='DIR_PATH',
    )
    
    compute_device = bpy.props.EnumProperty(
        name="Compute Device",
        description="Select the device to run AI computations on",
        items=[('CPU', 'CPU', 'Slower, more compatible'),
               ('GPU', 'GPU', 'Faster, requires compatible hardware')],
        default='GPU'
    )
    
    min_wall_thickness = bpy.props.FloatProperty(
        name="Min Wall Thickness (mm)",
        description="The minimum acceptable thickness for manufacturing checks",
        default=0.8,
        min=0.1,
        max=5.0
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Core Configuration")
        box.prop(self, "model_path")
        box.prop(self, "compute_device")
        
        box = layout.box()
        box.label(text="Analysis Settings")
        box.prop(self, "min_wall_thickness")

def install_preferences():
    bpy.utils.register_class(AddonPreferences)

def uninstall_preferences():
    bpy.utils.unregister_class(AddonPreferences)
