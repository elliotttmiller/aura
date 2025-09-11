"""
V22 Verifiable Artisan - Native Chat Interface
===========================================

Modern AI chat sidebar interface for real-time cognitive streaming.
This provides a native Blender experience with live AI thought process visualization.

Implements Protocol 3: Architectural Purity (The Native Imperative)
Implements Protocol 1: Sentient Transparency (Live cognitive streaming)
"""

import bpy
import json
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ChatPanel(bpy.types.Panel):
    """
    V32 Unified Design Studio - Master Control Room
    
    Multi-paradigm interface supporting both NURBS precision and Mesh artistry.
    Features tabbed interface switching between Rhino (NURBS) and Blender (Mesh)
    paradigms, with unified AI chat and collapsible sidebar functionality.
    
    Implements Protocol 13: The Unified Studio Doctrine (Master Control Room)
    Implements Protocol 14: AI as Multi-Paradigm Architect (Strategic Delegation)
    """
    
    bl_label = "🔮 Aura V32 Unified Design Studio"
    bl_idname = "DESIGN_PT_ChatPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aura'
    bl_order = 0
    bl_description = "V32 Unified Design Studio - Multi-paradigm Master Control Room with NURBS precision and Mesh artistry"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.settings
        
        # V32 Master Header with collapsible controls
        header_box = layout.box()
        header_row = header_box.row(align=True)
        
        # Collapse/Expand button for full-screen viewport
        if settings.sidebar_collapsed:
            expand_op = header_row.operator("design.toggle_sidebar", text="⬅️", emboss=True)
            expand_op.action = 'EXPAND'
            header_row.label(text="V32 Studio")
            return  # Show minimal collapsed state
        else:
            collapse_op = header_row.operator("design.toggle_sidebar", text="➡️", emboss=True)  
            collapse_op.action = 'COLLAPSE'
            header_row.label(text="🔮 Aura V32 Unified Design Studio", icon='TOOL_SETTINGS')
        
        # V32 Enhanced status with multi-paradigm awareness
        if settings.is_processing:
            status_text = f"🧠 Processing ({settings.active_paradigm_tab} Engine)..."
            status_icon = 'TIME'
            header_box.alert = True
        else:
            status_text = "✅ Ready for Multi-Paradigm Design"
            status_icon = 'CHECKMARK'
            header_box.alert = False
        
        status_row = header_box.row()
        status_row.label(text=f"Status: {status_text}", icon=status_icon)
        
        # Start/Stop Design Operator check
        if not self._is_design_operator_running(context):
            activate_op = layout.operator("design.sentient_operator", text="🔮 Activate V32 Multi-Paradigm Studio", icon='PLAY')
            activate_op.bl_description = "Start the V32 Unified Design Studio for multi-paradigm collaboration"
            layout.separator()
            layout.label(text="💡 Activate to begin multi-paradigm design collaboration", icon='INFO')
            return

        # V32 TABBED INTERFACE - The Core Innovation
        tabs_box = layout.box()
        tabs_box.label(text="🎛️ Design Paradigm Selection", icon='TAB_NEW')
        
        tab_row = tabs_box.row(align=True)
        tab_row.scale_y = 1.2
        
        # NURBS tab
        nurbs_op = tab_row.operator("design.switch_paradigm", text="🏭 Rhino (NURBS)")
        nurbs_op.paradigm = 'NURBS'
        if settings.active_paradigm_tab == 'NURBS':
            nurbs_op = tab_row.operator("design.switch_paradigm", text="🏭 Rhino (NURBS) ✓", depress=True)
            nurbs_op.paradigm = 'NURBS'
            
        # MESH tab  
        mesh_op = tab_row.operator("design.switch_paradigm", text="🎨 Blender (Mesh)")
        mesh_op.paradigm = 'MESH'
        if settings.active_paradigm_tab == 'MESH':
            mesh_op = tab_row.operator("design.switch_paradigm", text="🎨 Blender (Mesh) ✓", depress=True)
            mesh_op.paradigm = 'MESH'

        layout.separator()

        # V32 CONTEXT-SENSITIVE TOOLSETS
        self._draw_paradigm_toolset(layout, context, settings)
        
        layout.separator()
        
        # V32 UNIFIED AI CHAT INTERFACE - Persistent across paradigms
        self._draw_unified_ai_chat(layout, context, settings)

    def _draw_paradigm_toolset(self, layout, context, settings):
        """Draw context-sensitive toolset based on active paradigm tab."""
        
        toolset_box = layout.box()
        
        if settings.active_paradigm_tab == 'NURBS':
            # NURBS Precision Toolset
            toolset_box.label(text="🏭 NURBS Precision Controls", icon='MESH_GRID')
            
            nurbs_col = toolset_box.column(align=True)
            nurbs_col.scale_y = 0.9
            
            # NURBS-specific controls
            nurbs_col.prop(settings, "nurbs_fillet_radius", text="Fillet Radius")
            nurbs_col.prop(settings, "nurbs_curve_degree", text="Curve Degree") 
            
            # Material properties for NURBS
            material_row = nurbs_col.row()
            material_row.prop(settings, "material_type", text="Material")
            
            # Size controls for precision
            size_row = nurbs_col.row()
            size_row.prop(settings, "asset_size", text="Size (mm)")
            
        elif settings.active_paradigm_tab == 'MESH':
            # Mesh Artistic Toolset  
            toolset_box.label(text="🎨 Mesh Artistry Controls", icon='SCULPTMODE_HLT')
            
            mesh_col = toolset_box.column(align=True)
            mesh_col.scale_y = 0.9
            
            # Mesh-specific controls
            mesh_col.prop(settings, "mesh_subdivision_levels", text="Subdivision Levels")
            mesh_col.prop(settings, "mesh_remesh_resolution", text="Remesh Resolution")
            mesh_col.prop(settings, "mesh_quality", text="Mesh Quality")
            
            # Artistic properties for mesh
            feature_row = mesh_col.row()
            feature_row.prop(settings, "feature_shape", text="Feature Shape")
            
            scale_row = mesh_col.row()
            scale_row.prop(settings, "feature_scale", text="Feature Detail")

    def _draw_unified_ai_chat(self, layout, context, settings):
        """Draw the unified AI chat interface - persistent across all paradigms."""
        
        # AI Chat Messages Display
        chat_box = layout.box()
        paradigm_indicator = "🏭 NURBS" if settings.active_paradigm_tab == 'NURBS' else "🎨 MESH"
        chat_box.label(text=f"🧠 Multi-Paradigm AI Architect ({paradigm_indicator})", icon='COMMUNITY')
        
        # Display chat messages with paradigm awareness
        try:
            messages = json.loads(settings.chat_messages or "[]")
            
            if messages:
                chat_scroll = chat_box.column(align=True)
                chat_scroll.scale_y = 0.8
                
                recent_messages = messages[-8:] if len(messages) > 8 else messages
                
                for msg in recent_messages:
                    msg_row = chat_scroll.row(align=True)
                    content = msg['content']
                    
                    if msg['role'] == 'system':
                        msg_row.label(text="🔧 " + content[:70] + ("..." if len(content) > 70 else ""))
                    elif msg['role'] == 'assistant':
                        # Show paradigm awareness in AI responses
                        if 'NURBS' in content or 'nurbs' in content:
                            msg_row.label(text="🏭 " + content[:70] + ("..." if len(content) > 70 else ""))
                        elif 'MESH' in content or 'mesh' in content:
                            msg_row.label(text="🎨 " + content[:70] + ("..." if len(content) > 70 else ""))
                        else:
                            msg_row.label(text="🔮 " + content[:70] + ("..." if len(content) > 70 else ""))
                    else:
                        msg_row.label(text="👤 " + content[:70] + ("..." if len(content) > 70 else ""))
                    
                    chat_scroll.separator()
            else:
                info_row = chat_box.row()
                info_row.label(text="💭 Ready for multi-paradigm collaboration...")
        except json.JSONDecodeError:
            chat_box.label(text="🔄 Loading multi-paradigm AI...")
        
        # User Input Area with paradigm context
        input_box = layout.box()
        current_paradigm = settings.active_paradigm_tab
        paradigm_desc = "NURBS precision" if current_paradigm == 'NURBS' else "Mesh artistry"
        input_box.label(text=f"✨ Send Request to Multi-Paradigm AI ({paradigm_desc})", icon='OUTLINER_DATA_LIGHTPROBE')
        
        # Prompt input
        col = input_box.column()
        prompt_row = col.row()
        prompt_row.prop(settings, "current_prompt", text="")
        
        # Action buttons with paradigm awareness
        button_row = input_box.row(align=True)
        button_row.scale_y = 1.5
        
        if settings.is_processing:
            disabled_row = button_row.row()
            disabled_row.enabled = False
            disabled_row.operator("design.generate_design", text=f"🧠 Processing {current_paradigm}...", icon='TIME')
        else:
            # Generate button  
            generate_op = button_row.operator("design.generate_design", text="🔮 Generate", icon='PLAY')
            generate_op.is_refinement = False
            
            # Refine button
            refine_op = button_row.operator("design.generate_design", text="✨ Refine", icon='MODIFIER')
            refine_op.is_refinement = True
        
        # V32 Enhanced Processing indicator with paradigm info
        if settings.is_processing:
            proc_box = layout.box()
            proc_box.alert = True
            proc_box.label(text=f"🧠 V32 Multi-Paradigm Processing ({current_paradigm})...", icon='TIME')
            proc_box.label(text="💭 AI strategically delegating to optimal engine", icon='NONE')
            proc_box.scale_y = 0.8
    
    def _is_design_operator_running(self, context):
        """Check if the design operator is currently running."""
        # This would be implemented to check the modal operator state
        # For now, assume it's running if settings exists and is initialized
        return hasattr(context.scene, 'settings') and context.scene.settings is not None


