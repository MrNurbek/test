from datetime import timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test, Answer
from apps.useranswer.models import UserAnswer
from django.shortcuts import get_object_or_404
from django.utils.timezone import now


class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        exam_attempt = get_object_or_404(ExamAttempt, id=attempt_id, user_exam__user=request.user)

        if exam_attempt.status == 'completed':
            return Response({"error": "Exam is already completed."}, status=status.HTTP_400_BAD_REQUEST)

        if now() > exam_attempt.started_at + timedelta(minutes=exam_attempt.user_exam.exam.time_limit):
            exam_attempt.status = 'completed'
            exam_attempt.save()
            return Response({"error": "Exam time has expired."}, status=status.HTTP_400_BAD_REQUEST)

        test_id = request.data.get('test_id')
        selected_answer_id = request.data.get('selected_answer_id')

        if not test_id or not selected_answer_id:
            return Response({"error": "Both 'test_id' and 'selected_answer_id' are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        test = get_object_or_404(Test, id=test_id)

        if test not in exam_attempt.tests.all():
            valid_test_ids = [test.id for test in exam_attempt.tests.all()]
            return Response({
                "error": f"Test ID {test_id} is not linked to this exam attempt. Valid test IDs: {valid_test_ids}"
            }, status=status.HTTP_400_BAD_REQUEST)

        selected_answer = get_object_or_404(Answer, id=selected_answer_id, test=test)

        user_answer, created = UserAnswer.objects.update_or_create(
            exam_attempt=exam_attempt,
            test=test,
            defaults={
                'selected_answer': selected_answer.text,
                'is_correct': selected_answer.is_correct
            }
        )

        return Response({
            "message": "Answer submitted successfully.",
            "updated": not created
        }, status=status.HTTP_200_OK)













#
# class SubmitAnswerView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request, attempt_id):
#         try:
#             exam_attempt = get_object_or_404(ExamAttempt, id=attempt_id, user_exam__user=request.user)
#             if exam_attempt.status == 'completed':
#                 return Response({"error": "Exam is already completed."}, status=status.HTTP_400_BAD_REQUEST)
#
#             if timezone.now() > exam_attempt.started_at + timedelta(minutes=exam_attempt.user_exam.exam.time_limit):
#                 exam_attempt.status = 'completed'
#                 exam_attempt.save()
#                 return Response({"error": "Exam time has expired."}, status=status.HTTP_400_BAD_REQUEST)
#             test_id = request.data.get('test_id')
#             selected_answer_id = request.data.get('selected_answer_id')
#
#             if not test_id or not selected_answer_id:
#                 return Response({"error": "Both 'test_id' and 'selected_answer_id' are required."},
#                                 status=status.HTTP_400_BAD_REQUEST)
#             test = get_object_or_404(Test, id=test_id)
#             if test not in exam_attempt.tests.all():
#                 raise ValueError(f"Test ID {test_id} is not linked to ExamAttempt {exam_attempt.id}")
#
#             selected_answer = get_object_or_404(Answer, id=selected_answer_id, test=test)
#             user_answer, created = UserAnswer.objects.update_or_create(
#                 exam_attempt=exam_attempt,
#                 test=test,
#                 defaults={
#                     'selected_answer': selected_answer.text,
#                     'is_correct': selected_answer.is_correct
#                 }
#             )
#             return Response({
#                 "message": "Answer submitted successfully.",
#                 "updated": not created
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
