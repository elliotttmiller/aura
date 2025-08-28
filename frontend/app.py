from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import requests
import logging
import os

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Serve Static Frontend Files (HTML, CSS, JS) ---
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# --- Serve Generated 3D Models from the 'output' directory ---
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

@app.get("/")
async def index() -> FileResponse:
    return FileResponse("frontend/static/index.html")

@app.post("/generate")
async def generate(request: Request) -> JSONResponse:
    logger.debug('Frontend /generate called')
    try:
        data = await request.json()
        logger.debug('Forwarding request to backend')
        response = requests.post("http://localhost:8001/generate", json=data, timeout=300)
        response.raise_for_status()
        resp_data = response.json()
        logger.debug('Backend response: %s', resp_data)
        return JSONResponse(resp_data)
    except requests.exceptions.RequestException as e:
        logger.exception('Could not connect to backend service.')
        return JSONResponse(status_code=503, content={'error': 'Backend service is unavailable.'})
    except Exception as e:
        logger.exception('Exception in frontend /generate')
        return JSONResponse(status_code=500, content={'error': str(e)})
