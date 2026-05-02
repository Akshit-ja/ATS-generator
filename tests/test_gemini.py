#!/usr/bin/env python3
"""
Test Google Gemini API integration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API directly"""
    print("🚀 Testing Google Gemini API")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("AI_API_KEY")
    provider = os.getenv("AI_PROVIDER")
    
    print(f"🔧 AI Provider: {provider}")
    print(f"🔑 API Key: {'Set' if api_key and not api_key.startswith('YOUR_') else 'Not set or placeholder'}")
    
    if not api_key or api_key.startswith('YOUR_'):
        print("❌ Please set your real Gemini API key in .env file")
        print("   Replace YOUR_GEMINI_API_KEY_HERE with your actual key")
        return False
    
    try:
        import google.generativeai as genai
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Create the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with a simple prompt
        print("\n🧪 Testing Gemini with simple prompt...")
        response = model.generate_content("Hello, can you tell me your name and model?")
        
        print("✅ Gemini API is working!")
        print(f"📄 Response: {response.text[:200]}...")
        
        return True
        
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Run: pip install google-generativeai")
        return False
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    
    if success:
        print("\n🎉 Ready to use Gemini!")
        print("Your resume generator will now use Google Gemini AI!")
    else:
        print("\n🔧 Please fix the issues above and try again.")