import requests
import json

def test_interview_questions_api():
    """Test the interview questions API endpoint"""
    print("🔍 TESTING INTERVIEW QUESTIONS API")
    print("=" * 50)
    
    # First, login to get a token
    login_response = requests.post('http://localhost:8000/auth/login', 
                                   json={'email': 'test@example.com', 'password': 'testpass123'})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json().get('access_token')
    print("✅ Login successful, token obtained")
    
    # Test interview questions endpoint
    test_data = {
        "job_description": """Software Engineer Position
Delivering the best software engineering practices, supporting large-scale systems, and contributing to engineering best practices. SEs use various programming languages and cloud technologies, especially AWS services, to build and maintain innovative software at scale.

Key Responsibilities:
Design and Development: Design and build scalable, distributed software systems and features for new and existing products.
Coding and Implementation: Write high-quality, robust code in various languages (Java, Python, C++, JavaScript, etc.) and utilize AWS services.
Architecture: Contribute to the overall architecture and design of systems, making trade-offs between features and operations.
Quality and Operations: Ensure the quality and reliability of software through testing, performance monitoring, and implementing best practices.
Collaboration and Leadership: Work with cross-functional teams, mentor junior engineers, and play a role in recruiting and interviewing.
Customer Focus: Drive innovation to meet customer needs and enhance the customer experience""",
        "user_profile": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "skills": ["JavaScript", "React", "Node.js", "Python", "FastAPI", "SQL"],
            "work_history": [
                {
                    "company": "Tech Solutions Inc.",
                    "position": "Senior Frontend Developer",
                    "start_date": "2020-01",
                    "end_date": "2023-12",
                    "description": "Led development of responsive web applications using React and Node.js"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "major": "Computer Science",
                    "university": "State University",
                    "year": "2019"
                }
            ]
        }
    }
    
    try:
        response = requests.post('http://localhost:8000/api/v1/interview-questions',
                               json=test_data,
                               headers={'Authorization': f'Bearer {token}'})
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API call successful!")
            print("\n📋 Response Structure:")
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Check the structure of the response
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  - {key}: {type(value)} (length: {len(value) if isinstance(value, (list, str)) else 'N/A'})")
                    if isinstance(value, list) and len(value) > 0:
                        print(f"    First item: {type(value[0])}")
                        if isinstance(value[0], dict):
                            print(f"    Keys: {list(value[0].keys())}")
                        
            print(f"\n📄 Full Response:")
            print(json.dumps(data, indent=2)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2))
            
        else:
            print(f"❌ API call failed")
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error making API call: {e}")

if __name__ == "__main__":
    test_interview_questions_api()