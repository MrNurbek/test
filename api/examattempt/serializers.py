from rest_framework import serializers

from apps.examattempt.models import ExamAttempt


class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id', 'score', 'status', 'completed_at']



class AttemptDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id', 'attempt_number', 'score', 'status', 'completed_at']