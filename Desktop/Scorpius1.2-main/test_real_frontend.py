#!/usr/bin/env python3
import requests
import json

def test_real_frontend_format():
    """Test with the exact format the real frontend sends"""
    
    url = "http://localhost:8000/auth/register"
    
    # This is the EXACT format from the logs
    data = {
        "email": "guardefi@gmail.com",
        "password": "Ariella23!",
        "confirmPassword": "Ariella23!"
    }
    
    headers = {
        'Origin': 'http://localhost:3004',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Real frontend format registration successful!")
            result = response.json()
            print(f"Generated username: {result['user']['username']}")
            return True
        else:
            print("❌ Real frontend format registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing REAL frontend data format...")
    success = test_real_frontend_format()
    print(f"Test result: {'✅ PASSED' if success else '❌ FAILED'}") 