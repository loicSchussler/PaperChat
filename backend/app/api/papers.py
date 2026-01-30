from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import PaperResponse
import app.models as models

router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.post("/upload", response_model=PaperResponse, status_code=201)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload et indexation d'un article scientifique PDF
    TODO: Implémenter l'extraction PDF, métadonnées, chunking et embeddings
    """
    # TODO: Implémenter la logique d'upload
    raise HTTPException(status_code=501, detail="À implémenter")


@router.get("", response_model=List[PaperResponse])
async def list_papers(
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    year: int = None,
    db: Session = Depends(get_db)
):
    """
    Liste des articles avec pagination et filtres
    TODO: Implémenter la recherche et les filtres
    """
    query = db.query(models.Paper)

    if search:
        # TODO: Implémenter la recherche par titre/auteur
        pass

    if year:
        query = query.filter(models.Paper.year == year)

    papers = query.offset(skip).limit(limit).all()

    # Calculer le nombre de chunks pour chaque paper
    result = []
    for paper in papers:
        paper_dict = {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "year": paper.year,
            "abstract": paper.abstract,
            "keywords": paper.keywords,
            "nb_chunks": len(paper.chunks),
            "created_at": paper.created_at
        }
        result.append(PaperResponse(**paper_dict))

    return result


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """
    Récupérer un article spécifique
    """
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return PaperResponse(
        id=paper.id,
        title=paper.title,
        authors=paper.authors,
        year=paper.year,
        abstract=paper.abstract,
        keywords=paper.keywords,
        nb_chunks=len(paper.chunks),
        created_at=paper.created_at
    )


@router.delete("/{paper_id}", status_code=204)
async def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    """
    Supprimer un article et tous ses chunks
    """
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    db.delete(paper)
    db.commit()

    return None
