from rest_framework import serializers

from apps.exam.models import Exam
from apps.testbase.models import Topic





class ExamSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    topics = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d %H:%M:%S'])
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d %H:%M:%S'])

    class Meta:
        model = Exam
        fields = ['id', 'category', 'topics', 'start_time', 'end_time', 'total_questions', 'time_limit']

    def get_topics(self, obj):
        return [topic.name for topic in obj.topics.all()]

    def create(self, validated_data):
        topics = validated_data.pop('topics', [])
        exam = Exam.objects.create(**validated_data)
        exam.topics.set(topics)
        return exam




