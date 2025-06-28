from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main_api import router as main_router
from tag_recommendations_api import router as tag_router

# Create unified FastAPI app
app = FastAPI(
    title="Project Lumiere - Unified API",
    description="Combined API server with main endpoints and tag-based recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from both APIs
app.include_router(main_router)
app.include_router(tag_router) 