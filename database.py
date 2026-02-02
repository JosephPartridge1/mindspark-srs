# database.py - THREAD-SAFE DATABASE FOR SRS SYSTEM
import sqlite3
import threading
from datetime import datetime, timedelta

class SimpleDatabase:
    def __init__(self, db_name='srs_vocab.db'):
        self.db_name = db_name
        self.local = threading.local()  # Thread-local storage for connections
        self.init_database()

    def connect(self):
        # Create a separate connection for each thread
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        return self.local.connection
    
    def init_database(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        # Updated tables for Duolingo-style SRS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                indonesian TEXT NOT NULL,
                part_of_speech TEXT DEFAULT 'noun',
                example_sentence TEXT DEFAULT '',
                difficulty_score FLOAT DEFAULT 1.0,
                interval INTEGER DEFAULT 1,  -- in minutes for testing, later days
                repetitions INTEGER DEFAULT 0,
                ease_factor REAL DEFAULT 2.5,
                next_review DATETIME,
                last_reviewed DATETIME,
                streak INTEGER DEFAULT 0,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                correct BOOLEAN NOT NULL,
                response_time REAL,  -- in seconds
                user_answer TEXT NOT NULL,
                FOREIGN KEY(word_id) REFERENCES words(id)
            )
        ''')

        # Admin dashboard tables for session tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE,  -- Untuk identifikasi frontend
                user_ip TEXT,
                user_agent TEXT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                accuracy_rate REAL,
                completed BOOLEAN DEFAULT FALSE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT,
                word_id INTEGER,
                user_answer TEXT,
                correct BOOLEAN,
                response_time REAL,
                answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_token) REFERENCES learning_sessions(session_token) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        return True
    
    def add_word(self, english, indonesian):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO words (english, indonesian) VALUES (?, ?)',
            (english, indonesian)
        )
        word_id = cursor.lastrowid
        conn.commit()
        return word_id
    
    def add_review(self, word_id, score, interval_days=1, ease_factor=2.5, repetition_count=0):
        conn = self.connect()
        cursor = conn.cursor()

        # Calculate next review date
        next_date = datetime.now() + timedelta(days=interval_days)

        cursor.execute('''
            INSERT INTO reviews (word_id, score, next_review_date, interval_days, ease_factor, repetition_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (word_id, score, next_date, interval_days, ease_factor, repetition_count))

        review_id = cursor.lastrowid
        conn.commit()
        return review_id
    
    def get_all_words(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM words ORDER BY id')
        return cursor.fetchall()
    
    def get_due_words(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT w.* FROM words w
            LEFT JOIN reviews r ON w.id = r.word_id
            WHERE r.next_review_date IS NULL
               OR r.next_review_date <= datetime('now')
            ORDER BY r.next_review_date ASC
        ''')
        return cursor.fetchall()

    def get_due_vocab(self, user_id=1):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.
        Since SimpleDatabase doesn't have users, user_id is ignored.
        """
        conn = self.connect()
        cursor = conn.cursor()

        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT w.id, w.english, w.indonesian, w.part_of_speech, w.example_sentence, w.difficulty_score,
                   r.next_review_date, r.ease_factor, r.interval_days, r.repetition_count
            FROM words w
            LEFT JOIN reviews r ON w.id = r.word_id
            WHERE r.next_review_date IS NULL OR r.next_review_date <= ?
            ORDER BY
                CASE WHEN r.next_review_date < ? THEN 0 ELSE 1 END,
                r.next_review_date ASC,
                w.difficulty_score DESC,
                r.ease_factor ASC
        ''', (today, today))

        due_vocab = []
        for row in cursor.fetchall():
            due_vocab.append({
                'vocab_id': row[0],
                'english_word': row[1],
                'indonesian_meaning': row[2],
                'part_of_speech': row[3],
                'example_sentence': row[4],
                'difficulty_score': row[5],
                'next_review_date': row[6],
                'ease_factor': row[7] or 2.5,
                'interval_days': row[8] or 1,
                'repetition_count': row[9] or 0
            })

        conn.close()
        return due_vocab
    
    def get_stats(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        stats = {}
        cursor.execute('SELECT COUNT(*) FROM words')
        stats['total_words'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT word_id) FROM reviews')
        stats['reviewed_words'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(score) FROM reviews')
        stats['avg_score'] = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM reviews WHERE next_review_date <= datetime("now")')
        stats['due_count'] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        if self.connection:
            self.connection.close()

# Standalone init_database function for app.py import
def init_database(db_name='srs_vocab.db'):
    """Initialize database with required tables"""
    conn = sqlite3.connect(db_name, check_same_thread=False)
    cursor = conn.cursor()

    # Updated tables for Duolingo-style SRS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            indonesian TEXT NOT NULL,
            part_of_speech TEXT DEFAULT 'noun',
            example_sentence TEXT DEFAULT '',
            difficulty_score FLOAT DEFAULT 1.0,
            interval INTEGER DEFAULT 1,  -- in minutes for testing, later days
            repetitions INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            next_review DATETIME,
            last_reviewed DATETIME,
            streak INTEGER DEFAULT 0,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            correct BOOLEAN NOT NULL,
            response_time REAL,  -- in seconds
            user_answer TEXT NOT NULL,
            FOREIGN KEY(word_id) REFERENCES words(id)
        )
    ''')

    # Admin dashboard tables for session tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT UNIQUE,  -- Untuk identifikasi frontend
            user_ip TEXT,
            user_agent TEXT,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            accuracy_rate REAL,
            completed BOOLEAN DEFAULT FALSE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT,
            word_id INTEGER,
            user_answer TEXT,
            correct BOOLEAN,
            response_time REAL,
            answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_token) REFERENCES learning_sessions(session_token) ON DELETE CASCADE
        )
    ''')

    # Seed data with 10 words
    cursor.execute('SELECT COUNT(*) FROM words')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO words (english, indonesian, part_of_speech, example_sentence, difficulty_score) VALUES (?, ?, ?, ?, ?)
        ''', [
            ('apple', 'apel', 'noun', 'I eat an apple every day.', 1.0),
            ('book', 'buku', 'noun', 'This is an interesting book.', 1.0),
            ('run', 'berlari', 'verb', 'She likes to run in the park.', 1.5),
            ('happy', 'bahagia', 'adjective', 'The child looks very happy.', 1.2),
            ('computer', 'komputer', 'noun', 'I use a computer for work.', 2.0),
            ('algorithm', 'algoritma', 'noun', 'The algorithm solves complex problems.', 3.0),
            ('ephemeral', 'sementara', 'adjective', 'Life is ephemeral and fleeting.', 4.0),
            ('ubiquitous', 'dimana-mana', 'adjective', 'Smartphones are ubiquitous nowadays.', 3.5),
            ('serendipity', 'kebetulan baik', 'noun', 'Finding this book was pure serendipity.', 4.5),
            ('quintessential', 'paling murni', 'adjective', 'This dish is the quintessential Italian pasta.', 4.2)
        ])

    conn.commit()
    conn.close()
    return True

# Quick test function
def test_database():
    db = SimpleDatabase()
    
    # Add sample words if empty
    words = db.get_all_words()
    if len(words) == 0:
        sample = [
            ('apple', 'apel'),
            ('book', 'buku'), 
            ('run', 'berlari'),
            ('happy', 'bahagia'),
            ('teacher', 'guru')
        ]
        for eng, ind in sample:
            db.add_word(eng, ind)
        print("Added sample words")
    
    # Show stats
    stats = db.get_stats()
    print(f"Database stats: {stats}")
    
    db.close()
    return True

if __name__ == '__main__':
    test_database()