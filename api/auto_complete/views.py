from datetime import timedelta
from django.utils.timezone import now
from django.db import transaction
from apps.examattempt.models import ExamAttempt
from django.http import JsonResponse




def auto_complete_exams():
    expired_attempts = ExamAttempt.objects.filter(
        status='started',
        started_at__isnull=False,
        user_exam__exam__time_limit__isnull=False
    ).select_related('user_exam', 'user_exam__exam')

    for exam_attempt in expired_attempts:
        time_limit = exam_attempt.user_exam.exam.time_limit

        # To'g'ridan-to'g'ri timedelta qiymatidan foydalanish
        if isinstance(time_limit, timedelta):
            expiration_time = exam_attempt.started_at + time_limit
        elif isinstance(time_limit, (int, float)):
            expiration_time = exam_attempt.started_at + timedelta(minutes=time_limit)
        elif isinstance(time_limit, str):
            try:
                h, m, s = map(int, time_limit.split(':'))
                expiration_time = exam_attempt.started_at + timedelta(hours=h, minutes=m, seconds=s)
            except ValueError:
                raise ValueError(f"Invalid string format for time_limit: {time_limit}")
        else:
            raise TypeError(f"Unsupported time_limit type: {type(time_limit)}")

        print("Started at:", exam_attempt.started_at)
        print("Time limit:", time_limit)
        print("Expiration time:", expiration_time)

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


def some_view(request):
    auto_complete_exams()
    return JsonResponse({"message": "Hello, World!"})
