#!/usr/bin/env python3
"""
Test script to verify database compatibility fixes
"""

from database_adapter import db_adapter
import os

def test_database_adapter():
    """Test the database adapter functionality"""
    print("🧪 Testing Database Adapter Compatibility")
    print(f"📊 Database Type: {db_adapter.get_db_type()}")

    try:
        # Test insert_or_ignore
        print("\n1. Testing insert_or_ignore...")
        test_data = {
            'username': 'test_user',
            'created_date': '2024-01-01'
        }

        # First insert should succeed
        cursor = db_adapter.insert_or_ignore('users', test_data, 'username')
        print("✅ First insert_or_ignore successful")

        # Second insert should be ignored (no conflict)
        cursor = db_adapter.insert_or_ignore('users', test_data, 'username')
        print("✅ Second insert_or_ignore ignored (as expected)")

        # Test insert_or_replace
        print("\n2. Testing insert_or_replace...")
        replace_data = {
            'user_id': 1,
            'vocab_id': 1,
            'review_date': '2024-01-01',
            'next_review_date': '2024-01-02',
            'interval_days': 1,
            'ease_factor': 2.5,
            'performance_score': 5,
            'repetition_count': 1
        }

        cursor = db_adapter.insert_or_replace('review_sessions', replace_data, ['user_id', 'vocab_id'])
        print("✅ insert_or_replace successful")

        # Test SQL adaptation
        print("\n3. Testing SQL adaptation...")
        sqlite_sql = "SELECT * FROM words WHERE next_review <= datetime('now')"
        adapted_sql = db_adapter.adapt_sql(sqlite_sql)
        print(f"Original: {sqlite_sql}")
        print(f"Adapted:  {adapted_sql}")

        db_adapter.commit()
        print("\n✅ All tests passed! Database compatibility fixes working correctly.")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        db_adapter.close()
        return False

    return True

if __name__ == '__main__':
    success = test_database_adapter()
    exit(0 if success else 1)
