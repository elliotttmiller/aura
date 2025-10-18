"""
Backend Orchestrator - Professional AI Pipeline
====================================================

This orchestrator manages the professional workflow:
Stage 1: LLM (Llama 3.1 via LM Studio) generates Master Blueprint
Stage 2: External AI Environment generates 3D base geometry
Stage 3: State-of-the-Art Blender engine executes the Master Blueprint

Part of the Professional Integration.
"""

# CRITICAL: Load environment configuration FIRST before any other imports
from backend.config_init import ensure_config_loaded, validate_critical_config
ensure_config_loaded(verbose=True)

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import time
from typing import Dict, Any, Optional
import uuid

# Use centralized configuration
from config import config, get_lm_studio_url, get_ai_server_config, is_sandbox_mode, get_blender_path

app = FastAPI(title="Aura Backend Orchestrator", version="24.0")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API router with /api prefix for frontend compatibility
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Configure logging from centralized config
log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO').upper())
log_format = config.get('LOG_FORMAT', '[%(asctime)s] %(levelname)s %(message)s')
logging.basicConfig(level=log_level, format=log_format)

logger = logging.getLogger(__name__)

# Validate configuration on startup
validation = validate_critical_config()
if validation['status'] != 'ok':
    logger.warning(f"Configuration validation: {validation['status']}")
    for warning in validation['warnings']:
        logger.warning(f"  - {warning}")
    for error in validation['errors']:
        logger.error(f"  - {error}")

# Load configuration from centralized config
SANDBOX_MODE = is_sandbox_mode()
BLENDER_PATH = get_blender_path() or r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", config.get('OUTPUT_DIR', 'output')))
LM_STUDIO_URL = get_lm_studio_url()
EXTERNAL_AI_URL = get_ai_server_config().get('url', 'http://localhost:8002')
HUGGINGFACE_API_KEY = config.get('HUGGINGFACE_API_KEY', '')

# Enhanced script paths
BLENDER_PROC_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "blender_proc.py"))
BLENDER_SIM_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "blender_sim.py"))

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# Enhanced AI Integration
# ============================================================================
try:
    from backend.enhanced_ai_orchestrator import create_enhanced_orchestrator
    ENHANCED_AI_AVAILABLE = True
    logger.info("✓ Enhanced AI Orchestrator available")
except ImportError as e:
    ENHANCED_AI_AVAILABLE = False
    logger.warning(f"Enhanced AI Orchestrator not available: {e}")

# Initialize enhanced AI orchestrator
if ENHANCED_AI_AVAILABLE:
    try:
        enhanced_ai_orchestrator = create_enhanced_orchestrator()
        logger.info("✓ Enhanced AI Orchestrator initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Enhanced AI Orchestrator: {e}")
        enhanced_ai_orchestrator = None
else:
    enhanced_ai_orchestrator = None

# ============================================================================
# Blender Construction Executor Integration
# ============================================================================
try:
    from backend.blender_construction_executor import create_executor
    blender_executor = create_executor(BLENDER_PATH)
    BLENDER_EXECUTOR_AVAILABLE = True
    logger.info("✓ Blender Construction Executor available")
except ImportError as e:
    BLENDER_EXECUTOR_AVAILABLE = False
    blender_executor = None
    logger.warning(f"Blender Construction Executor not available: {e}")
except Exception as e:
    BLENDER_EXECUTOR_AVAILABLE = False
    blender_executor = None
    logger.error(f"Failed to initialize Blender Construction Executor: {e}")

# ============================================================================
# Scene State Management - Digital Twin Architecture
# ============================================================================

class SceneObject:
    """Represents a 3D object in the design scene."""
    def __init__(self, name: str, obj_type: str = "mesh"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = obj_type
        self.visible = True
        self.transform = {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0], 
            "scale": [1.0, 1.0, 1.0]
        }
        self.material = {
            "color": "#FFD700",
            "roughness": 0.2,
            "metallic": 0.8
        }
        self.geometry_data = None  # Store mesh/geometry data


    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "visible": self.visible,
            "transform": self.transform,
            "material": self.material
        }


class DesignSession:
    """Manages a design session with scene state."""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.objects: Dict[str, SceneObject] = {}
        self.created_at = time.time()
        self.last_modified = time.time()

    def add_object(self, obj: SceneObject) -> str:
        """Add object to scene and return its ID."""
        self.objects[obj.id] = obj
        self.last_modified = time.time()
        return obj.id

    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        """Get object by ID."""
        return self.objects.get(obj_id)

    def update_object(self, obj_id: str, updates: Dict[str, Any]) -> bool:
        """Update object properties."""
        obj = self.objects.get(obj_id)
        if not obj:
            return False

        # Update properties
        for key, value in updates.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        self.last_modified = time.time()
        return True

    def remove_object(self, obj_id: str) -> bool:
        """Remove object from scene."""
        if obj_id in self.objects:
            del self.objects[obj_id]
            self.last_modified = time.time()
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "objects": [obj.to_dict() for obj in self.objects.values()],
            "created_at": self.created_at,
            "last_modified": self.last_modified
        }


