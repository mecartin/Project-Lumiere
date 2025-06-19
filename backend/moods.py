from typing import List, Dict
from pydantic import BaseModel

class MoodTag(BaseModel):
    id: int
    name: str
    category: str
    emoji: str
    color: str
    related_keywords: List[str] = []

# Curated mood tags
MOOD_TAGS = [
    # Emotions
    {"id": 1, "name": "melancholic", "category": "emotion", "emoji": "🌧️", "color": "#4A5568", 
     "related_keywords": ["sad", "lonely", "introspective", "bittersweet"]},
    {"id": 2, "name": "euphoric", "category": "emotion", "emoji": "✨", "color": "#F6E05E",
     "related_keywords": ["happy", "joyful", "uplifting", "feel-good"]},
    {"id": 3, "name": "anxious", "category": "emotion", "emoji": "😰", "color": "#E53E3E",
     "related_keywords": ["tense", "nervous", "thriller", "suspense"]},
    {"id": 4, "name": "nostalgic", "category": "emotion", "emoji": "📼", "color": "#ED8936",
     "related_keywords": ["retro", "memory", "childhood", "past"]},
    
    # Aesthetics
    {"id": 10, "name": "neon-noir", "category": "aesthetic", "emoji": "🌃", "color": "#9F7AEA",
     "related_keywords": ["cyberpunk", "urban", "night", "neo-noir"]},
    {"id": 11, "name": "cottagecore", "category": "aesthetic", "emoji": "🌻", "color": "#48BB78",
     "related_keywords": ["rural", "pastoral", "cozy", "nature"]},
    {"id": 12, "name": "minimalist", "category": "aesthetic", "emoji": "⬜", "color": "#E2E8F0",
     "related_keywords": ["simple", "clean", "sparse", "quiet"]},
    
    # Themes
    {"id": 20, "name": "coming-of-age", "category": "theme", "emoji": "🌱", "color": "#4FD1C5",
     "related_keywords": ["youth", "growing up", "teenager", "adolescence"]},
    {"id": 21, "name": "forbidden-love", "category": "theme", "emoji": "💔", "color": "#F56565",
     "related_keywords": ["romance", "tragic", "star-crossed", "impossible"]},
    {"id": 22, "name": "anti-establishment", "category": "theme", "emoji": "✊", "color": "#2D3748",
     "related_keywords": ["rebellion", "anarchist", "revolution", "protest"]},
    
    # Vibes
    {"id": 30, "name": "slow-burn", "category": "vibe", "emoji": "🕯️", "color": "#718096",
     "related_keywords": ["patient", "deliberate", "atmospheric", "meditative"]},
    {"id": 31, "name": "fever-dream", "category": "vibe", "emoji": "🌀", "color": "#B794F4",
     "related_keywords": ["surreal", "psychedelic", "dreamlike", "bizarre"]},
    {"id": 32, "name": "cozy-night-in", "category": "vibe", "emoji": "🛋️", "color": "#F7FAFC",
     "related_keywords": ["comfort", "warm", "relaxing", "easy-watch"]},
]

def get_all_tags() -> List[Dict]:
    return MOOD_TAGS

def get_tag_by_id(tag_id: int) -> Dict:
    return next((tag for tag in MOOD_TAGS if tag["id"] == tag_id), None)

def get_tags_by_category(category: str) -> List[Dict]:
    return [tag for tag in MOOD_TAGS if tag["category"] == category]