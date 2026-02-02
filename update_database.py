import sqlite3

def update_schema():
    conn = sqlite3.connect('srs_vocab.db')
    cursor = conn.cursor()

    print("🔧 Updating database schema...")

    # 1. CEK STRUKTUR SAAT INI
    cursor.execute("PRAGMA table_info(user_answers)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Current columns in user_answers:", columns)

    # 2. TAMBAHKAN KOLOM JIKA BELUM ADA
    if 'answered_at' not in columns:
        print("➕ Adding 'answered_at' column to user_answers...")
        cursor.execute('''
            ALTER TABLE user_answers
            ADD COLUMN answered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ''')
        print("✅ Column added")
    else:
        print("✅ Column 'answered_at' already exists")

    # 3. CEK KOLOM LAIN YANG MUNGKIN HILANG
    required_columns = ['session_token', 'word_id', 'user_answer', 'correct', 'response_time', 'answered_at']
    for col in required_columns:
        if col not in columns and col != 'answered_at':
            print(f"⚠️  Missing column: {col}")

    conn.commit()
    conn.close()
    print("🎉 Database schema updated successfully!")

if __name__ == '__main__':
    update_schema()
