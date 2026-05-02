import requests
import json

def test_resume_generation():
    """Test resume generation API directly"""
    print("🔍 TESTING RESUME GENERATION API")
    print("=" * 50)
    
    # First, login to get a token
    try:
        login_response = requests.post('http://localhost:8000/auth/login', 
                                       json={'email': 'test@example.com', 'password': 'testpass123'})
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        token = login_response.json().get('access_token')
        print("✅ Login successful, token obtained")
        
        # Test resume generation without file (new resume)
        print("\n📄 Testing NEW RESUME GENERATION...")
        
        # Use proper form data format
        form_data = {
            'job_description': 'Software Engineer at a tech company. Must have Python, JavaScript, and React experience.'
        }
        
        response = requests.post('http://localhost:8000/api/v1/generate-resume',
                               data=form_data,
                               headers={'Authorization': f'Bearer {token}'})
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resume generation successful!")
            print(f"\n📋 Generated Resume Summary:")
            if 'professional_summary' in data:
                print(f"Summary: {data['professional_summary'][:100]}...")
            else:
                print(f"Response keys: {list(data.keys())}")
        else:
            print(f"❌ Resume generation failed")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_resume_generation()