#!/usr/bin/env python3
"""
FastAPI endpoint for tag-based movie recommendations
Integrates the new TagBasedRecommender with the existing backend
"""

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
from datetime import datetime

# Import the tag-based recommender
from tag_based_recommender import TagBasedRecommender

def load_user_data():
    """Load user data from enhanced_movie_scores_detailed.json"""
    try:
        user_data_path = os.path.join(os.path.dirname(__file__), "enhanced_movie_scores_detailed.json")
        if os.path.exists(user_data_path):
            with open(user_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract user preferences and enriched movies
            user_preferences = data.get('user_preferences', {})
            enriched_movies = data.get('enriched_movies', {})
            
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
            
            print(f"📊 Loaded {len(user_movies)} movies from user data")
            print(f"🎭 User preferences: {len(user_preferences.get('preferred_actors', []))} actors, "
                  f"{len(user_preferences.get('preferred_directors', []))} directors, "
                  f"{len(user_preferences.get('preferred_keywords', []))} keywords")
            
            return user_movies, user_preferences
        else:
            print("⚠️ enhanced_movie_scores_detailed.json not found")
            return [], {}
    except Exception as e:
        print(f"❌ Error loading user data: {e}")
        return [], {}

# Create router instead of FastAPI app
router = APIRouter(prefix="", tags=["tag-recommendations"])

# Pydantic models for request/response
class CalibrationSettings(BaseModel):
    era: int = 5
    runtime: int = 5
    popularity: int = 5
    familiarity: int = 5
    eraEnabled: bool = True
    runtimeEnabled: bool = True
    popularityEnabled: bool = True
    familiarityEnabled: bool = True

class TagRecommendationRequest(BaseModel):
    user_tags: List[str]
    calibration_settings: CalibrationSettings
    user_movies: Optional[List[Dict]] = None
    max_recommendations: int = 20

class MovieRecommendation(BaseModel):
    tmdb_id: int
    title: str
    overview: str
    release_date: str
    poster_path: Optional[str]
    backdrop_path: Optional[str]
    vote_average: float
    vote_count: int
    runtime: int
    genres: List[str]
    final_score: float
    similarity_score: float
    familiarity_score: float
    source_tags: List[str]
    credits: Optional[Dict] = None

class TagRecommendationResponse(BaseModel):
    recommendations: List[MovieRecommendation]
    total_found: int
    processing_time: float
    user_profile_summary: Dict

# Global recommender instance
recommender = None

def get_recommender() -> TagBasedRecommender:
    """Get or create the tag-based recommender instance"""
    global recommender
    
    if recommender is None:
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="TMDB API key not configured"
            )
        
        recommender = TagBasedRecommender(api_key)
    
    return recommender

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tag-recommendations-api",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/recommendations/tag-based", response_model=TagRecommendationResponse)
async def get_tag_based_recommendations(request: TagRecommendationRequest):
    """
    Get movie recommendations based on user-selected tags and calibration settings
    
    This endpoint implements the complete algorithm:
    1. Makes TMDB API calls for each selected tag with user filters
    2. Gets similar movies for user's top 40 movies
    3. Rates movies based on familiarity (cast/crew/keywords from user profile)
    4. Filters based on user's familiarity preference from calibration
    5. Ranks movies based on similarity to user's preferred keywords
    """
    start_time = datetime.now()
    
    try:
        # Get recommender instance
        recommender = get_recommender()
        
        # Validate input
        if not request.user_tags:
            raise HTTPException(
                status_code=400,
                detail="At least one tag must be provided"
            )
        
        if len(request.user_tags) > 25:
            raise HTTPException(
                status_code=400,
                detail="Maximum 25 tags allowed"
            )
        
        # Convert calibration settings to dict
        calibration_dict = request.calibration_settings.dict()
        
        # Load user data from enhanced_movie_scores_detailed.json
        user_movies, user_preferences = load_user_data()
        
        # Use provided user_movies if available, otherwise use loaded data
        final_user_movies = request.user_movies if request.user_movies else user_movies
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            user_tags=request.user_tags,
            calibration_settings=calibration_dict,
            user_movies=final_user_movies,
            max_recommendations=request.max_recommendations
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Build user profile summary
        user_profile_summary = {
            "tags_selected": len(request.user_tags),
            "tags": request.user_tags,
            "calibration_settings": calibration_dict,
            "movies_analyzed": len(final_user_movies),
            "recommendations_found": len(recommendations),
            "user_data_loaded": len(user_movies) > 0,
            "user_preferences": {
                "actors": len(user_preferences.get('preferred_actors', [])),
                "directors": len(user_preferences.get('preferred_directors', [])),
                "keywords": len(user_preferences.get('preferred_keywords', [])),
                "genres": len(user_preferences.get('preferred_genres', []))
            }
        }
        
        # Convert recommendations to response format
        response_recommendations = []
        for movie in recommendations:
            response_recommendations.append(MovieRecommendation(
                tmdb_id=movie.get('tmdb_id', 0),
                title=movie.get('title', 'Unknown'),
                overview=movie.get('overview', ''),
                release_date=movie.get('release_date', ''),
                poster_path=movie.get('poster_path'),
                backdrop_path=movie.get('backdrop_path'),
                vote_average=movie.get('vote_average', 0.0),
                vote_count=movie.get('vote_count', 0),
                runtime=movie.get('runtime', 0),
                genres=movie.get('genres', []),
                final_score=movie.get('final_score', 0.0),
                similarity_score=movie.get('similarity_score', 0.0),
                familiarity_score=movie.get('familiarity_score', 0.0),
                source_tags=movie.get('source_tags', []),
                credits=movie.get('credits')
            ))
        
        return TagRecommendationResponse(
            recommendations=response_recommendations,
            total_found=len(response_recommendations),
            processing_time=processing_time,
            user_profile_summary=user_profile_summary
        )
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.get("/tags/available")
async def get_available_tags():
    """Get list of available tags that can be used for recommendations"""
    available_tags = [
        "feel-good", "thought-provoking", "inspiring", "relaxing", "exciting",
        "romantic", "funny", "sad", "thrilling", "mysterious",
        "action", "comedy", "drama", "horror", "sci-fi",
        "romance", "thriller", "documentary", "animation", "family"
    ]
    
    return {
        "tags": available_tags,
        "total_tags": len(available_tags),
        "description": "Available tags for tag-based recommendations"
    }

