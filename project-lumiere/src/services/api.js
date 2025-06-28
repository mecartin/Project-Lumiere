import config from '../config';

// API service for communicating with the backend
class ApiService {
  constructor() {
    this.baseURL = config.API_BASE_URL;
  }

  // Generic request method
  async request(endpoint, options = {}, tagApiUrl = null) {
    const url = tagApiUrl ? `${tagApiUrl}${endpoint}` : `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // User management
  async createUser(userData) {
    return this.request('/users/create', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getUser(userId) {
    return this.request(`/users/${userId}`);
  }

  async getUserProfile(userId) {
    return this.request(`/users/${userId}/profile`);
  }

  async getUserStats(userId) {
    return this.request(`/users/${userId}/stats`);
  }

  // Letterboxd import
  async importLetterboxdData(userId, file) {
    const formData = new FormData();
    formData.append('file', file);

    const url = `${this.baseURL}/import/letterboxd/${userId}`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Import failed:', error);
      throw error;
    }
  }

  // Recommendations
  async getRecommendations(userId, tagIds = null, filters = null, count = 20) {
    const requestData = {
      user_id: userId,
      tag_ids: tagIds,
      filters: filters,
      count: count,
    };

    return this.request('/recommendations', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }

  // Tag-based recommendations (new algorithm)
  async getTagBasedRecommendations(userTags, calibrationSettings, userMovies = null, count = 20) {
    const requestData = {
      user_tags: userTags,
      calibration_settings: calibrationSettings,
      user_movies: userMovies,
      max_recommendations: count,
    };

    // Use the unified API endpoint (same port as main API)
    return this.request('/recommendations/tag-based', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }

  async getDiscoveryRecommendations(options = {}) {
    const params = new URLSearchParams();
    if (options.genre) params.append('genre', options.genre);
    if (options.decade) params.append('decade', options.decade);
    if (options.count) params.append('count', options.count);

    const endpoint = `/recommendations/discovery?${params.toString()}`;
    return this.request(endpoint);
  }

  // Tags
  async getTags(category = null) {
    const endpoint = category ? `/tags?category=${category}` : '/tags';
    return this.request(endpoint);
  }

  async getAvailableTags() {
    return this.request('/tags/available');
  }

  // Keywords database status
  async getKeywordsStatus() {
    return this.request('/keywords/status');
  }

  async generateKeywordsDatabase() {
    return this.request('/keywords/generate', {
      method: 'POST',
    });
  }

  // Movie data helpers
  getMoviePosterUrl(posterPath, size = 'w500') {
    if (!posterPath) return null;
    return `${config.TMDB_IMAGE_BASE_URL}/${size}${posterPath}`;
  }

  getMovieBackdropUrl(backdropPath, size = 'w1280') {
    if (!backdropPath) return null;
    return `${config.TMDB_IMAGE_BASE_URL}/${size}${backdropPath}`;
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService; 