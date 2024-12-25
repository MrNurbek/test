from api.category.views import CategoryListAPIView
from api.topic.views import TopicListAPIView
from api.userapi.views import RegisterView, LoginView, UserProfileView
from api.exam.views import CreateExamView, ExamListView
from api.testupload.views import NewTestUploadView
from api.useranswer.views import SubmitAnswerView
from api.userexam.views import StartExamView, CompleteExamView, UserExamListView
from core import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Django API Documentation",
        default_version='v1',
        description="API hujjatlari uchun Swagger interfeysi",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
                  path('admin/', admin.site.urls),
                  re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
                          name='schema-json'),
                  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
                  path('register/', RegisterView.as_view(), name='register'),
                  path('login/', LoginView.as_view(), name='login'),
                  path('upload-tests/', NewTestUploadView.as_view(), name='upload-tests'),
                  path('create-exam/', CreateExamView.as_view(), name='create-exam'),
                  path('exams/', ExamListView.as_view(), name='exam-list'),
                  path('start-exam/<int:exam_id>/', StartExamView.as_view(), name='start-exam'),
                  path('submit-answer/<int:attempt_id>/', SubmitAnswerView.as_view(), name='submit-answer'),
                  path('complete-exam/<int:attempt_id>/', CompleteExamView.as_view(), name='complete-exam'),
                  path('user-exams/', UserExamListView.as_view(), name='user-exam-list'),
                  path('profile/<int:exam_id>/', UserProfileView.as_view(), name='user-profile'),
                  path('categories/', CategoryListAPIView.as_view(), name='category-list'),
                  path('topics/', TopicListAPIView.as_view(), name='topic-list'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
