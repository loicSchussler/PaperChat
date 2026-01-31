from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import shutil
import os
from datetime import datetime

from app.database import get_db
from app.schemas import PaperResponse
import app.models as models
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.metadata_extractor import extract_metadata_from_text
from app.services.chunker import chunk_text
from app.services.embeddings import generate_embeddings_batch
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/papers", tags=["papers"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=PaperResponse, status_code=201)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and indexing of a scientific paper PDF

    Steps:
    1. Validate PDF file
    2. Save uploaded file
    3. Extract text from PDF
    4. Extract metadata (title, authors, year, etc.)
    5. Chunk the text
    6. Generate embeddings for chunks
    7. Save paper and chunks to database
    """

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate unique filename to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Extract text from PDF
        extracted_text = extract_text_from_pdf(str(file_path))

        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the PDF"
            )

        # Step 2: Extract metadata from text
        text_preview = extracted_text[:3000]

        metadata = await extract_metadata_from_text(text_preview)

        if metadata.get('error'):
            logger.error(f"❌ Metadata extraction had error: {metadata['error']}")

        # Step 3: Chunk the text
        # Note: metadata_extractor returns sections if available
        sections = metadata.get("sections", None)
        chunks = chunk_text(extracted_text, sections)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not create chunks from the PDF text"
            )

        # Step 4: Generate embeddings for all chunks
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = await generate_embeddings_batch(chunk_texts)

        # Step 5: Create Paper record
        # Use filename as fallback if title is None or empty
        title = metadata.get("title") or file.filename

        paper = models.Paper(
            title=title,
            authors=metadata.get("authors") or [],
            year=metadata.get("year"),
            abstract=metadata.get("abstract"),
            keywords=metadata.get("keywords") or [],
            pdf_path=str(file_path)
        )

        db.add(paper)
        db.flush()  # Get paper.id without committing

        # Step 6: Create Chunk records with embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk_record = models.Chunk(
                paper_id=paper.id,
                content=chunk["content"],
                section_name=chunk.get("section_name"),
                chunk_index=chunk["chunk_index"],
                embedding=embedding
            )
            db.add(chunk_record)

        # Commit all changes
        db.commit()
        db.refresh(paper)

        # Return response
        return PaperResponse(
            id=paper.id,
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            abstract=paper.abstract,
            keywords=paper.keywords,
            nb_chunks=len(chunks),
            created_at=paper.created_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        if file_path.exists():
            os.remove(file_path)
        raise
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            os.remove(file_path)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.get("", response_model=List[PaperResponse])
async def list_papers(
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    year: int = None,
    db: Session = Depends(get_db)
):
    """
    List papers with pagination and filters
    TODO: Implement search and filters
    """
    query = db.query(models.Paper)

    if search:
        # TODO: Implement search by title/author
        pass

    if year:
        query = query.filter(models.Paper.year == year)

    papers = query.offset(skip).limit(limit).all()

    # Calculate number of chunks for each paper
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
    Retrieve a specific paper
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
    Delete a paper and all its chunks
    """
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    db.delete(paper)
    db.commit()

    return None
