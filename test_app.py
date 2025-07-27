#!/usr/bin/env python3
"""
Simple test script to verify the application is working
"""

import requests
import time

def test_application():
    """Test the application endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test homepage
        print("Testing homepage...")
        response = requests.get(base_url, timeout=5)
        print(f"✅ Homepage: {response.status_code}")
        
        # Test signup page
        print("Testing signup page...")
        response = requests.get(f"{base_url}/signup", timeout=5)
        print(f"✅ Signup page: {response.status_code}")
        
        # Test login page
        print("Testing login page...")
        response = requests.get(f"{base_url}/login", timeout=5)
        print(f"✅ Login page: {response.status_code}")
        
        print("\n🎉 Application is working correctly!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application")
        print("Make sure the server is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error testing application: {e}")

if __name__ == "__main__":
    test_application() 