class GenerateOperator(bpy.types.Operator):
    """
    V22 Enhanced operator to trigger AI design generation or refinement.
    
    Implements instant UI state updates and professional user feedback
    for live cognitive streaming experience.
    """
    
    bl_idname = "design.generate_design"
    bl_label = "Generate Design"
    bl_description = "Collaborate with the V22 Verifiable AI Artisan for live cognitive streaming and Shape Key animations"
    
    is_refinement: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        settings = context.scene.settings
        prompt = settings.current_prompt.strip()
        
        if not prompt:
            self.report({'WARNING'}, "Please enter a design request to begin cognitive streaming collaboration")
            return {'CANCELLED'}
        
        # V22: Instant UI state update - begin live cognitive streaming immediately
        settings.is_processing = True
        
        # Find and call the design operator
        design_ops = [op for op in context.window_manager.operators if hasattr(op, 'start_ai_processing')]
        
        if design_ops:
            design_operator = design_ops[0]
            
            # V22 Enhanced: Add user message to chat with timestamp for cognitive tracking
            try:
                current_messages = json.loads(settings.chat_messages or "[]")
                current_messages.append({
                    "role": "user",
                    "content": prompt,
                    "timestamp": time.time()
                })
                settings.chat_messages = json.dumps(current_messages)
            except Exception as e:
                logger.warning(f"V22: Chat message update failed: {e}")
            
            # Start AI cognitive streaming processing
            design_operator.start_ai_processing(prompt, self.is_refinement)
            
            # V22 Enhanced: Clear the prompt and update status for live streaming
            settings.current_prompt = ""
            settings.status_message = "V22 cognitive streaming active..."
            
            # V22: Professional user feedback with live streaming language
            action_text = "Refinement request" if self.is_refinement else "Design request"
            self.report({'INFO'}, f"✨ {action_text} sent to V22 Verifiable AI Artisan - Live streaming started")
            
            # Force UI redraw to show instant state change
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
                    
        else:
            # V22: Enhanced error message
            settings.is_processing = False
            self.report({'ERROR'}, "🔮 V22 Verifiable Artisan not active. Please activate it first.")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class ModalOperator(bpy.types.Operator):
    """Lightweight modal operator for UI responsiveness."""
    
    bl_idname = "design.modal_ui"
    bl_label = "Design Modal UI"
    bl_description = "Modal operator for responsive UI updates"
    
    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        # Handle UI updates and responsiveness
        if event.type == 'TIMER':
            # Force UI redraw for chat updates
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        
        return {'PASS_THROUGH'}


