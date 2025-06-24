import React, { createContext, useContext, useState, useEffect } from 'react';
import { keywordIdMapping } from '../keywordsData';

const UserPreferencesContext = createContext();

export const useUserPreferences = () => {
  const context = useContext(UserPreferencesContext);
  if (!context) {
    throw new Error('useUserPreferences must be used within a UserPreferencesProvider');
  }
  return context;
};

export const UserPreferencesProvider = ({ children }) => {
  const [selectedTags, setSelectedTags] = useState([]);
  const [calibrationSettings, setCalibrationSettings] = useState({
    era: 5, // Default to middle value
    runtime: 5,
    popularity: 5,
    familiarity: 5,
  });
  const [recommendationStatus, setRecommendationStatus] = useState({
    isLoading: false,
    message: '',
    error: null,
    lastUpdated: null
  });

  // Load preferences from localStorage on mount
  useEffect(() => {
    const savedTags = localStorage.getItem('lumiere-selected-tags');
    const savedSettings = localStorage.getItem('lumiere-calibration-settings');
    
    if (savedTags) {
      try {
        setSelectedTags(JSON.parse(savedTags));
      } catch (error) {
        console.error('Failed to parse saved tags:', error);
      }
    }
    
    if (savedSettings) {
      try {
        setCalibrationSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('lumiere-selected-tags', JSON.stringify(selectedTags));
  }, [selectedTags]);

  useEffect(() => {
    localStorage.setItem('lumiere-calibration-settings', JSON.stringify(calibrationSettings));
  }, [calibrationSettings]);

  const updateSelectedTags = (tags) => {
    setSelectedTags(tags);
    console.log('🎯 Tags updated:', tags);
  };

  const addTag = (tag) => {
    if (!selectedTags.includes(tag) && selectedTags.length < 25) {
      const newTags = [...selectedTags, tag];
      setSelectedTags(newTags);
      console.log('➕ Tag added:', tag, 'Total:', newTags.length);
    }
  };

  const removeTag = (tag) => {
    const newTags = selectedTags.filter(t => t !== tag);
    setSelectedTags(newTags);
    console.log('➖ Tag removed:', tag, 'Total:', newTags.length);
  };

  const updateCalibrationSettings = (settings) => {
    setCalibrationSettings(settings);
    console.log('⚙️ Calibration settings updated:', settings);
  };

  const updateSetting = (key, value) => {
    setCalibrationSettings(prev => {
      const newSettings = { ...prev, [key]: value };
      console.log(`🎛️ Setting updated: ${key} = ${value}`);
      return newSettings;
    });
  };

  const setRecommendationLoading = (isLoading, message = '') => {
    setRecommendationStatus(prev => ({
      ...prev,
      isLoading,
      message,
      error: null,
      lastUpdated: new Date().toISOString()
    }));
    
    if (isLoading) {
      console.log('🔄 Loading recommendations:', message);
    } else {
      console.log('✅ Recommendations loaded');
    }
  };

  const setRecommendationError = (error) => {
    setRecommendationStatus(prev => ({
      ...prev,
      isLoading: false,
      error,
      lastUpdated: new Date().toISOString()
    }));
    console.error('❌ Recommendation error:', error);
  };

  const clearRecommendationStatus = () => {
    setRecommendationStatus({
      isLoading: false,
      message: '',
      error: null,
      lastUpdated: null
    });
  };

  const resetPreferences = () => {
    setSelectedTags([]);
    setCalibrationSettings({
      era: 5,
      runtime: 5,
      popularity: 5,
      familiarity: 5,
    });
    clearRecommendationStatus();
    localStorage.removeItem('lumiere-selected-tags');
    localStorage.removeItem('lumiere-calibration-settings');
    console.log('🔄 Preferences reset');
  };

  // Convert calibration settings to API filters
  const getApiFilters = () => {
    const filters = {};
    
    // Era filter (1-10 scale to year ranges)
    if (calibrationSettings.era <= 3) {
      filters.max_year = 1980;
    } else if (calibrationSettings.era <= 7) {
      filters.min_year = 1980;
      filters.max_year = 2010;
    } else {
      filters.min_year = 2010;
    }
    
    // Runtime filter (1-10 scale to minutes)
    if (calibrationSettings.runtime <= 3) {
      filters.max_runtime = 90;
    } else if (calibrationSettings.runtime <= 7) {
      filters.min_runtime = 90;
      filters.max_runtime = 150;
    } else {
      filters.min_runtime = 150;
    }
    
    // Popularity filter (1-10 scale to vote average)
    if (calibrationSettings.popularity <= 3) {
      filters.max_rating = 6.0;
    } else if (calibrationSettings.popularity <= 7) {
      filters.min_rating = 6.0;
      filters.max_rating = 7.5;
    } else {
      filters.min_rating = 7.5;
    }
    
    return filters;
  };

  // Convert selected tags to tag IDs (this would need to be mapped to actual tag IDs from the API)
  const getTagIds = () => {
    // Map selected tags to actual API tag IDs using the keyword mapping
    return selectedTags.map(tag => keywordIdMapping[tag]).filter(id => id !== undefined);
  };

  const value = {
    // State
    selectedTags,
    calibrationSettings,
    recommendationStatus,
    
    // Actions
    updateSelectedTags,
    addTag,
    removeTag,
    updateCalibrationSettings,
    updateSetting,
    setRecommendationLoading,
    setRecommendationError,
    clearRecommendationStatus,
    resetPreferences,
    
    // Utilities
    getApiFilters,
    getTagIds,
    
    // Computed values
    hasPreferences: selectedTags.length > 0,
    tagCount: selectedTags.length,
    maxTags: 25,
  };

  return (
    <UserPreferencesContext.Provider value={value}>
      {children}
    </UserPreferencesContext.Provider>
  );
}; 