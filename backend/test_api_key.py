"""
Direct OpenAI API Key Test
"""
import os
import openai
import requests

def test_openai_key_directly():
    print("🔑 Testing OpenAI API Key Directly\n")
    
    # Get the API key
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:20]}...")
        print(f"API Key length: {len(api_key)}")
    
    if not api_key:
        print("❌ No OpenAI API key found in environment")
        return
    
    # Test the API key with a simple request
    print("\n🧪 Testing API key with OpenAI...")
    
    try:
        # Set the API key
        openai.api_key = api_key
        
        # Try a simple completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'OpenAI API is working' if you can see this message."}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API is working!")
        print(f"Response: {response.choices[0].message.content}")
        
    except openai.error.AuthenticationError as e:
        print("❌ Authentication Error: Invalid API key")
        print(f"Error details: {e}")
    except openai.error.RateLimitError as e:
        print("❌ Rate Limit Error: API quota exceeded")
        print(f"Error details: {e}")
    except openai.error.APIError as e:
        print("❌ OpenAI API Error")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_openai_key_directly()