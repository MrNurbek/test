
from django.contrib import admin
from django.urls import path


from api.userapi.views import RegisterView, LoginView, UserProfileView
from api.exam.views import CreateExamView
from api.testupload.views import NewTestUploadView
from api.useranswer.views import SubmitAnswerView
from api.userexam.views import StartExamView, CompleteExamView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('upload-tests/', NewTestUploadView.as_view(), name='upload-tests'),
    path('create-exam/', CreateExamView.as_view(), name='create-exam'),
    path('start-exam/<int:exam_id>/', StartExamView.as_view(), name='start-exam'),
    path('submit-answer/<int:attempt_id>/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('complete-exam/<int:attempt_id>/', CompleteExamView.as_view(), name='complete-exam'),
    path('profile/<int:exam_id>/', UserProfileView.as_view(), name='user-profile'),
]
