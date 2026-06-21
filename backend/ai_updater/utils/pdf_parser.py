"""Utilities for extracting text from resume files (PDF and DOCX)."""


def extract_text_from_pdf(file) -> str:
    """Extract plain text from a PDF file."""
    ...


def extract_text_from_docx(file) -> str:
    """Extract plain text from a DOCX file."""
    ...


def extract_text(file) -> str:
    """Extract text from a file, detecting format by extension or MIME type."""
    ...
