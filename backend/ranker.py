import pandas as pd
import numpy as np
import os
import ast
import io
import glob
import zipfile
from datetime import datetime

def get_favorite_films_from_zip(zip_path):
    """
    Correctly parses profile.csv from a Letterboxd zip export to find the
    user's favorite films from the 'Favorite Films' column.

    Args:
        zip_path (str): The file path for the Letterboxd zip export.

    Returns:
        set: A set of Letterboxd URLs for the user's favorite films.
             Returns an empty set if the file is not found or is empty.
    """
    favorite_urls = set()
    if not zip_path or not os.path.exists(zip_path):
        print("Warning: Zip file not found. Cannot add 'Favorite Film' bonus.")
        return favorite_urls

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            all_files = zf.namelist()
            root_folder = ''
            if all_files and '/' in all_files[0]:
                root_folder = all_files[0].split('/')[0] + '/'
            
            profile_path = f'{root_folder}profile.csv'
            if profile_path not in all_files:
                print("Warning: profile.csv not found in zip. Cannot add 'Favorite Film' bonus.")
                return favorite_urls

            with zf.open(profile_path) as f:
                profile_df = pd.read_csv(io.TextIOWrapper(f, 'utf-8'))

            # Check if the 'Favorite Films' column exists
            if 'Favorite Films' in profile_df.columns:
                # The URLs are in a single cell, separated by commas.
                # Get the first row's value from that column.
                favorites_string = profile_df['Favorite Films'].iloc[0]
                
                # Ensure the value is a non-empty string before splitting
                if isinstance(favorites_string, str) and favorites_string.strip():
                    # Split the string by comma and strip any whitespace from each URL
                    urls = [url.strip() for url in favorites_string.split(',')]
                    favorite_urls.update(urls)
                    print(f"Found {len(favorite_urls)} favorite films in profile.csv.")
                else:
                    print("Warning: 'Favorite Films' column is empty in profile.csv.")
            else:
                print("Warning: 'Favorite Films' column not found in profile.csv.")


    except Exception as e:
        print(f"Warning: Could not process profile.csv. Favorite film bonus will not be applied. Error: {e}")
    
    return favorite_urls


