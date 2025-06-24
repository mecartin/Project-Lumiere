#!/usr/bin/env python3
"""
Test script for the new tag-based recommendation algorithm
This script demonstrates the complete algorithm workflow
"""

import os
import json
import time
from datetime import datetime
from tag_based_recommender import TagBasedRecommender

def test_tag_based_recommender():
    """Test the tag-based recommender with example data"""
    
    print("🎬 Testing Tag-Based Movie Recommender")
    print("=" * 60)
    
    # Get API key
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("❌ TMDB_API_KEY environment variable not set")
        print("Please set it with: export TMDB_API_KEY=your_api_key")
        return
    
    # Initialize recommender
    print("🔧 Initializing recommender...")
    recommender = TagBasedRecommender(api_key)
    
    # Check if keywords database exists
    keywords_file = os.path.join("tmdb_cache", "tmdb_keywords.json")
    if not os.path.exists(keywords_file):
        print("⚠️ Keywords database not found. Generating...")
        try:
            recommender.generate_keywords_database()
            print("✅ Keywords database generated successfully")
        except Exception as e:
            print(f"❌ Failed to generate keywords database: {e}")
            return
    else:
        print("✅ Keywords database found")
    
    # Example user data
    user_tags = ["feel-good", "comedy", "inspiring"]
    calibration_settings = {
        'era': 7,  # 1980s-2010s
        'runtime': 6,  # 90-150 minutes
        'popularity': 5,  # Medium popularity
        'familiarity': 4  # Somewhat familiar
    }
    
    # Example user movies (simulated)
    user_movies = [
        {
            'tmdb_id': 550,  # Fight Club
            'title': 'Fight Club',
            'cast': ['Brad Pitt', 'Edward Norton', 'Helena Bonham Carter'],
            'directors': ['David Fincher'],
            'writers': ['Chuck Palahniuk'],
            'keywords': ['psychological thriller', 'underground fighting', 'social commentary'],
            'genres': ['Drama', 'Thriller']
        },
        {
            'tmdb_id': 13,  # Forrest Gump
            'title': 'Forrest Gump',
            'cast': ['Tom Hanks', 'Robin Wright', 'Gary Sinise'],
            'directors': ['Robert Zemeckis'],
            'writers': ['Winston Groom'],
            'keywords': ['feel good', 'inspirational', 'historical'],
            'genres': ['Drama', 'Comedy']
        }
    ]
    
    print(f"\n📊 Test Configuration:")
    print(f"   Tags: {user_tags}")
    print(f"   Calibration: {calibration_settings}")
    print(f"   User movies: {len(user_movies)}")
    
    # Get recommendations
    print(f"\n🎯 Generating recommendations...")
    start_time = time.time()
    
    try:
        recommendations = recommender.get_recommendations(
            user_tags=user_tags,
            calibration_settings=calibration_settings,
            user_movies=user_movies,
            max_recommendations=10
        )
        
        processing_time = time.time() - start_time
        
        print(f"✅ Generated {len(recommendations)} recommendations in {processing_time:.2f} seconds")
        
        # Display results
        print(f"\n🎬 Top Recommendations:")
        print("-" * 80)
        
        for i, movie in enumerate(recommendations[:5]):
            print(f"{i+1}. {movie['title']} ({movie.get('release_date', 'Unknown')[:4]})")
            print(f"   Score: {movie.get('final_score', 0):.1f} | "
                  f"Similarity: {movie.get('similarity_score', 0):.1f} | "
                  f"Familiarity: {movie.get('familiarity_score', 0):.1f}")
            print(f"   Genres: {', '.join(movie.get('genres', []))}")
            print(f"   Source tags: {', '.join(movie.get('source_tags', []))}")
            if movie.get('overview'):
                overview = movie['overview'][:100] + "..." if len(movie['overview']) > 100 else movie['overview']
                print(f"   Overview: {overview}")
            print()
        
        # Show statistics
        print(f"📈 Statistics:")
        print(f"   Average similarity score: {sum(m.get('similarity_score', 0) for m in recommendations) / len(recommendations):.1f}")
        print(f"   Average familiarity score: {sum(m.get('familiarity_score', 0) for m in recommendations) / len(recommendations):.1f}")
        print(f"   Average final score: {sum(m.get('final_score', 0) for m in recommendations) / len(recommendations):.1f}")
        
        # Show source tag distribution
        source_tags = {}
        for movie in recommendations:
            for tag in movie.get('source_tags', []):
                source_tags[tag] = source_tags.get(tag, 0) + 1
        
        print(f"\n🏷️ Source tag distribution:")
        for tag, count in sorted(source_tags.items(), key=lambda x: x[1], reverse=True):
            print(f"   {tag}: {count} movies")
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()

def test_keyword_mapping():
    """Test the keyword mapping functionality"""
    
    print("\n🔗 Testing Keyword Mapping")
    print("=" * 40)
    
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("❌ TMDB_API_KEY not set")
        return
    
    recommender = TagBasedRecommender(api_key)
    
    # Test tags
    test_tags = ["feel-good", "comedy", "inspiring", "thrilling", "romantic"]
    
    print("Testing keyword ID lookup:")
    for tag in test_tags:
        keyword_id = recommender._get_keyword_id(tag)
        if keyword_id:
            print(f"   ✅ '{tag}' -> ID {keyword_id}")
        else:
            print(f"   ❌ '{tag}' -> No keyword found")
    
    # Show available keywords
    print(f"\n📊 Keywords database contains {len(recommender.keywords_db)} keywords")
    
    # Show some example keywords
    print("Example keywords:")
    for i, (name, keyword_id) in enumerate(list(recommender.keywords_db.items())[:10]):
        print(f"   {name} -> {keyword_id}")

def test_calibration_filters():
    """Test the calibration to filters conversion"""
    
    print("\n⚙️ Testing Calibration Filters")
    print("=" * 40)
    
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("❌ TMDB_API_KEY not set")
        return
    
    recommender = TagBasedRecommender(api_key)
    
    # Test different calibration settings
    test_settings = [
        {
            'name': 'Classic Films',
            'settings': {'era': 3, 'runtime': 4, 'popularity': 6, 'familiarity': 7}
        },
        {
            'name': 'Modern Blockbusters',
            'settings': {'era': 9, 'runtime': 8, 'popularity': 9, 'familiarity': 6}
        },
        {
            'name': 'Indie Films',
            'settings': {'era': 6, 'runtime': 3, 'popularity': 2, 'familiarity': 3}
        }
    ]
    
    for test in test_settings:
        filters = recommender._convert_calibration_to_filters(test['settings'])
        print(f"\n{test['name']}:")
        for key, value in filters.items():
            print(f"   {key}: {value}")

def main():
    """Main test function"""
    print("🧪 Tag-Based Recommender Test Suite")
    print("=" * 60)
    
    # Run tests
    test_keyword_mapping()
    test_calibration_filters()
    test_tag_based_recommender()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 