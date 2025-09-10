"""
V7.0 Backend Orchestrator - Professional AI Pipeline
====================================================

This orchestrator manages the V7.0 professional workflow:
Stage 1: LLM (Llama 3.1 via LM Studio) generates Master Blueprint
Stage 2: External AI Environment generates 3D base geometry  
Stage 3: State-of-the-Art Blender engine executes the Master Blueprint

Part of the V7.0 Professional Integration.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse
import subprocess
import os
import logging
import json
import requests
import shlex
import time

# V24 Enhancement: Centralized environment configuration
try:
    from ..config import config, get_lm_studio_url, get_ai_server_config, is_sandbox_mode
    CONFIG_AVAILABLE = True
except ImportError:
    logging.warning("Config module not available, using environment variables")
    CONFIG_AVAILABLE = False

app = FastAPI(title="V24 Backend Orchestrator", version="24.0")

# V24 Enhanced logging configuration
if CONFIG_AVAILABLE:
    log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO').upper())
    logging.basicConfig(level=log_level, format=config.get('LOG_FORMAT', '[%(asctime)s] %(levelname)s %(message)s'))
else:
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')

logger = logging.getLogger(__name__)

# V24 Configuration with centralized config management
if CONFIG_AVAILABLE:
    SANDBOX_MODE = is_sandbox_mode()
    BLENDER_PATH = config.get('BLENDER_PATH', r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe")
    OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", config.get('OUTPUT_DIR', 'output')))
    LM_STUDIO_URL = get_lm_studio_url()
    EXTERNAL_AI_URL = get_ai_server_config()['url']
    HUGGINGFACE_API_KEY = config.get('HUGGINGFACE_API_KEY', '')
else:
    # Fallback to environment variables
    SANDBOX_MODE = os.environ.get("SANDBOX_MODE", "").lower() == "true"
    BLENDER_PATH = os.environ.get("BLENDER_PATH", r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe")
    OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    if SANDBOX_MODE:
        LM_STUDIO_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct"
        HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")
    else:
        LM_STUDIO_URL = os.environ.get("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
    EXTERNAL_AI_URL = os.environ.get("EXTERNAL_AI_URL", "http://localhost:8002")

# V24 Enhanced script paths
BLENDER_PROC_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blender_proc.py"))
BLENDER_SIM_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blender_sim.py"))

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# V6.0 Master Blueprint Prompt Template for Llama 3.1 with Reasoning
MASTER_BLUEPRINT_PROMPT = """You are a world-class, expert jewelry CAD designer and system architect. Your mission is to translate a user's creative request into a complete, precise, and manufacturable 3D design blueprint.

You must generate a single, valid JSON object that contains ALL the necessary parameters to construct the final piece. Do not include any other text, explanations, or markdown formatting. Adhere strictly to the schema.

This is the required V6.0 JSON Master Blueprint schema with reasoning:
{{
  "reasoning": "A brief, step-by-step explanation of why you chose the following parameters based on the user's prompt.",
  "creative_prompt_for_3d_model": "A rich, descriptive paragraph for the 3D generative model. Describe the visual style, textures, and artistic elements. This is the most important creative step.",
  "shank_parameters": {{
    "profile_shape": "A string, either 'D-Shape' or 'Round'.",
    "thickness_mm": "A float, between 1.5 and 2.5."
  }},
  "setting_parameters": {{
    "prong_count": "An integer, either 4 or 6.",
    "style": "A string, either 'Classic' for straight prongs or 'Sweeping' for curved prongs.",
    "height_above_shank_mm": "A float, representing the height of the stone setting from the top of the ring band."
  }},
  "artistic_modifier_parameters": {{
    "twist_angle_degrees": "An integer, from 0 to 180. 0 means no twist.",
    "organic_displacement_strength": "A float, from 0.0 to 0.001. 0.0 means no organic texture."
  }}
}}

Analyze the following user request and generate the complete JSON Master Blueprint with reasoning.

