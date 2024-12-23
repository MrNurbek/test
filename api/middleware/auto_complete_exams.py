from datetime import timedelta
from django.utils.timezone import now
from django.db import transaction
from apps.examattempt.models import ExamAttempt

class AutoCompleteExamsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        self.auto_complete_exams()


        response = self.get_response(request)

        return response

    def auto_complete_exams(self):

        expired_attempts = ExamAttempt.objects.filter(
            status='started',
            started_at__isnull=False,
            user_exam__exam__time_limit__isnull=False
        ).select_related('user_exam', 'user_exam__exam')

        for exam_attempt in expired_attempts:
            time_limit = exam_attempt.user_exam.exam.time_limit
            expiration_time = exam_attempt.started_at + timedelta(minutes=time_limit)

            if now() > expiration_time:
                with transaction.atomic():
                    correct_answers = 0
                    for test in exam_attempt.tests.all():
                        user_answer = exam_attempt.answers.filter(test=test).first()
                        if user_answer and user_answer.is_correct:
                            correct_answers += 1

                    exam_attempt.score = correct_answers
                    exam_attempt.status = 'completed'
                    exam_attempt.completed_at = now()
                    exam_attempt.save()

                    user_exam = exam_attempt.user_exam
                    if not user_exam.attempts.filter(status='started').exists():
                        user_exam.status = 'completed'
                        user_exam.save()

                    print(f"ExamAttempt {exam_attempt.id} completed automatically.")
