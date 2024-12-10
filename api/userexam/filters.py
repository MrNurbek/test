from django.db.models import Count
import random


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