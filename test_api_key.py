#!/usr/bin/env python3
import os
import requests

def test_anthropic_api():
    # Read API key from .env file
    api_key = None
    env_path = "/mnt/h/Projects/project-prompt/.env"
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('anthropic_API'):
                    api_key = line.split('=')[1].strip().strip('"\'')
                    break
    except Exception as e:
        print(f"Error reading .env file: {e}")
        return False
    
    if not api_key:
        print("❌ No API key found in .env file")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...{api_key[-5:]}")
    
    # Test API connection
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 30,
        "messages": [{"role": "user", "content": "Reply with 'API connection successful'"}]
    }
    
    try:
        print("🔄 Testing API connection...")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("content", [])
            
            if content and content[0].get("type") == "text":
                text = content[0].get("text", "")
                print(f"✅ API Response: {text}")
                print("✅ Anthropic API is working correctly!")
                return True
            else:
                print("⚠️ Unexpected response format")
                return False
                
        else:
            print(f"❌ API request failed with status {response.status_code}")
            try:
                error_details = response.json()
                print(f"Error details: {error_details}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_anthropic_api()
    exit(0 if success else 1)
