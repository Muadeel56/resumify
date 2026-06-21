from unittest.mock import patch

from django.test import SimpleTestCase
from pdfminer.pdfdocument import PDFPasswordIncorrect

from ai_updater.tests.fixtures import (
    DOCX_BODY,
    DOCX_HEADING,
    PAGE_ONE_TEXT,
    PAGE_TWO_TEXT,
    make_corrupt_docx,
    make_corrupt_pdf,
    make_empty_docx,
    make_empty_pdf,
    make_sample_docx,
    make_sample_pdf,
)
from ai_updater.utils.pdf_parser import (
    extract_resume_text,
    extract_text_from_docx,
    extract_text_from_pdf,
)


class ExtractTextFromPdfTests(SimpleTestCase):
    def test_multi_page_pdf_joins_pages_with_blank_lines(self):
        text = extract_text_from_pdf(make_sample_pdf())
        self.assertIn(PAGE_ONE_TEXT, text)
        self.assertIn(PAGE_TWO_TEXT, text)
        self.assertEqual(text, f"{PAGE_ONE_TEXT}\n\n{PAGE_TWO_TEXT}")

    def test_empty_pdf_returns_empty_string(self):
        self.assertEqual(extract_text_from_pdf(make_empty_pdf()), "")

    def test_corrupt_pdf_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            extract_text_from_pdf(make_corrupt_pdf())
        self.assertIn("Could not parse PDF", str(ctx.exception))

    @patch("ai_updater.utils.pdf_parser.pdfplumber.open")
    def test_password_protected_pdf_raises_value_error(self, mock_open):
        mock_open.side_effect = PDFPasswordIncorrect("password required")
        with self.assertRaises(ValueError) as ctx:
            extract_text_from_pdf(make_sample_pdf())
        self.assertIn("password-protected", str(ctx.exception))


class ExtractTextFromDocxTests(SimpleTestCase):
    def test_docx_returns_non_empty_paragraphs_joined_by_newlines(self):
        text = extract_text_from_docx(make_sample_docx())
        self.assertEqual(text, f"{DOCX_HEADING}\n{DOCX_BODY}")

    def test_empty_docx_returns_empty_string(self):
        self.assertEqual(extract_text_from_docx(make_empty_docx()), "")

    def test_corrupt_docx_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            extract_text_from_docx(make_corrupt_docx())
        self.assertIn("Could not parse DOCX", str(ctx.exception))


class ExtractResumeTextTests(SimpleTestCase):
    def test_routing_pdf_case_insensitive(self):
        text = extract_resume_text(make_sample_pdf(), "Resume.PDF")
        self.assertIn(PAGE_ONE_TEXT, text)

    def test_routing_docx_case_insensitive(self):
        text = extract_resume_text(make_sample_docx(), "Resume.DOCX")
        self.assertIn(DOCX_HEADING, text)

    def test_unsupported_doc_extension_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            extract_resume_text(b"content", "resume.doc")
        self.assertIn("resume.doc", str(ctx.exception))
        self.assertIn("Only PDF and DOCX allowed", str(ctx.exception))

    def test_unsupported_txt_extension_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            extract_resume_text(b"content", "resume.txt")
        self.assertIn("resume.txt", str(ctx.exception))
