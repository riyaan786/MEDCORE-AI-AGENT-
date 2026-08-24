from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.llm import run_agent


app = FastAPI(
    title="MedCore AI",
    description="Hospital operations AI agent",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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

    return FileResponse(frontend_path)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "medcore-ai",
    }


@app.post("/chat")
def chat(request: ChatRequest):

    result = run_agent(request.message)

    return {
        "success": result["success"],
        "tool": result["tool"],
        "response": result["response"],
    }