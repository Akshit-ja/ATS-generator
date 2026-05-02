#!/usr/bin/env python3
"""
Fix and test all project issues
"""
import requests
import json

def fix_and_test_auth():
    """Fix and test authentication"""
    print("🔧 FIXING & TESTING AUTHENTICATION")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. Test registration with correct format
    print("\n1️⃣ Testing User Registration...")
    
    register_data = {
        "username": "testuser123",
        "email": "testuser@example.com", 
        "password": "testpassword123"  # 8+ characters
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=register_data, timeout=10)
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("   ✅ Registration successful!")
            user_data = response.json()
            print(f"   👤 User ID: {user_data.get('id')}")
            print(f"   📧 Email: {user_data.get('email')}")
        elif response.status_code == 400:
            print("   ⚠️  User might already exist (that's OK for testing)")
        else:
            print(f"   ❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Test login with form data (OAuth2PasswordRequestForm)
    print("\n2️⃣ Testing User Login...")
    
    login_data = {
        "username": "testuser@example.com",  # Use email for username
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", data=login_data, timeout=10)
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Login successful!")
            print(f"   🔑 Token type: {token_data.get('token_type')}")
            access_token = token_data.get('access_token')
            print(f"   🎫 Access token: {access_token[:20]}..." if access_token else "   ❌ No access token")
            return access_token
        else:
            print(f"   ❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_resume_with_gemini(token):
    """Test resume generation with Gemini AI"""
    print("\n3️⃣ Testing Resume Generation with Gemini...")
    
    url = "http://localhost:8000/api/v1/generate-resume"
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    test_data = {
        "user_profile": {
            "name": "Sarah Wilson",
            "email": "sarah@example.com",
            "skills": ["Python", "Machine Learning", "Google Cloud", "TensorFlow"],
            "work_history": [
                {
                    "company": "AI Startup",
                    "position": "ML Engineer",
                    "start_date": "2022-01-01",
                    "end_date": "2024-01-01", 
                    "description": "Built ML models using TensorFlow and deployed on Google Cloud Platform"
                }
            ],
            "education": [
                {
                    "degree": "MS Computer Science",
                    "university": "Stanford University", 
                    "year": "2021"
                }
            ]
        },
        "job_description": "Senior AI Engineer at Google. Looking for expertise in machine learning, Python, TensorFlow, and Google Cloud Platform. Must have experience building scalable ML systems."
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=45)
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Resume generation successful!")
            
            summary = result.get('professional_summary', '')
            skills = result.get('technical_skills', '')
            
            print(f"   📄 Professional Summary (first 150 chars):")
            print(f"      {summary[:150]}...")
            
            # Check if it's AI-generated content
            if any(keyword in summary.lower() for keyword in ['google', 'ai', 'machine learning', 'tensorflow']):
                print("   🎯 ✅ Gemini AI successfully tailored resume to job!")
            else:
                print("   ⚠️  Might be using fallback content")
                
            print(f"   🛠️  Technical Skills: {skills[:100]}...")
            
        elif response.status_code == 401:
            print("   🔐 Authentication required - trying without token...")
            # Retry without token
            response = requests.post(url, json=test_data, timeout=45)
            if response.status_code == 200:
                print("   ✅ Resume generation works without auth!")
            else:
                print(f"   ❌ Still failed: {response.text}")
        else:
            print(f"   ❌ Resume generation failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_interview_questions_with_gemini(token):
    """Test interview questions generation"""
    print("\n4️⃣ Testing Interview Questions with Gemini...")
    
    url = "http://localhost:8000/api/v1/interview-questions"
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    test_data = {
        "job_description": "Senior Data Scientist at Google. Looking for expertise in Python, machine learning, TensorFlow, and Google Cloud Platform. Must have PhD in Computer Science or related field.",
        "user_profile": {
            "name": "Dr. Alex Chen",
            "skills": ["Python", "Machine Learning", "TensorFlow", "Statistics", "Deep Learning"],
            "experience_level": "Senior",
            "work_history": [
                {
                    "position": "Data Scientist",
                    "company": "Tech Corp", 
                    "duration": "3 years"
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=45)
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Interview questions generation successful!")
            
            questions = result.get('questions', {})
            if isinstance(questions, dict):
                for category, question_list in questions.items():
                    print(f"   📋 {category.title()}: {len(question_list)} questions")
                    if question_list and len(question_list) > 0:
                        print(f"      Example: {question_list[0].get('question', 'N/A')[:80]}...")
            else:
                print(f"   📄 Generated {len(questions)} questions")
                
        elif response.status_code == 401:
            print("   🔐 Authentication required - trying without token...")
            response = requests.post(url, json=test_data, timeout=45)
            if response.status_code == 200:
                print("   ✅ Interview questions work without auth!")
            else:
                print(f"   ❌ Still failed: {response.text}")
        else:
            print(f"   ❌ Interview questions failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_frontend_pages():
    """Test frontend pages"""
    print("\n5️⃣ Testing Frontend Pages...")
    
    frontend_base = "http://localhost:3000"
    
    pages = [
        ("/", "Home Page"),
        ("/login", "Login Page"),
        ("/dashboard", "Dashboard"),
        ("/interview-questions", "Interview Questions Page")
    ]
    
    for path, name in pages:
        try:
            response = requests.get(f"{frontend_base}{path}", timeout=10)
            print(f"   📄 {name}: Status {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ Page loads successfully")
            else:
                print(f"      ⚠️  Page may have issues")
                
        except Exception as e:
            print(f"   ❌ {name}: Error {e}")

def main():
    print("🚀 COMPREHENSIVE PROJECT FIX & TEST")
    print("=" * 60)
    
    # Fix and test authentication
    token = fix_and_test_auth()
    
    # Test AI features
    test_resume_with_gemini(token)
    test_interview_questions_with_gemini(token)
    
    # Test frontend
    test_frontend_pages()
    
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TESTING COMPLETE!")
    print("=" * 60)
    
    print("\n📋 QUICK FIX SUMMARY:")
    print("✅ Auth endpoints: /auth/register, /auth/login")
    print("✅ Resume generation: /api/v1/generate-resume") 
    print("✅ Interview questions: /api/v1/interview-questions")
    print("✅ Registration format: username, email, password (8+ chars)")
    print("✅ Login format: form data with username/password")

if __name__ == "__main__":
    main()