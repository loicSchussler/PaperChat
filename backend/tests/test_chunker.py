"""
Unit tests for text chunking service
"""
from unittest.mock import Mock, patch
from app.services.chunker import chunk_text


class TestChunkText:
    """Test cases for chunk_text function"""

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_basic_no_sections(self, mock_splitter_class):
        """Test basic chunking without sections"""
        # Setup mock
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = [
            "First chunk of text.",
            "Second chunk of text.",
            "Third chunk of text."
        ]
        mock_splitter_class.return_value = mock_splitter

        # Execute
        text = "First chunk of text. Second chunk of text. Third chunk of text."
        result = chunk_text(text)

        # Assert
        assert len(result) == 3
        assert result[0]["content"] == "First chunk of text."
        assert result[0]["section_name"] is None
        assert result[0]["chunk_index"] == 0
        assert result[1]["chunk_index"] == 1
        assert result[2]["chunk_index"] == 2

        # Verify splitter configuration
        mock_splitter_class.assert_called_once_with(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_with_sections(self, mock_splitter_class):
        """Test chunking with section context"""
        # Setup mock
        text = "Introduction text here. Methods section content. Results section data. Conclusion text."
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = [
            "Introduction text here.",
            "Methods section content.",
            "Results section data.",
            "Conclusion text."
        ]
        mock_splitter_class.return_value = mock_splitter

        sections = {
            "Introduction": 0,
            "Methods": 24,
            "Results": 49,
            "Conclusion": 71
        }

        # Execute
        result = chunk_text(text, sections)

        # Assert
        assert len(result) == 4
        assert result[0]["section_name"] == "Introduction"
        assert result[1]["section_name"] == "Methods"
        assert result[2]["section_name"] == "Results"
        assert result[3]["section_name"] == "Conclusion"

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_empty_text(self, mock_splitter_class):
        """Test chunking with empty text"""
        # Setup mock
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = []
        mock_splitter_class.return_value = mock_splitter

        # Execute
        result = chunk_text("")

        # Assert
        assert result == []
        mock_splitter.split_text.assert_called_once_with("")

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_single_chunk(self, mock_splitter_class):
        """Test text that fits in a single chunk"""
        # Setup mock
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = ["Short text that fits in one chunk."]
        mock_splitter_class.return_value = mock_splitter

        # Execute
        result = chunk_text("Short text that fits in one chunk.")

        # Assert
        assert len(result) == 1
        assert result[0]["content"] == "Short text that fits in one chunk."
        assert result[0]["section_name"] is None
        assert result[0]["chunk_index"] == 0

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_multiple_chunks_same_section(self, mock_splitter_class):
        """Test multiple chunks all belonging to the same section"""
        # Setup mock
        text = "Introduction paragraph 1. Introduction paragraph 2. Introduction paragraph 3."
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = [
            "Introduction paragraph 1.",
            "Introduction paragraph 2.",
            "Introduction paragraph 3."
        ]
        mock_splitter_class.return_value = mock_splitter

        sections = {"Introduction": 0}

        # Execute
        result = chunk_text(text, sections)

        # Assert
        assert len(result) == 3
        assert all(chunk["section_name"] == "Introduction" for chunk in result)
        assert result[0]["chunk_index"] == 0
        assert result[1]["chunk_index"] == 1
        assert result[2]["chunk_index"] == 2

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_section_assignment_accuracy(self, mock_splitter_class):
        """Test accurate section assignment based on text position"""
        # Setup mock with realistic academic paper structure
        text = "Abstract content goes here.\n\nIntroduction section with detailed text.\n\nMethods and materials section.\n\nResults and findings section."

        mock_splitter = Mock()
        mock_splitter.split_text.return_value = [
            "Abstract content goes here.",
            "Introduction section with detailed text.",
            "Methods and materials section.",
            "Results and findings section."
        ]
        mock_splitter_class.return_value = mock_splitter

        sections = {
            "Abstract": 0,
            "Introduction": 29,
            "Methods": 71,
            "Results": 103
        }

        # Execute
        result = chunk_text(text, sections)

        # Assert
        assert result[0]["section_name"] == "Abstract"
        assert result[1]["section_name"] == "Introduction"
        assert result[2]["section_name"] == "Methods"
        assert result[3]["section_name"] == "Results"

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_with_special_characters(self, mock_splitter_class):
        """Test chunking with special characters and unicode"""
        # Setup mock
        text = "Résumé: α, β, γ — special chars! Next section: δ, ε, ζ."
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = [
            "Résumé: α, β, γ — special chars!",
            "Next section: δ, ε, ζ."
        ]
        mock_splitter_class.return_value = mock_splitter

        # Execute
        result = chunk_text(text)

        # Assert
        assert len(result) == 2
        assert "α" in result[0]["content"]
        assert "δ" in result[1]["content"]
        assert result[0]["chunk_index"] == 0
        assert result[1]["chunk_index"] == 1

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_with_newlines_and_paragraphs(self, mock_splitter_class):
        """Test chunking with multiple newlines and paragraph breaks"""
        # Setup mock
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = [
            "Paragraph 1.",
            "Paragraph 2.",
            "Paragraph 3."
        ]
        mock_splitter_class.return_value = mock_splitter

        # Execute
        result = chunk_text(text)

        # Assert
        assert len(result) == 3
        assert all("content" in chunk for chunk in result)
        assert all("chunk_index" in chunk for chunk in result)
        assert all("section_name" in chunk for chunk in result)

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_chunk_not_found_in_text(self, mock_splitter_class):
        """Test handling when chunk is not found in original text (edge case)"""
        # Setup mock - this is an edge case where text.find() returns -1
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = ["Some modified chunk"]
        mock_splitter_class.return_value = mock_splitter

        sections = {"Section1": 0}

        # Execute
        result = chunk_text("Original text", sections)

        # Assert - section_name should be None when chunk not found
        assert len(result) == 1
        assert result[0]["section_name"] is None

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_result_structure(self, mock_splitter_class):
        """Test that result has correct structure with all required fields"""
        # Setup mock
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = ["Test chunk"]
        mock_splitter_class.return_value = mock_splitter

        # Execute
        result = chunk_text("Test chunk")

        # Assert
        assert len(result) == 1
        assert "content" in result[0]
        assert "section_name" in result[0]
        assert "chunk_index" in result[0]
        assert isinstance(result[0]["content"], str)
        assert isinstance(result[0]["chunk_index"], int)
        assert result[0]["section_name"] is None or isinstance(result[0]["section_name"], str)

    @patch('app.services.chunker.RecursiveCharacterTextSplitter')
    def test_chunk_text_large_document(self, mock_splitter_class):
        """Test chunking of a large document with many chunks"""
        # Setup mock
        mock_splitter = Mock()
        chunks = [f"Chunk {i} content." for i in range(20)]
        mock_splitter.split_text.return_value = chunks
        mock_splitter_class.return_value = mock_splitter

        # Execute
        text = " ".join(chunks)
        result = chunk_text(text)

        # Assert
        assert len(result) == 20
        assert result[0]["chunk_index"] == 0
        assert result[19]["chunk_index"] == 19
        assert all(chunk["content"] == f"Chunk {i} content." for i, chunk in enumerate(result))
