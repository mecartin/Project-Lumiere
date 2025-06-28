#!/usr/bin/env python3
"""
Main API server for Project Lumiere
Handles basic endpoints that the frontend expects
"""

from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
import shutil
import uuid
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

# Import processing modules
from userdata import merge_letterboxd_data_from_zip
from ranker import rank_movies_by_intuitive_taste, get_favorite_films_from_zip
from enricher import MovieTasteEnricher

# Create router instead of FastAPI app
router = APIRouter(prefix="", tags=["main"])

# Global processing status
processing_status = {}
processing_lock = threading.Lock()

# Data models
class UserData(BaseModel):
    username: str
    email: Optional[str] = None
    preferences: Optional[Dict] = None

class UserProfile(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None
    preferences: Optional[Dict] = None
    created_at: str
    last_login: str

class UserStats(BaseModel):
    user_id: str
    total_movies: int
    total_lists: int
    favorite_genres: List[str]
    average_rating: float

class RecommendationRequest(BaseModel):
    user_id: str
    tag_ids: Optional[List[int]] = None
    filters: Optional[Dict] = None
    count: int = 20

class DiscoveryRequest(BaseModel):
    genre: Optional[str] = None
    decade: Optional[str] = None
    count: int = 20

class ProcessingStatus(BaseModel):
    status: str  # "processing", "completed", "error"
    progress: int  # 0-100
    current_step: str
    message: str
    result: Optional[Dict] = None

# In-memory storage (in production, use a database)
users_db = {}
user_profiles = {}
user_stats = {}

def update_processing_status(session_id: str, status: str, progress: int, current_step: str, message: str, result: Optional[Dict] = None):
    """Update processing status for a session"""
    with processing_lock:
        processing_status[session_id] = {
            "status": status,
            "progress": progress,
            "current_step": current_step,
            "message": message,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

def process_letterboxd_zip(zip_path: str, session_id: str):
    """Process Letterboxd zip file with progress tracking"""
    print(f"\n=== Starting Letterboxd Processing Session: {session_id} ===")
    print(f"Processing file: {zip_path}")
    
    try:
        # Step 1: Extract and merge data (25%)
        print("\n📁 Step 1: Extracting and merging Letterboxd data...")
        update_processing_status(session_id, "processing", 0, "Extracting data", "Reading Letterboxd export files...")
        
        merged_data = merge_letterboxd_data_from_zip(zip_path)
        if merged_data is None:
            print("❌ Failed to extract data from zip file")
            update_processing_status(session_id, "error", 0, "Error", "Failed to extract data from zip file")
            return
        
        # Save merged data
        merged_csv_path = f"temp_merged_{session_id}.csv"
        merged_data.to_csv(merged_csv_path, index=False)
        
        print(f"✅ Successfully processed {len(merged_data)} movies")
        update_processing_status(session_id, "processing", 25, "Data extracted", f"Successfully processed {len(merged_data)} movies")
        
        # Step 2: Rank movies (50%)
        print("\n🎯 Step 2: Ranking movies by user taste...")
        update_processing_status(session_id, "processing", 25, "Ranking movies", "Analyzing your movie preferences...")
        
        favorite_urls = get_favorite_films_from_zip(zip_path)
        print(f"📋 Found {len(favorite_urls)} favorite films")
        
        ranked_data = rank_movies_by_intuitive_taste(merged_csv_path, favorite_urls)
        
        if ranked_data is None:
            print("❌ Failed to rank movies")
            update_processing_status(session_id, "error", 25, "Error", "Failed to rank movies")
            return
        
        # Save ranked data
        ranked_csv_path = f"temp_ranked_{session_id}.csv"
        ranked_data.to_csv(ranked_csv_path, index=False)
        
        print(f"✅ Successfully ranked {len(ranked_data)} movies")
        update_processing_status(session_id, "processing", 50, "Movies ranked", f"Ranked {len(ranked_data)} movies by your taste")
        
        # Step 3: Enrich with TMDB data (75%)
        print("\n🔍 Step 3: Enriching data with TMDB information...")
        update_processing_status(session_id, "processing", 50, "Enriching data", "Fetching additional movie details...")
        
        # Initialize enricher (you'll need to set up TMDB API key)
        tmdb_api_key = os.getenv("TMDB_API_KEY", "your_tmdb_api_key_here")
        if tmdb_api_key == "your_tmdb_api_key_here":
            print("⚠️  Warning: TMDB API key not set. Skipping enrichment step.")
            enriched_data = ranked_data.head(60)  # Use ranked data as fallback
        else:
            enricher = MovieTasteEnricher(tmdb_api_key)
            
            # Test API connection
            if not enricher.test_api_connection():
                print("⚠️  Warning: TMDB API connection failed. Skipping enrichment step.")
                enriched_data = ranked_data.head(60)  # Use ranked data as fallback
            else:
                # Process top movies for enrichment
                top_movies = ranked_data.head(60)  # Process top 60 movies
                enriched_data = enricher.process_movies(ranked_csv_path, f"temp_enriched_{session_id}.csv", top_n=60)
        
        print(f"✅ Successfully enriched {len(enriched_data)} movies")
        update_processing_status(session_id, "processing", 75, "Data enriched", "Enhanced movie data with additional details")
        
        # Step 4: Finalize and clean up (100%)
        print("\n🧹 Step 4: Finalizing and cleaning up...")
        update_processing_status(session_id, "processing", 75, "Finalizing", "Preparing your personalized recommendations...")
        
        # Clean up temporary files
        for temp_file in [merged_csv_path, ranked_csv_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"🗑️  Cleaned up: {temp_file}")
        
        # Prepare result
        result = {
            "total_movies": len(merged_data),
            "ranked_movies": len(ranked_data),
            "enriched_movies": len(enriched_data),
            "favorite_films": len(favorite_urls),
            "processing_time": datetime.now().isoformat(),
            "enriched_csv_path": f"temp_enriched_{session_id}.csv"
        }
        
        print(f"\n🎉 Processing completed successfully!")
        print(f"📊 Results:")
        print(f"   - Total movies: {result['total_movies']}")
        print(f"   - Ranked movies: {result['ranked_movies']}")
        print(f"   - Enriched movies: {result['enriched_movies']}")
        print(f"   - Favorite films: {result['favorite_films']}")
        print(f"   - Output file: {result['enriched_csv_path']}")
        
        update_processing_status(session_id, "completed", 100, "Completed", "Your movie data has been processed successfully!", result)
        
    except Exception as e:
        print(f"\n❌ Processing failed with error: {str(e)}")
        update_processing_status(session_id, "error", 0, "Error", f"Processing failed: {str(e)}")

@router.post("/process-letterboxd")
async def process_letterboxd_file(file: UploadFile = File(...)):
    """Process uploaded Letterboxd zip file"""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP file")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save uploaded file
    zip_path = f"temp_upload_{session_id}.zip"
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Initialize processing status
    update_processing_status(session_id, "processing", 0, "Starting", "Upload received, beginning processing...")
    
    # Start processing in background thread
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(process_letterboxd_zip, zip_path, session_id)
    
    return {
        "session_id": session_id,
        "message": "Processing started",
        "status_endpoint": f"/processing-status/{session_id}"
    }

@router.get("/processing-status/{session_id}")
async def get_processing_status(session_id: str):
    """Get processing status for a session"""
    with processing_lock:
        if session_id not in processing_status:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return processing_status[session_id]

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "project-lumiere-main-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.post("/users/create")
async def create_user(user_data: UserData):
    """Create a new user"""
    user_id = f"user_{len(users_db) + 1}"
    
    user_profile = UserProfile(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        preferences=user_data.preferences or {},
        created_at=datetime.now().isoformat(),
        last_login=datetime.now().isoformat()
    )
    
    users_db[user_id] = user_data.dict()
    user_profiles[user_id] = user_profile.dict()
    
    return {
        "user_id": user_id,
        "message": "User created successfully",
        "profile": user_profile.dict()
    }

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user data"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "data": users_db[user_id]
    }

@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile"""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return user_profiles[user_id]

@router.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate mock stats
    stats = UserStats(
        user_id=user_id,
        total_movies=150,
        total_lists=5,
        favorite_genres=["Drama", "Comedy", "Sci-Fi"],
        average_rating=7.5
    )
    
    return stats.dict()

@router.post("/import/letterboxd/{user_id}")
async def import_letterboxd_data(user_id: str, file: bytes):
    """Import Letterboxd data for a user"""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mock import processing
    return {
        "user_id": user_id,
        "message": "Letterboxd data imported successfully",
        "movies_imported": 150,
        "lists_imported": 5,
        "processing_time": 2.5
    }

@router.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Get movie recommendations"""
    # Mock recommendations
    recommendations = [
        {
            "id": 1,
            "title": "Inception",
            "year": "2010",
            "director": "Christopher Nolan",
            "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            "runtime": "148 mins",
            "genres": ["Sci-Fi", "Thriller"],
            "rating": "8.8/10",
            "synopsis": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
            "streaming": "HBO MAX",
            "poster": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
            "score": 0.95
        },
        {
            "id": 2,
            "title": "Parasite",
            "year": "2019",
            "director": "Bong Joon Ho",
            "cast": ["Song Kang-ho", "Lee Sun-kyun"],
            "runtime": "132 mins",
            "genres": ["Thriller", "Comedy", "Drama"],
            "rating": "8.6/10",
            "synopsis": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
            "streaming": "HULU",
            "poster": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
            "score": 0.92
        }
    ]
    
    return {
        "recommendations": recommendations[:request.count],
        "total_found": len(recommendations),
        "user_id": request.user_id
    }

@router.get("/recommendations/discovery")
async def get_discovery_recommendations(
    genre: Optional[str] = None,
    decade: Optional[str] = None,
    count: int = 20
):
    """Get discovery recommendations"""
    # Mock discovery recommendations
    recommendations = [
        {
            "id": 3,
            "title": "The Shawshank Redemption",
            "year": "1994",
            "director": "Frank Darabont",
            "cast": ["Tim Robbins", "Morgan Freeman"],
            "runtime": "142 mins",
            "genres": ["Drama"],
            "rating": "9.3/10",
            "synopsis": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "streaming": "Netflix",
            "poster": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
            "score": 0.98
        }
    ]
    
    return {
        "recommendations": recommendations[:count],
        "total_found": len(recommendations),
        "filters": {
            "genre": genre,
            "decade": decade
        }
    }

@router.get("/tags")
async def get_tags(category: Optional[str] = None):
    """Get available tags"""
    all_tags = {
        "emotion": [
            {"id": 1, "name": "feel-good", "description": "Uplifting and positive"},
            {"id": 2, "name": "thought-provoking", "description": "Makes you think"},
            {"id": 3, "name": "inspiring", "description": "Motivational and uplifting"},
            {"id": 4, "name": "relaxing", "description": "Calm and peaceful"},
            {"id": 5, "name": "exciting", "description": "Thrilling and action-packed"}
        ],
        "genre": [
            {"id": 6, "name": "action", "description": "High-energy action films"},
            {"id": 7, "name": "comedy", "description": "Funny and humorous"},
            {"id": 8, "name": "drama", "description": "Serious and emotional"},
            {"id": 9, "name": "horror", "description": "Scary and suspenseful"},
            {"id": 10, "name": "sci-fi", "description": "Science fiction and futuristic"}
        ],
        "mood": [
            {"id": 11, "name": "romantic", "description": "Love and relationships"},
            {"id": 12, "name": "funny", "description": "Humor and comedy"},
            {"id": 13, "name": "sad", "description": "Emotional and melancholic"},
            {"id": 14, "name": "thrilling", "description": "Suspense and excitement"},
            {"id": 15, "name": "mysterious", "description": "Mystery and intrigue"}
        ]
    }
    
    if category:
        return all_tags.get(category, [])
    
    return all_tags

# For backward compatibility, create a FastAPI app instance
app = FastAPI(
    title="Project Lumiere Main API",
    description="Main API server for Project Lumiere frontend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Project Lumiere Main API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 