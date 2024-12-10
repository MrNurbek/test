from apps.exam.models import Exam
from apps.examattempt.models import ExamAttempt
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.response import Response

class AutoCompleteExpiredExamsView(APIView):
    def post(self, request):
        expired_exams = Exam.objects.filter(end_time__lt=timezone.now())
        ongoing_attempts = ExamAttempt.objects.filter(status='started', user_exam__exam__in=expired_exams)

        completed_attempts = []

        for attempt in ongoing_attempts:
            assigned_tests = attempt.tests.all()
            correct_count = 0
            answers_data = []

            for test in assigned_tests:
                user_answer = attempt.answers.filter(test=test).first()
                if user_answer:
                    is_correct = user_answer.is_correct
                    correct_count += 1 if is_correct else 0
                else:
                    is_correct = False

                answers_data.append({
                    "question": test.question,
                    "selected_answer": user_answer.selected_answer if user_answer else None,
                    "correct_answer": test.correct_answer,
                    "is_correct": is_correct
                })

            attempt.score = correct_count
            attempt.status = 'completed'
            attempt.completed_at = timezone.now()
            attempt.save()

            completed_attempts.append({
                "user": attempt.user_exam.user.username,
                "exam": attempt.user_exam.exam.category.name,
                "score": correct_count,
                "total_questions": assigned_tests.count(),
                "answers": answers_data
            })

        return Response({
            "message": "Expired exams auto-completed.",
            "completed_attempts": completed_attempts
        })