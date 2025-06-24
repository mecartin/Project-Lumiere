import requests
import pandas as pd
import time
from datetime import datetime
import json
from collections import Counter
import math
import os

class MovieTasteEnricher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        # TMDB uses simple API key parameter, not Bearer token
        self.session = requests.Session()
        
    def _make_request(self, endpoint, params=None):
        """Make authenticated request to TMDB API"""
        if params is None:
            params = {}
        
        # Add API key to all requests
        params['api_key'] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error for {endpoint}: {e}")
            return None
        
    def search_movie(self, title, year):
        """Search for movie by title and year"""
        params = {
            "query": title,
            "year": year,
            "language": "en-US"
        }
        
        data = self._make_request("/search/movie", params)
        
        if data and data.get('results'):
            # Return the best match (first result is usually most relevant)
            return data['results'][0]['id']
        
        # If no results with year, try without year
        if year:
            print(f"No results for {title} ({year}), trying without year...")
            params_no_year = {
                "query": title,
                "language": "en-US"
            }
            data = self._make_request("/search/movie", params_no_year)
            
            if data and data.get('results'):
                # Look for closest year match
                for result in data['results']:
                    if result.get('release_date'):
                        try:
                            result_year = int(result['release_date'][:4])
                            if abs(result_year - year) <= 1:  # Within 1 year
                                return result['id']
                        except:
                            continue
                # If no close year match, return first result
                return data['results'][0]['id']
        
        return None
    
    def get_movie_details(self, movie_id):
        """Get comprehensive movie details"""
        params = {
            "append_to_response": "credits,keywords,videos,recommendations,similar,reviews",
            "language": "en-US"
        }
        
        return self._make_request(f"/movie/{movie_id}", params)
    
    def test_api_connection(self):
        """Test if API key is working"""
        print("Testing TMDB API connection...")
        
        # Test with a simple configuration request
        data = self._make_request("/configuration")
        
        if data:
            print("✓ TMDB API connection successful!")
            return True
        else:
            print("✗ TMDB API connection failed!")
            print("Please check your API key and ensure it's valid.")
            print("Get your API key from: https://www.themoviedb.org/settings/api")
            return False
    def extract_features(self, movie_data):
        """Extract relevant features from movie data"""
        if not movie_data:
            return {}
        
        features = {
            'tmdb_id': movie_data.get('id'),
            'title': movie_data.get('title'),
            'release_date': movie_data.get('release_date'),
            'runtime': movie_data.get('runtime'),
            'budget': movie_data.get('budget'),
            'revenue': movie_data.get('revenue'),
            'popularity': movie_data.get('popularity'),
            'vote_average': movie_data.get('vote_average'),
            'vote_count': movie_data.get('vote_count'),
            'genres': [g['name'] for g in movie_data.get('genres', [])],
            'production_companies': [pc['name'] for pc in movie_data.get('production_companies', [])],
            'production_countries': [pc['name'] for pc in movie_data.get('production_countries', [])],
            'spoken_languages': [sl['english_name'] for sl in movie_data.get('spoken_languages', [])],
            'overview': movie_data.get('overview', ''),
            'tagline': movie_data.get('tagline', ''),
        }
        
        # Extract cast information
        credits = movie_data.get('credits', {})
        cast = credits.get('cast', [])[:10]  # Top 10 cast members
        features['cast'] = [{'name': actor['name'], 'character': actor['character']} for actor in cast]
        features['cast_names'] = [actor['name'] for actor in cast]
        
        # Extract crew information
        crew = credits.get('crew', [])
        directors = [c['name'] for c in crew if c['job'] == 'Director']
        writers = [c['name'] for c in crew if c['job'] in ['Writer', 'Screenplay', 'Story']]
        producers = [c['name'] for c in crew if c['job'] in ['Producer', 'Executive Producer']]
        
        features['directors'] = directors
        features['writers'] = writers
        features['producers'] = producers
        
        # Extract keywords
        keywords = movie_data.get('keywords', {}).get('keywords', [])
        features['keywords'] = [k['name'] for k in keywords]
        
        return features
    
    def calculate_enhanced_score(self, original_data, enriched_features, user_preferences):
        """Calculate enhanced taste score based on enriched data"""
        score = float(original_data['taste_score'])
        
        
        # TMDB-based enhancements
        tmdb_weight = 0
        
        if enriched_features:
            # Popularity boost (but not too much to avoid mainstream bias)
            popularity = enriched_features.get('popularity', 0)
            if popularity > 0:
                tmdb_weight += min(math.log(popularity) * 2, 15)
            
            # Vote average alignment with user rating
            vote_avg = enriched_features.get('vote_average', 0)
            user_rating = original_data['rating']
            if vote_avg > 0:
                # Reward alignment between user rating and TMDB rating
                rating_diff = abs((vote_avg * 0.5) - user_rating)  # Convert 10-scale to 5-scale
                alignment_bonus = max(5 - rating_diff, 0) * 2
                tmdb_weight += alignment_bonus
            
            # Genre preferences (would need to be calculated from user's movie history)
            genres = enriched_features.get('genres', [])
            for genre in genres:
                if genre in user_preferences.get('preferred_genres', []):
                    tmdb_weight += 3
            
            # Director preferences
            directors = enriched_features.get('directors', [])
            for director in directors:
                if director in user_preferences.get('preferred_directors', []):
                    tmdb_weight += 5
            
            # Cast preferences
            cast_names = enriched_features.get('cast_names', [])
            for actor in cast_names:
                if actor in user_preferences.get('preferred_actors', []):
                    tmdb_weight += 2
            
            # Keyword preferences
            keywords = enriched_features.get('keywords', [])
            for keyword in keywords:
                if keyword in user_preferences.get('preferred_keywords', []):
                    tmdb_weight += 1
        
        # Calculate final enhanced score
        enhanced_score = (
            score*0.85 + tmdb_weight*0.15
        )
        
        return round(enhanced_score, 2)
    
    def analyze_user_preferences(self, movies_data, enriched_data):
        """Analyze user preferences from their movie data"""
        preferences = {
            'preferred_genres': [],
            'preferred_directors': [],
            'preferred_actors': [],
            'preferred_keywords': [],
            'preferred_decades': [],
            'preferred_languages': []
        }
        
        # Collect all preferences from highly rated movies (4+ stars)
        high_rated_movies = [movie for movie in movies_data if movie['rating'] >= 4]
        
        all_genres = []
        all_directors = []
        all_actors = []
        all_keywords = []
        all_decades = []
        all_languages = []
        
        for movie in high_rated_movies:
            movie_id = movie.get('tmdb_id')
            if movie_id and movie_id in enriched_data:
                features = enriched_data[movie_id]
                
                all_genres.extend(features.get('genres', []))
                all_directors.extend(features.get('directors', []))
                all_actors.extend(features.get('cast_names', []))
                all_keywords.extend(features.get('keywords', []))
                all_languages.extend(features.get('spoken_languages', []))
                
                # Extract decade from release date
                release_date = features.get('release_date', '')
                if release_date:
                    try:
                        year = int(release_date[:4])
                        decade = (year // 10) * 10
                        all_decades.append(decade)
                    except:
                        pass
        
        # Get top preferences based on frequency
        preferences['preferred_genres'] = [item for item, count in Counter(all_genres).most_common(10)]
        preferences['preferred_directors'] = [item for item, count in Counter(all_directors).most_common(20)]
        preferences['preferred_actors'] = [item for item, count in Counter(all_actors).most_common(25)]
        preferences['preferred_keywords'] = [item for item, count in Counter(all_keywords).most_common(30)]
        preferences['preferred_decades'] = [item for item, count in Counter(all_decades).most_common(7)]
        preferences['preferred_languages'] = [item for item, count in Counter(all_languages).most_common(8)]
        
        return preferences
    
    def process_movies(self, csv_file_path, output_file_path, top_n=60):
        """Main processing function"""
        # Test API connection first
        if not self.test_api_connection():
            return None, None
        
        # Read the CSV file
        try:
            df = pd.read_csv(csv_file_path)
        except FileNotFoundError:
            print(f"Error: Could not find file {csv_file_path}")
            print("Please make sure your CSV file exists and the path is correct.")
            return None, None
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None, None
        
        # Take top N movies
        top_movies = df.head(top_n)
        
        print(f"Processing top {len(top_movies)} movies...")
        
        enriched_data = {}
        movies_data = []
        
        # Process each movie
        for idx, row in top_movies.iterrows():
            print(f"Processing {idx + 1}/{len(top_movies)}: {row['name']} ({row['year']})")
            
            # Search for movie on TMDB
            movie_id = self.search_movie(row['name'], row['year'])
            
            if movie_id:
                # Get detailed movie information
                movie_details = self.get_movie_details(movie_id)
                
                if movie_details:
                    # Extract features
                    features = self.extract_features(movie_details)
                    enriched_data[movie_id] = features
                    
                    # Prepare movie data
                    movie_data = {
                        'tmdb_id': movie_id,
                        'taste_score': row['taste_score'],
                        'name': row['name'],
                        'year': row['year'],
                        'rating': row['rating'],
                        'liked': row['liked'],
                        'no_of_watches': row['no_of_watches'],
                        'reviewed': row['reviewed'],
                        'in_lists_count': row['in_lists_count'],
                        'url': row['url']
                    }
                    movies_data.append(movie_data)
                    
                    # Rate limiting
                    time.sleep(0.25)  # 4 requests per second limit
                else:
                    print(f"Could not get details for {row['name']}")
            else:
                print(f"Could not find {row['name']} ({row['year']}) on TMDB")
        
        # Analyze user preferences
        print("Analyzing user preferences...")
        user_preferences = self.analyze_user_preferences(movies_data, enriched_data)
        
        # Calculate enhanced scores
        print("Calculating enhanced scores...")
        for movie_data in movies_data:
            movie_id = movie_data['tmdb_id']
            features = enriched_data.get(movie_id, {})
            enhanced_score = self.calculate_enhanced_score(movie_data, features, user_preferences)
            movie_data['enhanced_taste_score'] = enhanced_score
            movie_data['score_improvement'] = enhanced_score - movie_data['taste_score']
        
        # Sort by enhanced score
        movies_data.sort(key=lambda x: x['enhanced_taste_score'], reverse=True)
        
        # Create output DataFrame
        output_data = []
        for movie_data in movies_data:
            movie_id = movie_data['tmdb_id']
            features = enriched_data.get(movie_id, {})
            
            output_row = {
                'original_rank': movies_data.index(movie_data) + 1,
                'enhanced_rank': movies_data.index(movie_data) + 1,
                'original_taste_score': movie_data['taste_score'],
                'enhanced_taste_score': movie_data['enhanced_taste_score'],
                'score_improvement': movie_data['score_improvement'],
                'name': movie_data['name'],
                'year': movie_data['year'],
                'rating': movie_data['rating'],
                'liked': movie_data['liked'],
                'no_of_watches': movie_data['no_of_watches'],
                'tmdb_id': movie_id,
                'tmdb_rating': features.get('vote_average', 0),
                'tmdb_popularity': features.get('popularity', 0),
                'genres': ', '.join(features.get('genres', [])),
                'directors': ', '.join(features.get('directors', [])),
                'main_cast': ', '.join(features.get('cast_names', [])[:5]),
                'keywords': ', '.join(features.get('keywords', [])[:10]),
                'runtime': features.get('runtime', 0),
                'budget': features.get('budget', 0),
                'revenue': features.get('revenue', 0)
            }
            output_data.append(output_row)
        
        # Save to CSV
        output_df = pd.DataFrame(output_data)
        output_df.to_csv(output_file_path, index=False)
        
        # Save detailed data as JSON
        detailed_output = {
            'user_preferences': user_preferences,
            'enriched_movies': enriched_data,
            'processed_movies': movies_data
        }
        
        json_output_path = output_file_path.replace('.csv', '_detailed.json')
        with open(json_output_path, 'w') as f:
            json.dump(detailed_output, f, indent=2, default=str)
        
        print(f"Enhanced movie data saved to {output_file_path}")
        print(f"Detailed data saved to {json_output_path}")
        print(f"User preferences discovered: {len(user_preferences['preferred_genres'])} genres, "
              f"{len(user_preferences['preferred_directors'])} directors, "
              f"{len(user_preferences['preferred_actors'])} actors")
        
        return output_df, user_preferences

# Usage example
if __name__ == "__main__":
    # Initialize with your TMDB API key
    print("TMDB Movie Taste Enricher")
    print("=" * 50)
    
    # Get API key from environment variable
    API_KEY = os.getenv('TMDB_API_KEY')
    
    if not API_KEY:
        print("Please set your TMDB API key in the environment variable TMDB_API_KEY")
        print("Get your API key from: https://www.themoviedb.org/settings/api")
        exit(1)
    
    enricher = MovieTasteEnricher(API_KEY)
    
    # Process the movies
    input_file = "letterboxd_ranked_by_taste.csv"  # Your input CSV file
    output_file = "enhanced_movie_scores.csv"
    
    try:
        enhanced_df, preferences = enricher.process_movies(input_file, output_file, top_n=60)
        
        if enhanced_df is not None:
            print("\nTop 10 Enhanced Movies:")
            print(enhanced_df[['enhanced_rank', 'name', 'year', 'enhanced_taste_score', 'score_improvement']].head(10))
            
            print(f"\nTop Preferred Genres: {preferences['preferred_genres'][:5]}")
            print(f"Top Preferred Directors: {preferences['preferred_directors'][:5]}")
        
    except Exception as e:
        print(f"Error processing movies: {e}")
        print("Please check your input file format and API key.")