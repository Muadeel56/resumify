from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors
            first_error = next(iter(errors.values()))[0]
            return Response({'error': str(first_error)}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'message': 'Account created successfully.'}, status=status.HTTP_201_CREATED)
