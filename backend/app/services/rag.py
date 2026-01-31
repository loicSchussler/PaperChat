"""
RAG (Retrieval-Augmented Generation) service
"""
from typing import Dict, Any, List
import time
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from app.config import settings
from app.services.embeddings import generate_embedding
from app.services.vector_store import vector_search


# Initialize the AsyncOpenAI client with Mammouth AI configuration
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE
)


async def generate_rag_answer(
    db: Session,
    question: str,
    max_sources: int = 5,
    paper_ids: list = None
) -> Dict[str, Any]:
    """
    Complete RAG pipeline to answer a question

    Args:
        db: Database session
        question: User's question
        max_sources: Maximum number of sources to use
        paper_ids: Paper IDs to filter the search

    Returns:
        Dict with answer, sources, cost_usd, response_time_ms
    """
    start_time = time.time()

    # 1. Vectorize the question
    query_embedding = await generate_embedding(question)

    # 2. Vector search to find relevant chunks
    search_results = await vector_search(
        db=db,
        query_embedding=query_embedding,
        top_k=max_sources,
        paper_ids=paper_ids
    )

    # 3. Build the context from retrieved chunks
    context = _build_context(search_results)

    # 4. Call Mammouth AI for generation
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant specialized in analyzing scientific papers. "
                "Answer the user's question based ONLY on the provided context from the papers. "
                "If the context doesn't contain enough information to answer the question, "
                "say so clearly. Cite the papers when appropriate."
            )
        },
        {
            "role": "user",
            "content": f"Context from papers:\n\n{context}\n\nQuestion: {question}"
        }
    ]

    response = await client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )

    # Extract answer and token usage
    answer = response.choices[0].message.content
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens

    # 5. Calculate the cost
    cost_usd = calculate_cost(prompt_tokens, completion_tokens)

    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)

    # 6. Deduplicate and format sources for response
    deduplicated_sources = _deduplicate_sources(search_results)

    return {
        "answer": answer,
        "sources": deduplicated_sources,
        "cost_usd": cost_usd,
        "response_time_ms": response_time_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens
    }


def _build_context(search_results: List[Dict[str, Any]]) -> str:
    """
    Build a formatted context string from search results

    Args:
        search_results: List of chunks with metadata from vector search

    Returns:
        Formatted context string
    """
    if not search_results:
        return "No relevant information found in the indexed papers."

    context_parts = []
    for i, result in enumerate(search_results, 1):
        paper_info = f"{result['paper_title']}"
        if result['year']:
            paper_info += f" ({result['year']})"

        section_info = f" - {result['section_name']}" if result['section_name'] else ""

        context_parts.append(
            f"[Source {i}] {paper_info}{section_info}\n{result['content']}\n"
        )

    return "\n".join(context_parts)


def _deduplicate_sources(search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate sources by grouping chunks from the same paper

    Args:
        search_results: List of chunks with metadata from vector search

    Returns:
        List of deduplicated sources with combined content
    """
    if not search_results:
        return []

    # Group chunks by paper_id
    papers_dict = {}

    for result in search_results:
        paper_id = result["paper_id"]

        if paper_id not in papers_dict:
            # First occurrence of this paper
            papers_dict[paper_id] = {
                "paper_title": result["paper_title"],
                "paper_year": result["year"],
                "paper_id": paper_id,
                "sections": set(),
                "contents": [],
                "max_relevance": result["similarity_score"]
            }

        # Add this chunk's information
        if result["section_name"]:
            papers_dict[paper_id]["sections"].add(result["section_name"])

        papers_dict[paper_id]["contents"].append(result["content"])

        # Keep the highest relevance score
        if result["similarity_score"] > papers_dict[paper_id]["max_relevance"]:
            papers_dict[paper_id]["max_relevance"] = result["similarity_score"]

    # Format deduplicated sources
    deduplicated = []
    for paper_data in papers_dict.values():
        # Combine sections
        if paper_data["sections"]:
            section_name = ", ".join(sorted(paper_data["sections"]))
        else:
            section_name = None

        # Combine contents with separator
        combined_content = "\n\n[...]\n\n".join(paper_data["contents"])

        deduplicated.append({
            "paper_title": paper_data["paper_title"],
            "paper_year": paper_data["paper_year"],
            "section_name": section_name,
            "content": combined_content,
            "relevance_score": paper_data["max_relevance"]
        })

    # Sort by relevance score (descending)
    deduplicated.sort(key=lambda x: x["relevance_score"], reverse=True)

    return deduplicated


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calculates the cost of an LLM request via Mammouth AI

    Args:
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    # Mammouth AI pricing (OpenAI equivalents - January 2025)
    # Verify actual pricing at https://mammouth.ai
    PRICING = {
        "gpt-4o-mini": {
            "input": 0.00015,  # per 1K tokens
            "output": 0.0006   # per 1K tokens
        }
    }

    input_cost = (prompt_tokens / 1000) * PRICING["gpt-4o-mini"]["input"]
    output_cost = (completion_tokens / 1000) * PRICING["gpt-4o-mini"]["output"]

    return round(input_cost + output_cost, 6)
