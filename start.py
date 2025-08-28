
# ================= IMPORTS =================
import sys
import os
import subprocess
import time
import webbrowser
import requests

# ================= PATHS =================
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
AURA_PATH = os.path.abspath(os.path.dirname(__file__))
VENV_PATH = os.path.join(AURA_PATH, "venv", "Scripts", "python.exe")

# =============== LAUNCH BLENDER ===============



def launch_blender_server():
    env = os.environ.copy()
    env["PYTHONHOME"] = os.path.join(AURA_PATH, "venv")
    env["PYTHONPATH"] = os.path.join(AURA_PATH, "venv", "Lib")
    blender_script = os.path.join(AURA_PATH, "backend", "aura_backend.py")
    blender_cmd = [BLENDER_PATH, "--background", "--python", blender_script]
    subprocess.Popen(blender_cmd, env=env)
    print("Blender persistent server started in background mode.")

launch_blender_server()

# =============== SETUP VENV ENVIRONMENT ===============
venv_path = os.path.join(AURA_PATH, 'venv', 'Scripts')
os.environ['PATH'] = venv_path + os.pathsep + os.environ.get('PATH', '')
venv_python = VENV_PATH if os.path.exists(VENV_PATH) else sys.executable

# =============== LAUNCH SERVICES ===============
backend_proc = subprocess.Popen([
    venv_python, '-m', 'uvicorn', 'backend.main:app', '--port', '8001'
])
frontend_proc = subprocess.Popen([
    venv_python, '-m', 'uvicorn', 'frontend.app:app', '--port', '8000'
])

def wait_for_service(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

print('Aura pipeline started:')
print('Frontend: http://localhost:8000')
print('Backend: http://localhost:8001')
print('Submit a prompt in the web UI to generate a design.')

# Wait for frontend to be available, then open in browser
if wait_for_service('http://localhost:8000'):
    webbrowser.open('http://localhost:8000')
    print('Frontend UI opened in your browser.')
else:
    print('Frontend did not start in time. Please open http://localhost:8000 manually.')

# =============== WAIT FOR EXIT ===============
try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    backend_proc.terminate()
    frontend_proc.terminate()
