import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService from '../services/api';

const ApiContext = createContext();

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

export const ApiProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  // Check API connection on mount
  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const health = await apiService.healthCheck();
      setIsConnected(true);
      console.log('✅ API connected:', health);
    } catch (err) {
      setIsConnected(false);
      setError('Failed to connect to API server');
      console.error('❌ API connection failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const createUser = async (userData) => {
    try {
      setError(null);
      const user = await apiService.createUser(userData);
      setCurrentUser(user);
      return user;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const getUser = async (userId) => {
    try {
      setError(null);
      const user = await apiService.getUser(userId);
      setCurrentUser(user);
      return user;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const getUserProfile = async (userId) => {
    try {
      setError(null);
      return await apiService.getUserProfile(userId);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const getUserStats = async (userId) => {
    try {
      setError(null);
      return await apiService.getUserStats(userId);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const importLetterboxdData = async (userId, file) => {
    try {
      setError(null);
      return await apiService.importLetterboxdData(userId, file);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const getTags = async (category = null) => {
    try {
      setError(null);
      return await apiService.getTags(category);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const getRecommendations = async (userId, options = {}) => {
    try {
      setError(null);
      return await apiService.getRecommendations(userId, options);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const getDiscoveryRecommendations = async (options = {}) => {
    try {
      setError(null);
      return await apiService.getDiscoveryRecommendations(options);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const clearError = () => {
    setError(null);
  };

  const logout = () => {
    setCurrentUser(null);
  };

  const value = {
    // State
    isConnected,
    isLoading,
    error,
    currentUser,
    
    // Actions
    checkApiConnection,
    createUser,
    getUser,
    getUserProfile,
    getUserStats,
    importLetterboxdData,
    getTags,
    getRecommendations,
    getDiscoveryRecommendations,
    clearError,
    logout,
    
    // Utilities
    getMoviePosterUrl: apiService.getMoviePosterUrl,
    getMovieBackdropUrl: apiService.getMovieBackdropUrl,
  };

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
}; 