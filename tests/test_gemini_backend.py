#!/usr/bin/env python3
"""
Test Gemini integration via backend API
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_backend():
    """Test Gemini through the backend API"""
    print("🚀 Testing Gemini Integration via Backend")
    print("=" * 50)
    
    # Check environment
    provider = os.getenv("AI_PROVIDER")
    api_key = os.getenv("AI_API_KEY")
    
    print(f"🔧 AI Provider: {provider}")
    print(f"🔑 API Key: {'Set' if api_key and not api_key.startswith('YOUR_') else '❌ NOT SET - Please replace YOUR_GEMINI_API_KEY_HERE'}")
    
    if not api_key or api_key.startswith('YOUR_'):
        print("\n❌ PLEASE UPDATE YOUR .env FILE:")
        print("   Replace YOUR_GEMINI_API_KEY_HERE with your actual Gemini API key")
        print("   Get it from: https://makersuite.google.com/app/apikey")
        return False
    
    # Test backend connection
    try:
        print("\n📡 Testing backend connection...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend not accessible. Please start with: docker-compose up backend")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend not running. Please start with: docker-compose up backend")
        return False
    
    # Test login
    try:
        print("🔐 Authenticating...")
        login_data = {
            "username": "test@example.com",
            "password": "test123"
        }
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test Gemini AI generation
    try:
        print("🧠 Testing Gemini AI generation...")
        
        test_data = {
            "user_profile": {
                "name": "Alice Johnson",
                "skills": ["Python", "Machine Learning", "Data Science"],
                "work_experience": [
                    {
                        "company": "TechCorp",
                        "position": "Data Scientist",
                        "duration": "2 years",
                        "responsibilities": ["Built ML models", "Analyzed data"]
                    }
                ],
                "education": [
                    {
                        "degree": "BS Computer Science",
                        "school": "Tech University",
                        "year": "2020"
                    }
                ]
            },
            "job_description": "Looking for a Senior Data Scientist with Python and ML expertise for Google Gemini integration projects."
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/generate-resume",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Gemini resume generation successful!")
            
            # Check if it's a real AI response or mock
            summary = result.get("professional_summary", "")
            if "Gemini" in summary or "Google" in summary or len(summary) > 100:
                print("🎉 REAL GEMINI RESPONSE detected!")
                print(f"📝 Sample: {summary[:150]}...")
            else:
                print("⚠️  Mock response detected - check your API key")
                print(f"📝 Response: {summary[:150]}...")
            
            return True
        else:
            print(f"❌ Resume generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_backend()
    
    if success:
        print("\n🎉 GEMINI INTEGRATION SUCCESSFUL!")
        print("Your resume generator is now powered by Google Gemini!")
    else:
        print("\n🔧 Please fix the issues above and try again.")
        print("\nQuick checklist:")
        print("1. ✅ Replace YOUR_GEMINI_API_KEY_HERE in .env file")
        print("2. ✅ Start backend: docker-compose up backend")
        print("3. ✅ Run this test again")