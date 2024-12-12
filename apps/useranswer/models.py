

from django.db import models
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test, Answer

#
# class UserAnswer(models.Model):
#     exam_attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers',null=True)
#     test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='user_answers')
#     selected_answer = models.CharField(max_length=1255, null=True, blank=True)
#     started_at = models.DateTimeField(auto_now_add=True,null=True)
#     is_correct = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f"id-{self.id} - Test-{self.test.id} -- {self.test.question} "





class UserAnswer(models.Model):
    exam_attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="answers")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="user_answers")
    selected_answer = models.CharField(max_length=1255, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    randomized_answers = models.ManyToManyField(Answer, related_name="randomized_answers")
    started_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"id-{self.id} - {self.test.question}"
