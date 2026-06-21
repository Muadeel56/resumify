from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ai_updater.serializers import AIUpdateResumeSerializer
from ai_updater.utils.ai_client import (
    GeminiAPIError,
    GeminiConfigError,
    GeminiParseError,
    InvalidInputError,
    update_resume_with_ai,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_resume(request):
    serializer = AIUpdateResumeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if not settings.GEMINI_API_KEY:
        return Response(
            {"detail": "AI service is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    resume_text = serializer.validated_data["resume_text"]
    instructions = serializer.validated_data["instructions"]

    try:
        result = update_resume_with_ai(resume_text, instructions)
    except InvalidInputError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except GeminiConfigError:
        return Response(
            {"detail": "AI service is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except GeminiParseError:
        return Response(
            {"detail": "AI returned an invalid response. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except GeminiAPIError:
        return Response(
            {"detail": "AI service is temporarily unavailable. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(result, status=status.HTTP_200_OK)
