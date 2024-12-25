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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Foydalanuvchini ro'yxatdan o'tkazish va JWT token olish.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password', 'password_confirm'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Foydalanuvchi nomi'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email',
                                        description='Foydalanuvchi elektron pochtasi'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Foydalanuvchi paroli'),
                'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, description='Parolni tasdiqlash')
            },
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Foydalanuvchi ID'),
                            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Foydalanuvchi nomi'),
                            'email': openapi.Schema(type=openapi.TYPE_STRING,
                                                    description='Foydalanuvchi elektron pochtasi')
                        }
                    ),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Xatolik haqida ma\'lumot')
                }
            )
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Foydalanuvchi login qiladi va JWT token oladi. Username yoki Email ishlatish mumkin.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['password'],
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Foydalanuvchi nomi (majburiy emas)'
                ),
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Foydalanuvchi elektron pochtasi (majburiy emas)'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Foydalanuvchi paroli'
                ),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='JWT access token'
                    ),
                    'refresh': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='JWT refresh token'
                    ),
                    'role': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Foydalanuvchi roli'
                    ),
                },
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Xato ma\'lumotlar'
                    ),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(APIView):
    @swagger_auto_schema(
        operation_summary="Foydalanuvchi imtihon natijalari",
        operation_description="Foydalanuvchi tanlangan imtihon bo'yicha barcha urinishlari va javoblari haqida ma'lumot oladi.",
        manual_parameters=[
            openapi.Parameter(
                name='exam_id',
                in_=openapi.IN_PATH,
                required=True,
                type=openapi.TYPE_INTEGER,
                description='Imtihon identifikatori'
            )
        ],
        responses={
            200: openapi.Response(
                description='Foydalanuvchi imtihon natijalari.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'exam': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Imtihon kategoriyasi nomi'
                        ),
                        'attempts': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'attempt_number': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Urinish raqami'
                                    ),
                                    'score': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='To‘plangan ball'
                                    ),
                                    'status': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='Urinish holati'
                                    ),
                                    'answers': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Items(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'question': openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    description='Savol matni'
                                                ),
                                                'selected_answer': openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    description='Tanlangan javob'
                                                ),
                                                'correct_answer': openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    description='To‘g‘ri javob'
                                                ),
                                                'is_correct': openapi.Schema(
                                                    type=openapi.TYPE_BOOLEAN,
                                                    description='Javob to‘g‘riligini ko‘rsatadi'
                                                )
                                            }
                                        ),
                                        description='Javoblar roʻyxati'
                                    )
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='Foydalanuvchi uchun imtihon topilmadi.',
                examples={"application/json": {"error": "Exam not found."}}
            )
        },
        security=[{'Bearer': []}]
    )
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
