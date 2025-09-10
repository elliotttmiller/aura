"""
Aura V6.0 Sandbox 3D Server - Verifiable Testing Environment
===========================================================

This lightweight FastAPI server mimics the real ai_server.py for truthful
end-to-end testing. It provides the same /generate endpoint interface but
uses pre-existing test assets instead of running real AI models.

Part of the V6.0 Sentient Cognitive Loop Architecture.
"""

import os
import logging
import shutil
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Aura V6.0 Sandbox 3D Server", version="6.0")

# Output directory for generated models
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "generated"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test assets directory
TEST_ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "test_assets"))
os.makedirs(TEST_ASSETS_DIR, exist_ok=True)

class GenerationRequest(BaseModel):
    prompt: str
    guidance_scale: float = 15.0
    num_inference_steps: int = 64

class GenerationResponse(BaseModel):
    success: bool
    obj_path: str = None
    error: str = None

def ensure_test_cube_exists() -> str:
    """
    Ensure test_cube.obj exists in test_assets directory.
    Creates it if it doesn't exist.
    """
    test_cube_path = os.path.join(TEST_ASSETS_DIR, "test_cube.obj")
    
    if not os.path.exists(test_cube_path):
        logger.info("Creating test_cube.obj for sandbox mode")
        
        cube_content = """# Aura V6.0 Sandbox Test Cube
# Simple geometric test asset for verifiable sandbox testing
o TestCube

# Vertices
v -0.008 -0.008 -0.008
v  0.008 -0.008 -0.008
v  0.008  0.008 -0.008
v -0.008  0.008 -0.008
v -0.008 -0.008  0.008
v  0.008 -0.008  0.008
v  0.008  0.008  0.008
v -0.008  0.008  0.008

# Faces
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 5 1 4 8
"""
        
        with open(test_cube_path, 'w') as f:
            f.write(cube_content)
        
        logger.info(f"Created test cube: {test_cube_path}")
    
    return test_cube_path

def generate_sandbox_obj(prompt: str) -> str:
    """
    Generate a sandbox .obj file by copying the test cube with a unique name.
    This provides verifiable, predictable testing behavior.
    """
    # Ensure test cube exists
    test_cube_path = ensure_test_cube_exists()
    
    # Generate unique filename based on prompt
    safe_prompt = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_prompt = "_".join(safe_prompt.split())[:20]
    model_id = str(uuid.uuid4())[:8]
    obj_filename = f"sandbox_{safe_prompt}_{model_id}.obj"
    obj_path = os.path.join(OUTPUT_DIR, obj_filename)
    
    # Copy test cube to new location
    shutil.copy2(test_cube_path, obj_path)
    
    # Add prompt comment to the file
    with open(obj_path, 'r') as f:
        content = f.read()
    
    with open(obj_path, 'w') as f:
        f.write(f"# Sandbox generated model for prompt: {prompt}\n")
        f.write(content)
    
    logger.info(f"Generated sandbox .obj file: {obj_path}")
    return obj_path

@app.post("/generate", response_model=GenerationResponse)
async def generate_3d_model(request: GenerationRequest) -> GenerationResponse:
    """
    Generate a 3D model in sandbox mode using test assets.
    
    Args:
        request: Generation request containing the prompt and parameters
        
    Returns:
        GenerationResponse with success status and obj_path or error
    """
    try:
        logger.info(f"V6.0 Sandbox: Generating test model for prompt: '{request.prompt}'")
        
        # Generate sandbox model by copying test asset
        obj_path = generate_sandbox_obj(request.prompt)
        
        logger.info(f"V6.0 Sandbox: Model generation completed: {obj_path}")
        
        return GenerationResponse(
            success=True,
            obj_path=obj_path
        )
        
    except Exception as e:
        logger.error(f"Sandbox 3D model generation failed: {e}")
        return GenerationResponse(
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": "sandbox",
        "service": "V6.0 Sandbox 3D Server"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Aura V6.0 Sandbox 3D Server",
        "version": "6.0", 
        "mode": "sandbox",
        "status": "running - verifiable testing environment"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")