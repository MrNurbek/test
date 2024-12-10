


def get_attempt_details(attempt):
    assigned_tests = attempt.tests.all()
    user_answers = {
        answer.test_id: answer for answer in attempt.answers.all()
    }

    answers_data = []
    correct_count = 0

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
        "attempt_number": attempt.attempt_number,
        "score": correct_count,
        "total_questions": len(assigned_tests),
        "correct_answers": correct_count,
        "wrong_answers": len(assigned_tests) - correct_count,
        "answers": answers_data
    }
