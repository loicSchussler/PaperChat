"""
Service de génération d'embeddings
TODO: Implémenter avec Mammouth AI Embeddings (API compatible OpenAI)
"""
from typing import List
from app.config import settings


async def generate_embedding(text: str) -> List[float]:
    """
    Génère un embedding pour un texte donné

    Args:
        text: Texte à vectoriser

    Returns:
        Vecteur d'embedding (1536 dimensions pour text-embedding-3-small)
    """
    # TODO: Implémenter avec Mammouth AI text-embedding-3-small
    # Exemple d'utilisation:
    # from openai import OpenAI
    # client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)
    # response = client.embeddings.create(model="text-embedding-3-small", input=text)
    # return response.data[0].embedding
    raise NotImplementedError("À implémenter avec Mammouth AI Embeddings")


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Génère des embeddings pour plusieurs textes en batch

    Args:
        texts: Liste de textes à vectoriser

    Returns:
        Liste de vecteurs d'embeddings
    """
    # TODO: Implémenter en batch pour optimiser les coûts
    raise NotImplementedError("À implémenter avec Mammouth AI Embeddings")
