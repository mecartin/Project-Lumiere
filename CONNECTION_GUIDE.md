# Project Lumiere - Frontend-Backend Connection Guide

This guide explains how the React frontend and Python FastAPI backend are connected and how to run the full application.

## 🏗️ Architecture Overview

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   React App     │ ◄─────────────► │  FastAPI Server │
│  (Port 3000)    │                 │   (Port 8000)   │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   User Data     │                 │  TMDB API       │
│   Management    │                 │  Integration    │
└─────────────────┘                 └─────────────────┘
```

## 📁 File Structure

```
project-lumiere/
├── backend/
│   ├── enricher.py                 # Movie data enrichment with TMDB API
│   ├── ranker.py                   # Movie ranking and taste scoring
│   ├── test_simple.py              # TMDB API testing utilities
│   ├── userdata.py                 # User data management
│   ├── requirements_py38.txt       # Python dependencies
│   └── tmdb_cache/                 # Cached TMDB API responses
├── project-lumiere/                # React frontend
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js             # API service layer
│   │   ├── contexts/
│   │   │   └── ApiContext.js      # API state management
│   │   ├── config.js              # Configuration
│   │   └── App.js                 # Main app with API integration
│   └── package.json
├── start_backend.py                # Backend startup script
├── start_project.py                # Full stack startup script
└── CONNECTION_GUIDE.md             # This file
```

## 🚀 Quick Start

### Option 1: Start Everything at Once
```bash
# Run the combined startup script
python start_project.py
```

This will:
- Install all dependencies
- Start the backend server on port 8000
- Start the frontend server on port 3000
- Open the application in your browser

### Option 2: Start Servers Separately

#### Backend Only
```bash
# Install Python dependencies
cd backend
pip install -r requirements_py38.txt

# Start the server (you'll need to create a new main.py or use existing components)
# For now, you can test the core components:
python test_simple.py
python ranker.py
```

#### Frontend Only
```bash
# Install Node.js dependencies
cd project-lumiere
npm install

# Start the development server
npm start
```

## 🔧 Configuration

### Environment Variables

#### Backend (Optional)
```bash
export TMDB_API_KEY=your_tmdb_api_key_here
```

#### Frontend (Optional)
Create a `.env.local` file in the `project-lumiere` directory:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

### API Configuration

The frontend is configured to connect to the backend via:
- **Base URL**: `http://localhost:8000` (configurable)
- **CORS**: Enabled for development
- **Content Type**: JSON for most requests, FormData for file uploads

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /docs` - Interactive API documentation

### User Management
- `POST /users/create` - Create new user
- `GET /users/{user_id}` - Get user details
- `GET /users/{user_id}/profile` - Get user movie profile
- `GET /users/{user_id}/stats` - Get user statistics

### Data Import
- `POST /import/letterboxd/{user_id}` - Import Letterboxd data

### Movie Data Processing
- `POST /enrich/movies` - Enrich movie data with TMDB information
- `POST /rank/movies` - Rank movies by user taste preferences

### Tags
- `GET /tags` - Get available mood tags
- `GET /tags?category=emotion` - Get tags by category

> **Note**: The recommendation endpoints have been removed. You can use the `enricher.py` and `ranker.py` components directly for movie processing and ranking.

## 🎯 Frontend Integration

### API Service Layer (`src/services/api.js`)
Provides a clean interface for all backend communication:

```javascript
import apiService from '../services/api';

// Create a user
const user = await apiService.createUser({
  username: 'john_doe',
  email: 'john@example.com'
});

// Get recommendations
const recommendations = await apiService.getRecommendations(userId, {
  count: 20,
  filters: { min_year: 2000 }
});
```

### API Context (`src/contexts/ApiContext.js`)
Manages API state throughout the application:

```javascript
import { useApi } from '../contexts/ApiContext';

const { isConnected, currentUser, createUser } = useApi();
```

### Configuration (`src/config.js`)
Centralized configuration management:

```javascript
import config from '../config';

// API base URL
console.log(config.API_BASE_URL); // http://localhost:8000

// TMDB image URLs
const posterUrl = config.TMDB_IMAGE_BASE_URL + '/w500' + posterPath;
```

## 🔄 Data Flow

1. **User Authentication**: Frontend creates user via API
2. **Data Import**: User uploads Letterboxd ZIP file
3. **Profile Generation**: Backend processes data using `ranker.py` to create user profile
4. **Data Enrichment**: Use `enricher.py` to enhance movie data with TMDB information
5. **Movie Ranking**: Use `ranker.py` to rank movies by user taste preferences
6. **Display**: Frontend displays processed movie data with enhanced information

## 🛠️ Development

### Backend Development
- Core components: `enricher.py`, `ranker.py`, `test_simple.py`
- TMDB API integration with caching
- Letterboxd data processing and ranking
- User preference analysis

### Frontend Development
- React development server with hot reloading
- API connection status indicator in top-right corner
- Error handling and loading states built-in

### Testing Core Components
```bash
# Test TMDB API connection
cd backend
python test_simple.py

# Test movie ranking
python ranker.py

# Test movie enrichment
python -c "from enricher import MovieTasteEnricher; enricher = MovieTasteEnricher('your_api_key'); print(enricher.test_api_connection())"
```

### Debugging
- Backend logs are displayed in the terminal
- Frontend console shows API requests and responses
- Network tab in browser dev tools shows HTTP traffic

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check if port 8000 is available
lsof -i :8000

# Check Python dependencies
pip list | grep fastapi
```

#### Frontend Can't Connect to Backend
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/main.py
```

#### API Key Issues
```bash
# Set TMDB API key
export TMDB_API_KEY=your_key_here

# Verify it's set
echo $TMDB_API_KEY
```

### Error Messages

- **"API Disconnected"**: Backend server is not running
- **"Failed to connect to API server"**: Network or configuration issue
- **"TMDB API key not set"**: Some features may not work properly

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [TMDB API Documentation](https://developers.themoviedb.org/3)

## 🤝 Contributing

When adding new features:

1. **Backend**: Add new endpoints to `main.py`
2. **Frontend**: Add corresponding methods to `api.js`
3. **Context**: Update `ApiContext.js` if needed
4. **Documentation**: Update this guide

## 📄 License

This project is part of Project Lumiere. See the main README for license information. 