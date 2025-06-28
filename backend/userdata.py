import pandas as pd
import numpy as np
import os
import zipfile
import io
import glob
import json
from collections import Counter
from datetime import datetime
import uuid

def merge_letterboxd_data_from_zip(zip_path='letterboxd-export.zip'):
    """
    Loads, processes, and merges Letterboxd CSV data directly from a zip export.

    This function reads 'watched.csv' as the base and enriches it with data from
    'diary.csv', 'ratings.csv', 'reviews.csv', 'likes/films.csv', and all files
    in the 'lists/' directory. It is specifically designed to handle list files
    where the CSV headers are on the second row.

    Args:
        zip_path (str): The file path for the Letterboxd zip export.

    Returns:
        pandas.DataFrame: A DataFrame containing the merged and processed data,
                          or None if the zip file or essential CSVs are not found.
    """
    # --- Internal helper for consistent key creation ---
    def _create_primary_key(df):
        """Creates a composite key from Name and Year."""
        if 'Name' in df.columns and 'Year' in df.columns:
            return df['Name'].astype(str) + '_' + df['Year'].astype(float).astype(int).astype(str)
        return None

    # --- 1. Validate Zip Path and Find Root Directory ---
    if not os.path.exists(zip_path):
        print(f"Error: Zip file not found at '{zip_path}'")
        return None

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            print(f"Successfully opened zip file: '{zip_path}'")
            all_files = zf.namelist()
            
            root_folder = ''
            if all_files and '/' in all_files[0]:
                root_folder = all_files[0].split('/')[0] + '/'
            
            if root_folder and f'{root_folder}watched.csv' not in all_files:
                if 'watched.csv' in all_files:
                    print(f"Warning: Detected root folder '{root_folder}', but key files not found there. Assuming files are at the zip's root.")
                    root_folder = ''
            
            print(f"Identified root folder in zip as: '{root_folder or '(root of zip)'}'")

            # --- 2. Load Base Data (watched.csv) and Create Mappings ---
            watched_path = f'{root_folder}watched.csv'
            with zf.open(watched_path) as f:
                # Core files have normal headers on the first row.
                base_df = pd.read_csv(io.TextIOWrapper(f, 'utf-8'), skipinitialspace=True)
            
            base_df.rename(columns={'Letterboxd URI': 'url', 'Date': 'date_added'}, inplace=True)
            base_df = base_df[['url', 'Name', 'Year', 'date_added']].copy()
            base_df.dropna(subset=['Name', 'Year', 'url'], inplace=True)
            base_df['date_added'] = pd.to_datetime(base_df['date_added'])
            base_df['primary_key'] = _create_primary_key(base_df)
            
            uri_to_key_map = base_df.set_index('url')['primary_key'].to_dict()
            print(f"Base data established from watched.csv with {len(base_df)} entries.")

            # --- 3. Process 'Liked' Films ---
            likes_path = f'{root_folder}likes/films.csv'
            liked_keys = set()
            try:
                with zf.open(likes_path) as f:
                    likes_df = pd.read_csv(io.TextIOWrapper(f, 'utf-8'), skipinitialspace=True)
                    likes_df.dropna(subset=['Name', 'Year'], inplace=True)
                    liked_keys = set(_create_primary_key(likes_df))
                print(f"Found {len(liked_keys)} liked films.")
            except (KeyError, zipfile.BadZipFile):
                print("Warning: 'likes/films.csv' not found or is invalid. 'liked' column will default to 'no'.")
            
            base_df['liked'] = base_df['primary_key'].isin(liked_keys).map({True: 'yes', False: 'no'})

            # --- 4. Process Film Appearances in Lists (Robustly) ---
            list_files = [f for f in all_files if f.startswith(f'{root_folder}lists/') and f.endswith('.csv')]
            list_key_counter = Counter()
            if list_files:
                print(f"Processing {len(list_files)} files from the 'lists' directory...")
                for list_file_path in list_files:
                    try:
                        with zf.open(list_file_path) as f:
                            # List files have headers on the second row (header=1).
                            list_df = pd.read_csv(io.TextIOWrapper(f, 'utf-8'), header=1, skipinitialspace=True)
                            
                            if 'Name' in list_df.columns and 'Year' in list_df.columns:
                                list_df.dropna(subset=['Name', 'Year'], inplace=True)
                                unique_keys_in_list = _create_primary_key(list_df).unique()
                                list_key_counter.update(unique_keys_in_list)
                                continue

                            uri_col = None
                            if 'Letterboxd URI' in list_df.columns:
                                uri_col = 'Letterboxd URI'
                            elif 'URL' in list_df.columns:
                                uri_col = 'URL'

                            if uri_col:
                                print(f"-> Info: Matching list '{os.path.basename(list_file_path)}' by URI column ('{uri_col}').")
                                list_df.dropna(subset=[uri_col], inplace=True)
                                unique_uris_in_list = list_df[uri_col].unique()
                                keys_from_uris = [uri_to_key_map.get(uri) for uri in unique_uris_in_list]
                                valid_keys = [key for key in keys_from_uris if key is not None]
                                list_key_counter.update(valid_keys)
                                continue

                            print(f"-> Warning: Could not process list file '{os.path.basename(list_file_path)}'. It is missing 'Name'/'Year' or a URI column.")

                    except Exception as e:
                        print(f"-> Error processing list file '{os.path.basename(list_file_path)}'. Reason: {e}")
            else:
                print("No files found in the 'lists' directory.")

            base_df['in_lists_count'] = base_df['primary_key'].map(list_key_counter).fillna(0).astype(int)

            # --- 5. Aggregate Data from Other Core Files ---
            # A. Diary Data
            with zf.open(f'{root_folder}diary.csv') as f:
                diary_df = pd.read_csv(io.TextIOWrapper(f, 'utf-8'), skipinitialspace=True)
            diary_df.dropna(subset=['Name', 'Year'], inplace=True)
            diary_df['Date'] = pd.to_datetime(diary_df['Date'])
            
            agg_funcs = {'dates_watched': ('Date', lambda x: sorted(x.dt.strftime('%Y-%m-%d').unique())), 'no_of_watches': ('Date', 'size')}
            if 'Tags' in diary_df.columns:
                agg_funcs['user_tags'] = ('Tags', lambda x: ', '.join(x.dropna().unique()))

            diary_agg = diary_df.groupby(['Name', 'Year']).agg(**agg_funcs).reset_index()
            diary_agg['primary_key'] = _create_primary_key(diary_agg)

            # B. Ratings Data
            with zf.open(f'{root_folder}ratings.csv') as f:
                ratings_df = pd.read_csv(io.TextIOWrapper(f, 'utf-8'), skipinitialspace=True)
            ratings_df.dropna(subset=['Name', 'Year'], inplace=True)
            ratings_df['primary_key'] = _create_primary_key(ratings_df)
            ratings_df['Date'] = pd.to_datetime(ratings_df['Date'])
            ratings_info = ratings_df.sort_values('Date').drop_duplicates(subset='primary_key', keep='last')
            ratings_info = ratings_info[['primary_key', 'Rating']].rename(columns={'Rating': 'rating'})

            # C. Review Status
            with zf.open(f'{root_folder}reviews.csv') as f:
                reviews_df = pd.read_csv(io.TextIOWrapper(f, 'utf-8'), skipinitialspace=True)
            reviews_df.dropna(subset=['Name', 'Year'], inplace=True)
            reviews_df['primary_key'] = _create_primary_key(reviews_df)
            reviews_info = reviews_df[['primary_key']].copy()
            reviews_info['reviewed'] = 'yes'
            reviews_info = reviews_info.drop_duplicates(subset='primary_key')
            
            # --- 6. Merge All Data into Base DataFrame ---
            print("Merging all processed data...")
            merged_df = pd.merge(base_df, diary_agg.drop(columns=['Name', 'Year']), on='primary_key', how='left')
            merged_df = pd.merge(merged_df, ratings_info, on='primary_key', how='left')
            merged_df = pd.merge(merged_df, reviews_info, on='primary_key', how='left')
            print("Merge complete.")

            # --- 7. Clean Up and Finalize ---
            merged_df['reviewed'].fillna('no', inplace=True)
            merged_df['no_of_watches'] = merged_df['no_of_watches'].fillna(0).astype(int)
            merged_df['dates_watched'] = merged_df['dates_watched'].apply(lambda d: d if isinstance(d, list) else [])
            
            if 'user_tags' not in merged_df.columns:
                merged_df['user_tags'] = ''
            merged_df['user_tags'].fillna('', inplace=True)
            
            final_df = merged_df.rename(columns={'Name':'name', 'Year':'year'})
            
            final_columns = [
                'url', 'name', 'year', 'date_added', 'dates_watched', 'rating', 
                'no_of_watches', 'reviewed', 'user_tags', 'liked', 'in_lists_count'
            ]
            final_df = final_df[final_columns]
            
            return final_df

    except FileNotFoundError:
        print(f"Error: Could not find the zip file at '{zip_path}'.")
        return None
    except KeyError as e:
        print(f"Error: An essential file or column is missing: {e}. Please ensure your zip export is valid.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

class UserData:
    """Simple user data management class for the API"""
    
    def __init__(self):
        self.users_file = "users.json"
        self.users = self._load_users()
        
        # Sample mood tags for the API
        self.mood_tags = [
            {"id": 1, "name": "Feel Good", "category": "emotion"},
            {"id": 2, "name": "Thought Provoking", "category": "emotion"},
            {"id": 3, "name": "Inspiring", "category": "emotion"},
            {"id": 4, "name": "Relaxing", "category": "emotion"},
            {"id": 5, "name": "Exciting", "category": "emotion"},
            {"id": 6, "name": "Romantic", "category": "emotion"},
            {"id": 7, "name": "Funny", "category": "emotion"},
            {"id": 8, "name": "Sad", "category": "emotion"},
            {"id": 9, "name": "Thrilling", "category": "emotion"},
            {"id": 10, "name": "Mysterious", "category": "emotion"},
            {"id": 11, "name": "Action", "category": "genre"},
            {"id": 12, "name": "Comedy", "category": "genre"},
            {"id": 13, "name": "Drama", "category": "genre"},
            {"id": 14, "name": "Horror", "category": "genre"},
            {"id": 15, "name": "Sci-Fi", "category": "genre"},
            {"id": 16, "name": "Romance", "category": "genre"},
            {"id": 17, "name": "Thriller", "category": "genre"},
            {"id": 18, "name": "Documentary", "category": "genre"},
            {"id": 19, "name": "Animation", "category": "genre"},
            {"id": 20, "name": "Family", "category": "genre"}
        ]
    
    def _load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def save_user(self, user_data):
        """Save a new user"""
        user_id = user_data.get('id')
        if user_id:
            self.users[user_id] = user_data
            self._save_users()
            return True
        return False
    
    def get_user(self, user_id):
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_profile(self, user_id):
        """Get user's movie profile"""
        # For now, return a sample profile
        return {
            "total_watched": 150,
            "avg_rating": 7.2,
            "favorite_genres": ["Drama", "Comedy", "Action"],
            "favorite_directors": ["Christopher Nolan", "Quentin Tarantino"],
            "favorite_actors": ["Leonardo DiCaprio", "Emma Stone"],
            "watch_history": {
                "recent": ["Inception", "La La Land", "The Dark Knight"],
                "favorites": ["The Shawshank Redemption", "Pulp Fiction"]
            }
        }
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        return {
            "total_movies": 150,
            "average_rating": 7.2,
            "total_lists": 5,
            "favorite_year": 2010,
            "most_watched_genre": "Drama"
        }
    
    def import_letterboxd_data(self, user_id, data_path):
        """Import Letterboxd data for a user"""
        # Look for zip files in the data path
        zip_files = glob.glob(os.path.join(data_path, "*.zip"))
        
        if not zip_files:
            return {"error": "No zip files found"}
        
        zip_file = zip_files[0]
        result = merge_letterboxd_data_from_zip(zip_file)
        
        if result is not None:
            return {
                "success": True,
                "watched_count": len(result),
                "ratings_count": len(result[result['rating'].notna()]),
                "message": f"Successfully imported {len(result)} movies"
            }
        else:
            return {"error": "Failed to process Letterboxd data"}
    
    def get_tags(self, category=None):
        """Get available mood tags"""
        if category:
            return [tag for tag in self.mood_tags if tag["category"] == category]
        return self.mood_tags

if __name__ == '__main__':
    zip_to_process = None
    possible_zips = glob.glob('letterboxd-*.zip')
    if possible_zips:
        zip_to_process = possible_zips[0]
        print(f"Found Letterboxd export file: '{zip_to_process}'")
    else:
        print("\nOperation cancelled: No 'letterboxd-*.zip' file was found in this directory.")
        print("Please place your Letterboxd zip export in the same folder as this script.")

    if zip_to_process:
        merged_data = merge_letterboxd_data_from_zip(zip_to_process)
        if merged_data is not None:
            output_filename = 'letterboxd_merged_data.csv'
            merged_data.to_csv(output_filename, index=False)
            print(f"\nSuccessfully created the merged file: '{output_filename}'")
            print("\nPreview of the first 5 rows of the merged data:")
            print(merged_data.head())
