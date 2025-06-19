from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base, User, Movie, user_movies
from engine import RecommendationEngine
from moods import get_all_tags, get_tags_by_category

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Lumiere API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    letterboxd_username: Optional[str] = None

class TagSelection(BaseModel):
    user_id: int
    tag_ids: List[int]
    filters: Optional[Dict] = None

class ImportResponse(BaseModel):
    success: bool
    watched_count: int
    ratings_count: int
    message: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Project Lumiere API"}

@app.post("/users/create", response_model=Dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user already exists
    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    db_user = User(
        username=user.username,
        email=user.email,
        letterboxd_username=user.letterboxd_username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "message": "User created successfully"
    }

@app.post("/import/letterboxd/{user_id}", response_model=ImportResponse)
async def import_letterboxd_data(user_id: int, file: UploadFile = File(...)):
    """Import Letterboxd data from ZIP file"""
    # Import here to avoid circular import
    from import_letterboxd import EnhancedLetterboxdImporter
    
    # Save uploaded file temporarily
    temp_path = f"temp_upload_{user_id}.zip"
    
    try:
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Import data
        importer = EnhancedLetterboxdImporter(user_id)
        results = importer.import_from_zip(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return ImportResponse(
            success=True,
            watched_count=results["watched"],
            ratings_count=results["ratings"],
            message="Import successful"
        )
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tags")
def get_tags(category: Optional[str] = None):
    """Get all available mood tags"""
    if category:
        return get_tags_by_category(category)
    return get_all_tags()

@app.post("/recommendations")
def get_recommendations(selection: TagSelection):
    """Get movie recommendations based on selected tags"""
    engine = RecommendationEngine(selection.user_id)
    recommendations = engine.get_recommendations(
        selected_tags=selection.tag_ids,
        filters=selection.filters
    )
    
    return {
        "user_id": selection.user_id,
        "selected_tags": selection.tag_ids,
        "recommendations": recommendations,
        "count": len(recommendations)
    }

@app.get("/users/{user_id}/profile")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user's taste profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    engine = RecommendationEngine(user_id)
    profile = engine.build_user_profile()
    
    return {
        "user_id": user_id,
        "profile": profile
    }

@app.get("/users/{user_id}/stats")
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get user statistics"""
    from sqlalchemy import func
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get watched count
    watched_count = db.query(user_movies).filter(
        user_movies.c.user_id == user_id
    ).count()
    
    # Get average rating
    result = db.execute(
        f"SELECT AVG(rating) FROM user_movies WHERE user_id = {user_id} AND rating IS NOT NULL"
    ).fetchone()
    avg_rating = result[0] if result and result[0] else None
    
    return {
        "user_id": user_id,
        "total_watched": watched_count,
        "average_rating": round(avg_rating, 2) if avg_rating else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)