from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from api.examattempt.serializers import ExamResultSerializer
from api.test.serializers import TestSerializer
from api.userexam.filters import get_random_tests, get_exam_result
from apps.exam.models import Exam
from apps.examattempt.models import ExamAttempt
from apps.userexam.models import UserExam
from django.utils import timezone
from django.shortcuts import get_object_or_404


class StartExamView(APIView):
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

        random_tests = get_random_tests(exam)
        new_attempt = ExamAttempt.objects.create(
            user_exam=user_exam,
            attempt_number=completed_attempts + 1,
        )
        new_attempt.tests.set(random_tests)

        return self._response(new_attempt, "New attempt started.")

    def _response(self, attempt, message):
        return Response({
            "message": message,
            "attempt_id": attempt.id,
            "tests": TestSerializer(attempt.tests.all(), many=True).data
        }, status=status.HTTP_200_OK)


class CompleteExamView(APIView):
    def post(self, request, attempt_id):
        exam_attempt = get_object_or_404(
            ExamAttempt.objects.prefetch_related(
                Prefetch('tests'),
                Prefetch('answers')
            ),
            id=attempt_id,
            user_exam__user=request.user
        )

        if exam_attempt.status == 'completed':
            return Response({"error": "Attempt already completed."}, status=400)

        result_data = get_exam_result(exam_attempt)
        exam_attempt.score = result_data['correct_answers']
        exam_attempt.status = 'completed'
        exam_attempt.completed_at = timezone.now()
        exam_attempt.save()
        result = {
            "exam_attempt": ExamResultSerializer(exam_attempt).data,
            "result": result_data
        }
        return Response(result, status=200)
