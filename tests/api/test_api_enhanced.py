"""
Comprehensive API validation tests for Resume AI Generator
Tests all endpoints including OpenAI integration
"""
import requests
from typing import Dict, Any

# Base configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123"
}

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def test_health_check(self) -> bool:
        """Test if the API is responding"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API is responding")
                return True
            else:
                print(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def register_user(self) -> bool:
        """Register a test user"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=TEST_USER
            )
            if response.status_code in [200, 201]:
                print("✅ User registration successful")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                print("✅ User already exists (skipping registration)")
                return True
            else:
                print(f"❌ User registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ User registration error: {e}")
            return False
    
    def login_user(self) -> bool:
        """Login and get authentication token"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/token",
                data={
                    "username": TEST_USER["email"],  # OAuth2 expects email in username field
                    "password": TEST_USER["password"]
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ User login successful")
                return True
            else:
                print(f"❌ User login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ User login error: {e}")
            return False
    
    def test_budget_endpoints(self) -> bool:
        """Test budget management endpoints"""
        try:
            # Test get budget
            response = self.session.get(f"{self.base_url}/api/v1/budget/")
            if response.status_code == 200:
                print("✅ Get budget settings successful")
            
            # Test create budget
            budget_data = {
                "monthly_limit": 100.0,
                "alert_threshold": 80.0,
                "notifications_enabled": True
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/budget/",
                json=budget_data
            )
            if response.status_code in [200, 201]:
                print("✅ Create budget settings successful")
                return True
            else:
                print(f"❌ Budget endpoints failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Budget endpoints error: {e}")
            return False
    
    def test_interview_endpoints(self) -> bool:
        """Test interview question generation"""
        try:
            interview_data = {
                "job_description": "Senior Software Engineer role at a tech company. Responsible for designing and implementing scalable web applications.",
                "user_profile": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "skills": ["Python", "JavaScript", "React", "FastAPI"],
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
                            "degree": "Bachelor of Science",
                            "major": "Computer Science",
                            "university": "Tech University",
                            "year": "2019"
                        }
                    ]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/interview-questions",
                json=interview_data
            )
            if response.status_code == 200:
                data = response.json()
                if ("behavioral_questions" in data and 
                    "technical_questions" in data and 
                    "company_questions" in data):
                    print("✅ Interview questions successful")
                    print(f"   - Behavioral: {len(data['behavioral_questions'])} questions")
                    print(f"   - Technical: {len(data['technical_questions'])} questions") 
                    print(f"   - Company: {len(data['company_questions'])} questions")
                    return True
                else:
                    print(f"❌ Interview questions response missing expected fields. Got: {list(data.keys())}")
                    return False
            else:
                print(f"❌ Interview questions failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Interview endpoints error: {e}")
            return False
    
    def test_admin_endpoints(self) -> bool:
        """Test admin endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/admin/usage/stats")
            if response.status_code == 200:
                print("✅ Admin usage stats successful")
                return True
            else:
                print(f"❌ Admin usage stats failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin endpoints error: {e}")
            return False
    
    def test_resume_generation_endpoints(self) -> bool:
        """Test new OpenAI-powered resume generation endpoints"""
        try:
            # Test resume generation
            resume_data = {
                "job_description": "We are looking for a Senior Software Engineer with experience in Python, FastAPI, and cloud technologies. The ideal candidate will have 5+ years of experience building scalable web applications.",
                "user_profile": {
                    "name": "Test User",
                    "email": "test@example.com", 
                    "skills": ["Python", "FastAPI", "JavaScript", "React", "AWS"],
                    "work_history": [
                        {
                            "company": "Tech Corp",
                            "position": "Software Engineer",
                            "start_date": "2020-01-01",
                            "end_date": "2023-01-01",
                            "description": "Developed web applications using Python and FastAPI"
                        }
                    ],
                    "education": [
                        {
                            "degree": "Bachelor of Science",
                            "major": "Computer Science", 
                            "university": "Tech University",
                            "year": "2019"
                        }
                    ]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/generate-resume",
                json=resume_data
            )
            if response.status_code == 200:
                data = response.json()
                if "professional_summary" in data and "match_score" in data:
                    print("✅ Resume generation successful")
                    print(f"   - Match score: {data['match_score'].get('overall_score', 'N/A')}%")
                    return True
                else:
                    print(f"❌ Resume generation response missing fields: {list(data.keys())}")
                    return False
            else:
                print(f"❌ Resume generation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Resume generation endpoints error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Enhanced API Validation Tests\n")
        
        # Health check
        print("1. Testing API Health...")
        if not self.test_health_check():
            print("❌ API is not responding. Aborting tests.")
            return
        print()
        
        # Authentication flow
        print("2. Testing User Registration...")
        self.register_user()
        print()
        
        print("3. Testing User Login...")
        if not self.login_user():
            print("❌ Cannot proceed without authentication. Aborting tests.")
            return
        print()
        
        # Test endpoints that require authentication
        print("4. Testing Budget Endpoints...")
        self.test_budget_endpoints()
        print()
        
        print("5. Testing Interview Endpoints...")
        self.test_interview_endpoints()
        print()
        
        print("6. Testing Admin Endpoints...")
        self.test_admin_endpoints()
        print()
        
        print("7. Testing Resume Generation Endpoints...")
        self.test_resume_generation_endpoints()
        print()
        
        print("🎉 Enhanced API Validation Tests Complete!")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()