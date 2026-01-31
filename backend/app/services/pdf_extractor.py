"""
Text extraction service from PDF files
"""

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts full text from a PDF file

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text from the PDF
    """
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text