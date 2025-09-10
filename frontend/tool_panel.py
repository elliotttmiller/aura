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
    V22 Verifiable Artisan Chat Interface Panel
    
    Live cognitive streaming interface showcasing AI's multi-step thought process.
    Features real-time updates, clear error display, and professional tooltips
    for true AI collaboration transparency.
    """
    
    bl_label = "🔮 Aura V22 Verifiable Artisan"
    bl_idname = "DESIGN_PT_ChatPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aura'
    bl_order = 0
    bl_description = "V22 Verifiable Artisan - Live AI cognitive streaming with real-time Shape Key animations and complete transparency"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.settings
        
        # V22 Header with live cognitive streaming status
        header_box = layout.box()
        header_box.label(text="🔮 Aura V22 Verifiable Artisan", icon='TOOL_SETTINGS')
        
        # V22 Enhanced status with cognitive streaming indicators
        if settings.is_processing:
            status_text = "🧠 Live Cognitive Streaming..."
            status_icon = 'TIME'
            header_box.alert = True  # Visual emphasis during processing
        else:
            status_text = "✅ Ready for AI Collaboration"
            status_icon = 'CHECKMARK'
            header_box.alert = False
        
        status_row = header_box.row()
        status_row.label(text=f"Status: {status_text}", icon=status_icon)
        
        # Start/Stop Design Operator with V22 language
        if not self._is_design_operator_running(context):
            activate_op = layout.operator("design.sentient_operator", text="🔮 Activate V22 Verifiable Artisan", icon='PLAY')
            activate_op.bl_description = "Start the V22 Verifiable Artisan for live cognitive streaming and Shape Key animations"
            layout.separator()
            layout.label(text="💡 Activate to begin verifiable AI collaboration", icon='INFO')
            return
        
        # V22 Enhanced Chat Messages Display with cognitive streaming visibility
        chat_box = layout.box()
        chat_box.label(text="🧠 Live Cognitive Streaming", icon='COMMUNITY')
        
        # Display chat messages with V22 enhanced cognitive streaming formatting
        try:
            messages = json.loads(settings.chat_messages or "[]")
            
            if messages:
                # Create scrollable chat area for live streaming
                chat_scroll = chat_box.column(align=True)
                chat_scroll.scale_y = 0.8
                
                # Show last 10 messages to prevent UI overflow while preserving cognitive flow
                recent_messages = messages[-10:] if len(messages) > 10 else messages
                
                for msg in recent_messages:
                    msg_row = chat_scroll.row(align=True)
                    
                    # V22 Enhanced message formatting with cognitive streaming indicators
                    content = msg['content']
                    is_error = content.startswith('❌') or 'error' in content.lower()
                    is_cognitive_step = any(indicator in content for indicator in ['🧠', '🔍', '⚡', '📐', '✅', '🔧', '🏗️', '✨'])
                    
                    if msg['role'] == 'system':
                        msg_row.label(text="🔧 " + content[:80] + ("..." if len(content) > 80 else ""))
                    elif msg['role'] == 'assistant':
                        if is_error:
                            # V22: Red coloring for error messages
                            error_row = msg_row.row()
                            error_row.alert = True
                            error_row.label(text="❌ " + content[:80] + ("..." if len(content) > 80 else ""))
                        elif is_cognitive_step:
                            # V22: Highlight cognitive streaming steps
                            cognitive_row = msg_row.row()
                            cognitive_row.label(text=content[:80] + ("..." if len(content) > 80 else ""))
                        else:
                            msg_row.label(text="🔮 " + content[:80] + ("..." if len(content) > 80 else ""))
                    else:
                        msg_row.label(text="👤 " + content[:80] + ("..." if len(content) > 80 else ""))
                    
                    chat_scroll.separator()
            else:
                info_row = chat_box.row()
                info_row.label(text="💭 Ready for live cognitive streaming collaboration...")
        except json.JSONDecodeError:
            chat_box.label(text="🔄 Loading cognitive stream...")
        
        # V22 Enhanced User Input Area with verifiable artisan tooltips
        input_box = layout.box()
        input_box.label(text="✨ Send Request to V22 AI Artisan", icon='OUTLINER_DATA_LIGHTPROBE')
        
        # Large text input for prompts with V24 tooltip
        col = input_box.column()
        prompt_row = col.row()
        prompt_row.prop(settings, "current_prompt", text="")
        
        # V22 Enhanced Action buttons with verifiable artisan descriptions
        button_row = input_box.row(align=True)
        button_row.scale_y = 1.5
        
        # Generate button (primary action) with V22 instant disable/enable
        if settings.is_processing:
            # V22: Button disabled instantly when cognitive streaming starts
            disabled_row = button_row.row()
            disabled_row.enabled = False
            disabled_row.operator("design.generate_design", text="🧠 Cognitive Streaming...", icon='TIME')
        else:
            # V22 Enhanced generate button with verifiable artisan tooltip
            generate_op = button_row.operator("design.generate_design", text="🔮 Generate", icon='PLAY')
            generate_op.is_refinement = False
            
            # Refine button (secondary action) with V22 tooltip
            refine_op = button_row.operator("design.generate_design", text="✨ Refine", icon='MODIFIER')
            refine_op.is_refinement = True
        
        # V22 Enhanced Processing indicator with live cognitive streaming
        if settings.is_processing:
            proc_box = layout.box()
            proc_box.alert = True
            proc_box.label(text="🧠 V22 Live Cognitive Streaming...", icon='TIME')
            proc_box.label(text="💭 AI processing with full transparency", icon='NONE')
            proc_box.scale_y = 0.8
        
        # V22 Enhanced Technical specifications with verifiable artisan tooltips
        specs_box = layout.box()
        specs_box.label(text="⚙️ V22 Verifiable Configuration", icon='PREFERENCES')
        
        specs_col = specs_box.column(align=True)
        specs_col.scale_y = 0.9
        
        # V22 Enhanced Mesh Quality Control with Shape Key animation descriptions
        quality_box = specs_col.box()
        quality_box.label(text="🔬 V22 Mesh Quality Control", icon='MESH_GRID')
        quality_col = quality_box.column(align=True)
        
        # Mesh quality slider with V22 enhanced labels and Shape Key tooltips
        quality_row = quality_col.row()
        quality_row.prop(settings, "mesh_quality", text="Resolution")
        
        # V22 Quality indicator with Shape Key animation descriptions
        mesh_quality = settings.mesh_quality
        if mesh_quality <= 32:
            quality_label = "🟡 Low Quality (Fast) - Basic Shape Key animations"
        elif mesh_quality <= 64:
            quality_label = "🟠 Medium Quality (Balanced) - Smooth Shape Key transitions"
        elif mesh_quality <= 128:
            quality_label = "🔵 High Quality (Detailed) - Professional Shape Key animations"
        else:
            quality_label = "🟣 Ultra Quality (Slow) - Ultra-smooth Shape Key transitions"
            
        quality_col.label(text=quality_label)
        quality_col.separator()
        
        # V24 Enhanced asset specifications with professional tooltips
        asset_row = specs_col.row()
        asset_row.prop(settings, "asset_size", text="Asset Scale (mm)")
        
        material_row = specs_col.row()
        material_row.prop(settings, "material_type", text="Material Type")
        
        feature_row = specs_col.row()
        feature_row.prop(settings, "feature_shape", text="Primary Feature")
        
        scale_row = specs_col.row()
        scale_row.prop(settings, "feature_scale", text="Feature Detail")
        
        # V22 Enhanced technique selection with verifiable artisan language
        specs_col.separator()
        technique_label = specs_col.row()
        technique_label.label(text="🧠 V22 AI Strategy")
        technique_row = specs_col.row()
        technique_row.prop(settings, "preferred_technique", text="")
    
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



