"""Utilities for extracting text from resume files (PDF and DOCX)."""

import io

import docx
import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from PDF bytes."""
    text_parts = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except PDFPasswordIncorrect as exc:
        raise ValueError("Could not parse PDF: file is password-protected.") from exc
    except Exception as exc:
        raise ValueError(f"Could not parse PDF: {exc}") from exc
    return "\n\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from DOCX bytes."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    except Exception as exc:
        raise ValueError(f"Could not parse DOCX: {exc}") from exc
    return "\n".join(paragraphs)


def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from resume bytes, detecting format by filename extension."""
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if filename_lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    raise ValueError(
        f"Unsupported file type: {filename}. Only PDF and DOCX allowed."
    )
