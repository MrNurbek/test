from django.db import models
from apps.category.models import Category
from apps.testbase.models import  Topic




class Exam(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='exams')
    topics = models.ManyToManyField(Topic, related_name='exams')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_questions = models.IntegerField()
    time_limit = models.IntegerField(help_text="Time limit for the exam in minutes", null=True, blank=True)

    def __str__(self):
        return f"Exam: {self.category.name} ({self.start_time} - {self.end_time} - id={self.id})"


