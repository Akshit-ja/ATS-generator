#!/usr/bin/env python3
"""
Direct test of Gemini API key (no backend required)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_direct():
    """Test Gemini API directly without backend"""
    print("🚀 Direct Gemini API Test")
    print("=" * 40)
    
    # Check if API key is set
    api_key = os.getenv("AI_API_KEY")
    provider = os.getenv("AI_PROVIDER")
    
    print(f"🔧 AI Provider: {provider}")
    print(f"🔑 API Key: {api_key[:15]}...{api_key[-4:] if api_key else 'Not set'}")
    
    if not api_key or api_key.startswith('YOUR_'):
        print("❌ Please set your real Gemini API key in .env file")
        return False
    
    try:
        # Try to make a simple HTTP request to test the API key
        import requests
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": "Hello! Please respond with just 'Gemini API is working!' to confirm the connection."
                }]
            }]
        }
        
        # Make the request with API key as URL parameter
        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"\n📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print("✅ GEMINI API IS WORKING!")
                print(f"📝 Response: {text}")
                return True
            else:
                print("❌ Unexpected response format")
                print(f"Response: {result}")
                return False
        else:
            print("❌ API request failed")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except ImportError:
        print("❌ 'requests' library not found")
        print("   Install with: pip install requests")
        return False
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_direct()
    
    if success:
        print("\n🎉 GEMINI API KEY IS WORKING!")
        print("Your API key is valid and Gemini is responding!")
    else:
        print("\n🔧 Please check your API key and try again.")
        print("Get your key from: https://makersuite.google.com/app/apikey")