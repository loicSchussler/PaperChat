"""
Unit tests for RAG service
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.rag import generate_rag_answer, calculate_cost, _build_context, _deduplicate_sources


class TestGenerateRagAnswer:
    """Test cases for generate_rag_answer function"""

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_success(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test successful RAG answer generation"""
        # Setup mocks
        mock_db = Mock()
        mock_generate_embedding.return_value = [0.1] * 1536

        mock_search_results = [
            {
                "chunk_id": 1,
                "content": "Machine learning is a subset of AI.",
                "section_name": "Introduction",
                "paper_id": 1,
                "paper_title": "AI Paper",
                "authors": ["John Doe"],
                "year": 2024,
                "similarity_score": 0.95
            },
            {
                "chunk_id": 2,
                "content": "Neural networks are used in deep learning.",
                "section_name": "Methods",
                "paper_id": 1,
                "paper_title": "AI Paper",
                "authors": ["John Doe"],
                "year": 2024,
                "similarity_score": 0.87
            }
        ]
        mock_vector_search.return_value = mock_search_results

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Machine learning is indeed a subset of artificial intelligence."))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50)
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_rag_answer(
            db=mock_db,
            question="What is machine learning?",
            max_sources=5
        )

        # Assert
        assert "answer" in result
        assert result["answer"] == "Machine learning is indeed a subset of artificial intelligence."
        assert "sources" in result
        # Sources are deduplicated - 2 chunks from same paper become 1 source
        assert len(result["sources"]) == 1
        assert result["sources"][0]["paper_title"] == "AI Paper"
        assert result["sources"][0]["relevance_score"] == 0.95  # Max relevance score
        # Check that both chunks' content is combined
        assert "Machine learning is a subset of AI." in result["sources"][0]["content"]
        assert "Neural networks are used in deep learning." in result["sources"][0]["content"]
        assert "[...]" in result["sources"][0]["content"]  # Content separator
        # Check sections are combined
        assert "Introduction" in result["sources"][0]["section_name"]
        assert "Methods" in result["sources"][0]["section_name"]
        assert "cost_usd" in result
        assert "response_time_ms" in result
        assert "prompt_tokens" in result
        assert "completion_tokens" in result
        assert result["prompt_tokens"] == 100
        assert result["completion_tokens"] == 50

        # Verify services were called correctly
        mock_generate_embedding.assert_called_once_with("What is machine learning?")
        mock_vector_search.assert_called_once_with(
            db=mock_db,
            query_embedding=[0.1] * 1536,
            top_k=5,
            paper_ids=None
        )
        mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_with_paper_ids(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test RAG answer generation with paper IDs filter"""
        # Setup mocks
        mock_db = Mock()
        mock_generate_embedding.return_value = [0.1] * 1536
        mock_vector_search.return_value = []

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="No relevant information found."))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=10)
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Execute with paper_ids
        result = await generate_rag_answer(
            db=mock_db,
            question="Test question",
            max_sources=3,
            paper_ids=[1, 2, 3]
        )

        # Assert
        mock_vector_search.assert_called_once_with(
            db=mock_db,
            query_embedding=[0.1] * 1536,
            top_k=3,
            paper_ids=[1, 2, 3]
        )
        assert result["answer"] == "No relevant information found."

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_no_results(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test RAG answer generation with no search results"""
        # Setup mocks
        mock_db = Mock()
        mock_generate_embedding.return_value = [0.1] * 1536
        mock_vector_search.return_value = []

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="I don't have information to answer this."))]
        mock_response.usage = Mock(prompt_tokens=80, completion_tokens=20)
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_rag_answer(
            db=mock_db,
            question="Completely unrelated question",
            max_sources=5
        )

        # Assert
        assert result["sources"] == []
        assert "answer" in result

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_embedding_failure(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test handling of embedding generation failure"""
        # Setup mock to raise exception
        mock_db = Mock()
        mock_generate_embedding.side_effect = Exception("Embedding API failed")

        # Execute & Assert
        with pytest.raises(Exception, match="Embedding API failed"):
            await generate_rag_answer(
                db=mock_db,
                question="Test question",
                max_sources=5
            )

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_llm_failure(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test handling of LLM API failure"""
        # Setup mocks
        mock_db = Mock()
        mock_generate_embedding.return_value = [0.1] * 1536
        mock_vector_search.return_value = []

        # Mock LLM to raise exception
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("LLM API failed")
        )

        # Execute & Assert
        with pytest.raises(Exception, match="LLM API failed"):
            await generate_rag_answer(
                db=mock_db,
                question="Test question",
                max_sources=5
            )

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_response_time_measured(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test that response time is measured correctly"""
        # Setup mocks
        mock_db = Mock()
        mock_generate_embedding.return_value = [0.1] * 1536
        mock_vector_search.return_value = []

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Answer"))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=10)
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_rag_answer(
            db=mock_db,
            question="Test",
            max_sources=5
        )

        # Assert - response_time_ms should be a non-negative integer
        assert isinstance(result["response_time_ms"], int)
        assert result["response_time_ms"] >= 0

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_cost_calculation(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test that cost is calculated correctly"""
        # Setup mocks
        mock_db = Mock()
        mock_generate_embedding.return_value = [0.1] * 1536
        mock_vector_search.return_value = []

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Answer"))]
        mock_response.usage = Mock(prompt_tokens=1000, completion_tokens=500)
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_rag_answer(
            db=mock_db,
            question="Test",
            max_sources=5
        )

        # Assert - cost should match calculate_cost(1000, 500)
        expected_cost = calculate_cost(1000, 500)
        assert result["cost_usd"] == expected_cost
        assert result["cost_usd"] > 0

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_context_building(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test that context is built correctly from search results"""
        # Setup mocks
        mock_db = Mock()
        mock_generate_embedding.return_value = [0.1] * 1536

        mock_search_results = [
            {
                "chunk_id": 1,
                "content": "Content 1",
                "section_name": "Introduction",
                "paper_id": 1,
                "paper_title": "Paper 1",
                "authors": ["Author 1"],
                "year": 2024,
                "similarity_score": 0.9
            }
        ]
        mock_vector_search.return_value = mock_search_results

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Answer"))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50)

        # Capture the messages sent to LLM
        captured_messages = None

        async def capture_create_call(**kwargs):
            nonlocal captured_messages
            captured_messages = kwargs.get("messages")
            return mock_response

        mock_client.chat.completions.create = capture_create_call

        # Execute
        await generate_rag_answer(
            db=mock_db,
            question="Test question",
            max_sources=5
        )

        # Assert - check that context was included in messages
        assert captured_messages is not None
        user_message = captured_messages[1]["content"]
        assert "Paper 1" in user_message
        assert "Content 1" in user_message
        assert "2024" in user_message

    @pytest.mark.asyncio
    @patch('app.services.rag.generate_embedding')
    @patch('app.services.rag.vector_search')
    @patch('app.services.rag.client')
    async def test_generate_rag_answer_sources_format(
        self, mock_client, mock_vector_search, mock_generate_embedding
    ):
        """Test that sources are formatted correctly"""
        # Setup mocks
        mock_db = Mock()
        mock_generate_embedding.return_value = [0.1] * 1536

        mock_search_results = [
            {
                "chunk_id": 1,
                "content": "Test content",
                "section_name": "Methods",
                "paper_id": 1,
                "paper_title": "Test Paper",
                "authors": ["Test Author"],
                "year": 2023,
                "similarity_score": 0.88
            }
        ]
        mock_vector_search.return_value = mock_search_results

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Answer"))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50)
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_rag_answer(
            db=mock_db,
            question="Test",
            max_sources=5
        )

        # Assert - check source structure
        assert len(result["sources"]) == 1
        source = result["sources"][0]
        assert source["paper_title"] == "Test Paper"
        assert source["paper_year"] == 2023
        assert source["section_name"] == "Methods"
        assert source["content"] == "Test content"
        assert source["relevance_score"] == 0.88


class TestCalculateCost:
    """Test cases for calculate_cost function"""

    def test_calculate_cost_basic(self):
        """Test basic cost calculation"""
        cost = calculate_cost(1000, 500)
        # (1000/1000 * 0.00015) + (500/1000 * 0.0006) = 0.00015 + 0.0003 = 0.00045
        assert cost == pytest.approx(0.00045)

    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens"""
        cost = calculate_cost(0, 0)
        assert cost == 0.0

    def test_calculate_cost_only_input(self):
        """Test cost calculation with only input tokens"""
        cost = calculate_cost(2000, 0)
        # 2000/1000 * 0.00015 = 0.0003
        assert cost == pytest.approx(0.0003)

    def test_calculate_cost_only_output(self):
        """Test cost calculation with only output tokens"""
        cost = calculate_cost(0, 1000)
        # 1000/1000 * 0.0006 = 0.0006
        assert cost == pytest.approx(0.0006)

    def test_calculate_cost_large_numbers(self):
        """Test cost calculation with large token counts"""
        cost = calculate_cost(100000, 50000)
        # (100000/1000 * 0.00015) + (50000/1000 * 0.0006) = 0.015 + 0.03 = 0.045
        assert cost == pytest.approx(0.045)

    def test_calculate_cost_precision(self):
        """Test that cost is rounded to 6 decimal places"""
        cost = calculate_cost(1, 1)
        # Should have at most 6 decimal places
        assert len(str(cost).split('.')[-1]) <= 6


class TestBuildContext:
    """Test cases for _build_context helper function"""

    def test_build_context_single_result(self):
        """Test context building with single result"""
        results = [
            {
                "content": "This is test content.",
                "paper_title": "Test Paper",
                "year": 2024,
                "section_name": "Introduction"
            }
        ]

        context = _build_context(results)

        assert "[Source 1]" in context
        assert "Test Paper" in context
        assert "(2024)" in context
        assert "Introduction" in context
        assert "This is test content." in context

    def test_build_context_multiple_results(self):
        """Test context building with multiple results"""
        results = [
            {
                "content": "First content.",
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Intro"
            },
            {
                "content": "Second content.",
                "paper_title": "Paper 2",
                "year": 2023,
                "section_name": "Methods"
            }
        ]

        context = _build_context(results)

        assert "[Source 1]" in context
        assert "[Source 2]" in context
        assert "Paper 1" in context
        assert "Paper 2" in context
        assert "First content." in context
        assert "Second content." in context

    def test_build_context_empty_results(self):
        """Test context building with empty results"""
        context = _build_context([])
        assert context == "No relevant information found in the indexed papers."

    def test_build_context_no_year(self):
        """Test context building when year is None"""
        results = [
            {
                "content": "Content without year.",
                "paper_title": "Undated Paper",
                "year": None,
                "section_name": "Section"
            }
        ]

        context = _build_context(results)

        assert "Undated Paper" in context
        assert "Content without year." in context
        # Year should not appear in parentheses
        assert "(None)" not in context

    def test_build_context_no_section(self):
        """Test context building when section_name is None"""
        results = [
            {
                "content": "Content without section.",
                "paper_title": "Test Paper",
                "year": 2024,
                "section_name": None
            }
        ]

        context = _build_context(results)

        assert "Test Paper (2024)" in context
        assert "Content without section." in context
        # Should not have a section dash
        assert " - None" not in context

    def test_build_context_formatting(self):
        """Test that context is properly formatted with newlines"""
        results = [
            {
                "content": "Content 1",
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Intro"
            },
            {
                "content": "Content 2",
                "paper_title": "Paper 2",
                "year": 2023,
                "section_name": "Methods"
            }
        ]

        context = _build_context(results)

        # Should have proper separation between sources
        lines = context.split('\n')
        assert len(lines) > 2  # Should have multiple lines


class TestDeduplicateSources:
    """Test cases for _deduplicate_sources helper function"""

    def test_deduplicate_sources_no_duplicates(self):
        """Test deduplication with no duplicate papers"""
        results = [
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Introduction",
                "content": "Content 1",
                "similarity_score": 0.9
            },
            {
                "paper_id": 2,
                "paper_title": "Paper 2",
                "year": 2023,
                "section_name": "Methods",
                "content": "Content 2",
                "similarity_score": 0.8
            }
        ]

        deduplicated = _deduplicate_sources(results)

        assert len(deduplicated) == 2
        assert deduplicated[0]["paper_title"] == "Paper 1"
        assert deduplicated[0]["relevance_score"] == 0.9
        assert deduplicated[1]["paper_title"] == "Paper 2"
        assert deduplicated[1]["relevance_score"] == 0.8

    def test_deduplicate_sources_with_duplicates(self):
        """Test deduplication merges chunks from same paper"""
        results = [
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Introduction",
                "content": "First chunk",
                "similarity_score": 0.9
            },
            {
                "paper_id": 2,
                "paper_title": "Paper 2",
                "year": 2023,
                "section_name": "Methods",
                "content": "Middle chunk",
                "similarity_score": 0.85
            },
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Results",
                "content": "Second chunk",
                "similarity_score": 0.8
            }
        ]

        deduplicated = _deduplicate_sources(results)

        # Should have only 2 unique papers
        assert len(deduplicated) == 2

        # Paper 1 should be first (higher max relevance)
        assert deduplicated[0]["paper_title"] == "Paper 1"
        assert deduplicated[0]["relevance_score"] == 0.9  # Highest score from Paper 1
        assert "First chunk" in deduplicated[0]["content"]
        assert "Second chunk" in deduplicated[0]["content"]
        assert "[...]" in deduplicated[0]["content"]  # Separator
        assert "Introduction, Results" == deduplicated[0]["section_name"] or "Results, Introduction" == deduplicated[0]["section_name"]

        # Paper 2 should be second
        assert deduplicated[1]["paper_title"] == "Paper 2"
        assert deduplicated[1]["relevance_score"] == 0.85

    def test_deduplicate_sources_keeps_max_relevance(self):
        """Test that deduplication keeps the maximum relevance score"""
        results = [
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Introduction",
                "content": "Chunk with low score",
                "similarity_score": 0.7
            },
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Methods",
                "content": "Chunk with high score",
                "similarity_score": 0.95
            },
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Results",
                "content": "Chunk with medium score",
                "similarity_score": 0.8
            }
        ]

        deduplicated = _deduplicate_sources(results)

        assert len(deduplicated) == 1
        assert deduplicated[0]["relevance_score"] == 0.95  # Maximum score

    def test_deduplicate_sources_combines_sections(self):
        """Test that sections from same paper are combined"""
        results = [
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Introduction",
                "content": "Content A",
                "similarity_score": 0.9
            },
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Methods",
                "content": "Content B",
                "similarity_score": 0.85
            },
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": "Results",
                "content": "Content C",
                "similarity_score": 0.8
            }
        ]

        deduplicated = _deduplicate_sources(results)

        assert len(deduplicated) == 1
        sections = deduplicated[0]["section_name"].split(", ")
        assert len(sections) == 3
        assert "Introduction" in sections
        assert "Methods" in sections
        assert "Results" in sections

    def test_deduplicate_sources_with_none_sections(self):
        """Test deduplication with None section names"""
        results = [
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": None,
                "content": "Content 1",
                "similarity_score": 0.9
            },
            {
                "paper_id": 1,
                "paper_title": "Paper 1",
                "year": 2024,
                "section_name": None,
                "content": "Content 2",
                "similarity_score": 0.8
            }
        ]

        deduplicated = _deduplicate_sources(results)

        assert len(deduplicated) == 1
        assert deduplicated[0]["section_name"] is None

    def test_deduplicate_sources_empty_list(self):
        """Test deduplication with empty list"""
        deduplicated = _deduplicate_sources([])
        assert deduplicated == []

    def test_deduplicate_sources_sorted_by_relevance(self):
        """Test that results are sorted by relevance score"""
        results = [
            {
                "paper_id": 1,
                "paper_title": "Low Score Paper",
                "year": 2024,
                "section_name": "Intro",
                "content": "Content",
                "similarity_score": 0.6
            },
            {
                "paper_id": 2,
                "paper_title": "High Score Paper",
                "year": 2023,
                "section_name": "Methods",
                "content": "Content",
                "similarity_score": 0.95
            },
            {
                "paper_id": 3,
                "paper_title": "Medium Score Paper",
                "year": 2022,
                "section_name": "Results",
                "content": "Content",
                "similarity_score": 0.8
            }
        ]

        deduplicated = _deduplicate_sources(results)

        assert len(deduplicated) == 3
        assert deduplicated[0]["relevance_score"] == 0.95
        assert deduplicated[1]["relevance_score"] == 0.8
        assert deduplicated[2]["relevance_score"] == 0.6

    def test_deduplicate_sources_content_separator(self):
        """Test that content chunks are separated correctly"""
        results = [
            {
                "paper_id": 1,
                "paper_title": "Paper",
                "year": 2024,
                "section_name": "Intro",
                "content": "First part",
                "similarity_score": 0.9
            },
            {
                "paper_id": 1,
                "paper_title": "Paper",
                "year": 2024,
                "section_name": "Methods",
                "content": "Second part",
                "similarity_score": 0.8
            }
        ]

        deduplicated = _deduplicate_sources(results)

        assert len(deduplicated) == 1
        content = deduplicated[0]["content"]
        assert "First part" in content
        assert "Second part" in content
        assert "\n\n[...]\n\n" in content

    def test_deduplicate_sources_preserves_paper_metadata(self):
        """Test that paper metadata is preserved correctly"""
        results = [
            {
                "paper_id": 5,
                "paper_title": "Important Paper",
                "year": 2025,
                "section_name": "Introduction",
                "content": "Content",
                "similarity_score": 0.9
            },
            {
                "paper_id": 5,
                "paper_title": "Important Paper",
                "year": 2025,
                "section_name": "Conclusion",
                "content": "More content",
                "similarity_score": 0.85
            }
        ]

        deduplicated = _deduplicate_sources(results)

        assert len(deduplicated) == 1
        assert deduplicated[0]["paper_title"] == "Important Paper"
        assert deduplicated[0]["paper_year"] == 2025
