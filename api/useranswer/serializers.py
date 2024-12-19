from rest_framework import serializers
from apps.testbase.models import Test, Answer
from apps.useranswer.models import UserAnswer


class UserAnswerSerializer(serializers.ModelSerializer):
    # test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all(), required=True)
    # select_answer = serializers.IntegerField(required=True)
    class Meta:
        model = UserAnswer
        fields = ['test', 'selected_answer', 'is_correct']




class SubmitAnswerSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    selected_answer_id = serializers.IntegerField()

    def validate(self, data):
        exam_attempt = self.context['exam_attempt']
        test_id = data['test_id']
        selected_answer_id = data['selected_answer_id']

        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            raise serializers.ValidationError(f"Test ID {test_id} does not exist.")

        if test not in exam_attempt.tests.all():
            raise serializers.ValidationError(f"Test ID {test_id} is not linked to this exam attempt.")

        try:
            answer = Answer.objects.get(id=selected_answer_id, test=test)
        except Answer.DoesNotExist:
            raise serializers.ValidationError(f"Answer ID {selected_answer_id} does not exist for Test ID {test_id}.")

        data['test'] = test
        data['answer'] = answer
        return data

    def create(self, validated_data):
        exam_attempt = self.context['exam_attempt']
        test = validated_data['test']
        answer = validated_data['answer']

        user_answer, _ = UserAnswer.objects.update_or_create(
            exam_attempt=exam_attempt,
            test=test,
            defaults={
                'selected_answer': answer.text,
                'is_correct': answer.is_correct
            }
        )
        return user_answer