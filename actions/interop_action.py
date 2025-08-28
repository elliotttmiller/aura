import bpy
from ..backend import interop

class ImportOperator(bpy.types.Operator):
    bl_idname = "addon.import_model"
    bl_label = "Import Model"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.obj;*.stl", options={'HIDDEN'})

    def execute(self, context):
        interop.import_model(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ExportOperator(bpy.types.Operator):
    bl_idname = "addon.export"
    bl_label = "Export Model"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.stl;*.obj", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # Default to .stl if no extension is given
        if not self.filepath.lower().endswith(('.stl', '.obj')):
            self.filepath += '.stl'
        
        export_format = 'STL' if self.filepath.lower().endswith('.stl') else 'OBJ'
        interop.export_model(self.filepath, context, export_format)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = f"{context.active_object.name}.stl"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
