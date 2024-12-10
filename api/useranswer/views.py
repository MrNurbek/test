from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test
from apps.useranswer.models import UserAnswer
from django.shortcuts import get_object_or_404


class SubmitAnswerView(APIView):
    def post(self, request, attempt_id):
        exam_attempt = get_object_or_404(ExamAttempt, id=attempt_id, user_exam__user=request.user)

        if exam_attempt.status == 'completed' or timezone.now() > exam_attempt.user_exam.exam.end_time:
            exam_attempt.status = 'completed'
            exam_attempt.save()
            return Response({"error": "Exam is already completed or expired."}, status=status.HTTP_400_BAD_REQUEST)

        test = get_object_or_404(Test, id=request.data.get('test_id'), exam_attempts=exam_attempt)
        user_answer, created = UserAnswer.objects.update_or_create(
            exam_attempt=exam_attempt,
            test=test,
            defaults={
                'selected_answer': request.data.get('selected_answer'),
                'is_correct': request.data.get('selected_answer') == test.correct_answer
            }
        )

        return Response({"message": "Answer submitted.", "updated": not created})
