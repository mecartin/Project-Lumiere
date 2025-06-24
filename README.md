# Project Lumiere

<p align="center">
  <img src="project-lumiere/public/logo192.png" alt="Project Lumiere Logo" width="120" />
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build Status"></a>
  <a href="#"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/backend-FastAPI-green" alt="Backend: FastAPI"></a>
  <a href="#"><img src="https://img.shields.io/badge/frontend-React-blue" alt="Frontend: React"></a>
</p>

**Project Lumiere** is a full-stack movie recommendation system that combines a React frontend with a Python FastAPI backend. It provides highly personalized, explainable movie recommendations by analyzing user preferences across dozens of dimensions, integrating with the TMDB API, and leveraging advanced data enrichment and ranking algorithms.

---

## 🚀 Features

- **Advanced Movie Recommender**: Goes far beyond basic genre matching, analyzing 40+ user preference dimensions.
- **Tag-Based Recommender**: Accepts up to 25 user-selected mood, genre, or thematic tags (e.g., "feel-good", "thrilling", "romantic") and combines them with user calibration (era, runtime, popularity, familiarity) for highly personalized results.
- **Multi-Strategy Discovery**: Recommends movies by genre, director, actor, keywords, and content similarity, and leverages TMDB's similar-movies API.
- **Explainable Recommendations**: Each suggestion includes clear reasons, transparent scoring, and source tags.
- **User Data Enrichment**: Integrates with TMDB to fetch detailed movie, cast, and crew data.
- **Performance Optimized**: Caching, efficient data structures, and scalable processing.
- **Modern Frontend**: React app with API state management, error handling, and responsive UI.

---

## 🖼️ Screenshots

> _Add your own UI screenshots here!_

<p align="center">
  <img src="project-lumiere/public/logo192.png" alt="App Logo" width="120" />
  <!-- Example: <img src="screenshots/homepage.png" alt="Homepage" width="600" /> -->
</p>

---

## 🏗️ Architecture

```
Frontend (React, Port 3000) <----HTTP/JSON----> Backend (FastAPI, Port 8000)
         |                                            |
         v                                            v
   User Data Management                        TMDB API Integration
         |                                            |
         v                                            v
   Tag-Based Recommender Engine         TMDB Tag/Keyword/Similarity
```

---

## 📁 File Structure

```
project-lumiere/
├── backend/
│   ├── enricher.py         # Movie data enrichment with TMDB API
│   ├── ranker.py           # Movie ranking and taste scoring
│   ├── tag_based_recommender.py # Tag-based recommendation engine
│   ├── tag_recommendations_api.py # FastAPI endpoint for tag-based recommendations
│   ├── test_tag_recommender.py # Test and usage examples for tag-based recommender
│   ├── requirements_py38.txt
│   └── tmdb_cache/         # Cached TMDB API responses
├── project-lumiere/        # React frontend
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js      # API service layer
│   │   ├── contexts/
│   │   │   └── ApiContext.js # API state management
│   │   └── App.js          # Main app with API integration
│   └── package.json
├── start_backend.py        # Backend startup script
├── start_project.py        # Full stack startup script
└── CONNECTION_GUIDE.md     # Connection and setup guide
```

---

## ⚡ Quick Start

### 1. Start Everything at Once

```bash
python start_project.py
```
- Installs dependencies
- Starts backend (port 8000) and frontend (port 3000)
- Opens the app in your browser

### 2. Start Servers Separately

#### Backend

```bash
cd backend
pip install -r requirements_py38.txt
python test_simple.py
python ranker.py
```

#### Frontend

```bash
cd project-lumiere
npm install
npm start
```

---

## 🔧 Configuration

### Environment Variables

#### Backend

Set your TMDB API key:
```bash
export TMDB_API_KEY=your_tmdb_api_key_here
```
Or copy `.env.example` to `.env` and fill in your key.

#### Frontend

Create a `.env.local` in `project-lumiere`:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

---

## 🧩 Backend Dependencies

From `backend/requirements_py38.txt`:
- fastapi
- uvicorn
- python-dotenv
- pydantic
- pandas
- numpy
- sqlalchemy
- scikit-learn
- scipy
- httpx
- python-multipart
- requests
- python-jose[cryptography]
- passlib[bcrypt]

