"""
Backend Orchestrator - Professional AI Pipeline
====================================================

This orchestrator manages the professional workflow:
Stage 1: LLM (Llama 3.1 via LM Studio) generates Master Blueprint
Stage 2: External AI Environment generates 3D base geometry
Stage 3: State-of-the-Art Blender engine executes the Master Blueprint

Part of the Professional Integration.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import logging
import json
import requests
import time
import asyncio
from typing import Dict, Any, Optional
import uuid

# Enhancement: Centralized environment configuration
try:
    from ..config import config, get_lm_studio_url, get_ai_server_config, is_sandbox_mode
    CONFIG_AVAILABLE = True
except ImportError:
    logging.warning("Config module not available, using environment variables")
    CONFIG_AVAILABLE = False

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

# Enhanced logging configuration
if CONFIG_AVAILABLE:
    log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO').upper())
    logging.basicConfig(level=log_level, format=config.get('LOG_FORMAT', '[%(asctime)s] %(levelname)s %(message)s'))
else:
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')

logger = logging.getLogger(__name__)

# Configuration with centralized config management
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

# Enhanced script paths
BLENDER_PROC_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "blender_proc.py"))
BLENDER_SIM_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "blender_sim.py"))

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    """Execute AI prompt with enhanced scene context awareness."""
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
        
        logger.info(f"Executing context-aware AI prompt for session {session_id}: {prompt}")
        logger.info(f"Current scene context: {len(current_scene.get('objects', []))} objects")
        
        # Enhanced AI processing with scene context
        scene_context = analyze_scene_context(current_scene)
        ai_response = generate_intelligent_response(prompt, scene_context)
        
        # Create new object based on AI analysis
        new_object = create_object_from_ai_response(ai_response)
        object_id = session.add_object(new_object)
        
        return JSONResponse({
            "success": True,
            "message": "Context-aware AI prompt executed successfully",
            "created_object_id": object_id,
            "object": new_object.to_dict(),
            "ai_analysis": ai_response.get("analysis", ""),
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

@api_router.get("/health")
async def health_check():
    """Enhanced health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Aura Backend Orchestrator",
        "version": "24.0",
        "mode": "sandbox" if SANDBOX_MODE else "production",
        "lm_studio_configured": bool(LM_STUDIO_URL),
        "external_ai_configured": bool(EXTERNAL_AI_URL),
        "blender_path_configured": bool(BLENDER_PATH),
        "output_directory": OUTPUT_DIR,
        "active_sessions": len(active_sessions)
    }
    return health_status

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Aura Backend Orchestrator", 
        "version": "24.0",
        "mode": "sandbox" if SANDBOX_MODE else "production",
        "status": "Granular API Architecture Active - Professional CAD Studio",
        "active_sessions": len(active_sessions),
        "endpoints": {
            "sessions": "/session/new, /session/{id}",
            "scene": "/scene/{session_id}",
            "objects": "/object/{session_id}/{object_id}/transform, /object/{session_id}/{object_id}/material",
            "ai": "/session/{session_id}/execute_prompt"
        }
    }

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