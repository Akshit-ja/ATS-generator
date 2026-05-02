"""
Backend OpenAI API Key Test
Tests your API key through the backend service
"""

import requests
import json

def test_api_key_via_backend():
    print("🔑 Testing OpenAI API Key via Backend Service")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Check backend health
        print("📡 Checking backend connection...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Backend not accessible")
            return False
        print("✅ Backend is accessible")
        
        # Login
        print("\n🔐 Authenticating...")
        session = requests.Session()
        login_data = {
            "username": "integration_test@example.com", 
            "password": "testpassword123"
        }
        
        response = session.post(f"{base_url}/auth/token", data=login_data)
        if response.status_code != 200:
            print("❌ Authentication failed")
            return False
        
        token = response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        print("✅ Authentication successful")
        
        # Test with highly specific data
        print("\n🧪 Testing OpenAI API with unique test data...")
        
        unique_data = {
            "user_profile": {
                "name": "Alexandra Quantum-Smith",
                "email": "alexandra.quantum@testdomain.xyz",
                "skills": ["Quantum Encryption", "Blockchain AI", "Neural Cryptocurrency"],
                "work_history": [{
                    "company": "Futuristic Quantum Solutions Inc",
                    "position": "Senior Quantum-Blockchain Developer",
                    "start_date": "2023-01-01",
                    "end_date": "2024-12-31", 
                    "description": "Developed quantum-resistant cryptocurrency algorithms using advanced neural networks and blockchain integration for secure financial transactions."
                }],
                "education": [{
                    "degree": "PhD",
                    "major": "Quantum Computing and Blockchain",
                    "university": "Institute of Advanced Quantum Technologies",
                    "year": "2022"
                }]
            },
            "job_description": """
            Senior Quantum-Blockchain Engineer Position
            
            We are seeking an exceptional Quantum-Blockchain Engineer to join our cutting-edge research team.
            
            Requirements:
            - PhD in Quantum Computing, Blockchain, or related field
            - 3+ years experience with quantum-resistant algorithms
            - Expertise in neural cryptocurrency systems
            - Experience with blockchain AI integration
            - Strong background in quantum encryption protocols
            
            You will be responsible for:
            - Designing next-generation quantum-resistant cryptocurrency
            - Developing AI-powered blockchain solutions
            - Leading research in quantum encryption protocols
            - Collaborating with international quantum research teams
            
            This is a rare opportunity to work at the forefront of quantum-blockchain technology.
            """
        }
        
        print("   Sending request with highly specific quantum-blockchain profile...")
        response = session.post(f"{base_url}/api/v1/generate-resume", json=unique_data)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('professional_summary', '')
            skills = result.get('technical_skills', '')
            
            print(f"\n📄 Generated Response Analysis:")
            print(f"   Professional Summary: {summary[:100]}...")
            print(f"   Technical Skills: {skills[:100]}...")
            
            # Check for highly specific terms that would only appear with real AI
            quantum_terms = [
                "quantum", "blockchain", "cryptocurrency", "neural", 
                "Alexandra", "Quantum-Smith", "Futuristic Quantum Solutions"
            ]
            
            found_terms = []
            full_response = summary + " " + skills
            
            for term in quantum_terms:
                if term.lower() in full_response.lower():
                    found_terms.append(term)
            
            print(f"\n🔍 Specific Terms Found: {found_terms}")
            
            if len(found_terms) >= 3:
                print(f"\n🎉 REAL AI DETECTED!")
                print(f"   ✅ Your OpenAI API key is WORKING!")
                print(f"   ✅ The AI generated personalized content with {len(found_terms)} specific terms")
                return True
            elif len(found_terms) >= 1:
                print(f"\n⚠️  PARTIAL AI DETECTION")
                print(f"   ⚠️  Found {len(found_terms)} specific terms - API might be working with limitations")
                return False
            else:
                print(f"\n❌ MOCK RESPONSE DETECTED")
                print(f"   ❌ Generic response without specific terms - API not working or quota exceeded")
                return False
                
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error details: {error}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def check_backend_logs():
    print(f"\n📝 Checking Recent Backend Logs for OpenAI Activity...")
    try:
        import subprocess
        
        result = subprocess.run([
            "docker-compose", "logs", "backend", "--tail=5"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            logs = result.stdout
            if "openai" in logs.lower() or "api" in logs.lower():
                print("📋 Recent OpenAI-related logs:")
                for line in logs.split('\n'):
                    if any(term in line.lower() for term in ['openai', 'api', 'quota', 'error']):
                        print(f"   {line}")
            else:
                print("   No recent OpenAI-related activity in logs")
        else:
            print("   Could not retrieve logs")
            
    except Exception as e:
        print(f"   Could not check logs: {e}")

def main():
    print("🚀 OpenAI API Key Validation Test")
    print("Testing your configured API key")
    print("=" * 60)
    
    # Test via backend
    result = test_api_key_via_backend()
    
    # Check logs for additional info
    check_backend_logs()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULT:")
    
    if result:
        print("✅ SUCCESS: Your OpenAI API key is WORKING!")
        print("   🎉 The AI is generating real, personalized content")
        print("   🎉 Your resume generator has full AI capabilities")
    else:
        print("❌ ISSUE: Your OpenAI API key is not working properly")
        print("\n🔧 Common Solutions:")
        print("   1. Check billing: https://platform.openai.com/account/billing")
        print("   2. Verify API key: https://platform.openai.com/api-keys")  
        print("   3. Check usage limits and quotas")
        print("   4. Ensure account is in good standing")
        
    print(f"\n💡 Note: The system will use intelligent mock responses when API is unavailable")

if __name__ == "__main__":
    main()