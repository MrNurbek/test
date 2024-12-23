from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from api.exam.serializers import ExamSerializer
from apps.exam.models import Exam
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CreateExamView(CreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_summary="Yangi imtihon yaratish",
        operation_description="Admin foydalanuvchilar yangi imtihon yaratishlari mumkin.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['category', 'topics', 'start_time', 'end_time', 'total_questions', 'time_limit'],
            properties={
                'category': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Kategoriya identifikatori'
                ),
                'topics': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='Mavzular ro‘yxati (IDlar)'
                ),
                'start_time': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='date-time',
                    description='Imtihon boshlanish vaqti (Format: YYYY-MM-DD HH:MM:SS)'
                ),
                'end_time': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='date-time',
                    description='Imtihon tugash vaqti (Format: YYYY-MM-DD HH:MM:SS)'
                ),
                'total_questions': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Umumiy savollar soni'
                ),
                'time_limit': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Imtihon vaqti (daqiqalarda)'
                )
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Imtihon identifikatori'),
                    'category': openapi.Schema(type=openapi.TYPE_INTEGER, description='Kategoriya identifikatori'),
                    'topics': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_INTEGER),
                        description='Mavzular ro‘yxati'
                    ),
                    'start_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Boshlanish vaqti'),
                    'end_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Tugash vaqti'),
                    'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER, description='Savollar soni'),
                    'time_limit': openapi.Schema(type=openapi.TYPE_INTEGER, description='Imtihon vaqti')
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Xato haqida ma\'lumot')
                }
            ),
            403: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Ruxsat etilmagan foydalanuvchi.')
                }
            )
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

