from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from api.exam.serializers import ExamSerializer
from apps.exam.models import Exam
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics
from django.utils import timezone

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





class ExamListView(generics.ListAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Faol imtihonlar ro'yxati (tugash vaqti kelmagan).",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token orqali autentifikatsiya',
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Imtihon ID'),
                        'category': openapi.Schema(type=openapi.TYPE_STRING, description='Imtihon kategoriyasi'),
                        'topics': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_INTEGER),
                            description='Bog‘langan mavzular IDlari'
                        ),
                        'start_time': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description='Imtihon boshlanish vaqti'
                        ),
                        'end_time': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description='Imtihon tugash vaqti'
                        ),
                        'total_questions': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Umumiy savollar soni'
                        ),
                        'time_limit': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Vaqt chegarasi (daqiqalarda)'
                        )
                    }
                )
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Autentifikatsiya ma\'lumotlari yetishmayapti.'
                    )
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Exam.objects.filter(
            end_time__gt=timezone.now()
        ).order_by('start_time')
