from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.rag import generate_rag_answer_with_context
from app.models import QueryLog, Conversation, Message
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about indexed papers using RAG pipeline with conversation context
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Load conversation history
            messages = db.query(Message).filter(
                Message.conversation_id == request.conversation_id
            ).order_by(Message.created_at).all()

            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
        else:
            # Create new conversation
            conversation = Conversation(title=request.question[:50] + "..." if len(request.question) > 50 else request.question)
            db.add(conversation)
            db.flush()  # Get the ID without committing
            conversation_history = []

        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.question
        )
        db.add(user_message)

        # Generate answer using RAG pipeline with conversation context
        result = await generate_rag_answer_with_context(
            db=db,
            question=request.question,
            conversation_history=conversation_history,
            max_sources=request.max_sources,
            paper_ids=request.paper_ids
        )

        # Save assistant message with sources
        sources_json = json.dumps([
            {
                "paper_title": src["paper_title"],
                "paper_year": src["paper_year"],
                "section_name": src["section_name"],
                "content": src["content"],
                "relevance_score": src["relevance_score"]
            }
            for src in result["sources"]
        ])

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
            sources=sources_json,
            cost_usd=result["cost_usd"],
            response_time_ms=result["response_time_ms"]
        )
        db.add(assistant_message)

        # Log the query
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

        # Return the response
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            cost_usd=result["cost_usd"],
            response_time_ms=result["response_time_ms"],
            conversation_id=conversation.id
        )

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
