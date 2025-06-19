from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Table, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./project_lumiere.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association tables
user_movies = Table('user_movies', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('watched', Boolean, default=False),
    Column('rating', Float, nullable=True),
    Column('watched_date', DateTime, nullable=True)
)

movie_tags = Table('movie_tags', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('tag_id', Integer, ForeignKey('mood_tags.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    letterboxd_username = Column(String, nullable=True)
    taste_profile = Column(JSON, nullable=True)  # Stores computed taste vector
    created_at = Column(DateTime, default=datetime.utcnow)
    
    movies = relationship("Movie", secondary=user_movies, back_populates="users")

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String, index=True)
    year = Column(Integer)
    genres = Column(JSON)
    overview = Column(String)
    poster_path = Column(String)
    runtime = Column(Integer)
    vote_average = Column(Float)
    popularity = Column(Float)
    original_language = Column(String)
    director = Column(String, nullable=True)
    
    users = relationship("User", secondary=user_movies, back_populates="movies")
    tags = relationship("MoodTag", secondary=movie_tags, back_populates="movies")

class MoodTag(Base):
    __tablename__ = "mood_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)  # emotion, aesthetic, theme, etc.
    emoji = Column(String, nullable=True)
    color = Column(String, nullable=True)  # For UI theming
    
    movies = relationship("Movie", secondary=movie_tags, back_populates="tags")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    tags_used = Column(JSON)  # Which tags triggered this rec
    score = Column(Float)
    reason = Column(String)  # Human-readable explanation
    created_at = Column(DateTime, default=datetime.utcnow)
    
Base.metadata.create_all(bind=engine)