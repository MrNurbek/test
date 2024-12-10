from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from api.exam.serializers import ExamSerializer
from apps.exam.models import Exam


class CreateExamView(CreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminUser]
