from django.db import models
from apps.category.models import Category
import random


class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics',null=True)
    def __str__(self):
        return f"{self.name} -{self.category.name} - {self.id}"


class Test(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tests')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tests', null=True)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"id={self.id} - {self.category.name} - {self.topic.name}"


class Answer(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.test.question[:30]} -{self.test.id} {'Correct' if self.is_correct else 'Incorrect'} -{self.id}"



