from pathlib import Path
import logging
import logging.config
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.llm import run_agent


def setup_logging():
    """Configure logging from logging.toml."""
    config_path = (
        Path(__file__).parent.parent / "logging.toml"
    )
    try:
        logging.config.fileConfig(
            config_path,
            disable_existing_loggers=False,
        )
    except (FileNotFoundError, ImportError):
        logging.basicConfig(
            level=logging.INFO,
            format=(
                "%(asctime)s | %(levelname)-8s "
                "| %(name)s | %(message)s"
            ),
        )


setup_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title="MedCore AI",
    description="Hospital operations AI agent",
    version="1.0.0",
)


# CORS: restrict to known origins; override via env var.
_allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
]

_env_origins = os.environ.get("CORS_ORIGINS", "")
if _env_origins:
    _allowed_origins.extend(
        o.strip()
        for o in _env_origins.split(",")
        if o.strip()
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    frontend_path = (
        Path(__file__).parent.parent
        / "frontend"
        / "index.html"
    )

    if frontend_path.exists():
        return FileResponse(frontend_path)

    return {"message": "MedCore AI is running"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "medcore-ai",
    }


@app.post("/chat")
def chat(request: ChatRequest):

    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message must not be empty.",
        )

    try:

        result = run_agent(request.message)

    except Exception as error:

        logger.exception(
            "Error processing chat request: %s",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred.",
        )

    return {
        "success": result["success"],
        "tool": result["tool"],
        "response": result["response"],
    }