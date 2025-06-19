# Re-export models from database for easier imports
from database import User, Movie, MoodTag, Recommendation, user_movies, movie_tags

__all__ = ['User', 'Movie', 'MoodTag', 'Recommendation', 'user_movies', 'movie_tags']