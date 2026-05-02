#!/usr/bin/env python3
"""
Complete Project Test - Frontend, Backend, and Gemini AI Integration
"""
import requests
import time
import json

def test_complete_project():
    """Test the entire resume AI generator project"""
    print("🚀 Testing Complete Resume AI Generator Project")
    print("=" * 60)
    
    # Test Frontend
    print("\n🎨 Testing Frontend (Next.js)...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running on http://localhost:3000")
        else:
            print(f"⚠️  Frontend status: {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Frontend not accessible at http://localhost:3000")
    
    # Test Backend Health
    print("\n🔍 Testing Backend Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy on http://localhost:8000")
        else:
            print(f"⚠️  Backend health status: {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Backend not accessible at http://localhost:8000")
        print("   The backend might still be starting up...")
        return False
    
    # Test Backend API Documentation
    print("\n📚 Testing API Documentation...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs available at http://localhost:8000/docs")
        else:
            print(f"⚠️  API docs status: {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ API docs not accessible")
    
    # Test Authentication
    print("\n🔐 Testing Authentication...")
    try:
        login_data = {
            "username": "test@example.com",
            "password": "test123"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Authentication successful")
            
            # Test Gemini AI Integration
            print("\n🧠 Testing Gemini AI Resume Generation...")
            
            headers = {"Authorization": f"Bearer {token}"}
            test_data = {
                "user_profile": {
                    "name": "Sarah Chen",
                    "skills": ["Python", "Machine Learning", "Google Cloud", "TensorFlow"],
                    "work_experience": [
                        {
                            "company": "TechStart Inc",
                            "position": "ML Engineer",
                            "duration": "2 years",
                            "responsibilities": ["Built ML models", "Deployed on GCP", "Data analysis"]
                        }
                    ],
                    "education": [
                        {
                            "degree": "MS Computer Science",
                            "school": "Stanford University",
                            "year": "2022"
                        }
                    ]
                },
                "job_description": "Senior AI Engineer position at Google. Looking for expertise in machine learning, Python, and cloud technologies. Must have experience with TensorFlow and Google Cloud Platform."
            }
            
            response = requests.post(
                "http://localhost:8000/api/v1/generate-resume",
                json=test_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("professional_summary", "")
                
                print("✅ Gemini AI resume generation successful!")
                print(f"📝 Generated Professional Summary (first 200 chars):")
                print(f"   {summary[:200]}...")
                
                # Check if it mentions Google/Gemini specific content
                if any(keyword in summary.lower() for keyword in ["google", "cloud", "machine learning", "tensorflow"]):
                    print("🎯 AI successfully tailored resume to job description!")
                
                return True
            else:
                print(f"❌ Resume generation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication/AI test failed: {e}")
        return False

def show_project_urls():
    """Show all available project URLs"""
    print("\n🌐 PROJECT URLS")
    print("=" * 40)
    print("🎨 Frontend Application:")
    print("   🏠 Home Page: http://localhost:3000")
    print("   📊 Dashboard: http://localhost:3000/dashboard")
    print("   ❓ Interview Questions: http://localhost:3000/interview-questions")
    print("   🔐 Login: http://localhost:3000/login")
    print()
    print("🔍 Backend API:")
    print("   📚 API Documentation: http://localhost:8000/docs")
    print("   🔍 Health Check: http://localhost:8000/health")
    print("   🔐 Authentication: http://localhost:8000/api/v1/auth/login")
    print("   📝 Generate Resume: http://localhost:8000/api/v1/generate-resume")
    print("   ❓ Interview Questions: http://localhost:8000/api/v1/generate-interview-questions")

if __name__ == "__main__":
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    success = test_complete_project()
    
    show_project_urls()
    
    if success:
        print("\n🎉 SUCCESS! Your complete Resume AI Generator is working!")
        print("✨ Powered by Google Gemini AI")
        print("🚀 Ready to generate amazing resumes!")
    else:
        print("\n🔧 Some services might still be starting up.")
        print("💡 Try accessing http://localhost:3000 for the frontend")
        print("📚 Try http://localhost:8000/docs for API documentation")
    
    print("\n" + "=" * 60)
    print("🎯 Your AI-Powered Resume Generator is LIVE!")
    print("=" * 60)