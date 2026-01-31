"""
Unit tests for embeddings generation service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from app.services.embeddings import generate_embedding, generate_embeddings_batch


class TestGenerateEmbedding:
    """Test cases for generate_embedding function"""

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embedding_success(self, mock_client):
        """Test successful embedding generation"""
        # Setup mock
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [0.1]  # 1536 dimensions
        mock_response.data = [mock_data]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_embedding("Test text for embedding")

        # Assert
        assert len(result) == 1536
        assert isinstance(result, list)
        assert all(isinstance(x, float) for x in result)
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input="Test text for embedding"
        )

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embedding_with_custom_model(self, mock_client):
        """Test embedding generation with custom model"""
        # Setup mock
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1] * 1536
        mock_response.data = [mock_data]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_embedding("Test text", model="text-embedding-3-large")

        # Assert
        assert len(result) == 1536
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-large",
            input="Test text"
        )

    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self):
        """Test embedding generation with empty text"""
        # Execute & Assert
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await generate_embedding("")

    @pytest.mark.asyncio
    async def test_generate_embedding_whitespace_only(self):
        """Test embedding generation with whitespace-only text"""
        # Execute & Assert
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await generate_embedding("   \n\t  ")

    @pytest.mark.asyncio
    async def test_generate_embedding_none_text(self):
        """Test embedding generation with None text"""
        # Execute & Assert
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await generate_embedding(None)

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embedding_api_failure(self, mock_client):
        """Test handling of API failures"""
        # Setup mock to raise exception
        mock_client.embeddings.create = AsyncMock(
            side_effect=Exception("API connection failed")
        )

        # Execute & Assert
        with pytest.raises(Exception, match="Failed to generate embedding"):
            await generate_embedding("Test text")

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embedding_long_text(self, mock_client):
        """Test embedding generation with long text"""
        # Setup mock
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.5] * 1536
        mock_response.data = [mock_data]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Create a long text (simulate an academic paper abstract)
        long_text = "This is a long text. " * 100

        # Execute
        result = await generate_embedding(long_text)

        # Assert
        assert len(result) == 1536
        mock_client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embedding_special_characters(self, mock_client):
        """Test embedding generation with special characters"""
        # Setup mock
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.3] * 1536
        mock_response.data = [mock_data]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Execute with special characters and unicode
        text = "Résumé: Machine learning α, β, γ — neural networks!"
        result = await generate_embedding(text)

        # Assert
        assert len(result) == 1536
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input=text
        )


class TestGenerateEmbeddingsBatch:
    """Test cases for generate_embeddings_batch function"""

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embeddings_batch_success(self, mock_client):
        """Test successful batch embedding generation"""
        # Setup mock
        mock_response = Mock()
        mock_data_1 = Mock()
        mock_data_1.embedding = [0.1] * 1536
        mock_data_2 = Mock()
        mock_data_2.embedding = [0.2] * 1536
        mock_data_3 = Mock()
        mock_data_3.embedding = [0.3] * 1536
        mock_response.data = [mock_data_1, mock_data_2, mock_data_3]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Execute
        texts = ["First text", "Second text", "Third text"]
        result = await generate_embeddings_batch(texts)

        # Assert
        assert len(result) == 3
        assert all(len(emb) == 1536 for emb in result)
        assert result[0] == [0.1] * 1536
        assert result[1] == [0.2] * 1536
        assert result[2] == [0.3] * 1536
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input=texts
        )

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embeddings_batch_single_text(self, mock_client):
        """Test batch generation with a single text"""
        # Setup mock
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.5] * 1536
        mock_response.data = [mock_data]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_embeddings_batch(["Single text"])

        # Assert
        assert len(result) == 1
        assert len(result[0]) == 1536

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_empty_list(self):
        """Test batch generation with empty list"""
        # Execute & Assert
        with pytest.raises(ValueError, match="Texts list cannot be empty"):
            await generate_embeddings_batch([])

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_contains_empty_text(self):
        """Test batch generation with empty text in list"""
        # Execute & Assert
        with pytest.raises(ValueError, match="Texts at indices .* are empty"):
            await generate_embeddings_batch(["Valid text", "", "Another valid text"])

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_contains_whitespace_only(self):
        """Test batch generation with whitespace-only text"""
        # Execute & Assert
        with pytest.raises(ValueError, match="Texts at indices .* are empty"):
            await generate_embeddings_batch(["Valid text", "   \n\t  "])

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embeddings_batch_with_custom_model(self, mock_client):
        """Test batch generation with custom model"""
        # Setup mock
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.7] * 1536
        mock_response.data = [mock_data]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Execute
        result = await generate_embeddings_batch(
            ["Test text"],
            model="text-embedding-3-large"
        )

        # Assert
        assert len(result) == 1
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-large",
            input=["Test text"]
        )

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embeddings_batch_large_batch(self, mock_client):
        """Test batch generation with large number of texts using batching"""
        # Setup mock - simulate two API calls for batch_size=100
        texts = [f"Text {i}" for i in range(150)]

        # First batch (100 texts)
        first_batch_data = [Mock(embedding=[0.1] * 1536) for _ in range(100)]
        first_response = Mock()
        first_response.data = first_batch_data

        # Second batch (50 texts)
        second_batch_data = [Mock(embedding=[0.2] * 1536) for _ in range(50)]
        second_response = Mock()
        second_response.data = second_batch_data

        mock_client.embeddings.create = AsyncMock(
            side_effect=[first_response, second_response]
        )

        # Execute
        result = await generate_embeddings_batch(texts, batch_size=100)

        # Assert
        assert len(result) == 150
        assert all(len(emb) == 1536 for emb in result)
        # First 100 should have 0.1
        assert all(emb == [0.1] * 1536 for emb in result[:100])
        # Last 50 should have 0.2
        assert all(emb == [0.2] * 1536 for emb in result[100:])
        # Should be called twice (2 batches)
        assert mock_client.embeddings.create.call_count == 2

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embeddings_batch_custom_batch_size(self, mock_client):
        """Test batch generation with custom batch size"""
        # Setup mock
        texts = [f"Text {i}" for i in range(10)]

        # Create 3 batches of size 4, 4, 2
        batch_responses = []
        for i in range(3):
            batch_size = 4 if i < 2 else 2
            batch_data = [Mock(embedding=[float(i)] * 1536) for _ in range(batch_size)]
            response = Mock()
            response.data = batch_data
            batch_responses.append(response)

        mock_client.embeddings.create = AsyncMock(side_effect=batch_responses)

        # Execute with batch_size=4
        result = await generate_embeddings_batch(texts, batch_size=4)

        # Assert
        assert len(result) == 10
        assert mock_client.embeddings.create.call_count == 3

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embeddings_batch_api_failure(self, mock_client):
        """Test handling of API failures in batch generation"""
        # Setup mock to raise exception
        mock_client.embeddings.create = AsyncMock(
            side_effect=Exception("API rate limit exceeded")
        )

        # Execute & Assert
        with pytest.raises(Exception, match="Failed to generate batch embeddings"):
            await generate_embeddings_batch(["Text 1", "Text 2"])

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embeddings_batch_preserves_order(self, mock_client):
        """Test that batch generation preserves the order of texts"""
        # Setup mock with distinct embeddings
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[float(i)] * 1536) for i in range(5)
        ]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Execute
        texts = [f"Text {i}" for i in range(5)]
        result = await generate_embeddings_batch(texts)

        # Assert - embeddings should be in same order
        assert len(result) == 5
        for i in range(5):
            assert result[i] == [float(i)] * 1536

    @pytest.mark.asyncio
    @patch('app.services.embeddings.client')
    async def test_generate_embeddings_batch_with_special_characters(self, mock_client):
        """Test batch generation with special characters"""
        # Setup mock
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 1536),
            Mock(embedding=[0.2] * 1536)
        ]

        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Execute with special characters
        texts = [
            "Résumé: α, β, γ",
            "Machine learning — neural networks!"
        ]
        result = await generate_embeddings_batch(texts)

        # Assert
        assert len(result) == 2
        assert all(len(emb) == 1536 for emb in result)
