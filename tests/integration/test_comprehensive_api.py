"""
Comprehensive OpenAI API Key Validation Test
"""

import requests
import json
import os
from openai import OpenAI

def test_api_key_comprehensive():
    print("🔑 Comprehensive OpenAI API Key Test")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    print(f"📝 API Key Analysis:")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:15]}...")
    print(f"   Format: {'✅ Valid format' if api_key.startswith('sk-') else '❌ Invalid format'}")
    
    if not api_key or api_key.startswith("your-"):
        print("\n❌ No valid API key found!")
        return False
    
    print(f"\n🧪 Testing OpenAI API Connection...")
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        
        # Test 1: Simple completion
        print("\n📝 Test 1: Simple completion request...")
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'API key is working!' if you can see this."}
                ],
                max_tokens=20
            )
            
            message = response.choices[0].message.content
            print(f"✅ API Response: {message}")
            
            if "API key is working" in message or "working" in message.lower():
                print("🎉 API KEY IS FULLY FUNCTIONAL!")
                return True
            else:
                print(f"⚠️  Unexpected response: {message}")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ API Request Failed: {error_msg}")
            
            if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                print("💳 Issue: API quota exceeded - need to add billing/credits")
                print("   Solution: Visit https://platform.openai.com/account/billing")
                return False
            elif "invalid_api_key" in error_msg or "authentication" in error_msg.lower():
                print("🔐 Issue: Invalid API key")
                return False
            elif "model_not_found" in error_msg:
                print("🤖 Issue: Model access problem")
                return False
            else:
                print(f"🔍 Unknown error: {error_msg}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return False

def test_api_via_backend():
    print(f"\n🌐 Testing API Key via Backend Service...")
    
    try:
        base_url = "http://localhost:8000"
        
        # Check if backend is running
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Backend not accessible")
            return False
        
        print("✅ Backend is accessible")
        
        # Login
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
        
        # Test OpenAI endpoint
        test_data = {
            "user_profile": {
                "name": "OpenAI Test User",
                "email": "test@openai-test.com", 
                "skills": ["API Testing"],
                "work_history": [{
                    "company": "OpenAI Test Company",
                    "position": "API Tester",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "description": "Testing OpenAI API integration"
                }],
                "education": [{
                    "degree": "Bachelor",
                    "major": "API Testing",
                    "university": "OpenAI University",
                    "year": "2023"
                }]
            },
            "job_description": "API Testing Specialist - We need someone to test OpenAI API functionality."
        }
        
        print("🧪 Testing resume generation with specific test data...")
        response = session.post(f"{base_url}/api/v1/generate-resume", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('professional_summary', '')
            
            print(f"📄 Generated Summary:")
            print(f"   {summary[:150]}...")
            
            # Check for specific test data in response
            test_indicators = ["OpenAI Test", "API Testing", "test@openai-test.com"]
            found_indicators = [indicator for indicator in test_indicators if indicator.lower() in summary.lower()]
            
            if found_indicators:
                print(f"🎉 REAL AI DETECTED! Found specific test data: {found_indicators}")
                print("✅ API KEY IS WORKING WITH BACKEND!")
                return True
            else:
                print("⚠️  Generic response detected - likely using fallback")
                return False
        else:
            print(f"❌ Backend request failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Raw error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def main():
    print("🚀 Starting Comprehensive OpenAI API Key Validation")
    print("=" * 60)
    
    # Test 1: Direct API key test
    direct_test_result = test_api_key_comprehensive()
    
    # Test 2: Backend integration test
    backend_test_result = test_api_via_backend()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"   Direct API Test: {'✅ PASS' if direct_test_result else '❌ FAIL'}")
    print(f"   Backend Integration: {'✅ PASS' if backend_test_result else '❌ FAIL'}")
    
    if direct_test_result and backend_test_result:
        print("\n🎉 SUCCESS: Your OpenAI API key is fully functional!")
        print("   Both direct API calls and backend integration are working.")
    elif direct_test_result:
        print("\n⚠️  PARTIAL SUCCESS: API key works directly but backend has issues")
        print("   Check backend configuration and restart services.")
    elif backend_test_result:
        print("\n⚠️  PARTIAL SUCCESS: Backend works but direct API has issues")
        print("   This is unusual - check environment variables.")
    else:
        print("\n❌ FAILURE: API key is not working")
        print("   Common solutions:")
        print("   1. Check API key validity at https://platform.openai.com/api-keys")
        print("   2. Add billing/credits at https://platform.openai.com/account/billing")
        print("   3. Verify account status and quotas")

if __name__ == "__main__":
    main()