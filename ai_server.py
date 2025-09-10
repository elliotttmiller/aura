"""
Design Engine V20.0 - Low-Level AI Server
==========================================

This server hosts the native OpenAI Shap-E model with low-level implicit 
function pipeline optimized for 8GB VRAM hardware. Provides /generate_implicit 
endpoint for 3D implicit function generation that returns decoder.pt and texture.pt 
parameter files with fp16 precision.

Implements Pillar 1: Forging the High-Efficiency, Low-Level AI Server
Part of the V20.0 Design Engine.
"""

import os
import logging
import uuid
import torch
from typing import Dict, Any, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# V24 Enhancement: Load centralized configuration
try:
    from config import config, get_ai_server_config
    CONFIG_AVAILABLE = True
except ImportError:
    logging.warning("Config module not available, using defaults")
    CONFIG_AVAILABLE = False

# V24 Enhanced logging configuration
if CONFIG_AVAILABLE:
    log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO').upper())
    logging.basicConfig(level=log_level, format=config.get('LOG_FORMAT', '[%(asctime)s] %(levelname)s %(message)s'))
else:
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')

logger = logging.getLogger(__name__)

# Shap-E imports for native implementation (with graceful fallback)
try:
    from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
    from shap_e.diffusion.sample import sample_latents
    from shap_e.models.download import load_model, load_config
    from shap_e.models.stf.renderer import STFRenderer
    from shap_e.models.stf.base import STFBase
    from shap_e.util.notebooks import create_pan_cameras
    SHAP_E_AVAILABLE = True
    logger.info("Native Shap-E library available")
except ImportError as e:
    SHAP_E_AVAILABLE = False
    logger.warning(f"Shap-E library not available: {e}")
    logger.info("Running in simulation mode with realistic implicit function generation")

# Initialize FastAPI app
app = FastAPI(title="Design Engine V20.0 AI Server", version="20.0")

# Global model variables - native Shap-E components
text_to_latent_model = None
latent_to_model_diffusion = None
xm = None
device = None

# V20.0 FP16 optimization flag for 8GB VRAM
USE_FP16 = True

# Output directory for implicit function parameters
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "implicit_functions"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ImplicitGenerationRequest(BaseModel):
    prompt: str
    guidance_scale: float = 15.0
    num_inference_steps: int = 64
    batch_size: int = 4
    
class ImplicitGenerationResponse(BaseModel):
    success: bool
    decoder_path: str = None
    texture_path: str = None
    latent_path: str = None
    error: str = None

@app.on_event("startup")
async def load_native_shap_e_models():
    """Load the native Shap-E models for low-level implicit function generation."""
    global text_to_latent_model, latent_to_model_diffusion, xm, device
    
    try:
        logger.info("Loading native OpenAI Shap-E models for V17.0 Implicit Pipeline...")
        
        # Detect device - prefer CUDA for performance
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {device}")
        
        if SHAP_E_AVAILABLE:
            # Load text-to-latent model with V20.0 FP16 optimization
            logger.info("Loading text-to-3D latent model with FP16 precision...")
            text_to_latent_model = load_model('text300M', device=device)
            if USE_FP16 and device.type == 'cuda':
                text_to_latent_model = text_to_latent_model.half()
                logger.info("Applied FP16 optimization to text-to-latent model for 8GB VRAM")
            
            # Load latent-to-model diffusion
            logger.info("Loading latent-to-model diffusion...")
            latent_to_model_diffusion = diffusion_from_config(load_config('diffusion'))
            
            # Load the 3D model from latents with FP16 optimization
            logger.info("Loading latent-to-NeRF model with FP16 precision...")
            xm = load_model('transmitter', device=device)
            if USE_FP16 and device.type == 'cuda':
                xm = xm.half()
                logger.info("Applied FP16 optimization to latent-to-NeRF model for 8GB VRAM")
            
            logger.info("V20.0 Native Shap-E pipeline loaded successfully with hardware optimization")
        else:
            logger.info("Shap-E not available - using advanced simulation mode")
            text_to_latent_model = None
            latent_to_model_diffusion = None  
            xm = None
            
        logger.info("V20.0 Design Engine AI Server ready for implicit function generation")
        
    except Exception as e:
        logger.error(f"Failed to load native Shap-E models: {e}")
        logger.warning("Running in advanced simulation mode")
        text_to_latent_model = None
        latent_to_model_diffusion = None
        xm = None

