#!/usr/bin/env python3
"""
Test script to verify user data loading from enhanced_movie_scores_detailed.json
"""

import json
import os
from tag_based_recommender import TagBasedRecommender

def test_user_data_loading():
    """Test loading user data and building user profile"""
    
    print("🧪 Testing User Data Loading")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("❌ TMDB_API_KEY environment variable not set")
        return
    
    # Initialize recommender
    print("🔧 Initializing recommender...")
    recommender = TagBasedRecommender(api_key)
    
    # Test loading user data
    try:
        user_data_path = os.path.join(os.path.dirname(__file__), "enhanced_movie_scores_detailed.json")
        if os.path.exists(user_data_path):
            with open(user_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract user preferences and enriched movies
            user_preferences = data.get('user_preferences', {})
            enriched_movies = data.get('enriched_movies', {})
            
            print(f"📊 Found {len(enriched_movies)} movies in enhanced data")
            print(f"🎭 User preferences: {len(user_preferences.get('preferred_actors', []))} actors, "
                  f"{len(user_preferences.get('preferred_directors', []))} directors, "
                  f"{len(user_preferences.get('preferred_keywords', []))} keywords")
            
            # Convert enriched movies to list format expected by recommender
            user_movies = []
            for movie_id, movie_data in enriched_movies.items():
                # Extract cast names from the cast data
                cast_names = []
                if 'cast' in movie_data:
                    cast_names = [actor.get('name', '') for actor in movie_data['cast'][:10]]
                
                # Extract director names from crew data (if available)
                directors = []
                if 'crew' in movie_data:
                    directors = [crew.get('name', '') for crew in movie_data['crew'] 
                               if crew.get('job', '').lower() == 'director']
                
                # Create movie object in expected format
                movie_obj = {
                    'tmdb_id': movie_data.get('tmdb_id'),
                    'title': movie_data.get('title'),
                    'cast': cast_names,
                    'directors': directors,
                    'genres': movie_data.get('genres', []),
                    'keywords': movie_data.get('keywords', []),
                    'release_date': movie_data.get('release_date'),
                    'vote_average': movie_data.get('vote_average'),
                    'popularity': movie_data.get('popularity')
                }
                user_movies.append(movie_obj)
            
            print(f"📋 Converted {len(user_movies)} movies to recommender format")
            
            # Test building user profile
            print("\n🔍 Testing user profile building...")
            user_profile = recommender._build_user_profile(user_movies)
            
            print(f"✅ Built user profile with:")
            print(f"   - {len(user_profile['known_actors'])} known actors")
            print(f"   - {len(user_profile['known_directors'])} known directors")
            print(f"   - {len(user_profile['known_keywords'])} known keywords")
            print(f"   - {len(user_profile['preferred_genres'])} preferred genres")
            
            # Show some examples
            if user_profile['known_actors']:
                print(f"   Sample actors: {user_profile['known_actors'][:5]}")
            if user_profile['known_directors']:
                print(f"   Sample directors: {user_profile['known_directors'][:5]}")
            if user_profile['known_keywords']:
                print(f"   Sample keywords: {user_profile['known_keywords'][:5]}")
            
        else:
            print("❌ enhanced_movie_scores_detailed.json not found")
            
    except Exception as e:
        print(f"❌ Error testing user data loading: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_data_loading() 