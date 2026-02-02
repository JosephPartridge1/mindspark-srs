import sqlite3
from datetime import date, timedelta

def create_demo_data(db_path='vocab.db'):
    """
    Buat data sample untuk testing
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert sample users
    users = [
        ('alice', date.today().isoformat()),
        ('bob', date.today().isoformat()),
    ]

    cursor.executemany('INSERT OR IGNORE INTO users (username, created_date) VALUES (?, ?)', users)

    # Insert sample vocabulary
    vocab = [
        ('apple', 'apel', 'noun', 'I eat an apple every day.', 1.0),
        ('banana', 'pisang', 'noun', 'Bananas are yellow.', 1.2),
        ('cherry', 'ceri', 'noun', 'Cherries are red.', 1.5),
        ('date', 'kurma', 'noun', 'Dates are sweet.', 1.3),
        ('elderberry', 'buah elder', 'noun', 'Elderberries are dark.', 2.0),
        ('fig', 'buah ara', 'noun', 'Figs are delicious.', 1.8),
        ('grape', 'anggur', 'noun', 'Grapes grow on vines.', 1.1),
        ('house', 'rumah', 'noun', 'The house is big.', 1.0),
        ('run', 'lari', 'verb', 'He runs fast.', 1.4),
        ('eat', 'makan', 'verb', 'I eat breakfast.', 1.2),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO vocabulary
        (english_word, indonesian_meaning, part_of_speech, example_sentence, difficulty_score)
        VALUES (?, ?, ?, ?, ?)
    ''', vocab)

    # Get user IDs
    cursor.execute('SELECT id FROM users WHERE username = ?', ('alice',))
    alice_id = cursor.fetchone()[0]

    cursor.execute('SELECT id FROM users WHERE username = ?', ('bob',))
    bob_id = cursor.fetchone()[0]

    # Insert sample review sessions
    today = date.today()
    reviews = []

    # Alice's reviews
    for i, word in enumerate(['apple', 'banana', 'cherry']):
        cursor.execute('SELECT id FROM vocabulary WHERE english_word = ?', (word,))
        vocab_id = cursor.fetchone()[0]

        review_date = today - timedelta(days=i*2)
        next_review = today + timedelta(days=1 + i)
        reviews.append((alice_id, vocab_id, review_date.isoformat(), next_review.isoformat(), 1 + i, 2.5, 4, i+1))

    # Bob's reviews
    for i, word in enumerate(['date', 'elderberry']):
        cursor.execute('SELECT id FROM vocabulary WHERE english_word = ?', (word,))
        vocab_id = cursor.fetchone()[0]

        review_date = today - timedelta(days=i*3)
        next_review = today + timedelta(days=2 + i)
        reviews.append((bob_id, vocab_id, review_date.isoformat(), next_review.isoformat(), 2 + i, 2.3, 3, i+1))

    cursor.executemany('''
        INSERT OR IGNORE INTO review_sessions
        (user_id, vocab_id, review_date, next_review_date, interval_days, ease_factor, performance_score, repetition_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', reviews)

    conn.commit()
    conn.close()
    print("Demo data created successfully.")

if __name__ == "__main__":
    try:
        # Coba import dari direktori saat ini
        from database import DatabaseManager
    except ImportError:
        # Jika gagal, coba relative import
        from .database import DatabaseManager
    db_manager = DatabaseManager()
    db_manager.create_tables()
    create_demo_data()
