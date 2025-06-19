from typing import List, Dict
import re
from database import SessionLocal, Movie, MoodTag, movie_tags
from moods import MOOD_TAGS

class TagMapper:
    def __init__(self):
        self.db = SessionLocal()
        self._init_tags()
    
    def _init_tags(self):
        """Initialize mood tags in database"""
        for tag_data in MOOD_TAGS:
            existing = self.db.query(MoodTag).filter(MoodTag.name == tag_data["name"]).first()
            if not existing:
                tag = MoodTag(
                    id=tag_data["id"],
                    name=tag_data["name"],
                    category=tag_data["category"],
                    emoji=tag_data["emoji"],
                    color=tag_data["color"]
                )
                self.db.add(tag)
        self.db.commit()
    
    def map_movie_to_tags(self, movie: Movie) -> List[int]:
        """Map a movie to relevant mood tags based on its attributes"""
        mapped_tag_ids = []
        
        # Keywords to check in overview and genres
        text_to_analyze = f"{movie.overview or ''} {' '.join(movie.genres or [])}".lower()
        
        for tag_data in MOOD_TAGS:
            # Check if any related keywords match
            for keyword in tag_data.get("related_keywords", []):
                if keyword.lower() in text_to_analyze:
                    mapped_tag_ids.append(tag_data["id"])
                    break
            
            # Special mapping rules
            if tag_data["name"] == "coming-of-age" and movie.genres:
                if "Drama" in movie.genres and any(word in text_to_analyze for word in ["teenage", "youth", "school", "growing"]):
                    mapped_tag_ids.append(tag_data["id"])
            
            if tag_data["name"] == "slow-burn" and movie.runtime:
                if movie.runtime > 140 and "Drama" in (movie.genres or []):
                    mapped_tag_ids.append(tag_data["id"])
            
            if tag_data["name"] == "neon-noir" and movie.genres:
                if any(genre in movie.genres for genre in ["Crime", "Thriller"]) and movie.year and movie.year > 1980:
                    if any(word in text_to_analyze for word in ["city", "night", "detective", "noir"]):
                        mapped_tag_ids.append(tag_data["id"])
        
        return list(set(mapped_tag_ids))
    
    def update_movie_tags(self, movie_id: int):
        """Update tags for a specific movie"""
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return
        
        # Get mapped tags
        tag_ids = self.map_movie_to_tags(movie)
        
        # Clear existing tags
        self.db.execute(movie_tags.delete().where(movie_tags.c.movie_id == movie_id))
        
        # Add new tags
        for tag_id in tag_ids:
            self.db.execute(movie_tags.insert().values(movie_id=movie_id, tag_id=tag_id))
        
        self.db.commit()