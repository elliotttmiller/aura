"""
V22.0 Verifiable Artisan - Master Planner Orchestrator
=====================================================

The evolved AI Master Planner that generates dynamic construction plans as sequences of operations.
The Llama 3.1 LLM generates JSON Master Blueprints with construction_plan lists that are 
executed dynamically by the Blender Engine.

Implements Protocol 2: Absolute Cognitive Authority - AI generates dynamic operation sequences.
Implements Protocol 1: Sentient Transparency - All processing is verifiable and auditable.
"""

import os
import json
import time
import logging
import requests
import subprocess
from typing import Dict, Any, Optional

import bpy

# V24 Enhancement: Load centralized configuration
try:
    from ..config import config, get_lm_studio_url, get_ai_server_config, is_sandbox_mode
    CONFIG_AVAILABLE = True
except ImportError:
    logging.warning("Config module not available, using environment variables")
    CONFIG_AVAILABLE = False

# Setup logging
logger = logging.getLogger(__name__)

class Orchestrator:
    """Native Blender orchestrator for V24 Design Engine."""
    
    def __init__(self):
        self.addon_root = self._get_addon_root()
        
        # V24 Enhanced directory setup with configuration
        if CONFIG_AVAILABLE:
            self.output_dir = os.path.join(self.addon_root, config.get('OUTPUT_DIR', 'output'))
            self.sandbox_mode = is_sandbox_mode()
            self.lm_studio_url = get_lm_studio_url()
            self.huggingface_api_key = config.get('HUGGINGFACE_API_KEY', '')
        else:
            # Fallback configuration
            self.output_dir = os.path.join(self.addon_root, "output")
            self.sandbox_mode = True
            self.lm_studio_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct"
            self.huggingface_api_key = os.environ.get("HUGGINGFACE_API_KEY", "")
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Paths
        self.blender_proc_script = os.path.join(self.addon_root, "blender_proc.py")
        
        logger.info(f"V24 Orchestrator initialized - Sandbox: {self.sandbox_mode}")
    
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
        """Generate V22.0 Master Blueprint with dynamic construction_plan using Llama 3.1."""
        
        # V22.0 Revolutionary Master Blueprint Prompt with dynamic construction_plan
        master_blueprint_prompt = f"""You are a world-class master artisan and system architect. Generate a JSON Master Blueprint with a DYNAMIC CONSTRUCTION PLAN for the following request.

The construction_plan must be a LIST OF OPERATIONS that will be executed sequentially. Each operation calls a function from the procedural knowledge base.

Available operations and their parameters:
- create_shank: profile_shape, thickness_mm, diameter_mm, taper_factor
- create_bezel_setting: bezel_height_mm, bezel_thickness_mm, feature_diameter_mm, setting_position
- create_prong_setting: prong_count, prong_thickness_mm, prong_height_mm, prong_placement_radius_mm, prong_taper
- apply_twist_modifier: twist_angle_degrees, twist_axis, twist_limits

Required V22.0 JSON Master Blueprint schema:
{{
  "reasoning": "Step-by-step explanation of the design approach and construction sequence",
  "construction_plan": [
    {{
      "operation": "create_shank",
      "parameters": {{
        "profile_shape": "Round",
        "thickness_mm": 2.0,
        "diameter_mm": 18.0,
        "taper_factor": 0.0
      }}
    }},
    {{
      "operation": "create_prong_setting", 
      "parameters": {{
        "prong_count": 4,
        "prong_thickness_mm": 0.8,
        "prong_height_mm": 3.5,
        "prong_placement_radius_mm": 3.0,
        "prong_taper": 0.2
      }}
    }},
    {{
      "operation": "apply_twist_modifier",
      "parameters": {{
        "twist_angle_degrees": 15,
        "twist_axis": "Z",
        "twist_limits": [0.0, 1.0]
      }}
    }}
  ],
  "material_specifications": {{
    "primary_material": "GOLD" | "SILVER" | "PLATINUM",
    "finish": "POLISHED" | "MATTE" | "BRUSHED"
  }}
}}

USER REQUEST: "{user_prompt}"
SPECIFICATIONS:
- Target Size: {user_specs.get('ring_size', 7.0)}
- Material: {user_specs.get('metal', 'GOLD')}
- Feature Shape: {user_specs.get('stone_shape', 'ROUND')}
- Feature Scale: {user_specs.get('stone_carat', 1.0)}

Generate a construction_plan with 2-4 operations that will create the requested design. 
Each operation must use the exact function names and parameter structures listed above.
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
    
    def _validate_master_blueprint(self, blueprint: Dict[str, Any]) -> None:
        """
        V24 Enhancement: Strict Master Blueprint JSON validation.
        
        Validates that the AI response contains all required fields and proper structure
        as mandated by Protocol 10: Holistic Integration & Autonomy.
        
        Args:
            blueprint: The parsed JSON blueprint from AI
            
        Raises:
            ValueError: If blueprint validation fails
        """
        logger.info("V24: Validating Master Blueprint JSON schema")
        
        # Required top-level fields
        required_fields = ['reasoning', 'construction_plan', 'material_specifications']
        for field in required_fields:
            if field not in blueprint:
                raise ValueError(f"V24 Validation Failed: Missing required field '{field}' in Master Blueprint")
        
        # Validate construction_plan structure
        construction_plan = blueprint['construction_plan']
        if not isinstance(construction_plan, list):
            raise ValueError("V24 Validation Failed: construction_plan must be a list of operations")
        
        if len(construction_plan) == 0:
            raise ValueError("V24 Validation Failed: construction_plan cannot be empty")
        
        # Validate each operation in the construction plan
        valid_operations = [
            'create_shank', 'create_bezel_setting', 'create_prong_setting', 
            'apply_twist_modifier', 'create_pave_setting', 'create_tension_setting'
        ]
        
        for i, operation in enumerate(construction_plan):
            if not isinstance(operation, dict):
                raise ValueError(f"V24 Validation Failed: Operation {i+1} must be a dictionary")
            
            if 'operation' not in operation:
                raise ValueError(f"V24 Validation Failed: Operation {i+1} missing 'operation' field")
            
            if 'parameters' not in operation:
                raise ValueError(f"V24 Validation Failed: Operation {i+1} missing 'parameters' field")
            
            op_name = operation['operation']
            if op_name not in valid_operations:
                logger.warning(f"V24 Validation Warning: Unknown operation '{op_name}' in position {i+1}")
        
        # Validate material specifications
        material_specs = blueprint['material_specifications']
        if not isinstance(material_specs, dict):
            raise ValueError("V24 Validation Failed: material_specifications must be a dictionary")
        
        if 'primary_material' not in material_specs:
            raise ValueError("V24 Validation Failed: material_specifications missing 'primary_material'")
        
        logger.info(f"V24: Master Blueprint validation successful - {len(construction_plan)} operations validated")
    
    def _call_huggingface_api(self, prompt: str) -> Dict[str, Any]:
        """Call Hugging Face API for blueprint generation with V24 JSON validation."""
        
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
        
        try:
            response = requests.post(self.lm_studio_url, headers=headers, json=request_data, timeout=60)
            response.raise_for_status()
            
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                blueprint_text = response_data[0]['generated_text'].strip()
            else:
                blueprint_text = str(response_data).strip()
            
            # V24 Enhancement: Parse and validate JSON structure
            blueprint = json.loads(blueprint_text)
            self._validate_master_blueprint(blueprint)
            
            logger.info("V24: AI response JSON validation successful")
            return blueprint
            
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            logger.error(f"V24: AI API call failed with validation error: {e}")
            raise RuntimeError(f"AI Master Planner communication failed: {e}")
    
    def _call_lm_studio_api(self, prompt: str) -> Dict[str, Any]:
        """Call LM Studio API for blueprint generation with V24 JSON validation."""
        
        request_data = {
            "model": "llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": "You are a master jewelry designer. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            lm_studio_url = "http://localhost:1234/v1/chat/completions"
            response = requests.post(lm_studio_url, json=request_data, timeout=60)
            response.raise_for_status()
            
            response_data = response.json()
            blueprint_text = response_data['choices'][0]['message']['content'].strip()
            
            # V24 Enhancement: Parse and validate JSON structure
            blueprint = json.loads(blueprint_text)
            self._validate_master_blueprint(blueprint)
            
            logger.info("V24: LM Studio response JSON validation successful")
            return blueprint
            
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            logger.error(f"V24: LM Studio API call failed with validation error: {e}")
            raise RuntimeError(f"AI Master Planner communication failed: {e}")
    
    def _generate_dynamic_bmesh_code(self, user_request_for_component: str, component_parameters: Dict[str, Any]) -> str:
        """
        V23 Generative Artisan: Generate custom bmesh Python code for novel geometry.
        
        This is the revolutionary V23 "Text-to-bmesh" capability that allows the AI to
        create new procedural techniques on the fly when existing knowledge base is insufficient.
        
        Args:
            user_request_for_component: Description of the custom component needed
            component_parameters: Dictionary of parameters to work with
            
        Returns:
            String containing the complete Python function code
        """
        logger.info(f"V23: Generating dynamic bmesh code for: {user_request_for_component}")
        
        # V23 State-of-the-Art "Text-to-bmesh" Prompt Template
        text_to_bmesh_prompt = f"""You are a world-class, expert Blender Python programmer specializing in the `bmesh` API. Your sole mission is to write a clean, efficient, and secure Python function that generates a specific 3D geometry using `bmesh`.

