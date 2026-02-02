from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from database import get_db
from srs_algorithm import SRSAlgorithm
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

srs = SRSAlgorithm()

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            indonesian TEXT NOT NULL,
            part_of_speech TEXT DEFAULT 'noun',
            example_sentence TEXT DEFAULT '',
            interval INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            next_review DATETIME,
            last_reviewed DATETIME,
            streak INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            correct BOOLEAN NOT NULL,
            response_time REAL,
            user_answer TEXT NOT NULL,
            review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(word_id) REFERENCES words(id)
        );

        INSERT OR IGNORE INTO words (english, indonesian, part_of_speech, example_sentence) VALUES
        ('apple', 'apel', 'noun', 'I eat an apple every day.'),
        ('book', 'buku', 'noun', 'This is an interesting book.'),
        ('run', 'berlari', 'verb', 'She likes to run in the park.'),
        ('happy', 'bahagia', 'adjective', 'The child looks very happy.'),
        ('computer', 'komputer', 'noun', 'I use a computer for work.');
    """)
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/next-word')
def get_next_word():
    try:
        conn = get_db()
        cursor = conn.cursor()

        now = datetime.now()
        cursor.execute('''
            SELECT id, english, indonesian, part_of_speech, example_sentence,
                   interval, repetitions, ease_factor, next_review, streak
            FROM words
            WHERE next_review IS NULL OR next_review <= ?
            ORDER BY next_review ASC
            LIMIT 1
        ''', (now,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': 'No words due for review'}), 404

        return jsonify({
            'id': row[0],
            'english': row[1],
            'indonesian': row[2],
            'part_of_speech': row[3],
            'example_sentence': row[4],
            'interval': row[5],
            'repetitions': row[6],
            'ease_factor': row[7],
            'next_review': row[8],
            'streak': row[9]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    try:
        data = request.get_json()
        word_id = data.get('word_id')
        user_answer = data.get('user_answer', '').strip()

        if word_id is None or user_answer is None:
            return jsonify({'error': 'word_id and user_answer required'}), 400

        conn = get_db()
        cursor = conn.cursor()

        # Get word details
        cursor.execute('SELECT indonesian, interval, repetitions, ease_factor, streak FROM words WHERE id = ?', (word_id,))
        word_row = cursor.fetchone()
        if not word_row:
            conn.close()
            return jsonify({'error': 'Word not found'}), 404

        correct_answer = word_row[0]
        current_interval = word_row[1] or 1
        current_repetitions = word_row[2] or 0
        current_ease = word_row[3] or 2.5
        current_streak = word_row[4] or 0

        # Check if answer is correct
        is_correct = srs.fuzzy_match(user_answer, correct_answer)

        # Calculate new SRS values
        new_interval, new_ease, new_repetitions = srs.calculate_srs(
            is_correct, current_interval, current_ease, current_repetitions
        )

        # Update streak
        new_streak = current_streak + 1 if is_correct else 0

        # Calculate next review time
        next_review = datetime.now() + timedelta(minutes=new_interval)

        # Update word
        cursor.execute('''
            UPDATE words
            SET interval = ?, repetitions = ?, ease_factor = ?, next_review = ?,
                last_reviewed = ?, streak = ?
            WHERE id = ?
        ''', (new_interval, new_ease, new_repetitions, next_review, datetime.now(), new_streak, word_id))

        # Insert review record
        cursor.execute('INSERT INTO reviews (word_id, correct, user_answer) VALUES (?, ?, ?)',
                      (word_id, is_correct, user_answer))

        conn.commit()
        conn.close()

        return jsonify({
            'correct': is_correct,
            'actual_answer': correct_answer,
            'streak': new_streak
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM words")
        total_words = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_reviews = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "total_words": total_words,
            "total_reviews": total_reviews,
            "system_status": "online"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
