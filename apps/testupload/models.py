from django.db import models
from apps.category.models import Category
from apps.testbase.models import Test, Topic


class NewTestUpload(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='new_test_uploads')
    topic_name = models.CharField(max_length=200,null=True)
    json_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.process_and_save_tests()
    def process_and_save_tests(self):
        topic, created = Topic.objects.get_or_create(name=self.topic_name)
        for item in self.json_data:
            question = item.get('question')
            answers = item.get('answers')
            correct_answer = answers[0] if answers else None

            if question and answers:
                Test.objects.create(
                    category=self.category,
                    topic=topic,
                    question=question,
                    answers=answers,
                    correct_answer=correct_answer
                )


