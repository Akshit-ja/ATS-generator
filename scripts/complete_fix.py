#!/usr/bin/env python3
"""
Complete project fix - test all functionality and identify issues
"""
import requests
import json

def test_registration():
    """Test user registration with correct format"""
    print("🔧 TESTING REGISTRATION")
    
    url = "http://localhost:8000/auth/register"
    
    # Test with new user
    test_data = {
        "username": "newuser2024",
        "email": "newuser2024@test.com",
        "password": "securepass123",
        "full_name": "Test User 2024"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ Registration successful!")
            user_data = response.json()
            print(f"👤 User created: {user_data}")
            return True
        elif response.status_code == 400:
            print("⚠️  User already exists or validation error")
            error_data = response.json()
            print(f"Error: {error_data}")
            return False
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login_json():
    """Test login with JSON format"""
    print("\n🔑 TESTING LOGIN (JSON)")
    
    url = "http://localhost:8000/auth/login"
    
    # Try JSON format
    login_data = {
        "username": "newuser2024@test.com",
        "password": "securepass123"
    }
    
    try:
        response = requests.post(url, json=login_data, timeout=10)
        print(f"📡 JSON Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            access_token = token_data.get('access_token')
            print(f"🎫 Token: {access_token[:30]}...")
            return access_token
        else:
            print(f"❌ JSON Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ JSON Login error: {e}")
        return None

def test_login_form():
    """Test login with form data"""
    print("\n🔑 TESTING LOGIN (FORM DATA)")
    
    url = "http://localhost:8000/auth/login"
    
    # Try form data format
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    login_data = {
        "username": "newuser2024@test.com",
        "password": "securepass123"
    }
    
    try:
        response = requests.post(url, data=login_data, headers=headers, timeout=10)
        print(f"📡 Form Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Form login successful!")
            access_token = token_data.get('access_token')
            print(f"🎫 Token: {access_token[:30]}...")
            return access_token
        else:
            print(f"❌ Form login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Form login error: {e}")
        return None

def test_ai_features(token):
    """Test AI features (resume and interview questions)"""
    print(f"\n🤖 TESTING AI FEATURES (Token: {'Yes' if token else 'No'})")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Test Resume Generation
    print("\n📄 Testing Resume Generation...")
    resume_url = "http://localhost:8000/api/v1/generate-resume"
    
    resume_data = {
        "user_profile": {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
            "work_history": [
                {
                    "company": "Tech Corp",
                    "position": "Software Engineer",
                    "start_date": "2020-01-01",
                    "end_date": "2024-01-01",
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
        "job_description": "Looking for a Python developer with FastAPI experience"
    }
    
    try:
        response = requests.post(resume_url, json=resume_data, headers=headers, timeout=45)
        print(f"📡 Resume Generation Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Resume generation works!")
            summary = result.get('professional_summary', '')[:100]
            print(f"📝 Summary preview: {summary}...")
        else:
            print(f"❌ Resume generation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Resume generation error: {e}")
    
    # Test Interview Questions
    print("\n❓ Testing Interview Questions...")
    interview_url = "http://localhost:8000/api/v1/interview-questions"
    
    interview_data = {
        "job_description": "Senior Python Developer needed with FastAPI and PostgreSQL experience",
        "user_profile": {
            "name": "Jane Smith",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience_level": "Senior"
        }
    }
    
    try:
        response = requests.post(interview_url, json=interview_data, headers=headers, timeout=45)
        print(f"📡 Interview Questions Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Interview questions generation works!")
            questions = result.get('questions', {})
            if isinstance(questions, dict):
                for category, q_list in questions.items():
                    print(f"📋 {category}: {len(q_list)} questions")
            else:
                print(f"📋 Generated {len(questions)} questions")
        else:
            print(f"❌ Interview questions failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Interview questions error: {e}")

def diagnose_auth_endpoints():
    """Diagnose auth endpoint schemas"""
    print("\n🔍 DIAGNOSING AUTH ENDPOINTS")
    
    # Check if we can get schema info
    try:
        response = requests.get("http://localhost:8000/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API docs available at http://localhost:8000/docs")
        
        response = requests.get("http://localhost:8000/openapi.json", timeout=10)
        if response.status_code == 200:
            print("✅ OpenAPI schema available")
            
    except Exception as e:
        print(f"❌ Schema check error: {e}")

def main():
    print("🚀 COMPLETE PROJECT FIX & DIAGNOSIS")
    print("=" * 50)
    
    # Diagnose auth endpoints
    diagnose_auth_endpoints()
    
    # Test registration
    reg_success = test_registration()
    
    # Test both login methods
    token = test_login_json()
    if not token:
        token = test_login_form()
    
    # Test AI features
    test_ai_features(token)
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE!")
    print("=" * 50)
    
    # Summary
    print("\n📋 FINDINGS:")
    if reg_success:
        print("✅ Registration: Working")
    else:
        print("❌ Registration: Issues found")
        
    if token:
        print("✅ Login: Working")
        print("✅ Authentication: Token obtained")
    else:
        print("❌ Login: Not working")
        print("❌ Authentication: No token")
    
    print("\n🔧 NEXT STEPS:")
    if not token:
        print("1. Fix login endpoint to accept correct format")
        print("2. Check FastAPI OAuth2PasswordRequestForm setup")
    print("3. Test AI features once auth is working")
    print("4. Check frontend API endpoint paths")

if __name__ == "__main__":
    main()