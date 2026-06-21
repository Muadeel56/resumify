from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ai_updater.utils.ai_client import GeminiParseError

User = get_user_model()

UPDATE_URL = "/api/ai/update-resume/"

SAMPLE_PAYLOAD = {
    "resume_text": "John Doe\nSoftware Engineer at Acme Corp",
    "instructions": "Change title to Senior Software Engineer",
}

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


class UpdateResumeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_unauthenticated_returns_401(self):
        response = self.client.post(UPDATE_URL, SAMPLE_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_fields_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(UPDATE_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("resume_text", response.data)
        self.assertIn("instructions", response.data)

    def test_empty_resume_text_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            UPDATE_URL,
            {"resume_text": "", "instructions": "Fix grammar"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("ai_updater.views.update_resume_with_ai")
    def test_success_returns_200(self, mock_update):
        mock_update.return_value = SAMPLE_RESULT
        self.client.force_authenticate(user=self.user)

        response = self.client.post(UPDATE_URL, SAMPLE_PAYLOAD, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_resume"]["fullName"], "John Doe")
        self.assertEqual(
            response.data["changes_made"],
            ["Updated position title to Senior Software Engineer"],
        )
        mock_update.assert_called_once_with(
            SAMPLE_PAYLOAD["resume_text"],
            SAMPLE_PAYLOAD["instructions"],
        )

    @override_settings(GEMINI_API_KEY="")
    def test_missing_api_key_returns_503(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(UPDATE_URL, SAMPLE_PAYLOAD, format="json")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["detail"], "AI service is not configured.")
        self.assertNotIn("AIza", str(response.data))

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("ai_updater.views.update_resume_with_ai")
    def test_parse_error_returns_502(self, mock_update):
        mock_update.side_effect = GeminiParseError("AI returned an invalid response.")
        self.client.force_authenticate(user=self.user)

        response = self.client.post(UPDATE_URL, SAMPLE_PAYLOAD, format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            response.data["detail"],
            "AI returned an invalid response. Please try again.",
        )