USER'S REQUEST: "{user_prompt}"
TECHNICAL SPECIFICATIONS:
- Ring Size (US): {ring_size}
- Metal: {metal}
- Stone Shape: {stone_shape}
- Stone Carat: {stone_carat}"""

# V6.0 AI Critic Refinement Prompt Template
REFINEMENT_PROMPT = """You are a world-class, expert jewelry CAD designer performing a design review.
Your previous design plan was:
{previous_json_blueprint}

A geometric analysis of the 3D model created from this plan reveals the following metrics:
{geometric_analysis_report}

The user's new request is: "{user_refinement_prompt}"

Your mission is to generate a new, revised JSON Master Blueprint that incorporates the user's feedback. Output only the revised JSON object with the same V6.0 schema including reasoning."""

def get_output_path(prompt: str) -> str:
    """Generate output file path based on prompt."""
    safe_name = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = "_".join(safe_name.split())[:40]
    return os.path.join(OUTPUT_DIR, f"output_{safe_name}.stl")

async def generate_master_blueprint(user_prompt: str, user_specs: dict) -> dict:
    """
    Stage 1: Generate Master Blueprint using Llama 3.1 via LM Studio or Hugging Face.
    
    Args:
        user_prompt: User's creative request
        user_specs: Technical specifications
        
    Returns:
        Parsed JSON Master Blueprint
    """
    logger.info("=== STAGE 1: AI SYSTEM ARCHITECT (LLAMA 3.1) ===")
    logger.info(f"Mode: {'V6.0 Sandbox (Hugging Face)' if SANDBOX_MODE else 'V7.0 Production (LM Studio)'}")
    logger.info(f"Generating Master Blueprint for: '{user_prompt}'")
    
    # Construct the master prompt
    master_prompt = MASTER_BLUEPRINT_PROMPT.format(
        user_prompt=user_prompt,
        ring_size=user_specs['ring_size'],
        metal=user_specs['metal'],
        stone_shape=user_specs['stone_shape'],
        stone_carat=user_specs['stone_carat']
    )
    
    if SANDBOX_MODE:
        # V6.0 Sandbox Mode - Use Hugging Face API
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}" if HUGGINGFACE_API_KEY else "",
            "Content-Type": "application/json"
        }
        
        hf_request = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a master jewelry designer. Respond only with valid JSON, no other text.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{master_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        try:
            logger.debug(f"Sending request to Hugging Face: {LM_STUDIO_URL}")
            response = requests.post(LM_STUDIO_URL, headers=headers, json=hf_request, timeout=60)
            response.raise_for_status()
            
            hf_data = response.json()
            if isinstance(hf_data, list) and len(hf_data) > 0:
                blueprint_text = hf_data[0]['generated_text'].strip()
            else:
                blueprint_text = str(hf_data).strip()
                
            logger.debug(f"Hugging Face Response: {blueprint_text}")
            
            # Parse JSON Master Blueprint
            blueprint = json.loads(blueprint_text)
            logger.info("V6.0 Master Blueprint generated successfully via Hugging Face")
            logger.debug(f"Blueprint: {json.dumps(blueprint, indent=2)}")
            
            return blueprint
            
        except requests.RequestException as e:
            logger.error(f"Hugging Face API connection failed: {e}")
            logger.warning("Using fallback Master Blueprint")
            return create_fallback_blueprint(user_prompt)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from Hugging Face: {e}")
            return create_fallback_blueprint(user_prompt)
    
    else:
        # V7.0 Production Mode - Use LM Studio
        lm_request = {
            "model": "llama-3.1-8b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a master jewelry designer. Respond only with valid JSON, no other text."
                },
                {
                    "role": "user", 
                    "content": master_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            logger.debug(f"Sending request to LM Studio: {LM_STUDIO_URL}")
            response = requests.post(LM_STUDIO_URL, json=lm_request, timeout=60)
            response.raise_for_status()
            
            lm_data = response.json()
            blueprint_text = lm_data['choices'][0]['message']['content'].strip()
            
            logger.debug(f"LLM Response: {blueprint_text}")
            
            # Parse JSON Master Blueprint
            blueprint = json.loads(blueprint_text)
            logger.info("V7.0 Master Blueprint generated successfully via LM Studio")
            logger.debug(f"Blueprint: {json.dumps(blueprint, indent=2)}")
            
            return blueprint
            
        except requests.RequestException as e:
            logger.error(f"LM Studio connection failed: {e}")
            # Fallback blueprint for testing
            logger.warning("Using fallback Master Blueprint")
            return create_fallback_blueprint(user_prompt)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from LLM: {e}")
            return create_fallback_blueprint(user_prompt)

def create_fallback_blueprint(user_prompt: str) -> dict:
    """Create a fallback Master Blueprint when LLM is unavailable."""
    return {
        "reasoning": f"Fallback blueprint generated due to LLM unavailability. Using sensible defaults based on keywords in prompt: '{user_prompt}'. Selected classic styling with moderate parameters for reliable manufacturing.",
        "creative_prompt_for_3d_model": f"An elegant jewelry piece inspired by: {user_prompt}. The design features smooth curves and sophisticated metalwork with fine details and artistic flourishes.",
        "shank_parameters": {
            "profile_shape": "Round",
            "thickness_mm": 2.0
        },
        "setting_parameters": {
            "prong_count": 4,
            "style": "Classic",
            "height_above_shank_mm": 3.5
        },
        "artistic_modifier_parameters": {
            "twist_angle_degrees": 15 if "twist" in user_prompt.lower() else 0,
            "organic_displacement_strength": 0.0005 if "organic" in user_prompt.lower() or "vine" in user_prompt.lower() else 0.0
        }
    }

async def generate_3d_base_geometry(blueprint: dict) -> str:
    """
    Stage 2: Generate 3D base geometry using Shap-E.
    
    Args:
        blueprint: Master Blueprint containing creative_prompt_for_3d_model
        
    Returns:
        Path to generated .obj file
    """
    logger.info("=== STAGE 2: AI MASTER ARTISAN (SHAP-E) ===")
    creative_prompt = blueprint['creative_prompt_for_3d_model']
    logger.info(f"Generating 3D geometry for: '{creative_prompt}'")
    
    try:
        # Send request to AI server
        ai_request = {
            "prompt": creative_prompt,
            "guidance_scale": 15.0,
            "num_inference_steps": 64
        }
        
        logger.debug(f"Sending request to external AI environment: {EXTERNAL_AI_URL}")
        try:
            response = requests.post(f"{EXTERNAL_AI_URL}/generate", json=ai_request, timeout=120)
            response.raise_for_status()
            
            ai_data = response.json()
            
            if not ai_data.get('success'):
                raise RuntimeError(f"External AI service error: {ai_data.get('error', 'Unknown error')}")
            
            obj_path = ai_data['obj_path']
            logger.info(f"3D base geometry generated: {obj_path}")
            
            return obj_path
            
        except requests.RequestException as e:
            logger.warning(f"External AI service not available: {e}")
            logger.info("Using fallback geometry generation...")
            
            # V7.0 Fallback: Generate simple base geometry for testing
            return await generate_fallback_geometry(creative_prompt)
        
    except Exception as e:
        logger.error(f"3D geometry generation failed: {e}")
        raise RuntimeError(f"Could not generate 3D geometry: {e}")

async def generate_fallback_geometry(prompt: str) -> str:
    """
    Generate fallback geometry when external AI service is not available.
    Creates a simple parametric shape for testing and development.
    """
    logger.info("Generating fallback geometry for development/testing")
    
    # Create fallback directory in models
    fallback_dir = os.path.join(os.path.dirname(__file__), "..", "models", "fallback")
    os.makedirs(fallback_dir, exist_ok=True)
    
    # Generate a simple OBJ file with basic geometry
    safe_name = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = "_".join(safe_name.split())[:20]
    obj_path = os.path.join(fallback_dir, f"fallback_{safe_name}.obj")
    
    # Write simple cube geometry
    with open(obj_path, 'w') as f:
        f.write("""# Simple fallback geometry
v -0.005 -0.005 -0.005
v  0.005 -0.005 -0.005
v  0.005  0.005 -0.005
v -0.005  0.005 -0.005
v -0.005 -0.005  0.005
v  0.005 -0.005  0.005
v  0.005  0.005  0.005
v -0.005  0.005  0.005

f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 5 1 4 8
""")
    
    logger.info(f"Fallback geometry generated: {obj_path}")
    return obj_path

async def execute_blender_analyzer(stl_path: str, analysis_output_path: str):
    """
    V6.0 Cognitive Loop: Execute Blender Engine in analysis mode.
    
    Args:
        stl_path: Path to STL file to analyze
        analysis_output_path: Path for JSON analysis output
    """
    logger.info("=== V6.0 BLENDER ENGINE - ANALYSIS MODE ===")
    logger.info(f"Analyzing STL: {stl_path}")
    
    # Use empty params for analysis mode
    empty_params = json.dumps({})
    
    # Check if we should use simulator (when Blender is not available)
    use_simulator = not os.path.exists(BLENDER_PATH)
    
    if use_simulator:
        logger.info("Using Blender simulator for analysis")
        # For simulator, create a basic analysis JSON
        basic_analysis = {
            "analysis_timestamp": str(time.time()),
            "geometry_metrics": {
                "vertex_count": 500,
                "edge_count": 1000,
                "face_count": 500,
                "bounding_box": {
                    "min": [-0.01, -0.01, -0.01],
                    "max": [0.01, 0.01, 0.01],
                    "dimensions": [0.02, 0.02, 0.02]
                },
                "approximate_volume_cubic_mm": 8.0,
                "center_of_mass": [0.0, 0.0, 0.0]
            },
            "manufacturing_assessment": {
                "complexity_level": "medium",
                "printability_score": 0.8,
                "estimated_material_usage_grams": 0.15,
                "structural_integrity": "good"
            },
            "design_characteristics": {
                "dominant_dimension": "width",
                "aspect_ratio": 1.2,
                "symmetry_assessment": "likely_symmetric"
            }
        }
        with open(analysis_output_path, 'w') as f:
            json.dump(basic_analysis, f, indent=2)
        logger.info("Simulator analysis completed")
        return
        
    command = [
        BLENDER_PATH, "--background", "--python", BLENDER_PROC_SCRIPT, "--",
        "--mode", "analyze",
        "--input", stl_path,
        "--output", analysis_output_path,
        "--params", empty_params,
        "--ring_size", "7.0",
        "--stone_carat", "1.0",
        "--stone_shape", "ROUND",
        "--metal", "GOLD"
    ]
    
    logger.debug(f"Analysis command: {' '.join(command[:8])}... [params truncated]")
    
    # Execute analyzer
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=120)
    
    logger.debug("[Analyzer stdout]\n%s", result.stdout)
    if result.stderr:
        logger.error("[Analyzer stderr]\n%s", result.stderr)
    
    if result.returncode != 0:
        raise RuntimeError(f"Analysis execution failed: {result.stderr}")
    
    if not os.path.exists(analysis_output_path):
        raise RuntimeError("Analyzer did not generate output file")
    
    logger.info("Geometric analysis completed successfully")

async def generate_refined_blueprint(user_refinement_prompt: str, previous_blueprint: dict, geometric_analysis: dict) -> dict:
    """
    V6.0 AI Critic: Generate refined blueprint based on analysis and user feedback.
    
    Args:
        user_refinement_prompt: User's refinement request
        previous_blueprint: Previous Master Blueprint
        geometric_analysis: Geometric analysis results
        
    Returns:
        Refined JSON Master Blueprint
    """
    logger.info("=== V6.0 AI CRITIC - REFINEMENT INTELLIGENCE ===")
    logger.info(f"Processing refinement request: '{user_refinement_prompt}'")
    
    # Format geometric analysis for the prompt
    analysis_summary = f"""
Vertex Count: {geometric_analysis.get('geometry_metrics', {}).get('vertex_count', 'N/A')}
Face Count: {geometric_analysis.get('geometry_metrics', {}).get('face_count', 'N/A')}
Complexity Level: {geometric_analysis.get('manufacturing_assessment', {}).get('complexity_level', 'N/A')}
Printability Score: {geometric_analysis.get('manufacturing_assessment', {}).get('printability_score', 'N/A')}
Dominant Dimension: {geometric_analysis.get('design_characteristics', {}).get('dominant_dimension', 'N/A')}
Symmetry: {geometric_analysis.get('design_characteristics', {}).get('symmetry_assessment', 'N/A')}
"""
    
    # Construct the refinement prompt
    refinement_prompt = REFINEMENT_PROMPT.format(
        previous_json_blueprint=json.dumps(previous_blueprint, indent=2),
        geometric_analysis_report=analysis_summary,
        user_refinement_prompt=user_refinement_prompt
    )
    
    if SANDBOX_MODE:
        # V6.0 Sandbox Mode - Use Hugging Face API
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}" if HUGGINGFACE_API_KEY else "",
            "Content-Type": "application/json"
        }
        
        hf_request = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a master jewelry designer. Respond only with valid JSON, no other text.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{refinement_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        try:
            logger.debug("Sending refinement request to Hugging Face")
            response = requests.post(LM_STUDIO_URL, headers=headers, json=hf_request, timeout=60)
            response.raise_for_status()
            
            hf_data = response.json()
            if isinstance(hf_data, list) and len(hf_data) > 0:
                blueprint_text = hf_data[0]['generated_text'].strip()
            else:
                blueprint_text = str(hf_data).strip()
                
            logger.debug(f"Hugging Face Refinement Response: {blueprint_text}")
            
            # Parse JSON Master Blueprint
            refined_blueprint = json.loads(blueprint_text)
            logger.info("V6.0 Refined Blueprint generated successfully via Hugging Face")
            
            return refined_blueprint
            
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error(f"Refinement failed via Hugging Face: {e}")
            logger.warning("Using fallback refinement")
            return create_fallback_refinement(user_refinement_prompt, previous_blueprint)
    
    else:
        # V7.0 Production Mode - Use LM Studio
        lm_request = {
            "model": "llama-3.1-8b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a master jewelry designer. Respond only with valid JSON, no other text."
                },
                {
                    "role": "user", 
                    "content": refinement_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            logger.debug("Sending refinement request to LM Studio")
            response = requests.post(LM_STUDIO_URL, json=lm_request, timeout=60)
            response.raise_for_status()
            
            lm_data = response.json()
            blueprint_text = lm_data['choices'][0]['message']['content'].strip()
            
            logger.debug(f"LLM Refinement Response: {blueprint_text}")
            
            # Parse JSON Master Blueprint
            refined_blueprint = json.loads(blueprint_text)
            logger.info("V7.0 Refined Blueprint generated successfully via LM Studio")
            
            return refined_blueprint
            
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error(f"Refinement failed via LM Studio: {e}")
            logger.warning("Using fallback refinement")
            return create_fallback_refinement(user_refinement_prompt, previous_blueprint)

def create_fallback_refinement(user_refinement_prompt: str, previous_blueprint: dict) -> dict:
    """Create a fallback refined blueprint when LLM is unavailable."""
    # Start with previous blueprint and make minor adjustments based on keywords
    refined = previous_blueprint.copy()
    
    prompt_lower = user_refinement_prompt.lower()
    
    # Update reasoning
    refined["reasoning"] = f"Fallback refinement based on request: '{user_refinement_prompt}'. Applied keyword-based adjustments to previous design parameters."
    
    # Apply simple keyword-based refinements
    if "thicker" in prompt_lower or "wider" in prompt_lower:
        refined["shank_parameters"]["thickness_mm"] = min(2.5, refined.get("shank_parameters", {}).get("thickness_mm", 2.0) + 0.2)
    elif "thinner" in prompt_lower or "narrower" in prompt_lower:
        refined["shank_parameters"]["thickness_mm"] = max(1.5, refined.get("shank_parameters", {}).get("thickness_mm", 2.0) - 0.2)
    
    if "more prongs" in prompt_lower or "six prong" in prompt_lower:
        refined["setting_parameters"]["prong_count"] = 6
    elif "fewer prongs" in prompt_lower or "four prong" in prompt_lower:
        refined["setting_parameters"]["prong_count"] = 4
    
    if "twist" in prompt_lower or "spiral" in prompt_lower:
        refined["artistic_modifier_parameters"]["twist_angle_degrees"] = 45
    elif "straight" in prompt_lower or "simple" in prompt_lower:
        refined["artistic_modifier_parameters"]["twist_angle_degrees"] = 0
    
    if "organic" in prompt_lower or "texture" in prompt_lower:
        refined["artistic_modifier_parameters"]["organic_displacement_strength"] = 0.0008
    elif "smooth" in prompt_lower or "clean" in prompt_lower:
        refined["artistic_modifier_parameters"]["organic_displacement_strength"] = 0.0
    
    return refined

async def execute_blender_processor(blueprint: dict, obj_path: str, output_path: str, user_specs: dict):
    """
    Stage 3: Execute V6.0/V7.0 State-of-the-Art Blender Engine.
    
    Args:
        blueprint: Complete Master Blueprint
        obj_path: Path to AI-generated base geometry
        output_path: Final STL output path
        user_specs: User specifications
    """
    logger.info("=== STAGE 3: V6.0/V7.0 STATE-OF-THE-ART BLENDER ENGINE ===")
    logger.info(f"Executing professional pipeline with: {obj_path}")
    
    # Prepare command - use simulator if Blender not available
    blueprint_json = json.dumps(blueprint)
    
    # Check if we should use simulator (when Blender is not available)
    use_simulator = not os.path.exists(BLENDER_PATH)
    
    if use_simulator:
        logger.info("Using Blender simulator for testing")
        command = [
            "python", BLENDER_SIM_SCRIPT, "--",
            "--mode", "generate",
            "--input", obj_path,
            "--output", output_path,
            "--params", blueprint_json,
            "--ring_size", str(user_specs['ring_size']),
            "--stone_carat", str(user_specs['stone_carat']),
            "--stone_shape", user_specs['stone_shape'],
            "--metal", user_specs['metal']
        ]
    else:
        command = [
            BLENDER_PATH, "--background", "--python", BLENDER_PROC_SCRIPT, "--",
            "--mode", "generate",
            "--input", obj_path,
            "--output", output_path,
            "--params", blueprint_json,
            "--ring_size", str(user_specs['ring_size']),
            "--stone_carat", str(user_specs['stone_carat']),
            "--stone_shape", user_specs['stone_shape'],
            "--metal", user_specs['metal']
        ]
    
    logger.debug(f"Execution command: {' '.join(command[:8])}... [params truncated]")
    
    # Execute processor
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=300)
    
    logger.debug("[Processor stdout]\n%s", result.stdout)
    if result.stderr:
        logger.error("[Processor stderr]\n%s", result.stderr)
    
    if result.returncode != 0:
        raise RuntimeError(f"Processor execution failed: {result.stderr}")
    
    if not os.path.exists(output_path):
        raise RuntimeError("Processor did not generate output file")
    
    mode_text = "simulation" if use_simulator else "Blender"
    logger.info(f"Master Blueprint execution completed successfully ({mode_text})")
    """
    Stage 3: Execute V7.0 State-of-the-Art Blender Engine.
    
    Args:
        blueprint: Complete Master Blueprint
        obj_path: Path to AI-generated base geometry
        output_path: Final STL output path
        user_specs: User specifications
    """
    logger.info("=== STAGE 3: V7.0 STATE-OF-THE-ART BLENDER ENGINE ===")
    logger.info(f"Executing professional pipeline with: {obj_path}")
    
    # Prepare command - use simulator if Blender not available
    blueprint_json = json.dumps(blueprint)
    
    # Check if we should use simulator (when Blender is not available)
    use_simulator = not os.path.exists(BLENDER_PATH)
    
    if use_simulator:
        logger.info("Using Blender simulator for testing")
        command = [
            "python", BLENDER_SIM_SCRIPT, "--",
            "--input", obj_path,
            "--output", output_path,
            "--params", blueprint_json,
            "--ring_size", str(user_specs['ring_size']),
            "--stone_carat", str(user_specs['stone_carat']),
            "--stone_shape", user_specs['stone_shape'],
            "--metal", user_specs['metal']
        ]
    else:
        command = [
            BLENDER_PATH, "--background", "--python", BLENDER_PROC_SCRIPT, "--",
            "--input", obj_path,
            "--output", output_path,
            "--params", blueprint_json,
            "--ring_size", str(user_specs['ring_size']),
            "--stone_carat", str(user_specs['stone_carat']),
            "--stone_shape", user_specs['stone_shape'],
            "--metal", user_specs['metal']
        ]
    
    logger.debug(f"Execution command: {' '.join(command[:8])}... [params truncated]")
    
    # Execute processor
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=300)
    
    logger.debug("[Processor stdout]\n%s", result.stdout)
    if result.stderr:
        logger.error("[Processor stderr]\n%s", result.stderr)
    
    if result.returncode != 0:
        raise RuntimeError(f"Processor execution failed: {result.stderr}")
    
    if not os.path.exists(output_path):
        raise RuntimeError("Processor did not generate output file")
    
    mode_text = "simulation" if use_simulator else "Blender"
    logger.info(f"Master Blueprint execution completed successfully ({mode_text})")

