from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from api.testupload.permission import NewTestUploadPermission
from apps.category.models import Category
from apps.testbase.models import Topic, Test, Answer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class TestFileParser:
    @staticmethod
    def parse(content):
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        tests, i = [], 0

        while i < len(lines):
            if lines[i].startswith('(S)'):
                question, i = TestFileParser._extract_block(lines, i, '(S)', '(J)')
                answers, i = TestFileParser._extract_answers(lines, i)
                if not answers:
                    raise ValueError(f"No answers found for the question: {question}")
                tests.append({'question': question, 'answers': answers})
            else:
                i += 1

        return tests

    @staticmethod
    def _extract_block(lines, start_index, block_prefix, stop_prefix):
        block, i = [lines[start_index][len(block_prefix):].strip()], start_index + 1
        while i < len(lines) and not lines[i].startswith(stop_prefix) and not lines[i].startswith('(S)'):
            block.append(lines[i].strip())
            i += 1
        return ' '.join(block), i

    @staticmethod
    def _extract_answers(lines, start_index):
        answers, i = [], start_index
        while i < len(lines) and lines[i].startswith('(J)'):
            answer_text, i = TestFileParser._extract_block(lines, i, '(J)', '(J)')
            answers.append({
                'text': answer_text,
                'is_correct': len(answers) == 0
            })
        return answers, i


