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


# Monitoring Schemas
class MonitoringStats(BaseModel):
    total_papers: int
    total_chunks: int
    total_queries: int
    total_cost_usd: float
    avg_response_time_ms: float
    queries_today: int
