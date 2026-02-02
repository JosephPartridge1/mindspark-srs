import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta

def plot_review_schedule(user_id, db_path='vocabulary_app.db'):
    '''Plot jumlah review per hari untuk 30 hari ke depan'''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query data
    cursor.execute('''
        SELECT next_review_date, COUNT(*) 
        FROM review_sessions 
        WHERE user_id = ? 
        GROUP BY next_review_date
    ''', (user_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    # Proses data
    dates = [row[0] for row in data]
    counts = [row[1] for row in data]
    
    # Plot
    plt.figure(figsize=(10, 5))
    plt.bar(dates, counts)
    plt.xlabel('Tanggal Review')
    plt.ylabel('Jumlah Kata')
    plt.title('Jadwal Review')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_retention_curve(user_id, db_path='vocabulary_app.db'):
    '''Plot retensi berdasarkan performa review'''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT review_date, performance_score 
        FROM review_sessions 
        WHERE user_id = ? 
        ORDER BY review_date
    ''', (user_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("Tidak ada data untuk user ini.")
        return
    
    # Hitung retensi kumulatif
    dates = []
    retention_rates = []
    total_correct = 0
    total_reviews = 0
    
    for i, (date, score) in enumerate(data):
        total_reviews += 1
        if score >= 3:  # Score 3-5 dianggap berhasil
            total_correct += 1
        
        if i % 5 == 0 or i == len(data) - 1:  # Ambil sampel setiap 5 review
            dates.append(date[:10])  # Ambil hanya tanggal
            retention_rates.append((total_correct / total_reviews) * 100)
    
    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(dates, retention_rates, marker='o')
    plt.xlabel('Tanggal')
    plt.ylabel('Retensi (%)')
    plt.title('Kurva Retensi')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def generate_report(user_id, db_path='vocabulary_app.db'):
    '''Generate laporan statistik sederhana'''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query statistik
    cursor.execute('SELECT COUNT(*) FROM review_sessions WHERE user_id = ?', (user_id,))
    total_reviews = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(DISTINCT vocab_id) 
        FROM review_sessions 
        WHERE user_id = ? AND performance_score >= 3
    ''', (user_id,))
    mastered_words = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT AVG(ease_factor) 
        FROM review_sessions 
        WHERE user_id = ?
    ''', (user_id,))
    avg_ease = cursor.fetchone()[0] or 0
    
    cursor.execute('''
        SELECT COUNT(*) 
        FROM review_sessions 
        WHERE user_id = ? 
        AND next_review_date <= date('now')
    ''', (user_id,))
    due_cards = cursor.fetchone()[0]
    
    conn.close()
    
    # Print report
    print("\n" + "="*50)
    print("LAPORAN STATISTIK BELAJAR")
    print("="*50)
    print(f"User ID: {user_id}")
    print(f"Total Review: {total_reviews}")
    print(f"Kata yang dikuasai: {mastered_words}")
    print(f"Rata-rata ease factor: {avg_ease:.2f}")
    print(f"Kata yang perlu diulang besok: {due_cards}")
    print("="*50)
    return {
        'total_reviews': total_reviews,
        'mastered_words': mastered_words,
        'avg_ease': avg_ease,
        'due_cards': due_cards
    }
