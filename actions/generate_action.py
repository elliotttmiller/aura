import bpy
from ..backend import ai_model, mesh_tools

class GenerateFromScratchOperator(bpy.types.Operator):
    bl_idname = "addon.generate_from_scratch"
    bl_label = "Generate From Scratch"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.addon_settings
        raw_data = ai_model.generate_from_scratch(settings.prompt_text)
        mesh_tools.create_object_in_scene(raw_data, "GeneratedObject", context)
        return {'FINISHED'}

class AddDetailOperator(bpy.types.Operator):
    bl_idname = "addon.add_detail"
    bl_label = "Add Detail to Selected"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        settings = context.scene.addon_settings
        target_obj = context.active_object
        
        detail_data = ai_model.add_surface_detail(target_obj, settings.prompt_text)
        detail_obj = mesh_tools.create_object_in_scene(detail_data, "GeneratedDetail", context)
        
        mesh_tools.join_objects(base_obj=target_obj, detail_obj=detail_obj, context=context)
        
        return {'FINISHED'}
