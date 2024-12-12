from django.db.models import Count
from apps.testbase.models import Test
from django.db.models import Max
import random


def get_random_tests_with_answers(exam):
    """Optimized random test and answer selection."""
    all_tests = []
    topics = exam.topics.all()

    for topic in topics:
        # Maksimal ID-ni olish (ID bo'yicha random tanlash uchun)
        max_id = Test.objects.filter(topic=topic).aggregate(max_id=Max('id'))['max_id']
        if not max_id:
            continue  # Mavzu uchun testlar mavjud bo'lmasa, keyingi mavzuga o'tamiz

        topic_tests = []
        while len(topic_tests) < exam.total_questions // len(topics):
            random_id = random.randint(1, max_id)  # Tasodifiy ID tanlash
            random_test = Test.objects.filter(topic=topic, id=random_id).first()
            if random_test and random_test not in topic_tests:
                topic_tests.append(random_test)

        for test in topic_tests:
            randomized_answers = list(test.answers.all())
            random.shuffle(randomized_answers)  # Javoblarni randomlashtirish
            all_tests.append({
                "test": test,
                "randomized_answers": randomized_answers
            })

    random.shuffle(all_tests)  # Testlarni ham randomlashtirish
    return all_tests


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
