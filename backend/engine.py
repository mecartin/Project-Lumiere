import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from database import SessionLocal, User, Movie, MoodTag, user_movies, movie_tags
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import pandas as pd

class RecommendationEngine:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db = SessionLocal()
        self.user = self.db.query(User).filter(User.id == user_id).first()
        
    def build_user_profile(self) -> Dict:
        """Build taste profile from user's watched/rated movies"""
        # Get user's movie history
        user_movies_data = self.db.execute(
            user_movies.select().where(user_movies.c.user_id == self.user_id)
        ).fetchall()
        
        if not user_movies_data:
            return {}
        
        # Analyze preferences
        genre_counts = {}
        director_counts = {}
        avg_rating = []
        avg_year = []
        
        for um in user_movies_data:
            movie = self.db.query(Movie).filter(Movie.id == um.movie_id).first()
            if movie:
                # Genre preferences
                if movie.genres:
                    for genre in movie.genres:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
                
                # Director preferences
                if movie.director:
                    director_counts[movie.director] = director_counts.get(movie.director, 0) + 1
                
                # Rating patterns
                if um.rating:
                    avg_rating.append(um.rating)
                
                # Era preferences
                if movie.year:
                    avg_year.append(movie.year)
        
        profile = {
            "genre_preferences": genre_counts,
            "director_preferences": director_counts,
            "avg_rating": np.mean(avg_rating) if avg_rating else 3.5,
            "preferred_era": np.mean(avg_year) if avg_year else 2000,
            "total_watched": len(user_movies_data)
        }
        
        # Save to user record
        self.user.taste_profile = profile
        self.db.commit()
        
        return profile
    
    def get_recommendations(self, selected_tags: List[int], 
                           filters: Dict = None, 
                           limit: int = 20) -> List[Dict]:
        """Generate movie recommendations based on tags and user profile"""
        
        # Get user profile
        if not self.user.taste_profile:
            self.build_user_profile()
        
        profile = self.user.taste_profile or {}
        
        # Get watched movie IDs to exclude
        watched_ids = self.db.execute(
            user_movies.select().where(
                and_(
                    user_movies.c.user_id == self.user_id,
                    user_movies.c.watched == True
                )
            )
        ).fetchall()
        watched_movie_ids = [w.movie_id for w in watched_ids]
        
        # Build query for candidate movies
        query = self.db.query(Movie).filter(~Movie.id.in_(watched_movie_ids))
        
        # Apply filters
        if filters:
            if filters.get('min_year'):
                query = query.filter(Movie.year >= filters['min_year'])
            if filters.get('max_year'):
                query = query.filter(Movie.year <= filters['max_year'])
            if filters.get('max_runtime'):
                query = query.filter(Movie.runtime <= filters['max_runtime'])
            if filters.get('min_rating'):
                query = query.filter(Movie.vote_average >= filters['min_rating'])
            if filters.get('language'):
                query = query.filter(Movie.original_language == filters['language'])
        
        # Get candidate movies
        candidates = query.all()
        
        # Score each candidate
        scored_movies = []
        for movie in candidates:
            score, reasons = self._calculate_movie_score(movie, selected_tags, profile)
            if score > 0:
                scored_movies.append({
                    'movie': movie,
                    'score': score,
                    'reasons': reasons
                })
        
        # Sort by score and return top results
        scored_movies.sort(key=lambda x: x['score'], reverse=True)
        
        # Format results
        recommendations = []
        for item in scored_movies[:limit]:
            movie = item['movie']
            recommendations.append({
                'id': movie.id,
                'title': movie.title,
                'year': movie.year,
                'poster_path': movie.poster_path,
                'overview': movie.overview,
                'score': item['score'],
                'reasons': item['reasons'],
                'runtime': movie.runtime,
                'vote_average': movie.vote_average
            })
        
        return recommendations
    
    def _calculate_movie_score(self, movie: Movie, selected_tags: List[int], 
                              profile: Dict) -> Tuple[float, List[str]]:
        """Calculate recommendation score for a movie"""
        score = 0.0
        reasons = []
        
        # Tag matching score (highest weight)
        movie_tag_ids = [tag.id for tag in movie.tags]
        tag_overlap = len(set(selected_tags) & set(movie_tag_ids))
        if tag_overlap > 0:
            score += tag_overlap * 0.3
            tag_names = [tag.name for tag in movie.tags if tag.id in selected_tags]
            reasons.append(f"Matches your mood: {', '.join(tag_names)}")
        
        # Genre preference score
        if movie.genres and profile.get('genre_preferences'):
            genre_score = 0
            for genre in movie.genres:
                if genre in profile['genre_preferences']:
                    genre_score += profile['genre_preferences'][genre]
            if genre_score > 0:
                score += min(genre_score * 0.1, 0.2)
                reasons.append(f"Similar to genres you enjoy")
        
        # Director preference
        if movie.director and profile.get('director_preferences'):
            if movie.director in profile['director_preferences']:
                score += 0.2
                reasons.append(f"From director {movie.director}")
        
        # Rating compatibility
        if movie.vote_average and profile.get('avg_rating'):
            rating_diff = abs(movie.vote_average/2 - profile['avg_rating'])
            if rating_diff < 1:
                score += 0.1
        
        # Era preference
        if movie.year and profile.get('preferred_era'):
            year_diff = abs(movie.year - profile['preferred_era'])
            if year_diff < 10:
                score += 0.05
        
        # Popularity modifier (slight preference for known films)
        if movie.popularity:
            score += min(movie.popularity / 1000, 0.05)
        
        return score, reasons