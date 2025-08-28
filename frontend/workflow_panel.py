import bpy

class WorkflowPanel(bpy.types.Panel):
    bl_label = "Workflow"
    bl_idname = "ADDON_PT_WorkflowPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Tool'
    bl_order = 0 # Ensure this panel is at the top

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Import & Export", icon='ARROW_LEFTRIGHT')
        
        row = box.row(align=True)
        row.operator("addon.import_model", text="Import", icon='IMPORT')
        row.operator("addon.export", text="Export", icon='EXPORT')
