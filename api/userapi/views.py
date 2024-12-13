from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Prefetch
from api.test.serializers import AttemptDetailsSerializer
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
        attempts_data = AttemptDetailsSerializer(user_exam.attempts.all(), many=True).data

        return Response({
            "exam": user_exam.exam.category.name,
            "attempts": attempts_data
        }, status=status.HTTP_200_OK)

















# class UserProfileView(APIView):
#     def get(self, request, exam_id):
#         user_exam = get_object_or_404(
#             UserExam.objects.prefetch_related(
#                 Prefetch('attempts__tests'),
#                 Prefetch('attempts__answers')
#             ),
#             user=request.user,
#             exam_id=exam_id
#         )
#
#         attempts_data = [self.get_attempt_details(attempt) for attempt in user_exam.attempts.all()]
#
#         return Response({
#             "exam": user_exam.exam.category.name,
#             "attempts": attempts_data
#         }, status=200)
#
#     def get_attempt_details(self, attempt):
#         assigned_tests = attempt.tests.all()
#         user_answers = {
#             answer.test_id: answer for answer in attempt.answers.all()
#         }
#
#         answers_data = []
#         correct_count = 0
#
#         for test in assigned_tests:
#             user_answer = user_answers.get(test.id)
#             selected_answer_text = user_answer.selected_answer if user_answer else None
#             correct_answer_text = next((answer.text for answer in test.answers.all() if answer.is_correct), None)
#             is_correct = user_answer.is_correct if user_answer else False
#
#             if is_correct:
#                 correct_count += 1
#
#             answers_data.append({
#                 "question": test.question,
#                 "selected_answer": selected_answer_text,
#                 "correct_answer": correct_answer_text,
#                 "is_correct": is_correct
#             })
#
#         return {
#             "attempt_number": attempt.attempt_number,
#             "score": correct_count,
#             "total_questions": assigned_tests.count(),
#             "correct_answers": correct_count,
#             "wrong_answers": assigned_tests.count() - correct_count,
#             "answers": answers_data
#         }
