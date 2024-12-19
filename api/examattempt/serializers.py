from django.utils import timezone
from rest_framework import serializers
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test
from apps.useranswer.models import UserAnswer


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['id', 'selected_answer', 'is_correct']


class TestSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, source='user_answers', read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'question', 'answers']


class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id', 'attempt_number', 'score', 'status', 'completed_at']

    @staticmethod
    def calculate_and_update_result(exam_attempt):
        correct_answers = 0

        for test in exam_attempt.tests.all():
            user_answer = exam_attempt.answers.filter(test=test).first()
            if user_answer and user_answer.is_correct:
                correct_answers += 1

        exam_attempt.score = correct_answers
        exam_attempt.status = 'completed'
        exam_attempt.completed_at = timezone.now()
        return {
            "total_questions": exam_attempt.tests.count(),
            "correct_answers": correct_answers,
            "wrong_answers": exam_attempt.tests.count() - correct_answers
        }

        exam_attempt.score = correct_answers
        exam_attempt.status = 'completed'
        exam_attempt.completed_at = timezone.now()
        exam_attempt.save()

        user_exam = exam_attempt.user_exam
        if not user_exam.attempts.filter(status='started').exists():
            user_exam.status = 'completed'
            user_exam.save()

        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "wrong_answers": total_questions - correct_answers,
            "answers": answers_data
        }


class AttemptDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id', 'attempt_number', 'score', 'status', 'completed_at']
