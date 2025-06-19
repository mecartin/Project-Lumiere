import pandas as pd
from database import SessionLocal, Movie, Base, engine
from tag_mapper import TagMapper
import json

def import_movie_data():
    """Import movie data from CSV"""
    db = SessionLocal()
    df = pd.read_csv('movie_data.csv')
    
    # Clean and import movies
    for _, row in df.iterrows():
        if pd.notna(row['tmdb_id']) and row['tmdb_id'] > 0:
            # Parse genres
            genres = []
            if pd.notna(row['genres']):
                try:
                    genres = json.loads(row['genres'].replace("'", '"'))
                except:
                    genres = []
            
            movie = Movie(
                tmdb_id=int(row['tmdb_id']),
                title=row['movie_title'],
                year=int(row['year_released']) if pd.notna(row['year_released']) else None,
                genres=genres,
                overview=row['overview'] if pd.notna(row['overview']) else "",
                poster_path=f"https://letterboxd.com/{row['image_url']}" if pd.notna(row['image_url']) else None,
                runtime=int(row['runtime']) if pd.notna(row['runtime']) and row['runtime'] > 0 else None,
                vote_average=float(row['vote_average']) if pd.notna(row['vote_average']) else 0,
                popularity=float(row['popularity']) if pd.notna(row['popularity']) else 0,
                original_language=row['original_language'] if pd.notna(row['original_language']) else 'en'
            )
            
            db.add(movie)
    
    db.commit()
    print(f"Imported {len(df)} movies")
    
    # Map tags to movies
    mapper = TagMapper()
    movies = db.query(Movie).all()
    
    for i, movie in enumerate(movies):
        mapper.update_movie_tags(movie.id)
        if i % 100 == 0:
            print(f"Tagged {i} movies...")
    
    print("Database build complete!")

if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Import data
    import_movie_data()