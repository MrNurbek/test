from django.db import models
from apps.category.models import Category
from apps.testbase.models import Topic
from datetime import time


class Exam(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='exams')
    topics = models.ManyToManyField(Topic, related_name='exams')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_questions = models.IntegerField()
    time_limit = models.TimeField(help_text="Time limit for the exam in HH:MM:SS format", null=True, blank=True,default=time(0, 30, 0))

    def __str__(self):
        return f"Exam: {self.category.name} ({self.start_time} - {self.end_time} - id={self.id})"
