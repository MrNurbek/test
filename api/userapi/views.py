from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Prefetch
from api.userapi.filters import get_attempt_details
from api.userapi.serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from apps.testbase.models import Test
from apps.userexam.models import UserExam
from django.shortcuts import get_object_or_404

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




class UserProfileView(APIView):
    def get(self, request, exam_id):
        user_exam = get_object_or_404(
            UserExam.objects.prefetch_related(
                Prefetch('attempts__tests'),
                Prefetch('attempts__answers')
            ),
            user=request.user,
            exam_id=exam_id
        )
        attempts_data = [get_attempt_details(attempt) for attempt in user_exam.attempts.all()]

        return Response({
            "exam": user_exam.exam.category.name,
            "attempts": attempts_data
        })
