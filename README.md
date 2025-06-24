# Project Lumiere

**Project Lumiere** is a full-stack movie recommendation system that combines a React frontend with a Python FastAPI backend. It provides highly personalized, explainable movie recommendations by analyzing user preferences across dozens of dimensions, integrating with the TMDB API, and leveraging advanced data enrichment and ranking algorithms.

---

## 🚀 Features

- **Advanced Movie Recommender**: Goes far beyond basic genre matching, analyzing 40+ user preference dimensions.
- **Multi-Strategy Discovery**: Recommends movies by genre, director, actor, keywords, and content similarity.
- **Explainable Recommendations**: Each suggestion includes clear reasons and transparent scoring.
- **User Data Enrichment**: Integrates with TMDB to fetch detailed movie, cast, and crew data.
- **Performance Optimized**: Caching, efficient data structures, and scalable processing.
- **Modern Frontend**: React app with API state management, error handling, and responsive UI.

---

## 🏗️ Architecture

```
Frontend (React, Port 3000) <----HTTP/JSON----> Backend (FastAPI, Port 8000)
         |                                            |
         v                                            v
   User Data Management                        TMDB API Integration
```

---

## 📁 File Structure

```
project-lumiere/
├── backend/
│   ├── enricher.py         # Movie data enrichment with TMDB API
│   ├── ranker.py           # Movie ranking and taste scoring
│   ├── test_simple.py      # TMDB API testing utilities
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

---

## 🧠 How It Works

1. **User Authentication**: Create user via API.
2. **Data Import**: Upload Letterboxd ZIP file.
3. **Profile Generation**: Backend processes data using `ranker.py`.
4. **Data Enrichment**: `enricher.py` fetches TMDB info.
5. **Movie Ranking**: Movies ranked by user taste.
6. **Display**: Frontend shows enhanced movie data.

---

## 🛠️ Development

- **Backend**: FastAPI, TMDB API integration, user preference analysis, caching.
- **Frontend**: React, API state/context, error handling, responsive UI.

---

## 📝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 📄 License

MIT License (or specify your license here)
