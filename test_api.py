#!/usr/bin/env python3
import requests
import json

def test_api():
    base_url = "http://localhost:8000/api"

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")

    # Test login endpoint
    try:
        response = requests.post(f"{base_url}/login",
                               json={"email": "sample@gmail.com", "password": "12345"},
                               headers={"Content-Type": "application/json"})
        print(f"Login: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Login failed: {e}")

    # Test register endpoint
    try:
        response = requests.post(f"{base_url}/register",
                               json={"email": "test@example.com", "password": "testpass", "name": "Test User"},
                               headers={"Content-Type": "application/json"})
        print(f"Register: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Register failed: {e}")

if __name__ == "__main__":
    test_api()
