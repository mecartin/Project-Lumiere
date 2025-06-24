#!/usr/bin/env python3
"""
Simple test script for the tag-based recommender
This script tests the basic functionality without requiring the full keywords database
"""

import os
import json
from tag_based_recommender import TagBasedRecommender

def test_simple_recommendations():
    """Test the recommender with manual keyword mapping"""
    
    print("🎬 Simple Tag-Based Recommender Test")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("❌ TMDB_API_KEY environment variable not set")
        print("Please set it with: export TMDB_API_KEY=your_api_key")
        return
    
    # Initialize recommender
    print("🔧 Initializing recommender...")
    recommender = TagBasedRecommender(api_key)
    
    # Check what keywords database was loaded
    print(f"📊 Keywords database contains {len(recommender.keywords_db)} entries")
    
    # Test with simple tags that should have manual mappings
    user_tags = ["feel-good", "comedy"]
    calibration_settings = {
        'era': 7,  # 1980s-2010s
        'runtime': 6,  # 90-150 minutes
        'popularity': 5,  # Medium popularity
        'familiarity': 4  # Somewhat familiar
    }
    
    print(f"\n📊 Test Configuration:")
    print(f"   Tags: {user_tags}")
    print(f"   Calibration: {calibration_settings}")
    
    # Test keyword ID lookup
    print(f"\n🔍 Testing keyword ID lookup:")
    for tag in user_tags:
        keyword_id = recommender._get_keyword_id(tag)
        if keyword_id:
            print(f"   ✅ '{tag}' -> ID {keyword_id}")
        else:
            print(f"   ❌ '{tag}' -> No keyword found")
    
    # Test calibration to filters conversion
    print(f"\n⚙️ Testing calibration filters:")
    filters = recommender._convert_calibration_to_filters(calibration_settings)
    for key, value in filters.items():
        print(f"   {key}: {value}")
    
    # Test a simple API call
    print(f"\n🌐 Testing TMDB API connection:")
    try:
        test_data = recommender._make_cached_request("/configuration")
        if test_data:
            print("   ✅ TMDB API connection successful")
        else:
            print("   ❌ TMDB API connection failed")
    except Exception as e:
        print(f"   ❌ TMDB API error: {e}")
    
    print(f"\n✅ Simple test completed!")

if __name__ == "__main__":
    test_simple_recommendations()
