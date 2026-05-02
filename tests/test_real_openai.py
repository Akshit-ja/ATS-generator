"""
Test script to verify OpenAI API integration
Run this after adding your real OpenAI API key
"""
import requests
import json
import os

def test_real_openai():
    print("🔑 Testing Real OpenAI API Integration\n")
    
    base_url = "http://localhost:8000"
    
    # Check if API key is configured
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key.startswith("your-") or not api_key:
        print("⚠️  OpenAI API key not configured properly")
        print("   Current key starts with:", api_key[:20] + "..." if len(api_key) > 20 else api_key)
        print("   Please update the OPENAI_API_KEY in .env file")
        return
    
    print(f"✅ API key configured (starts with: {api_key[:20]}...)")
    
    # Login to get token
    session = requests.Session()
    login_data = {
        "username": "integration_test@example.com",
        "password": "testpassword123"
    }
    
    response = session.post(f"{base_url}/auth/token", data=login_data)
    if response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    token = response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ Authentication successful")
    
    # Test resume generation with real OpenAI
    print("\n🤖 Testing Real AI Resume Generation...")
    
    test_data = {
        "user_profile": {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "skills": ["Python", "Machine Learning", "Docker", "FastAPI"],
            "work_history": [{
                "company": "TechCorp Inc",
                "position": "Senior Python Developer",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "description": "Led development of ML-powered applications using Python, FastAPI, and Docker. Improved system performance by 40% and mentored junior developers."
            }],
            "education": [{
                "degree": "Master's",
                "major": "Computer Science",
                "university": "Stanford University",
                "year": "2019"
            }]
        },
        "job_description": """
        Senior AI Engineer Position
        
        We are looking for a Senior AI Engineer to join our team. The ideal candidate will have:
        - 5+ years of Python development experience
        - Strong background in machine learning and AI
        - Experience with FastAPI and containerization
        - Leadership and mentoring experience
        - Master's degree in Computer Science or related field
        
        Responsibilities:
        - Design and implement AI/ML solutions
        - Lead technical projects and mentor team members
        - Optimize system performance and scalability
        - Collaborate with cross-functional teams
        """
    }
    
    response = session.post(f"{base_url}/api/v1/generate-resume", json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Real AI Resume Generation Successful!")
        print("\n📋 Generated Resume Sections:")
        for section, content in result.items():
            if section != "match_score":
                print(f"\n**{section.replace('_', ' ').title()}:**")
                print(content[:200] + "..." if len(content) > 200 else content)
        
        if "match_score" in result:
            match_score = result["match_score"]
            print(f"\n🎯 **Job Match Analysis:**")
            print(f"Overall Score: {match_score.get('overall_score', 'N/A')}%")
            print(f"Strengths: {', '.join(match_score.get('strengths', []))}")
            print(f"Recommendations: {', '.join(match_score.get('recommendations', []))}")
    
    elif response.status_code == 500:
        print("❌ OpenAI API Error - Check your API key and quota")
        try:
            error_detail = response.json()
            print(f"Error details: {error_detail}")
        except:
            print(f"Error response: {response.text}")
    else:
        print(f"❌ Unexpected error: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_real_openai()