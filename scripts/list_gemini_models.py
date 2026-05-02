#!/usr/bin/env python3
"""
List available Gemini models
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_gemini_models():
    """List available Gemini models"""
    print("🔍 Checking Available Gemini Models")
    print("=" * 40)
    
    api_key = os.getenv("AI_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        response = requests.get(
            f"{url}?key={api_key}",
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Available Models:")
            
            if 'models' in result:
                for model in result['models']:
                    name = model.get('name', 'Unknown')
                    display_name = model.get('displayName', 'Unknown')
                    supported_methods = model.get('supportedGenerationMethods', [])
                    
                    if 'generateContent' in supported_methods:
                        print(f"  ✅ {name} ({display_name}) - Supports generateContent")
                    else:
                        print(f"  ❌ {name} ({display_name}) - Does NOT support generateContent")
            else:
                print("No models found in response")
                print(f"Response: {result}")
        else:
            print(f"❌ Failed to list models: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_gemini_models()