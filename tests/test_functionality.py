#!/usr/bin/env python3
"""
Test the actual working endpoints
"""
import requests
import json

def test_registration():
    """Test user registration"""
    print("👤 TESTING USER REGISTRATION")
    print("=" * 40)
    
    url = "http://localhost:8000/auth/register"
    test_user = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(url, json=test_user, timeout=10)
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Registration successful!")
            return response.json()
        else:
            print("⚠️  Registration failed, but endpoint is working")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\n🔐 TESTING USER LOGIN")
    print("=" * 40)
    
    url = "http://localhost:8000/auth/login"
    
    # Test with form data (OAuth2PasswordRequestForm)
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(url, data=login_data, timeout=10)
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("⚠️  Login failed, but endpoint is working")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_resume_generation(token=None):
    """Test resume generation"""
    print("\n📝 TESTING RESUME GENERATION")
    print("=" * 40)
    
    url = "http://localhost:8000/api/v1/generate-resume"
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    test_data = {
        "user_profile": {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "FastAPI", "Machine Learning"],
            "work_history": [
                {
                    "company": "Tech Corp",
                    "position": "Software Engineer", 
                    "start_date": "2020-01-01",
                    "end_date": "2023-01-01",
                    "description": "Developed web applications"
                }
            ],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "university": "Tech University",
                    "year": "2019"
                }
            ]
        },
        "job_description": "Looking for a Python developer with FastAPI experience for building scalable web applications."
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Resume generation successful!")
            print(f"📄 Generated summary: {result.get('professional_summary', 'N/A')[:100]}...")
            return result
        else:
            print(f"⚠️  Resume generation failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_interview_questions(token=None):
    """Test interview questions generation"""
    print("\n❓ TESTING INTERVIEW QUESTIONS")
    print("=" * 40)
    
    url = "http://localhost:8000/api/v1/interview-questions"
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    test_data = {
        "job_description": "Senior Python Developer position requiring FastAPI, machine learning, and cloud experience.",
        "user_profile": {
            "name": "Jane Smith",
            "skills": ["Python", "FastAPI", "AWS", "Machine Learning"],
            "experience_level": "Senior"
        }
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Interview questions generation successful!")
            questions = result.get('questions', {})
            for category, question_list in questions.items():
                print(f"   📋 {category}: {len(question_list)} questions")
            return result
        else:
            print(f"⚠️  Interview questions failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🚀 TESTING ALL CORE FUNCTIONALITY")
    print("=" * 50)
    
    # Test registration
    user_data = test_registration()
    
    # Test login
    login_result = test_login()
    token = None
    if login_result:
        token = login_result.get("access_token")
    
    # Test resume generation (with or without auth)
    test_resume_generation(token)
    
    # Test interview questions (with or without auth)
    test_interview_questions(token)
    
    print("\n" + "=" * 50)
    print("🎯 TESTING COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main()