class ToggleSidebarOperator(bpy.types.Operator):
    """V32 Operator to toggle sidebar collapse/expand for full-screen viewport."""
    
    bl_idname = "design.toggle_sidebar"
    bl_label = "Toggle Sidebar"
    bl_description = "Collapse or expand the sidebar for full-screen 3D viewport"
    
    action: bpy.props.EnumProperty(
        items=[
            ('COLLAPSE', 'Collapse', 'Collapse sidebar for full-screen viewport'),
            ('EXPAND', 'Expand', 'Expand sidebar to show full controls'),
        ]
    )
    
    def execute(self, context):
        settings = context.scene.settings
        
        if self.action == 'COLLAPSE':
            settings.sidebar_collapsed = True
            self.report({'INFO'}, "V32: Sidebar collapsed - Full-screen viewport active")
        else:
            settings.sidebar_collapsed = False
            self.report({'INFO'}, "V32: Sidebar expanded - Full controls restored")
        
        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        return {'FINISHED'}


class SwitchParadigmOperator(bpy.types.Operator):
    """V32 Operator to switch between NURBS and Mesh paradigm tabs."""
    
    bl_idname = "design.switch_paradigm"
    bl_label = "Switch Paradigm"
    bl_description = "Switch between NURBS precision and Mesh artistry paradigms"
    
    paradigm: bpy.props.EnumProperty(
        items=[
            ('NURBS', 'NURBS', 'Switch to NURBS precision paradigm'),
            ('MESH', 'MESH', 'Switch to Mesh artistry paradigm'),
        ]
    )
    
    def execute(self, context):
        settings = context.scene.settings
        settings.active_paradigm_tab = self.paradigm
        
        paradigm_name = "NURBS Precision" if self.paradigm == 'NURBS' else "Mesh Artistry"
        self.report({'INFO'}, f"V32: Switched to {paradigm_name} paradigm")
        
        # Force UI redraw to show new toolset
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        return {'FINISHED'}



