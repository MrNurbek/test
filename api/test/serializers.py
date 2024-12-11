from rest_framework import serializers

from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test, Answer


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'category', 'topic', 'question', 'answers']





class AnswerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']

class AttemptDetailsSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = ExamAttempt
        fields = ['attempt_number', 'score', 'status', 'answers']

    def get_answers(self, obj):
        return [
            {
                "question": test.question,
                "selected_answer": self.get_selected_answer(obj, test),
                "correct_answer": self.get_correct_answer(test),
                "is_correct": self.get_is_correct(obj, test)
            }
            for test in obj.tests.all()
        ]

    def get_selected_answer(self, obj, test):
        answer = obj.answers.filter(test=test).first()
        return answer.selected_answer if answer else None

    def get_correct_answer(self, test):
        correct_answer = test.answers.filter(is_correct=True).first()
        return correct_answer.text if correct_answer else None

    def get_is_correct(self, obj, test):
        answer = obj.answers.filter(test=test).first()
        return answer.is_correct if answer else False
