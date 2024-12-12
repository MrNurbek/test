from django.db import models
from apps.testbase.models import Test
from apps.userexam.models import UserExam


class ExamAttempt(models.Model):
    user_exam = models.ForeignKey(UserExam, on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=(('started', 'Started'), ('completed', 'Completed')), default='started')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    tests = models.ManyToManyField(Test, related_name='exam_attempts')
    score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Attempt {self.attempt_number} for {self.user_exam.exam.category.name}-{self.started_at} - {self.completed_at} -{self.id}"
