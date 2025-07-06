#!/usr/bin/env python3
import requests
import json

def test_frontend_registration():
    """Test registration exactly like the frontend would"""
    
    # Step 1: OPTIONS preflight request
    print("Step 1: Testing OPTIONS preflight request...")
    options_headers = {
        'Origin': 'http://localhost:3004',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'
    }
    
    try:
        options_response = requests.options(
            'http://localhost:8000/auth/register',
            headers=options_headers
        )
        print(f"OPTIONS Status: {options_response.status_code}")
        print(f"OPTIONS Headers: {dict(options_response.headers)}")
        
        if options_response.status_code != 200:
            print("❌ OPTIONS request failed!")
            return False
            
    except Exception as e:
        print(f"❌ OPTIONS request error: {e}")
        return False
    
    # Step 2: Actual POST request
    print("\nStep 2: Testing actual POST request...")
    post_headers = {
        'Origin': 'http://localhost:3004',
        'Content-Type': 'application/json'
    }
    
    data = {
        "username": "frontenduser",
        "email": "frontend@example.com",
        "password": "testpass123",
        "full_name": "Frontend User"
    }
    
    try:
        post_response = requests.post(
            'http://localhost:8000/auth/register',
            json=data,
            headers=post_headers
        )
        print(f"POST Status: {post_response.status_code}")
        print(f"POST Headers: {dict(post_response.headers)}")
        print(f"POST Response: {post_response.text}")
        
        if post_response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ POST request error: {e}")
        return False

if __name__ == "__main__":
    print("Testing frontend-like registration flow...")
    success = test_frontend_registration()
    print(f"\nOverall test: {'✅ PASSED' if success else '❌ FAILED'}") 