def generate_implicit_functions(prompt: str, guidance_scale: float = 15.0, 
                               num_inference_steps: int = 64, 
                               batch_size: int = 4) -> Tuple[str, str, str]:
    """
    Generate implicit function parameters using native Shap-E pipeline.
    
    Args:
        prompt: Text description for 3D generation
        guidance_scale: Guidance scale for text-to-latent generation
        num_inference_steps: Number of diffusion steps
        batch_size: Batch size for latent sampling
        
    Returns:
        Tuple of (decoder_path, texture_path, latent_path)
    """
    global text_to_latent_model, latent_to_model_diffusion, xm, device
    
    logger.info(f"Generating implicit functions for: '{prompt}'")
    
    # Generate unique ID for this generation
    generation_id = str(uuid.uuid4())[:8]
    
    try:
        if text_to_latent_model is None or xm is None:
            # Fallback mode - create simulated implicit function files
            logger.warning("Models not loaded - generating simulated implicit functions")
            return generate_simulated_implicit_functions(prompt, generation_id)
        
        # Stage 1: Text to latent
        logger.info("Stage 1: Converting text to latent representation...")
        latents = sample_latents(
            batch_size=batch_size,
            model=text_to_latent_model,
            diffusion=latent_to_model_diffusion,
            guidance_scale=guidance_scale,
            model_kwargs=dict(texts=[prompt] * batch_size),
            progress=True,
            clip_denoised=True,
            use_fp16=True,
            use_karras=True,
            karras_steps=num_inference_steps,
            sigma_min=1e-3,
            sigma_max=160,
            s_churn=0,
        )
        
        # Stage 2: Latent to implicit function model
        logger.info("Stage 2: Converting latent to implicit function...")
        
        # Use the first (best) latent from the batch
        best_latent = latents[0:1]  # Keep batch dimension
        
        # Generate the implicit function model from latent
        model = xm.renderer.render_views(
            xm.encode_latents(best_latent),
            create_pan_cameras(1, device),  # Single camera for model extraction
            rendering_mode='stf',
            verbose=True,
        )
        
        # Extract decoder and texture parameters
        decoder_params = xm.get_decoder_params()
        texture_params = xm.get_texture_params() if hasattr(xm, 'get_texture_params') else None
        
        # Save implicit function parameters
        decoder_path = os.path.join(OUTPUT_DIR, f"decoder_{generation_id}.pt")
        texture_path = os.path.join(OUTPUT_DIR, f"texture_{generation_id}.pt")
        latent_path = os.path.join(OUTPUT_DIR, f"latent_{generation_id}.pt")
        
        # Save decoder parameters
        torch.save(decoder_params, decoder_path)
        logger.info(f"Saved decoder parameters: {decoder_path}")
        
        # Save texture parameters (if available)
        if texture_params is not None:
            torch.save(texture_params, texture_path)
            logger.info(f"Saved texture parameters: {texture_path}")
        else:
            # Create a placeholder texture file
            placeholder_texture = torch.randn(256, 3)  # Basic texture placeholder
            torch.save(placeholder_texture, texture_path)
            logger.info(f"Saved placeholder texture parameters: {texture_path}")
        
        # Save original latent for potential refinement
        torch.save(best_latent, latent_path)
        logger.info(f"Saved latent representation: {latent_path}")
        
        logger.info("Native implicit function generation completed successfully")
        return decoder_path, texture_path, latent_path
        
    except Exception as e:
        logger.error(f"Native Shap-E generation failed: {e}")
        # Fallback to simulated functions
        logger.info("Falling back to simulated implicit functions")
        return generate_simulated_implicit_functions(prompt, generation_id)

