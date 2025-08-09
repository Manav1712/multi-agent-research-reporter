#!/usr/bin/env python3
"""
Test script for Google Custom Search API
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT FOUND")
print(f"Search Engine ID: {search_engine_id}")

if not api_key or not search_engine_id:
    print("❌ Missing credentials")
    exit(1)

# Test API call
url = "https://www.googleapis.com/customsearch/v1"
params = {
    'key': api_key,
    'cx': search_engine_id,
    'q': 'test',
    'num': 1
}

try:
    print("\nTesting API call...")
    response = requests.get(url, params=params, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API call successful!")
        print(f"Results found: {len(data.get('items', []))}")
    else:
        print(f"❌ API call failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
