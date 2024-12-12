from datetime import timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from api.examattempt.serializers import ExamResultSerializer
from api.test.serializers import TestSerializer
from apps.exam.models import Exam
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test
from apps.useranswer.models import UserAnswer
from apps.userexam.models import UserExam
from django.utils import timezone
from django.shortcuts import get_object_or_404
import random


# class StartExamView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, exam_id):
#         exam = get_object_or_404(Exam, id=exam_id)
#         print(exam.start_time,'exam.start_time')
#         print(timezone.now(),'timezone.now')
#         print(exam.end_time,'exam.end_time')
#         if not (exam.start_time <= timezone.now() <= exam.end_time):
#             return Response({"error": "Exam is not active."}, status=status.HTTP_400_BAD_REQUEST)
#
#         user_exam, _ = UserExam.objects.get_or_create(user=request.user, exam=exam)
#
#         completed_attempts = user_exam.attempts.filter(status='completed').count()
#         if completed_attempts >= 3:
#             return Response({"error": "No attempts remaining for this exam."}, status=status.HTTP_400_BAD_REQUEST)
#
#         ongoing_attempt = user_exam.attempts.filter(status='started').first()
#         if ongoing_attempt:
#             return self._response(ongoing_attempt, "Exam already started.")
#
#         random_tests = self._get_random_tests(exam)
#         if not random_tests:
#             return Response({"error": "No tests available for the selected topics."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         new_attempt = ExamAttempt.objects.create(
#             user_exam=user_exam,
#             attempt_number=completed_attempts + 1,
#         )
#         new_attempt.tests.set(random_tests)
#
#         return self._response(new_attempt, "New attempt started.")
#
#     def _get_random_tests(self, exam):
#         all_tests = []
#         topics = exam.topics.all()
#         for topic in topics:
#             topic_tests = list(Test.objects.filter(topic=topic))
#             if not topic_tests:
#                 continue
#
#             num_questions = min(len(topic_tests), exam.total_questions // len(topics))
#             random_tests = random.sample(topic_tests, num_questions)
#             all_tests.extend(random_tests)
#
#         random.shuffle(all_tests)
#         return all_tests
#
#     def _response(self, attempt, message):
#         return Response({
#             "message": message,
#             "attempt_id": attempt.id,
#             "tests": TestSerializer(attempt.tests.all(), many=True).data
#         }, status=status.HTTP_200_OK)



class StartExamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        current_time = timezone.now()

        if not self._is_exam_active(exam, current_time):
            return Response({"error": "Imtixon faol emas."}, status=400)

        user_exam, _ = UserExam.objects.get_or_create(user=request.user, exam=exam)
        self._complete_expired_attempts(user_exam, exam)

        if user_exam.attempts.filter(status='completed').count() >= 3:
            return Response({"error": "Sizda boshqa urinishlar qolmadi."}, status=400)

        ongoing_attempt = user_exam.attempts.filter(status='started').first()
        if ongoing_attempt:
            return self._response(ongoing_attempt, "Imtixon allaqachon boshlangan.")

        random_tests = self._get_random_tests_with_answers(exam)
        if not random_tests:
            return Response({"error": "Tanlangan mavzular uchun savollar mavjud emas."}, status=400)

        new_attempt = ExamAttempt.objects.create(
            user_exam=user_exam, attempt_number=user_exam.attempts.count() + 1
        )
        new_attempt.tests.set([test["test"] for test in random_tests])

        return self._response(new_attempt, "Yangi urinish boshlandi.", random_tests)

    def _is_exam_active(self, exam, current_time):
        return exam.start_time <= current_time <= exam.end_time

    def _complete_expired_attempts(self, user_exam, exam):
        ongoing_attempt = user_exam.attempts.filter(status='started').first()
        if not ongoing_attempt:
            return

        expired = timezone.now() > ongoing_attempt.started_at + timedelta(minutes=exam.time_limit)
        if expired or timezone.now() > exam.end_time:
            ongoing_attempt.status = "completed"
            ongoing_attempt.completed_at = timezone.now()
            ongoing_attempt.save()

    def _get_random_tests_with_answers(self, exam):
        all_tests = []
        topics = exam.topics.all()
        for topic in topics:
            topic_tests = list(Test.objects.filter(topic=topic))
            if not topic_tests:
                continue

            num_questions = min(len(topic_tests), exam.total_questions // len(topics))
            selected_tests = random.sample(topic_tests, num_questions)

            for test in selected_tests:
                all_tests.append({
                    "test": test,
                    "randomized_answers": test.get_randomized_answers()
                })

        random.shuffle(all_tests)
        return all_tests

    def _response(self, attempt, message, random_tests):
        return Response({
            "message": message,
            "attempt_id": attempt.id,
            "tests": [
                {
                    "id": test_data["test"].id,
                    "question": test_data["test"].question,
                    "answers": [{"id": ans.id, "text": ans.text, "is_correct": ans.is_correct} for ans in test_data["randomized_answers"]]
                }
                for test_data in random_tests
            ],
        }, status=200)



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