@app.post("/generate")
async def generate_design(request: Request):
    """
    Main endpoint for V6.0/V7.0 professional design generation.
    Orchestrates the complete state-of-the-art AI pipeline.
    """
    logger.info("=== V6.0/V7.0 PROFESSIONAL DESIGN GENERATION ===")
    logger.info(f"Architecture: {'V6.0 Sentient Cognitive Loop (Sandbox)' if SANDBOX_MODE else 'V7.0 Professional (Production)'}")
    
    try:
        data = await request.json()
        logger.debug(f'Request data: {data}')
        
        # Extract user inputs
        user_prompt = data.get("prompt", "elegant engagement ring")
        user_specs = {
            'ring_size': data.get("ring_size", 7.0),
            'stone_carat': data.get("stone_carat", 1.0),
            'stone_shape': data.get("stone_shape", "ROUND"),
            'metal': data.get("metal", "GOLD")
        }
        
        output_file = get_output_path(user_prompt)
        if os.path.exists(output_file):
            os.remove(output_file)
        
        # Stage 1: Generate Master Blueprint (LLM)
        blueprint = await generate_master_blueprint(user_prompt, user_specs)
        
        # Stage 2: Generate 3D base geometry (Shap-E)
        obj_path = await generate_3d_base_geometry(blueprint)
        
        # Stage 3: Execute Blender processor
        await execute_blender_processor(blueprint, obj_path, output_file, user_specs)
        
        logger.info("=== V6.0/V7.0 AUTONOMOUS DESIGN GENERATION COMPLETED ===")
        
        return JSONResponse({
            "file": os.path.basename(output_file),
            "message": f"{'V6.0 Sentient' if SANDBOX_MODE else 'V7.0 Professional'} design generated successfully",
            "blueprint_used": blueprint
        })
        
    except Exception as e:
        logger.exception('V6.0/V7.0 generation pipeline failed')
        return JSONResponse(status_code=500, content={
            "error": str(e),
            "message": f"{'V6.0 Sentient' if SANDBOX_MODE else 'V7.0 Professional'} generation failed"
        })

