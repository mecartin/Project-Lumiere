#!/usr/bin/env python3
"""
Main API server for Project Lumiere
Handles basic endpoints that the frontend expects
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
from datetime import datetime

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

# In-memory storage (in production, use a database)
users_db = {}
user_profiles = {}
user_stats = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "project-lumiere-main-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/users/create")
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

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user data"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "data": users_db[user_id]
    }

@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile"""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return user_profiles[user_id]

@app.get("/users/{user_id}/stats")
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

@app.post("/import/letterboxd/{user_id}")
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

@app.post("/recommendations")
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

@app.get("/recommendations/discovery")
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
            "title": "Spirited Away",
            "year": "2001",
            "director": "Hayao Miyazaki",
            "cast": ["Rumi Hiiragi", "Miyu Irino"],
            "runtime": "125 mins",
            "genres": ["Animation", "Fantasy"],
            "rating": "8.6/10",
            "synopsis": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits.",
            "streaming": "HBO MAX",
            "poster": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
            "score": 0.89
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

@app.get("/tags")
async def get_tags(category: Optional[str] = None):
    """Get available tags"""
    tags = [
        {"id": 1, "name": "feel-good", "category": "mood"},
        {"id": 2, "name": "thought-provoking", "category": "mood"},
        {"id": 3, "name": "inspiring", "category": "mood"},
        {"id": 4, "name": "relaxing", "category": "mood"},
        {"id": 5, "name": "exciting", "category": "mood"},
        {"id": 6, "name": "romantic", "category": "mood"},
        {"id": 7, "name": "funny", "category": "mood"},
        {"id": 8, "name": "sad", "category": "mood"},
        {"id": 9, "name": "thrilling", "category": "mood"},
        {"id": 10, "name": "mysterious", "category": "mood"},
        {"id": 11, "name": "action", "category": "genre"},
        {"id": 12, "name": "comedy", "category": "genre"},
        {"id": 13, "name": "drama", "category": "genre"},
        {"id": 14, "name": "horror", "category": "genre"},
        {"id": 15, "name": "sci-fi", "category": "genre"},
        {"id": 16, "name": "romance", "category": "genre"},
        {"id": 17, "name": "thriller", "category": "genre"},
        {"id": 18, "name": "documentary", "category": "genre"},
        {"id": 19, "name": "animation", "category": "genre"},
        {"id": 20, "name": "family", "category": "genre"}
    ]
    
    if category:
        tags = [tag for tag in tags if tag["category"] == category]
    
    return {
        "tags": tags,
        "total_tags": len(tags),
        "category": category
    }

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