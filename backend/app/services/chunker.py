"""
Service de découpage intelligent de texte
TODO: Implémenter avec LangChain RecursiveCharacterTextSplitter
"""
from typing import List, Dict


def chunk_text(text: str, sections: Dict[str, int] = None) -> List[Dict[str, any]]:
    """
    Découpe un texte en chunks avec contexte sectionnel

    Args:
        text: Texte complet à découper
        sections: Dict {nom_section: offset_debut}

    Returns:
        Liste de dicts avec content, section_name, chunk_index
    """
    # TODO: Implémenter avec LangChain RecursiveCharacterTextSplitter
    # chunk_size=1000, chunk_overlap=200
    raise NotImplementedError("À implémenter avec LangChain")
