#!/usr/bin/env python3
"""
Detailed TMDB API debugging script
"""

import os
import requests
import sys

def test_tmdb_api():
    """Test TMDB API with detailed error reporting"""
    print("🔍 Detailed TMDB API Debug Test")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test different TMDB endpoints
    base_url = "https://api.themoviedb.org/3"
    endpoints = [
        "/configuration",
        "/movie/550",  # Fight Club (test movie)
        "/search/movie?query=inception&year=2010"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔗 Testing endpoint: {endpoint}")
        
        try:
            # Test without API key first
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=15)
            print(f"   Without API key: {response.status_code}")
            
            # Test with API key
            params = {"api_key": api_key}
            response = requests.get(url, params=params, timeout=15)
            print(f"   With API key: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Success!")
                data = response.json()
                if "title" in data:
                    print(f"   📽️  Movie: {data['title']}")
                elif "results" in data:
                    print(f"   📽️  Search results: {len(data['results'])} movies")
                else:
                    print(f"   📊 Response keys: {list(data.keys())}")
            else:
                print(f"   ❌ Error: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Connection Error: {e}")
        except requests.exceptions.Timeout as e:
            print(f"   ❌ Timeout Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request Error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")
    
    return True

def test_alternative_methods():
    """Test alternative connection methods"""
    print("\n🔄 Testing Alternative Connection Methods")
    print("=" * 50)
    
    api_key = os.getenv("TMDB_API_KEY")
    
    # Test with different headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        url = "https://api.themoviedb.org/3/configuration"
        params = {"api_key": api_key}
        
        print("🔗 Testing with custom headers...")
        response = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Success with custom headers!")
            return True
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Starting TMDB API Debug Test...")
    
    # Test basic connectivity
    print("\n🌐 Testing basic connectivity...")
    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        print(f"✅ Internet connection: {response.status_code}")
    except Exception as e:
        print(f"❌ Internet connection failed: {e}")
        sys.exit(1)
    
    # Test TMDB API
    test_tmdb_api()
    test_alternative_methods()
    
    print("\n📋 Summary:")
    print("- If you see 'Success!' messages, your API key is working")
    print("- If you see connection errors, it might be a network/firewall issue")
    print("- Try again in a few minutes if it's a temporary issue") 