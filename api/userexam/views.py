from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from api.examattempt.serializers import ExamResultSerializer
from api.test.serializers import TestSerializer
from api.userexam.filters import get_random_tests, get_exam_result
from apps.exam.models import Exam
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test
from apps.useranswer.models import UserAnswer
from apps.userexam.models import UserExam
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
import random


class StartExamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)

        if not (exam.start_time <= timezone.now() <= exam.end_time):
            return Response({"error": "Exam is not active."}, status=status.HTTP_400_BAD_REQUEST)

        user_exam, _ = UserExam.objects.get_or_create(user=request.user, exam=exam)

        completed_attempts = user_exam.attempts.filter(status='completed').count()
        if completed_attempts >= 3:
            return Response({"error": "No attempts remaining for this exam."}, status=status.HTTP_400_BAD_REQUEST)

        ongoing_attempt = user_exam.attempts.filter(status='started').first()
        if ongoing_attempt:
            return self._response(ongoing_attempt, "Exam already started.")

        random_tests = self._get_random_tests(exam)
        if not random_tests:
            return Response({"error": "No tests available for the selected topics."},
                            status=status.HTTP_400_BAD_REQUEST)

        new_attempt = ExamAttempt.objects.create(
            user_exam=user_exam,
            attempt_number=completed_attempts + 1,
        )
        new_attempt.tests.set(random_tests)

        return self._response(new_attempt, "New attempt started.")

    def _get_random_tests(self, exam):
        all_tests = []
        topics = exam.topics.all()
        for topic in topics:
            topic_tests = list(Test.objects.filter(topic=topic))
            if not topic_tests:
                continue

            num_questions = min(len(topic_tests), exam.total_questions // len(topics))
            random_tests = random.sample(topic_tests, num_questions)
            all_tests.extend(random_tests)

        random.shuffle(all_tests)
        return all_tests

    def _response(self, attempt, message):
        return Response({
            "message": message,
            "attempt_id": attempt.id,
            "tests": TestSerializer(attempt.tests.all(), many=True).data
        }, status=status.HTTP_200_OK)

class CompleteExamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        # ExamAttempt obyektini olish
        exam_attempt = get_object_or_404(
            ExamAttempt.objects.prefetch_related(
                Prefetch('tests'),
                Prefetch('answers', queryset=UserAnswer.objects.select_related('test'))
            ),
            id=attempt_id,
            user_exam__user=request.user
        )

        # Imtihon holatini tekshirish
        if exam_attempt.status == 'completed':
            return Response({"error": "This exam attempt is already completed."}, status=400)

        # Imtihon natijalarini hisoblash
        result_data = self.get_exam_result(exam_attempt)

        # ExamAttempt holatini yangilash
        exam_attempt.score = result_data['correct_answers']
        exam_attempt.status = 'completed'
        exam_attempt.completed_at = timezone.now()
        exam_attempt.save()

        # Javobni qaytarish
        result = {
            "exam_attempt": ExamResultSerializer(exam_attempt).data,
            "result": result_data
        }
        return Response(result, status=200)

    def get_exam_result(self, exam_attempt):
        """
        Imtihon natijalarini hisoblash funksiyasi.
        """
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
