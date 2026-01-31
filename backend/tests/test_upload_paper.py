"""
Unit tests for upload_paper endpoint
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import UploadFile
from io import BytesIO


class TestUploadPaperEndpoint:
    """Test cases for upload_paper endpoint"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = Mock()
        db.add = Mock()
        db.flush = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.rollback = Mock()
        return db

    @pytest.fixture
    def mock_pdf_file(self):
        """Mock PDF upload file"""
        file = Mock(spec=UploadFile)
        file.filename = "test_paper.pdf"
        file.file = BytesIO(b"fake pdf content")
        return file

    @pytest.fixture
    def sample_metadata(self):
        """Sample metadata extracted from PDF"""
        return {
            "title": "Machine Learning in Healthcare",
            "authors": ["John Doe", "Jane Smith"],
            "year": 2023,
            "abstract": "This paper explores machine learning applications in healthcare.",
            "keywords": ["machine learning", "healthcare", "AI"],
            "sections": {
                "Introduction": 0,
                "Methods": 500,
                "Results": 1000,
                "Conclusion": 1500
            }
        }

    @pytest.fixture
    def sample_chunks(self):
        """Sample chunks from chunker"""
        return [
            {"content": "Introduction text here.", "section_name": "Introduction", "chunk_index": 0},
            {"content": "Methods description here.", "section_name": "Methods", "chunk_index": 1},
            {"content": "Results analysis here.", "section_name": "Results", "chunk_index": 2},
            {"content": "Conclusion summary here.", "section_name": "Conclusion", "chunk_index": 3}
        ]

    @pytest.fixture
    def sample_embeddings(self):
        """Sample embeddings for chunks"""
        return [
            [0.1] * 1536,
            [0.2] * 1536,
            [0.3] * 1536,
            [0.4] * 1536
        ]

    @pytest.mark.asyncio
    @patch('app.api.papers.generate_embeddings_batch', new_callable=AsyncMock)
    @patch('app.api.papers.chunk_text')
    @patch('app.api.papers.extract_metadata_from_text', new_callable=AsyncMock)
    @patch('app.api.papers.extract_text_from_pdf')
    @patch('app.api.papers.open')
    @patch('app.api.papers.shutil.copyfileobj')
    async def test_upload_paper_success(
        self,
        mock_copyfileobj,
        mock_open,
        mock_extract_text,
        mock_extract_metadata,
        mock_chunk_text,
        mock_generate_embeddings,
        mock_pdf_file,
        mock_db,
        sample_metadata,
        sample_chunks,
        sample_embeddings
    ):
        """Test successful paper upload and processing"""
        # Setup mocks
        mock_extract_text.return_value = "Full text content from PDF..."
        mock_extract_metadata.return_value = sample_metadata
        mock_chunk_text.return_value = sample_chunks
        mock_generate_embeddings.return_value = sample_embeddings

        # Mock paper model
        mock_paper = Mock()
        mock_paper.id = 1
        mock_paper.title = sample_metadata["title"]
        mock_paper.authors = sample_metadata["authors"]
        mock_paper.year = sample_metadata["year"]
        mock_paper.abstract = sample_metadata["abstract"]
        mock_paper.keywords = sample_metadata["keywords"]
        mock_paper.created_at = "2024-01-01T00:00:00"

        # Import inside test to use mocked dependencies
        from app.api.papers import upload_paper

        with patch('app.api.papers.models.Paper', return_value=mock_paper):
            with patch('app.api.papers.models.Chunk'):
                # Execute
                await upload_paper(mock_pdf_file, mock_db)

                # Assert - verify all services were called
                assert mock_extract_text.called
                assert mock_extract_metadata.called
                mock_chunk_text.assert_called_once()
                mock_generate_embeddings.assert_called_once()

                # Assert - verify database operations
                assert mock_db.add.called
                assert mock_db.flush.called
                assert mock_db.commit.called

    @pytest.mark.asyncio
    @patch('app.api.papers.extract_text_from_pdf')
    @patch('app.api.papers.open')
    @patch('app.api.papers.shutil.copyfileobj')
    async def test_upload_paper_invalid_file_type(
        self,
        mock_copyfileobj,
        mock_open,
        mock_extract_text,
        mock_db
    ):
        """Test rejection of non-PDF files"""
        # Create mock non-PDF file
        file = Mock(spec=UploadFile)
        file.filename = "document.docx"
        file.file = BytesIO(b"fake content")

        from app.api.papers import upload_paper
        from fastapi import HTTPException

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await upload_paper(file, mock_db)

        assert exc_info.value.status_code == 400
        assert "Only PDF files are allowed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('app.api.papers.Path.exists')
    @patch('app.api.papers.extract_text_from_pdf')
    @patch('app.api.papers.open')
    @patch('app.api.papers.shutil.copyfileobj')
    @patch('app.api.papers.os.remove')
    async def test_upload_paper_empty_pdf(
        self,
        mock_remove,
        mock_copyfileobj,
        mock_open,
        mock_extract_text,
        mock_exists,
        mock_pdf_file,
        mock_db
    ):
        """Test handling of PDF with no extractable text"""
        # Setup - PDF with no text
        mock_extract_text.return_value = ""
        mock_exists.return_value = True  # File exists for cleanup

        from app.api.papers import upload_paper
        from fastapi import HTTPException

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await upload_paper(mock_pdf_file, mock_db)

        assert exc_info.value.status_code == 400
        assert "No text could be extracted" in str(exc_info.value.detail)
        # Verify cleanup was attempted
        assert mock_remove.called

    @pytest.mark.asyncio
    @patch('app.api.papers.Path.exists')
    @patch('app.api.papers.chunk_text')
    @patch('app.api.papers.extract_metadata_from_text', new_callable=AsyncMock)
    @patch('app.api.papers.extract_text_from_pdf')
    @patch('app.api.papers.open')
    @patch('app.api.papers.shutil.copyfileobj')
    @patch('app.api.papers.os.remove')
    async def test_upload_paper_no_chunks(
        self,
        mock_remove,
        mock_copyfileobj,
        mock_open,
        mock_extract_text,
        mock_extract_metadata,
        mock_chunk_text,
        mock_exists,
        mock_pdf_file,
        mock_db,
        sample_metadata
    ):
        """Test handling when chunking fails"""
        # Setup
        mock_extract_text.return_value = "Some text"
        mock_extract_metadata.return_value = sample_metadata
        mock_chunk_text.return_value = []  # No chunks created
        mock_exists.return_value = True  # File exists for cleanup

        from app.api.papers import upload_paper
        from fastapi import HTTPException

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await upload_paper(mock_pdf_file, mock_db)

        assert exc_info.value.status_code == 400
        assert "Could not create chunks" in str(exc_info.value.detail)
        assert mock_remove.called

    @pytest.mark.asyncio
    @patch('app.api.papers.Path.exists')
    @patch('app.api.papers.generate_embeddings_batch', new_callable=AsyncMock)
    @patch('app.api.papers.chunk_text')
    @patch('app.api.papers.extract_metadata_from_text', new_callable=AsyncMock)
    @patch('app.api.papers.extract_text_from_pdf')
    @patch('app.api.papers.open')
    @patch('app.api.papers.shutil.copyfileobj')
    @patch('app.api.papers.os.remove')
    async def test_upload_paper_embedding_failure(
        self,
        mock_remove,
        mock_copyfileobj,
        mock_open,
        mock_extract_text,
        mock_extract_metadata,
        mock_chunk_text,
        mock_generate_embeddings,
        mock_exists,
        mock_pdf_file,
        mock_db,
        sample_metadata,
        sample_chunks
    ):
        """Test handling of embedding generation failure"""
        # Setup
        mock_extract_text.return_value = "Some text"
        mock_extract_metadata.return_value = sample_metadata
        mock_chunk_text.return_value = sample_chunks
        mock_generate_embeddings.side_effect = Exception("API rate limit exceeded")
        mock_exists.return_value = True  # File exists for cleanup

        from app.api.papers import upload_paper
        from fastapi import HTTPException

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await upload_paper(mock_pdf_file, mock_db)

        assert exc_info.value.status_code == 500
        assert "Error processing PDF" in str(exc_info.value.detail)
        assert mock_remove.called
        assert mock_db.rollback.called

    @pytest.mark.asyncio
    @patch('app.api.papers.chunk_text')
    @patch('app.api.papers.extract_metadata_from_text', new_callable=AsyncMock)
    @patch('app.api.papers.extract_text_from_pdf')
    @patch('app.api.papers.open')
    @patch('app.api.papers.shutil.copyfileobj')
    async def test_upload_paper_minimal_metadata(
        self,
        mock_copyfileobj,
        mock_open,
        mock_extract_text,
        mock_extract_metadata,
        mock_chunk_text,
        mock_pdf_file,
        mock_db,
        sample_chunks
    ):
        """Test upload with minimal metadata (title only)"""
        # Setup - minimal metadata
        minimal_metadata = {
            "title": "Untitled Paper"
        }
        mock_extract_text.return_value = "Some text content"
        mock_extract_metadata.return_value = minimal_metadata
        mock_chunk_text.return_value = sample_chunks

        # Mock embeddings
        with patch('app.api.papers.generate_embeddings_batch', new_callable=AsyncMock) as mock_embeddings:
            mock_embeddings.return_value = [[0.1] * 1536] * len(sample_chunks)

            mock_paper = Mock()
            mock_paper.id = 1
            mock_paper.title = "Untitled Paper"
            mock_paper.authors = []
            mock_paper.year = None
            mock_paper.abstract = None
            mock_paper.keywords = []
            mock_paper.created_at = "2024-01-01T00:00:00"

            from app.api.papers import upload_paper

            with patch('app.api.papers.models.Paper', return_value=mock_paper):
                with patch('app.api.papers.models.Chunk'):
                    # Execute
                    await upload_paper(mock_pdf_file, mock_db)

                    # Assert - paper created with defaults
                    assert mock_db.add.called
                    assert mock_db.commit.called

    @pytest.mark.asyncio
    @patch('app.api.papers.generate_embeddings_batch', new_callable=AsyncMock)
    @patch('app.api.papers.chunk_text')
    @patch('app.api.papers.extract_metadata_from_text', new_callable=AsyncMock)
    @patch('app.api.papers.extract_text_from_pdf')
    @patch('app.api.papers.open')
    @patch('app.api.papers.shutil.copyfileobj')
    async def test_upload_paper_creates_correct_number_of_chunks(
        self,
        mock_copyfileobj,
        mock_open,
        mock_extract_text,
        mock_extract_metadata,
        mock_chunk_text,
        mock_generate_embeddings,
        mock_pdf_file,
        mock_db,
        sample_metadata,
        sample_chunks,
        sample_embeddings
    ):
        """Test that all chunks are saved to database"""
        # Setup
        mock_extract_text.return_value = "Full text"
        mock_extract_metadata.return_value = sample_metadata
        mock_chunk_text.return_value = sample_chunks
        mock_generate_embeddings.return_value = sample_embeddings

        mock_paper = Mock()
        mock_paper.id = 1
        mock_paper.title = sample_metadata["title"]
        mock_paper.authors = sample_metadata["authors"]
        mock_paper.year = sample_metadata["year"]
        mock_paper.abstract = sample_metadata["abstract"]
        mock_paper.keywords = sample_metadata["keywords"]
        mock_paper.created_at = "2024-01-01T00:00:00"

        chunk_records = []

        def mock_chunk_init(*args, **kwargs):
            chunk = Mock()
            chunk.paper_id = kwargs.get('paper_id')
            chunk.content = kwargs.get('content')
            chunk.section_name = kwargs.get('section_name')
            chunk.chunk_index = kwargs.get('chunk_index')
            chunk.embedding = kwargs.get('embedding')
            chunk_records.append(chunk)
            return chunk

        from app.api.papers import upload_paper

        with patch('app.api.papers.models.Paper', return_value=mock_paper):
            with patch('app.api.papers.models.Chunk', side_effect=mock_chunk_init):
                # Execute
                await upload_paper(mock_pdf_file, mock_db)

                # Assert - correct number of chunks created
                assert len(chunk_records) == len(sample_chunks)
                # Verify each chunk has an embedding
                for chunk in chunk_records:
                    assert chunk.embedding is not None
                    assert len(chunk.embedding) == 1536

    @pytest.mark.asyncio
    @patch('app.api.papers.extract_text_from_pdf')
    @patch('app.api.papers.open')
    @patch('app.api.papers.shutil.copyfileobj')
    async def test_upload_paper_with_special_characters_in_filename(
        self,
        mock_copyfileobj,
        mock_open,
        mock_extract_text,
        mock_db
    ):
        """Test upload with special characters in filename"""
        # Create file with special characters
        file = Mock(spec=UploadFile)
        file.filename = "paper (2023) [v2] - final.pdf"
        file.file = BytesIO(b"fake content")

        mock_extract_text.return_value = "Some text"

        with patch('app.api.papers.extract_metadata_from_text', new_callable=AsyncMock) as mock_metadata:
            with patch('app.api.papers.chunk_text') as mock_chunk:
                with patch('app.api.papers.generate_embeddings_batch', new_callable=AsyncMock):
                    mock_metadata.return_value = {"title": "Test"}
                    mock_chunk.return_value = [
                        {"content": "text", "section_name": None, "chunk_index": 0}
                    ]

                    mock_paper = Mock()
                    mock_paper.id = 1
                    mock_paper.title = "Test"
                    mock_paper.authors = []
                    mock_paper.year = None
                    mock_paper.abstract = None
                    mock_paper.keywords = []
                    mock_paper.created_at = "2024-01-01T00:00:00"

                    from app.api.papers import upload_paper

                    with patch('app.api.papers.models.Paper', return_value=mock_paper):
                        with patch('app.api.papers.models.Chunk'):
                            # Should not raise an exception
                            result = await upload_paper(file, mock_db)
                            assert result is not None
