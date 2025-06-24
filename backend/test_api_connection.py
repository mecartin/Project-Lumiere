#!/usr/bin/env python3
"""
Test script to verify the tag-based recommendations API is working
"""

import requests
import json

def test_api_connection():
    """Test the tag-based recommendations API"""
    
    base_url = "http://localhost:8001"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test tag-based recommendations
    try:
        test_data = {
            "user_tags": ["feel-good", "comedy"],
            "calibration_settings": {
                "era": 7,
                "runtime": 6,
                "popularity": 5,
                "familiarity": 4
            },
            "max_recommendations": 5
        }
        
        response = requests.post(
            f"{base_url}/recommendations/tag-based",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Tag-based recommendations API working")
            print(f"   Processing time: {result.get('processing_time', 0):.2f} seconds")
            print(f"   Recommendations found: {result.get('total_found', 0)}")
            print(f"   User profile: {result.get('user_profile_summary', {})}")
            
            if result.get('recommendations'):
                print("\n🎬 Sample recommendations:")
                for i, movie in enumerate(result['recommendations'][:3]):
                    print(f"   {i+1}. {movie.get('title', 'Unknown')} ({movie.get('release_date', 'Unknown')[:4]})")
                    print(f"      Score: {movie.get('final_score', 0):.1f}")
                    print(f"      Genres: {', '.join(movie.get('genres', []))}")
            else:
                print("⚠️ No recommendations returned")
            
            return True
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API request error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Tag-Based Recommendations API")
    print("=" * 50)
    
    success = test_api_connection()
    
    if success:
        print("\n✅ API is ready for frontend integration!")
    else:
        print("\n❌ API needs attention before frontend integration") 