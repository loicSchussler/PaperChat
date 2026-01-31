from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.rag import generate_rag_answer
from app.models import QueryLog

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about indexed papers using RAG pipeline
    """
    try:
        # Generate answer using RAG pipeline
        result = await generate_rag_answer(
            db=db,
            question=request.question,
            max_sources=request.max_sources,
            paper_ids=request.paper_ids
        )

        # Log the query in the database
        query_log = QueryLog(
            question=request.question,
            answer=result["answer"],
            nb_sources=len(result["sources"]),
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            cost_usd=result["cost_usd"],
            response_time_ms=result["response_time_ms"]
        )
        db.add(query_log)
        db.commit()

        # Return the response (without internal token counts)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            cost_usd=result["cost_usd"],
            response_time_ms=result["response_time_ms"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
