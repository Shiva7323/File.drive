#!/usr/bin/env python3
import requests
import time

def test_server():
    try:
        print("Testing server connection...")
        response = requests.get('http://127.0.0.1:5000', timeout=5)
        print(f"Server is running! Status code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("Server is not running or not accessible")
        return False
    except Exception as e:
        print(f"Error testing server: {e}")
        return False

if __name__ == "__main__":
    test_server() 