def rank_movies_by_intuitive_taste(input_csv, favorite_film_urls):
    """
    Analyzes and ranks films from merged Letterboxd data using a nuanced,
    intuitive "taste score" model.

    This model incorporates:
    - Base scores for ratings, likes, rewatches, and list inclusions.
    - A "Favorite Film" bonus for films in the user's profile favorites.
    - A "Review Conviction" bonus that amplifies the rating's impact.
    - "Pantheon" and "Obsession" synergy bonuses for specific action combos.
    - Recency weighting to reflect taste evolution.
    - Normalization to a 0-100 scale for intuitive results.

    Args:
        input_csv (str): The path to the merged Letterboxd data CSV file.
        favorite_film_urls (set): A set of URLs for films marked as favorites.

    Returns:
        pandas.DataFrame: A new DataFrame with films ranked by the final taste score,
                          or None if the input file is not found.
    """
    # --- 1. Load and Prepare Data ---
    if not os.path.exists(input_csv):
        print(f"Error: Input file not found at '{input_csv}'")
        return None
    
    df = pd.read_csv(input_csv)
    print(f"Successfully loaded '{input_csv}' with {len(df)} entries.")

    try:
        df['dates_watched'] = df['dates_watched'].apply(ast.literal_eval)
    except (ValueError, SyntaxError):
        print("Warning: Could not parse 'dates_watched' column. Assuming it's already in list format.")
        
    df['date_added'] = pd.to_datetime(df['date_added'])


    # --- 2. Define Weights and Bonuses for the Scoring Algorithm ---
    weights = {
        'rating': 2,
        'rewatch': 20,
        'lists': 2,
        'liked': 10
    }
    bonuses = {
        'favorite_film': 30, # Ultimate seal of approval
        'pantheon': 15,      # For liked + high-rated films
        'obsession': 10,     # For liked + rewatched films
        'review_multiplier': 1.5
    }

    # --- 3. Calculate Taste Score Components ---
    print("Calculating taste score based on the advanced model...")

    df['raw_score'] = 0

    # a. Base Rating Score & Review Amplification
    rating_score = df['rating'].fillna(0) * weights['rating']
    is_reviewed = df['reviewed'] == 'yes'
    amplified_rating_score = np.where(is_reviewed, rating_score * bonuses['review_multiplier'], rating_score)
    df['raw_score'] += amplified_rating_score

    # b. Liked, Rewatch, and List Scores
    df['raw_score'] += np.where(df['liked'] == 'yes', weights['liked'], 0)
    rewatch_counts = (df['no_of_watches'] - 1).clip(lower=0)
    df['raw_score'] += rewatch_counts * weights['rewatch']
    df['raw_score'] += df['in_lists_count'].fillna(0) * weights['lists']

    # c. Synergy and Favorite Film Bonuses
    is_pantheon = (df['liked'] == 'yes') & (df['rating'] >= 4.5)
    is_obsession = (df['liked'] == 'yes') & (df['no_of_watches'] > 1)
    is_favorite = df['url'].isin(favorite_film_urls)
    
    df['raw_score'] += np.where(is_pantheon, bonuses['pantheon'], 0)
    df['raw_score'] += np.where(is_obsession, bonuses['obsession'], 0)
    df['raw_score'] += np.where(is_favorite, bonuses['favorite_film'], 0)

    # --- 4. Apply Recency Weighting ---
    
    def get_last_watched(row):
        if row['dates_watched'] and isinstance(row['dates_watched'], list) and row['dates_watched']:
            return max([pd.to_datetime(d) for d in row['dates_watched']])
        return row['date_added']

    df['last_watched_date'] = df.apply(get_last_watched, axis=1)
    
    years_since = (datetime.now() - pd.to_datetime(df['last_watched_date'])).dt.days / 365.25
    recency_multiplier = 1 / (1 + 0.2 * years_since)
    df['final_score'] = df['raw_score'] * recency_multiplier

    # --- 5. Normalize Score to 0-100 Scale ---
    min_score = df['final_score'].min()
    max_score = df['final_score'].max()
    
    if (max_score - min_score) > 0:
        df['taste_score'] = 100 * (df['final_score'] - min_score) / (max_score - min_score)
    else:
        df['taste_score'] = 100.0
        
    print("Score calculation and normalization complete.")
    
    # --- 6. Sort and Finalize DataFrame ---
    ranked_df = df.sort_values(by='taste_score', ascending=False, kind='mergesort')
    
    final_cols = [
        'taste_score', 'name', 'year', 'rating', 'liked', 'no_of_watches', 
        'reviewed', 'in_lists_count', 'url', 'last_watched_date'
    ]
    existing_cols = [col for col in final_cols if col in ranked_df.columns]
    
    return ranked_df[existing_cols]


if __name__ == '__main__':
    input_file = 'letterboxd_merged_data.csv'
    output_file = 'letterboxd_ranked_by_taste.csv'

    # Find the Letterboxd zip file automatically
    zip_to_process = None
    possible_zips = glob.glob('letterboxd-*.zip')
    if possible_zips:
        zip_to_process = possible_zips[0]
        print(f"Found Letterboxd export file: '{zip_to_process}'")
    else:
        print("Warning: No 'letterboxd-*.zip' file found. Cannot add 'Favorite Film' bonus.")

    # Get the list of favorite films from the zip file
    favorite_urls = get_favorite_films_from_zip(zip_to_process)
    
    # Run the ranking process
    ranked_movies = rank_movies_by_intuitive_taste(
        input_csv=input_file,
        favorite_film_urls=favorite_urls
    )
    
    if ranked_movies is not None:
        ranked_movies.round({'taste_score': 2}).to_csv(output_file, index=False)
        print(f"\nSuccessfully created the ranked file: '{output_file}'")

        print("\n--- Top 20 Films That Best Represent Your Taste ---")
        ranked_movies['taste_score'] = ranked_movies['taste_score'].map('{:,.2f}'.format)
        print(ranked_movies.head(20).to_string(index=False))