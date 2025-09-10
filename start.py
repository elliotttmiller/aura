
"""
Aura V7.0 Master Orchestrator - Professional 2-Server Architecture  
================================================================

Launches the V7.0 Professional Integration components:
1. Backend Orchestrator (Two-stage AI pipeline) - Port 8001
2. Frontend Web Application - Port 8000

External Dependencies (User-Managed):
- LM Studio with Meta-Llama-3.1-8B-Instruct (Port 1234)
- Dedicated AI Environment with Shap-E model

Part of the V7.0 Professional Integration.
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

# V7.0 Service URLs - Lean 2-server architecture
SERVICES = {
    "Backend Orchestrator": "http://localhost:8001", 
    "Frontend Application": "http://localhost:8000"
}

# External Dependencies
EXTERNAL_SERVICES = {
    "LM Studio (Llama 3.1)": "http://localhost:1234"
}

# Check for V6.0 Sandbox Mode
SANDBOX_MODE = os.environ.get("AURA_SANDBOX_MODE", "").lower() == "true"

if SANDBOX_MODE:
    print("=== AURA V6.0 SENTIENT COGNITIVE LOOP - SANDBOX MODE ===")
    print("Verifiable sandbox environment for truthful end-to-end testing")
else:
    print("=== AURA V7.0 PROFESSIONAL INTEGRATION ===")
    print("State-of-the-art architecture aligned with OpenAI best practices")

# =============== SETUP ENVIRONMENT ===============
venv_path = os.path.join(AURA_PATH, 'venv', 'Scripts')
os.environ['PATH'] = venv_path + os.pathsep + os.environ.get('PATH', '')
venv_python = VENV_PATH if os.path.exists(VENV_PATH) else sys.executable

print(f"Using Python: {venv_python}")

# =============== CHECK EXTERNAL DEPENDENCIES ===============
print("\nChecking external dependencies...")

def check_external_service(name: str, url: str) -> bool:
    """Check if external service is available."""
    try:
        r = requests.get(url, timeout=3)
        if r.status_code in [200, 404]:  # 404 is OK for base endpoints
            print(f"   ✓ {name} is available")
            return True
    except Exception:
        pass
    print(f"   ⚠️  {name} is not available - ensure it's running")
    return False

lm_studio_available = check_external_service("LM Studio (Llama 3.1)", "http://localhost:1234")

if not lm_studio_available:
    print("\n⚠️  WARNING: LM Studio is not detected.")
    print("   Please ensure LM Studio is running with Meta-Llama-3.1-8B-Instruct")
    print("   on port 1234 for full V7.0 functionality.")

# =============== LAUNCH V7.0 SERVICES ===============

print("\n1. Starting Backend Orchestrator (Professional AI Pipeline)...")
backend_proc = subprocess.Popen([
    venv_python, '-m', 'uvicorn', 'backend.main:app', '--port', '8001', '--host', '0.0.0.0'
], cwd=AURA_PATH)

print("2. Starting Frontend Web Application...")
frontend_proc = subprocess.Popen([
    venv_python, '-m', 'uvicorn', 'frontend.app:app', '--port', '8000', '--host', '0.0.0.0'
], cwd=AURA_PATH)

# Start appropriate 3D server based on mode
if SANDBOX_MODE:
    print("3. Starting V6.0 Sandbox 3D Server (Verifiable Testing)...")
    ai_server_proc = subprocess.Popen([
        venv_python, 'sandbox_3d_server.py'
    ], cwd=AURA_PATH)
else:
    # In production mode, we assume external AI environment is managed separately
    print("3. External AI Environment: User-managed (AI server expected at port 8002)")
    ai_server_proc = None

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
print("\nWaiting for V7.0 services to initialize...")

# Check each service
all_ready = True
for service_name, service_url in SERVICES.items():
    if not wait_for_service(service_name, service_url):
        all_ready = False

if all_ready:
    print("\n=== AURA V7.0 PROFESSIONAL INTEGRATION READY ===")
    print("Architecture: State-of-the-Art 2-Server Design")
    print("Blender Engine: Aligned with OpenAI Shap-E Best Practices")  
    print("Features: Dynamic Camera Framing, GPU Optimization, Professional Scene Management")
    print()
    for service_name, service_url in SERVICES.items():
        print(f"{service_name}: {service_url}")
    print()
    for service_name, service_url in EXTERNAL_SERVICES.items():
        status = "✓ Available" if service_name == "LM Studio (Llama 3.1)" and lm_studio_available else "⚠️ External"
        print(f"{service_name}: {service_url} ({status})")
    print()
    print("🎨 Submit a creative prompt to experience the V7.0 professional pipeline!")
    
    # Open frontend in browser
    print("\nOpening professional web interface...")
    webbrowser.open('http://localhost:8000')
    
else:
    print("\n⚠️  Some services failed to start. Check the logs above.")

print("\n=== V7.0 SERVICE MANAGEMENT ===")
print("Press Ctrl+C to stop all services")

# =============== WAIT FOR EXIT ===============
try:
    # Keep the main process alive
    while True:
        time.sleep(1)
        
        # Check if any process has died
        processes_to_check = [
            ("Backend", backend_proc), 
            ("Frontend", frontend_proc)
        ]
        
        if ai_server_proc is not None:
            processes_to_check.append(("AI Server", ai_server_proc))
        
        for proc_name, proc in processes_to_check:
            if proc.poll() is not None:
                print(f"⚠️  {proc_name} process has stopped unexpectedly")
                break
        
except KeyboardInterrupt:
    print("\n\nShutting down Aura V7.0 services...")
    
    # Terminate all processes gracefully
    processes = [
        ("Backend Orchestrator", backend_proc),
        ("Frontend Application", frontend_proc)
    ]
    
    if ai_server_proc is not None:
        processes.append(("AI Server", ai_server_proc))
    
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
    print("Aura V6.0/V7.0 Integration shutdown complete.")
