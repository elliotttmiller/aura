PS C:\Users\AMD\aura> & C:/Users/AMD/AppData/Local/Programs/Python/Python311/python.exe c:/Users/AMD/aura/start.py

Aura Quick Start - Full System
========================================
No old server processes found.

================================================================================
Aura Backend Server - Starting...
================================================================================

[1/4] Loading environment configuration...

[2/4] Validating configuration...
  Status: ok

[3/4] Importing application...
[2025-10-17 22:47:38,153] CONFIG INFO Loaded environment from .env
  Host: 0.0.0.0
  Port: 8001
  Workers: 1
  Reload: False

[4/4] Starting FastAPI server...
================================================================================
[2025-10-17 22:47:39,330] CONFIG INFO Loaded environment from .env
[2025-10-17 22:47:40,108] CONFIG INFO ✓ Enhanced AI Orchestrator available
[2025-10-17 22:47:40,108] CONFIG INFO 🚀 Initializing Enhanced AI Orchestrator...
[2025-10-17 22:47:40,108] CONFIG INFO Auto-selected provider: openai
[2025-10-17 22:47:40,108] CONFIG INFO AI Provider Manager initialized
[2025-10-17 22:47:40,108] CONFIG INFO Active provider: openai
[2025-10-17 22:47:40,108] CONFIG INFO Available providers: ['lm_studio', 'openai', 'ollama']
[2025-10-17 22:47:40,543] CONFIG INFO ✓ AI 3D Model Generator initialized with OpenAI GPT-4
[2025-10-17 22:47:40,543] CONFIG INFO ✓ OpenAI GPT-4 3D Generator: ENABLED
[2025-10-17 22:47:40,543] CONFIG INFO ✓ Multi-Provider AI: ENABLED (openai)
[2025-10-17 22:47:40,543] CONFIG INFO 🎯 Enhanced AI Orchestrator initialized successfully
[2025-10-17 22:47:40,543] CONFIG INFO ✓ Enhanced AI Orchestrator initialized
[2025-10-17 22:47:40,549] CONFIG INFO Blender path: C:\Program Files\Blender Foundation\Blender 4.5\blender.exe
[2025-10-17 22:47:40,549] CONFIG INFO Output directory: C:\Users\AMD\aura\output\ai_generated
[2025-10-17 22:47:40,549] CONFIG INFO ✓ Blender Construction Executor available
[2025-10-17 22:47:40,557] CONFIG INFO Mounted 3D models directory: C:\Users\AMD\aura\3d_models
INFO:     Started server process [6856]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
Starting frontend dev server...

Servers are starting. Access frontend at http://localhost:5173

Press Ctrl+C to stop both servers.

> aura-design-studio@1.0.0 dev
> vite


  VITE v4.5.14  ready in 331 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
(node:8880) [DEP0060] DeprecationWarning: The `util._extend` API is deprecated. Please use Object.assign() instead.
(Use `node --trace-deprecation ...` to show where the warning was created)
[2025-10-17 22:47:43,088] CONFIG INFO Created new design session: 27ef0902-53df-4c50-937c-632f92ad6227
INFO:     127.0.0.1:50596 - "POST /api/session/new HTTP/1.1" 200 OK
[2025-10-17 22:47:43,091] CONFIG INFO Created new design session: f74ce6d8-cb39-4b11-b9c4-12423b1f9232
INFO:     127.0.0.1:50597 - "POST /api/session/new HTTP/1.1" 200 OK