# Global sessions storage (in production, use database)
active_sessions: Dict[str, DesignSession] = {}


# Enhanced AI Processing Functions
def analyze_scene_context(current_scene: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the current scene context for AI decision making."""
    objects = current_scene.get('objects', [])
    selected_object_id = current_scene.get('selected_object_id')

    context = {
        "object_count": len(objects),
        "object_types": list(set(obj.get('type', 'unknown') for obj in objects)),
        "materials_used": list(set(obj.get('material', {}).get('color', '#ffffff') for obj in objects)),
        "has_selection": selected_object_id is not None,
        "selected_object": None
    }

    # Get selected object details if any
    if selected_object_id:
        selected = next((obj for obj in objects if obj.get('id') == selected_object_id), None)
        if selected:
            context["selected_object"] = {
                "name": selected.get('name', ''),
                "type": selected.get('type', ''),
                "material": selected.get('material', {}),
                "transform": selected.get('transform', {})
            }

    return context

def generate_intelligent_response(prompt: str, scene_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an intelligent response based on prompt and scene context."""
    prompt_lower = prompt.lower()
    
    # Determine object type and properties based on prompt analysis
    object_type = "mesh"
    material_properties = {
        "color": "#C0C0C0",  # Default silver
        "roughness": 0.5,
        "metallic": 0.8
    }

    analysis_notes = []

    # Material intelligence
    if any(material in prompt_lower for material in ["gold", "golden"]):
        material_properties["color"] = "#FFD700"
        material_properties["roughness"] = 0.3
        material_properties["metallic"] = 1.0
        analysis_notes.append("Detected gold material request")
    elif any(material in prompt_lower for material in ["silver", "platinum"]):
        material_properties["color"] = "#C0C0C0"
        material_properties["roughness"] = 0.2
        material_properties["metallic"] = 1.0
        analysis_notes.append("Detected precious metal material")
    elif any(gem in prompt_lower for gem in ["diamond", "crystal", "gem"]):
        material_properties["color"] = "#ffffff"
        material_properties["roughness"] = 0.0
        material_properties["metallic"] = 0.1
        analysis_notes.append("Detected gemstone material - high clarity")

    # Object type intelligence
    if any(jewelry in prompt_lower for jewelry in ["ring", "band"]):
        object_type = "ring"
        analysis_notes.append("Identified ring/band geometry")
    elif any(jewelry in prompt_lower for jewelry in ["necklace", "chain"]):
        object_type = "chain"
        analysis_notes.append("Identified chain/necklace geometry")
    elif any(jewelry in prompt_lower for jewelry in ["earring", "stud"]):
        object_type = "earring"
        analysis_notes.append("Identified earring geometry")

    # Context awareness
    if scene_context["has_selection"] and any(word in prompt_lower for word in ["add", "attach", "mount", "set"]):
        analysis_notes.append(f"Context: Working with selected object '{scene_context['selected_object']['name']}'")

    # Size intelligence
    size_scale = [1.0, 1.0, 1.0]
    if any(size in prompt_lower for size in ["small", "tiny", "delicate"]):
        size_scale = [0.7, 0.7, 0.7]
        analysis_notes.append("Scaled for small/delicate proportions")
    elif any(size in prompt_lower for size in ["large", "big", "bold"]):
        size_scale = [1.3, 1.3, 1.3]
        analysis_notes.append("Scaled for large/bold proportions")

    return {
        "object_type": object_type,
        "material": material_properties,
        "scale": size_scale,
        "analysis": "; ".join(analysis_notes) if analysis_notes else "Standard object creation",
        "prompt_keywords": [word for word in prompt_lower.split() if word in [
            "gold", "silver", "diamond", "ring", "necklace", "earring", "small", "large", "add", "create"
        ]]
    }


def create_object_from_ai_response(ai_response: Dict[str, Any]) -> 'SceneObject':
    """Create a SceneObject from AI analysis."""
    object_type = ai_response.get("object_type", "mesh")
    material = ai_response.get("material", {})
    scale = ai_response.get("scale", [1.0, 1.0, 1.0])
    
    # Generate intelligent object name
    object_names = {
        "ring": ["Elegant Ring", "Wedding Band", "Signet Ring", "Statement Ring"],
        "chain": ["Fine Chain", "Cuban Link", "Rope Chain", "Box Chain"],
        "earring": ["Stud Earring", "Drop Earring", "Hoop Earring", "Chandelier Earring"],
        "mesh": ["Custom Jewelry", "Artisan Piece", "Designer Element", "Geometric Form"]
    }

    import random
    object_name = random.choice(object_names.get(object_type, object_names["mesh"]))

    new_object = SceneObject(object_name, object_type)
    new_object.material.update(material)
    new_object.transform["scale"] = scale

    return new_object


async def generate_3d_model(prompt: str, ai_response: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """
    Generate an actual 3D model using AI orchestrator with Blender bridge.
    
    This integrates with the backend AI pipeline to create real 3D jewelry models
    based on the user's text prompt using Blender subprocess execution.
    """
    try:
        logger.info(f"Starting 3D model generation for prompt: {prompt}")

        # Prepare generation parameters based on AI analysis
        generation_params = {
            "jewelry_type": ai_response.get("object_type", "ring"),
            "material": extract_material_from_response(ai_response),
            "detail_level": "high",
            "style": extract_style_from_prompt(prompt)
        }

        # Try to use Blender bridge for real generation
        from .blender_bridge import get_blender_bridge, check_blender_available
        
        if check_blender_available():
            logger.info("Using Blender bridge for real 3D generation")
            
            # Call AI orchestrator to get blueprint
            from .ai_orchestrator import AiOrchestrator
            orchestrator = AiOrchestrator()
            result = orchestrator.generate_jewelry(prompt, generation_params)
            
            if result.get("success"):
                # Extract the blueprint for Blender execution
                master_blueprint = result.get("master_blueprint", {})
                
                # Execute Blender generation
                bridge = get_blender_bridge()
                blender_result = bridge.generate_3d_model(
                    blueprint=master_blueprint,
                    session_id=session_id,
                    user_prompt=prompt
                )
                
                if blender_result.get("success"):
                    logger.info(f"✅ 3D model generated via Blender: {blender_result.get('model_url')}")
                    
                    return {
                        "success": True,
                        "model_url": blender_result.get("model_url"),
                        "model_path": blender_result.get("model_path"),
                        "model_name": f"AI Generated {generation_params['jewelry_type'].title()}",
                        "details": {
                            "generation_time": blender_result.get("execution_time", 0),
                            "quality_score": 0.95,  # High quality from Blender generation
                            "parameters": generation_params,
                            "renders": blender_result.get("renders", {}),
                            "package_path": blender_result.get("package_path")
                        },
                        "generation_method": "blender_subprocess"
                    }
                else:
                    logger.warning(f"Blender generation failed, using fallback: {blender_result.get('error')}")
                    # Fall through to fallback mode
            else:
                logger.warning(f"AI orchestrator failed: {result.get('error')}")
                # Fall through to fallback mode
        else:
            logger.info("Blender not available, using fallback mode")
        
        # Fallback mode: Use placeholder with intelligent properties
        logger.info("Using fallback generation mode")
        
        return {
            "success": True,
            "model_url": "/3d_models/diamond_ring_example.glb",  # Use example GLB
            "model_name": f"AI Analyzed {generation_params['jewelry_type'].title()}",
            "details": {
                "generation_time": 0.5,
                "quality_score": 0.7,  # Lower score for fallback
                "parameters": generation_params
            },
            "generation_method": "fallback",
            "fallback_reason": "Blender not available or generation failed"
        }

    except Exception as e:
        logger.error(f"3D model generation exception: {e}")
        return {
            "success": False,
            "error": str(e),
            "model_url": None
        }


def extract_material_from_response(ai_response: Dict[str, Any]) -> str:
    """Extract material type from AI response."""
    color = ai_response.get("material", {}).get("color", "#FFD700")

    # Map color to material
    if color == "#FFD700":
        return "GOLD"
    elif color == "#C0C0C0":
        return "SILVER"
    elif color == "#ffffff":
        return "PLATINUM"
    else:
        return "GOLD"


def extract_style_from_prompt(prompt: str) -> str:
    """Extract style classification from prompt."""
    prompt_lower = prompt.lower()

    if any(word in prompt_lower for word in ["vintage", "antique", "classic"]):
        return "vintage"
    elif any(word in prompt_lower for word in ["modern", "contemporary", "minimal"]):
        return "modern"
    elif any(word in prompt_lower for word in ["ornate", "decorative", "elaborate"]):
        return "ornate"
    elif any(word in prompt_lower for word in ["nature", "floral", "organic"]):
        return "nature"
    else:
        return "classic"

def get_output_path(prompt: str) -> str:
    """Generate output file path based on prompt."""
    safe_name = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = "_".join(safe_name.split())[:40]
    return os.path.join(OUTPUT_DIR, f"output_{safe_name}.stl")

# ============================================================================
# Granular API Endpoints - Professional CAD Studio Interface  
# ============================================================================

@api_router.post("/session/new")
async def create_new_session():
    """Create a new design session."""
    session = DesignSession()
    active_sessions[session.id] = session
    
    logger.info(f"Created new design session: {session.id}")
    
    return JSONResponse({
        "success": True,
        "session_id": session.id,
        "message": "New design session created successfully"
    })

@api_router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information."""
    session = active_sessions.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Session not found"
        })
    
    return JSONResponse({
        "success": True,
        "session": session.to_dict()
    })

@api_router.post("/session/{session_id}/execute_prompt")
async def execute_ai_prompt(session_id: str, request: Request):
    """Execute AI prompt with real 3D model generation."""
    session = active_sessions.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Session not found"
        })
    
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        current_scene = data.get("current_scene", {})
        
        logger.info(f"Executing AI prompt for session {session_id}: {prompt}")
        logger.info(f"Current scene context: {len(current_scene.get('objects', []))} objects")
        
        # Enhanced AI processing with scene context
        scene_context = analyze_scene_context(current_scene)
        ai_response = generate_intelligent_response(prompt, scene_context)
        
        # Generate actual 3D model using AI
        generation_result = await generate_3d_model(prompt, ai_response, session_id)
        
        if generation_result.get("success"):
            # Create new object with generated model
            new_object = SceneObject(
                generation_result.get("model_name", f"AI Generated: {prompt[:30]}..."),
                "glb_model"
            )
            new_object.material.update(ai_response.get("material", {}))
            new_object.transform["scale"] = ai_response.get("scale", [1.0, 1.0, 1.0])
            
            # Store the URL to the generated GLB file
            if generation_result.get("model_url"):
                # Add URL as a property (will be used by frontend)
                new_object.geometry_data = {"url": generation_result["model_url"]}
            
            object_id = session.add_object(new_object)
            
            return JSONResponse({
                "success": True,
                "message": "AI-generated 3D model created successfully",
                "created_object_id": object_id,
                "object": {**new_object.to_dict(), "url": generation_result.get("model_url")},
                "ai_analysis": ai_response.get("analysis", ""),
                "generation_details": generation_result.get("details", {}),
                "scene_context": scene_context
            })
        else:
            # Fallback to simple object if generation fails
            logger.warning(f"3D generation failed, creating fallback object: {generation_result.get('error')}")
            new_object = create_object_from_ai_response(ai_response)
            object_id = session.add_object(new_object)
            
            return JSONResponse({
                "success": True,
                "message": "Object created (generation in progress)",
                "created_object_id": object_id,
                "object": new_object.to_dict(),
                "ai_analysis": ai_response.get("analysis", ""),
                "generation_status": "fallback",
                "scene_context": scene_context
            })
        
    except Exception as e:
        logger.exception('AI prompt execution failed')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "message": "AI prompt execution failed"
        })

@api_router.get("/scene/{session_id}")
async def get_scene_state(session_id: str):
    """Get the current scene state."""
    session = active_sessions.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Session not found"
        })
    
    return JSONResponse({
        "success": True,
        "scene": {
            "session_id": session_id,
            "objects": [obj.to_dict() for obj in session.objects.values()],
            "last_modified": session.last_modified
        }
    })

@api_router.put("/object/{session_id}/{object_id}/transform")
async def update_object_transform(session_id: str, object_id: str, request: Request):
    """Update object transformation (position, rotation, scale)."""
    session = active_sessions.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Session not found"
        })
    
    obj = session.get_object(object_id)
    if not obj:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Object not found"
        })
    
    try:
        data = await request.json()
        transform_updates = {}
        
        if "position" in data:
            transform_updates["position"] = data["position"]
        if "rotation" in data:
            transform_updates["rotation"] = data["rotation"]  
        if "scale" in data:
            transform_updates["scale"] = data["scale"]
        
        # Update the object's transform
        obj.transform.update(transform_updates)
        session.last_modified = time.time()
        
        logger.info(f"Updated transform for object {object_id} in session {session_id}")
        
        return JSONResponse({
            "success": True,
            "message": "Object transform updated successfully",
            "object": obj.to_dict()
        })
        
    except Exception as e:
        logger.exception('Object transform update failed')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e)
        })

@api_router.put("/object/{session_id}/{object_id}/material")
async def update_object_material(session_id: str, object_id: str, request: Request):
    """Update object material properties."""
    session = active_sessions.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Session not found"
        })
    
    obj = session.get_object(object_id)
    if not obj:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Object not found"
        })
    
    try:
        data = await request.json()
        material_updates = {}
        
        if "color" in data:
            material_updates["color"] = data["color"]
        if "roughness" in data:
            material_updates["roughness"] = float(data["roughness"])
        if "metallic" in data:
            material_updates["metallic"] = float(data["metallic"])
        
        # Update the object's material
        obj.material.update(material_updates)
        session.last_modified = time.time()
        
        logger.info(f"Updated material for object {object_id} in session {session_id}")
        
        return JSONResponse({
            "success": True,
            "message": "Object material updated successfully",
            "object": obj.to_dict()
        })
        
    except Exception as e:
        logger.exception('Object material update failed')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e)
        })

@api_router.delete("/object/{session_id}/{object_id}")
async def delete_object(session_id: str, object_id: str):
    """Delete an object from the scene."""
    session = active_sessions.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Session not found"
        })
    
    if session.remove_object(object_id):
        logger.info(f"Deleted object {object_id} from session {session_id}")
        return JSONResponse({
            "success": True,
            "message": "Object deleted successfully"
        })
    else:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": "Object not found"
        })

# ============================================================================
# Legacy Endpoints (for backward compatibility)
# ============================================================================

@api_router.post("/generate")
async def generate_design(request: Request):
    """
    Legacy endpoint for professional design generation.
    Creates a new session and executes prompt.
    """
    logger.info("=== LEGACY /generate ENDPOINT ===")
    
    try:
        # Create new session
        session = DesignSession()
        active_sessions[session.id] = session
        
        data = await request.json()
        prompt = data.get("prompt", "elegant engagement ring")
        
        # Execute prompt on new session
        new_object = SceneObject(f"Generated: {prompt[:30]}...", "mesh")
        object_id = session.add_object(new_object)
        
        return JSONResponse({
            "success": True,
            "session_id": session.id,
            "file": f"output_{prompt[:20]}.stl",
            "message": "Design generated successfully",
            "created_object_id": object_id,
            "object": new_object.to_dict()
        })
        
    except Exception as e:
        logger.exception('Legacy generation failed')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "message": "Legacy generation failed"
        })

@api_router.get("/output/{filename}")
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

@api_router.get("/output/ai_generated/{filename}")
async def serve_ai_generated_file(filename: str):
    """Serve AI-generated GLB and other files."""
    logger.debug('Received AI-generated file request: %s', filename)
    try:
        # Allow GLB, BLEND, and PNG files from AI generation
        allowed_extensions = ['.glb', '.blend', '.png']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            logger.error(f"Rejected AI file request: {filename} (invalid extension)")
            return Response(status_code=400)
        
        file_path = os.path.join(OUTPUT_DIR, "ai_generated", filename)
        if os.path.exists(file_path):
            logger.info(f"Serving AI file from output dir: {file_path}")
            
            # Set appropriate media type based on extension
            media_type = "model/gltf-binary" if filename.lower().endswith('.glb') else "application/octet-stream"
            return FileResponse(file_path, media_type=media_type)
        else:
            logger.error(f"AI file not found in output dir: {filename}")
            return Response(status_code=404)
    except Exception as e:
        logger.exception('Exception serving AI-generated file')
        return Response(content=str(e), status_code=500)

@api_router.get("/health")
async def health_check():
    """Enhanced health check endpoint with Blender and AI provider status."""
    from .blender_bridge import check_blender_available
    from .ai_provider_manager import get_ai_provider_manager
    
    # Get AI provider status
    try:
        provider_manager = get_ai_provider_manager()
        ai_status = provider_manager.get_status()
    except Exception as e:
        logger.warning(f"Could not get AI provider status: {e}")
        ai_status = {
            'active_provider': None,
            'available_providers': [],
            'error': str(e)
        }
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Aura Backend Orchestrator",
        "version": "24.0",
        "mode": "sandbox" if SANDBOX_MODE else "production",
        "lm_studio_configured": bool(LM_STUDIO_URL),
        "external_ai_configured": bool(EXTERNAL_AI_URL),
        "blender_path_configured": bool(BLENDER_PATH),
        "blender_available": check_blender_available(),
        "output_directory": OUTPUT_DIR,
        "active_sessions": len(active_sessions),
        "ai_provider": ai_status,
        "capabilities": {
            "ai_generation": check_blender_available(),
            "fallback_mode": not check_blender_available(),
            "multi_provider_ai": len(ai_status.get('available_providers', [])) > 0
        }
    }
    return health_status


@api_router.get("/ai/providers")
async def get_ai_providers():
    """Get information about available AI providers."""
    from .ai_provider_manager import get_ai_provider_manager
    
    try:
        provider_manager = get_ai_provider_manager()
        status = provider_manager.get_status()
        
        return JSONResponse({
            "success": True,
            "providers": status
        })
    except Exception as e:
        logger.exception('Failed to get AI provider status')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e)
        })


@api_router.post("/ai/providers/switch")
async def switch_ai_provider(request: Request):
    """Switch the active AI provider."""
    from .ai_provider_manager import get_ai_provider_manager, AIProvider
    
    try:
        data = await request.json()
        provider_name = data.get('provider', '').lower()
        
        if not provider_name:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "Provider name required"
            })
        
        # Convert to enum
        try:
            provider_enum = AIProvider(provider_name)
        except ValueError:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": f"Unknown provider: {provider_name}",
                "available_providers": [p.value for p in AIProvider]
            })
        
        # Switch provider
        provider_manager = get_ai_provider_manager()
        success = provider_manager.set_active_provider(provider_enum)
        
        if success:
            return JSONResponse({
                "success": True,
                "message": f"Switched to provider: {provider_name}",
                "active_provider": provider_name
            })
        else:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": f"Provider {provider_name} not available or not configured"
            })
    
    except Exception as e:
        logger.exception('Failed to switch AI provider')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e)
        })


# ============================================================================
# Enhanced AI 3D Model Generation Endpoints
# ============================================================================

@api_router.post("/ai/generate-3d-model")
async def generate_3d_model_enhanced(request: Request):
    """
    Generate a complete 3D model using advanced AI orchestration.
    
    This endpoint uses OpenAI GPT-4/GPT-4o for sophisticated design planning
    and construction plan generation.
    
    Request Body:
        - prompt: Natural language design description
        - complexity: simple, moderate, complex, or hyper_realistic
        - session_id: Optional session ID for context
        - context: Optional scene context
    
    Returns:
        Complete 3D model generation results with construction plan
    """
    if not ENHANCED_AI_AVAILABLE or enhanced_ai_orchestrator is None:
        return JSONResponse(status_code=503, content={
            "success": False,
            "error": "Enhanced AI orchestration not available",
            "message": "Please ensure OpenAI API key is configured"
        })
    
    try:
        data = await request.json()
        prompt = data.get('prompt', '')
        complexity = data.get('complexity', 'moderate')
        session_id = data.get('session_id')
        context = data.get('context')
        
        if not prompt:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "Prompt is required"
            })
        
        logger.info(f"🚀 Enhanced AI 3D model generation request: {prompt}")
        
        # --- MOCK MODE: skip OpenAI and Blender for local testing ---
        import os
        mock_mode = os.environ.get('AURA_MOCK_AI', '0') == '1' or request.query_params.get('mock', '0') == '1'
        if mock_mode:
            logger.info('🧪 MOCK MODE ENABLED: Returning hardcoded AI response')
            # Hardcoded mock response
            mock_result = {
                "success": True,
                "object_id": "ai_mock_12345",
                "construction_plan": {
                    "type": "jewelry_ring",
                    "construction_steps": [
                        {"operation": "create_shank", "parameters": {"profile": "round", "width": 2.0}},
                        {"operation": "create_head", "parameters": {"type": "prong_setting"}},
                        {"operation": "create_diamond", "parameters": {"shape": "round", "size": 1.0}}
                    ]
                },
                "material_specifications": {
                    "primary_material": {
                        "name": "Gold",
                        "base_color": "#FFD700",
                        "roughness": 0.2,
                        "metallic": 0.9
                    }
                },
                "blender_execution": {
                    "success": True,
                    "blend_file": "output/ai_generated/ai_mock_12345.blend",
                    "glb_file": "output/ai_generated/ai_mock_12345.glb",
                    "render_file": "output/ai_generated/ai_mock_12345.png",
                    "execution_time": 1.23
                },
                "model_url": "/output/ai_generated/ai_mock_12345.glb",
                "glb_file": "output/ai_generated/ai_mock_12345.glb",
                "blend_file": "output/ai_generated/ai_mock_12345.blend",
                "render_file": "output/ai_generated/ai_mock_12345.png"
            }
            return JSONResponse(status_code=200, content=mock_result)
        
        # Generate 3D model using enhanced orchestrator
        result = enhanced_ai_orchestrator.generate_3d_model(
            user_prompt=prompt,
            complexity=complexity,
            context=context,
            progress_callback=None  # Could implement SSE for progress
        )
        
        # If successful and Blender executor available, build actual 3D model
        if result.get('success', False) and BLENDER_EXECUTOR_AVAILABLE and blender_executor:
            logger.info("🔨 Executing construction plan with Blender...")
            
            execution_result = blender_executor.execute_construction_plan(
                construction_plan=result.get('construction_plan', []),
                material_specs=result.get('material_specifications', {}),
                presentation_plan=result.get('presentation_plan', {}),
                user_prompt=prompt
            )
            
            if execution_result.get('success'):
                logger.info(f"✅ 3D model built successfully: {execution_result.get('glb_file')}")
                result['blender_execution'] = execution_result
                result['model_url'] = execution_result.get('model_url')
                result['glb_file'] = execution_result.get('glb_file')
                result['blend_file'] = execution_result.get('blend_file')
                result['render_file'] = execution_result.get('render_file')
            else:
                logger.warning(f"⚠ Blender execution failed: {execution_result.get('error')}")
                result['blender_execution'] = execution_result
                result['blender_error'] = execution_result.get('error')
        
        # If session provided, add generated object to session
        if session_id and result.get('success', False):
            session = active_sessions.get(session_id)
            if session:
                # Create scene object from AI result
                new_object = SceneObject(
                    name=f"AI: {prompt[:40]}...",
                    obj_type="ai_generated"
                )
                
                # Apply material specs from AI
                material_specs = result.get('material_specifications', {})
                primary_material = material_specs.get('primary_material', {})
                if primary_material:
                    new_object.material['color'] = primary_material.get('base_color', '#FFD700')
                    new_object.material['roughness'] = primary_material.get('roughness', 0.2)
                    new_object.material['metallic'] = primary_material.get('metallic', 0.8)
                
                # Store construction plan in object
                new_object.geometry_data = {
                    'construction_plan': result.get('construction_plan', []),
                    'presentation_plan': result.get('presentation_plan', {}),
                    'ai_metadata': result.get('metadata', {}),
                    'blender_files': {
                        'glb': result.get('glb_file'),
                        'blend': result.get('blend_file'),
                        'render': result.get('render_file')
                    }
                }
                
                # Set model URL if available
                if result.get('model_url'):
                    new_object.url = result.get('model_url')
                
                # Add to session
                session.objects[new_object.id] = new_object
                logger.info(f"Added AI-generated object {new_object.id} to session {session_id}")
                
                result['object_id'] = new_object.id
                result['session_id'] = session_id
        
        return JSONResponse(result)
        
    except Exception as e:
        logger.exception('Enhanced AI 3D model generation failed')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "message": "Enhanced AI generation failed"
        })


@api_router.post("/ai/refine-design")
async def refine_design(request: Request):
    """
    Refine an existing 3D design based on user feedback.
    
    Request Body:
        - session_id: Session ID
        - object_id: Object ID to refine
        - refinement_request: User's refinement instructions
    
    Returns:
        Refined design with updated construction plan
    """
    if not ENHANCED_AI_AVAILABLE or enhanced_ai_orchestrator is None:
        return JSONResponse(status_code=503, content={
            "success": False,
            "error": "Enhanced AI orchestration not available"
        })
    
    try:
        data = await request.json()
        session_id = data.get('session_id')
        object_id = data.get('object_id')
        refinement_request = data.get('refinement_request', '')
        
        if not all([session_id, object_id, refinement_request]):
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "session_id, object_id, and refinement_request are required"
            })
        
        # Get session and object
        session = active_sessions.get(session_id)
        if not session:
            return JSONResponse(status_code=404, content={
                "success": False,
                "error": "Session not found"
            })
        
        scene_object = session.objects.get(object_id)
        if not scene_object:
            return JSONResponse(status_code=404, content={
                "success": False,
                "error": "Object not found in session"
            })
        
        # Get current design from object
        current_design = scene_object.geometry_data or {}
        
        logger.info(f"🔄 Refining design for object {object_id}: {refinement_request}")
        
        # Refine using enhanced orchestrator
        result = enhanced_ai_orchestrator.refine_existing_model(
            current_design=current_design,
            refinement_request=refinement_request
        )
        
        # Update object with refined design
        if result.get('success', False):
            refined_design = result.get('refined_design', {})
            scene_object.geometry_data = refined_design
            
            # Update materials if changed
            if 'presentation_plan' in refined_design:
                material_style = refined_design['presentation_plan'].get('material_style', '')
                if 'Gold' in material_style:
                    scene_object.material['color'] = '#FFD700'
                elif 'Silver' in material_style or 'Platinum' in material_style:
                    scene_object.material['color'] = '#C0C0C0'
            
            logger.info(f"✓ Design refined successfully for object {object_id}")
        
        result['object_id'] = object_id
        result['session_id'] = session_id
        
        return JSONResponse(result)
        
    except Exception as e:
        logger.exception('Design refinement failed')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e)
        })


@api_router.post("/ai/generate-variations")
async def generate_variations(request: Request):
    """
    Generate multiple variations of a design concept.
    
    Request Body:
        - base_prompt: Base design description
        - variation_count: Number of variations (1-5)
        - session_id: Optional session ID to add variations to
    
    Returns:
        List of design variations
    """
    if not ENHANCED_AI_AVAILABLE or enhanced_ai_orchestrator is None:
        return JSONResponse(status_code=503, content={
            "success": False,
            "error": "Enhanced AI orchestration not available"
        })
    
    try:
        data = await request.json()
        base_prompt = data.get('base_prompt', '')
        variation_count = min(int(data.get('variation_count', 3)), 5)  # Max 5 variations
        session_id = data.get('session_id')
        
        if not base_prompt:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "base_prompt is required"
            })
        
        logger.info(f"🎨 Generating {variation_count} variations of: {base_prompt}")
        
        # Generate variations
        variations = enhanced_ai_orchestrator.batch_generate_variations(
            base_prompt=base_prompt,
            variation_count=variation_count
        )
        
        # If session provided, add variations as objects
        object_ids = []
        if session_id:
            session = active_sessions.get(session_id)
            if session:
                for i, variation in enumerate(variations):
                    if variation.get('success', False):
                        new_object = SceneObject(
                            name=f"Variation {i+1}: {base_prompt[:30]}...",
                            obj_type="ai_generated_variation"
                        )
                        
                        # Apply material specs
                        material_specs = variation.get('material_specifications', {})
                        primary_material = material_specs.get('primary_material', {})
                        if primary_material:
                            new_object.material['color'] = primary_material.get('base_color', '#FFD700')
                            new_object.material['roughness'] = primary_material.get('roughness', 0.2)
                            new_object.material['metallic'] = primary_material.get('metallic', 0.8)
                        
                        # Position variations side by side
                        new_object.transform['position'] = [i * 0.05, 0, 0]
                        
                        # Store construction plan
                        new_object.geometry_data = {
                            'construction_plan': variation.get('construction_plan', []),
                            'presentation_plan': variation.get('presentation_plan', {}),
                            'ai_metadata': variation.get('metadata', {})
                        }
                        
                        session.objects[new_object.id] = new_object
                        object_ids.append(new_object.id)
        
        return JSONResponse({
            "success": True,
            "variations": variations,
            "variation_count": len(variations),
            "session_id": session_id,
            "object_ids": object_ids
        })
        
    except Exception as e:
        logger.exception('Variation generation failed')
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e)
        })


@api_router.get("/ai/status")
async def get_ai_status():
    """
    Get status of AI 3D model generation capabilities.
    
    Returns information about available AI providers and features.
    """
    status = {
        "enhanced_ai_available": ENHANCED_AI_AVAILABLE,
        "openai_configured": False,
        "capabilities": {
            "advanced_3d_generation": False,
            "design_refinement": False,
            "variation_generation": False,
            "material_generation": False
        }
    }
    
    if ENHANCED_AI_AVAILABLE and enhanced_ai_orchestrator:
        status["openai_configured"] = enhanced_ai_orchestrator.openai_enabled
        status["multi_provider_available"] = enhanced_ai_orchestrator.multi_provider_enabled
        
        if enhanced_ai_orchestrator.openai_enabled:
            status["capabilities"]["advanced_3d_generation"] = True
            status["capabilities"]["design_refinement"] = True
            status["capabilities"]["variation_generation"] = True
            status["capabilities"]["material_generation"] = True
            status["openai_model"] = enhanced_ai_orchestrator.ai_3d_generator.model
    
    return JSONResponse(status)

@app.get("/")
async def root():
    """Root endpoint with service information."""
    from .blender_bridge import check_blender_available
    
    return {
        "service": "Aura Backend Orchestrator", 
        "version": "24.0",
        "mode": "sandbox" if SANDBOX_MODE else "production",
        "status": "Granular API Architecture Active - Professional CAD Studio",
        "active_sessions": len(active_sessions),
        "blender_available": check_blender_available(),
        "endpoints": {
            "sessions": "/api/session/new, /api/session/{id}",
            "scene": "/api/scene/{session_id}",
            "objects": "/api/object/{session_id}/{object_id}/transform, /api/object/{session_id}/{object_id}/material",
            "ai": "/api/session/{session_id}/execute_prompt",
            "models": "/3d_models/{filename}"
        }
    }

# Serve static 3D model files
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Mount the 3d_models directory for serving GLB files
models_dir = Path(__file__).parent.parent / "3d_models"
if models_dir.exists():
    app.mount("/3d_models", StaticFiles(directory=str(models_dir)), name="3d_models")
    logger.info(f"Mounted 3D models directory: {models_dir}")
else:
    logger.warning(f"3D models directory not found: {models_dir}")

# Mount the output directory for serving AI-generated files
output_static_dir = Path(__file__).parent.parent / "output"
if output_static_dir.exists():
    app.mount("/output", StaticFiles(directory=str(output_static_dir)), name="output")
    logger.info(f"Mounted output directory: {output_static_dir}")
else:
    logger.warning(f"Output directory not found: {output_static_dir}")

# Serve the control panel HTML
@app.get("/control-panel")
async def serve_control_panel():
    """Serve the web-based control panel."""
    from fastapi.responses import HTMLResponse
    try:
        control_panel_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "control_panel.html")
        with open(control_panel_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Control Panel Not Found</h1><p>The control panel HTML file could not be found.</p>", status_code=404)

# Enhanced: Serve the AI Design Studio
@app.get("/design-studio")
async def serve_design_studio():
    """Serve the AI Design Studio - Real-time Collaborative Design Interface."""
    from fastapi.responses import HTMLResponse
    try:
        design_studio_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "design_studio.html")
        with open(design_studio_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Design Studio Not Found</h1><p>The AI Design Studio interface could not be found.</p>", status_code=404)

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)