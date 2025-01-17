from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.useranswer.serializers import SubmitAnswerSerializer
from apps.examattempt.models import ExamAttempt
from apps.testbase.models import Test, Answer
from apps.useranswer.models import UserAnswer
from django.shortcuts import get_object_or_404
from django.utils.timezone import now


class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Javob yuborish",
        operation_description="Foydalanuvchi testga javob yuboradi va natijasi saqlanadi.",
        manual_parameters=[
            openapi.Parameter(
                name='attempt_id',
                in_=openapi.IN_PATH,
                required=True,
                type=openapi.TYPE_INTEGER,
                description='Imtihon urinish identifikatori'
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['test_id', 'selected_answer_id'],
            properties={
                'test_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Test identifikatori'
                ),
                'selected_answer_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Tanlangan javob identifikatori'
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description='Javob muvaffaqiyatli yuborildi.',
                examples={"application/json": {"message": "Answer submitted successfully."}}
            ),
            400: openapi.Response(
                description='Soʻrov notoʻgʻri yoki imtihon allaqachon yakunlangan.',
                examples={"application/json": {"error": "Exam time has expired."}}
            ),
            404: openapi.Response(
                description='Imtihon urinish yoki test topilmadi.',
                examples={"application/json": {"error": "Exam attempt not found."}}
            )
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, attempt_id):
        exam_attempt = get_object_or_404(ExamAttempt, id=attempt_id, user_exam__user=request.user)

        if exam_attempt.status == 'completed':
            return Response({"error": "Exam is already completed."}, status=status.HTTP_400_BAD_REQUEST)

        time_limit = exam_attempt.user_exam.exam.time_limit

        # ✅ To'g'ri time_limit ishlov berish
        if isinstance(time_limit, timedelta):
            expiration_time = exam_attempt.started_at + time_limit
        elif isinstance(time_limit, (int, float)):
            expiration_time = exam_attempt.started_at + timedelta(minutes=time_limit)
        elif isinstance(time_limit, str):
            try:
                h, m, s = map(int, time_limit.split(':'))
                expiration_time = exam_attempt.started_at + timedelta(hours=h, minutes=m, seconds=s)
            except ValueError:
                raise ValueError(f"Invalid string format for time_limit: {time_limit}")
        else:
            raise TypeError(f"Unsupported time_limit type: {type(time_limit)}")

        print("Started at:", exam_attempt.started_at)
        print("Time limit:", time_limit)
        print("Expiration time:", expiration_time)

        if now() > expiration_time:
            exam_attempt.status = 'completed'
            exam_attempt.save()
            return Response({"error": "Exam time has expired."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubmitAnswerSerializer(data=request.data, context={'exam_attempt': exam_attempt})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Answer submitted successfully."}, status=status.HTTP_200_OK)



# class SubmitAnswerView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, attempt_id):
#         exam_attempt = get_object_or_404(ExamAttempt, id=attempt_id, user_exam__user=request.user)
#
#         if exam_attempt.status == 'completed':
#             return Response({"error": "Exam is already completed."}, status=status.HTTP_400_BAD_REQUEST)
#
#         if now() > exam_attempt.started_at + timedelta(minutes=exam_attempt.user_exam.exam.time_limit):
#             exam_attempt.status = 'completed'
#             exam_attempt.save()
#             return Response({"error": "Exam time has expired."}, status=status.HTTP_400_BAD_REQUEST)
#
#         test_id = request.data.get('test_id')
#         selected_answer_id = request.data.get('selected_answer_id')
#
#         if not test_id or not selected_answer_id:
#             return Response({"error": "Both 'test_id' and 'selected_answer_id' are required."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         test = get_object_or_404(Test, id=test_id)
#
#         if test not in exam_attempt.tests.all():
#             valid_test_ids = [test.id for test in exam_attempt.tests.all()]
#             return Response({
#                 "error": f"Test ID {test_id} is not linked to this exam attempt. Valid test IDs: {valid_test_ids}"
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         selected_answer = get_object_or_404(Answer, id=selected_answer_id, test=test)
#
#         user_answer, created = UserAnswer.objects.update_or_create(
#             exam_attempt=exam_attempt,
#             test=test,
#             defaults={
#                 'selected_answer': selected_answer.text,
#                 'is_correct': selected_answer.is_correct
#             }
#         )
#
#         return Response({
#             "message": "Answer submitted successfully.",
#             "updated": not created
#         }, status=status.HTTP_200_OK)


#
# class SubmitAnswerView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request, attempt_id):
#         try:
#             exam_attempt = get_object_or_404(ExamAttempt, id=attempt_id, user_exam__user=request.user)
#             if exam_attempt.status == 'completed':
#                 return Response({"error": "Exam is already completed."}, status=status.HTTP_400_BAD_REQUEST)
#
#             if timezone.now() > exam_attempt.started_at + timedelta(minutes=exam_attempt.user_exam.exam.time_limit):
#                 exam_attempt.status = 'completed'
#                 exam_attempt.save()
#                 return Response({"error": "Exam time has expired."}, status=status.HTTP_400_BAD_REQUEST)
#             test_id = request.data.get('test_id')
#             selected_answer_id = request.data.get('selected_answer_id')
#
#             if not test_id or not selected_answer_id:
#                 return Response({"error": "Both 'test_id' and 'selected_answer_id' are required."},
#                                 status=status.HTTP_400_BAD_REQUEST)
#             test = get_object_or_404(Test, id=test_id)
#             if test not in exam_attempt.tests.all():
#                 raise ValueError(f"Test ID {test_id} is not linked to ExamAttempt {exam_attempt.id}")
#
#             selected_answer = get_object_or_404(Answer, id=selected_answer_id, test=test)
#             user_answer, created = UserAnswer.objects.update_or_create(
#                 exam_attempt=exam_attempt,
#                 test=test,
#                 defaults={
#                     'selected_answer': selected_answer.text,
#                     'is_correct': selected_answer.is_correct
#                 }
#             )
#             return Response({
#                 "message": "Answer submitted successfully.",
#                 "updated": not created
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
