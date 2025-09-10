# File: aura/main.py
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse
import subprocess, os, logging, shlex, requests

app = FastAPI()
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

BLENDER_PATH = os.environ.get("BLENDER_PATH", r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe")
BLENDER_PROC_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blender_proc.py"))
BLENDER_TEST_STUB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blender_test_stub.py"))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
NVIDIA_BLUEPRINT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "3d-object-generation"))

def get_output_path(prompt: str) -> str:
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    safe_name = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = "_".join(safe_name.split())[:40]
    return os.path.join(OUTPUT_DIR, f"final_{safe_name}.stl")

@app.post("/generate")
async def generate_design(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "default_prompt")
        
        logger.info("Sending request to persistent AI Inference Server...")
        creative_prompt = f"a photorealistic, highly detailed 3d model of a {data.get('metal', 'gold')} ring with {prompt}, jewelry design"
        ai_response = requests.post("http://localhost:5000/generate", json={"prompt": creative_prompt}, timeout=300)
        ai_response.raise_for_status()
        ai_data = ai_response.json()
        
        container_path = ai_data['file_path']
        filename = os.path.basename(container_path)
        ai_model_host_path = os.path.join(NVIDIA_BLUEPRINT_PATH, "output", filename)
        
        if not os.path.exists(ai_model_host_path):
            raise FileNotFoundError(f"AI file not found on host at: {ai_model_host_path}")
        
        final_output_file = get_output_path(prompt)
        if os.path.exists(final_output_file): os.remove(final_output_file)

        # Use test stub if Blender not available
        if not os.path.exists(BLENDER_PATH) and os.name != 'nt':
            logger.info("Using Blender test stub for processing...")
            command = ["python", BLENDER_TEST_STUB, "--", "--input", ai_model_host_path, "--output", final_output_file, "--ring_size", str(data.get("ring_size", 7.0))]
        else:
            command = [BLENDER_PATH, "--background", "--python", BLENDER_PROC_SCRIPT, "--", "--input", ai_model_host_path, "--output", final_output_file, "--ring_size", str(data.get("ring_size", 7.0))]
        
        logger.debug(f"Executing post-processor: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.returncode != 0 or not os.path.exists(final_output_file):
            logger.error("[Post-processor stderr]\n%s", result.stderr)
            logger.error("[Post-processor stdout]\n%s", result.stdout)
            raise RuntimeError(f"Post-processing failed: {result.stderr}")

        return JSONResponse({"file": os.path.basename(final_output_file), "message": "Design generated and processed successfully."})
    except Exception as e:
        logger.exception('Exception in /generate orchestrator')
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/output/{filename}")
async def serve_stl(filename: str):
    logger.debug('Received STL file request: %s', filename)
    try:
        if not filename.startswith("final_") and not filename.startswith("output_"):
            logger.error(f"Rejected STL request: {filename} (invalid pattern)")
            return Response(status_code=400)
        if not filename.endswith(".stl"):
            logger.error(f"Rejected STL request: {filename} (not STL file)")
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

@app.get("/")
async def root():
    return {"status": "Aura backend running"}
