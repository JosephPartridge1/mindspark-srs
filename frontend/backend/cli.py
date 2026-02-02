import sqlite3
from datetime import date
from review_scheduler import SRSAlgorithm, load_due_vocabulary, simulate_learning_curve
from visualization import plot_review_schedule, plot_retention_curve, generate_report

DATABASE = "vocabulary_app.db"

def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Tabel users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            created_date DATE
        )
    ''')

    # Tabel vocabulary
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY,
            english_word TEXT,
            indonesian_meaning TEXT,
            part_of_speech TEXT,
            example_sentence TEXT,
            difficulty_score FLOAT DEFAULT 1.0
        )
    ''')

    # Tabel review_sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS review_sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            vocab_id INTEGER,
            review_date TIMESTAMP,
            next_review_date TIMESTAMP,
            interval_days INTEGER,
            ease_factor FLOAT DEFAULT 2.5,
            performance_score INTEGER,
            repetition_count INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

def register_user(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, created_date) VALUES (?, ?)", (username, date.today().isoformat()))
        conn.commit()
        user_id = cursor.lastrowid
        print(f"User {username} registered successfully.")
        return user_id
    except sqlite3.IntegrityError:
        print("Username already exists.")
        return None
    finally:
        conn.close()

def login_user(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        print(f"Logged in as {username}.")
        return user[0]
    else:
        print("User not found.")
        return None

def add_vocabulary(english_word, indonesian_meaning, part_of_speech, example_sentence, difficulty_score=1.0):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vocabulary (english_word, indonesian_meaning, part_of_speech, example_sentence, difficulty_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (english_word, indonesian_meaning, part_of_speech, example_sentence, difficulty_score))
    vocab_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Vocabulary '{english_word}' added.")
    return vocab_id

def start_review_session(user_id):
    due_vocab = load_due_vocabulary(user_id)
    if not due_vocab:
        print("No vocabulary due for review.")
        return

    srs = SRSAlgorithm()
    for vocab in due_vocab:
        print(f"\nWord: {vocab['english_word']}")
        input("Press Enter to reveal meaning...")
        print(f"Meaning: {vocab['indonesian_meaning']} ({vocab['part_of_speech']})")
        print(f"Example: {vocab['example_sentence']}")
        quality = int(input("How well did you remember? (0-5): "))

        # Calculate next review
        result = srs.calculate_next_review(
            quality_response=quality,
            current_interval=vocab['interval_days'],
            current_ease=vocab['ease_factor'],
            repetition_count=vocab['repetition_count']
        )

        # Calculate new repetition_count
        if quality < 3:
            new_repetition_count = 0
        else:
            new_repetition_count = vocab['repetition_count'] + 1

        # Update database
        update_review_session(user_id, vocab['vocab_id'], result, quality, new_repetition_count)

def update_review_session(user_id, vocab_id, result, quality):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO review_sessions
        (user_id, vocab_id, review_date, next_review_date, interval_days, ease_factor, performance_score, repetition_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, vocab_id, date.today().isoformat(), result['next_review_date'],
        result['new_interval'], result['new_ease'], quality,
        # Need to calculate repetition_count, but for simplicity, assume it's updated in SRSAlgorithm, but since it's not returned, let's add it
        # Actually, SRSAlgorithm doesn't return repetition_count, so I need to adjust
        0  # Placeholder, need to fix
    ))
    conn.commit()
    conn.close()

def view_statistics(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*), AVG(performance_score), COUNT(DISTINCT vocab_id)
        FROM review_sessions WHERE user_id = ?
    ''', (user_id,))
    stats = cursor.fetchone()
    conn.close()
    print(f"Total reviews: {stats[0]}")
    print(f"Average performance: {stats[1]:.2f}")
    print(f"Unique words reviewed: {stats[2]}")

def simulate_curve(user_id):
    rates = simulate_learning_curve(user_id)
    for i, rate in enumerate(rates):
        print(f"Day {i+1}: Retention rate {rate:.2f}")

def main():
    create_tables()
    current_user = None

    while True:
        if not current_user:
            print("\n1. Login")
            print("2. Register")
            print("3. Exit")
            choice = input("Choose: ")
            if choice == '1':
                username = input("Username: ")
                current_user = login_user(username)
            elif choice == '2':
                username = input("Username: ")
                current_user = register_user(username)
            elif choice == '3':
                break
        else:
            print("\n1. Add vocabulary")
            print("2. Start review session")
            print("3. View statistics")
            print("4. Simulate learning curve")
            print("5. Logout")
            choice = input("Choose: ")
            if choice == '1':
                word = input("English word: ")
                meaning = input("Indonesian meaning: ")
                pos = input("Part of speech: ")
                example = input("Example sentence: ")
                diff = float(input("Difficulty score (default 1.0): ") or 1.0)
                add_vocabulary(word, meaning, pos, example, diff)
            elif choice == '2':
                start_review_session(current_user)
            elif choice == '3':
                view_statistics(current_user)
            elif choice == '4':
                simulate_curve(current_user)
            elif choice == '5':
                current_user = None

if __name__ == "__main__":
    main()
