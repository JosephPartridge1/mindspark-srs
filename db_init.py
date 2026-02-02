"""
Database initialization module for SRS Vocabulary App
Supports both PostgreSQL (Railway) and SQLite (local development)
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Schema definitions for both databases
SCHEMA_SQLITE = {
    'words': '''
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
        )
    ''',
    'reviews': '''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            correct BOOLEAN NOT NULL,
            response_time REAL,
            user_answer TEXT NOT NULL,
            FOREIGN KEY(word_id) REFERENCES words(id)
        )
    ''',
    'learning_sessions': '''
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
        )
    ''',
    'user_answers': '''
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
        )
    '''
}

SCHEMA_POSTGRESQL = {
    'words': '''
        CREATE TABLE IF NOT EXISTS words (
            id SERIAL PRIMARY KEY,
            english TEXT NOT NULL,
            indonesian TEXT NOT NULL,
            part_of_speech TEXT DEFAULT 'noun',
            example_sentence TEXT DEFAULT '',
            difficulty_score FLOAT DEFAULT 1.0,
            interval INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            next_review TIMESTAMP,
            last_reviewed TIMESTAMP,
            streak INTEGER DEFAULT 0,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    'reviews': '''
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            word_id INTEGER NOT NULL,
            review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            correct BOOLEAN NOT NULL,
            response_time REAL,
            user_answer TEXT NOT NULL,
            FOREIGN KEY(word_id) REFERENCES words(id)
        )
    ''',
    'learning_sessions': '''
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id SERIAL PRIMARY KEY,
            session_token TEXT UNIQUE NOT NULL,
            user_ip TEXT,
            user_agent TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            accuracy_rate REAL DEFAULT 0.0,
            completed BOOLEAN DEFAULT FALSE
        )
    ''',
    'user_answers': '''
        CREATE TABLE IF NOT EXISTS user_answers (
            id SERIAL PRIMARY KEY,
            session_token TEXT NOT NULL,
            word_id INTEGER NOT NULL,
            user_answer TEXT NOT NULL,
            correct BOOLEAN NOT NULL,
            response_time REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_token) REFERENCES learning_sessions(session_token),
            FOREIGN KEY(word_id) REFERENCES words(id)
        )
    '''
}

# Seed data
SEED_DATA = [
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
]

def get_schema_for_db(db_type):
    """Get appropriate schema based on database type"""
    if db_type == 'postgresql':
        return SCHEMA_POSTGRESQL
    else:
        return SCHEMA_SQLITE

def detect_db_type(connection):
    """Detect database type from connection"""
    try:
        # Try PostgreSQL-specific query
        cursor = connection.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        if version and 'postgresql' in version[0].lower():
            return 'postgresql'
    except:
        pass

    # Default to SQLite
    return 'sqlite'

def create_tables(connection, db_type=None):
    """Create all required tables"""
    if db_type is None:
        db_type = detect_db_type(connection)

    logger.info(f"🗄️  Creating tables for {db_type} database...")

    schema = get_schema_for_db(db_type)
    cursor = connection.cursor()

    try:
        for table_name, create_sql in schema.items():
            logger.info(f"📋 Creating table: {table_name}")
            cursor.execute(create_sql)

        connection.commit()
        logger.info("✅ All tables created successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        connection.rollback()
        raise

def insert_seed_data(connection, db_type=None):
    """Insert seed data if tables are empty"""
    if db_type is None:
        db_type = detect_db_type(connection)

    logger.info("🌱 Checking for seed data insertion...")

    cursor = connection.cursor()

    try:
        # Check if words table is empty
        cursor.execute("SELECT COUNT(*) FROM words")
        count = cursor.fetchone()[0]

        if count == 0:
            logger.info("📝 Inserting seed data...")

            if db_type == 'postgresql':
                # PostgreSQL uses %s for placeholders
                cursor.executemany('''
                    INSERT INTO words (english, indonesian, part_of_speech, example_sentence, difficulty_score)
                    VALUES (%s, %s, %s, %s, %s)
                ''', SEED_DATA)
            else:
                # SQLite uses ? for placeholders
                cursor.executemany('''
                    INSERT INTO words (english, indonesian, part_of_speech, example_sentence, difficulty_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', SEED_DATA)

            connection.commit()
            logger.info(f"✅ Inserted {len(SEED_DATA)} seed words")
        else:
            logger.info(f"✅ Seed data already exists ({count} words found)")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to insert seed data: {e}")
        connection.rollback()
        raise

def init_database(connection, db_type=None):
    """
    Complete database initialization
    Returns True if successful, raises exception on failure
    """
    start_time = datetime.now()
    logger.info("🚀 Starting database initialization...")

    try:
        # Create tables
        create_tables(connection, db_type)

        # Insert seed data
        insert_seed_data(connection, db_type)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"✅ Database initialization completed successfully in {duration:.2f}s")
        return True

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.error(f"❌ Database initialization failed after {duration:.2f}s: {e}")
        raise

def check_database_health(connection):
    """Check if database is properly initialized and healthy"""
    try:
        cursor = connection.cursor()

        # Check if all required tables exist
        required_tables = ['words', 'reviews', 'learning_sessions', 'user_answers']
        existing_tables = []

        if detect_db_type(connection) == 'postgresql':
            cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]

        missing_tables = [t for t in required_tables if t not in existing_tables]

        if missing_tables:
            return {
                'healthy': False,
                'error': f'Missing tables: {missing_tables}',
                'tables_exist': existing_tables
            }

        # Check word count
        cursor.execute("SELECT COUNT(*) FROM words")
        word_count = cursor.fetchone()[0]

        return {
            'healthy': True,
            'word_count': word_count,
            'tables_exist': existing_tables
        }

    except Exception as e:
        return {
            'healthy': False,
            'error': str(e)
        }
