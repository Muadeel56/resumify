import os

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_updater.utils.ai_client import update_resume_with_ai
from ai_updater.utils.pdf_parser import extract_resume_text


class AIResumeUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    MAX_FILE_SIZE = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    def post(self, request):
        file = request.FILES.get("file")
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

        try:
            resume_text = extract_resume_text(file.read(), file.name)
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
            result = update_resume_with_ai(resume_text, instructions)
        except Exception:
            return Response(
                {"error": "AI processing failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result, status=status.HTTP_200_OK)
