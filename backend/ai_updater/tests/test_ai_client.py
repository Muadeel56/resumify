from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from ai_updater.utils.ai_client import (
    GeminiConfigError,
    GeminiParseError,
    InvalidInputError,
    _ensure_ids,
    _parse_gemini_response,
    update_resume_with_ai,
)

SAMPLE_RESUME_JSON = {
    "fullName": "John Doe",
    "profileSummary": "Software engineer with 5 years of experience.",
    "experience": [
        {
            "company": "Acme Corp",
            "position": "Software Engineer",
            "startDate": "2020-01",
            "endDate": "2023-06",
            "description": "Built web applications.",
        }
    ],
    "education": [
        {
            "institution": "State University",
            "degree": "BS",
            "field": "Computer Science",
            "startDate": "2016",
            "endDate": "2020",
        }
    ],
    "skills": ["Python", "React"],
    "languages": [{"name": "English", "proficiency": "Native"}],
    "certifications": [{"name": "AWS Certified", "issuer": "Amazon", "date": "2022"}],
}


def _make_gemini_response(json_data, changes=None):
    import json

    body = json.dumps(json_data)
    if changes is not None:
        changes_lines = "\n".join(f"- {c}" for c in changes)
        return f"{body}\nCHANGES:\n{changes_lines}"
    return body


class ParseGeminiResponseTests(SimpleTestCase):
    def test_valid_json_with_changes(self):
        text = _make_gemini_response(
            SAMPLE_RESUME_JSON,
            ["Updated position title", "Fixed grammar in profile summary"],
        )
        resume_data, changes = _parse_gemini_response(text)
        self.assertEqual(resume_data["fullName"], "John Doe")
        self.assertEqual(changes, ["Updated position title", "Fixed grammar in profile summary"])

    def test_json_wrapped_in_fences(self):
        import json

        text = (
            "```json\n"
            f"{json.dumps(SAMPLE_RESUME_JSON)}\n"
            "```\n"
            "CHANGES:\n"
            "- Fixed typo in profile summary"
        )
        resume_data, changes = _parse_gemini_response(text)
        self.assertEqual(resume_data["fullName"], "John Doe")
        self.assertEqual(changes, ["Fixed typo in profile summary"])

    def test_missing_changes_defaults(self):
        import json

        text = json.dumps(SAMPLE_RESUME_JSON)
        _, changes = _parse_gemini_response(text)
        self.assertEqual(changes, ["Resume updated successfully"])

    def test_invalid_json_raises_parse_error(self):
        with self.assertRaises(GeminiParseError):
            _parse_gemini_response("not valid json\nCHANGES:\n- something")


class EnsureIdsTests(SimpleTestCase):
    def test_missing_ids_get_uuid(self):
        data = {
            "experience": [{"company": "Acme"}],
            "education": [{"institution": "State U"}],
            "languages": [{"name": "English", "proficiency": "Native"}],
            "certifications": [{"name": "AWS", "issuer": "Amazon", "date": "2022"}],
        }
        result = _ensure_ids(data)
        for section in ("experience", "education", "languages", "certifications"):
            for item in result[section]:
                self.assertIn("id", item)
                self.assertTrue(len(item["id"]) > 0)

    def test_existing_ids_preserved(self):
        data = {
            "experience": [{"id": "existing-id", "company": "Acme"}],
            "education": [],
            "languages": [],
            "certifications": [],
        }
        result = _ensure_ids(data)
        self.assertEqual(result["experience"][0]["id"], "existing-id")


class UpdateResumeWithAiTests(SimpleTestCase):
    def setUp(self):
        self.resume_text = "John Doe\nSoftware Engineer at Acme Corp"
        self.instructions = "Change title to Senior Software Engineer"

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("ai_updater.utils.ai_client.genai.GenerativeModel")
    def test_valid_response_parsed(self, mock_model_cls):
        mock_response = MagicMock()
        mock_response.text = _make_gemini_response(
            SAMPLE_RESUME_JSON,
            ["Updated position title to Senior Software Engineer"],
        )
        mock_model_cls.return_value.generate_content.return_value = mock_response

        result = update_resume_with_ai(self.resume_text, self.instructions)

        self.assertEqual(result["updated_resume"]["fullName"], "John Doe")
        self.assertEqual(
            result["changes_made"],
            ["Updated position title to Senior Software Engineer"],
        )
        mock_model_cls.assert_called_once()

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("ai_updater.utils.ai_client.genai.GenerativeModel")
    def test_fenced_json_stripped(self, mock_model_cls):
        import json

        mock_response = MagicMock()
        mock_response.text = (
            "```json\n"
            f"{json.dumps(SAMPLE_RESUME_JSON)}\n"
            "```\n"
            "CHANGES:\n"
            "- Fixed grammar"
        )
        mock_model_cls.return_value.generate_content.return_value = mock_response

        result = update_resume_with_ai(self.resume_text, self.instructions)
        self.assertEqual(result["updated_resume"]["fullName"], "John Doe")

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("ai_updater.utils.ai_client.genai.GenerativeModel")
    def test_missing_changes_defaults(self, mock_model_cls):
        import json

        mock_response = MagicMock()
        mock_response.text = json.dumps(SAMPLE_RESUME_JSON)
        mock_model_cls.return_value.generate_content.return_value = mock_response

        result = update_resume_with_ai(self.resume_text, self.instructions)
        self.assertEqual(result["changes_made"], ["Resume updated successfully"])

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("ai_updater.utils.ai_client.genai.GenerativeModel")
    def test_missing_ids_injected(self, mock_model_cls):
        mock_response = MagicMock()
        mock_response.text = _make_gemini_response(SAMPLE_RESUME_JSON, ["Updated resume"])
        mock_model_cls.return_value.generate_content.return_value = mock_response

        result = update_resume_with_ai(self.resume_text, self.instructions)
        resume = result["updated_resume"]
        for section in ("experience", "education", "languages", "certifications"):
            for item in resume[section]:
                self.assertIn("id", item)

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("ai_updater.utils.ai_client.genai.GenerativeModel")
    def test_invalid_json_raises_parse_error(self, mock_model_cls):
        mock_response = MagicMock()
        mock_response.text = "not json\nCHANGES:\n- something"
        mock_model_cls.return_value.generate_content.return_value = mock_response

        with self.assertRaises(GeminiParseError):
            update_resume_with_ai(self.resume_text, self.instructions)

    @override_settings(GEMINI_API_KEY="")
    def test_empty_api_key_raises_config_error(self):
        with self.assertRaises(GeminiConfigError):
            update_resume_with_ai(self.resume_text, self.instructions)

    @override_settings(GEMINI_API_KEY="test-key")
    def test_empty_resume_text_raises_invalid_input(self):
        with self.assertRaises(InvalidInputError):
            update_resume_with_ai("", self.instructions)

    @override_settings(GEMINI_API_KEY="test-key")
    def test_empty_instructions_raises_invalid_input(self):
        with self.assertRaises(InvalidInputError):
            update_resume_with_ai(self.resume_text, "   ")
