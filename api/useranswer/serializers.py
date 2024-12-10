from rest_framework import serializers

from apps.useranswer.models import UserAnswer


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['test', 'selected_answer', 'is_correct']