@router.get("/keywords/status")
async def get_keywords_status():
    """Check the status of the keywords database"""
    try:
        recommender = get_recommender()
        keywords_file = os.path.join("tmdb_cache", "tmdb_keywords.json")
        
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r') as f:
                keywords_data = json.load(f)
            
            return {
                "status": "available",
                "total_keywords": len(keywords_data),
                "file_size": os.path.getsize(keywords_file),
                "last_updated": datetime.fromtimestamp(
                    os.path.getmtime(keywords_file)
                ).isoformat()
            }
        else:
            return {
                "status": "not_found",
                "message": "Keywords database not found. Use /keywords/generate to create it."
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking keywords status: {str(e)}"
        }

@router.post("/keywords/generate")
async def generate_keywords_database():
    """Generate the keywords database from TMDB"""
    try:
        recommender = get_recommender()
        print("🔧 Generating keywords database...")
        
        recommender.generate_keywords_database()
        
        return {
            "status": "success",
            "message": "Keywords database generated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate keywords database: {str(e)}"
        )

@router.get("/keywords/search")
async def search_keywords(q: str = Query(..., min_length=1), limit: int = 20):
    """Search for keywords by name"""
    try:
        recommender = get_recommender()
        
        # Search in the keywords database
        matching_keywords = []
        search_term = q.lower()
        
        for keyword_name, keyword_id in recommender.keywords_db.items():
            if search_term in keyword_name.lower():
                matching_keywords.append({
                    "name": keyword_name,
                    "id": keyword_id
                })
                if len(matching_keywords) >= limit:
                    break
        
        return {
            "query": q,
            "results": matching_keywords,
            "total_found": len(matching_keywords)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search keywords: {str(e)}"
        )

@router.get("/example")
async def get_example_recommendations():
    """Get example tag-based recommendations for testing"""
    example_request = TagRecommendationRequest(
        user_tags=["feel-good", "comedy"],
        calibration_settings=CalibrationSettings(
            era=7,
            runtime=6,
            popularity=5,
            familiarity=4,
            eraEnabled=True,
            runtimeEnabled=True,
            popularityEnabled=True,
            familiarityEnabled=True
        ),
        max_recommendations=5
    )
    
    return await get_tag_based_recommendations(example_request)

# For backward compatibility, create a FastAPI app instance
app = FastAPI(title="Tag-Based Movie Recommendations API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        "tag_recommendations_api:app",
        host="0.0.0.0",
        port=8001,  # Different port from main backend
        reload=True
    ) 