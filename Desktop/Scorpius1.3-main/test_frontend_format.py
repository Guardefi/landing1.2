#!/usr/bin/env python3
import requests
import json

def test_frontend_format():
    """Test registration with frontend data format"""
    
    url = "http://localhost:8000/auth/register"
    
    # This is the exact format the frontend sends
    data = {
        "email": "test@frontend.com",
        "username": "testuser123",
        "password": "testpass123",
        "firstName": "John",
        "lastName": "Doe",
        "acceptTerms": True,
        "marketingOptIn": False
    }
    
    headers = {
        'Origin': 'http://localhost:3004',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Frontend format registration successful!")
            return True
        else:
            print("❌ Frontend format registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing frontend data format...")
    success = test_frontend_format()
    print(f"Test result: {'✅ PASSED' if success else '❌ FAILED'}") 