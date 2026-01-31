"""
Unit tests for vector search service
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.vector_store import vector_search


class TestVectorSearch:
    """Test cases for vector_search function"""

    @pytest.mark.asyncio
    async def test_vector_search_success(self):
        """Test successful vector search with results"""
        # Setup mock database session
        mock_db = Mock()

        # Create mock query results
        mock_row_1 = Mock()
        mock_row_1.id = 1
        mock_row_1.content = "This is a test chunk about machine learning"
        mock_row_1.section_name = "Introduction"
        mock_row_1.paper_id = 10
        mock_row_1.title = "Machine Learning Paper"
        mock_row_1.authors = ["John Doe", "Jane Smith"]
        mock_row_1.year = 2024
        mock_row_1.distance = 0.15

        mock_row_2 = Mock()
        mock_row_2.id = 2
        mock_row_2.content = "Another chunk about neural networks"
        mock_row_2.section_name = "Methods"
        mock_row_2.paper_id = 11
        mock_row_2.title = "Neural Networks Study"
        mock_row_2.authors = ["Alice Brown"]
        mock_row_2.year = 2023
        mock_row_2.distance = 0.25

        # Mock the execute result
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row_1, mock_row_2]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=5
        )

        # Assert
        assert len(result) == 2
        assert result[0]["chunk_id"] == 1
        assert result[0]["content"] == "This is a test chunk about machine learning"
        assert result[0]["section_name"] == "Introduction"
        assert result[0]["paper_id"] == 10
        assert result[0]["paper_title"] == "Machine Learning Paper"
        assert result[0]["authors"] == ["John Doe", "Jane Smith"]
        assert result[0]["year"] == 2024
        assert result[0]["similarity_score"] == 0.85  # 1 - 0.15

        assert result[1]["chunk_id"] == 2
        assert result[1]["similarity_score"] == 0.75  # 1 - 0.25

        # Verify database execute was called
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_search_with_paper_ids_filter(self):
        """Test vector search with paper IDs filter"""
        # Setup mock
        mock_db = Mock()
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result

        # Execute with paper_ids filter
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=3,
            paper_ids=[1, 2, 3]
        )

        # Assert
        assert isinstance(result, list)
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_search_empty_results(self):
        """Test vector search with no results"""
        # Setup mock with empty results
        mock_db = Mock()
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.5] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=5
        )

        # Assert
        assert result == []
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_search_custom_top_k(self):
        """Test vector search with custom top_k parameter"""
        # Setup mock
        mock_db = Mock()
        mock_rows = []
        for i in range(10):
            mock_row = Mock()
            mock_row.id = i
            mock_row.content = f"Chunk {i}"
            mock_row.section_name = "Section"
            mock_row.paper_id = i
            mock_row.title = f"Paper {i}"
            mock_row.authors = [f"Author {i}"]
            mock_row.year = 2024
            mock_row.distance = 0.1 * i
            mock_rows.append(mock_row)

        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        # Execute with top_k=10
        query_embedding = [0.2] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=10
        )

        # Assert
        assert len(result) == 10
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_search_similarity_score_calculation(self):
        """Test that similarity scores are correctly calculated from distances"""
        # Setup mock
        mock_db = Mock()

        mock_row = Mock()
        mock_row.id = 1
        mock_row.content = "Test content"
        mock_row.section_name = "Test"
        mock_row.paper_id = 1
        mock_row.title = "Test Paper"
        mock_row.authors = ["Test Author"]
        mock_row.year = 2024
        mock_row.distance = 0.3

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=1
        )

        # Assert - similarity_score should be 1 - distance
        assert result[0]["similarity_score"] == 0.7  # 1 - 0.3

    @pytest.mark.asyncio
    async def test_vector_search_with_none_section_name(self):
        """Test vector search when section_name is None"""
        # Setup mock
        mock_db = Mock()

        mock_row = Mock()
        mock_row.id = 1
        mock_row.content = "Content without section"
        mock_row.section_name = None
        mock_row.paper_id = 5
        mock_row.title = "Paper Title"
        mock_row.authors = ["Author Name"]
        mock_row.year = 2023
        mock_row.distance = 0.2

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.3] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=1
        )

        # Assert
        assert result[0]["section_name"] is None
        assert result[0]["content"] == "Content without section"

    @pytest.mark.asyncio
    async def test_vector_search_with_empty_authors(self):
        """Test vector search with papers that have no authors"""
        # Setup mock
        mock_db = Mock()

        mock_row = Mock()
        mock_row.id = 1
        mock_row.content = "Test content"
        mock_row.section_name = "Abstract"
        mock_row.paper_id = 1
        mock_row.title = "Anonymous Paper"
        mock_row.authors = []
        mock_row.year = 2024
        mock_row.distance = 0.1

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.4] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=1
        )

        # Assert
        assert result[0]["authors"] == []

    @pytest.mark.asyncio
    async def test_vector_search_with_multiple_paper_ids(self):
        """Test vector search filtering by multiple paper IDs"""
        # Setup mock
        mock_db = Mock()

        # Create results that would come from papers 1, 2, 3
        mock_rows = []
        for paper_id in [1, 2, 3]:
            mock_row = Mock()
            mock_row.id = paper_id
            mock_row.content = f"Content from paper {paper_id}"
            mock_row.section_name = "Section"
            mock_row.paper_id = paper_id
            mock_row.title = f"Paper {paper_id}"
            mock_row.authors = [f"Author {paper_id}"]
            mock_row.year = 2024
            mock_row.distance = 0.1 * paper_id
            mock_rows.append(mock_row)

        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        # Execute with specific paper_ids
        query_embedding = [0.5] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=10,
            paper_ids=[1, 2, 3]
        )

        # Assert
        assert len(result) == 3
        assert all(r["paper_id"] in [1, 2, 3] for r in result)

    @pytest.mark.asyncio
    async def test_vector_search_result_structure(self):
        """Test that result structure contains all required fields"""
        # Setup mock
        mock_db = Mock()

        mock_row = Mock()
        mock_row.id = 1
        mock_row.content = "Test"
        mock_row.section_name = "Intro"
        mock_row.paper_id = 1
        mock_row.title = "Title"
        mock_row.authors = ["Author"]
        mock_row.year = 2024
        mock_row.distance = 0.1

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=1
        )

        # Assert - check all required fields are present
        required_fields = [
            "chunk_id", "content", "section_name", "paper_id",
            "paper_title", "authors", "year", "similarity_score"
        ]
        assert len(result) == 1
        for field in required_fields:
            assert field in result[0], f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_vector_search_with_high_similarity(self):
        """Test vector search with very high similarity (low distance)"""
        # Setup mock
        mock_db = Mock()

        mock_row = Mock()
        mock_row.id = 1
        mock_row.content = "Nearly identical content"
        mock_row.section_name = "Results"
        mock_row.paper_id = 1
        mock_row.title = "Similar Paper"
        mock_row.authors = ["Author"]
        mock_row.year = 2024
        mock_row.distance = 0.01  # Very low distance = high similarity

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=1
        )

        # Assert - similarity should be very high
        assert result[0]["similarity_score"] == 0.99  # 1 - 0.01

    @pytest.mark.asyncio
    async def test_vector_search_with_low_similarity(self):
        """Test vector search with low similarity (high distance)"""
        # Setup mock
        mock_db = Mock()

        mock_row = Mock()
        mock_row.id = 1
        mock_row.content = "Very different content"
        mock_row.section_name = "Discussion"
        mock_row.paper_id = 1
        mock_row.title = "Different Paper"
        mock_row.authors = ["Author"]
        mock_row.year = 2024
        mock_row.distance = 0.9  # High distance = low similarity

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=1
        )

        # Assert - similarity should be low
        assert result[0]["similarity_score"] == pytest.approx(0.1)  # 1 - 0.9

    @pytest.mark.asyncio
    async def test_vector_search_default_parameters(self):
        """Test vector search with default parameters"""
        # Setup mock
        mock_db = Mock()
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result

        # Execute with only required parameters
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding
        )

        # Assert
        assert isinstance(result, list)
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_search_with_special_characters_in_content(self):
        """Test vector search with special characters in chunk content"""
        # Setup mock
        mock_db = Mock()

        mock_row = Mock()
        mock_row.id = 1
        mock_row.content = "Content with special chars: α, β, γ, Σ — and unicode: é, ñ, 中文"
        mock_row.section_name = "Methodology"
        mock_row.paper_id = 1
        mock_row.title = "International Paper"
        mock_row.authors = ["José García", "François Dubois"]
        mock_row.year = 2024
        mock_row.distance = 0.2

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=1
        )

        # Assert - should handle special characters correctly
        assert result[0]["content"] == "Content with special chars: α, β, γ, Σ — and unicode: é, ñ, 中文"
        assert "José García" in result[0]["authors"]

    @pytest.mark.asyncio
    async def test_vector_search_with_none_year(self):
        """Test vector search when year is None"""
        # Setup mock
        mock_db = Mock()

        mock_row = Mock()
        mock_row.id = 1
        mock_row.content = "Content from paper with unknown year"
        mock_row.section_name = "Introduction"
        mock_row.paper_id = 1
        mock_row.title = "Undated Paper"
        mock_row.authors = ["Author"]
        mock_row.year = None
        mock_row.distance = 0.15

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=1
        )

        # Assert
        assert result[0]["year"] is None
        assert result[0]["content"] == "Content from paper with unknown year"

    @pytest.mark.asyncio
    async def test_vector_search_ordering(self):
        """Test that results are ordered by similarity (distance ascending)"""
        # Setup mock with results in specific order
        mock_db = Mock()

        # Create rows with increasing distances
        mock_rows = []
        distances = [0.1, 0.2, 0.3, 0.4, 0.5]
        for i, dist in enumerate(distances):
            mock_row = Mock()
            mock_row.id = i
            mock_row.content = f"Content {i}"
            mock_row.section_name = "Section"
            mock_row.paper_id = i
            mock_row.title = f"Paper {i}"
            mock_row.authors = [f"Author {i}"]
            mock_row.year = 2024
            mock_row.distance = dist
            mock_rows.append(mock_row)

        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        # Execute
        query_embedding = [0.1] * 1536
        result = await vector_search(
            db=mock_db,
            query_embedding=query_embedding,
            top_k=5
        )

        # Assert - similarity scores should be in descending order
        similarities = [r["similarity_score"] for r in result]
        assert similarities == [0.9, 0.8, 0.7, 0.6, 0.5]
        assert similarities == sorted(similarities, reverse=True)