class NewTestUploadView(APIView):
    permission_classes = [NewTestUploadPermission]

    @swagger_auto_schema(
        operation_description="Yangi testlarni yuklash va saqlash.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['category_id', 'topic_name', 'file'],
            properties={
                'category_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Kategoriya identifikatori'
                ),
                'topic_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Mavzu nomi'
                ),
                'file': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='binary',
                    description='Testlar saqlangan fayl (masalan, CSV yoki TXT format)'
                ),
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Testlar muvaffaqiyatli yuklandi.'
                    )
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Xatolik yuz berdi.'
                    )
                }
            ),
            403: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Sizda ushbu amalni bajarish uchun ruxsat mavjud emas.'
                    )
                }
            )
        },
        security=[{'Bearer': []}]
    )
    def post(self, request):
        category_id = request.data.get('category_id')
        topic_name = request.data.get('topic_name')
        file = request.FILES.get('file')

        if not all([file, category_id, topic_name]):
            return Response(
                {"error": "Category ID, topic name, and file are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        category = get_object_or_404(Category, id=category_id)

        topic, created = Topic.objects.get_or_create(
            name=topic_name,
            defaults={'category': category}
        )

        if not created and topic.category != category:
            topic.category = category
            topic.save()

        try:
            content = file.read().decode('utf-8')
            tests = TestFileParser.parse(content)
        except Exception as e:
            return Response({"error": f"Failed to process the file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        self._save_tests_and_answers(tests, category, topic)
        return Response({"message": "Tests successfully uploaded."}, status=status.HTTP_201_CREATED)

    def _save_tests_and_answers(self, tests, category, topic):
        for test_data in tests:
            test = Test.objects.create(category=category, topic=topic, question=test_data['question'])
            Answer.objects.bulk_create([
                Answer(test=test, text=answer['text'], is_correct=answer['is_correct'])
                for answer in test_data['answers']
            ])
# class NewTestUploadView(APIView):
#
#     permission_classes = [NewTestUploadPermission]
#
#     def post(self, request):
#         category_id = request.data.get('category_id')
#         topic_name = request.data.get('topic_name')
#         file = request.FILES.get('file')
#
#         if not all([file, category_id, topic_name]):
#             return Response(
#                 {"error": "Category ID, topic name, and file are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         category = get_object_or_404(Category, id=category_id)
#         topic, _ = Topic.objects.get_or_create(name=topic_name)
#
#         try:
#             content = file.read().decode('utf-8')
#             tests = TestFileParser.parse(content)
#         except Exception as e:
#             return Response({"error": f"Failed to process the file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
#
#         self._save_tests_and_answers(tests, category, topic)
#         return Response({"message": "Tests successfully uploaded."}, status=status.HTTP_201_CREATED)
#
#     def _save_tests_and_answers(self, tests, category, topic):
#
#         for test_data in tests:
#             test = Test.objects.create(category=category, topic=topic, question=test_data['question'])
#             Answer.objects.bulk_create([
#                 Answer(test=test, text=answer['text'], is_correct=answer['is_correct'])
#                 for answer in test_data['answers']
#             ])
#
#
#


#
# class TestFileParser:
#     @staticmethod
#     def parse(content):
#         tests, lines, i = [], [line.strip() for line in content.splitlines() if line.strip()], 0
#         while i < len(lines):
#             if lines[i].startswith('(S)'):
#                 question, i = TestFileParser._extract_block(lines, i, '(S)', '(J)')
#                 answers, i = TestFileParser._extract_answers(lines, i)
#                 if answers:
#                     tests.append({'question': question, 'answers': answers})
#                 else:
#                     raise ValueError(f"Question does not have any answers: {question}")
#             else:
#                 i += 1
#         return tests
#
#     @staticmethod
#     def _extract_block(lines, start_index, block_prefix, stop_prefix):
#         block, i = [lines[start_index][len(block_prefix):].strip()], start_index + 1
#         while i < len(lines) and not lines[i].startswith(stop_prefix) and not lines[i].startswith('(S)'):
#             block.append(lines[i].strip())
#             i += 1
#         return ' '.join(block), i
#
#     @staticmethod
#     def _extract_answers(lines, start_index):
#         answers, i = [], start_index
#         while i < len(lines) and lines[i].startswith('(J)'):
#             answer_block, i = TestFileParser._extract_block(lines, i, '(J)', '(J)')
#             answers.append({
#                 'text': answer_block,
#                 'is_correct': len(answers) == 0
#             })
#         return answers, i
#
#
# class NewTestUploadView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         if request.user.role != 'admin':
#             return Response({"error": "Only admins can upload tests."}, status=status.HTTP_403_FORBIDDEN)
#
#         category_id, topic_name, file = request.data.get('category_id'), request.data.get(
#             'topic_name'), request.FILES.get('file')
#         if not all([file, category_id, topic_name]):
#             return Response({"error": "Category ID, topic name, and file are required."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         category = get_object_or_404(Category, id=category_id)
#         topic, _ = Topic.objects.get_or_create(name=topic_name)
#
#         try:
#             content = file.read().decode('utf-8')
#             tests = TestFileParser.parse(content)
#         except Exception as e:
#             return Response({"error": f"Failed to process the file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
#         self._save_tests_and_answers(tests, category, topic)
#         return Response({"message": "Tests successfully uploaded."}, status=status.HTTP_201_CREATED)
#
#     def _save_tests_and_answers(self, tests, category, topic):
#         for test_data in tests:
#             test = Test.objects.create(category=category, topic=topic, question=test_data['question'])
#             Answer.objects.bulk_create([
#                 Answer(test=test, text=answer['text'], is_correct=answer['is_correct'])
#                 for answer in test_data['answers']
#             ])


# class NewTestUploadView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         if request.user.role != 'admin':
#             return Response({"error": "Only admins can upload tests."}, status=status.HTTP_403_FORBIDDEN)
#
#         category_id = request.data.get('category_id')
#         topic_name = request.data.get('topic_name')
#         file = request.FILES.get('file')
#
#         if not file or not category_id or not topic_name:
#             return Response({"error": "Category ID, topic name, and file are required."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         category = get_object_or_404(Category, id=category_id)
#         topic, _ = Topic.objects.get_or_create(name=topic_name)
#
#         try:
#             content = file.read().decode('utf-8')
#             tests = self.parse_txt(content)
#         except Exception as e:
#             return Response({"error": f"Failed to process the file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
#
#         for test_data in tests:
#             test = Test.objects.create(
#                 category=category,
#                 topic=topic,
#                 question=test_data['question']
#             )
#             for answer in test_data['answers']:
#                 Answer.objects.create(
#                     test=test,
#                     text=answer['text'],
#                     is_correct=answer['is_correct']
#                 )
#
#         return Response({"message": "Tests successfully uploaded."}, status=status.HTTP_201_CREATED)
#
#     def parse_txt(self, content):
#         tests = []
#         lines = [line.strip() for line in content.splitlines() if line.strip()]
#         i = 0
#
#         while i < len(lines):
#             if lines[i].startswith('(S)'):
#                 question_lines = [lines[i][3:].strip()]
#                 i += 1
#
#                 while i < len(lines) and not lines[i].startswith('(J)'):
#                     question_lines.append(lines[i].strip())
#                     i += 1
#                 question = ' '.join(question_lines)
#
#                 answers = []
#                 while i < len(lines) and lines[i].startswith('(J)'):
#                     answer_lines = [lines[i][3:].strip()]
#                     i += 1
#                     while i < len(lines) and not lines[i].startswith('(J)') and not lines[i].startswith('(S)'):
#                         answer_lines.append(lines[i].strip())
#                         i += 1
#
#                     answer_text = ' '.join(answer_lines)
#                     is_correct = False
#                     if len(answers) == 0:
#                         is_correct = True
#                     answers.append({'text': answer_text, 'is_correct': is_correct})
#
#                 if not answers:
#                     raise ValueError(f"Question does not have any answers: {question}")
#
#                 tests.append({'question': question, 'answers': answers})
#             else:
#                 i += 1
#
#         return tests
