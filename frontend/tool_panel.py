"""
Universal Design Engine V20.0 - Native Chat Interface
====================================================

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


class UniversalChatPanel(bpy.types.Panel):
    """Main AI chat interface panel for V20.0 Universal Design Engine."""
    
    bl_label = "Universal Design Engine V20.0"
    bl_idname = "TOOL_PT_ChatPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Design'
    bl_order = 0
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_settings
        
        # Header with version and status
        header_box = layout.box()
        header_box.label(text="🔧 Universal Engine V20.0", icon='TOOL_SETTINGS')
        
        status_text = "Processing..." if settings.is_processing else "Ready"
        status_icon = 'TIME' if settings.is_processing else 'CHECKMARK'
        header_box.label(text=f"Status: {status_text}", icon=status_icon)
        
        # Start/Stop Universal Operator
        if not self._is_universal_operator_running(context):
            layout.operator("tool.universal_operator", text="🚀 Activate Design Engine", icon='PLAY')
            layout.separator()
            return
        
        # Chat Messages Display
        chat_box = layout.box()
        chat_box.label(text="💬 AI Conversation", icon='COMMUNITY')
        
        # Display chat messages
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
                    
                    if msg['role'] == 'system':
                        msg_row.label(text="🔧 " + msg['content'][:80] + ("..." if len(msg['content']) > 80 else ""))
                    elif msg['role'] == 'assistant':
                        msg_row.label(text="🧠 " + msg['content'][:80] + ("..." if len(msg['content']) > 80 else ""))
                    else:
                        msg_row.label(text="👤 " + msg['content'][:80] + ("..." if len(msg['content']) > 80 else ""))
                    
                    chat_scroll.separator()
            else:
                chat_box.label(text="Start a conversation below...")
        except json.JSONDecodeError:
            chat_box.label(text="Chat history loading...")
        
        # User Input Area
        input_box = layout.box()
        input_box.label(text="✨ Design Request", icon='OUTLINER_DATA_LIGHTPROBE')
        
        # Large text input for prompts
        col = input_box.column()
        col.prop(settings, "current_prompt", text="")
        
        # Action buttons
        button_row = input_box.row(align=True)
        button_row.scale_y = 1.5
        
        # Generate button (primary action)
        generate_op = button_row.operator("tool.generate_design", text="🎨 Generate", icon='PLAY')
        generate_op.is_refinement = False
        
        # Refine button (secondary action)
        if not settings.is_processing:
            refine_op = button_row.operator("tool.generate_design", text="✨ Refine", icon='MODIFIER')
            refine_op.is_refinement = True
        
        # Processing indicator
        if settings.is_processing:
            proc_box = layout.box()
            proc_box.label(text="🔄 AI is thinking and creating...", icon='TIME')
            proc_box.scale_y = 0.8
        
        # Technical specifications (collapsible)
        specs_box = layout.box()
        specs_box.label(text="⚙️ Technical Specifications", icon='PREFERENCES')
        
        specs_col = specs_box.column(align=True)
        specs_col.scale_y = 0.9
        
        # V20.0 Mesh Quality Control - Revolutionary Marching Cubes Resolution
        quality_box = specs_col.box()
        quality_box.label(text="🔬 V20.0 Mesh Quality Control", icon='MESH_GRID')
        quality_col = quality_box.column(align=True)
        
        # Mesh quality slider with intuitive labels
        quality_col.prop(settings, "mesh_quality", text="Resolution")
        
        # Quality indicator
        mesh_quality = settings.mesh_quality
        if mesh_quality <= 32:
            quality_label = "🟡 Low Quality (Fast)"
        elif mesh_quality <= 64:
            quality_label = "🟠 Medium Quality (Balanced)"
        elif mesh_quality <= 128:
            quality_label = "🔵 High Quality (Detailed)"
        else:
            quality_label = "🟣 Ultra Quality (Slow)"
            
        quality_col.label(text=quality_label)
        quality_col.separator()
        
        # Asset specifications - Universal parameters
        specs_col.prop(settings, "asset_size", text="Asset Scale")
        specs_col.prop(settings, "material_type", text="Material")
        specs_col.prop(settings, "feature_shape", text="Feature Shape")
        specs_col.prop(settings, "feature_scale", text="Feature Scale")
        
        # Technique selection (V20.0 enhancement)
        specs_col.separator()
        specs_col.label(text="⚙️ Preferred Generation Technique")
        specs_col.prop(settings, "preferred_technique", text="")
    
    def _is_universal_operator_running(self, context):
        """Check if the universal operator is currently running."""
        # This would be implemented to check the modal operator state
        # For now, assume it's running if universal_settings exists and is initialized
        return hasattr(context.scene, 'universal_settings') and context.scene.universal_settings is not None


class UniversalGenerateOperator(bpy.types.Operator):
    """Operator to trigger AI design generation or refinement."""
    
    bl_idname = "tool.generate_design"
    bl_label = "Generate Design"
    bl_description = "Generate or refine a procedural asset design using AI"
    
    is_refinement: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        settings = context.scene.universal_settings
        prompt = settings.current_prompt.strip()
        
        if not prompt:
            self.report({'WARNING'}, "Please enter a design request")
            return {'CANCELLED'}
        
        # Find and call the universal operator
        universal_ops = [op for op in context.window_manager.operators if hasattr(op, 'start_ai_processing')]
        
        if universal_ops:
            universal_operator = universal_ops[0]
            
            # Add user message to chat
            try:
                current_messages = json.loads(settings.chat_messages or "[]")
                current_messages.append({
                    "role": "user",
                    "content": prompt,
                    "timestamp": time.time()
                })
                settings.chat_messages = json.dumps(current_messages)
            except:
                pass
            
            # Start AI processing
            universal_operator.start_ai_processing(prompt, self.is_refinement)
            
            # Clear the prompt
            settings.current_prompt = ""
            
            action_text = "Refinement" if self.is_refinement else "Generation"
            self.report({'INFO'}, f"{action_text} started: {prompt}")
        else:
            self.report({'ERROR'}, "Universal Design Engine not active. Please activate the Design Engine first.")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class UniversalModalOperator(bpy.types.Operator):
    """Lightweight modal operator for UI responsiveness."""
    
    bl_idname = "tool.modal_ui"
    bl_label = "Universal Modal UI"
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


# Enhanced settings for V20.0
class UniversalEngineSettings(bpy.types.PropertyGroup):
    """Extended settings for V20.0 Universal Design Engine."""
    
    # Core system properties
    is_processing: bpy.props.BoolProperty(
        name="Is Processing",
        description="Whether AI is currently processing",
        default=False
    )
    
    chat_messages: bpy.props.StringProperty(
        name="Chat Messages",
        description="JSON string containing chat history",
        default=""
    )
    
    current_prompt: bpy.props.StringProperty(
        name="Design Request",
        description="Current design request from user",
        default="",
        maxlen=512
    )
    
    # V20.0 Mesh Quality Control with 8GB VRAM optimization
    mesh_quality: bpy.props.IntProperty(
        name="Mesh Resolution",
        description="Marching Cubes resolution for implicit surface extraction",
        default=64,
        min=16,
        max=256,
        step=16
    )
    
    # Universal asset specifications
    asset_size: bpy.props.FloatProperty(
        name="Asset Scale",
        description="Overall scale factor for the generated asset",
        default=1.0,
        min=0.1,
        max=20.0
    )
    
    material_type: bpy.props.EnumProperty(
        name="Material Type",
        description="Type of material for the asset",
        items=[
            ('METAL', 'Metal', 'Metallic material'),
            ('CERAMIC', 'Ceramic', 'Ceramic material'),
            ('PLASTIC', 'Plastic', 'Plastic material'),
            ('ORGANIC', 'Organic', 'Organic/wood material'),
        ],
        default='METAL'
    )
    
    feature_shape: bpy.props.EnumProperty(
        name="Feature Shape",
        description="Shape of the primary feature",
        items=[
            ('ROUND', 'Round', 'Circular feature'),
            ('SQUARE', 'Square', 'Square/rectangular feature'),
            ('ORGANIC', 'Organic', 'Organic/curved feature'),
            ('GEOMETRIC', 'Geometric', 'Geometric/angular feature'),
            ('TWISTED', 'Twisted', 'Twisted/spiral feature'),
        ],
        default='ROUND'
    )
    
    feature_scale: bpy.props.FloatProperty(
        name="Feature Scale",
        description="Scale of the primary feature relative to asset",
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    # V20.0 Professional technique selection
    preferred_technique: bpy.props.EnumProperty(
        name="Generation Technique",
        description="Preferred procedural generation technique",
        items=[
            ('AUTO', 'AI Selects', 'Let AI choose the best technique'),
            ('IMPLICIT', 'Implicit Functions', 'Neural implicit function generation'),
            ('PROCEDURAL', 'Procedural', 'Rule-based procedural generation'),
            ('HYBRID', 'Hybrid', 'Combined implicit and procedural techniques'),
        ],
        default='AUTO'
    )


def register():
    bpy.utils.register_class(UniversalEngineSettings)
    bpy.types.Scene.universal_settings = bpy.props.PointerProperty(type=UniversalEngineSettings)


def unregister():
    if hasattr(bpy.types.Scene, 'universal_settings'):
        del bpy.types.Scene.universal_settings
    bpy.utils.unregister_class(UniversalEngineSettings)
