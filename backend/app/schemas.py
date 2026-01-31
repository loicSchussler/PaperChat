from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Paper Schemas
class PaperBase(BaseModel):
    title: str
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None


class PaperCreate(PaperBase):
    pass


class PaperResponse(PaperBase):
    id: int
    nb_chunks: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# Chat Schemas
class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[int] = None  # Optional conversation ID for context
    paper_ids: Optional[List[int]] = None
    max_sources: int = 5


class SourceCitation(BaseModel):
    paper_title: str
    paper_year: Optional[int]
    section_name: Optional[str]
    content: str
    relevance_score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    cost_usd: float
    response_time_ms: int
    conversation_id: int  # ID of the conversation this message belongs to


# Conversation Schemas
class MessageBase(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    sources: Optional[List[SourceCitation]] = None
    cost_usd: float = 0.0
    response_time_ms: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_preview: Optional[str] = None

    class Config:
        from_attributes = True


# Monitoring Schemas
class MonitoringStats(BaseModel):
    total_papers: int
    total_chunks: int
    total_queries: int
    total_cost_usd: float
    avg_response_time_ms: float
    queries_today: int
