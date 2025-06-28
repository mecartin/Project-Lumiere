# Letterboxd Data Processing Workflow

This document explains the new file processing workflow for Project Lumiere.

## Overview

The system now supports uploading Letterboxd export ZIP files and automatically processes them through three stages:

1. **Data Extraction** (userdata.py) - Extracts and merges CSV data from the ZIP
2. **Movie Ranking** (ranker.py) - Analyzes user preferences and ranks movies
3. **Data Enrichment** (enricher.py) - Enhances data with TMDB information

## API Endpoints

### POST `/process-letterboxd`
Upload a Letterboxd export ZIP file for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: ZIP file with key `file`

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Processing started",
  "status_endpoint": "/processing-status/{session_id}"
}
```

### GET `/processing-status/{session_id}`
Get the current processing status for a session.

**Response:**
```json
{
  "status": "processing|completed|error",
  "progress": 0-100,
  "current_step": "Step description",
  "message": "Detailed message",
  "result": {
    "total_movies": 150,
    "ranked_movies": 150,
    "enriched_movies": 60,
    "favorite_films": 5,
    "processing_time": "2025-01-XX...",
    "enriched_csv_path": "temp_enriched_{session_id}.csv"
  }
}
```

## Processing Steps

### Step 1: Data Extraction (0-25%)
- Reads `watched.csv`, `diary.csv`, `ratings.csv`, `reviews.csv`
- Processes `likes/films.csv` and all files in `lists/` directory
- Merges all data into a unified DataFrame
- Output: `temp_merged_{session_id}.csv`

### Step 2: Movie Ranking (25-50%)
- Analyzes user preferences using the intuitive taste model
- Incorporates ratings, likes, rewatches, list inclusions
- Applies favorite film bonuses and synergy effects
- Output: `temp_ranked_{session_id}.csv`

### Step 3: Data Enrichment (50-75%)
- Fetches additional data from TMDB API
- Enhances movie information with genres, cast, crew, keywords
- Requires valid TMDB API key (optional - will skip if not available)
- Output: `temp_enriched_{session_id}.csv`

### Step 4: Finalization (75-100%)
- Cleans up temporary files
- Prepares final results
- Updates processing status

## Terminal Output

The backend provides detailed terminal output during processing:

```
=== Starting Letterboxd Processing Session: abc123 ===
Processing file: temp_upload_abc123.zip

📁 Step 1: Extracting and merging Letterboxd data...
✅ Successfully processed 150 movies

🎯 Step 2: Ranking movies by user taste...
📋 Found 5 favorite films
✅ Successfully ranked 150 movies

🔍 Step 3: Enriching data with TMDB information...
✅ Successfully enriched 60 movies

🧹 Step 4: Finalizing and cleaning up...
🗑️ Cleaned up: temp_merged_abc123.csv
🗑️ Cleaned up: temp_ranked_abc123.csv

🎉 Processing completed successfully!
📊 Results:
   - Total movies: 150
   - Ranked movies: 150
   - Enriched movies: 60
   - Favorite films: 5
   - Output file: temp_enriched_abc123.csv
```

## Frontend Integration

The Import page now includes:

1. **Download Button** - Redirects to Letterboxd export page
2. **Upload Button** - Opens file dialog for ZIP selection
3. **Progress Display** - Shows real-time processing status
4. **Next Button** - Appears when processing is complete

## Setup Instructions

### 1. Start the Backend
```bash
cd backend
python start_backend.py
```

### 2. (Optional) Set TMDB API Key
```bash
export TMDB_API_KEY=your_api_key_here
```

### 3. Test the Workflow
```bash
python test_processing.py
```

## Error Handling

- **Invalid ZIP**: Returns 400 error with message
- **Processing Errors**: Updates status with error details
- **TMDB API Issues**: Gracefully skips enrichment step
- **File Not Found**: Provides clear error messages

## File Management

- Temporary files are automatically cleaned up after processing
- Only the final enriched CSV is retained
- Session IDs ensure no file conflicts between users

## Performance Notes

- Processing time depends on file size and TMDB API availability
- Large exports (1000+ movies) may take 2-5 minutes
- TMDB enrichment is limited to top 60 movies for performance
- Background processing prevents API timeouts 