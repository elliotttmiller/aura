"""
V20.0 Design Engine - Native Chat Interface
===========================================

Modern AI chat sidebar interface for real-time cognitive streaming.
This provides a native Blender experience for procedural asset generation.

Implements Protocol 1: Architectural Purity (The Native Imperative)
"""

import bpy
import json
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ChatPanel(bpy.types.Panel):
    """
    V24 Enhanced AI chat interface panel for Autonomous Design Engine.
    
    Implements Pillar 3: Honing the Sentient Cockpit with perfect state representation,
    clear error display, and professional tooltips reflecting collaboration with an autonomous agent.
    """
    
    bl_label = "🤖 Aura V24 Autonomous Design Engine"
    bl_idname = "DESIGN_PT_ChatPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aura'
    bl_order = 0
    bl_description = "Collaborate with the V24 Autonomous Design Engine - a sentient AI that creates 3D models through natural conversation"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.settings
        
        # V24 Header with enhanced version and autonomous status
        header_box = layout.box()
        header_box.label(text="🤖 Aura V24 Autonomous Engine", icon='TOOL_SETTINGS')
        
        # V24 Enhanced status representation with color coding
        if settings.is_processing:
            status_text = "🧠 Autonomous Agent Thinking..."
            status_icon = 'TIME'
            header_box.alert = True  # Visual emphasis during processing
        else:
            status_text = "✅ Ready for Collaboration"
            status_icon = 'CHECKMARK'
            header_box.alert = False
        
        status_row = header_box.row()
        status_row.label(text=f"Status: {status_text}", icon=status_icon)
        
        # Start/Stop Design Operator with V24 language
        if not self._is_design_operator_running(context):
            activate_op = layout.operator("design.sentient_operator", text="🚀 Activate Autonomous Engine", icon='PLAY')
            activate_op.bl_description = "Start the V24 Autonomous Design Engine for AI collaboration"
            layout.separator()
            layout.label(text="💡 Activate the engine to begin creating with AI", icon='INFO')
            return
        
        # V24 Enhanced Chat Messages Display with error color coding
        chat_box = layout.box()
        chat_box.label(text="💬 Autonomous Agent Conversation", icon='COMMUNITY')
        
        # Display chat messages with V24 enhanced formatting
        try:
            messages = json.loads(settings.chat_messages or "[]")
            
            if messages:
                # Create scrollable chat area
                chat_scroll = chat_box.column(align=True)
                chat_scroll.scale_y = 0.8
                
                # Show last 10 messages to prevent UI overflow
                recent_messages = messages[-10:] if len(messages) > 10 else messages
                
                for msg in recent_messages:
                    msg_row = chat_scroll.row(align=True)
                    
                    # V24 Enhanced message formatting with error detection
                    content = msg['content']
                    is_error = content.startswith('❌') or 'error' in content.lower()
                    
                    if msg['role'] == 'system':
                        msg_row.label(text="🔧 " + content[:80] + ("..." if len(content) > 80 else ""))
                    elif msg['role'] == 'assistant':
                        if is_error:
                            # V24: Red coloring for error messages
                            error_row = msg_row.row()
                            error_row.alert = True
                            error_row.label(text="🧠 " + content[:80] + ("..." if len(content) > 80 else ""))
                        else:
                            msg_row.label(text="🧠 " + content[:80] + ("..." if len(content) > 80 else ""))
                    else:
                        msg_row.label(text="👤 " + content[:80] + ("..." if len(content) > 80 else ""))
                    
                    chat_scroll.separator()
            else:
                info_row = chat_box.row()
                info_row.label(text="💭 Ready to collaborate with your autonomous AI designer...")
        except json.JSONDecodeError:
            chat_box.label(text="🔄 Loading conversation history...")
        
        # V24 Enhanced User Input Area with professional tooltips
        input_box = layout.box()
        input_box.label(text="✨ Send Request to AI Designer", icon='OUTLINER_DATA_LIGHTPROBE')
        
        # Large text input for prompts with V24 tooltip
        col = input_box.column()
        prompt_row = col.row()
        prompt_row.prop(settings, "current_prompt", text="")
        
        # V24 Enhanced Action buttons with professional descriptions
        button_row = input_box.row(align=True)
        button_row.scale_y = 1.5
        
        # Generate button (primary action) with V24 instant disable/enable
        if settings.is_processing:
            # V24: Button disabled instantly when processing starts
            disabled_row = button_row.row()
            disabled_row.enabled = False
            disabled_row.operator("design.generate_design", text="🧠 Thinking...", icon='TIME')
        else:
            # V24 Enhanced generate button with professional tooltip
            generate_op = button_row.operator("design.generate_design", text="🎨 Generate", icon='PLAY')
            generate_op.is_refinement = False
            
            # Refine button (secondary action) with V24 tooltip
            refine_op = button_row.operator("design.generate_design", text="✨ Refine", icon='MODIFIER')
            refine_op.is_refinement = True
        
        # V24 Enhanced Processing indicator with transparency
        if settings.is_processing:
            proc_box = layout.box()
            proc_box.alert = True
            proc_box.label(text="🤖 Autonomous Agent Working...", icon='TIME')
            proc_box.label(text="💭 AI analyzing your request", icon='NONE')
            proc_box.scale_y = 0.8
        
        # V24 Enhanced Technical specifications with professional tooltips
        specs_box = layout.box()
        specs_box.label(text="⚙️ Autonomous Agent Configuration", icon='PREFERENCES')
        
        specs_col = specs_box.column(align=True)
        specs_col.scale_y = 0.9
        
        # V24 Enhanced Mesh Quality Control with professional descriptions
        quality_box = specs_col.box()
        quality_box.label(text="🔬 V24 Mesh Quality Control", icon='MESH_GRID')
        quality_col = quality_box.column(align=True)
        
        # Mesh quality slider with V24 enhanced labels and tooltips
        quality_row = quality_col.row()
        quality_row.prop(settings, "mesh_quality", text="Resolution")
        
        # V24 Quality indicator with professional descriptions
        mesh_quality = settings.mesh_quality
        if mesh_quality <= 32:
            quality_label = "🟡 Low Quality (Fast) - Rapid prototyping"
        elif mesh_quality <= 64:
            quality_label = "🟠 Medium Quality (Balanced) - Production ready"
        elif mesh_quality <= 128:
            quality_label = "🔵 High Quality (Detailed) - Professional finish"
        else:
            quality_label = "🟣 Ultra Quality (Slow) - Maximum precision"
            
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
        
        # V24 Enhanced technique selection with autonomous agent language
        specs_col.separator()
        technique_label = specs_col.row()
        technique_label.label(text="🧠 AI Generation Strategy")
        technique_row = specs_col.row()
        technique_row.prop(settings, "preferred_technique", text="")
    
    def _is_design_operator_running(self, context):
        """Check if the design operator is currently running."""
        # This would be implemented to check the modal operator state
        # For now, assume it's running if settings exists and is initialized
        return hasattr(context.scene, 'settings') and context.scene.settings is not None


