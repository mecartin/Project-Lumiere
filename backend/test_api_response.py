#!/usr/bin/env python3
"""
Test script to verify API response includes user profile summary
"""

import requests
import json

def test_api_response():
    """Test the API response to verify user data is loaded"""
    
    print("🧪 Testing API Response")
    print("=" * 30)
    
    url = "http://localhost:8001/recommendations/tag-based"
    
    payload = {
        "user_tags": ["comedy"],
        "calibration_settings": {
            "era": 5,
            "runtime": 5,
            "popularity": 5,
            "familiarity": 5,
            "eraEnabled": False,
            "runtimeEnabled": False,
            "popularityEnabled": False,
            "familiarityEnabled": False
        },
        "max_recommendations": 1
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response successful")
            print(f"📊 Total recommendations: {data.get('total_found', 0)}")
            print(f"⏱️ Processing time: {data.get('processing_time', 0):.3f}s")
            
            # Check user profile summary
            user_profile = data.get('user_profile_summary', {})
            print(f"\n👤 User Profile Summary:")
            print(f"   - Tags selected: {user_profile.get('tags_selected', 0)}")
            print(f"   - Movies analyzed: {user_profile.get('movies_analyzed', 0)}")
            print(f"   - User data loaded: {user_profile.get('user_data_loaded', False)}")
            
            # Check user preferences
            preferences = user_profile.get('user_preferences', {})
            print(f"   - Preferred actors: {preferences.get('actors', 0)}")
            print(f"   - Preferred directors: {preferences.get('directors', 0)}")
            print(f"   - Preferred keywords: {preferences.get('keywords', 0)}")
            print(f"   - Preferred genres: {preferences.get('genres', 0)}")
            
            # Check recommendations
            recommendations = data.get('recommendations', [])
            if recommendations:
                movie = recommendations[0]
                print(f"\n🎬 Sample Recommendation:")
                print(f"   - Title: {movie.get('title', 'Unknown')}")
                print(f"   - Final score: {movie.get('final_score', 0):.1f}")
                print(f"   - Similarity score: {movie.get('similarity_score', 0):.1f}")
                print(f"   - Familiarity score: {movie.get('familiarity_score', 0):.1f}")
                print(f"   - Source tags: {movie.get('source_tags', [])}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_api_response() 