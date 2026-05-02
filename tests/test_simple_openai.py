"""
Simple OpenAI test with minimal request
"""
import requests
import json

def simple_openai_test():
    print("🤖 Simple OpenAI Test\n")
    
    base_url = "http://localhost:8000"
    
    # Login
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
    
    # Simple test request
    test_data = {
        "user_profile": {
            "name": "Test User",
            "email": "test@example.com", 
            "skills": ["Python"],
            "work_history": [{
                "company": "Test Corp",
                "position": "Developer",
                "start_date": "2020-01-01",
                "end_date": "2023-01-01",
                "description": "Built Python applications"
            }],
            "education": [{
                "degree": "Bachelor",
                "major": "Computer Science",
                "university": "Test University",
                "year": "2019"
            }]
        },
        "job_description": "Python Developer - We need someone with Python experience."
    }
    
    print("🧪 Sending simple request...")
    response = session.post(f"{base_url}/api/v1/generate-resume", json=test_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        summary = result.get('professional_summary', '')
        print(f"\nProfessional Summary (first 100 chars):")
        print(f"'{summary[:100]}...'")
        
        # Check if it mentions the user's actual name or company
        if "Test User" in summary or "Test Corp" in summary:
            print("\n🎉 REAL AI DETECTED! Response includes specific details from the request!")
        else:
            print("\n⚠️  Still receiving generic mock response")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    simple_openai_test()