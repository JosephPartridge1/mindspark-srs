from flask import Flask, jsonify, request, render_template, g, Response
from flask_cors import CORS
import sqlite3
import os
import csv
import io
import logging
from functools import wraps
from datetime import datetime, timedelta
from srs_algorithm import SRSAlgorithm
from db_init import init_database, check_database_health, detect_db_type

# Baris 1-10: Imports
from flask import Flask, jsonify, request, render_template, g, session
import os
import sys
import traceback
import sqlite3
from datetime import datetime, timedelta
from functools import wraps


# Baris 11-15: Definisikan app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')  # Ganti dengan key kuat

# Baris 16-30: Helper functions
def require_admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Cek session atau token auth
        if not session.get('is_admin'):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


# Setup logging for Railway deployment
def setup_logging():
    """Setup comprehensive logging for Railway environment"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler (always available)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler for Railway (write to /tmp/)
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        try:
            file_handler = logging.FileHandler('/tmp/app.log')
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            print("✅ Railway logging to /tmp/app.log enabled")
        except Exception as e:
            print(f"⚠️  Could not setup file logging: {e}")

    return logger

# Initialize logging
logger = setup_logging()
logger.info("🚀 Starting SRS Vocabulary App")

# Database path - use /tmp/ for Railway to avoid read-only filesystem issues
# Check for both RAILWAY_ENVIRONMENT and RAILWAY env vars
is_railway = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY')
DATABASE = '/tmp/srs_vocab.db' if is_railway else 'srs_vocab.db'
logger.info(f"📁 Using database path: {DATABASE}")

def get_db():
    if 'db' not in g:
        logger.info("🔌 Establishing database connection...")
        # Try PostgreSQL first (Railway)
        db_url = os.environ.get('DATABASE_URL')

        if db_url and db_url.startswith('postgres'):
            # Convert postgres:// to postgresql://
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)

            try:
                import psycopg2
                g.db = psycopg2.connect(db_url, sslmode='require')
                logger.info("✅ Connected to PostgreSQL database")
                # Note: PostgreSQL doesn't need row_factory like SQLite
            except ImportError:
                logger.warning("⚠️  PostgreSQL driver not available, falling back to SQLite")
                g.db = sqlite3.connect(DATABASE, check_same_thread=False)
                g.db.row_factory = sqlite3.Row
                logger.info("✅ Connected to SQLite database (fallback)")
        else:
            # Fallback to SQLite (built-in, always works)
            g.db = sqlite3.connect(DATABASE, check_same_thread=False)
            g.db.row_factory = sqlite3.Row
            logger.info("✅ Connected to SQLite database")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize database on app startup with new system
def init_app_database():
    """Initialize database using the new db_init system"""
    try:
        logger.info("🔍 Checking database health and initialization...")
        conn = get_db()

        # Check if database needs initialization
        health = check_database_health(conn)
        if not health['healthy']:
            logger.warning(f"⚠️  Database not healthy: {health.get('error', 'Unknown error')}")
            logger.info("🚀 Initializing database...")

            # Detect database type
            db_type = detect_db_type(conn)
            logger.info(f"📊 Detected database type: {db_type}")

            # Initialize database
            init_database(conn, db_type)
            logger.info("✅ Database initialization completed")
        else:
            logger.info("✅ Database is healthy and initialized")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
        raise

# Call database initialization on app startup
try:
    with app.app_context():
        init_app_database()
    logger.info("✅ Database initialization check completed")
except Exception as e:
    logger.critical(f"❌ Critical error during database setup: {e}", exc_info=True)
    raise

# Manual database initialization endpoint
@app.route('/api/init-db', methods=['POST'])
@require_admin_auth
def manual_init_db():
    """Manually trigger database initialization (admin only)"""
    try:
        logger.info("🔧 Manual database initialization requested")
        with app.app_context():
            conn = get_db()
            db_type = detect_db_type(conn)
            init_database(conn, db_type)
            health = check_database_health(conn)
            conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Database initialized successfully',
            'database_type': db_type,
            'health': health
        })

    except Exception as e:
        logger.error(f"❌ Manual database initialization failed: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Legacy database functions (kept for compatibility)
def ensure_database():
    """Legacy function - now handled by init_app_database()"""
    logger.warning("⚠️  ensure_database() is deprecated, using new init_app_database() instead")
    return True

try:
    srs = SRSAlgorithm()
    logger.info("✅ SRS Algorithm initialized")
except Exception as e:
    logger.error(f"❌ SRS Algorithm initialization failed: {e}", exc_info=True)
    raise

try:
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend
    logger.info("✅ Flask app created successfully")
except Exception as e:
    logger.error(f"❌ Flask app creation failed: {e}", exc_info=True)
    raise

# Admin authentication decorator
def require_admin_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        admin_token = os.environ.get('ADMIN_TOKEN', 'dev_admin_123')
        if not auth or auth != f'Bearer {admin_token}':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def init_db():
    logger.info("🗄️  Initializing database tables...")
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

        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT UNIQUE NOT NULL,
            user_ip TEXT,
            user_agent TEXT,
            start_time DATETIME NOT NULL,
            end_time DATETIME,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            accuracy_rate REAL DEFAULT 0.0,
            completed BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT NOT NULL,
            word_id INTEGER NOT NULL,
            user_answer TEXT NOT NULL,
            correct BOOLEAN NOT NULL,
            response_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_token) REFERENCES learning_sessions(session_token),
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
    logger.info("✅ Database tables initialized successfully")

def initialize_app():
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

@app.route('/health')
def health_check():
    """Health check endpoint for Railway deployment monitoring"""
    try:
        # Test database connection
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()

        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'db_path': DATABASE,
            'timestamp': datetime.now().isoformat(),
            'environment': 'railway' if os.environ.get('RAILWAY_ENVIRONMENT') else 'local'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'db_path': DATABASE,
            'timestamp': datetime.now().isoformat()
        }), 500

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

@app.route('/admin/stats')
@require_admin_auth
def admin_stats():
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Aggregate data
        cursor.execute('''
            SELECT
                COUNT(DISTINCT user_ip) as unique_users,
                COUNT(*) as total_sessions,
                SUM(total_questions) as total_questions,
                AVG(accuracy_rate) as avg_accuracy,
                MAX(end_time) as last_activity
            FROM learning_sessions
            WHERE end_time IS NOT NULL
        ''')
        stats = cursor.fetchone()

        # Recent sessions
        cursor.execute('''
            SELECT * FROM learning_sessions
            ORDER BY end_time DESC
            LIMIT 10
        ''')
        recent = cursor.fetchall()

        conn.close()

        return jsonify({
            "overview": dict(stats) if stats else {},
            "recent_sessions": [dict(row) for row in recent] if recent else []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/export/csv')
@require_admin_auth
def export_csv():
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Export semua data
        cursor.execute('''
            SELECT
                ls.user_ip,
                ls.start_time,
                ls.end_time,
                ls.total_questions,
                ls.correct_answers,
                ls.accuracy_rate,
                wa.word_id,
                wa.user_answer,
                wa.correct,
                wa.response_time
            FROM learning_sessions ls
            LEFT JOIN user_answers wa ON ls.session_token = wa.session_token
            ORDER BY ls.end_time DESC
        ''')
        data = cursor.fetchall()
        conn.close()

        # Convert to CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['User IP', 'Start Time', 'End Time', 'Total Questions',
                         'Correct Answers', 'Accuracy', 'Word ID', 'User Answer',
                         'Is Correct', 'Response Time (s)'])

        # Data
        for row in data:
            writer.writerow(row)

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=learning_data.csv"}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')





@app.route('/api/debug/test-insert')
def debug_test_insert():
    """Test insert data ke learning_sessions"""
    conn = sqlite3.connect('srs_vocab.db', check_same_thread=False)
    cursor = conn.cursor()

    try:
        # Coba insert test data
        test_token = f"test_{int(datetime.now().timestamp())}"
        cursor.execute('''
            INSERT INTO learning_sessions
            (session_token, start_time, total_questions, correct_answers, accuracy_rate)
            VALUES (?, ?, ?, ?, ?)
        ''', (test_token, datetime.now().isoformat(), 10, 8, 80.0))

        conn.commit()
        conn.close()

        return jsonify({
            "status": "test_insert_ok",
            "test_token": test_token
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def api_not_found(e):
    if request.path.startswith('/api'):
        return jsonify({"error": "API endpoint not found", "path": request.path}), 404
    return e

import sqlite3
import os
from datetime import datetime

@app.route('/api/debug/db')
def debug_database():
    """Check database status"""
    try:
        if not os.path.exists('srs_vocab.db'):
            return jsonify({
                "error": "Database file not found",
                "status": "missing"
            }), 404
        
        conn = sqlite3.connect('srs_vocab.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Count rows
        counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "status": "ok",
            "database": "srs_vocab.db",
            "exists": True,
            "tables": tables,
            "row_counts": counts,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/test')
def debug_test():
    """Simple test endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Flask is running",
        "time": datetime.now().isoformat()
    })

