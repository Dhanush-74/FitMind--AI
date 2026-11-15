from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class MessageBase(BaseModel):
    role: str
    content: str
    message_type: str = "text"  # text, image, document
    file_name: Optional[str] = None
    timestamp: Optional[str] = None

class ConversationBase(BaseModel):
    id: Optional[str] = None
    title: str = "New Chat"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ConversationResponse(ConversationBase):
    messages: List[MessageBase] = []
    document_ids: List[str] = []

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

class RAGQuestionRequest(BaseModel):
    question: str
    conversation_id: str
    document_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    gemini_configured: bool = False
