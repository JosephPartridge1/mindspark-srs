#!/usr/bin/env python3
"""
Test script for the /api/session/start endpoint
"""
import requests
import json
from datetime import datetime

def test_session_start():
    """Test the session start endpoint"""
    url = "http://localhost:5000/api/session/start"

    # Test data
    test_data = {
        "session_token": f"test_session_{int(datetime.now().timestamp())}",
        "start_time": datetime.now().isoformat()
    }

    print("🧪 Testing /api/session/start endpoint")
    print(f"📤 Sending data: {json.dumps(test_data, indent=2)}")

    try:
        response = requests.post(url, json=test_data, timeout=10)

        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ SUCCESS: Endpoint returned 200")
            print(f"📄 Response JSON: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ FAILED: Endpoint returned {response.status_code}")
            print(f"📄 Response text: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Could not connect to server. Is Flask running?")
        print("💡 Try running: python app.py")
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_session_start()
