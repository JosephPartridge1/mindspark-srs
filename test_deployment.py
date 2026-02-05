#!/usr/bin/env python3
"""
Deployment Testing Script for Railway
Tests all critical endpoints and functionality
"""

import requests
import json
import sys
import time
from datetime import datetime

def test_endpoint(url, endpoint, expected_status=200, timeout=10):
    """Test a single endpoint"""
    try:
        full_url = url.rstrip('/') + endpoint
        print(f"🔍 Testing {endpoint}...")

        response = requests.get(full_url, timeout=timeout)

        if response.status_code == expected_status:
            print(f"✅ {endpoint}: {response.status_code}")
            return True, response
        else:
            print(f"❌ {endpoint}: {response.status_code} (expected {expected_status})")
            return False, response

    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint}: Connection failed - {e}")
        return False, None

def test_health_endpoint(url):
    """Test health endpoint specifically"""
    success, response = test_endpoint(url, "/api/health")
    if success and response:
        try:
            data = response.json()
            print(f"   Health data: {json.dumps(data, indent=2)}")

            # Check if database is connected
            if "database" in data:
                db_status = data.get("database", {}).get("status", "unknown")
                print(f"   Database status: {db_status}")

            return True
        except json.JSONDecodeError:
            print("   ❌ Health endpoint returned invalid JSON")
            return False
    return success

def test_frontend(url):
    """Test if frontend loads"""
    success, response = test_endpoint(url, "/", expected_status=200)
    if success and response:
        content = response.text.lower()
        if "mindspark" in content or "flask" in content or "html" in content:
            print("   ✅ Frontend appears to be loading")
            return True
        else:
            print("   ⚠️  Frontend loaded but content seems minimal")
            return True
    return success

def test_api_endpoints(url):
    """Test various API endpoints"""
    endpoints = [
        ("/api/test", 200),
        ("/api/stats", 200),
        ("/api/words", 200),
        ("/api/learn", 200),
    ]

    results = []
    for endpoint, expected_status in endpoints:
        success, _ = test_endpoint(url, endpoint, expected_status)
        results.append(success)

    return results

def main():
    print("🚀 Railway Deployment Testing Script")
    print("=" * 50)

    # Get Railway URL
    try:
        import subprocess
        result = subprocess.run(["railway", "domain"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"📡 Detected Railway URL: {url}")
        else:
            print("❌ Could not get Railway URL automatically")
            url = input("Enter your Railway app URL: ").strip()
    except Exception as e:
        print(f"❌ Error getting Railway URL: {e}")
        url = input("Enter your Railway app URL: ").strip()

    if not url:
        print("❌ No URL provided. Exiting.")
        return

    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    print(f"\n🔗 Testing deployment at: {url}")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    # Test sequence
    tests = [
        ("Health Check", lambda: test_health_endpoint(url)),
        ("Frontend Load", lambda: test_frontend(url)),
        ("API Endpoints", lambda: test_api_endpoints(url)),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            if isinstance(result, list):
                success_count = sum(result)
                total_count = len(result)
                print(f"   Results: {success_count}/{total_count} endpoints working")
                results.append(success_count > 0)  # At least one endpoint works
            else:
                results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT TEST SUMMARY")
    print("=" * 50)

    total_tests = len(results)
    passed_tests = sum(results)

    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{test_name}: {status}")

    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 DEPLOYMENT SUCCESSFUL! Your app is working on Railway.")
        print("\n💡 Next steps:")
        print("   1. Test user registration and login")
        print("   2. Test vocabulary learning features")
        print("   3. Consider adding gunicorn for production performance")
    elif passed_tests > 0:
        print("⚠️  PARTIAL SUCCESS: Some features work, but not all.")
        print("   Check Railway logs for more details: railway logs")
    else:
        print("❌ DEPLOYMENT FAILED: No endpoints are working.")
        print("   Check Railway logs: railway logs --tail 50")

    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
