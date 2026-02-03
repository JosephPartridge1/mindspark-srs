import sqlite3

conn = sqlite3.connect('srs_vocab.db')
cursor = conn.cursor()

# Check user_answers count
cursor.execute('SELECT COUNT(*) FROM user_answers')
user_answers_count = cursor.fetchone()[0]
print(f'user_answers count: {user_answers_count}')

# Check test sessions
cursor.execute('SELECT COUNT(*) FROM learning_sessions WHERE session_token LIKE "session_test_%"')
test_sessions_count = cursor.fetchone()[0]
print(f'test sessions count: {test_sessions_count}')

# Get latest test session
cursor.execute('SELECT session_token, total_questions, correct_answers, accuracy_rate FROM learning_sessions WHERE session_token LIKE "session_test_%" ORDER BY id DESC LIMIT 1')
row = cursor.fetchone()
if row:
    print(f'Latest test session: {row}')
else:
    print('No test sessions found')

# Check recent user_answers
cursor.execute('SELECT session_token, word_id, user_answer, correct FROM user_answers ORDER BY id DESC LIMIT 5')
recent_answers = cursor.fetchall()
print(f'Recent answers: {recent_answers}')

conn.close()
