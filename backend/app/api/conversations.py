"""
Conversations API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
import json
from app.database import get_db
from app.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationListItem,
    MessageResponse,
    SourceCitation
)
import app.models as models

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    new_conversation = models.Conversation(
        title=conversation.title or "Nouvelle conversation"
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation


@router.get("", response_model=List[ConversationListItem])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List all conversations with preview"""
    conversations = db.query(models.Conversation).order_by(
        desc(models.Conversation.updated_at)
    ).offset(skip).limit(limit).all()

    result = []
    for conv in conversations:
        # Get message count
        message_count = db.query(func.count(models.Message.id)).filter(
            models.Message.conversation_id == conv.id
        ).scalar() or 0

        # Get last message preview
        last_message = db.query(models.Message).filter(
            models.Message.conversation_id == conv.id
        ).order_by(desc(models.Message.created_at)).first()

        last_message_preview = None
        if last_message:
            preview_text = last_message.content[:100]
            if len(last_message.content) > 100:
                preview_text += "..."
            last_message_preview = preview_text

        result.append(ConversationListItem(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=message_count,
            last_message_preview=last_message_preview
        ))

    return result


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get all messages
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.created_at).all()

    # Format messages with sources
    formatted_messages = []
    for msg in messages:
        sources = None
        if msg.sources:
            sources_data = json.loads(msg.sources)
            sources = [SourceCitation(**src) for src in sources_data]
            

        formatted_messages.append(MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            sources=sources,
            cost_usd=msg.cost_usd,
            response_time_ms=msg.response_time_ms,
            created_at=msg.created_at
        ))

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=formatted_messages
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted successfully"}


@router.patch("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: int,
    title: str,
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.title = title
    db.commit()

    return {"message": "Title updated successfully"}
