"""
Service de recherche vectorielle avec pgvector
TODO: Implémenter la recherche de similarité
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
    Recherche les chunks les plus similaires à un embedding donné

    Args:
        db: Session de base de données
        query_embedding: Embedding de la question
        top_k: Nombre de résultats à retourner
        paper_ids: Liste optionnelle d'IDs de papers pour filtrer

    Returns:
        Liste de chunks avec leur score de similarité
    """
    # TODO: Implémenter avec pgvector <=> operator pour similarité cosinus
    raise NotImplementedError("À implémenter avec pgvector")
