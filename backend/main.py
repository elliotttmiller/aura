"""
Aura V7.0 Backend Orchestrator - Professional AI Pipeline
========================================================

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

app = FastAPI(title="Aura V7.0 Backend Orchestrator", version="7.0")

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# V7.0 Configuration - External AI Environment
BLENDER_PATH = os.environ.get("BLENDER_PATH", r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe")
BLENDER_PROC_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blender_proc.py"))
BLENDER_SIM_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blender_sim.py"))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
LM_STUDIO_URL = os.environ.get("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")

# V7.0: External AI Environment (User-Managed Shap-E Installation)
EXTERNAL_AI_URL = os.environ.get("EXTERNAL_AI_URL", "http://localhost:8002")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Master Blueprint Prompt Template for Llama 3.1
MASTER_BLUEPRINT_PROMPT = """You are a world-class, expert jewelry CAD designer and system architect. Your mission is to translate a user's creative request into a complete, precise, and manufacturable 3D design blueprint.

You must generate a single, valid JSON object that contains ALL the necessary parameters to construct the final piece. Do not include any other text, explanations, or markdown formatting. Adhere strictly to the schema.

This is the required JSON Master Blueprint schema:
{{
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

Analyze the following user request and generate the complete JSON Master Blueprint.

USER'S REQUEST: "{user_prompt}"
TECHNICAL SPECIFICATIONS:
- Ring Size (US): {ring_size}
- Metal: {metal}
- Stone Shape: {stone_shape}
- Stone Carat: {stone_carat}"""

def get_output_path(prompt: str) -> str:
    """Generate output file path based on prompt."""
    safe_name = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = "_".join(safe_name.split())[:40]
    return os.path.join(OUTPUT_DIR, f"output_{safe_name}.stl")

async def generate_master_blueprint(user_prompt: str, user_specs: dict) -> dict:
    """
    Stage 1: Generate Master Blueprint using Llama 3.1 via LM Studio.
    
    Args:
        user_prompt: User's creative request
        user_specs: Technical specifications
        
    Returns:
        Parsed JSON Master Blueprint
    """
    logger.info("=== STAGE 1: AI SYSTEM ARCHITECT (LLAMA 3.1) ===")
    logger.info(f"Generating Master Blueprint for: '{user_prompt}'")
    
    # Construct the master prompt
    master_prompt = MASTER_BLUEPRINT_PROMPT.format(
        user_prompt=user_prompt,
        ring_size=user_specs['ring_size'],
        metal=user_specs['metal'],
        stone_shape=user_specs['stone_shape'],
        stone_carat=user_specs['stone_carat']
    )
    
    # Prepare LM Studio request
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
        logger.info("Master Blueprint generated successfully")
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

async def execute_blender_processor(blueprint: dict, obj_path: str, output_path: str, user_specs: dict):
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
    Main endpoint for V7.0 professional design generation.
    Orchestrates the complete state-of-the-art AI pipeline.
    """
    logger.info("=== AURA V7.0 PROFESSIONAL DESIGN GENERATION ===")
    logger.info("Architecture: State-of-the-art pipeline aligned with OpenAI best practices")
    
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
        
        logger.info("=== V5.0 AUTONOMOUS DESIGN GENERATION COMPLETED ===")
        
        return JSONResponse({
            "file": os.path.basename(output_file),
            "message": "V5.0 autonomous design generated successfully",
            "blueprint_used": blueprint
        })
        
    except Exception as e:
        logger.exception('V5.0 generation pipeline failed')
        return JSONResponse(status_code=500, content={
            "error": str(e),
            "message": "V5.0 autonomous generation failed"
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
    return {
        "service": "Aura V5.0 Backend Orchestrator",
        "status": "running",
        "version": "5.0",
        "architecture": "Two-Stage Autonomous AI Pipeline"
    }

@app.get("/")
async def root():
    return {
        "service": "Aura V5.0 Backend Orchestrator",
        "version": "5.0",
        "status": "Autonomous Cognitive Architecture Active"
    }