@app.post("/refine")
async def refine_design(request: Request):
    """
    V6.0 Sentient Cognitive Loop: Refine existing design based on geometric analysis and user feedback.
    """
    logger.info("=== V6.0 SENTIENT COGNITIVE LOOP - REFINEMENT ===")
    logger.info("Multi-pass iterative design process initiated")
    
    try:
        data = await request.json()
        logger.debug(f'Refinement request data: {data}')
        
        # Extract refinement inputs
        user_refinement_prompt = data.get("refinement_prompt", "make it more elegant")
        previous_blueprint = data.get("previous_blueprint", {})
        previous_stl_file = data.get("previous_stl_file", "")
        user_specs = {
            'ring_size': data.get("ring_size", 7.0),
            'stone_carat': data.get("stone_carat", 1.0),
            'stone_shape': data.get("stone_shape", "ROUND"),
            'metal': data.get("metal", "GOLD")
        }
        
        if not previous_blueprint:
            raise ValueError("Previous blueprint required for refinement")
        
        # Step 1: Geometric Analysis of Previous Design
        logger.info("=== STEP 1: BLENDER ENGINE GEOMETRIC ANALYSIS ===")
        previous_stl_path = os.path.join(OUTPUT_DIR, previous_stl_file)
        analysis_file = os.path.join(OUTPUT_DIR, f"analysis_{previous_stl_file.replace('.stl', '.json')}")
        
        # Execute Blender in analysis mode
        await execute_blender_analyzer(previous_stl_path, analysis_file)
        
        # Load analysis results
        with open(analysis_file, 'r') as f:
            geometric_analysis = json.load(f)
        
        logger.info("Geometric analysis completed successfully")
        
        # Step 2: Generate Refined Blueprint (LLM Critic)
        logger.info("=== STEP 2: AI CRITIC - REFINEMENT ANALYSIS ===")
        refined_blueprint = await generate_refined_blueprint(
            user_refinement_prompt, previous_blueprint, geometric_analysis
        )
        
        # Step 3: Generate New 3D Base Geometry
        obj_path = await generate_3d_base_geometry(refined_blueprint)
        
        # Step 4: Execute Blender Processor for Refined Design
        output_file = get_output_path(f"refined_{user_refinement_prompt}")
        if os.path.exists(output_file):
            os.remove(output_file)
            
        await execute_blender_processor(refined_blueprint, obj_path, output_file, user_specs)
        
        logger.info("=== V6.0 SENTIENT COGNITIVE LOOP COMPLETED ===")
        
        return JSONResponse({
            "file": os.path.basename(output_file),
            "message": "V6.0 Sentient refinement completed successfully",
            "refined_blueprint": refined_blueprint,
            "geometric_analysis": geometric_analysis
        })
        
    except Exception as e:
        logger.exception('V6.0 refinement pipeline failed')
        return JSONResponse(status_code=500, content={
            "error": str(e),
            "message": "V6.0 Sentient refinement failed"
        })

