import os

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_updater.utils.ai_client import (
    GeminiAPIError,
    GeminiConfigError,
    GeminiParseError,
    InvalidInputError,
    update_resume_with_ai,
)
from ai_updater.utils.pdf_parser import extract_resume_text


class AIResumeUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    MAX_FILE_SIZE = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    def post(self, request):
        file = request.FILES.get("file")
        supporting_file = request.FILES.get("supporting_file")
        instructions = request.data.get("instructions", "").strip()

        if not file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not instructions:
            return Response(
                {"error": "Please describe what changes you want."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if file.size > self.MAX_FILE_SIZE:
            return Response(
                {"error": "File too large. Maximum size is 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        extension = os.path.splitext(file.name)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            return Response(
                {"error": "Only PDF and DOCX files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if supporting_file:
            if supporting_file.size > self.MAX_FILE_SIZE:
                return Response(
                    {"error": "File too large. Maximum size is 5MB."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            supporting_extension = os.path.splitext(supporting_file.name)[1].lower()
            if supporting_extension not in self.ALLOWED_EXTENSIONS:
                return Response(
                    {"error": "Only PDF and DOCX files are supported."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            resume_text = extract_resume_text(file.read(), file.name)
        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supporting_text = ""
        if supporting_file:
            try:
                supporting_text = extract_resume_text(
                    supporting_file.read(),
                    supporting_file.name,
                )
            except ValueError as exc:
                return Response(
                    {"error": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not resume_text or not resume_text.strip():
            return Response(
                {
                    "error": (
                        "Could not extract text from the file. "
                        "Make sure your PDF is not scanned/image-based."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            combined_text = resume_text
            if supporting_text and supporting_text.strip():
                combined_text = (
                    "PRIMARY RESUME:\n"
                    f"{resume_text.strip()}\n\n"
                    "SUPPORTING DOCUMENT:\n"
                    f"{supporting_text.strip()}\n"
                )

            result = update_resume_with_ai(combined_text, instructions)
        except InvalidInputError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except GeminiConfigError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except GeminiParseError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        except GeminiAPIError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception:
            return Response(
                {"error": "AI processing failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result, status=status.HTTP_200_OK)
