from django.db import models
from apps.category.models import Category
import random



class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.name} - {self.id}"

class Test(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tests')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tests',null=True)
    question = models.TextField()
    answers = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_randomized_answers(self):
        answers = self.answers.copy()
        random.shuffle(answers)
        return answers

    def __str__(self):
        return f"id={self.id} - {self.category.name} - {self.topic.name}"