class GenerateOperator(bpy.types.Operator):
    """
    V24 Enhanced operator to trigger AI design generation or refinement.
    
    Implements instant UI state updates and professional user feedback
    as specified in Protocol 10: Holistic Integration & Autonomy.
    """
    
    bl_idname = "design.generate_design"
    bl_label = "Generate Design"
    bl_description = "Collaborate with the autonomous AI designer to generate or refine procedural assets"
    
    is_refinement: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        settings = context.scene.settings
        prompt = settings.current_prompt.strip()
        
        if not prompt:
            self.report({'WARNING'}, "Please enter a design request to collaborate with the AI")
            return {'CANCELLED'}
        
        # V24: Instant UI state update - disable processing immediately
        settings.is_processing = True
        
        # Find and call the design operator
        design_ops = [op for op in context.window_manager.operators if hasattr(op, 'start_ai_processing')]
        
        if design_ops:
            design_operator = design_ops[0]
            
            # V24 Enhanced: Add user message to chat with timestamp
            try:
                current_messages = json.loads(settings.chat_messages or "[]")
                current_messages.append({
                    "role": "user",
                    "content": prompt,
                    "timestamp": time.time()
                })
                settings.chat_messages = json.dumps(current_messages)
            except Exception as e:
                logger.warning(f"V24: Chat message update failed: {e}")
            
            # Start AI processing
            design_operator.start_ai_processing(prompt, self.is_refinement)
            
            # V24 Enhanced: Clear the prompt and update status
            settings.current_prompt = ""
            settings.status_message = "Autonomous agent thinking..."
            
            # V24: Professional user feedback
            action_text = "Refinement request" if self.is_refinement else "Design request"
            self.report({'INFO'}, f"✨ {action_text} sent to autonomous AI designer")
            
            # Force UI redraw to show instant state change
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
                    
        else:
            # V24: Enhanced error message
            settings.is_processing = False
            self.report({'ERROR'}, "🤖 Autonomous Design Engine not active. Please activate it first.")
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