You must adhere to these strict rules:
1. The function must be named `create_custom_component`.
2. It must accept two arguments: `bm` (the bmesh object to add geometry to) and `params` (a dictionary of parameters).
3. You are ONLY allowed to use the `bmesh` API and the standard Python `math` library.
4. You are FORBIDDEN from using any other imports (like `os` or `sys`).
5. The function must not create new objects or modify the scene; it must only add geometry to the provided `bm`.
6. You must return the `geom` created by the final `bmesh.ops` call.

Here is the user's request for the custom component:
"{user_request_for_component}"

Here are the parameters you have to work with:
{component_parameters}

Now, write only the Python code for the `create_custom_component` function. Do not include any other text, explanations, or markdown formatting."""

        try:
            # Use the same LLM endpoint as blueprint generation
            if self.sandbox_mode:
                code_response = self._call_huggingface_api_for_code(text_to_bmesh_prompt)
            else:
                code_response = self._call_lm_studio_api_for_code(text_to_bmesh_prompt)
            
            logger.info("V23: Dynamic bmesh code generated successfully")
            return code_response
            
        except Exception as e:
            logger.error(f"V23: Dynamic code generation failed: {e}")
            # Return a safe fallback function
            return self._create_fallback_bmesh_function(user_request_for_component)
    
    def _call_huggingface_api_for_code(self, prompt: str) -> str:
        """Call Hugging Face API specifically for code generation."""
        request_data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.3,  # Lower temperature for more deterministic code
                "return_full_text": False
            }
        }
        
        headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
        response = requests.post(self.lm_studio_url, json=request_data, headers=headers, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        if isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0].get('generated_text', '').strip()
        else:
            raise RuntimeError("Invalid response format from Hugging Face API")
    
    def _call_lm_studio_api_for_code(self, prompt: str) -> str:
        """Call LM Studio API specifically for code generation."""
        request_data = {
            "model": "llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": "You are an expert Blender bmesh programmer. Respond only with Python code, no explanations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more deterministic code
            "max_tokens": 500
        }
        
        lm_studio_url = "http://localhost:1234/v1/chat/completions"
        response = requests.post(lm_studio_url, json=request_data, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        return response_data['choices'][0]['message']['content'].strip()
    
    def _create_fallback_bmesh_function(self, user_request: str) -> str:
        """Create a safe fallback bmesh function when dynamic generation fails."""
        logger.warning(f"V23: Creating fallback bmesh function for: {user_request}")
        
        # Simple star-shaped geometry as fallback for star bezel request
        if "star" in user_request.lower():
            return """def create_custom_component(bm, params):
    import bmesh
    import math
    
    # Create a star-shaped bezel
    radius_outer = params.get('radius_outer', 0.006)  # 6mm outer radius
    radius_inner = params.get('radius_inner', 0.004)  # 4mm inner radius
    height = params.get('height', 0.002)  # 2mm height
    points = 5  # 5-pointed star
    
    # Create star profile vertices
    verts = []
    for i in range(points * 2):  # Outer and inner points
        angle = (i * math.pi) / points
        if i % 2 == 0:  # Outer points
            radius = radius_outer
        else:  # Inner points
            radius = radius_inner
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        verts.extend([
            bm.verts.new((x, y, 0)),  # Bottom
            bm.verts.new((x, y, height))  # Top
        ])
    
    # Create faces to form the star bezel
    faces = []
    for i in range(0, len(verts), 2):
        next_i = (i + 2) % len(verts)
        # Side face
        face_verts = [verts[i], verts[i+1], verts[next_i+1], verts[next_i]]
        faces.append(bm.faces.new(face_verts))
    
    bm.faces.ensure_lookup_table()
    return faces"""
        
        # Generic fallback
        return """def create_custom_component(bm, params):
    import bmesh
    import math
    
    # Generic cylindrical component
    radius = params.get('radius', 0.005)
    height = params.get('height', 0.002)
    
    geom = bmesh.ops.create_cylinder(bm, cap_ends=True, radius=radius, depth=height)
    return geom['verts']"""
    
    def _create_fallback_blueprint(self, user_prompt: str, user_specs: Dict) -> Dict[str, Any]:
        """Create V22.0 fallback blueprint with construction_plan when LLM is unavailable."""
        
        # Determine operations based on prompt keywords
        prompt_lower = user_prompt.lower()
        operations = []
        
        # Always start with shank creation
        operations.append({
            "operation": "create_shank",
            "parameters": {
                "profile_shape": "Round",
                "thickness_mm": 2.0,
                "diameter_mm": 18.0,
                "taper_factor": 0.0
            }
        })
        
        # Add setting based on prompt
        if "tension" in prompt_lower:
            # Tension setting doesn't use traditional prongs/bezels
            pass  # Shank only for tension
        elif "bezel" in prompt_lower:
            operations.append({
                "operation": "create_bezel_setting",
                "parameters": {
                    "bezel_height_mm": 2.0,
                    "bezel_thickness_mm": 0.5,
                    "feature_diameter_mm": 6.0,
                    "setting_position": [0, 0, 0.002]
                }
            })
        else:  # Default to prong setting
            operations.append({
                "operation": "create_prong_setting",
                "parameters": {
                    "prong_count": 4,
                    "prong_thickness_mm": 0.8,
                    "prong_height_mm": 3.5,
                    "prong_placement_radius_mm": 3.0,
                    "prong_taper": 0.2
                }
            })
        
        # Add twist if mentioned
        if "twist" in prompt_lower:
            operations.append({
                "operation": "apply_twist_modifier",
                "parameters": {
                    "twist_angle_degrees": 15,
                    "twist_axis": "Z",
                    "twist_limits": [0.0, 1.0]
                }
            })
        
        return {
            "reasoning": f"V22.0 Fallback construction plan for '{user_prompt}'. Generated {len(operations)} sequential operations based on prompt analysis.",
            "construction_plan": operations,
            "material_specifications": {
                "primary_material": user_specs.get('metal', 'GOLD'),
                "finish": "POLISHED"
            }
        }
    
    def _technique_exists(self, operation_name: str) -> bool:
        """
        V23 Generative Artisan: Check if a technique exists in the procedural knowledge base.
        
        Args:
            operation_name: The name of the operation to check
            
        Returns:
            True if the technique exists, False if it needs to be dynamically generated
        """
        # List of all known techniques in the V24 knowledge base
        known_techniques = {
            'create_shank',
            'create_bezel_setting', 
            'create_prong_setting',
            'apply_twist_modifier',
            'create_pave_setting',
            'create_tension_setting', 
            'create_classic_prong_setting'
        }
        
        exists = operation_name in known_techniques
        logger.info(f"V23: Technique validation for '{operation_name}': {'EXISTS' if exists else 'REQUIRES GENERATION'}")
        return exists
    
    def _execute_native_blender_processing(self, blueprint: Dict[str, Any], user_specs: Dict) -> Dict[str, Any]:
        """
        Execute V22.0 dynamic construction plan processing natively within Blender.
        
        This is the revolutionary V22.0 transformation where the Blender Engine
        dynamically executes the AI's construction_plan as a sequence of operations.
        """
        try:
            logger.info("Starting V22.0 dynamic construction plan execution")
            
            # Stage 1: Initialize procedural knowledge system
            from .procedural_knowledge import execute_operation
            
            # Stage 2: Execute construction plan dynamically
            construction_plan = blueprint.get('construction_plan', [])
            if not construction_plan:
                logger.warning("No construction_plan found, using fallback")
                construction_plan = [{"operation": "create_shank", "parameters": {"profile_shape": "Round", "thickness_mm": 2.0}}]
            
            logger.info(f"Executing {len(construction_plan)} operations from construction plan")
            
            # Context for tracking objects across operations
            context_objects = {"base": None}
            final_object = None
            
            # Execute each operation in sequence
            for i, operation in enumerate(construction_plan):
                operation_name = operation.get('operation', 'unknown')
                logger.info(f"Operation {i+1}/{len(construction_plan)}: {operation_name}")
                
                # V23 Generative Artisan: Check if technique exists in knowledge base
                if not self._technique_exists(operation_name):
                    logger.info(f"V23: Technique '{operation_name}' not found in knowledge base")
                    logger.info("V23: 🧠 Inventing new technique...")
                    
                    # Generate dynamic bmesh code for the unknown technique
                    try:
                        user_request = f"Create a {operation_name.replace('_', ' ')} component for jewelry design"
                        component_params = operation.get('parameters', {})
                        
                        dynamic_code = self._generate_dynamic_bmesh_code(user_request, component_params)
                        
                        # Pass dynamic code to the operation for execution
                        operation['_v23_dynamic_code'] = dynamic_code
                        logger.info(f"V23: ✨ Dynamic technique code generated for '{operation_name}'")
                        
                    except Exception as e:
                        logger.error(f"V23: Dynamic code generation failed for '{operation_name}': {e}")
                        # Continue with standard execution (will use fallback)
                
                try:
                    result_object = execute_operation(operation, context_objects)
                    if result_object:
                        final_object = result_object
                        context_objects['base'] = result_object
                        logger.info(f"Operation {operation_name} completed successfully")
                    else:
                        logger.warning(f"Operation {operation_name} returned no object")
                        
                except Exception as e:
                    logger.error(f"Operation {operation_name} failed: {e}")
                    continue
            
            if not final_object:
                logger.warning("No objects created, generating fallback")
                final_object = self._create_fallback_ring(blueprint, user_specs)
            
            # Stage 3: Create Shape Key for animation (V22.0 feature)
            if final_object.data.shape_keys is None:
                final_object.shape_key_add(name="Basis")
            
            shape_key = final_object.shape_key_add(name="V22_ConstructionPlan_Result")
            shape_key.value = 0.0  # Start at 0 for animation
            
            # Stage 4: Apply material
            material_specs = blueprint.get('material_specifications', {})
            metal_type = material_specs.get('primary_material', user_specs.get('metal', 'GOLD'))
            self._apply_material(final_object, metal_type)
            
            logger.info("V22.0 dynamic construction plan execution completed successfully")
            
            return {
                'object_name': final_object.name,
                'shape_key_name': 'V22_ConstructionPlan_Result',
                'operations_executed': len(construction_plan)
            }
            
        except Exception as e:
            logger.error(f"V22.0 construction plan execution failed: {e}")
            raise
    
    def _generate_implicit_functions(self, blueprint: Dict, user_specs: Dict) -> Dict[str, str]:
        """Generate implicit function parameters using AI server."""
        try:
            # Call the new /generate_implicit endpoint
            ai_server_url = "http://localhost:8002/generate_implicit"
            
            # Create prompt from blueprint
            prompt = blueprint.get('reasoning', 'Beautiful jewelry design')
            
            request_data = {
                "prompt": prompt,
                "guidance_scale": 15.0,
                "num_inference_steps": 64,
                "batch_size": 4
            }
            
            logger.info(f"Calling AI server for implicit function generation: {prompt}")
            
            response = requests.post(ai_server_url, json=request_data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            if not result['success']:
                raise RuntimeError(f"AI server error: {result.get('error', 'Unknown error')}")
            
            logger.info("Implicit functions generated successfully")
            
            return {
                'decoder_path': result['decoder_path'],
                'texture_path': result['texture_path'],
                'latent_path': result.get('latent_path')
            }
            
        except Exception as e:
            logger.error(f"Implicit function generation failed: {e}")
            raise
    
    def _extract_mesh_from_implicit_functions(self, implicit_files: Dict[str, str], 
                                            blueprint: Dict, user_specs: Dict) -> bpy.types.Object:
        """Extract mesh using Marching Cubes algorithm."""
        try:
            # Import the blender_proc functions directly
            import sys
            sys.path.append(self.addon_root)
            
            from blender_proc import create_blender_mesh_from_implicit
            
            # Get mesh quality setting from scene settings
            mesh_quality = getattr(bpy.context.scene.settings, 'mesh_quality', 64)
            
            logger.info(f"Extracting mesh using Marching Cubes (quality={mesh_quality})")
            
            # Create mesh from implicit functions
            result_object = create_blender_mesh_from_implicit(
                decoder_path=implicit_files['decoder_path'],
                texture_path=implicit_files['texture_path'],
                mesh_quality=mesh_quality,
                object_name="V17_Symbiotic_Creation"
            )
            
            logger.info("Mesh extraction completed successfully")
            return result_object
            
        except Exception as e:
            logger.error(f"Mesh extraction failed: {e}")
            # Fallback to basic ring creation
            return self._create_fallback_ring(blueprint, user_specs)
    
    def _apply_procedural_enhancements(self, obj: bpy.types.Object, blueprint: Dict) -> bpy.types.Object:
        """Apply procedural knowledge enhancements to the implicit surface."""
        try:
            from .procedural_knowledge import execute_technique
            
            setting_params = blueprint['setting_parameters']
            technique = setting_params.get('technique', 'ClassicProng')
            technique_params = setting_params.get('parameters', {})
            artistic_modifiers = blueprint.get('artistic_modifier_parameters', {})
            
            logger.info(f"Applying procedural enhancement: {technique}")
            
            enhanced_object = execute_technique(
                base_object=obj,
                technique=technique, 
                parameters=technique_params,
                artistic_modifiers=artistic_modifiers
            )
            
            return enhanced_object
            
        except Exception as e:
            logger.warning(f"Procedural enhancement failed: {e}")
            return obj  # Return original object
    
    def _create_fallback_ring(self, blueprint: Dict, user_specs: Dict) -> bpy.types.Object:
        """Create fallback ring if implicit processing fails."""
        logger.info("Creating fallback ring geometry")
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.009,  # Ring size radius
            minor_radius=blueprint['shank_parameters'].get('thickness_mm', 2.0) / 1000 / 2
        )
        
        fallback_object = bpy.context.active_object
        fallback_object.name = "V17_Fallback_Ring"
        
        return fallback_object
    
    def _apply_material(self, obj: bpy.types.Object, metal_type: str):
        """Apply basic material to the object."""
        
        material_name = f"Material_{metal_type}"
        
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