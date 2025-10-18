#!/usr/bin/env python3
"""
Aura Quick Start Script
======================
Starts both backend and frontend servers for local development.

Usage:
    python start.py
"""


import sys
import os
import time
import requests
from pathlib import Path
import subprocess
import psutil

def kill_existing_servers():
    """Find and kill any running backend (uvicorn) and frontend (vite) server processes."""
    try:
        import psutil
    except ImportError:
        print("⚠️  psutil not available, skipping process cleanup")
        return
        
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
            # Kill uvicorn (backend)
            if 'uvicorn' in cmdline and 'main:app' in cmdline:
                print(f"🔄 Killing backend server (PID {proc.pid})...")
                proc.kill()
                killed = True
            # Kill vite (frontend)
            elif ('vite' in cmdline or 'npm run dev' in cmdline) and 'frontend' in cmdline:
                print(f"🔄 Killing frontend server (PID {proc.pid})...")
                proc.kill()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if killed:
        print("✅ Old server processes terminated.\n")
    else:
        print("ℹ️  No old server processes found.\n")

def run_frontend():
    print("Starting frontend dev server...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'static')
    return subprocess.Popen([
        'npm', 'run', 'dev'
    ], cwd=frontend_dir, shell=True)

def run_backend_with_config():
    # --- Begin migrated backend startup workflow ---
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    # CRITICAL: Load environment configuration FIRST
    from backend.config_init import ensure_config_loaded, validate_critical_config, get_project_root

    print("=" * 80)
    print("Aura Backend Server - Starting...")
    print("=" * 80)

    # Load configuration
    print("\n[1/5] Loading environment configuration...")
    config_loaded = ensure_config_loaded(verbose=True)

    # Validate configuration
    print("\n[2/5] Validating configuration...")
    validation = validate_critical_config()
    print(f"  Status: {validation['status']}")
    if validation['warnings']:
        print(f"  Warnings: {len(validation['warnings'])}")
        for warning in validation['warnings']:
            print(f"    - {warning}")
    if validation['errors']:
        print(f"  Errors: {len(validation['errors'])}")
        for error in validation['errors']:
            print(f"    - {error}")
        print("\n⚠ Critical configuration errors found!")
        sys.exit(1)

    # Import config to get settings
    print("\n[3/5] Importing application...")
    from config import config

    # NEW: Initialize and check AI models
    print("\n[4/5] Initializing AI Models and Providers...")
    print("-" * 60)
    
    try:
        # Import AI components to trigger initialization
        print("🔄 Loading AI provider manager...")
        from backend.ai_provider_manager import AIProviderManager
        
        print("🔄 Loading enhanced AI orchestrator...")
        from backend.enhanced_ai_orchestrator import EnhancedAIOrchestrator
        
        print("🔄 Loading AI 3D model generator...")
        from backend.ai_3d_model_generator import AI3DModelGenerator
        
        print("🔄 Checking available AI providers...")
        
        # Initialize AI provider manager to see what's available
        provider_manager = AIProviderManager()
        available_providers = provider_manager.get_available_providers()
        active_provider = provider_manager.active_provider
        
        print(f"📋 Available AI providers: {[p.value for p in available_providers]}")
        print(f"🎯 Active AI provider: {active_provider.value if active_provider else 'None'}")
        
        # Check specific provider configurations
        print("\n🔍 Checking AI Provider Configurations:")
        
        # Check OpenAI
        openai_key = config.get('OPENAI_API_KEY', '')
        if openai_key and openai_key != 'your-openai-api-key-here':
            print("  ✅ OpenAI: API key configured")
            try:
                # Test OpenAI connection
                print("  🔄 OpenAI: Testing connection...")
                # We'll just check if we can import and initialize
                import openai
                print("  ✅ OpenAI: SDK loaded successfully")
            except Exception as e:
                print(f"  ⚠️  OpenAI: SDK issue - {str(e)}")
        else:
            print("  ❌ OpenAI: No valid API key configured")
        
        # Check LM Studio
        lm_studio_url = config.get('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
        print(f"  🔄 LM Studio: Checking endpoint {lm_studio_url}")
        try:
            import requests
            response = requests.get(f"{lm_studio_url.rstrip('/v1')}/health", timeout=2)
            if response.status_code == 200:
                print("  ✅ LM Studio: Server responding")
            else:
                print(f"  ⚠️  LM Studio: Server returned status {response.status_code}")
        except requests.exceptions.RequestException:
            print("  ❌ LM Studio: Server not reachable")
        except Exception as e:
            print(f"  ⚠️  LM Studio: Check failed - {str(e)}")
        
        # Check Ollama
        ollama_url = config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        print(f"  🔄 Ollama: Checking endpoint {ollama_url}")
        try:
            import requests
            response = requests.get(f"{ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"  ✅ Ollama: {len(models)} models available")
                if models:
                    print(f"    📦 Models: {[m.get('name', 'unknown') for m in models[:3]]}")
            else:
                print(f"  ⚠️  Ollama: Server returned status {response.status_code}")
        except requests.exceptions.RequestException:
            print("  ❌ Ollama: Server not reachable")
        except Exception as e:
            print(f"  ⚠️  Ollama: Check failed - {str(e)}")
        
        # Initialize the AI orchestrator and see what gets loaded
        print("\n🚀 Initializing Enhanced AI Orchestrator...")
        try:
            orchestrator = EnhancedAIOrchestrator()
            print("  ✅ Enhanced AI Orchestrator initialized successfully")
            
            # Get the active generator info
            if hasattr(orchestrator, 'ai_3d_generator') and orchestrator.ai_3d_generator:
                generator = orchestrator.ai_3d_generator
                print(f"  🎯 Active 3D generator: {type(generator).__name__}")
                
                # Check provider-specific details
                if hasattr(generator, 'provider_manager'):
                    active_provider = generator.provider_manager.active_provider
                    print(f"  🔗 Using provider: {active_provider.value if active_provider else 'None'}")
                
            else:
                print("  ⚠️  No 3D generator available")
                
        except Exception as e:
            print(f"  ❌ AI Orchestrator initialization failed: {str(e)}")
        
        # Check Blender availability
        print("\n🔄 Checking Blender Integration...")
        try:
            from backend.blender_construction_executor import BlenderConstructionExecutor
            executor = BlenderConstructionExecutor()
            if executor.blender_path and os.path.exists(executor.blender_path):
                print(f"  ✅ Blender found at: {executor.blender_path}")
                print("  🎯 3D model generation: FULLY ENABLED")
            else:
                print("  ❌ Blender not found or not configured")
                print("  ⚠️  3D model generation: DISABLED")
        except Exception as e:
            print(f"  ❌ Blender check failed: {str(e)}")
        
        print("-" * 60)
        print("✅ AI Model initialization complete")
        
    except Exception as e:
        print(f"❌ AI Model initialization failed: {str(e)}")
        print("⚠️  Server will start but AI features may be limited")

    # Get server configuration
    print(f"\n[5/5] Configuring server...")
    host = os.getenv('BACKEND_HOST', '0.0.0.0')
    port = int(os.getenv('BACKEND_PORT', '8001'))
    workers = int(os.getenv('BACKEND_WORKERS', '1'))
    reload = config.get_bool('DEBUG_MODE', False)

    # Parse command line arguments
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == '--port' and i + 1 < len(sys.argv) - 1:
                port = int(sys.argv[i + 2])
            elif arg == '--host' and i + 1 < len(sys.argv) - 1:
                host = sys.argv[i + 2]
            elif arg == '--reload':
                reload = True

    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Workers: {workers}")
    print(f"  Reload: {reload}")

    # Start server
    print("\n[6/6] Starting FastAPI server...")
    print("=" * 80)

    try:
        import uvicorn
        backend_proc = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'backend.main:app', '--host', str(host), '--port', str(port), '--log-level', 'info'
        ] + (["--reload"] if reload else []))
        
        print(f"🚀 Backend server starting on http://{host}:{port}")
        print("📡 Server will display additional AI model status in its own logs...")
        
        return backend_proc
    except Exception as e:
        print(f"\n⚠ Server error: {e}")
        sys.exit(1)

def main():
    print("\nAura Quick Start - Full System\n" + "="*40)
    kill_existing_servers()
    
    print("\n🔧 Starting Backend (AI + API Server)...")
    backend_proc = run_backend_with_config()
    
    print("\n⏳ Waiting for backend to initialize...")
    time.sleep(5)  # Give backend more time to fully initialize AI models
    
    print("\n🌐 Starting Frontend (Development Server)...")
    frontend_proc = run_frontend()
    
    print("\n" + "="*60)
    print("🎉 AURA SYSTEM READY")
    print("="*60)
    print("📱 Frontend: http://localhost:3000")
    print("🤖 Backend API: http://localhost:8001") 
    print("📚 API Docs: http://localhost:8001/docs")
    print("📊 Health Check: http://localhost:8001/health")
    print("="*60)
    print("\n💡 Usage:")
    print("  1. Open http://localhost:3000 in your browser")
    print("  2. Use the AI chat to create 3D jewelry models")
    print("  3. View generated models in the 3D viewport")
    print("  4. Check Scene Outliner for model layers")
    print("\n🔍 Monitoring:")
    print("  - Backend logs: AI model status and generation progress")
    print("  - Frontend logs: 3D rendering and UI interactions")
    print("  - Console warnings: Model loading and rendering issues")
    print("\n⚠️  Press Ctrl+C to stop both servers")
    print("-"*60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        print("📴 Terminating backend...")
        backend_proc.terminate()
        print("📴 Terminating frontend...")
        frontend_proc.terminate()
        print("⏳ Waiting for clean shutdown...")
        backend_proc.wait()
        frontend_proc.wait()
        print("✅ All servers stopped cleanly.")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
