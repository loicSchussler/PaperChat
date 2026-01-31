"""
Unit tests for metadata extraction service using Mammouth AI API
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.services.metadata_extractor import extract_metadata_from_text


class TestExtractMetadataFromText:
    """Test cases for extract_metadata_from_text function"""

    @pytest.mark.asyncio
    @patch('app.services.metadata_extractor.AsyncOpenAI')
    async def test_extract_metadata_success(self, mock_openai):
        """Test successful metadata extraction"""
        # Setup mock response
        mock_response = {
            "title": "Deep Learning for Computer Vision",
            "authors": ["John Doe", "Jane Smith"],
            "year": 2023,
            "abstract": "This paper presents a novel approach to computer vision using deep learning.",
            "keywords": ["deep learning", "computer vision", "neural networks"]
        }

        mock_message = Mock()
        mock_message.content = json.dumps(mock_response)

        mock_choice = Mock()
        mock_choice.message = mock_message

        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai.return_value = mock_client

        # Execute
        text = "Deep Learning for Computer Vision\nAuthors: John Doe, Jane Smith\nYear: 2023"
        result = await extract_metadata_from_text(text)

        # Assert
        assert result["title"] == "Deep Learning for Computer Vision"
        assert result["authors"] == ["John Doe", "Jane Smith"]
        assert result["year"] == 2023
        assert "deep learning" in result["abstract"]
        assert len(result["keywords"]) == 3
        assert "deep learning" in result["keywords"]

    @pytest.mark.asyncio
    @patch('app.services.metadata_extractor.AsyncOpenAI')
    async def test_extract_metadata_with_markdown_code_blocks(self, mock_openai):
        """Test extraction when API returns JSON wrapped in markdown code blocks"""
        # Setup mock response with markdown code blocks
        mock_response = {
            "title": "Test Paper",
            "authors": ["Author One"],
            "year": 2024,
            "abstract": "Test abstract",
            "keywords": ["test"]
        }

        mock_message = Mock()
        mock_message.content = f"```json\n{json.dumps(mock_response)}\n```"

        mock_choice = Mock()
        mock_choice.message = mock_message

        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai.return_value = mock_client

        # Execute
        result = await extract_metadata_from_text("Some paper text")

        # Assert
        assert result["title"] == "Test Paper"
        assert result["authors"] == ["Author One"]
        assert result["year"] == 2024

    @pytest.mark.asyncio
    @patch('app.services.metadata_extractor.AsyncOpenAI')
    async def test_extract_metadata_partial_data(self, mock_openai):
        """Test extraction when some metadata fields are missing"""
        # Setup mock response with partial data
        mock_response = {
            "title": "Partial Paper",
            "authors": [],
            "year": None,
            "abstract": "Some abstract text",
            "keywords": []
        }

        mock_message = Mock()
        mock_message.content = json.dumps(mock_response)

        mock_choice = Mock()
        mock_choice.message = mock_message

        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai.return_value = mock_client

        # Execute
        result = await extract_metadata_from_text("Incomplete paper text")

        # Assert
        assert result["title"] == "Partial Paper"
        assert result["authors"] == []
        assert result["year"] is None
        assert result["abstract"] == "Some abstract text"
        assert result["keywords"] == []

    @pytest.mark.asyncio
    @patch('app.services.metadata_extractor.AsyncOpenAI')
    async def test_extract_metadata_api_error(self, mock_openai):
        """Test handling of API errors"""
        # Setup mock to raise an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        mock_openai.return_value = mock_client

        # Execute
        result = await extract_metadata_from_text("Some text")

        # Assert - should return default structure with error
        assert result["title"] is None
        assert result["authors"] == []
        assert result["year"] is None
        assert result["abstract"] is None
        assert result["keywords"] == []
        assert "error" in result
        assert "API Error" in result["error"]

    @pytest.mark.asyncio
    @patch('app.services.metadata_extractor.AsyncOpenAI')
    async def test_extract_metadata_invalid_json(self, mock_openai):
        """Test handling of invalid JSON response"""
        # Setup mock with invalid JSON
        mock_message = Mock()
        mock_message.content = "This is not valid JSON {broken"

        mock_choice = Mock()
        mock_choice.message = mock_message

        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai.return_value = mock_client

        # Execute
        result = await extract_metadata_from_text("Some text")

        # Assert - should return default structure with error
        assert result["title"] is None
        assert result["authors"] == []
        assert result["year"] is None
        assert result["abstract"] is None
        assert result["keywords"] == []
        assert "error" in result

    @pytest.mark.asyncio
    @patch('app.services.metadata_extractor.AsyncOpenAI')
    async def test_extract_metadata_api_call_parameters(self, mock_openai):
        """Test that API is called with correct parameters"""
        # Setup mock
        mock_response = {
            "title": "Test",
            "authors": [],
            "year": None,
            "abstract": None,
            "keywords": []
        }

        mock_message = Mock()
        mock_message.content = json.dumps(mock_response)

        mock_choice = Mock()
        mock_choice.message = mock_message

        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai.return_value = mock_client

        # Execute
        test_text = "Sample paper text for testing"
        await extract_metadata_from_text(test_text)

        # Assert API was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]

        assert call_kwargs["model"] == "gpt-4o-mini"
        assert call_kwargs["temperature"] == 0.1
        assert call_kwargs["max_tokens"] == 1000
        assert len(call_kwargs["messages"]) == 2
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][1]["role"] == "user"

    @pytest.mark.asyncio
    @patch('app.services.metadata_extractor.AsyncOpenAI')
    async def test_extract_metadata_with_multiple_authors(self, mock_openai):
        """Test extraction with multiple authors"""
        # Setup mock response
        mock_response = {
            "title": "Collaborative Research",
            "authors": ["Alice Johnson", "Bob Wilson", "Carol Davis", "David Brown"],
            "year": 2025,
            "abstract": "A collaborative study",
            "keywords": ["collaboration", "research"]
        }

        mock_message = Mock()
        mock_message.content = json.dumps(mock_response)

        mock_choice = Mock()
        mock_choice.message = mock_message

        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai.return_value = mock_client

        # Execute
        result = await extract_metadata_from_text("Multi-author paper text")

        # Assert
        assert len(result["authors"]) == 4
        assert "Alice Johnson" in result["authors"]
        assert "David Brown" in result["authors"]
