from rest_framework import serializers
from api.examattempt.serializers import AttemptDetailSerializer
from api.useranswer.serializers import UserAnswerSerializer
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Answer, Test
from apps.userexam.models import UserExam
import random


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


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text']


class TestSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ['id', 'question', 'answers']

    def get_answers(self, obj):
        answers = obj.answers.all()
        randomized_answers = list(answers)
        random.shuffle(randomized_answers)
        return AnswerSerializer(randomized_answers, many=True).data


class StartExamSerializer(serializers.ModelSerializer):
    tests = TestSerializer(many=True)

    class Meta:
        model = ExamAttempt
        fields = ['id', 'status', 'tests']
