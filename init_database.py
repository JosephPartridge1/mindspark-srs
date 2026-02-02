import sqlite3
import os

def init_database():
    # Hapus file lama jika ingin fresh start (opsional)
    # if os.path.exists('srs_vocab.db'):
    #     os.remove('srs_vocab.db')
    
    conn = sqlite3.connect('srs_vocab.db')
    cursor = conn.cursor()
    
    # 1. TABLE words (untuk vocabulary)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            indonesian TEXT NOT NULL,
            part_of_speech TEXT DEFAULT 'noun',
            example_sentence TEXT,
            interval INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            next_review DATETIME,
            last_reviewed DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. TABLE reviews (history jawaban user)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER,
            session_token TEXT,
            correct BOOLEAN,
            user_answer TEXT,
            response_time REAL,
            reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (word_id) REFERENCES words(id)
        )
    ''')
    
    # 3. TABLE learning_sessions (session tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT UNIQUE,
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
    
    # 4. TABLE user_answers (detailed answers)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT,
            word_id INTEGER,
            user_answer TEXT,
            correct BOOLEAN,
            response_time REAL,
            answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_token) REFERENCES learning_sessions(session_token)
        )
    ''')
    
    # 5. INSERT SAMPLE DATA (jika kosong)
    cursor.execute("SELECT COUNT(*) FROM words")
    if cursor.fetchone()[0] == 0:
        sample_words = [
            ('apple', 'apel', 'noun', 'I eat an apple every day.'),
            ('computer', 'komputer', 'noun', 'I use a computer for work.'),
            ('algorithm', 'algoritma', 'noun', 'The algorithm sorts data efficiently.'),
            ('book', 'buku', 'noun', 'She reads a book every night.'),
            ('run', 'berlari', 'verb', 'He can run very fast.')
        ]
        
        cursor.executemany('''
            INSERT INTO words (english, indonesian, part_of_speech, example_sentence)
            VALUES (?, ?, ?, ?)
        ''', sample_words)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == '__main__':
    init_database()
