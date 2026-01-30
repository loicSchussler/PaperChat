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
    Poser une question sur les articles indexés
    TODO: Implémenter le pipeline RAG complet
    """
    # TODO: Implémenter
    # 1. Vectoriser la question
    # 2. Recherche vectorielle dans pgvector
    # 3. Construire le contexte
    # 4. Appel OpenAI pour génération
    # 5. Logger la requête
    # 6. Calculer le coût

    raise HTTPException(status_code=501, detail="À implémenter")
