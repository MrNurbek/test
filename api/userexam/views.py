from datetime import timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from api.examattempt.serializers import ExamResultSerializer
from api.test.serializers import TestSerializer
from api.userexam.filters import get_random_tests, get_random_tests_with_answers
from apps.exam.models import Exam
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test
from apps.useranswer.models import UserAnswer
from apps.userexam.models import UserExam
from django.utils import timezone
from django.shortcuts import get_object_or_404
import random


class StartExamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        user = request.user

        user_exam, created = UserExam.objects.get_or_create(
            user=user,
            exam=exam,
            defaults={'attempt_count': 0, 'status': 'started'}
        )

        if user_exam.attempt_count >= 3:
            return Response({
                'error': 'Maximum attempts reached for this exam.'
            }, status=status.HTTP_403_FORBIDDEN)

        if user_exam.status == 'completed':
            user_exam.attempt_count += 1
            user_exam.status = 'started'
            user_exam.tests.clear()
            user_exam.save()

        if not user_exam.tests.exists():
            relevant_tests = list(Test.objects.filter(topic__in=exam.topics.all()))
            tests = random.sample(relevant_tests, min(exam.total_questions, len(relevant_tests)))
            user_exam.tests.set(tests)
            user_exam.save()

        exam_attempt, attempt_created = ExamAttempt.objects.get_or_create(
            user_exam=user_exam,
            attempt_number=user_exam.attempt_count,
            defaults={'status': 'started'}
        )
        if not exam_attempt.tests.exists():
            exam_attempt.tests.set(user_exam.tests.all())
            exam_attempt.save()
        response_data = []
        for test in user_exam.tests.all():
            answers = list(test.answers.all())
            random.shuffle(answers)

            response_data.append({
                'id': test.id,
                'question': test.question,
                'answers': [
                    {
                        'id': answer.id,
                        'text': answer.text
                    }
                    for answer in answers
                ]
            })
        random.shuffle(response_data)
        return Response({
            'exam_id': exam.id,
            'exam_status': user_exam.status,
            'attempt_id': exam_attempt.id,
            'tests': response_data
        })


class CompleteExamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        exam_attempt = get_object_or_404(
            ExamAttempt.objects.prefetch_related(
                Prefetch('tests'),
                Prefetch('answers', queryset=UserAnswer.objects.select_related('test'))
            ),
            id=attempt_id,
            user_exam__user=request.user
        )
        if exam_attempt.status == 'completed':
            return Response({"error": "This exam attempt is already completed."}, status=400)
        result_data = self.get_exam_result(exam_attempt)
        exam_attempt.score = result_data['correct_answers']
        exam_attempt.status = 'completed'
        exam_attempt.completed_at = timezone.now()
        exam_attempt.save()
        user_exam = exam_attempt.user_exam
        if not user_exam.attempts.filter(status='started').exists():
            user_exam.status = 'completed'
            user_exam.save()
        result = {
            "exam_attempt": ExamResultSerializer(exam_attempt).data,
            "result": result_data
        }
        return Response(result, status=200)

    def get_exam_result(self, exam_attempt):
        correct_answers = 0
        total_questions = exam_attempt.tests.count()
        answers_data = []
        for test in exam_attempt.tests.all():
            user_answer = exam_attempt.answers.filter(test=test).first()
            is_correct = user_answer.is_correct if user_answer else False
            correct_answers += is_correct

            answers_data.append({
                "question": test.question,
                "selected_answer": user_answer.selected_answer if user_answer else None,
                "is_correct": is_correct
            })

        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "wrong_answers": total_questions - correct_answers,
            "answers": answers_data
        }
