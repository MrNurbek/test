from rest_framework import serializers

from api.examattempt.serializers import AttemptDetailSerializer
from api.useranswer.serializers import UserAnswerSerializer
from apps.userexam.models import UserExam


class UserExamSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = UserExam
        fields = ['id', 'exam', 'status', 'score', 'answers']



class UserExam0Serializer(serializers.ModelSerializer):
    attempts = AttemptDetailSerializer(many=True)

    class Meta:
        model = UserExam
        fields = ['exam', 'attempts']