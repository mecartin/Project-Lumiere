#!/usr/bin/env python3
"""
Test script to verify fuzzy matching and similar movies logic
"""

import requests
import json

def test_fuzzy_matching():
    """Test the fuzzy matching functionality"""
    
    print("🧪 Testing Fuzzy Matching and Similar Movies Logic")
    print("=" * 50)
    
    url = "http://localhost:8001/recommendations/tag-based"
    
    # Test with multiple tags to see the superlist behavior
    payload = {
        "user_tags": ["comedy", "feel-good"],
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
        "max_recommendations": 5
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
            
            # Check recommendations and their source tags
            recommendations = data.get('recommendations', [])
            print(f"\n🎬 Recommendations Analysis:")
            
            tag_sources = {}
            similar_sources = 0
            
            for i, movie in enumerate(recommendations):
                source_tags = movie.get('source_tags', [])
                print(f"   {i+1}. {movie.get('title', 'Unknown')}")
                print(f"      - Source tags: {source_tags}")
                print(f"      - Final score: {movie.get('final_score', 0):.1f}")
                print(f"      - Similarity: {movie.get('similarity_score', 0):.1f}")
                print(f"      - Familiarity: {movie.get('familiarity_score', 0):.1f}")
                
                # Count source types
                for tag in source_tags:
                    if tag == 'similar_to_user_favorite':
                        similar_sources += 1
                    else:
                        tag_sources[tag] = tag_sources.get(tag, 0) + 1
            
            print(f"\n📈 Source Analysis:")
            print(f"   - Movies from tag matching: {sum(tag_sources.values())}")
            for tag, count in tag_sources.items():
                print(f"     * {tag}: {count} movies")
            print(f"   - Movies also similar to user favorites: {similar_sources}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_fuzzy_match_function():
    """Test the fuzzy matching function directly"""
    
    print("\n🔍 Testing Fuzzy Match Function")
    print("=" * 30)
    
    # Import the function
    from tag_based_recommender import fuzzy_match_title
    
    test_cases = [
        ("The Matrix", "The Matrix", True),
        ("The Matrix", "Matrix", True),
        ("The Matrix", "The Matrix Reloaded", True),
        ("The Matrix", "Matrix Reloaded", True),
        ("The Matrix", "Inception", False),
        ("Little Miss Sunshine", "Little Miss Sunshine", True),
        ("Little Miss Sunshine", "Little Miss", True),
        ("Little Miss Sunshine", "Sunshine", True),
        ("Little Miss Sunshine", "Little Miss Sunshine (2006)", True),
        ("Little Miss Sunshine", "Big Miss Sunshine", True),  # Should match due to similarity
        ("Little Miss Sunshine", "The Dark Knight", False),
    ]
    
    for title1, title2, expected in test_cases:
        result = fuzzy_match_title(title1, title2)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{title1}' vs '{title2}' -> {result} (expected {expected})")

if __name__ == "__main__":
    test_fuzzy_match_function()
    test_fuzzy_matching() 