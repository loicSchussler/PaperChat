"""
Embeddings generation service using Mammouth AI (OpenAI-compatible API)
"""
from typing import List
from openai import AsyncOpenAI
from app.config import settings


# Initialize the AsyncOpenAI client with Mammouth AI configuration
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE
)


async def generate_embedding(text: str, model: str = None) -> List[float]:
    """
    Generates an embedding for a given text

    Args:
        text: Text to vectorize
        model: Embedding model to use (default: from settings.OPENAI_EMBEDDING_MODEL)

    Returns:
        Embedding vector (1536 dimensions for text-embedding-3-small)

    Raises:
        ValueError: If text is empty or None
        Exception: If API call fails
    """
    if model is None:
        model = settings.OPENAI_EMBEDDING_MODEL
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    try:
        response = await client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f"Failed to generate embedding: {str(e)}")


async def generate_embeddings_batch(
    texts: List[str],
    model: str = None,
    batch_size: int = 100
) -> List[List[float]]:
    """
    Generates embeddings for multiple texts in batch

    Args:
        texts: List of texts to vectorize
        model: Embedding model to use (default: from settings.OPENAI_EMBEDDING_MODEL)
        batch_size: Maximum number of texts to process in one API call (default: 100)

    Returns:
        List of embedding vectors in the same order as input texts

    Raises:
        ValueError: If texts list is empty or contains empty strings
        Exception: If API call fails
    """
    if model is None:
        model = settings.OPENAI_EMBEDDING_MODEL
    if not texts:
        raise ValueError("Texts list cannot be empty")

    # Filter out empty texts and raise error if any found
    empty_indices = [i for i, text in enumerate(texts) if not text or not text.strip()]
    if empty_indices:
        raise ValueError(f"Texts at indices {empty_indices} are empty")

    try:
        all_embeddings = []

        # Process in batches to optimize API calls and avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = await client.embeddings.create(
                model=model,
                input=batch
            )

            # Extract embeddings in the correct order
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings
    except Exception as e:
        raise Exception(f"Failed to generate batch embeddings: {str(e)}")
