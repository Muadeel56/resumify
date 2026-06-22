"""Gemini AI client for resume updates."""

import json
import re
from uuid import uuid4

import google.generativeai as genai
from django.conf import settings
from google.api_core import exceptions as google_exceptions

SYSTEM_PROMPT = """You are a professional resume editor. Your task is to parse plain-text resume content into structured JSON and apply the user's requested changes.

RULES:
1. Output ONLY valid raw JSON matching this exact schema (no markdown, no code fences):
{
  "fullName": "string",
  "profileSummary": "string",
  "contact": {
    "phone": "string",
    "email": "string",
    "location": "string"
  },
  "experience": [
    {
      "id": "string (UUID, optional)",
      "company": "string",
      "position": "string",
      "startDate": "string",
      "endDate": "string",
      "description": "string"
    }
  ],
  "education": [
    {
      "id": "string (UUID, optional)",
      "institution": "string",
      "degree": "string",
      "field": "string",
      "startDate": "string",
      "endDate": "string",
      "grade": "string (optional)"
    }
  ],
  "skills": ["string"],
  "languages": [
    {
      "id": "string (UUID, optional)",
      "name": "string",
      "proficiency": "string"
    }
  ],
  "certifications": [
    {
      "id": "string (UUID, optional)",
      "name": "string",
      "issuer": "string",
      "date": "string"
    }
  ],
  "extracurricular": ["string"]
}
2. The resume text may come from a multi-column PDF and appear out of order. Reconstruct logical sections (Contact, Profile, Work Experience, Education, Skills, Languages, Certifications/Training, Extracurricular) from context.
3. The resume text may include two blocks: a PRIMARY RESUME and an optional SUPPORTING DOCUMENT. If a supporting document is present, use it only to add missing facts (e.g. internship company, title, dates) and do not remove existing resume content.
4. Apply ONLY the changes the user requests. NEVER invent experience, skills, education, languages, certifications, or extracurricular items not present in the source text.
3. Fix grammar and spelling errors across all sections automatically.
4. Preserve all factual content from the original resume unless the user explicitly asks to change it.
5. After the JSON object, on a new line, write CHANGES: followed by a human-readable bullet list of every change you made (one change per line, prefixed with "- ").

Example output format:
{"fullName": "John Doe", ...}
CHANGES:
- Updated position title to Senior Software Engineer
- Fixed grammar in profile summary
"""

_configured_key: str | None = None


class GeminiConfigError(Exception):
    """Raised when GEMINI_API_KEY is missing or empty."""


class GeminiParseError(Exception):
    """Raised when Gemini response cannot be parsed as valid JSON."""


class GeminiAPIError(Exception):
    """Raised when the Gemini API call fails."""


class InvalidInputError(Exception):
    """Raised when resume_text or instructions are empty."""


def _ensure_configured() -> None:
    global _configured_key
    if not settings.GEMINI_API_KEY:
        raise GeminiConfigError(
            "AI service is not configured. Set GEMINI_API_KEY in backend/.env."
        )
    if _configured_key != settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured_key = settings.GEMINI_API_KEY


def _map_google_api_error(exc: google_exceptions.GoogleAPIError) -> str:
    if isinstance(exc, google_exceptions.PermissionDenied):
        return (
            "The AI API key is invalid or has been revoked. "
            "Generate a new key at https://aistudio.google.com/apikey "
            "and update GEMINI_API_KEY in backend/.env."
        )
    if isinstance(exc, google_exceptions.ResourceExhausted):
        return "AI service quota exceeded. Please try again later."
    if isinstance(exc, google_exceptions.NotFound):
        return (
            f"The configured AI model ({settings.GEMINI_MODEL}) is not available. "
            "Set GEMINI_MODEL in backend/.env to a supported model."
        )
    return "AI service is temporarily unavailable. Please try again."


def _strip_json_fences(text: str) -> str:
    stripped = text.strip()
    fence_match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", stripped, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return stripped


def _parse_changes(changes_part: str) -> list[str]:
    changes = []
    for line in changes_part.strip().splitlines():
        line = line.strip()
        if line.startswith("- "):
            changes.append(line[2:].strip())
        elif line.startswith("* "):
            changes.append(line[2:].strip())
        elif line:
            changes.append(line)
    return changes


def _parse_gemini_response(text: str) -> tuple[dict, list[str]]:
    if "CHANGES:" in text:
        json_part, changes_part = text.split("CHANGES:", 1)
        changes = _parse_changes(changes_part)
    else:
        json_part = text
        changes = ["Resume updated successfully"]

    json_part = _strip_json_fences(json_part.strip())

    try:
        resume_data = json.loads(json_part)
    except json.JSONDecodeError as exc:
        raise GeminiParseError("AI returned an invalid response.") from exc

    if not isinstance(resume_data, dict):
        raise GeminiParseError("AI returned an invalid response.")

    return resume_data, changes


def _ensure_ids(resume_data: dict) -> dict:
    list_sections = ("experience", "education", "languages", "certifications")
    for section in list_sections:
        items = resume_data.get(section, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and not item.get("id"):
                item["id"] = str(uuid4())
    return resume_data


def _normalize_resume_data(resume_data: dict) -> dict:
    if not isinstance(resume_data, dict):
        return {}

    resume_data.setdefault("fullName", "")
    resume_data.setdefault("profileSummary", "")
    resume_data.setdefault("experience", [])
    resume_data.setdefault("education", [])
    resume_data.setdefault("skills", [])
    resume_data.setdefault("languages", [])
    resume_data.setdefault("certifications", [])
    resume_data.setdefault("extracurricular", [])

    contact = resume_data.get("contact")
    if not isinstance(contact, dict):
        contact = {}
    contact.setdefault("phone", "")
    contact.setdefault("email", "")
    contact.setdefault("location", "")
    resume_data["contact"] = contact

    return resume_data


def update_resume_with_ai(resume_text: str, instructions: str) -> dict:
    """Parse resume text, apply user instructions via Gemini, return structured result."""
    if not resume_text or not resume_text.strip():
        raise InvalidInputError("Resume text cannot be empty.")
    if not instructions or not instructions.strip():
        raise InvalidInputError("Instructions cannot be empty.")

    _ensure_configured()

    user_prompt = (
        f"CURRENT RESUME TEXT:\n{resume_text.strip()}\n\n"
        f"USER'S REQUESTED CHANGES:\n{instructions.strip()}"
    )

    try:
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(user_prompt)
        response_text = response.text
    except google_exceptions.GoogleAPIError as exc:
        raise GeminiAPIError(_map_google_api_error(exc)) from exc
    except Exception as exc:
        raise GeminiAPIError("AI service is temporarily unavailable. Please try again.") from exc

    if not response_text:
        raise GeminiParseError("AI returned an empty response.")

    resume_data, changes = _parse_gemini_response(response_text)
    resume_data = _normalize_resume_data(resume_data)
    resume_data = _ensure_ids(resume_data)

    return {"updated_resume": resume_data, "changes_made": changes}
