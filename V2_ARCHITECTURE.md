# Aura V2.0 - AI-Powered Jewelry Design Pipeline

## V2.0 Architecture Overview

Aura V2.0 introduces a revolutionary 4-tier architecture that integrates real AI generation capabilities:

1. **AI Inference Server** (`3d-object-generation/`) - Persistent AI model server
2. **Backend Orchestrator** (`backend/main.py`) - Coordinates AI → Post-processing pipeline  
3. **Post-Processor** (`blender_proc.py`) - Fuses AI output with procedural jewelry components
4. **Frontend** (`frontend/`) - Web interface for design generation

## New V2.0 Pipeline

```
User Prompt → AI Server → Raw 3D Model → Post-Processor → Final STL → Web Viewer
```

### Key V2.0 Features

- **Persistent AI Server**: Eliminates cold-start latency by keeping models loaded in GPU memory
- **Two-Stage Generation**: AI creativity + procedural manufacturing constraints
- **Hybrid Synthesis**: Seamless fusion of artistic AI geometry with engineered jewelry components
- **Manufacturing Ready**: All outputs are watertight, manufacturable 3D models

## Quick Start

1. **Start the complete pipeline:**
   ```bash
   python start.py
   ```

2. **Access the web interface:**
   - Frontend: http://localhost:8000
   - Backend API: http://localhost:8001  
   - AI Server: http://localhost:5000

## Architecture Components

### AI Inference Server (`3d-object-generation/`)
- **File**: `main_server.py` - Flask server with persistent AI models
- **Docker**: `Dockerfile` - Containerized deployment with GPU support
- **Models**: Currently supports geometric test generation (Shap-E integration ready)

### Backend Orchestrator (`backend/main.py`) 
- Receives user prompts from frontend
- Calls AI server for creative 3D generation  
- Invokes post-processor for manufacturing integration
- Returns final STL files

### Post-Processor (`blender_proc.py`)
- Imports AI-generated OBJ files
- Creates procedural ring shanks with proper sizing
- Performs boolean fusion of components
- Exports production-ready STL files

### Frontend (`frontend/`)
- Modern web interface for prompt submission
- Real-time 3D visualization of generated models
- Supports metal selection and ring sizing parameters

## Development Notes

- **Test Mode**: When Blender is unavailable, the system uses `blender_test_stub.py` for testing
- **Local Development**: The AI server can run locally without Docker for development
- **GPU Acceleration**: Full GPU support for AI inference when Docker container is used

## Migration from V1.0

V2.0 replaces the single `aura_backend.py` with a sophisticated pipeline:
- Old: Single script simulation → STL  
- New: AI generation → Post-processing → STL

The web interface remains compatible, but the backend architecture is completely redesigned for real AI integration.