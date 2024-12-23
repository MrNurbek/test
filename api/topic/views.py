from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from api.topic.filters import TopicFilter
from api.topic.serializers import TopicSerializer
from apps.testbase.models import Topic
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class TopicListAPIView(ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TopicFilter

    @swagger_auto_schema(
        operation_summary="Mavzular ro'yxati",
        operation_description="Barcha mavzular ro'yxatini olish va kategoriya bo'yicha filterlash uchun API.",
        manual_parameters=[
            openapi.Parameter(
                name='category',
                in_=openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_INTEGER,
                description='Kategoriya identifikatori bo\'yicha filtrlash'
            )
        ],
        responses={
            200: openapi.Response(
                description="Mavzular ro'yxati",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='Mavzu identifikatori'
                            ),
                            'name': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='Mavzu nomi'
                            ),
                            'category': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Kategoriya identifikatori'
                                    ),
                                    'name': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='Kategoriya nomi'
                                    )
                                }
                            )
                        }
                    )
                )
            ),
            400: openapi.Response(
                description="Noto'g'ri so'rov parametrlari.",
                examples={"application/json": {"error": "Invalid query parameters."}}
            )
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
