"""
Vector search service with pgvector
TODO: Implement similarity search
"""
from typing import List
from sqlalchemy.orm import Session


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
    # TODO: Implement with pgvector <=> operator for cosine similarity
    raise NotImplementedError("To be implemented with pgvector")
