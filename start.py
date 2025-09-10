
"""
Aura V5.0 Master Orchestrator - Launch All Services
==================================================

Launches all three components of the V5.0 Autonomous Cognitive Architecture:
1. AI Artist Server (Shap-E) - Port 8002
2. Backend Orchestrator (Two-stage AI pipeline) - Port 8001  
3. Frontend Web Application - Port 8000

Part of the V5.0 Autonomous Cognitive Architecture.
"""

import sys
import os
import subprocess
import time
import webbrowser
import requests

# ================= CONFIGURATION =================
AURA_PATH = os.path.abspath(os.path.dirname(__file__))
VENV_PATH = os.path.join(AURA_PATH, "venv", "Scripts", "python.exe")

# Service URLs
SERVICES = {
    "AI Artist Server": "http://localhost:8002",
    "Backend Orchestrator": "http://localhost:8001", 
    "Frontend Application": "http://localhost:8000"
}

print("=== AURA V5.0 AUTONOMOUS COGNITIVE ARCHITECTURE ===")
print("Initializing the complete AI pipeline...")

# =============== SETUP ENVIRONMENT ===============
venv_path = os.path.join(AURA_PATH, 'venv', 'Scripts')
os.environ['PATH'] = venv_path + os.pathsep + os.environ.get('PATH', '')
venv_python = VENV_PATH if os.path.exists(VENV_PATH) else sys.executable

print(f"Using Python: {venv_python}")

# =============== LAUNCH SERVICES ===============

print("\n1. Starting AI Artist Server (Shap-E Model)...")
ai_server_proc = subprocess.Popen([
    venv_python, '-m', 'uvicorn', 'ai_server:app', '--port', '8002', '--host', '0.0.0.0'
], cwd=AURA_PATH)

print("2. Starting Backend Orchestrator (Two-Stage AI Pipeline)...")
backend_proc = subprocess.Popen([
    venv_python, '-m', 'uvicorn', 'backend.main:app', '--port', '8001', '--host', '0.0.0.0'
], cwd=AURA_PATH)

print("3. Starting Frontend Web Application...")
frontend_proc = subprocess.Popen([
    venv_python, '-m', 'uvicorn', 'frontend.app:app', '--port', '8000', '--host', '0.0.0.0'
], cwd=AURA_PATH)

def wait_for_service(name: str, url: str, timeout: int = 30) -> bool:
    """Wait for a service to become available."""
    print(f"   Waiting for {name}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print(f"   ✓ {name} is ready")
                return True
        except Exception:
            pass
        time.sleep(2)
    print(f"   ✗ {name} failed to start in time")
    return False

# =============== WAIT FOR SERVICES ===============
print("\nWaiting for services to initialize...")

# Check each service
all_ready = True
for service_name, service_url in SERVICES.items():
    if not wait_for_service(service_name, service_url):
        all_ready = False

if all_ready:
    print("\n=== AURA V5.0 PIPELINE READY ===")
    print("Architecture: Two-Stage Autonomous AI")
    print("Stage 1: LLM System Architect (Llama 3.1)")  
    print("Stage 2: AI Master Artisan (Shap-E)")
    print("Stage 3: Hyper-Parametric Executor (Blender)")
    print()
    for service_name, service_url in SERVICES.items():
        print(f"{service_name}: {service_url}")
    print()
    print("🎨 Submit a creative prompt to experience autonomous AI design!")
    
    # Open frontend in browser
    print("\nOpening web interface...")
    webbrowser.open('http://localhost:8000')
    
else:
    print("\n⚠️  Some services failed to start. Check the logs above.")

print("\n=== SERVICE MANAGEMENT ===")
print("Press Ctrl+C to stop all services")

# =============== WAIT FOR EXIT ===============
try:
    # Keep the main process alive
    while True:
        time.sleep(1)
        
        # Check if any process has died
        for proc_name, proc in [
            ("AI Server", ai_server_proc),
            ("Backend", backend_proc), 
            ("Frontend", frontend_proc)
        ]:
            if proc.poll() is not None:
                print(f"⚠️  {proc_name} process has stopped unexpectedly")
                break
        
except KeyboardInterrupt:
    print("\n\nShutting down Aura V5.0 services...")
    
    # Terminate all processes gracefully
    processes = [
        ("AI Artist Server", ai_server_proc),
        ("Backend Orchestrator", backend_proc),
        ("Frontend Application", frontend_proc)
    ]
    
    for name, proc in processes:
        if proc.poll() is None:  # Process is still running
            print(f"Stopping {name}...")
            proc.terminate()
            
    # Give processes time to shut down gracefully
    time.sleep(2)
    
    # Force kill if necessary
    for name, proc in processes:
        if proc.poll() is None:
            print(f"Force stopping {name}...")
            proc.kill()
    
    print("All services stopped.")
    print("Aura V5.0 Autonomous Cognitive Architecture shutdown complete.")
