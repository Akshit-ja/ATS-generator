"""
Quick test for OpenAI endpoints
"""
import requests
import json

def test_openai_endpoints():
    base_url = "http://localhost:8000"
    
    # Login first to get token
    login_data = {
        "username": "integration_test@example.com",
        "password": "testpassword123"
    }
    
    session = requests.Session()
    response = session.post(f"{base_url}/auth/token", data=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        print("✅ Authentication successful")
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return
    
    # Test OpenAI endpoints
    endpoints = [
        ("/api/v1/generate-resume", {
            "user_profile": {
                "name": "John Doe",
                "email": "john@example.com",
                "skills": ["Python", "FastAPI", "Docker"],
                "work_history": [{
                    "company": "Tech Corp",
                    "position": "Software Developer",
                    "start_date": "2022-01-01",
                    "end_date": "2024-01-01",
                    "description": "Developed web applications using Python and FastAPI"
                }],
                "education": [{
                    "degree": "Bachelor's",
                    "major": "Computer Science",
                    "university": "Tech University",
                    "year": "2021"
                }]
            },
            "job_description": "Software Engineer position requiring Python and FastAPI experience"
        }),
    ]
    
    for endpoint, data in endpoints:
        print(f"\n🧪 Testing {endpoint}")
        response = session.post(f"{base_url}{endpoint}", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code != 404:
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response text: {response.text[:200]}")
        else:
            print("❌ Endpoint not found - 404")

if __name__ == "__main__":
    test_openai_endpoints()