---

## 🔌 API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /docs` - Interactive API docs
- `POST /users/create` - Create user
- `GET /users/{user_id}` - Get user details
- `POST /import/letterboxd/{user_id}` - Import Letterboxd data
- `POST /enrich/movies` - Enrich movie data
- `POST /rank/movies` - Rank movies by user taste
- `GET /tags` - Get available mood tags
- `POST /recommendations/tag-based` - **Tag-based movie recommendations** (see below)

### Tag-Based Recommender Endpoint
- **POST `/recommendations/tag-based`**
  - **Request:**
    - `user_tags`: List of up to 25 tags (e.g., ["feel-good", "comedy", "inspiring"])
    - `calibration_settings`: Dict with `era`, `runtime`, `popularity`, `familiarity` (1-10 scale)
    - `user_movies`: (Optional) List of user's favorite movies for profile building
    - `max_recommendations`: (Optional) Number of results to return
  - **Response:**
    - List of recommended movies, each with TMDB info, scores, and source tags
    - User profile summary and processing time

---

## 💻 Usage Examples

### Tag-Based Recommender API Example (Python)
```python
import requests

payload = {
    "user_tags": ["feel-good", "comedy", "inspiring"],
    "calibration_settings": {"era": 7, "runtime": 6, "popularity": 5, "familiarity": 4},
    "user_movies": [
        {"tmdb_id": 550, "title": "Fight Club", "cast": ["Brad Pitt"], "directors": ["David Fincher"], "keywords": ["psychological thriller"]}
    ],
    "max_recommendations": 10
}
resp = requests.post('http://localhost:8000/recommendations/tag-based', json=payload)
print(resp.json())
```

**Example Response:**
```json
{
  "recommendations": [
    {
      "tmdb_id": 13,
      "title": "Forrest Gump",
      "genres": ["Drama", "Comedy"],
      "final_score": 9.2,
      "similarity_score": 8.5,
      "familiarity_score": 7.0,
      "source_tags": ["feel-good", "inspiring"]
    }
    // ...
  ],
  "total_found": 10,
  "processing_time": 2.1,
  "user_profile_summary": {
    "tags_selected": 3,
    "tags": ["feel-good", "comedy", "inspiring"],
    "calibration_settings": { "era": 7, "runtime": 6, "popularity": 5, "familiarity": 4 },
    "movies_analyzed": 1,
    "recommendations_found": 10
  }
}
```

### Frontend Example (React)
```js
import apiService from './services/api';

const user = await apiService.createUser({ username: 'john_doe', email: 'john@example.com' });
const recommendations = await apiService.getTagBasedRecommendations({
  user_tags: ['feel-good', 'comedy', 'inspiring'],
  calibration_settings: { era: 7, runtime: 6, popularity: 5, familiarity: 4 },
  user_movies: [/* ... */],
  max_recommendations: 10
});
```

---

## 🧠 How It Works

1. **User Authentication**: Create user via API.
2. **Data Import**: Upload Letterboxd ZIP file.
3. **Profile Generation**: Backend processes data using `ranker.py`.
4. **Tag-Based Recommendation**: Users select up to 25 tags and set calibration preferences (era, runtime, popularity, familiarity). The backend fetches and scores movies from TMDB for each tag, finds similar movies to the user's favorites, and ranks results by similarity, familiarity, and calibration.
5. **Data Enrichment**: `enricher.py` fetches TMDB info for additional context.
6. **Movie Ranking**: Movies ranked by user taste and tag-based scores.
7. **Display**: Frontend shows enhanced, explainable movie data with source tags and scores.

---

## 🛠️ Development

- **Backend**: FastAPI, TMDB API integration, tag-based and traditional recommenders, user preference analysis, caching.
- **Frontend**: React, API state/context, error handling, responsive UI.

### Testing

- **Backend**: Run `python test_simple.py`, `python test_api_connection.py`, or `python test_tag_recommender.py` in the backend directory.
- **Frontend**: Run `npm test` in the `project-lumiere` directory.

### Deployment

- **Backend**: Deploy with any WSGI/ASGI server (e.g., Uvicorn, Gunicorn).
- **Frontend**: Build with `npm run build` and serve with any static file server.

---

## 📝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 📄 License

MIT License (or specify your license here)