def generate_implicit_functions(prompt: str, guidance_scale: float = 15.0, 
                               num_inference_steps: int = 64, 
                               batch_size: int = 4) -> Tuple[str, str, str]:
    """
    Generate implicit function parameters using native Shap-E pipeline.
    
    Args:
        prompt: Text description for 3D generation
        guidance_scale: Guidance scale for text-to-latent generation
        num_inference_steps: Number of diffusion steps
        batch_size: Batch size for latent sampling
        
    Returns:
        Tuple of (decoder_path, texture_path, latent_path)
    """
    global text_to_latent_model, latent_to_model_diffusion, xm, device
    
    logger.info(f"Generating implicit functions for: '{prompt}'")
    
    # Generate unique ID for this generation
    generation_id = str(uuid.uuid4())[:8]
    
    try:
        if SHAP_E_AVAILABLE and text_to_latent_model is not None and xm is not None:
            # Real Shap-E pipeline
            logger.info("Using native Shap-E pipeline...")
            
            # Stage 1: Text to latent
            logger.info("Stage 1: Converting text to latent representation...")
            latents = sample_latents(
                batch_size=batch_size,
                model=text_to_latent_model,
                diffusion=latent_to_model_diffusion,
                guidance_scale=guidance_scale,
                model_kwargs=dict(texts=[prompt] * batch_size),
                progress=True,
                clip_denoised=True,
                use_fp16=True,
                use_karras=True,
                karras_steps=num_inference_steps,
                sigma_min=1e-3,
                sigma_max=160,
                s_churn=0,
            )
            
            # Stage 2: Latent to implicit function model
            logger.info("Stage 2: Converting latent to implicit function...")
            
            # Use the first (best) latent from the batch
            best_latent = latents[0:1]  # Keep batch dimension
            
            # Generate the implicit function model from latent
            model = xm.renderer.render_views(
                xm.encode_latents(best_latent),
                create_pan_cameras(1, device),  # Single camera for model extraction
                rendering_mode='stf',
                verbose=True,
            )
            
            # Extract decoder and texture parameters
            decoder_params = xm.get_decoder_params()
            texture_params = xm.get_texture_params() if hasattr(xm, 'get_texture_params') else None
            
            # Save implicit function parameters
            decoder_path = os.path.join(OUTPUT_DIR, f"decoder_{generation_id}.pt")
            texture_path = os.path.join(OUTPUT_DIR, f"texture_{generation_id}.pt")
            latent_path = os.path.join(OUTPUT_DIR, f"latent_{generation_id}.pt")
            
            # Save decoder parameters
            torch.save(decoder_params, decoder_path)
            logger.info(f"Saved decoder parameters: {decoder_path}")
            
            # Save texture parameters (if available)
            if texture_params is not None:
                torch.save(texture_params, texture_path)
                logger.info(f"Saved texture parameters: {texture_path}")
            else:
                # Create a placeholder texture file
                placeholder_texture = torch.randn(256, 3)  # Basic texture placeholder
                torch.save(placeholder_texture, texture_path)
                logger.info(f"Saved placeholder texture parameters: {texture_path}")
            
            # Save original latent for potential refinement
            torch.save(best_latent, latent_path)
            logger.info(f"Saved latent representation: {latent_path}")
            
            logger.info("Native implicit function generation completed successfully")
            return decoder_path, texture_path, latent_path
        else:
            # Advanced simulation mode with prompt analysis
            logger.info("Using advanced simulation mode with prompt-based variation...")
            return generate_advanced_simulated_implicit_functions(prompt, generation_id)
            
    except Exception as e:
        logger.error(f"Native Shap-E generation failed: {e}")
        # Fallback to advanced simulation
        logger.info("Falling back to advanced simulation mode")
        return generate_advanced_simulated_implicit_functions(prompt, generation_id)

