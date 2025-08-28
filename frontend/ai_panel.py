import bpy

class AIPanel(bpy.types.Panel):
    bl_label = "AI Co-Pilot"
    bl_idname = "ADDON_PT_AIPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Tool'
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        settings = context.scene.addon_settings

        box = layout.box()
        box.label(text="AI Generation", icon='LIGHT')
        
        col = box.column()
        col.prop(settings, "prompt_text", text="")
        
        row = box.row(align=True)
        row.scale_y = 1.5
        
        # Button to add detail to an existing, selected object
        add_detail_op = row.operator("addon.add_detail", text="Add Detail", icon='MODIFIER')
        add_detail_op.enabled = context.active_object is not None
        
        # Button to generate a new object from scratch
        row.operator("addon.generate_from_scratch", text="From Scratch", icon='PLAY')
