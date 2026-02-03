#!/usr/bin/env python3
"""
Test script to check database connection resilience
"""

import os
import sys
import json
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_resilience():
    """Test the database resilience module"""
    print("🧪 Testing Database Resilience Module")
    print("=" * 50)

    try:
        from database_resilience import get_resilient_connection, get_connection_status

        # Test 1: Get connection status
        print("📊 Getting connection status...")
        status = get_connection_status()
        print(f"Status: {json.dumps(status, indent=2, default=str)}")

        # Test 2: Get resilient connection
        print("\n🔌 Getting resilient connection...")
        start_time = time.time()
        conn = get_resilient_connection()
        elapsed = time.time() - start_time
        print(".2f")

        # Test 3: Check connection type
        db_type = getattr(conn, 'db_type', 'unknown')
        if hasattr(conn, 'is_mock') and conn.is_mock:
            db_type = 'mock'
        print(f"Database type: {db_type}")

        # Test 4: Test basic query
        print("\n🗃️ Testing basic query...")
        cursor = conn.cursor()
        cursor.execute('SELECT 1 as test')
        result = cursor.fetchone()
        cursor.close()
        print(f"Query result: {result}")

        # Test 5: Close connection
        conn.close()
        print("✅ Connection closed successfully")

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Endpoint")
    print("=" * 30)

    try:
        # Import Flask app
        from app import app

        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            data = response.get_json()

            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2, default=str)}")

            if response.status_code == 200 and data.get('status') == 'healthy':
                print("✅ Health endpoint working correctly")
                return True
            else:
                print("❌ Health endpoint not working")
                return False

    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

if __name__ == '__main__':
    print(f"🕐 Test started at {datetime.now().isoformat()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print()

    # Run tests
    resilience_ok = test_database_resilience()
    health_ok = test_health_endpoint()

    print("\n" + "=" * 50)
    if resilience_ok and health_ok:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        sys.exit(1)
