"""
Vector search service with pgvector
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Chunk, Paper


async def vector_search(
    db: Session,
    query_embedding: List[float],
    top_k: int = 5,
    paper_ids: List[int] = None
) -> List[dict]:
    """
    Searches for chunks most similar to a given embedding

    Args:
        db: Database session
        query_embedding: Question embedding
        top_k: Number of results to return
        paper_ids: Optional list of paper IDs to filter

    Returns:
        List of chunks with their similarity score
    """
    # Build the query with pgvector cosine similarity
    query = (
        select(
            Chunk.id,
            Chunk.content,
            Chunk.section_name,
            Chunk.paper_id,
            Paper.title,
            Paper.authors,
            Paper.year,
            Chunk.embedding.cosine_distance(query_embedding).label("distance")
        )
        .join(Paper, Chunk.paper_id == Paper.id)
        .filter(Chunk.embedding.isnot(None))
    )

    # Filter by paper IDs if provided
    if paper_ids:
        query = query.filter(Chunk.paper_id.in_(paper_ids))

    # Order by similarity (lower distance = more similar) and limit results
    query = query.order_by("distance").limit(top_k)

    # Execute the query
    results = db.execute(query).fetchall()

    # Format the results
    return [
        {
            "chunk_id": row.id,
            "content": row.content,
            "section_name": row.section_name,
            "paper_id": row.paper_id,
            "paper_title": row.title,
            "authors": row.authors,
            "year": row.year,
            "similarity_score": 1 - row.distance  # Convert distance to similarity score
        }
        for row in results
    ]
