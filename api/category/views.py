from rest_framework.generics import ListAPIView
from api.category.serializers import CategorySerializer
from apps.category.models import Category
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        operation_summary="Kategoriya ro'yxati",
        operation_description="Barcha kategoriyalar ro'yxatini olish uchun API.",
        responses={
            200: openapi.Response(
                description="Kategoriya ro'yxati",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
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
                )
            )
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



