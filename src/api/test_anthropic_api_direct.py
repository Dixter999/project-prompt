#!/usr/bin/env python3
"""
Simple test script for Anthropic API
"""

import os
import sys
import requests

def main():
    """Test Anthropic API connection"""
    # Get API key from .env
    api_key = None
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('anthropic_API'):
                        api_key = line.split('=')[1].strip().strip('"\'')
                        break
    except Exception as e:
        print(f"Error reading .env file: {e}")
        
    if not api_key:
        print("API key not found in .env file")
        sys.exit(1)
        
    print(f"Using API key: {api_key[:10]}...{api_key[-5:]}")
    
    # Make a simple API request
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 30,
        "messages": [{"role": "user", "content": "Say hello and confirm that the API is working"}]
    }
    
    try:
        print("Making API request to Anthropic...")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("content", [])
            
            # Extract text from content
            text_parts = []
            for item in content:
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                    
            text = "".join(text_parts).strip()
            print("\nResponse from Claude:")
            print(text)
            print("\nAPI is working correctly!")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    main()