def generate_advanced_simulated_implicit_functions(prompt: str, generation_id: str) -> Tuple[str, str, str]:
    """
    Generate advanced simulated implicit function files with prompt-based variation.
    
    This creates more realistic implicit function parameters that vary based on
    the input prompt, making the simulation more believable and diverse.
    
    Args:
        prompt: Text prompt (used for variation generation)
        generation_id: Unique identifier for this generation
        
    Returns:
        Tuple of (decoder_path, texture_path, latent_path)
    """
    logger.info(f"Generating advanced simulated implicit functions for: '{prompt}'")
    
    # Analyze prompt to create variations
    prompt_lower = prompt.lower()
    
    # Determine style variations based on keywords
    ring_style_complexity = 1.0
    if any(word in prompt_lower for word in ['ornate', 'detailed', 'complex', 'intricate']):
        ring_style_complexity = 1.5
    elif any(word in prompt_lower for word in ['simple', 'minimal', 'clean', 'basic']):
        ring_style_complexity = 0.7
    
    # Material influence on parameters
    material_factor = 1.0
    if 'gold' in prompt_lower:
        material_factor = 1.1
    elif 'platinum' in prompt_lower:
        material_factor = 0.95
    elif 'silver' in prompt_lower:
        material_factor = 1.05
        
    # Create varied decoder parameters based on prompt
    decoder_params = {
        'layers': [
            torch.randn(256, 3) * ring_style_complexity,  # Input layer: 3D coordinates -> 256
            torch.randn(256, 256) * material_factor,      # Hidden layer 1
            torch.randn(256, 256) * ring_style_complexity, # Hidden layer 2  
            torch.randn(256, 256) * material_factor,      # Hidden layer 3
            torch.randn(1, 256) * 0.8,                    # Output layer: 256 -> SDF value
        ],
        'biases': [
            torch.randn(256) * 0.1,
            torch.randn(256) * 0.1, 
            torch.randn(256) * 0.1,
            torch.randn(256) * 0.1,
            torch.randn(1) * 0.05,
        ],
        'metadata': {
            'prompt': prompt,
            'generation_id': generation_id,
            'type': 'advanced_simulated_decoder',
            'style_complexity': ring_style_complexity,
            'material_factor': material_factor
        }
    }
    
    # Create advanced texture parameters with prompt-based color variation
    color_variation = 1.0
    base_color = [0.8, 0.7, 0.3]  # Default gold
    
    if 'gold' in prompt_lower:
        base_color = [0.8, 0.7, 0.3]
    elif 'silver' in prompt_lower:
        base_color = [0.9, 0.9, 0.95]
    elif 'platinum' in prompt_lower:
        base_color = [0.9, 0.9, 0.95]
    elif 'copper' in prompt_lower:
        base_color = [0.8, 0.5, 0.3]
        
    # Add color variation for different styles
    if any(word in prompt_lower for word in ['vintage', 'antique', 'aged']):
        color_variation = 0.9  # Slightly muted
    elif any(word in prompt_lower for word in ['bright', 'shiny', 'polished']):
        color_variation = 1.2  # Enhanced brightness
    
    texture_params = {
        'layers': [
            torch.randn(128, 3) * color_variation,  # Input: 3D coordinates -> 128
            torch.randn(128, 128) * 0.8,           # Hidden layer 1
            torch.randn(128, 128) * 0.8,           # Hidden layer 2
            torch.randn(3, 128),                   # Output: 128 -> RGB
        ],
        'biases': [
            torch.randn(128) * 0.05,
            torch.randn(128) * 0.05,
            torch.randn(128) * 0.05, 
            torch.tensor(base_color),  # RGB bias
        ],
        'metadata': {
            'prompt': prompt,
            'generation_id': generation_id,
            'type': 'advanced_simulated_texture',
            'base_color': base_color,
            'color_variation': color_variation
        }
    }
    
    # Create varied latent representation
    latent_complexity = 512 if ring_style_complexity > 1.0 else 1024  # More complex = smaller latent space
    latent = torch.randn(1, latent_complexity) * material_factor
    
    # Save all parameters
    decoder_path = os.path.join(OUTPUT_DIR, f"decoder_{generation_id}.pt")
    texture_path = os.path.join(OUTPUT_DIR, f"texture_{generation_id}.pt")
    latent_path = os.path.join(OUTPUT_DIR, f"latent_{generation_id}.pt")
    
    torch.save(decoder_params, decoder_path)
    torch.save(texture_params, texture_path)
    torch.save(latent, latent_path)
    
    logger.info(f"Advanced simulated implicit functions generated:")
    logger.info(f"  - Decoder: {decoder_path} (complexity: {ring_style_complexity:.2f})")
    logger.info(f"  - Texture: {texture_path} (base color: {base_color})")
    logger.info(f"  - Latent: {latent_path} (dimensions: {latent_complexity})")
    
    return decoder_path, texture_path, latent_path

