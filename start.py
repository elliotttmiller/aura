
# File: aura/start.py
import subprocess
import webbrowser
import time
import os
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] INFO %(message)s')

# Use local paths for testing
AURA_DIR = os.path.abspath(os.path.dirname(__file__))
AI_BLUEPRINT_PATH = os.path.join(AURA_DIR, "3d-object-generation")
AI_SERVER_PORT = 5000
FRONTEND_PORT = 8000 
BACKEND_PORT = 8001

def main():
    processes = []
    try:
        # For testing without Docker, start AI server directly
        logging.info("Starting AI Inference Server (local mode)...")
        ai_server_script = os.path.join(AI_BLUEPRINT_PATH, "main_server.py")
        processes.append(subprocess.Popen([
            "python", ai_server_script
        ], cwd=AI_BLUEPRINT_PATH))
        logging.info(f"AI Server starting on port {AI_SERVER_PORT}...")
        time.sleep(3)  # Give AI server time to start

        logging.info("Launching backend service...")
        processes.append(subprocess.Popen([
            "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)
        ]))
        
        logging.info("Launching frontend service...")
        processes.append(subprocess.Popen([
            "uvicorn", "frontend.app:app", "--host", "127.0.0.1", "--port", str(FRONTEND_PORT)
        ]))
        
        time.sleep(2)
        webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
        logging.info("Aura pipeline started successfully. Press CTRL+C to shut down.")
        logging.info(f"AI Server: http://localhost:{AI_SERVER_PORT}")
        logging.info(f"Backend: http://localhost:{BACKEND_PORT}")
        logging.info(f"Frontend: http://localhost:{FRONTEND_PORT}")
        
        while True: 
            time.sleep(1)
    except KeyboardInterrupt: 
        logging.info("Shutting down all services...")
    finally:
        for p in processes: 
            p.terminate()
        logging.info("All services terminated.")

if __name__ == "__main__":
    main()
