from rest_framework import serializers
from api.category.serializers import CategorySerializer
from apps.testbase.models import Topic



class TopicSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'name', 'category']
