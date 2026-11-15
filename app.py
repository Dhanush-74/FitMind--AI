import os
import sys
import webbrowser
import threading
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
import uvicorn

import config
from database.db import init_database
from database.models import (
    ChatRequest, ChatResponse, ConversationUpdate,
    HealthResponse, RAGQuestionRequest
)
from backend.chat_service import chat_service
from backend.conversation_manager import conversation_manager
from backend.image_analyzer import validate_image
from backend.document_processor import document_processor
from backend.gemini_service import gemini_service

# Initialize database
init_database()

# Create FastAPI app
app = FastAPI(
    title="FitMind AI",
    description="Intelligent Health & Fitness Coach",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
FRONTEND_DIR = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/health")
async def health_check():
    gemini_status = gemini_service.health_check()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "gemini_configured": gemini_service.is_available(),
        "gemini_status": gemini_status.get("status", "unknown"),
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    result = await chat_service.process_message(
        request.message.strip(), request.conversation_id
    )
    return result


@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    message: str = Form(""),
    conversation_id: Optional[str] = Form(None),
):
    file_bytes = await file.read()
    content_type = file.content_type or "image/jpeg"
    
    valid, error_msg = validate_image(file_bytes, content_type)
    if not valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    result = await chat_service.process_image(
        file_bytes, content_type, message, conversation_id
    )
    return result


@app.post("/api/analyze-document")
async def analyze_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
):
    file_bytes = await file.read()
    filename = file.filename or "document"
    content_type = file.content_type or ""
    
    valid, error_msg = document_processor.validate_document(file_bytes, content_type, filename)
    if not valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    result = await chat_service.process_document(
        file_bytes, filename, conversation_id
    )
    return result


@app.post("/api/rag/question")
async def rag_question(request: RAGQuestionRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    result = await chat_service.answer_document_question(
        request.question.strip(), request.conversation_id, request.document_id
    )
    return result


@app.get("/api/conversations")
async def get_conversations():
    convs = conversation_manager.get_conversations()
    return {"conversations": convs}


@app.post("/api/conversations")
async def create_conversation():
    conv = conversation_manager.create_conversation()
    return conv


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    conv = conversation_manager.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@app.patch("/api/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, update: ConversationUpdate):
    if update.title:
        result = conversation_manager.update_conversation(conversation_id, update.title)
        if not result:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return result
    raise HTTPException(status_code=400, detail="No update data provided")


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    success = conversation_manager.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted"}


@app.delete("/api/conversations")
async def clear_conversations():
    count = conversation_manager.clear_all_conversations()
    return {"message": f"Deleted {count} conversations"}


@app.post("/api/fitness-data")
async def save_fitness_data(request: Request):
    data = await request.json()
    data_type = data.get("type")
    payload = data.get("data")
    if not data_type or not payload:
        raise HTTPException(status_code=400, detail="Missing type or data")
    result = conversation_manager.save_fitness_data(data_type, payload)
    return result


@app.get("/api/fitness-data/{data_type}")
async def get_fitness_data(data_type: str, limit: int = 30):
    data = conversation_manager.get_fitness_data(data_type, limit)
    return {"data": data}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )


def open_browser():
    webbrowser.open(f"http://{config.APP_HOST}:{config.APP_PORT}")


if __name__ == "__main__":
    print("=" * 60)
    print("  FitMind AI - Intelligent Health & Fitness Coach")
    print("=" * 60)
    if not config.GEMINI_API_KEY:
        print("\n⚠️  WARNING: GEMINI_API_KEY not set in .env file!")
        print("   AI features will be unavailable.")
        print("   Get your API key from: https://aistudio.google.com/apikey")
        print("   Then add it to the .env file\n")
    else:
        print("\n✅ Gemini API key configured")
    
    print(f"\n🚀 Starting server at http://{config.APP_HOST}:{config.APP_PORT}")
    print("   Press Ctrl+C to stop\n")
    
    # Open browser locally after a short delay
    if config.AUTO_OPEN_BROWSER:
        threading.Timer(1.5, open_browser).start()
    
    uvicorn.run(
        "app:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=config.DEBUG,
        log_level="info",
    )
