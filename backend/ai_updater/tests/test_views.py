from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from ai_updater.tests.fixtures import make_corrupt_pdf, make_sample_pdf

User = get_user_model()

UPDATE_URL = "/api/ai-updater/update/"

SAMPLE_INSTRUCTIONS = "Change title to Senior Software Engineer"

SAMPLE_RESULT = {
    "updated_resume": {
        "fullName": "John Doe",
        "profileSummary": "Experienced engineer.",
        "experience": [
            {
                "id": "abc-123",
                "company": "Acme Corp",
                "position": "Senior Software Engineer",
                "startDate": "2020-01",
                "endDate": "2023-06",
                "description": "Built web applications.",
            }
        ],
        "education": [],
        "skills": ["Python"],
        "languages": [],
        "certifications": [],
    },
    "changes_made": ["Updated position title to Senior Software Engineer"],
}

EXTRACTED_RESUME_TEXT = "John Doe\nSoftware Engineer at Acme Corp"


def make_uploaded_pdf(content: bytes | None = None, name: str = "resume.pdf"):
    return SimpleUploadedFile(
        name,
        content if content is not None else make_sample_pdf(),
        content_type="application/pdf",
    )


class AIResumeUpdateViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def _post_update(self, data):
        return self.client.post(UPDATE_URL, data, format="multipart")

    def test_unauthenticated_returns_401(self):
        response = self._post_update(
            {
                "file": make_uploaded_pdf(),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_file_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self._post_update({"instructions": SAMPLE_INSTRUCTIONS})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "No file uploaded.")

    def test_missing_instructions_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self._post_update({"file": make_uploaded_pdf()})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Please describe what changes you want.")

    def test_blank_instructions_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self._post_update(
            {
                "file": make_uploaded_pdf(),
                "instructions": "   ",
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Please describe what changes you want.")

    def test_file_too_large_returns_400(self):
        self.client.force_authenticate(user=self.user)
        oversized = b"x" * (5 * 1024 * 1024 + 1)
        response = self._post_update(
            {
                "file": make_uploaded_pdf(oversized),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "File too large. Maximum size is 5MB.")

    def test_unsupported_extension_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self._post_update(
            {
                "file": SimpleUploadedFile(
                    "resume.txt",
                    b"plain text resume",
                    content_type="text/plain",
                ),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Only PDF and DOCX files are supported.")

    @patch("ai_updater.views.update_resume_with_ai")
    @patch("ai_updater.views.extract_resume_text")
    def test_empty_extracted_text_returns_400(self, mock_extract, mock_update):
        mock_extract.return_value = ""
        self.client.force_authenticate(user=self.user)

        response = self._post_update(
            {
                "file": make_uploaded_pdf(),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "Could not extract text from the file. "
            "Make sure your PDF is not scanned/image-based.",
        )
        mock_update.assert_not_called()

    @patch("ai_updater.views.update_resume_with_ai")
    @patch("ai_updater.views.extract_resume_text")
    def test_success_returns_200(self, mock_extract, mock_update):
        mock_extract.return_value = EXTRACTED_RESUME_TEXT
        mock_update.return_value = SAMPLE_RESULT
        self.client.force_authenticate(user=self.user)

        response = self._post_update(
            {
                "file": make_uploaded_pdf(),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_resume"]["fullName"], "John Doe")
        self.assertEqual(
            response.data["changes_made"],
            ["Updated position title to Senior Software Engineer"],
        )
        mock_extract.assert_called_once()
        mock_update.assert_called_once_with(EXTRACTED_RESUME_TEXT, SAMPLE_INSTRUCTIONS)

    @patch("ai_updater.views.update_resume_with_ai")
    @patch("ai_updater.views.extract_resume_text")
    def test_supporting_file_passed_to_ai(self, mock_extract, mock_update):
        mock_extract.side_effect = [EXTRACTED_RESUME_TEXT, "supporting doc text"]
        mock_update.return_value = SAMPLE_RESULT
        self.client.force_authenticate(user=self.user)

        response = self._post_update(
            {
                "file": make_uploaded_pdf(name="resume.pdf"),
                "supporting_file": make_uploaded_pdf(name="support.pdf"),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_extract.call_count, 2)
        mock_update.assert_called_once()
        combined_text = mock_update.call_args.args[0]
        self.assertIn("PRIMARY RESUME:", combined_text)
        self.assertIn("SUPPORTING DOCUMENT:", combined_text)

    @patch("ai_updater.views.update_resume_with_ai")
    @patch("ai_updater.views.extract_resume_text")
    def test_parser_value_error_returns_400(self, mock_extract, mock_update):
        mock_extract.side_effect = ValueError("Could not parse PDF: corrupt file.")
        self.client.force_authenticate(user=self.user)

        response = self._post_update(
            {
                "file": make_uploaded_pdf(make_corrupt_pdf()),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Could not parse PDF: corrupt file.")
        mock_update.assert_not_called()

    @patch("ai_updater.views.update_resume_with_ai")
    @patch("ai_updater.views.extract_resume_text")
    def test_ai_failure_returns_500(self, mock_extract, mock_update):
        mock_extract.return_value = EXTRACTED_RESUME_TEXT
        mock_update.side_effect = RuntimeError("Gemini unavailable")
        self.client.force_authenticate(user=self.user)

        response = self._post_update(
            {
                "file": make_uploaded_pdf(),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"], "AI processing failed. Please try again.")

    @patch("ai_updater.views.update_resume_with_ai")
    @patch("ai_updater.views.extract_resume_text")
    def test_gemini_api_error_returns_503(self, mock_extract, mock_update):
        from ai_updater.utils.ai_client import GeminiAPIError

        mock_extract.return_value = EXTRACTED_RESUME_TEXT
        mock_update.side_effect = GeminiAPIError("The AI API key is invalid or has been revoked.")
        self.client.force_authenticate(user=self.user)

        response = self._post_update(
            {
                "file": make_uploaded_pdf(),
                "instructions": SAMPLE_INSTRUCTIONS,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("invalid or has been revoked", response.data["error"])
