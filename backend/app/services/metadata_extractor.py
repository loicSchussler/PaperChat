"""
Service d'extraction de métadonnées via LLM
TODO: Implémenter avec Mammouth AI (API compatible OpenAI)
"""
from typing import Dict, Any
from app.config import settings


def extract_metadata_from_text(text: str) -> Dict[str, Any]:
    """
    Extrait les métadonnées d'un article scientifique via GPT-4o-mini (Mammouth AI)

    Args:
        text: Début du texte de l'article (premiers 2000 caractères)

    Returns:
        Dict avec title, authors, year, abstract, keywords
    """
    # TODO: Implémenter avec Mammouth AI API
    # Exemple d'utilisation:
    # from openai import OpenAI
    # client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)
    # response = client.chat.completions.create(...)
    raise NotImplementedError("À implémenter avec Mammouth AI")
