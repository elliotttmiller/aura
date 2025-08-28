import bpy

class AnalysisPanel(bpy.types.Panel):
    bl_label = "Analysis"
    bl_idname = "ADDON_PT_AnalysisPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Tool'
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        settings = context.scene.addon_settings

        box = layout.box()
        box.label(text="Manufacturing Check", icon='SHIELD')
        
        op = box.operator("addon.analyze", text="Run Check on Selected", icon='VIEWZOOM')
        op.enabled = context.active_object is not None
        
        report_box = box.box()
        for line in settings.analysis_report.split('\n'):
            report_box.label(text=line)
