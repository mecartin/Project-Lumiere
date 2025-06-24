import requests
import json
import time
import os
from datetime import datetime
from collections import defaultdict, Counter
import math
from typing import List, Dict, Set, Optional, Tuple
import pandas as pd
import csv

class TagBasedRecommender:
    """
    Advanced tag-based movie recommendation system that:
    1. Makes TMDB API calls for each selected tag with user filters
    2. Gets similar movies for user's top 40 movies
    3. Rates movies based on familiarity (cast/crew/keywords from user profile)
    4. Filters based on user's familiarity preference from calibration
    5. Ranks movies based on similarity to user's preferred keywords
    """
    
    def __init__(self, api_key: str, cache_dir: str = "tmdb_cache"):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.cache_dir = cache_dir
        self.session = requests.Session()
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load TMDB keywords database (to be generated later)
        self.keywords_db = self._load_keywords_database()
        
    def _load_keywords_database(self) -> Dict[str, int]:
        """Load keywords database from all_keywords.csv mapping keyword names to IDs"""
        keywords_file = os.path.join(os.path.dirname(__file__), "all_keywords.csv")
        keywords_db = {}
        if os.path.exists(keywords_file):
            try:
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    for row in reader:
                        if len(row) >= 2:
                            name = row[0].strip().lower()
                            try:
                                kid = int(row[1])
                                keywords_db[name] = kid
                            except ValueError:
                                continue
                if keywords_db:
                    print(f"✅ Loaded {len(keywords_db)} keywords from all_keywords.csv")
                    return keywords_db
            except Exception as e:
                print(f"Warning: Could not load keywords from all_keywords.csv: {e}")
        print("⚠️ No keywords database found, using manual mapping")
        return {}
    
    def _make_cached_request(self, endpoint: str, params: Optional[Dict] = None, cache_key: Optional[str] = None) -> Optional[Dict]:
        """Make TMDB API request with caching"""
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        # Create cache filename
        if cache_key:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        else:
            # Create cache key from endpoint and params
            param_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items()) if k != 'api_key'])
            cache_file = os.path.join(self.cache_dir, f"{endpoint.replace('/', '_')}_{param_str}.json")
        
        # Check cache first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache file {cache_file}: {e}")
        
        # Make API request
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache the response
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Warning: Could not cache response: {e}")
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"API request failed for {endpoint}: {e}")
            return None
    
    def _get_keyword_id(self, keyword_name: str) -> Optional[int]:
        """Get TMDB keyword ID from keyword name"""
        return self.keywords_db.get(keyword_name.lower())
    
    def _convert_calibration_to_filters(self, calibration_settings: Dict) -> Dict:
        """Convert calibration settings to TMDB API filters"""
        filters = {}
        
        # Era filter (1-10 scale to year ranges)
        era = calibration_settings.get('era', 5)
        if era <= 3:
            filters['primary_release_date.gte'] = '1920-01-01'
            filters['primary_release_date.lte'] = '1980-12-31'
        elif era <= 7:
            filters['primary_release_date.gte'] = '1980-01-01'
            filters['primary_release_date.lte'] = '2010-12-31'
        else:
            filters['primary_release_date.gte'] = '2010-01-01'
            filters['primary_release_date.lte'] = '2030-12-31'
        
        # Runtime filter (1-10 scale to minutes)
        runtime = calibration_settings.get('runtime', 5)
        if runtime <= 3:
            filters['with_runtime.lte'] = 90
        elif runtime <= 7:
            filters['with_runtime.gte'] = 90
            filters['with_runtime.lte'] = 150
        else:
            filters['with_runtime.gte'] = 150
        
        # Popularity filter (1-10 scale to sort order)
        popularity = calibration_settings.get('popularity', 5)
        if popularity <= 3:
            filters['sort_by'] = 'popularity.asc'  # Less popular first
        elif popularity <= 7:
            filters['sort_by'] = 'popularity.desc'  # Medium popularity
        else:
            filters['sort_by'] = 'vote_average.desc'  # Highly rated
        
        return filters
    
    def _get_movies_by_keyword(self, keyword_id: int, filters: Dict, max_pages: int = 3) -> List[Dict]:
        """Get movies by keyword ID with filters"""
        movies = []
        
        for page in range(1, max_pages + 1):
            params = {
                'page': page,
                **filters
            }
            
            # Check if this is a genre ID or keyword ID
            # Genre IDs are typically < 100, keyword IDs are > 1000
            if keyword_id < 100:
                # This is a genre ID, use with_genres parameter
                params['with_genres'] = keyword_id
                cache_key = f"genre_{keyword_id}_page_{page}"
            else:
                # This is a keyword ID, use with_keywords parameter
                params['with_keywords'] = keyword_id
                cache_key = f"keyword_{keyword_id}_page_{page}"
            
            data = self._make_cached_request(
                "/discover/movie", 
                params, 
                cache_key
            )
            
            if data and data.get('results'):
                movies.extend(data['results'])
            
            # Rate limiting
            time.sleep(0.1)
        
        return movies
    
    def _get_similar_movies(self, movie_id: int, max_pages: int = 2) -> List[Dict]:
        """Get similar movies for a given movie ID"""
        movies = []
        
        for page in range(1, max_pages + 1):
            params = {'page': page}
            
            data = self._make_cached_request(
                f"/movie/{movie_id}/similar",
                params,
                f"similar_{movie_id}_page_{page}"
            )
            
            if data and data.get('results'):
                movies.extend(data['results'])
            
            time.sleep(0.1)
        
        return movies
    
    def _get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed movie information including credits and keywords"""
        return self._make_cached_request(
            f"/movie/{movie_id}",
            {'append_to_response': 'credits,keywords'},
            f"movie_details_{movie_id}"
        )
    
    def _calculate_familiarity_score(self, movie_data: Dict, user_profile: Dict) -> float:
        """Calculate familiarity score based on user's movie history"""
        if not movie_data:
            return 0.0
        
        score = 0.0
        max_score = 100.0
        
        # Extract movie features
        credits = movie_data.get('credits', {})
        keywords = movie_data.get('keywords', {}).get('keywords', [])
        
        # Cast familiarity
        cast = credits.get('cast', [])[:10]  # Top 10 cast members
        cast_names = [actor['name'].lower() for actor in cast]
        
        for actor in cast_names:
            if actor in user_profile.get('known_actors', set()):
                score += 5.0  # 5 points per known actor
        
        # Crew familiarity (directors, writers)
        crew = credits.get('crew', [])
        directors = [c['name'].lower() for c in crew if c['job'] == 'Director']
        writers = [c['name'].lower() for c in crew if c['job'] in ['Writer', 'Screenplay', 'Story']]
        
        for director in directors:
            if director in user_profile.get('known_directors', set()):
                score += 10.0  # 10 points per known director
        
        for writer in writers:
            if writer in user_profile.get('known_writers', set()):
                score += 7.0  # 7 points per known writer
        
        # Keyword familiarity
        movie_keywords = [k['name'].lower() for k in keywords]
        for keyword in movie_keywords:
            if keyword in user_profile.get('known_keywords', set()):
                score += 2.0  # 2 points per known keyword
        
        # Genre familiarity
        genres = [g['name'].lower() for g in movie_data.get('genres', [])]
        for genre in genres:
            if genre in user_profile.get('preferred_genres', set()):
                score += 3.0  # 3 points per preferred genre
        
        return min(score, max_score)
    
    def _calculate_similarity_score(self, movie_data: Dict, user_tags: List[str]) -> float:
        """Calculate similarity score based on user's selected tags"""
        if not movie_data or not user_tags:
            return 0.0
        
        score = 0.0
        max_score = 100.0
        
        # Extract movie features
        keywords = movie_data.get('keywords', {}).get('keywords', [])
        movie_keywords = [k['name'].lower() for k in keywords]
        genres = movie_data.get('genres', [])
        overview = movie_data.get('overview', '').lower()
        
        # Tag to keyword mapping (simplified - would need more sophisticated mapping)
        tag_keyword_mapping = {
            'feel-good': ['feel good', 'uplifting', 'heartwarming', 'positive'],
            'thought-provoking': ['thought provoking', 'philosophical', 'deep', 'meaningful'],
            'inspiring': ['inspiring', 'motivational', 'empowering', 'heroic'],
            'relaxing': ['relaxing', 'calm', 'peaceful', 'tranquil'],
            'exciting': ['exciting', 'thrilling', 'action', 'adventure'],
            'romantic': ['romantic', 'love', 'romance', 'passion'],
            'funny': ['funny', 'comedy', 'humorous', 'hilarious'],
            'sad': ['sad', 'melancholy', 'tragic', 'emotional'],
            'thrilling': ['thrilling', 'suspense', 'tension', 'edge of seat'],
            'mysterious': ['mysterious', 'mystery', 'enigmatic', 'puzzling'],
            'action': ['action', 'fight', 'battle', 'explosion'],
            'comedy': ['comedy', 'funny', 'humor', 'joke'],
            'drama': ['drama', 'dramatic', 'serious', 'intense'],
            'horror': ['horror', 'scary', 'frightening', 'terrifying'],
            'sci-fi': ['sci-fi', 'science fiction', 'futuristic', 'space'],
            'romance': ['romance', 'love story', 'romantic', 'relationship'],
            'thriller': ['thriller', 'suspense', 'tension', 'mystery'],
            'documentary': ['documentary', 'real', 'factual', 'educational'],
            'animation': ['animation', 'animated', 'cartoon', 'drawn'],
            'family': ['family', 'children', 'kid friendly', 'wholesome']
        }
        
        # Calculate similarity for each user tag
        for tag in user_tags:
            tag_keywords = tag_keyword_mapping.get(tag.lower(), [])
            
            # Check keyword matches
            for tag_keyword in tag_keywords:
                if any(tag_keyword in mk for mk in movie_keywords):
                    score += 8.0  # 8 points per keyword match
                
                if tag_keyword in overview:
                    score += 3.0  # 3 points per overview mention
            
            # Check genre matches
            for tag_keyword in tag_keywords:
                if any(tag_keyword in genre['name'].lower() for genre in genres):
                    score += 5.0  # 5 points per genre match
        
        return min(score, max_score)
    
    def _build_user_profile(self, user_movies: List[Dict]) -> Dict:
        """Build user profile from their movie history"""
        profile = {
            'known_actors': set(),
            'known_directors': set(),
            'known_writers': set(),
            'known_keywords': set(),
            'preferred_genres': set(),
            'total_movies': len(user_movies)
        }
        
        for movie in user_movies:
            # Extract features from user's movies
            if 'cast' in movie:
                profile['known_actors'].update([actor.lower() for actor in movie['cast'][:5]])
            
            if 'directors' in movie:
                profile['known_directors'].update([director.lower() for director in movie['directors']])
            
            if 'writers' in movie:
                profile['known_writers'].update([writer.lower() for writer in movie['writers']])
            
            if 'keywords' in movie:
                profile['known_keywords'].update([keyword.lower() for keyword in movie['keywords'][:10]])
            
            if 'genres' in movie:
                profile['preferred_genres'].update([genre.lower() for genre in movie['genres']])
        
        # Convert sets to lists for JSON serialization
        for key in ['known_actors', 'known_directors', 'known_writers', 'known_keywords', 'preferred_genres']:
            profile[key] = list(profile[key])
        
        return profile
    
    def get_recommendations(self, 
                          user_tags: List[str], 
                          calibration_settings: Dict,
                          user_movies: Optional[List[Dict]] = None,
                          max_recommendations: int = 20) -> List[Dict]:
        """
        Main recommendation function that implements the complete algorithm
        
        Args:
            user_tags: List of tag names selected by user
            calibration_settings: User's calibration preferences
            user_movies: User's movie history (for familiarity calculation)
            max_recommendations: Maximum number of recommendations to return
        
        Returns:
            List of recommended movies with scores and details
        """
        print(f"🎬 Starting tag-based recommendations for {len(user_tags)} tags")
        
        # Build user profile from movie history
        user_profile = self._build_user_profile(user_movies or [])
        print(f"📊 Built user profile with {len(user_profile['known_actors'])} known actors")
        
        # Convert calibration settings to API filters
        filters = self._convert_calibration_to_filters(calibration_settings)
        print(f"⚙️ Applied filters: {filters}")
        
        # Step 1: Get movies for each tag (recom_superlist)
        all_movies = {}
        
        for tag in user_tags:
            print(f"🔍 Processing tag: {tag}")
            
            # Get keyword ID for this tag
            keyword_id = self._get_keyword_id(tag)
            if not keyword_id:
                print(f"⚠️ No keyword ID found for tag: {tag}")
                continue
            
            # Get movies for this keyword
            tag_movies = self._get_movies_by_keyword(keyword_id, filters)
            print(f"📽️ Found {len(tag_movies)} movies for tag '{tag}'")
            
            # Add to superlist
            for movie in tag_movies:
                movie_id = movie['id']
                if movie_id not in all_movies:
                    all_movies[movie_id] = movie
                    all_movies[movie_id]['source_tags'] = [tag]
                else:
                    all_movies[movie_id]['source_tags'].append(tag)
        
        print(f"📋 Superlist contains {len(all_movies)} unique movies")
        
        # Step 2: Get similar movies for user's top 40 movies
        if user_movies:
            top_movies = user_movies[:40]  # Top 40 movies
            print(f"🎯 Getting similar movies for top {len(top_movies)} user movies")
            
            for movie in top_movies:
                if 'tmdb_id' in movie and movie['tmdb_id']:
                    similar_movies = self._get_similar_movies(movie['tmdb_id'])
                    
                    for similar_movie in similar_movies:
                        movie_id = similar_movie['id']
                        if movie_id not in all_movies:
                            all_movies[movie_id] = similar_movie
                            all_movies[movie_id]['source_tags'] = ['similar_to_user_favorite']
                        else:
                            all_movies[movie_id]['source_tags'].append('similar_to_user_favorite')
        
        # Step 3: Rate movies based on familiarity
        print("🎭 Calculating familiarity scores...")
        familiarity_scores = {}
        
        for movie_id, movie in all_movies.items():
            # Get detailed movie information
            movie_details = self._get_movie_details(movie_id)
            if movie_details:
                familiarity_score = self._calculate_familiarity_score(movie_details, user_profile)
                familiarity_scores[movie_id] = familiarity_score
                movie['familiarity_score'] = familiarity_score
            else:
                movie['familiarity_score'] = 0.0
        
        # Step 4: Filter based on familiarity preference
        familiarity_preference = calibration_settings.get('familiarity', 5)
        print(f"🎛️ Filtering by familiarity preference: {familiarity_preference}")
        
        filtered_movies = {}
        for movie_id, movie in all_movies.items():
            familiarity_score = movie.get('familiarity_score', 0.0)
            
            # Convert familiarity preference (1-10) to score threshold
            # Make filtering more lenient to ensure we get recommendations
            if familiarity_preference <= 3:
                # Prefer unfamiliar movies (low familiarity scores)
                if familiarity_score <= 50:  # Increased from 30
                    filtered_movies[movie_id] = movie
            elif familiarity_preference <= 7:
                # Prefer medium familiarity - accept most movies
                if familiarity_score <= 80:  # Increased from 60
                    filtered_movies[movie_id] = movie
            else:
                # Prefer familiar movies (high familiarity scores)
                if familiarity_score >= 20:  # Decreased from 40
                    filtered_movies[movie_id] = movie
        
        # If no movies pass the filter, accept all movies
        if not filtered_movies:
            print("⚠️ No movies passed familiarity filter, accepting all movies")
            filtered_movies = all_movies
        
        print(f"🔍 Filtered to {len(filtered_movies)} movies based on familiarity")
        
        # Step 5: Calculate similarity scores and rank
        print("📊 Calculating similarity scores...")
        ranked_movies = []
        
        for movie_id, movie in filtered_movies.items():
            # Get detailed movie information for similarity calculation
            movie_details = self._get_movie_details(movie_id)
            if movie_details:
                similarity_score = self._calculate_similarity_score(movie_details, user_tags)
                movie['similarity_score'] = similarity_score
                
                # Calculate final score (weighted combination)
                final_score = (
                    similarity_score * 0.6 +  # 60% weight to similarity
                    movie.get('familiarity_score', 0) * 0.4  # 40% weight to familiarity
                )
                movie['final_score'] = final_score
                
                # Add movie details
                movie.update({
                    'title': movie_details.get('title', movie.get('title', 'Unknown')),
                    'overview': movie_details.get('overview', ''),
                    'release_date': movie_details.get('release_date', ''),
                    'poster_path': movie_details.get('poster_path', ''),
                    'backdrop_path': movie_details.get('backdrop_path', ''),
                    'vote_average': movie_details.get('vote_average', 0),
                    'vote_count': movie_details.get('vote_count', 0),
                    'runtime': movie_details.get('runtime', 0),
                    'genres': [g['name'] for g in movie_details.get('genres', [])],
                    'tmdb_id': movie_id
                })
                
                ranked_movies.append(movie)
        
        # Sort by final score
        ranked_movies.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        # Return top recommendations
        recommendations = ranked_movies[:max_recommendations]
        
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        return recommendations
    
    def generate_keywords_database(self):
        """Generate TMDB keywords database (to be called separately)"""
        print("🔧 Generating TMDB keywords database...")
        
        # Get all keywords from TMDB
        keywords = []
        page = 1
        
        while True:
            data = self._make_cached_request("/keyword/list", {'page': page})
            if not data or not data.get('results'):
                break
            
            keywords.extend(data['results'])
            print(f"📄 Loaded page {page} with {len(data['results'])} keywords")
            
            page += 1
            time.sleep(0.1)  # Rate limiting
        
        # Create mapping
        keywords_db = {}
        for keyword in keywords:
            keywords_db[keyword['name'].lower()] = keyword['id']
        
        # Save to file
        keywords_file = os.path.join(self.cache_dir, "tmdb_keywords.json")
        with open(keywords_file, 'w', encoding='utf-8') as f:
            json.dump(keywords_db, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(keywords_db)} keywords to database")
        self.keywords_db = keywords_db
        
        return keywords_db


