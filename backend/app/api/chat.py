from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about indexed papers
    TODO: Implement complete RAG pipeline
    """
    # TODO: Implement
    # 1. Vectorize the question
    # 2. Vector search in pgvector
    # 3. Build the context
    # 4. Call OpenAI for generation
    # 5. Log the query
    # 6. Calculate the cost

    raise HTTPException(status_code=501, detail="To be implemented")
