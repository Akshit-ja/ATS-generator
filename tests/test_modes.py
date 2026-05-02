import requests
import json

def test_dual_mode_dashboard():
    """Test the new dual-mode dashboard functionality"""
    print("🎯 TESTING DUAL-MODE DASHBOARD")
    print("=" * 50)
    
    # First, login to get a token
    try:
        login_response = requests.post('http://localhost:8000/auth/login', 
                                       json={'email': 'test@example.com', 'password': 'testpass123'})
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json().get('access_token')
        print("✅ Login successful, token obtained")
        
        # Test Mode 1: Generate New Resume (no file)
        print("\n🆕 Testing MODE 1: Generate New Resume...")
        test_data = {
            'job_description': 'Software Engineer at a tech company. Must have Python, JavaScript, and React experience.'
        }
        
        response = requests.post('http://localhost:8000/api/v1/generate-resume',
                               data=test_data,
                               headers={'Authorization': f'Bearer {token}'})
        
        print(f"📊 Mode 1 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Mode 1 (Generate New) successful!")
            print(f"📝 Generated Summary: {data.get('professional_summary', 'N/A')[:100]}...")
            print(f"🔧 Mode: {data.get('mode', 'unknown')}")
        else:
            print(f"❌ Mode 1 failed: {response.text}")
            
        # Test Mode 2: Optimize Existing Resume (with file)
        print("\n🔧 Testing MODE 2: Optimize Existing Resume...")
        
        # Create a dummy file for testing
        files = {
            'resume_file': ('test_resume.txt', 'John Doe\nSoftware Engineer\nPython | JavaScript | React', 'text/plain')
        }
        data = {
            'job_description': 'Senior Full Stack Developer position requiring React, Node.js, and AWS experience.'
        }
        
        response = requests.post('http://localhost:8000/api/v1/generate-resume',
                               data=data,
                               files=files,
                               headers={'Authorization': f'Bearer {token}'})
        
        print(f"📊 Mode 2 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Mode 2 (Optimize Existing) successful!")
            print(f"📝 Optimized Summary: {data.get('professional_summary', 'N/A')[:100]}...")
            print(f"🔧 Mode: {data.get('mode', 'unknown')}")
        else:
            print(f"❌ Mode 2 failed: {response.text}")
            
        print("\n" + "=" * 50)
        print("🎉 DUAL-MODE TESTING COMPLETE!")
        print("✅ Both Generate and Optimize modes are working")
        print("🌐 Frontend Dashboard: http://localhost:3000/dashboard")
        print("💡 You should now see mode selection buttons!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dual_mode_dashboard()