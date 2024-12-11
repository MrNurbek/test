from django.db.models import Count
import random

from apps.testbase.models import Test


def _get_random_tests(self, exam):
    all_tests = []
    topics = exam.topics.all()
    for topic in topics:
        topic_tests = list(Test.objects.filter(topic=topic))
        if not topic_tests:
            continue  # Agar topic uchun savollar yo'q bo'lsa, o'tib ketamiz

        num_questions = min(len(topic_tests), exam.total_questions // len(topics))  # Mavjud savollar soniga moslash
        random_tests = random.sample(topic_tests, num_questions)
        all_tests.extend(random_tests)

    random.shuffle(all_tests)
    return all_tests


def get_random_tests(exam):
    all_tests = [
        test
        for topic in exam.topics.annotate(test_count=Count('tests'))
        for test in random.sample(
            list(topic.tests.all()),
            min(topic.test_count, exam.total_questions // exam.topics.count())
        )
    ]
    random.shuffle(all_tests)
    return all_tests




def get_exam_result(exam_attempt):
    assigned_tests = exam_attempt.tests.all()
    user_answers = {
        answer.test_id: answer for answer in exam_attempt.answers.all()
    }

    correct_count = 0
    answers_data = []

    for test in assigned_tests:
        user_answer = user_answers.get(test.id)
        is_correct = user_answer.is_correct if user_answer else False
        correct_count += is_correct

        answers_data.append({
            "question": test.question,
            "selected_answer": user_answer.selected_answer if user_answer else None,
            "correct_answer": test.correct_answer,
            "is_correct": is_correct
        })

    return {
        "total_questions": len(assigned_tests),
        "correct_answers": correct_count,
        "wrong_answers": len(assigned_tests) - correct_count,
        "answers": answers_data
    }