@app.get("/output/{filename}")
async def serve_stl(filename: str):
    """Serve generated STL files."""
    logger.debug('Received STL file request: %s', filename)
    try:
        if not filename.startswith("output_") or not filename.endswith(".stl"):
            logger.error(f"Rejected STL request: {filename} (invalid pattern)")
            return Response(status_code=400)
        file_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(file_path):
            logger.info(f"Serving STL from output dir: {file_path}")
            return FileResponse(file_path, media_type="application/sla")
        else:
            logger.error(f"STL file not found in output dir: {filename}")
            return Response(status_code=404)
    except Exception as e:
        logger.exception('Exception serving STL file')
        return Response(content=str(e), status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if SANDBOX_MODE:
        return {
            "service": "V6.0 Sentient Cognitive Loop",
            "status": "running",
            "version": "6.0",
            "mode": "sandbox",
            "architecture": "Multi-Pass Iterative AI Pipeline"
        }
    else:
        return {
            "service": "V7.0 Backend Orchestrator", 
            "status": "running",
            "version": "7.0",
            "mode": "production",
            "architecture": "Two-Stage Professional AI Pipeline"
        }

# V24 Enhancement: Add health check endpoint
@app.get("/health")
async def health_check():
    """V24 Enhanced health check endpoint."""
    import time
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "V24 Backend Orchestrator",
        "version": "24.0",
        "mode": "sandbox" if SANDBOX_MODE else "production",
        "lm_studio_configured": bool(LM_STUDIO_URL),
        "external_ai_configured": bool(EXTERNAL_AI_URL),
        "blender_path_configured": bool(BLENDER_PATH),
        "output_directory": OUTPUT_DIR
    }
    
    # Test LM Studio connectivity if not in sandbox mode
    if not SANDBOX_MODE and LM_STUDIO_URL:
        try:
            test_response = requests.get(LM_STUDIO_URL.replace('/chat/completions', '/models'), timeout=5)
            health_status["lm_studio_reachable"] = test_response.status_code == 200
        except:
            health_status["lm_studio_reachable"] = False
            health_status["status"] = "degraded"
    
    return health_status

@app.get("/")
async def root():
    if SANDBOX_MODE:
        return {
            "service": "V6.0 Sentient Cognitive Loop",
            "version": "6.0",
            "mode": "sandbox",
            "status": "Cognitive Loop Architecture Active - Verifiable Testing Environment"
        }
    else:
        return {
            "service": "V7.0 Backend Orchestrator",
            "version": "7.0", 
            "mode": "production",
            "status": "Professional Integration Active"
        }
