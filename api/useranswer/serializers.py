from rest_framework import serializers
from apps.testbase.models import Test
from apps.useranswer.models import UserAnswer


class UserAnswerSerializer(serializers.ModelSerializer):
    # test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all(), required=True)
    # select_answer = serializers.IntegerField(required=True)
    class Meta:
        model = UserAnswer
        fields = ['test', 'selected_answer', 'is_correct']
