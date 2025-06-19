import pandas as pd
import zipfile
from datetime import datetime
from typing import Dict, List
import os
import re
from database import SessionLocal, User, Movie, user_movies
from sqlalchemy.orm import Session
import httpx
from dotenv import load_dotenv

load_dotenv()

class EnhancedLetterboxdImporter:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db = SessionLocal()
        self.tmdb_api_key = os.getenv("TMDB_API_KEY")
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        
    def import_from_zip(self, zip_path: str) -> Dict:
        """Import complete Letterboxd data"""
        results = {
            "watched": 0,
            "ratings": 0,
            "diary": 0,
            "watchlist": 0,
            "lists": 0,
            "errors": []
        }
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                temp_dir = f"temp_import_{self.user_id}"
                zip_ref.extractall(temp_dir)
                
                # Import watched films
                if os.path.exists(f"{temp_dir}/watched.csv"):
                    watched_df = pd.read_csv(f"{temp_dir}/watched.csv")
                    results["watched"] = self._import_watched(watched_df)
                
                # Import ratings
                if os.path.exists(f"{temp_dir}/ratings.csv"):
                    ratings_df = pd.read_csv(f"{temp_dir}/ratings.csv")
                    results["ratings"] = self._import_ratings(ratings_df)
                
                # Import diary with reviews
                if os.path.exists(f"{temp_dir}/diary.csv"):
                    diary_df = pd.read_csv(f"{temp_dir}/diary.csv")
                    results["diary"] = self._import_diary(diary_df)
                
                # Import watchlist
                if os.path.exists(f"{temp_dir}/watchlist.csv"):
                    watchlist_df = pd.read_csv(f"{temp_dir}/watchlist.csv")
                    results["watchlist"] = self._import_watchlist(watchlist_df)
                
                # Import lists for additional context
                results["lists"] = self._import_lists(temp_dir)
                
                # Clean up
                import shutil
                shutil.rmtree(temp_dir)
                
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    def _search_tmdb_movie(self, title: str, year: int = None) -> Dict:
        """Search for movie in TMDB"""
        if not self.tmdb_api_key:
            return None
            
        search_url = f"{self.tmdb_base_url}/search/movie"
        params = {
            "api_key": self.tmdb_api_key,
            "query": title,
            "year": year if year else ""
        }
        
        try:
            response = httpx.get(search_url, params=params)
            if response.status_code == 200:
                results = response.json()["results"]
                if results:
                    return results[0]  # Return first match
        except:
            pass
        
        return None
    
    def _get_or_create_movie(self, title: str, year: int = None) -> Movie:
        """Get movie from DB or fetch from TMDB"""
        # Clean title
        title = title.strip()
        
        # First check if movie exists in DB
        query = self.db.query(Movie).filter(Movie.title == title)
        if year:
            query = query.filter(Movie.year == int(year))
        
        movie = query.first()
        if movie:
            return movie
        
        # Try to find in TMDB
        tmdb_data = self._search_tmdb_movie(title, year)
        if tmdb_data:
            movie = Movie(
                tmdb_id=tmdb_data["id"],
                title=tmdb_data["title"],
                year=int(tmdb_data["release_date"][:4]) if tmdb_data.get("release_date") else year,
                genres=self._get_genre_names(tmdb_data.get("genre_ids", [])),
                overview=tmdb_data.get("overview", ""),
                poster_path=f"https://image.tmdb.org/t/p/w500{tmdb_data['poster_path']}" if tmdb_data.get("poster_path") else None,
                vote_average=tmdb_data.get("vote_average", 0),
                popularity=tmdb_data.get("popularity", 0),
                original_language=tmdb_data.get("original_language", "en")
            )
            
            # Fetch additional details
            self._enrich_movie_details(movie, tmdb_data["id"])
        else:
            # Create basic entry if TMDB search fails
            movie = Movie(
                title=title,
                year=int(year) if year else None,
                tmdb_id=0
            )
        
        self.db.add(movie)
        self.db.commit()
        return movie
    
    def _enrich_movie_details(self, movie: Movie, tmdb_id: int):
        """Get additional movie details from TMDB"""
        detail_url = f"{self.tmdb_base_url}/movie/{tmdb_id}"
        params = {"api_key": self.tmdb_api_key, "append_to_response": "credits"}
        
        try:
            response = httpx.get(detail_url, params=params)
            if response.status_code == 200:
                data = response.json()
                movie.runtime = data.get("runtime", 0)
                
                # Get director
                if "credits" in data and "crew" in data["credits"]:
                    directors = [c["name"] for c in data["credits"]["crew"] if c["job"] == "Director"]
                    if directors:
                        movie.director = directors[0]
        except:
            pass
    
    def _get_genre_names(self, genre_ids: List[int]) -> List[str]:
        """Convert TMDB genre IDs to names"""
        genre_map = {
            28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
            80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
            14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
            9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
            10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
        }
        return [genre_map.get(gid, "") for gid in genre_ids if gid in genre_map]
    
    def _import_lists(self, temp_dir: str) -> int:
        """Import user lists to understand preferences"""
        lists_dir = f"{temp_dir}/lists"
        count = 0
        
        if not os.path.exists(lists_dir):
            return count
        
        # Look for specific preference lists
        preference_lists = ["top-25.csv", "my-taste-ig.csv", "favourite-films.csv"]
        
        for list_file in preference_lists:
            if os.path.exists(f"{lists_dir}/{list_file}"):
                try:
                    # Read the Letterboxd list format
                    with open(f"{lists_dir}/{list_file}", 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Parse list entries (skip metadata lines)
                    in_entries = False
                    for line in lines:
                        if "Position,Name,Year" in line:
                            in_entries = True
                            continue
                        if in_entries and line.strip():
                            parts = line.strip().split(',')
                            if len(parts) >= 3:
                                title = parts[1].strip('"')
                                year = parts[2].strip() if parts[2].strip() else None
                                
                                # Mark these as highly preferred
                                movie = self._get_or_create_movie(title, year)
                                if movie:
                                    # Could add to a preferences table
                                    count += 1
                except:
                    pass
        
        return count