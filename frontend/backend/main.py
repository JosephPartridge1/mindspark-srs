import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta

app = FastAPI()

# Agar frontend dari localhost:5173 bisa request tanpa masalah CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = "vocabulary_app.db"

def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Tabel users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
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
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

class SRSAlgorithm:
    def __init__(self, database: str = DATABASE):
        self.database = database

    def calculate_next_review(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Mengimplementasikan algoritma SM-2 sederhana.

        Parameters:
        - quality_response: integer 0-5 (0=lupa total, 5=sangat mudah)
        - current_interval: integer (hari)
        - current_ease: float (default 2.5)
        - repetition_count: integer

        Returns:
        - dictionary: {'new_interval': interval, 'new_ease': ease_factor, 'next_review_date': date}
        """
        if quality_response < 3:
            repetition_count = 0
            interval = 1
        else:
            repetition_count += 1
            if repetition_count == 1:
                interval = 1
            elif repetition_count == 2:
                interval = 6
            else:
                interval = round(current_interval * current_ease)

        # Update ease_factor
        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calculate next review date
        today = date.today()
        next_review_date = today + timedelta(days=interval)

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = %s AND rs.next_review_date <= %s
        ''' if db_adapter.is_postgresql else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
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
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

class SRSAlgorithm:
    def __init__(self, database: str = DATABASE):
        self.database = database

    def calculate_next_review(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Mengimplementasikan algoritma SM-2 sederhana.

        Parameters:
        - quality_response: integer 0-5 (0=lupa total, 5=sangat mudah)
        - current_interval: integer (hari)
        - current_ease: float (default 2.5)
        - repetition_count: integer

        Returns:
        - dictionary: {'new_interval': interval, 'new_ease': ease_factor, 'next_review_date': date}
        """
        if quality_response < 3:
            repetition_count = 0
            interval = 1
        else:
            repetition_count += 1
            if repetition_count == 1:
                interval = 1
            elif repetition_count == 2:
                interval = 6
            else:
                interval = round(current_interval * current_ease)

        # Update ease_factor
        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calculate next review date
        today = date.today()
        next_review_date = today + timedelta(days=interval)

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = %s AND rs.next_review_date <= %s
        ''' if db_adapter.is_postgresql else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
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
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

class SRSAlgorithm:
    def __init__(self, database: str = DATABASE):
        self.database = database

    def calculate_next_review(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Mengimplementasikan algoritma SM-2 sederhana.

        Parameters:
        - quality_response: integer 0-5 (0=lupa total, 5=sangat mudah)
        - current_interval: integer (hari)
        - current_ease: float (default 2.5)
        - repetition_count: integer

        Returns:
        - dictionary: {'new_interval': interval, 'new_ease': ease_factor, 'next_review_date': date}
        """
        if quality_response < 3:
            repetition_count = 0
            interval = 1
        else:
            repetition_count += 1
            if repetition_count == 1:
                interval = 1
            elif repetition_count == 2:
                interval = 6
            else:
                interval = round(current_interval * current_ease)

        # Update ease_factor
        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calculate next review date
        today = date.today()
        next_review_date = today + timedelta(days=interval)

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = %s AND rs.next_review_date <= %s
        ''' if db_adapter.is_postgresql else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
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
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

class SRSAlgorithm:
    def __init__(self, database: str = DATABASE):
        self.database = database

    def calculate_next_review(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Mengimplementasikan algoritma SM-2 sederhana.

        Parameters:
        - quality_response: integer 0-5 (0=lupa total, 5=sangat mudah)
        - current_interval: integer (hari)
        - current_ease: float (default 2.5)
        - repetition_count: integer

        Returns:
        - dictionary: {'new_interval': interval, 'new_ease': ease_factor, 'next_review_date': date}
        """
        if quality_response < 3:
            repetition_count = 0
            interval = 1
        else:
            repetition_count += 1
            if repetition_count == 1:
                interval = 1
            elif repetition_count == 2:
                interval = 6
            else:
                interval = round(current_interval * current_ease)

        # Update ease_factor
        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calculate next review date
        today = date.today()
        next_review_date = today + timedelta(days=interval)

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = %s AND rs.next_review_date <= %s
        ''' if db_adapter.is_postgresql else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
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
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

class SRSAlgorithm:
    def __init__(self, database: str = DATABASE):
        self.database = database

    def calculate_next_review(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Mengimplementasikan algoritma SM-2 sederhana.

        Parameters:
        - quality_response: integer 0-5 (0=lupa total, 5=sangat mudah)
        - current_interval: integer (hari)
        - current_ease: float (default 2.5)
        - repetition_count: integer

        Returns:
        - dictionary: {'new_interval': interval, 'new_ease': ease_factor, 'next_review_date': date}
        """
        if quality_response < 3:
            repetition_count = 0
            interval = 1
        else:
            repetition_count += 1
            if repetition_count == 1:
                interval = 1
            elif repetition_count == 2:
                interval = 6
            else:
                interval = round(current_interval * current_ease)

        # Update ease_factor
        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calculate next review date
        today = date.today()
        next_review_date = today + timedelta(days=interval)

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = %s AND rs.next_review_date <= %s
        ''' if db_adapter.is_postgresql else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
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
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

class SRSAlgorithm:
    def __init__(self, database: str = DATABASE):
        self.database = database

    def calculate_next_review(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Mengimplementasikan algoritma SM-2 sederhana.

        Parameters:
        - quality_response: integer 0-5 (0=lupa total, 5=sangat mudah)
        - current_interval: integer (hari)
        - current_ease: float (default 2.5)
        - repetition_count: integer

        Returns:
        - dictionary: {'new_interval': interval, 'new_ease': ease_factor, 'next_review_date': date}
        """
        if quality_response < 3:
            repetition_count = 0
            interval = 1
        else:
            repetition_count += 1
            if repetition_count == 1:
                interval = 1
            elif repetition_count == 2:
                interval = 6
            else:
                interval = round(current_interval * current_ease)

        # Update ease_factor
        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calculate next review date
        today = date.today()
        next_review_date = today + timedelta(days=interval)

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = ? AND rs.next_review_date <= ?
        ''' if db_adapter.is_postgresql else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
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
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

class SRSAlgorithm:
    def __init__(self, database: str = DATABASE):
        self.database = database

    def calculate_next_review(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Mengimplementasikan algoritma SM-2 sederhana.

        Parameters:
        - quality_response: integer 0-5 (0=lupa total, 5=sangat mudah)
        - current_interval: integer (hari)
        - current_ease: float (default 2.5)
        - repetition_count: integer

        Returns:
        - dictionary: {'new_interval': interval, 'new_ease': ease_factor, 'next_review_date': date}
        """
        if quality_response < 3:
            repetition_count = 0
            interval = 1
        else:
            repetition_count += 1
            if repetition_count == 1:
                interval = 1
            elif repetition_count == 2:
                interval = 6
            else:
                interval = round(current_interval * current_ease)

        # Update ease_factor
        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calculate next review date
        today = date.today()
        next_review_date = today + timedelta(days=interval)

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = %s AND rs.next_review_date <= ?
        ''' if db_adapter.is_postgresql else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
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
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
        )
    ''')

    conn.commit()
    conn.close()

class SRSAlgorithm:
    def __init__(self, database: str = DATABASE):
        self.database = database

    def calculate_next_review(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Mengimplementasikan algoritma SM-2 sederhana.

        Parameters:
        - quality_response: integer 0-5 (0=lupa total, 5=sangat mudah)
        - current_interval: integer (hari)
        - current_ease: float (default 2.5)
        - repetition_count: integer

        Returns:
        - dictionary: {'new_interval': interval, 'new_ease': ease_factor, 'next_review_date': date}
        """
        if quality_response < 3:
            repetition_count = 0
            interval = 1
        else:
            repetition_count += 1
            if repetition_count == 1:
                interval = 1
            elif repetition_count == 2:
                interval = 6
            else:
                interval = round(current_interval * current_ease)

        # Update ease_factor
        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calculate next review date
        today = date.today()
        next_review_date = today + timedelta(days=interval)

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = ? AND rs.next_review_date <= ?
        ''', (user_id, today))

        due_vocab = []
        for row in cursor.fetchall():
            due_vocab.append({
                'vocab_id': row[0],
                'english_word': row[1],
                'indonesian_meaning': row[2],
                'part_of_speech': row[3],
                'example_sentence': row[4],
                'difficulty_score': row[5]
            })

        conn.close()
        return due_vocab

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Dummy session data (for now, can be replaced with database queries)
WORDS = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]

@app.get("/session/start")
def start_session(user_id: int = 1, size: int = 5):
    # Ambil kata sesuai size
    items = WORDS[:size]
    return items

@app.post("/answer")
def submit_answer(word: str, quality: str):
    # Untuk testing, hanya log jawaban
    print(f"Word: {word}, Answer Quality: {quality}")
    return {"status": "ok", "word": word, "quality": quality}
