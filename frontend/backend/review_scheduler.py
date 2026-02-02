import sqlite3
from datetime import date, timedelta
from .main import DATABASE, SRSAlgorithm  # Import from main.py

def load_due_vocabulary(user_id: int):
    """
    Query database untuk kosakata yang harus diulang hari ini.
    Urutkan berdasarkan:
    a. Yang terlambat review (next_review_date paling lama lewat)
    b. Difficulty_score tertinggi
    c. Ease_factor terendah
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    today = date.today().isoformat()
    cursor.execute('''
        SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score,
               rs.next_review_date, rs.ease_factor, rs.interval_days, rs.repetition_count
        FROM vocabulary v
        JOIN review_sessions rs ON v.id = rs.vocab_id
        WHERE rs.user_id = ? AND rs.next_review_date <= ?
        ORDER BY
            CASE WHEN rs.next_review_date < ? THEN 0 ELSE 1 END,  -- Prioritize overdue
            rs.next_review_date ASC,  -- Most overdue first
            v.difficulty_score DESC,  -- Highest difficulty first
            rs.ease_factor ASC  -- Lowest ease first
    ''', (user_id, today, today))

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
            'ease_factor': row[7],
            'interval_days': row[8],
            'repetition_count': row[9]
        })

    conn.close()
    return due_vocab

def simulate_learning_curve(user_id: int, days: int = 30):
    """
    Simulasi sederhana: asumsi user menyelesaikan 10 kata/hari
    Prediksi jumlah kata yang akan dipertahankan (retention)
    Output: list retention_rate per hari
    """
    srs = SRSAlgorithm()
    retention_rates = []

    # Get initial due vocab
    due_vocab = load_due_vocabulary(user_id)
    total_vocab = len(due_vocab)

    if total_vocab == 0:
        return [0.0] * days

    # Simulate over days
    for day in range(days):
        # Assume user reviews 10 words per day, with quality 4 (good)
        reviews_today = min(10, len(due_vocab))
        retained = 0

        for i in range(reviews_today):
            vocab = due_vocab.pop(0)  # Review the first due vocab
            # Simulate review with quality 4
            result = srs.calculate_next_review(
                quality_response=4,
                current_interval=vocab['interval_days'],
                current_ease=vocab['ease_factor'],
                repetition_count=vocab['repetition_count']
            )
            # Assume retained if interval > 1
            if result['new_interval'] > 1:
                retained += 1
            # Update vocab (in simulation, add back if due again, but simplify)
            # For simplicity, assume all are retained and scheduled later

        # Calculate retention rate for the day
        retention_rate = retained / reviews_today if reviews_today > 0 else 0.0
        retention_rates.append(retention_rate)

        # For next day, assume new due vocab appear, but simplify: keep due_vocab as is or add more
        # This is a basic simulation; in reality, more complex

    return retention_rates
