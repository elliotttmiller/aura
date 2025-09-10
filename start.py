
# File: aura/start.py
import subprocess
import webbrowser
import time
import os
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] INFO %(message)s')

NVIDIA_BLUEPRINT_PATH = os.environ.get("NVIDIA_BLUEPRINT_PATH", "C:/path/to/your/3d-object-generation")
AI_SERVER_PORT = 5000; FRONTEND_PORT = 8000; BACKEND_PORT = 8001

def main():
    processes = []
    try:
        logging.info("Launching AI Inference Server...")
        ai_output_dir = os.path.join(NVIDIA_BLUEPRINT_PATH, "output")
        if not os.path.exists(ai_output_dir): os.makedirs(ai_output_dir)
        docker_command = ["docker", "run", "--rm", "--gpus", "all", "-it", "-p", f"{AI_SERVER_PORT}:5000", "-v", f"{ai_output_dir}:/workspace/output", "aura-ai-engine"]
        processes.append(subprocess.Popen(docker_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        logging.info(f"AI Server starting... This may take a minute to load the model.")
        time.sleep(15)

        logging.info("Launching backend service...")
        processes.append(subprocess.Popen(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)]))
        
        logging.info("Launching frontend service...")
        processes.append(subprocess.Popen(["uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(FRONTEND_PORT)]))
        
        time.sleep(2)
        webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
        logging.info("Aura pipeline started successfully. Press CTRL+C to shut down.")
        
        while True: time.sleep(1)
    except KeyboardInterrupt: logging.info("Shutting down all services...")
    finally:
        for p in processes: p.terminate()
        logging.info("All services terminated.")

if __name__ == "__main__":
    main()
