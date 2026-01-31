"""
Smart text chunking service
"""
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_text(text: str, sections: Dict[str, int] = None) -> List[Dict[str, Any]]:
    """
    Splits text into chunks with section context

    Args:
        text: Complete text to split
        sections: Dict {section_name: start_offset}

    Returns:
        List of dicts with content, section_name, chunk_index
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    # Split text into chunks
    chunks = text_splitter.split_text(text)

    # Build result with section context
    result = []
    for chunk_index, chunk_content in enumerate(chunks):
        # Find which section this chunk belongs to
        section_name = None
        if sections:
            # Find chunk position in original text
            chunk_start = text.find(chunk_content)
            if chunk_start != -1:
                # Find the section with the largest start_offset <= chunk_start
                for sec_name, sec_offset in sorted(sections.items(), key=lambda x: x[1], reverse=True):
                    if sec_offset <= chunk_start:
                        section_name = sec_name
                        break

        result.append({
            "content": chunk_content,
            "section_name": section_name,
            "chunk_index": chunk_index
        })

    return result
