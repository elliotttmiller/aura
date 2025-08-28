from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse
import subprocess
import os
import logging
import shlex

app = FastAPI()

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

BLENDER_PATH = os.environ.get("BLENDER_PATH", r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe")
AURA_BACKEND_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "aura_backend.py"))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def get_output_path(prompt: str) -> str:
    safe_name = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = "_".join(safe_name.split())[:40]
    return os.path.join(OUTPUT_DIR, f"output_{safe_name}.stl")

@app.post("/generate")
async def generate_design(request: Request):
    logger.debug('Received /generate request')
    try:
        data = await request.json()
        logger.debug('Request data: %s', data)
        prompt = data.get("prompt", "default_prompt")
        output_file = get_output_path(prompt)
        if os.path.exists(output_file):
            os.remove(output_file)
        command = [
            BLENDER_PATH, "--background", "--python", AURA_BACKEND_SCRIPT, "--",
            shlex.quote(prompt),
            "--output", output_file,
            "--ring_size", str(data.get("ring_size", 7.0)),
            "--stone_carat", str(data.get("stone_carat", 1.0)),
            "--stone_shape", data.get("stone_shape", "ROUND"),
            "--metal", data.get("metal", "GOLD")
        ]
        logger.debug(f"Blender command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        logger.debug("[Blender stdout]\n%s", result.stdout)
        if result.stderr:
            logger.error("[Blender stderr]\n%s", result.stderr)
        if result.returncode != 0 or not os.path.exists(output_file):
            error_message = result.stderr or "Blender process failed and no output file was generated."
            return JSONResponse(status_code=500, content={"error": error_message, "stdout": result.stdout})
        logger.debug('Design generated successfully: %s', output_file)
        return JSONResponse({
            "file": os.path.basename(output_file),
            "message": "Design generated successfully."
        })
    except Exception as e:
        logger.exception('Exception in /generate')
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/output/{filename}")
async def serve_stl(filename: str):
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

@app.get("/")
async def root():
    return {"status": "Aura backend running"}
