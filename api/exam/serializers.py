from rest_framework import serializers

from apps.category.models import Category
from apps.exam.models import Exam
from apps.testbase.models import Topic





class ExamSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    category_name = serializers.SerializerMethodField()
    topics = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(), many=True
    )
    start_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d %H:%M:%S']
    )
    end_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d %H:%M:%S']
    )

    class Meta:
        model = Exam
        fields = [
            'id', 'category', 'category_name', 'topics',
            'start_time', 'end_time', 'total_questions', 'time_limit'
        ]

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def create(self, validated_data):
        topics = validated_data.pop('topics', [])
        exam = Exam.objects.create(**validated_data)
        exam.topics.set(topics)
        return exam



