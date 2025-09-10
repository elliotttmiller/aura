"""
V20.0 Design Engine - Master Modal Operator
===========================================

The core asynchronous modal operator that manages the AI conversation 
and real-time 3D implicit surface updates with smooth Shape Key transitions.

Implements Protocol 2: Asynchronous Supremacy (The Non-Blocking Mandate)
Revolutionary implicit function-based cognitive streaming architecture.
"""

import bpy
import threading
import queue
import time
import json
import logging
from typing import Dict, Any, Optional

from .backend.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentientOperator(bpy.types.Operator):
    """Master Modal Operator for V20.0 Design Engine."""
    
    bl_idname = "design.sentient_operator"
    bl_label = "Design Engine V20.0 Operator"
    bl_description = "Master asynchronous operator for implicit function-based AI design"
    
    def __init__(self):
        self.orchestrator = None
        self.worker_thread = None
        self.message_queue = queue.Queue()
        self.is_running = False
        self.timer_handle = None
        self.current_shape_key_animation = None
        
    def execute(self, context):
        """Start the design operator in modal mode."""
        logger.info("Starting Design Engine V20.0")
        
        # Initialize the orchestrator
        self.orchestrator = Orchestrator()
        
        # Start modal operation
        context.window_manager.modal_handler_add(self)
        self.is_running = True
        
        # Register timer for real-time updates
        self.timer_handle = bpy.app.timers.register(
            self.process_messages, 
            first_interval=0.1, 
            persistent=True
        )
        
        # Update UI to show we're active
        context.scene.settings.is_processing = False
        context.scene.settings.chat_messages = json.dumps([
            {"role": "system", "content": "Design Engine V20.0 activated. Revolutionary implicit function-based AI collaboration ready."}
        ])
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        """Modal handler for continuous operation."""
        
        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}
            
        # Continue running
        return {'PASS_THROUGH'}
    
    def process_messages(self):
        """Timer callback to process messages from worker thread."""
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                self.handle_message(message)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error processing messages: {e}")
        
        # Return interval for next call
        return 0.1 if self.is_running else None
    
    def handle_message(self, message: Dict[str, Any]):
        """Handle different types of messages from the worker thread."""
        msg_type = message.get('type')
        
        if msg_type == 'chat_update':
            self.update_chat_ui(message['content'])
        elif msg_type == 'shape_key_created':
            self.animate_shape_key(message['object_name'], message['shape_key_name'])
        elif msg_type == 'processing_complete':
            self.handle_processing_complete(message)
        elif msg_type == 'error':
            self.handle_error(message['error'])
    
    def update_chat_ui(self, content: str):
        """Update the chat UI with new content."""
        try:
            scene = bpy.context.scene
            current_messages = json.loads(scene.settings.chat_messages or "[]")
            current_messages.append({
                "role": "assistant", 
                "content": content, 
                "timestamp": time.time()
            })
            scene.settings.chat_messages = json.dumps(current_messages)
            
            # Force UI redraw
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        except Exception as e:
            logger.error(f"Error updating chat UI: {e}")
    
    def animate_shape_key(self, object_name: str, shape_key_name: str):
        """Animate Shape Key from 0 to 1 for smooth transitions."""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or not obj.data.shape_keys:
                return
            
            shape_key = obj.data.shape_keys.key_blocks.get(shape_key_name)
            if not shape_key:
                return
            
            logger.info(f"Starting V20.0 Implicit Shape Key animation for {shape_key_name}")
            
            # Start animation from 0 to 1 over 2 seconds
            self.current_shape_key_animation = {
                'object': obj,
                'shape_key': shape_key,
                'start_time': time.time(),
                'duration': 2.0,
                'start_value': 0.0,
                'end_value': 1.0
            }
            
            # Register animation timer
            bpy.app.timers.register(self.update_shape_key_animation, first_interval=0.02)
            
        except Exception as e:
            logger.error(f"Error starting Shape Key animation: {e}")
    
    def update_shape_key_animation(self):
        """Update Shape Key animation progress."""
        if not self.current_shape_key_animation:
            return None
            
        animation = self.current_shape_key_animation
        elapsed = time.time() - animation['start_time']
        progress = min(elapsed / animation['duration'], 1.0)
        
        # Smooth interpolation
        smooth_progress = 3 * progress**2 - 2 * progress**3
        current_value = animation['start_value'] + (animation['end_value'] - animation['start_value']) * smooth_progress
        
        animation['shape_key'].value = current_value
        
        # Force viewport update
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        # Continue animation or finish
        if progress >= 1.0:
            logger.info("V20.0 Implicit Surface Shape Key animation completed")
            self.current_shape_key_animation = None
            return None
        else:
            return 0.02  # 50 FPS animation
    
    def start_ai_processing(self, user_prompt: str, is_refinement: bool = False):
        """Start AI processing in worker thread."""
        if self.worker_thread and self.worker_thread.is_alive():
            logger.warning("AI processing already in progress")
            return
        
        # Update UI to show processing state
        bpy.context.scene.settings.is_processing = True
        self.update_chat_ui(f"Processing: {user_prompt}")
        
        # Start worker thread
        self.worker_thread = threading.Thread(
            target=self.ai_worker_thread,
            args=(user_prompt, is_refinement),
            daemon=True
        )
        self.worker_thread.start()
    
    def ai_worker_thread(self, user_prompt: str, is_refinement: bool):
        """
        V24 Enhanced AI worker thread with comprehensive error handling.
        
        Master try-catch block ensures all exceptions are caught and gracefully
        handled as mandated by Protocol 10: Holistic Integration & Autonomy.
        """
        try:
            logger.info(f"V24: AI worker thread started for: {user_prompt}")
            
            # Send initial status update
            self.message_queue.put({
                'type': 'chat_update',
                'content': f"🧠 AI Master Planner analyzing: {user_prompt}"
            })
            
            # Stage 1: AI cognition and blueprint generation
            self.message_queue.put({
                'type': 'chat_update', 
                'content': "⚡ Contacting AI Architect..."
            })
            
            if is_refinement:
                result = self.orchestrator.refine_design(user_prompt)
            else:
                result = self.orchestrator.generate_design(user_prompt)
            
            # Stage 2: Blueprint validation
            if result.get('success'):
                self.message_queue.put({
                    'type': 'chat_update',
                    'content': "✅ Validating AI Blueprint..."
                })
                
                # Stage 3: Blender Engine execution
                self.message_queue.put({
                    'type': 'chat_update',
                    'content': "🔧 Launching Blender Engine..."
                })
                
                # Stage 4: Final polish and completion
                self.message_queue.put({
                    'type': 'chat_update',
                    'content': "✨ Applying Final Polish..."
                })
            
            # Send completion message
            self.message_queue.put({
                'type': 'processing_complete',
                'result': result
            })
            
        except Exception as e:
            # V24 Master exception handler - catches ALL possible failures
            logger.error(f"V24: AI worker thread master exception handler: {e}")
            
            # Determine appropriate user-friendly error message
            if "validation" in str(e).lower():
                error_msg = f"🔍 Blueprint Validation Error: {str(e)}"
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                error_msg = f"🌐 Network Communication Error: Unable to reach AI Master Planner"
            elif "timeout" in str(e).lower():
                error_msg = f"⏱️ Processing Timeout: AI Master Planner taking too long to respond"
            else:
                error_msg = f"⚠️ Autonomous Agent Decision: Process halted due to unexpected condition"
            
            # Stream clear error message to UI
            self.message_queue.put({
                'type': 'error',
                'error': error_msg,
                'technical_details': str(e)
            })
            
            logger.info("V24: Master exception handler completed - user notified")
    
    def handle_processing_complete(self, message: Dict[str, Any]):
        """Handle completion of AI processing."""
        result = message['result']
        
        # Update UI
        bpy.context.scene.settings.is_processing = False
        
        if result.get('success'):
            self.update_chat_ui("Design completed successfully!")
            
            # If a 3D model was created, trigger shape key animation
            if result.get('object_name'):
                self.message_queue.put({
                    'type': 'shape_key_created',
                    'object_name': result['object_name'],
                    'shape_key_name': result.get('shape_key_name', 'Modification')
                })
        else:
            self.update_chat_ui(f"Error: {result.get('error', 'Unknown error')}")
    
    def handle_error(self, error_message: str):
        """
        V24 Enhanced error handler with clear, user-friendly error display.
        
        Implements colored error messages and detailed logging as specified
        in Protocol 10: Holistic Integration & Autonomy.
        """
        bpy.context.scene.settings.is_processing = False
        
        # V24: Color-coded error message for UI distinction
        formatted_error = f"❌ {error_message}"
        
        self.update_chat_ui(formatted_error)
        logger.error(f"V24: Worker thread error handled and displayed to user: {error_message}")
        
        # Additional status update for transparency
        bpy.context.scene.settings.status_message = "Error - See chat for details"
    
    def cancel(self, context):
        """Cancel the modal operator and clean up."""
        logger.info("Cancelling Design Engine Operator")
        
        self.is_running = False
        
        # Remove timer
        if self.timer_handle:
            try:
                bpy.app.timers.unregister(self.timer_handle)
            except:
                pass
            self.timer_handle = None
        
        # Stop worker thread gracefully
        if self.worker_thread and self.worker_thread.is_alive():
            # Note: threading.Thread doesn't have a built-in way to stop gracefully
            # The thread will finish its current operation and exit
            pass
        
        # Clean up UI
        context.scene.settings.is_processing = False
        
        return {'CANCELLED'}


# Properties for the Design Engine system
class EngineBaseSettings(bpy.types.PropertyGroup):
    """Settings for the Design Engine V20.0 system."""
    
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
        name="Current Prompt",
        description="Current user prompt",
        default=""
    )


def register():
    bpy.utils.register_class(EngineBaseSettings)
    bpy.types.Scene.settings_base = bpy.props.PointerProperty(type=EngineBaseSettings)


def unregister():
    if hasattr(bpy.types.Scene, 'settings_base'):
        del bpy.types.Scene.settings_base
    bpy.utils.unregister_class(EngineBaseSettings)