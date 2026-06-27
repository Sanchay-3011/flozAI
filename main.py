"""
FlozAI API Server Entrypoint
"""
import sys
from pathlib import Path

# ─── Step 1: fix path FIRST, before any flozai imports ───
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# ─── Step 2: load .env SECOND, before any flozai imports ───
from dotenv import load_dotenv
load_dotenv()

# ─── Step 3: NOW safe to import flozai (key is in environment) ───
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from flozai.api.routes import app
from flozai.utils.logger import setup_logging
from fastapi.responses import JSONResponse
from fastapi.exceptions import ResponseValidationError

setup_logging()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    return JSONResponse(
        status_code=500,
        content={
            "error": "Unhandled Server Crash",
            "message": str(exc),
            "traceback": traceback.format_exc()
        }
    )

@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "ResponseValidationError",
            "message": str(exc),
            "errors": exc.errors()
        }
    )

# ─── Step 4: CORS middleware ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Step 5: entrypoint ───
import os

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    uvicorn.run(
        "flozai.api.routes:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )