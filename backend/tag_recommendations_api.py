#!/usr/bin/env python3
"""
FastAPI endpoint for tag-based movie recommendations
Integrates the new TagBasedRecommender with the existing backend
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
from datetime import datetime

# Import the tag-based recommender
from tag_based_recommender import TagBasedRecommender

# Initialize FastAPI app
app = FastAPI(title="Tag-Based Movie Recommendations API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CalibrationSettings(BaseModel):
    era: int = 5
    runtime: int = 5
    popularity: int = 5
    familiarity: int = 5

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

@app.on_event("startup")
async def startup_event():
    """Initialize the recommender on startup"""
    try:
        get_recommender()
        print("✅ Tag-based recommender initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize recommender: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tag-recommendations-api",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/recommendations/tag-based", response_model=TagRecommendationResponse)
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
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            user_tags=request.user_tags,
            calibration_settings=calibration_dict,
            user_movies=request.user_movies or [],
            max_recommendations=request.max_recommendations
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Build user profile summary
        user_profile_summary = {
            "tags_selected": len(request.user_tags),
            "tags": request.user_tags,
            "calibration_settings": calibration_dict,
            "movies_analyzed": len(request.user_movies or []),
            "recommendations_found": len(recommendations)
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
                source_tags=movie.get('source_tags', [])
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

@app.get("/tags/available")
async def get_available_tags():
    """Get list of available tags that can be used for recommendations"""
    available_tags = [
        "feel-good", "thought-provoking", "inspiring", "relaxing", "exciting",
        "romantic", "funny", "sad", "thrilling", "mysterious",
        "action", "comedy", "drama", "horror", "sci-fi",
        "romance", "thriller", "documentary", "animation", "family"
    ]
    
    return {
        "available_tags": available_tags,
        "total_tags": len(available_tags),
        "max_selection": 25
    }

@app.get("/keywords/status")
async def get_keywords_status():
    """Check the status of the TMDB keywords database"""
    try:
        recommender = get_recommender()
        
        keywords_file = os.path.join(recommender.cache_dir, "tmdb_keywords.json")
        tag_mapping_file = os.path.join(recommender.cache_dir, "tag_to_keyword_mapping.json")
        
        keywords_exists = os.path.exists(keywords_file)
        tag_mapping_exists = os.path.exists(tag_mapping_file)
        
        status = {
            "keywords_database_exists": keywords_exists,
            "tag_mapping_exists": tag_mapping_exists,
            "keywords_count": len(recommender.keywords_db) if keywords_exists else 0,
            "cache_directory": recommender.cache_dir
        }
        
        if keywords_exists:
            with open(keywords_file, 'r') as f:
                keywords_data = json.load(f)
                status["keywords_count"] = len(keywords_data)
        
        if tag_mapping_exists:
            with open(tag_mapping_file, 'r') as f:
                tag_mapping = json.load(f)
                status["mapped_tags_count"] = len(tag_mapping)
        
        return status
        
    except Exception as e:
        return {
            "error": str(e),
            "keywords_database_exists": False,
            "tag_mapping_exists": False
        }

@app.post("/keywords/generate")
async def generate_keywords_database():
    """Generate the TMDB keywords database (admin endpoint)"""
    try:
        recommender = get_recommender()
        
        # Generate keywords database
        keywords_db = recommender.generate_keywords_database()
        
        return {
            "success": True,
            "keywords_generated": len(keywords_db),
            "message": "Keywords database generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate keywords database: {str(e)}"
        )

@app.get("/keywords/search")
async def search_keywords(q: str = Query(..., min_length=1), limit: int = 20):
    """Search keywords by substring (case-insensitive)"""
    recommender = get_recommender()
    # Load keywords database (assume it's a dict: name.lower() -> id)
    keywords_db = recommender.keywords_db
    results = []
    q_lower = q.lower()
    for name, kid in keywords_db.items():
        if q_lower in name:
            results.append({"keyword": name, "id": kid})
            if len(results) >= limit:
                break
    return {"results": results}

# Example usage endpoint for testing
@app.get("/example")
async def get_example_recommendations():
    """Get example recommendations for testing"""
    example_request = TagRecommendationRequest(
        user_tags=["feel-good", "comedy"],
        calibration_settings=CalibrationSettings(
            era=7,
            runtime=6,
            popularity=5,
            familiarity=4
        ),
        max_recommendations=5
    )
    
    return await get_tag_based_recommendations(example_request)

if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        "tag_recommendations_api:app",
        host="0.0.0.0",
        port=8001,  # Different port from main backend
        reload=True
    ) 