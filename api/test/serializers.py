from rest_framework import serializers

from apps.testbase.models import Test





class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'category', 'topic', 'question', 'answers']
