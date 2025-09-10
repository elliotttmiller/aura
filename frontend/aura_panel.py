"""
Aura V14.0 Sentient Artisan Environment - Native Chat Interface
============================================================

Modern AI chat sidebar interface for real-time cognitive streaming.
This replaces the old web-based UI with a native Blender experience.

Implements Protocol 1: Architectural Purity (The Native Imperative)
"""

import bpy
import json
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class AuraChatPanel(bpy.types.Panel):
    """Main AI chat interface panel for V14.0 Sentient Artisan Environment."""
    
    bl_label = "Aura V14.0 Sentient Artisan"
    bl_idname = "AURA_PT_ChatPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Design'
    bl_order = 0
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.aura_settings
        
        # Header with version and status
        header_box = layout.box()
        header_box.label(text="🧠 Sentient Artisan V14.0", icon='LIGHT')
        
        status_text = "Processing..." if settings.is_processing else "Ready"
        status_icon = 'TIME' if settings.is_processing else 'CHECKMARK'
        header_box.label(text=f"Status: {status_text}", icon=status_icon)
        
        # Start/Stop Sentient Operator
        if not self._is_sentient_operator_running(context):
            layout.operator("aura.sentient_operator", text="🚀 Activate Sentient Mode", icon='PLAY')
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
        generate_op = button_row.operator("aura.generate_design", text="🎨 Generate", icon='PLAY')
        generate_op.is_refinement = False
        
        # Refine button (secondary action)
        if not settings.is_processing:
            refine_op = button_row.operator("aura.generate_design", text="✨ Refine", icon='MODIFIER')
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
        
        # Ring specifications
        specs_col.prop(settings, "ring_size", text="Ring Size")
        specs_col.prop(settings, "metal_type", text="Metal")
        specs_col.prop(settings, "stone_shape", text="Stone Shape")
        specs_col.prop(settings, "stone_carat", text="Stone Carat")
        
        # Technique selection (V14.0 enhancement)
        specs_col.separator()
        specs_col.label(text="💎 Preferred Setting Technique")
        specs_col.prop(settings, "preferred_technique", text="")
    
    def _is_sentient_operator_running(self, context):
        """Check if the sentient operator is currently running."""
        # This would be implemented to check the modal operator state
        # For now, assume it's running if aura_settings exists and is initialized
        return hasattr(context.scene, 'aura_settings') and context.scene.aura_settings is not None


class AuraGenerateOperator(bpy.types.Operator):
    """Operator to trigger AI design generation or refinement."""
    
    bl_idname = "aura.generate_design"
    bl_label = "Generate Design"
    bl_description = "Generate or refine a jewelry design using AI"
    
    is_refinement: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        settings = context.scene.aura_settings
        prompt = settings.current_prompt.strip()
        
        if not prompt:
            self.report({'WARNING'}, "Please enter a design request")
            return {'CANCELLED'}
        
        # Find and call the sentient operator
        sentient_ops = [op for op in context.window_manager.operators if hasattr(op, 'start_ai_processing')]
        
        if sentient_ops:
            sentient_operator = sentient_ops[0]
            
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
            sentient_operator.start_ai_processing(prompt, self.is_refinement)
            
            # Clear the prompt
            settings.current_prompt = ""
            
            action_text = "Refinement" if self.is_refinement else "Generation"
            self.report({'INFO'}, f"{action_text} started: {prompt}")
        else:
            self.report({'ERROR'}, "Sentient Operator not active. Please activate Sentient Mode first.")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class AuraModalOperator(bpy.types.Operator):
    """Lightweight modal operator for UI responsiveness."""
    
    bl_idname = "aura.modal_ui"
    bl_label = "Aura Modal UI"
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


# Enhanced settings for V14.0
class AuraV14Settings(bpy.types.PropertyGroup):
    """Extended settings for V14.0 Sentient Artisan Environment."""
    
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
    
    # Technical specifications
    ring_size: bpy.props.FloatProperty(
        name="Ring Size (US)",
        description="Ring size in US standard",
        default=7.0,
        min=1.0,
        max=20.0
    )
    
    metal_type: bpy.props.EnumProperty(
        name="Metal Type",
        description="Type of metal for the ring",
        items=[
            ('GOLD', 'Gold', 'Gold metal'),
            ('PLATINUM', 'Platinum', 'Platinum metal'),
            ('SILVER', 'Silver', 'Silver metal'),
            ('TITANIUM', 'Titanium', 'Titanium metal'),
        ],
        default='GOLD'
    )
    
    stone_shape: bpy.props.EnumProperty(
        name="Stone Shape",
        description="Shape of the primary stone",
        items=[
            ('ROUND', 'Round', 'Round brilliant cut'),
            ('PRINCESS', 'Princess', 'Princess/square cut'),
            ('EMERALD', 'Emerald', 'Emerald/rectangular cut'),
            ('OVAL', 'Oval', 'Oval cut'),
            ('PEAR', 'Pear', 'Pear/teardrop cut'),
        ],
        default='ROUND'
    )
    
    stone_carat: bpy.props.FloatProperty(
        name="Stone Carat",
        description="Weight of the primary stone in carats",
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    # V14.0 Professional technique selection
    preferred_technique: bpy.props.EnumProperty(
        name="Setting Technique",
        description="Preferred professional setting technique",
        items=[
            ('AUTO', 'AI Selects', 'Let AI choose the best technique'),
            ('CLASSIC_PRONG', 'Classic Prong', 'Traditional prong setting'),
            ('BEZEL', 'Bezel', 'Bezel setting with metal surround'),
            ('TENSION', 'Tension', 'Modern tension setting'),
            ('PAVE', 'Pave', 'Pave setting with multiple small stones'),
        ],
        default='AUTO'
    )


def register():
    bpy.utils.register_class(AuraV14Settings)
    bpy.types.Scene.aura_settings = bpy.props.PointerProperty(type=AuraV14Settings)


def unregister():
    if hasattr(bpy.types.Scene, 'aura_settings'):
        del bpy.types.Scene.aura_settings
    bpy.utils.unregister_class(AuraV14Settings)
