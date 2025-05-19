#!/usr/bin/env python3
import os

print("Reading Anthropic API key...")

# Get API key from .env
api_key = None
try:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    print(f"Looking for .env at: {env_path}")
    if os.path.exists(env_path):
        print(".env file exists")
        with open(env_path, 'r') as f:
            contents = f.read()
            print(f"Contents of .env file: {contents}")
            
            for line in contents.splitlines():
                print(f"Processing line: {line}")
                if line.startswith('anthropic_API'):
                    key_part = line.split('=')[1].strip().strip('"\'')
                    api_key = key_part
                    print(f"Found API key: {key_part[:5]}...{key_part[-5:] if len(key_part) > 10 else ''}")
    else:
        print(".env file does not exist")
except Exception as e:
    print(f"Error: {e}")
    
if api_key:
    print("Successfully found API key")
else:
    print("Failed to find API key")
