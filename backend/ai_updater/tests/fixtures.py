"""Programmatic test fixtures for resume parser tests."""

import io

import docx

PAGE_ONE_TEXT = "Jane Doe - Software Engineer"
PAGE_TWO_TEXT = "Experience at Acme Corp since 2020"
DOCX_HEADING = "Professional Summary"
DOCX_BODY = "Full-stack developer with five years of experience."


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _assemble_pdf(page_texts: list[str]) -> bytes:
    """Build a minimal valid PDF with extractable text on each page."""
    if not page_texts:
        page_texts = [""]

    num_pages = len(page_texts)
    font_id = 3 + (num_pages * 2)
    page_entries = []
    body_objects = []

    for index, text in enumerate(page_texts):
        page_id = 3 + (index * 2)
        contents_id = page_id + 1
        escaped = _pdf_escape(text)
        stream = f"BT\n/F1 12 Tf\n72 720 Td\n({escaped}) Tj\nET"
        body_objects.append(
            f"{contents_id} 0 obj\n"
            f"<< /Length {len(stream)} >>\n"
            f"stream\n{stream}\nendstream\n"
            f"endobj\n"
        )
        body_objects.append(
            f"{page_id} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {contents_id} 0 R "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>\n"
            f"endobj\n"
        )
        page_entries.append(f"{page_id} 0 R")

    kids = " ".join(page_entries)
    body = (
        "%PDF-1.4\n"
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {num_pages} >>\nendobj\n"
        + "".join(body_objects)
        + (
            f"{font_id} 0 obj\n"
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n"
            "endobj\n"
        )
    )

    num_objects = font_id
    offsets = [0]
    for obj_num in range(1, num_objects + 1):
        marker = f"\n{obj_num} 0 obj\n" if obj_num > 1 else f"{obj_num} 0 obj\n"
        pos = body.find(marker)
        if pos == -1:
            raise ValueError(f"PDF fixture missing object {obj_num}")
        offsets.append(pos if obj_num == 1 else pos + 1)

    xref_offset = len(body.encode("latin-1"))
    xref_rows = ["0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref_rows.append(f"{offset:010d} 00000 n \n")

    trailer = (
        f"xref\n0 {num_objects + 1}\n"
        + "".join(xref_rows)
        + (
            "trailer\n"
            f"<< /Size {num_objects + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        )
    )
    return (body + trailer).encode("latin-1")


def make_sample_pdf() -> bytes:
    """Two-page PDF with known text on each page."""
    return _assemble_pdf([PAGE_ONE_TEXT, PAGE_TWO_TEXT])


def make_empty_pdf() -> bytes:
    """Valid PDF with no extractable text."""
    body = (
        "%PDF-1.4\n"
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        "3 0 obj\n"
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << >> >>\n"
        "endobj\n"
        "4 0 obj\n<< /Length 0 >>\nstream\n\nendstream\nendobj\n"
    )
    def _object_offset(obj_num: int) -> int:
        marker = f"\n{obj_num} 0 obj\n" if obj_num > 1 else f"{obj_num} 0 obj\n"
        pos = body.find(marker)
        return pos if obj_num == 1 else pos + 1

    xref_offset = len(body.encode("latin-1"))
    trailer = (
        "xref\n0 5\n"
        "0000000000 65535 f \n"
        f"{_object_offset(1):010d} 00000 n \n"
        f"{_object_offset(2):010d} 00000 n \n"
        f"{_object_offset(3):010d} 00000 n \n"
        f"{_object_offset(4):010d} 00000 n \n"
        "trailer\n<< /Size 5 /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    )
    return (body + trailer).encode("latin-1")


def make_corrupt_pdf() -> bytes:
    """Invalid bytes that are not a valid PDF."""
    return b"not-a-valid-pdf-file"


def make_sample_docx() -> bytes:
    """DOCX with headings, body text, and blank paragraphs."""
    document = docx.Document()
    document.add_paragraph(DOCX_HEADING)
    document.add_paragraph("")
    document.add_paragraph(DOCX_BODY)
    document.add_paragraph("   ")
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def make_empty_docx() -> bytes:
    """Valid DOCX with no paragraphs."""
    document = docx.Document()
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def make_corrupt_docx() -> bytes:
    """Invalid bytes that are not a valid DOCX."""
    return b"not-a-valid-docx-file"
