import bpy
from backend.aura_backend import ProcessingEngine, create_object_in_scene, prepare_and_join, run_analysis, import_model, export_model
from backend.aura_helpers import get_addon_root, get_models_path, get_assets_path, add_vendor_to_path

# --- Panels ---
class WorkflowPanel(bpy.types.Panel):
    bl_label = "Workflow"
    bl_idname = "DESIGN_PT_WorkflowPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Design'
    bl_order = 0
    def draw(self, context):
        layout = self.layout
        settings = context.scene.tool_settings
        layout.enabled = not settings.is_processing
        box = layout.box()
        box.label(text="Import & Export", icon='ARROW_LEFTRIGHT')
        row = box.row(align=True)
        row.operator("addon.import_model", text="Import", icon='IMPORT')
        row.operator("addon.export", text="Export", icon='EXPORT')

class AIPanel(bpy.types.Panel):
    bl_label = "AI Co-Pilot"
    bl_idname = "DESIGN_PT_AIPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Design'
    bl_order = 1
    def draw(self, context):
        layout = self.layout
        settings = context.scene.tool_settings
        layout.enabled = not settings.is_processing
        box = layout.box()
        box.label(text="AI Generation", icon='LIGHT')
        col = box.column()
        col.prop(settings, "prompt_text", text="")
        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("addon.add_detail", text="Add Detail", icon='MODIFIER')
        row.operator("addon.generate_from_scratch", text="From Scratch", icon='PLAY')
        if settings.is_processing:
            processing_box = layout.box()
            processing_box.label(text="Processing...", icon='TIME')

class AnalysisPanel(bpy.types.Panel):
    bl_label = "Analysis"
    bl_idname = "DESIGN_PT_AnalysisPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Design'
    bl_order = 2
    def draw(self, context):
        layout = self.layout
        settings = context.scene.tool_settings
        layout.enabled = not settings.is_processing
        box = layout.box()
        box.label(text="Manufacturing Check", icon='SHIELD')
        box.operator("addon.analyze", text="Run Check on Selected", icon='VIEWZOOM')
        report_box = box.box()
        for line in settings.analysis_report.split('\n'):
            report_box.label(text=line)

class LibraryPanel(bpy.types.Panel):
    bl_label = "Asset Library"
    bl_idname = "DESIGN_PT_LibraryPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Design'
    bl_order = 3
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        layout = self.layout
        settings = context.scene.tool_settings
        layout.enabled = not settings.is_processing
        box = layout.box()
        box.label(text="Add Components", icon='COLLECTION_NEW')
        row = box.row()
        row.label(text="Example Asset 1")
        op = row.operator("addon.add_asset", text="Add", icon='ADD')
        op.asset_name = "asset_one.blend"

# --- Operators ---
class GenerateFromScratchOperator(bpy.types.Operator):
    bl_idname = "addon.generate_from_scratch"
    bl_label = "Generate From Scratch"
    def execute(self, context):
        # Placeholder for async logic
        self.report({'INFO'}, "Generated from scratch.")
        return {'FINISHED'}

class AddDetailOperator(bpy.types.Operator):
    bl_idname = "addon.add_detail"
    bl_label = "Add Detail"
    def execute(self, context):
        self.report({'INFO'}, "Detail added.")
        return {'FINISHED'}

class AnalyzeOperator(bpy.types.Operator):
    bl_idname = "addon.analyze"
    bl_label = "Analyze"
    def execute(self, context):
        self.report({'INFO'}, "Analysis complete.")
        return {'FINISHED'}

class AddAssetOperator(bpy.types.Operator):
    bl_idname = "addon.add_asset"
    bl_label = "Add Asset"
    asset_name = bpy.props.StringProperty()
    def execute(self, context):
        self.report({'INFO'}, f"Asset {self.asset_name} added.")
        return {'FINISHED'}

class ImportOperator(bpy.types.Operator):
    bl_idname = "addon.import_model"
    bl_label = "Import Model"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob = bpy.props.StringProperty(default="*.obj;*.stl", options={'HIDDEN'})
    def execute(self, context):
        import_model(self.filepath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ExportOperator(bpy.types.Operator):
    bl_idname = "addon.export"
    bl_label = "Export Model"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob = bpy.props.StringProperty(default="*.stl;*.obj", options={'HIDDEN'})
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        if not self.filepath.lower().endswith(('.stl', '.obj')):
            self.filepath += '.stl'
        export_format = 'STL' if self.filepath.lower().endswith('.stl') else 'OBJ'
        export_model(self.filepath, context, export_format)
        return {'FINISHED'}
    def invoke(self, context, event):
        self.filepath = f"{context.active_object.name}.stl"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# --- Registration ---
ALL_CLASSES = [
    WorkflowPanel, AIPanel, AnalysisPanel, LibraryPanel,
    GenerateFromScratchOperator, AddDetailOperator, AnalyzeOperator,
    AddAssetOperator, ImportOperator, ExportOperator
]

def register():
    for cls in ALL_CLASSES:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(ALL_CLASSES):
        bpy.utils.unregister_class(cls)
