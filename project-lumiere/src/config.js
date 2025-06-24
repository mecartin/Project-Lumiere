// Configuration for the application
const config = {
  // API Configuration
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // Environment
  ENV: process.env.REACT_APP_ENV || 'development',
  
  // TMDB Configuration
  TMDB_IMAGE_BASE_URL: 'https://image.tmdb.org/t/p',
  TMDB_POSTER_SIZES: {
    small: 'w185',
    medium: 'w342',
    large: 'w500',
    original: 'original'
  },
  TMDB_BACKDROP_SIZES: {
    small: 'w300',
    medium: 'w780',
    large: 'w1280',
    original: 'original'
  },
  
  // App Configuration
  DEFAULT_RECOMMENDATION_COUNT: 20,
  MAX_RECOMMENDATION_COUNT: 100,
  
  // Animation settings
  ANIMATION_DURATION: 1500,
  ANIMATION_STIFFNESS: 50,
  ANIMATION_DAMPING: 20,
};

export default config; 