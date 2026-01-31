"""
Metadata extraction service via LLM
"""
from typing import Dict, Any
import json
import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


async def extract_metadata_from_text(text: str) -> Dict[str, Any]:
    """
    Extracts metadata from a scientific paper via GPT-4o-mini (Mammouth AI)

    Args:
        text: Beginning of the paper text (first 2000 characters)

    Returns:
        Dict with title, authors, year, abstract, keywords
    """
    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE
    )

    prompt = """You are extracting metadata from a scientific paper. The text below is extracted from a PDF and may contain formatting issues.

Extract the following information and return ONLY a valid JSON object:
{{
  "title": "The paper title (look for the largest/first heading)",
  "authors": ["List", "of", "author", "names"],
  "year": 2023 (publication year as integer, or null),
  "abstract": "The abstract or summary text",
  "keywords": ["keyword1", "keyword2"]
}}

Important:
- The title is usually at the beginning, often in caps or larger font
- Authors are typically listed right after the title
- Look for sections labeled "Abstract", "Summary", or similar
- Year might be near the title, authors, or in a citation
- If you can't find something, use null or []

Paper text (may contain formatting artifacts):
---
{text}
---

Return ONLY the JSON object, no other text:"""

    try:

        response = await client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a metadata extraction assistant for scientific papers. Always respond with valid JSON only."},
                {"role": "user", "content": prompt.format(text=text[:2000])}  # Limit to 2000 chars for API
            ],
            temperature=0.1,
            max_tokens=1000
        )

        # Parse the response
        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        metadata = json.loads(content)

        # Ensure all required fields are present
        result = {
            "title": metadata.get("title"),
            "authors": metadata.get("authors", []),
            "year": metadata.get("year"),
            "abstract": metadata.get("abstract"),
            "keywords": metadata.get("keywords", [])
        }

        return result

    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}", exc_info=True)
        # Return default structure in case of error
        return {
            "title": None,
            "authors": [],
            "year": None,
            "abstract": None,
            "keywords": [],
            "error": str(e)
        }
