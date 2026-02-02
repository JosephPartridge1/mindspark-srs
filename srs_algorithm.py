from datetime import datetime, timedelta, date
import difflib

class SRSAlgorithm:
    def __init__(self):
        pass

    def calculate_srs(self, correct: bool, current_interval: int, ease_factor: float, repetitions: int):
        """
        Simplified SM-2 algorithm for Duolingo-style SRS.

        Parameters:
        - correct: boolean (True if user answered correctly)
        - current_interval: integer (current interval in minutes)
        - ease_factor: float (current ease factor)
        - repetitions: integer (current repetition count)

        Returns:
        - tuple: (new_interval, new_ease_factor, new_repetitions)
        """
        if correct:
            # Correct answer
            repetitions += 1
            if repetitions == 1:
                new_interval = 1  # 1 minute for first correct
            elif repetitions == 2:
                new_interval = 3  # 3 minutes for second correct
            else:
                new_interval = round(current_interval * ease_factor)

            new_ease_factor = min(ease_factor + 0.1, 3.0)
        else:
            # Incorrect answer
            repetitions = 0
            new_interval = max(1, current_interval // 2)  # Reset to 1 minute or half current
            new_ease_factor = max(1.3, ease_factor - 0.2)

        return new_interval, new_ease_factor, repetitions

    def fuzzy_match(self, user_answer: str, correct_answer: str, threshold: float = 0.8):
        """
        Check if user answer is similar enough to correct answer using fuzzy matching.

        Parameters:
        - user_answer: string (user's input)
        - correct_answer: string (correct answer)
        - threshold: float (similarity threshold, default 0.8)

        Returns:
        - boolean: True if similar enough
        """
        user_clean = user_answer.lower().strip()
        correct_clean = correct_answer.lower().strip()

        # Exact match
        if user_clean == correct_clean:
            return True

        # Fuzzy matching using difflib
        similarity = difflib.SequenceMatcher(None, user_clean, correct_clean).ratio()
        return similarity >= threshold

    def calculate_next_review(self, correct: bool, current_interval: int, current_ease: float, repetition_count: int):
        """
        Legacy method for backward compatibility - converts boolean to quality score.
        """
        quality_response = 5 if correct else 0
        return self.calculate_next_review_legacy(quality_response, current_interval, current_ease, repetition_count)

    def calculate_next_review_legacy(self, quality_response: int, current_interval: int, current_ease: float, repetition_count: int):
        """
        Legacy SM-2 implementation for backward compatibility.
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

        ease_factor = current_ease + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        today = datetime.now()
        next_review_date = today + timedelta(minutes=interval)  # Changed to minutes

        return {
            'new_interval': interval,
            'new_ease': ease_factor,
            'new_repetition_count': repetition_count,
            'next_review_date': next_review_date.isoformat()
        }

    def get_due_vocab(self, user_id: int, db_conn):
        """
        Mengembalikan kosakata yang next_review_date <= hari ini untuk user tertentu.

        Parameters:
        - user_id: integer
        - db_conn: database connection

        Returns:
        - list of dictionaries: [{'vocab_id': id, 'english_word': word, ...}, ...]
        """
        cursor = db_conn.cursor()

        today = date.today().isoformat()
        cursor.execute('''
            SELECT v.id, v.english_word, v.indonesian_meaning, v.part_of_speech, v.example_sentence, v.difficulty_score,
                   rs.next_review_date, rs.ease_factor, rs.interval_days, rs.repetition_count
            FROM vocabulary v
            JOIN review_sessions rs ON v.id = rs.vocab_id
            WHERE rs.user_id = ? AND rs.next_review_date <= ?
            ORDER BY
                CASE WHEN rs.next_review_date < ? THEN 0 ELSE 1 END,
                rs.next_review_date ASC,
                v.difficulty_score DESC,
                rs.ease_factor ASC
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

        return due_vocab
