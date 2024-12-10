from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.testupload.serializers import NewTestUploadSerializer


class NewTestUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            raise PermissionDenied("You do not have permission to perform this action.")

        serializer = NewTestUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Tests successfully uploaded."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
