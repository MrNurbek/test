from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from docx import Document
from apps.category.models import Category
from apps.testbase.models import Topic, Test, Answer


class NewTestUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            return Response({"error": "Only admins can upload tests."}, status=status.HTTP_403_FORBIDDEN)

        category_id = request.data.get('category_id')
        topic_name = request.data.get('topic_name')
        file = request.FILES.get('file')

        if not file or not category_id or not topic_name:
            return Response({"error": "Category ID, topic name, and file are required."}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(Category, id=category_id)
        topic, _ = Topic.objects.get_or_create(name=topic_name)

        try:
            content = file.read().decode('utf-8')
            tests = self.parse_txt(content)
        except Exception as e:
            return Response({"error": f"Failed to process the file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        for test_data in tests:
            test = Test.objects.create(
                category=category,
                topic=topic,
                question=test_data['question']
            )
            for answer in test_data['answers']:
                Answer.objects.create(
                    test=test,
                    text=answer['text'],
                    is_correct=answer['is_correct']
                )

        return Response({"message": "Tests successfully uploaded."}, status=status.HTTP_201_CREATED)

    def parse_txt(self, content):
        tests = []
        lines = [line.strip() for line in content.splitlines() if line.strip()]

        if not lines:
            raise ValueError("The file appears to be empty or incorrectly formatted.")

        i = 0
        while i < len(lines):
            question = lines[i]
            answers = lines[i + 1:i + 5]

            if len(answers) != 4:
                raise ValueError(f"Question at line {i + 1} does not have exactly 4 answers. Found: {len(answers)}")

            tests.append({
                'question': question,
                'answers': [
                    {'text': answers[0], 'is_correct': True},
                    {'text': answers[1], 'is_correct': False},
                    {'text': answers[2], 'is_correct': False},
                    {'text': answers[3], 'is_correct': False}
                ]
            })
            i += 5

        return tests



