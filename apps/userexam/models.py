from django.db import models

from apps.testbase.models import Test
from apps.userapp.models import User
from apps.exam.models import Exam



class UserExam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_exams')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='user_exams')
    tests = models.ManyToManyField(Test, related_name='user_exams')
    attempt_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('started', 'Started'), ('completed', 'Completed')), default='started')
    score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(f"{self.user.username} - {self.id}")