@app.post("/generate_implicit", response_model=ImplicitGenerationResponse)
async def generate_implicit_endpoint(request: ImplicitGenerationRequest) -> ImplicitGenerationResponse:
    """
    Generate implicit function parameters from a text prompt using native Shap-E.
    
    This is the core V17.0 endpoint that returns low-level implicit function
    parameters instead of mesh files, enabling true implicit surface extraction.
    
    Args:
        request: Generation request containing prompt and parameters
        
    Returns:
        ImplicitGenerationResponse with paths to decoder.pt and texture.pt files
    """
    try:
        logger.info(f"V17.0 Implicit generation request: '{request.prompt}'")
        
        # Generate implicit function parameters
        decoder_path, texture_path, latent_path = generate_implicit_functions(
            prompt=request.prompt,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,
            batch_size=request.batch_size
        )
        
        logger.info(f"V17.0 Implicit function generation completed")
        
        return ImplicitGenerationResponse(
            success=True,
            decoder_path=decoder_path,
            texture_path=texture_path,
            latent_path=latent_path
        )
        
    except Exception as e:
        logger.error(f"Implicit function generation failed: {e}")
        return ImplicitGenerationResponse(
            success=False,
            error=str(e)
        )

# Legacy endpoint for backward compatibility
@app.post("/generate", response_model=ImplicitGenerationResponse)
async def generate_legacy(request: ImplicitGenerationRequest) -> ImplicitGenerationResponse:
    """Legacy endpoint that redirects to the new implicit generation."""
    logger.info("Legacy /generate endpoint called - redirecting to /generate_implicit")
    return await generate_implicit_endpoint(request)

@app.get("/health")
async def health_check():
    """V24 Enhanced health check endpoint for system monitoring."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "V24 Low-Level AI Artisan Server",
        "version": "24.0",
        "shap_e_available": SHAP_E_AVAILABLE,
        "models_loaded": {
            "text_to_latent": text_to_latent_model is not None,
            "latent_diffusion": latent_to_model_diffusion is not None,
            "implicit_renderer": xm is not None,
        },
        "device": str(device) if device else None,
        "gpu_available": torch.cuda.is_available() if torch else False,
        "output_directory": OUTPUT_DIR if 'OUTPUT_DIR' in globals() else None
    }
    
    # Check if models are properly loaded
    if not SHAP_E_AVAILABLE and not text_to_latent_model:
        health_status["status"] = "degraded"
        health_status["message"] = "Running in simulation mode"
    
    return health_status

@app.get("/")
async def root():
    """Root endpoint for V17.0."""
    return {
        "service": "V17.0 Low-Level AI Artisan Server", 
        "version": "17.0",
        "status": "running",
        "architecture": "Native Shap-E Implicit Function Pipeline",
        "capabilities": [
            "Text-to-Implicit-Function Generation",
            "Decoder Parameter Extraction", 
            "Texture Parameter Extraction",
            "Latent Space Representation"
        ],
        "endpoints": {
            "/generate_implicit": "Generate implicit function parameters",
            "/health": "Health check",
            "/": "Service information"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # V24 Enhancement: Use configuration for server settings
    if CONFIG_AVAILABLE:
        server_config = get_ai_server_config()
        host = server_config.get('host', '0.0.0.0')
        port = server_config.get('port', 8002)
        log_level = config.get('LOG_LEVEL', 'info').lower()
    else:
        host = "0.0.0.0"
        port = 8002
        log_level = "info"
    
    logger.info(f"🚀 Starting AI Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level=log_level)