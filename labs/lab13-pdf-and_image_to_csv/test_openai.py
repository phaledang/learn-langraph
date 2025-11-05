#!/usr/bin/env python3
"""
Simple test to verify Azure OpenAI API configuration
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

def test_azure_openai_connection():
    try:
        print("🔍 Testing Azure OpenAI API connection...")
        
        # Load environment variables
        load_dotenv()
        
        # Check environment variables
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
        
        if api_key:
            print(f"✅ AZURE_OPENAI_API_KEY found (starts with: {api_key[:10]}...)")
        else:
            print("❌ AZURE_OPENAI_API_KEY not found in environment")
            return False
            
        if endpoint:
            print(f"✅ AZURE_OPENAI_ENDPOINT found: {endpoint}")
        else:
            print("❌ AZURE_OPENAI_ENDPOINT not found in environment")
            return False
            
        print(f"✅ Using deployment: {deployment}")
        print(f"✅ Using API version: {api_version}")
        
        # Test API call
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "user", "content": "Say 'Hello, this is a test!'"}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ Azure OpenAI API working! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI API error: {e}")
        return False

if __name__ == "__main__":
    test_azure_openai_connection()