from django.db import models

from apps.testbase.models import Test
from apps.userexam.models import UserExam



class ExamAttempt(models.Model):
    user_exam = models.ForeignKey(UserExam, on_delete=models.CASCADE, related_name='attempts')
    tests = models.ManyToManyField(Test, related_name='exam_attempts')
    attempt_number = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=(('started', 'Started'), ('completed', 'Completed')), default='started')

    def __str__(self):
        return f"Attempt {self.attempt_number} - {self.user_exam.user.username} - {self.status} - {self.id}"