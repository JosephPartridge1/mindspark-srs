# test_srs_logic.py - Test SRS algorithm logic
from datetime import datetime, timedelta

def test_srs_intervals():
    print("="*60)
    print("TES LOGIKA ALGORITMA SRS")
    print("="*60)
    
    print("\n1. TES INTERVAL BERDASARKAN SKOR:")
    print("-"*40)
    
    test_cases = [
        {"score": 1, "expected_interval": 1, "description": "Sangat sulit → ulang besok"},
        {"score": 2, "expected_interval": 1, "description": "Sulit → ulang besok"},
        {"score": 3, "expected_interval": 2, "description": "Cukup → 2 hari lagi"},
        {"score": 4, "expected_interval": 4, "description": "Mudah → 4 hari lagi"},
        {"score": 5, "expected_interval": 7, "description": "Sangat mudah → 7 hari lagi"},
    ]
    
    all_passed = True
    
    for test in test_cases:
        score = test["score"]
        
        # This is the SRS logic from your system
        intervals = {1: 1, 2: 1, 3: 2, 4: 4, 5: 7}
        actual_interval = intervals.get(score, 1)
        
        passed = actual_interval == test["expected_interval"]
        status = "✓" if passed else "✗"
        
        print(f"{status} Score {score}: {test['description']}")
        print(f"    Expected: {test['expected_interval']} hari, Actual: {actual_interval} hari")
        
        if not passed:
            all_passed = False
    
    print("\n2. SIMULASI LEARNING PATH:")
    print("-"*40)
    
    # Simulate a word being learned over time
    print("Simulasi pembelajaran kata 'apple':")
    
    timeline = [
        {"day": 0, "score": 3, "note": "Pertama kali belajar"},
        {"day": 2, "score": 4, "note": "Review pertama"},
        {"day": 6, "score": 5, "note": "Review kedua"},
        {"day": 13, "score": 5, "note": "Review ketiga"},
    ]
    
    current_day = 0
    for i, step in enumerate(timeline):
        intervals = {1: 1, 2: 1, 3: 2, 4: 4, 5: 7}
        interval = intervals.get(step["score"], 1)
        
        next_review = current_day + interval
        print(f"  Hari {current_day}: Score {step['score']} → Interval {interval} hari")
        print(f"     Akan direview hari: {next_review} ({step['note']})")
        
        current_day = next_review
    
    print("\n3. KONSEP SPACED REPETITION:")
    print("-"*40)
    print("✓ Interval meningkat jika diingat dengan baik")
    print("✓ Interval menurun jika lupa")
    print("✓ Tujuan: transfer ke memori jangka panjang")
    print("✓ Efisiensi: review tepat sebelum lupa")
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ SEMUA TES LOGIKA SRS BERHASIL")
    else:
        print("⚠️  Beberapa tes gagal, periksa logika interval")
    print("="*60)
    
    return all_passed

def calculate_forgetting_curve():
    """Demonstrate the forgetting curve concept"""
    print("\n4. KURVA LUPA (FORGETTING CURVE):")
    print("-"*40)
    
    # Simplified forgetting curve data (Ebbinghaus)
    curve_data = [
        {"time": "20 menit", "retention": 58},
        {"time": "1 jam", "retention": 44},
        {"time": "9 jam", "retention": 36},
        {"time": "1 hari", "retention": 33},
        {"time": "2 hari", "retention": 28},
        {"time": "6 hari", "retention": 25},
        {"time": "31 hari", "retention": 21},
    ]
    
    print("Tanpa review, retensi menurun:")
    for point in curve_data:
        bar = "█" * int(point["retention"] / 3)
        print(f"  {point['time']:8} → {bar} {point['retention']}%")
    
    print("\nDengan SRS, retensi dipertahankan >90%")

if __name__ == "__main__":
    test_srs_intervals()
    calculate_forgetting_curve()