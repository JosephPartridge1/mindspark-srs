from flask import Flask, jsonify, request, render_template, g, Response
from flask_cors import CORS
import sqlite3
import os
import csv
import io
from functools import wraps
from datetime import datetime, timedelta
from srs_algorithm import SRSAlgorithm

srs = SRSAlgorithm()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for frontend

DATABASE = 'srs_vocab.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            indonesian TEXT NOT NULL,
            part_of_speech TEXT DEFAULT 'noun',
            example_sentence TEXT DEFAULT '',
            difficulty_score FLOAT DEFAULT 1.0,
            interval INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            next_review DATETIME,
            last_reviewed DATETIME,
            streak INTEGER DEFAULT 0,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            correct BOOLEAN NOT NULL,
            response_time REAL,
            user_answer TEXT NOT NULL,
            FOREIGN KEY(word_id) REFERENCES words(id)
        );

        -- Seed data with 10 words
        INSERT OR IGNORE INTO words (english, indonesian, part_of_speech, example_sentence, difficulty_score) VALUES
        ('apple', 'apel', 'noun', 'I eat an apple every day.', 1.0),
        ('book', 'buku', 'noun', 'This is an interesting book.', 1.0),
        ('run', 'berlari', 'verb', 'She likes to run in the park.', 1.5),
        ('happy', 'bahagia', 'adjective', 'The child looks very happy.', 1.2),
        ('computer', 'komputer', 'noun', 'I use a computer for work.', 2.0),
        ('algorithm', 'algoritma', 'noun', 'The algorithm solves complex problems.', 3.0),
        ('ephemeral', 'sementara', 'adjective', 'Life is ephemeral and fleeting.', 4.0),
        ('ubiquitous', 'dimana-mana', 'adjective', 'Smartphones are ubiquitous nowadays.', 3.5),
        ('serendipity', 'kebetulan baik', 'noun', 'Finding this book was pure serendipity.', 4.5),
        ('quintessential', 'paling murni', 'adjective', 'This dish is the quintessential Italian pasta.', 4.2);
    """)
    db.commit()

# Initialize database on app startup
with app.app_context():
    init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/words')
def get_words():
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Get all words
        cursor.execute('SELECT id, english, indonesian, part_of_speech, example_sentence FROM words ORDER BY id')
        words = []
        for row in cursor.fetchall():
            words.append({
                'id': row[0],
                'english': row[1],
                'indonesian': row[2],
                'part_of_speech': row[3],
                'example_sentence': row[4]
            })

        conn.close()
        return jsonify({'words': words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/apiAction', methods=['POST'])
def api_action():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Expected data: vocab_id, quality_response (0-5)
        vocab_id = data.get('vocab_id')
        quality_response = data.get('quality_response')

        if vocab_id is None or quality_response is None:
            return jsonify({'error': 'vocab_id and quality_response required'}), 400

        # Get current review data for the vocab (simplified, assuming latest review)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ease_factor, interval_days, repetition_count
            FROM reviews
            WHERE word_id = ?
            ORDER BY review_date DESC
            LIMIT 1
        ''', (vocab_id,))
        row = cursor.fetchone()

        current_ease = row[0] if row else 2.5
        current_interval = row[1] if row else 1
        repetition_count = row[2] if row else 0

        # Calculate next review using SRS algorithm
        result = srs.calculate_next_review(quality_response, current_interval, current_ease, repetition_count)

        # Update database with new review
        next_date = datetime.now() + timedelta(days=result['new_interval'])
        cursor.execute('''
            INSERT INTO reviews (word_id, score, next_review_date, interval_days, ease_factor, repetition_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (vocab_id, quality_response, next_date, result['new_interval'], result['new_ease'], result['new_repetition_count']))

        conn.commit()
        conn.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM words")
        total_words = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reviews WHERE date(review_date) = date('now')")
        today_reviews = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reviews WHERE next_review_date <= date('now')")
        due_reviews = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "total_words": total_words,
            "today_reviews": today_reviews,
            "due_reviews": due_reviews,
            "system_status": "online"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        anon_code = data.get('anon_code')
        class_name = data.get('class_name')

        if not anon_code:
            return jsonify({'error': 'anon_code required'}), 400

        # For simplicity, return user_id=1 for any anon_code
        return jsonify({'user_id': 1})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/session/start')
def start_session():
    try:
        user_id = request.args.get('user_id', type=int)
        size = request.args.get('size', 10, type=int)

        if not user_id:
            return jsonify({'error': 'user_id required'}), 400

        # Get due vocabularies
        conn = get_db()
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
            LIMIT ?
        ''', (today, today, size))

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

        # Format for frontend
        items = []
        for vocab in due_vocab:
            items.append({
                'id': vocab['vocab_id'],
                'english': vocab['english_word'],
                'indonesian': vocab['indonesian_meaning'],
                'part_of_speech': vocab['part_of_speech'],
                'example_sentence': vocab['example_sentence']
            })

        return jsonify({'items': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/session/answer', methods=['POST'])
def submit_answer():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        item_id = data.get('item_id')
        quality = data.get('quality')  # 'correct', 'partial', 'wrong'
        hint_used = data.get('hint_used', False)

        if not all([user_id, item_id, quality]):
            return jsonify({'error': 'user_id, item_id, quality required'}), 400

        # Map quality to SRS score (0-5)
        quality_map = {'wrong': 0, 'partial': 3, 'correct': 5}
        srs_score = quality_map.get(quality, 3)

        # Get current review data
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ease_factor, interval_days, repetition_count
            FROM reviews
            WHERE word_id = ?
            ORDER BY review_date DESC
            LIMIT 1
        ''', (item_id,))
        row = cursor.fetchone()

        current_ease = row[0] if row else 2.5
        current_interval = row[1] if row else 1
        repetition_count = row[2] if row else 0

        # Calculate next review
        result = srs.calculate_next_review(srs_score, current_interval, current_ease, repetition_count)

        # Update database
        next_date = datetime.now() + timedelta(days=result['new_interval'])
        cursor.execute('''
            INSERT INTO reviews (word_id, score, next_review_date, interval_days, ease_factor, repetition_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (item_id, srs_score, next_date, result['new_interval'], result['new_ease'], result['new_repetition_count']))

        conn.commit()
        conn.close()

        return jsonify({'next_review': result['next_review_date']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/learn')
def get_learn():
    try:
        conn = get_db()
        cursor = conn.cursor()

        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT w.id, w.english, w.indonesian, w.part_of_speech, w.example_sentence
            FROM words w
            LEFT JOIN reviews r ON w.id = r.word_id
            WHERE r.next_review_date IS NULL OR r.next_review_date <= ?
            ORDER BY r.next_review_date ASC
            LIMIT 10
        ''', (today,))

        words = []
        for row in cursor.fetchall():
            words.append({
                'id': row[0],
                'english': row[1],
                'indonesian': row[2],
                'part_of_speech': row[3],
                'example_sentence': row[4]
            })

        conn.close()
        return jsonify({'words': words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/review', methods=['POST'])
def post_review():
    if request.method != 'POST':
        return jsonify({"error": "Method not allowed"}), 405

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        word_id = data.get('word_id')
        score = data.get('score')

        if word_id is None or score is None:
            return jsonify({'error': 'word_id and score required'}), 400

        # Get current review data
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ease_factor, interval_days, repetition_count
            FROM reviews
            WHERE word_id = ?
            ORDER BY review_date DESC
            LIMIT 1
        ''', (word_id,))
        row = cursor.fetchone()

        current_ease = row[0] if row else 2.5
        current_interval = row[1] if row else 1
        repetition_count = row[2] if row else 0

        # Calculate next review
        result = srs.calculate_next_review(score, current_interval, current_ease, repetition_count)

        # Update database
        next_date = datetime.now() + timedelta(days=result['new_interval'])
        cursor.execute('''
            INSERT INTO reviews (word_id, score, next_review_date, interval_days, ease_factor, repetition_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (word_id, score, next_date, result['new_interval'], result['new_ease'], result['new_repetition_count']))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'next_review': result['next_review_date']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test')
def test_connection():
    return jsonify({'status': 'ok'})

@app.route('/api/next-word')
def get_next_word():
    """
    Get the next word due for review (Duolingo-style).
    Returns the word with the earliest next_review date.
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        now = datetime.now()
        cursor.execute('''
            SELECT w.id, w.english, w.indonesian, w.part_of_speech, w.example_sentence,
                   w.interval, w.repetitions, w.ease_factor, w.next_review, w.streak
            FROM words w
            WHERE w.next_review IS NULL OR w.next_review <= ?
            ORDER BY
                CASE WHEN w.next_review IS NULL THEN 0 ELSE 1 END,
                w.next_review ASC
            LIMIT 1
        ''', (now,))

        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'No words due for review'}), 404

        word = {
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
        }

        conn.close()
        return jsonify(word)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer_duolingo():
    """
    Submit user's answer for a word (Duolingo-style typing exercise).
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        word_id = data.get('word_id')
        user_answer = data.get('user_answer', '').strip()
        response_time = data.get('response_time', 0.0)

        if word_id is None or user_answer is None:
            return jsonify({'error': 'word_id and user_answer required'}), 400

        conn = get_db()
        cursor = conn.cursor()

        # Get word details
        cursor.execute('SELECT english, indonesian, interval, repetitions, ease_factor, streak FROM words WHERE id = ?', (word_id,))
        word_row = cursor.fetchone()
        if not word_row:
            return jsonify({'error': 'Word not found'}), 404

        correct_answer = word_row[1]  # indonesian
        current_interval = word_row[2] or 1
        current_repetitions = word_row[3] or 0
        current_ease = word_row[4] or 2.5
        current_streak = word_row[5] or 0

        # Check if answer is correct (with fuzzy matching)
        is_correct = srs.fuzzy_match(user_answer, correct_answer)

        # Calculate new SRS values
        new_interval, new_ease, new_repetitions = srs.calculate_srs(
            is_correct, current_interval, current_ease, current_repetitions
        )

        # Update streak
        new_streak = current_streak + 1 if is_correct else 0

        # Calculate next review time
        next_review = datetime.now() + timedelta(minutes=new_interval)

        # Update word in database
        cursor.execute('''
            UPDATE words
            SET interval = ?, repetitions = ?, ease_factor = ?, next_review = ?,
                last_reviewed = ?, streak = ?
            WHERE id = ?
        ''', (new_interval, new_repetitions, new_ease, next_review, datetime.now(), new_streak, word_id))

        # Insert review record
        cursor.execute('''
            INSERT INTO reviews (word_id, correct, response_time, user_answer)
            VALUES (?, ?, ?, ?)
        ''', (word_id, is_correct, response_time, user_answer))

        conn.commit()
        conn.close()

        # Calculate interval increase for feedback
        interval_increase = ""
        if is_correct:
            if new_interval > current_interval:
                interval_increase = f"+{new_interval - current_interval} min"
            else:
                interval_increase = "Same interval"
        else:
            interval_increase = f"Reset to {new_interval} min"

        return jsonify({
            'correct': is_correct,
            'actual_answer': correct_answer,
            'next_review_in': next_review.isoformat(),
            'streak': new_streak,
            'interval_increase': interval_increase
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/due-count')
def get_due_count():
    """
    Get count of words due for review.
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        now = datetime.now()
        cursor.execute('''
            SELECT COUNT(*) FROM words
            WHERE next_review IS NULL OR next_review <= ?
        ''', (now,))

        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({'due_count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings')
def get_settings():
    return jsonify({"theme": "dark", "language": "en"})

@app.errorhandler(404)
def api_not_found(e):
    if request.path.startswith('/api'):
        return jsonify({"error": "API endpoint not found", "path": request.path}), 404
    return e

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