@app.route('/api/session/start', methods=['POST'])
def session_start():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO learning_sessions
            (session_token, start_time)
            VALUES (?, ?)
        ''', (data['session_token'], data['start_time']))

        conn.commit()
        return jsonify({"status": "started", "token": data['session_token']})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/session/complete', methods=['POST'])
def session_complete():
    data = request.get_json()

    # Validate required fields
    required = ['session_token', 'total_questions', 'correct_answers', 'accuracy_rate']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE learning_sessions
            SET end_time = CURRENT_TIMESTAMP,
                total_questions = ?,
                correct_answers = ?,
                accuracy_rate = ?,
                completed = 1
            WHERE session_token = ?
        ''', (
            data['total_questions'],
            data['correct_answers'],
            data['accuracy_rate'],
            data['session_token']
        ))

        conn.commit()
        return jsonify({
            "status": "completed",
            "updated": cursor.rowcount
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/session/answer', methods=['POST'])
def session_answer():
    data = request.get_json()
    print(f"📥 Received answer data: {data}")  # LOG untuk debug

    # VALIDASI DATA
    required_fields = ['session_token', 'word_id', 'user_answer', 'correct', 'response_time']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing field: {field}",
                "received": data
            }), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # CEK: apakah session_token valid?
        cursor.execute('SELECT 1 FROM learning_sessions WHERE session_token = ?',
                      (data['session_token'],))
        if not cursor.fetchone():
            return jsonify({"error": "Invalid session_token"}), 400

        # INSERT dengan error detail - menggunakan kolom 'timestamp' yang ada
        cursor.execute('''
            INSERT INTO user_answers
            (session_token, word_id, user_answer, correct, response_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['session_token'],
            data['word_id'],
            data['user_answer'],
            bool(data['correct']),  # Convert to boolean
            float(data['response_time'])  # Convert to float
        ))

        conn.commit()
        return jsonify({
            "status": "answer_saved",
            "answer_id": cursor.lastrowid
        })

    except sqlite3.IntegrityError as e:
        return jsonify({
            "error": "Database integrity error",
            "details": str(e),
            "data_sent": data
        }), 400
    except Exception as e:
        import traceback
        return jsonify({
            "error": "Server error",
            "details": str(e),
            "traceback": traceback.format_exc()
        }), 500
    finally:
        conn.close()

if __name__ == '__main__':
    import os
    import sys
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 App starting in {'RAILWAY' if is_railway else 'LOCAL'} mode")
    logger.info(f"📁 Database path: {DATABASE}")
    logger.info(f"🌐 Port: {port}")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info(f"🌐 Starting Flask server on port {port}")
    initialize_app()
    app.run(host='0.0.0.0', port=port, debug=False)
