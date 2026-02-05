import requests
import time
import sqlite3

BASE_URL = 'http://localhost:5000'

def test_session_completion():
    # Start session
    session_token = f'session_test_{int(time.time())}'
    start_response = requests.post(f'{BASE_URL}/api/session-start', json={
        'token': session_token,
        'start_time': time.time() * 1000  # milliseconds
    })
    print(f'Session start: {start_response.status_code}')

    # Simulate 10 answers (5 correct, 5 wrong for edge case)
    answers = [
        {'word_id': 1, 'user_answer': 'apel', 'correct': True},  # correct
        {'word_id': 2, 'user_answer': 'buku', 'correct': True},  # correct
        {'word_id': 3, 'user_answer': 'run', 'correct': False},  # wrong
        {'word_id': 4, 'user_answer': 'happy', 'correct': True}, # correct
        {'word_id': 5, 'user_answer': 'computer', 'correct': True}, # correct
        {'word_id': 6, 'user_answer': 'algoritma', 'correct': True}, # correct
        {'word_id': 7, 'user_answer': 'sementara', 'correct': False}, # wrong
        {'word_id': 8, 'user_answer': 'dimana-mana', 'correct': True}, # correct
        {'word_id': 9, 'user_answer': 'kebetulan', 'correct': False}, # wrong
        {'word_id': 10, 'user_answer': 'paling murni', 'correct': True} # correct
    ]

    for i, ans in enumerate(answers):
        response = requests.post(f'{BASE_URL}/api/submit-answer', json={
            'word_id': ans['word_id'],
            'user_answer': ans['user_answer'],
            'response_time': 1.0
        })
        print(f'Answer {i+1}: {response.status_code} - Correct: {ans["correct"]}')

    # Complete session (this should trigger the updated completeSession logic)
    # But since it's frontend, we need to simulate the POST to /api/session/complete
    # The frontend now sends this data
    total_questions = len(answers)
    correct_answers = sum(1 for a in answers if a['correct'])
    accuracy = (correct_answers / total_questions) * 100

    complete_response = requests.post(f'{BASE_URL}/api/session/complete', json={
        'session_token': session_token,
        'end_time': time.time() * 1000,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'accuracy_rate': accuracy
    })
    print(f'Session complete: {complete_response.status_code}')

    # Save answers (simulate saveAllAnswers)
    for ans in answers:
        requests.post(f'{BASE_URL}/api/session/answer', json={
            'session_token': session_token,
            'word_id': ans['word_id'],
            'user_answer': ans['user_answer'],
            'correct': ans['correct'],
            'response_time': 1.0,
            'answered_at': time.time() * 1000
        })

    # Check database
    conn = sqlite3.connect('srs_vocab.db')
    cursor = conn.cursor()

    # Test 1: Session completion data
    cursor.execute('''
        SELECT total_questions, correct_answers, accuracy_rate
        FROM learning_sessions
        ORDER BY id DESC LIMIT 1
    ''')
    session_data = cursor.fetchone()
    print(f'Session data: {session_data}')

    # Test 2: Answers saved
    cursor.execute('''
        SELECT COUNT(*) FROM user_answers
        WHERE session_token = %s
    ''' if db_adapter.is_postgresql else '''
        SELECT total_questions, correct_answers, accuracy_rate
        FROM learning_sessions
        ORDER BY id DESC LIMIT 1
    ''')
    session_data = cursor.fetchone()
    print(f'Session data: {session_data}')

    # Test 2: Answers saved
    cursor.execute('''
        SELECT COUNT(*) FROM user_answers
        WHERE session_token = %s
    ''' if db_adapter.is_postgresql else '''
        SELECT total_questions, correct_answers, accuracy_rate
        FROM learning_sessions
        ORDER BY id DESC LIMIT 1
    ''')
    session_data = cursor.fetchone()
    print(f'Session data: {session_data}')

    # Test 2: Answers saved
    cursor.execute('''
        SELECT COUNT(*) FROM user_answers
        WHERE session_token = %s
    ''' if db_adapter.is_postgresql else '''
        SELECT total_questions, correct_answers, accuracy_rate
        FROM learning_sessions
        ORDER BY id DESC LIMIT 1
    ''')
    session_data = cursor.fetchone()
    print(f'Session data: {session_data}')

    # Test 2: Answers saved
    cursor.execute('''
        SELECT COUNT(*) FROM user_answers
        WHERE session_token = %s
    ''' if db_adapter.is_postgresql else '''
        SELECT total_questions, correct_answers, accuracy_rate
        FROM learning_sessions
        ORDER BY id DESC LIMIT 1
    ''')
    session_data = cursor.fetchone()
    print(f'Session data: {session_data}')

    # Test 2: Answers saved
    cursor.execute('''
        SELECT COUNT(*) FROM user_answers
        WHERE session_token = %s
    ''' if db_adapter.is_postgresql else '''
        SELECT total_questions, correct_answers, accuracy_rate
        FROM learning_sessions
        ORDER BY id DESC LIMIT 1
    ''')
    session_data = cursor.fetchone()
    print(f'Session data: {session_data}')

    # Test 2: Answers saved
    cursor.execute('''
        SELECT COUNT(*) FROM user_answers
        WHERE session_token = %s
    ''' if db_adapter.is_postgresql else '''
        SELECT total_questions, correct_answers, accuracy_rate
        FROM learning_sessions
        ORDER BY id DESC LIMIT 1
    ''')
    session_data = cursor.fetchone()
    print(f'Session data: {session_data}')

    # Test 2: Answers saved
    cursor.execute('''
        SELECT COUNT(*) FROM user_answers
        WHERE session_token = %s
    ''' if db_adapter.is_postgresql else '''
        SELECT total_questions, correct_answers, accuracy_rate
        FROM learning_sessions
        ORDER BY id DESC LIMIT 1
    ''')
    session_data = cursor.fetchone()
    print(f'Session data: {session_data}')

    # Test 2: Answers saved
    cursor.execute('''
        SELECT COUNT(*) FROM user_answers
        WHERE session_token = ?
    ''', (session_token,))
    answer_count = cursor.fetchone()[0]
    print(f'Answer count: {answer_count}')

    conn.close()

    # Assertions
    assert session_data[0] == 10, f"total_questions should be 10, got {session_data[0]}"
    assert session_data[1] == 7, f"correct_answers should be 7, got {session_data[1]}"
    assert session_data[2] == 70.0, f"accuracy_rate should be 70.0, got {session_data[2]}"
    assert answer_count == 10, f"Answer count should be 10, got {answer_count}"

    print("All tests PASSED!")

if __name__ == '__main__':
    test_session_completion()