# Example usage
if __name__ == "__main__":
    # Initialize with your TMDB API key
    API_KEY = os.getenv("TMDB_API_KEY", "YOUR_TMDB_API_KEY")
    
    if API_KEY == "YOUR_TMDB_API_KEY":
        print("Please set your TMDB API key")
        exit(1)
    
    recommender = TagBasedRecommender(API_KEY)
    
    # Example user data
    user_tags = ["feel-good", "inspiring", "comedy"]
    calibration_settings = {
        'era': 7,  # 1980s-2010s
        'runtime': 6,  # 90-150 minutes
        'popularity': 5,  # Medium popularity
        'familiarity': 4  # Somewhat familiar
    }
    
    # Get recommendations
    recommendations = recommender.get_recommendations(
        user_tags=user_tags,
        calibration_settings=calibration_settings,
        user_movies=[],  # Would be loaded from user's movie history
        max_recommendations=10
    )
    
    print("\n🎬 Top Recommendations:")
    for i, movie in enumerate(recommendations[:5]):
        print(f"{i+1}. {movie['title']} ({movie.get('release_date', 'Unknown')[:4]})")
        print(f"   Score: {movie.get('final_score', 0):.1f}")
        print(f"   Similarity: {movie.get('similarity_score', 0):.1f}")
        print(f"   Familiarity: {movie.get('familiarity_score', 0):.1f}")
        print(f"   Genres: {', '.join(movie.get('genres', []))}")
        print() 