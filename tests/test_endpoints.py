#!/usr/bin/env python3
"""
Quick API Test - Find available endpoints
"""
import requests
import json

def test_endpoints():
    """Test available endpoints"""
    print("🔍 API ENDPOINT DISCOVERY")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Get OpenAPI spec to see all available endpoints
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            print(f"📋 Total endpoints: {len(paths)}")
            print("\n🔗 AVAILABLE ENDPOINTS:")
            for path in sorted(paths.keys()):
                methods = list(paths[path].keys())
                print(f"   {path} - {', '.join(methods).upper()}")
        else:
            print(f"❌ Could not get endpoints: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()