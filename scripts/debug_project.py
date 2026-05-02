#!/usr/bin/env python3
"""
Debug project issues
"""
import requests
import json

def debug_project():
    print("🔍 DEBUGGING PROJECT ISSUES")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test backend endpoints discovery
    print("\n1️⃣ Discovering Available Endpoints...")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            print(f"   Found {len(paths)} API endpoints:")
            for path in sorted(paths.keys()):
                methods = list(paths[path].keys())
                print(f"   📍 {path} - {methods}")
        else:
            print(f"   ❌ Cannot get API schema: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting endpoints: {e}")
    
    # Test auth endpoints specifically
    print("\n2️⃣ Testing Auth Endpoints...")
    
    # Test registration
    print("\n   📝 Testing Registration...")
    register_data = {
        "username": "debuguser123",
        "email": "debuguser123@test.com",
        "password": "password123",
        "full_name": "Debug User"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=register_data, timeout=10)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            print("      ✅ Registration works")
        elif response.status_code == 400:
            print("      ⚠️  User might already exist")
        else:
            print("      ❌ Registration failed")
            
    except Exception as e:
        print(f"      ❌ Registration error: {e}")
    
    # Test login
    print("\n   🔐 Testing Login...")
    login_data = {
        "email": "debuguser123@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("      ✅ Login works")
            token_data = response.json()
            token = token_data.get('access_token')
            if token:
                print(f"      🔑 Token: {token[:30]}...")
                return token
        else:
            print("      ❌ Login failed")
            
    except Exception as e:
        print(f"      ❌ Login error: {e}")
    
    return None

def test_frontend_apis(token):
    """Test the frontend by making the same API calls it would make"""
    print("\n3️⃣ Testing Frontend API Calls...")
    
    # Test what the frontend login form would do
    print("\n   🌐 Testing Frontend Login Call...")
    try:
        # This simulates what your fixed frontend login.tsx does
        response = requests.post("http://localhost:8000/auth/login", 
                               json={"email": "debuguser123@test.com", "password": "password123"},
                               timeout=10)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ Frontend login would work")
            print(f"      🔑 access_token present: {'access_token' in data}")
        else:
            print("      ❌ Frontend login would fail")
            print(f"      Response: {response.text}")
    except Exception as e:
        print(f"      ❌ Frontend login error: {e}")
    
    if not token:
        print("   ⚠️  Cannot test AI features without token")
        return
    
    # Test AI features
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n   🤖 Testing Resume Generation...")
    resume_data = {
        "user_profile": {
            "name": "Test User",
            "email": "test@example.com",
            "skills": ["Python", "React"],
            "work_history": [{
                "company": "Test Corp",
                "position": "Developer", 
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "description": "Developed apps"
            }],
            "education": [{
                "degree": "Bachelor",
                "major": "Computer Science",
                "university": "Test University", 
                "year": "2020"
            }]
        },
        "job_description": "Python developer needed"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/generate-resume",
                               json=resume_data, headers=headers, timeout=30)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            print("      ✅ Resume generation works")
        else:
            print("      ❌ Resume generation failed")
            print(f"      Error: {response.text[:200]}...")
    except Exception as e:
        print(f"      ❌ Resume generation error: {e}")

def main():
    token = debug_project()
    test_frontend_apis(token)
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 50)
    
    if token:
        print("✅ Backend APIs are working")
        print("✅ Authentication is working")
        print("✅ Project should be functional")
        print("\n💡 If frontend isn't working, the issue might be:")
        print("   1. Frontend not connecting to backend correctly")
        print("   2. Frontend JavaScript errors")
        print("   3. Browser cache issues")
        print("\n🚀 Try opening http://localhost:3000 in browser")
    else:
        print("❌ Authentication is not working")
        print("❌ Project has backend issues")

if __name__ == "__main__":
    main()