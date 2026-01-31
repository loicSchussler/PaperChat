"""
Unit tests for PDF text extraction service
"""
from unittest.mock import Mock, patch, MagicMock
from app.services.pdf_extractor import extract_text_from_pdf


class TestExtractTextFromPdf:
    """Test cases for extract_text_from_pdf function"""

    @patch('app.services.pdf_extractor.PdfReader')
    def test_extract_text_from_pdf_success(self, mock_pdf_reader):
        """Test successful text extraction from PDF"""
        # Setup mock
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content. "
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader

        # Execute
        result = extract_text_from_pdf("dummy_path.pdf")

        # Assert
        assert result == "Page 1 content. Page 2 content."
        mock_pdf_reader.assert_called_once_with("dummy_path.pdf")
        mock_page1.extract_text.assert_called_once()
        mock_page2.extract_text.assert_called_once()

    @patch('app.services.pdf_extractor.PdfReader')
    def test_extract_text_from_pdf_empty_pages(self, mock_pdf_reader):
        """Test extraction from PDF with empty pages"""
        # Setup mock with empty content
        mock_page = Mock()
        mock_page.extract_text.return_value = ""

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        # Execute
        result = extract_text_from_pdf("empty.pdf")

        # Assert
        assert result == ""
        mock_pdf_reader.assert_called_once_with("empty.pdf")

    @patch('app.services.pdf_extractor.PdfReader')
    def test_extract_text_from_pdf_single_page(self, mock_pdf_reader):
        """Test extraction from single-page PDF"""
        # Setup mock
        mock_page = Mock()
        mock_page.extract_text.return_value = "Single page content"

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        # Execute
        result = extract_text_from_pdf("single_page.pdf")

        # Assert
        assert result == "Single page content"
        assert len(mock_reader.pages) == 1

    @patch('app.services.pdf_extractor.PdfReader')
    def test_extract_text_from_pdf_special_characters(self, mock_pdf_reader):
        """Test extraction with special characters and unicode"""
        # Setup mock with special characters
        mock_page = Mock()
        mock_page.extract_text.return_value = "Résumé: α, β, γ — special chars!"

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        # Execute
        result = extract_text_from_pdf("special.pdf")

        # Assert
        assert result == "Résumé: α, β, γ — special chars!"
        assert "α" in result
        assert "Résumé" in result

    @patch('app.services.pdf_extractor.PdfReader')
    def test_extract_text_from_pdf_multiple_pages(self, mock_pdf_reader):
        """Test extraction from multi-page PDF"""
        # Setup mock with multiple pages
        pages = []
        for i in range(5):
            mock_page = Mock()
            mock_page.extract_text.return_value = f"Content page {i+1}. "
            pages.append(mock_page)

        mock_reader = MagicMock()
        mock_reader.pages = pages
        mock_pdf_reader.return_value = mock_reader

        # Execute
        result = extract_text_from_pdf("multi_page.pdf")

        # Assert
        expected = "Content page 1. Content page 2. Content page 3. Content page 4. Content page 5. "
        assert result == expected
        assert len(mock_reader.pages) == 5
