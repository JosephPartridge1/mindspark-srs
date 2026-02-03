from datetime import date, timedelta
from database_adapter import db_adapter

def create_demo_data():
    """
    Buat data sample untuk testing using database adapter
    """
    try:
        # Insert sample users
        users = [
            {'username': 'alice', 'created_date': date.today().isoformat()},
            {'username': 'bob', 'created_date': date.today().isoformat()},
        ]

        for user in users:
            db_adapter.insert_or_ignore('users', user, 'username')

        # Insert sample vocabulary
        vocab = [
            {'english_word': 'apple', 'indonesian_meaning': 'apel', 'part_of_speech': 'noun', 'example_sentence': 'I eat an apple every day.', 'difficulty_score': 1.0},
            {'english_word': 'banana', 'indonesian_meaning': 'pisang', 'part_of_speech': 'noun', 'example_sentence': 'Bananas are yellow.', 'difficulty_score': 1.2},
            {'english_word': 'cherry', 'indonesian_meaning': 'ceri', 'part_of_speech': 'noun', 'example_sentence': 'Cherries are red.', 'difficulty_score': 1.5},
            {'english_word': 'date', 'indonesian_meaning': 'kurma', 'part_of_speech': 'noun', 'example_sentence': 'Dates are sweet.', 'difficulty_score': 1.3},
            {'english_word': 'elderberry', 'indonesian_meaning': 'buah elder', 'part_of_speech': 'noun', 'example_sentence': 'Elderberries are dark.', 'difficulty_score': 2.0},
            {'english_word': 'fig', 'indonesian_meaning': 'buah ara', 'part_of_speech': 'noun', 'example_sentence': 'Figs are delicious.', 'difficulty_score': 1.8},
            {'english_word': 'grape', 'indonesian_meaning': 'anggur', 'part_of_speech': 'noun', 'example_sentence': 'Grapes grow on vines.', 'difficulty_score': 1.1},
            {'english_word': 'house', 'indonesian_meaning': 'rumah', 'part_of_speech': 'noun', 'example_sentence': 'The house is big.', 'difficulty_score': 1.0},
            {'english_word': 'run', 'indonesian_meaning': 'lari', 'part_of_speech': 'verb', 'example_sentence': 'He runs fast.', 'difficulty_score': 1.4},
            {'english_word': 'eat', 'indonesian_meaning': 'makan', 'part_of_speech': 'verb', 'example_sentence': 'I eat breakfast.', 'difficulty_score': 1.2},
        ]

        for v in vocab:
            db_adapter.insert_or_ignore('vocabulary', v, 'english_word')

        # Get user IDs
        cursor = db_adapter.execute("SELECT id FROM users WHERE username = 'alice'")
        alice_id = db_adapter.fetchone(cursor)['id']

        cursor = db_adapter.execute("SELECT id FROM users WHERE username = 'bob'")
        bob_id = db_adapter.fetchone(cursor)['id']

        # Insert sample review sessions
        today = date.today()
        reviews = []

        # Alice's reviews
        for i, word in enumerate(['apple', 'banana', 'cherry']):
            cursor = db_adapter.execute('SELECT id FROM vocabulary WHERE english_word = ?', (word,))
            vocab_id = db_adapter.fetchone(cursor)['id']

            review_date = today - timedelta(days=i*2)
            next_review = today + timedelta(days=1 + i)
            reviews.append({
                'user_id': alice_id,
                'vocab_id': vocab_id,
                'review_date': review_date.isoformat(),
                'next_review_date': next_review.isoformat(),
                'interval_days': 1 + i,
                'ease_factor': 2.5,
                'performance_score': 4,
                'repetition_count': i+1
            })

        # Bob's reviews
        for i, word in enumerate(['date', 'elderberry']):
            cursor = db_adapter.execute('SELECT id FROM vocabulary WHERE english_word = ?', (word,))
            vocab_id = db_adapter.fetchone(cursor)['id']

            review_date = today - timedelta(days=i*3)
            next_review = today + timedelta(days=2 + i)
            reviews.append({
                'user_id': bob_id,
                'vocab_id': vocab_id,
                'review_date': review_date.isoformat(),
                'next_review_date': next_review.isoformat(),
                'interval_days': 2 + i,
                'ease_factor': 2.3,
                'performance_score': 3,
                'repetition_count': i+1
            })

        for review in reviews:
            db_adapter.insert_or_ignore('review_sessions', review, 'id')

        db_adapter.commit()
        print("Demo data created successfully.")

    except Exception as e:
        print(f"Error creating demo data: {e}")
        db_adapter.close()

if __name__ == "__main__":
    create_demo_data()
