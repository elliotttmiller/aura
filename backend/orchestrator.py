"""
Aura V14.0 Sentient Artisan Environment - Native Orchestrator
==========================================================

Native Blender orchestrator that manages the AI conversation and 3D processing
without web server dependencies. Adapted from the V7.0 backend architecture.

Implements Protocol 3: Cognitive Authority (The AI-Minded Principle)
"""

import os
import json
import time
import logging
import requests
import subprocess
from typing import Dict, Any, Optional

import bpy

# Setup logging
logger = logging.getLogger(__name__)

class AuraOrchestrator:
    """Native Blender orchestrator for V14.0 Sentient Artisan Environment."""
    
    def __init__(self):
        self.addon_root = self._get_addon_root()
        self.output_dir = os.path.join(self.addon_root, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # AI Configuration - sandbox mode for initial implementation
        self.sandbox_mode = True
        self.lm_studio_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct"
        self.huggingface_api_key = os.environ.get("HUGGINGFACE_API_KEY", "")
        
        # Paths
        self.blender_proc_script = os.path.join(self.addon_root, "blender_proc.py")
        
        logger.info("AuraOrchestrator initialized in native Blender mode")
    
    def _get_addon_root(self) -> str:
        """Get the addon root directory."""
        return os.path.dirname(os.path.abspath(__file__))
    
    def generate_design(self, user_prompt: str, user_specs: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a new design based on user prompt.
        
        Args:
            user_prompt: The user's creative request
            user_specs: Optional technical specifications
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            logger.info(f"Starting design generation for: {user_prompt}")
            
            # Use default specs if none provided
            if user_specs is None:
                user_specs = {
                    'ring_size': 7.0,
                    'stone_carat': 1.0,
                    'stone_shape': 'ROUND',
                    'metal': 'GOLD'
                }
            
            # Stage 1: Generate Master Blueprint
            blueprint = self._generate_master_blueprint(user_prompt, user_specs)
            
            # Stage 2: Execute in Blender directly (native mode)
            result = self._execute_native_blender_processing(blueprint, user_specs)
            
            return {
                'success': True,
                'blueprint': blueprint,
                'object_name': result.get('object_name'),
                'shape_key_name': result.get('shape_key_name'),
                'message': 'Design generated successfully'
            }
            
        except Exception as e:
            logger.error(f"Design generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refine_design(self, refinement_prompt: str) -> Dict[str, Any]:
        """
        Refine an existing design based on user feedback.
        
        Args:
            refinement_prompt: User's refinement request
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            logger.info(f"Starting design refinement: {refinement_prompt}")
            
            # For now, treat refinement as a new design with the prompt
            # In full implementation, this would analyze existing geometry
            return self.generate_design(f"Refined design: {refinement_prompt}")
            
        except Exception as e:
            logger.error(f"Design refinement failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_master_blueprint(self, user_prompt: str, user_specs: Dict) -> Dict[str, Any]:
        """Generate Master Blueprint using Llama 3.1."""
        
        # V14.0 Updated Master Blueprint Prompt with technique selection
        master_blueprint_prompt = f"""You are a world-class jewelry CAD designer and system architect. Generate a JSON Master Blueprint for the following request.

        You must select a specific professional technique for the setting from: ['Pave', 'Bezel', 'Tension', 'ClassicProng'].

        Required V14.0 JSON Master Blueprint schema:
        {{
          "reasoning": "Step-by-step explanation of design choices and technique selection",
          "shank_parameters": {{
            "profile_shape": "D-Shape | Round",
            "thickness_mm": 1.5-2.5
          }},
          "setting_parameters": {{
            "technique": "One of ['Pave', 'Bezel', 'Tension', 'ClassicProng']",
            "parameters": {{
              // Technique-specific parameters object
            }}
          }},
          "artistic_modifier_parameters": {{
            "twist_angle_degrees": 0-180,
            "organic_displacement_strength": 0.0-0.001
          }}
        }}

        USER REQUEST: "{user_prompt}"
        SPECIFICATIONS:
        - Ring Size: {user_specs['ring_size']}
        - Metal: {user_specs['metal']}
        - Stone Shape: {user_specs['stone_shape']}
        - Stone Carat: {user_specs['stone_carat']}

        Respond only with valid JSON, no other text."""

        try:
            if self.sandbox_mode:
                blueprint = self._call_huggingface_api(master_blueprint_prompt)
            else:
                blueprint = self._call_lm_studio_api(master_blueprint_prompt)
            
            logger.info("Master Blueprint generated successfully")
            return blueprint
            
        except Exception as e:
            logger.warning(f"LLM call failed, using fallback blueprint: {e}")
            return self._create_fallback_blueprint(user_prompt, user_specs)
    
    def _call_huggingface_api(self, prompt: str) -> Dict[str, Any]:
        """Call Hugging Face API for blueprint generation."""
        
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}" if self.huggingface_api_key else "",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\\n\\nYou are a master jewelry designer. Respond only with valid JSON.<|eot_id|><|start_header_id|>user<|end_header_id|>\\n\\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\\n\\n",
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.lm_studio_url, headers=headers, json=request_data, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        if isinstance(response_data, list) and len(response_data) > 0:
            blueprint_text = response_data[0]['generated_text'].strip()
        else:
            blueprint_text = str(response_data).strip()
        
        return json.loads(blueprint_text)
    
    def _call_lm_studio_api(self, prompt: str) -> Dict[str, Any]:
        """Call LM Studio API for blueprint generation."""
        
        request_data = {
            "model": "llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": "You are a master jewelry designer. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        lm_studio_url = "http://localhost:1234/v1/chat/completions"
        response = requests.post(lm_studio_url, json=request_data, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        blueprint_text = response_data['choices'][0]['message']['content'].strip()
        
        return json.loads(blueprint_text)
    
    def _create_fallback_blueprint(self, user_prompt: str, user_specs: Dict) -> Dict[str, Any]:
        """Create fallback blueprint when LLM is unavailable."""
        
        # Determine technique based on prompt keywords
        prompt_lower = user_prompt.lower()
        if "tension" in prompt_lower:
            technique = "Tension"
            technique_params = {"tension_strength": 0.8}
        elif "bezel" in prompt_lower:
            technique = "Bezel"
            technique_params = {"bezel_height_mm": 2.0, "bezel_thickness_mm": 0.5}
        elif "pave" in prompt_lower or "pav" in prompt_lower:
            technique = "Pave"
            technique_params = {"stone_count": 12, "stone_size_mm": 1.5}
        else:
            technique = "ClassicProng"
            technique_params = {"prong_count": 4, "prong_thickness_mm": 0.8}
        
        return {
            "reasoning": f"Fallback blueprint for '{user_prompt}'. Selected {technique} technique based on prompt analysis. Using standard parameters for reliable manufacturing.",
            "shank_parameters": {
                "profile_shape": "Round",
                "thickness_mm": 2.0
            },
            "setting_parameters": {
                "technique": technique,
                "parameters": technique_params
            },
            "artistic_modifier_parameters": {
                "twist_angle_degrees": 15 if "twist" in prompt_lower else 0,
                "organic_displacement_strength": 0.0005 if "organic" in prompt_lower or "vine" in prompt_lower else 0.0
            }
        }
    
    def _execute_native_blender_processing(self, blueprint: Dict[str, Any], user_specs: Dict) -> Dict[str, Any]:
        """
        Execute Blender processing natively within the current session.
        
        This is the key transformation from subprocess to native execution.
        """
        try:
            logger.info("Starting native Blender processing")
            
            # Import the procedural knowledge module
            from .backend.procedural_knowledge import execute_technique
            
            # Create base object
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.009,  # Ring size radius
                minor_radius=blueprint['shank_parameters']['thickness_mm'] / 1000 / 2
            )
            base_object = bpy.context.active_object
            base_object.name = "AuraRing"
            
            # Apply technique from procedural knowledge
            technique = blueprint['setting_parameters']['technique']
            technique_params = blueprint['setting_parameters']['parameters']
            
            result_object = execute_technique(
                base_object=base_object,
                technique=technique,
                parameters=technique_params,
                artistic_modifiers=blueprint['artistic_modifier_parameters']
            )
            
            # Create Shape Key for animation
            if result_object.data.shape_keys is None:
                result_object.shape_key_add(name="Basis")
            
            shape_key = result_object.shape_key_add(name="AuraModification")
            shape_key.value = 0.0  # Start at 0 for animation
            
            # Apply basic material
            self._apply_material(result_object, user_specs['metal'])
            
            logger.info("Native Blender processing completed successfully")
            
            return {
                'object_name': result_object.name,
                'shape_key_name': 'AuraModification'
            }
            
        except Exception as e:
            logger.error(f"Native Blender processing failed: {e}")
            raise
    
    def _apply_material(self, obj: bpy.types.Object, metal_type: str):
        """Apply basic material to the object."""
        
        material_name = f"Aura_{metal_type}"
        
        # Create or get existing material
        material = bpy.data.materials.get(material_name)
        if material is None:
            material = bpy.data.materials.new(name=material_name)
            material.use_nodes = True
            
            # Set basic metallic properties
            if material.node_tree:
                principled = material.node_tree.nodes.get("Principled BSDF")
                if principled:
                    if metal_type.upper() == "GOLD":
                        principled.inputs["Base Color"].default_value = (1.0, 0.766, 0.336, 1.0)
                    elif metal_type.upper() == "SILVER":
                        principled.inputs["Base Color"].default_value = (0.972, 0.960, 0.915, 1.0)
                    elif metal_type.upper() == "PLATINUM":
                        principled.inputs["Base Color"].default_value = (0.9, 0.9, 0.95, 1.0)
                    
                    principled.inputs["Metallic"].default_value = 1.0
                    principled.inputs["Roughness"].default_value = 0.1
        
        # Apply material to object
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)