// src/App.js
// This is the main router of our application. It controls which page is currently
// visible and handles the animated transitions between them using Framer Motion.

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';

import { FavoritesProvider } from './contexts/FavoritesContext';
import { ApiProvider, useApi } from './contexts/ApiContext';
import { UserPreferencesProvider } from './contexts/UserPreferencesContext';
import AuthPage from './components/AuthPage';
import ImportPage from './components/ImportPage';
import LoadingPage from './components/LoadingPage';
import TagSelectionPage from './components/TagSelectionPageNew';
import CalibrationPage from './components/CalibrationPage';
import RecommendationsPage from './components/RecommendationsPage';
import FavoritesPage from './components/FavoritesPage';

// Animation settings for page transitions
const pageVariants = {
  initial: { opacity: 0, y: 50, scale: 0.9 },
  in: { opacity: 1, y: 0, scale: 1 },
  out: { opacity: 0, y: -50, scale: 1.1 }
};

const pageTransition = {
  type: 'spring',
  stiffness: 50,
  damping: 20,
  duration: 1.5
};

// Wrapper component to handle animations with React Router
const AnimatedPage = ({ children }) => (
  <motion.div
    initial="initial"
    animate="in"
    exit="out"
    variants={pageVariants}
    transition={pageTransition}
  >
    {children}
  </motion.div>
);

// API Connection Status Component
const ApiStatus = () => {
  const { isConnected, isLoading, error } = useApi();

  if (isLoading) {
    return (
      <div className="fixed top-4 right-4 bg-blue-500 text-white px-3 py-1 rounded-full text-sm">
        Connecting to API...
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="fixed top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm">
        API Disconnected
      </div>
    );
  }

  return (
    <div className="fixed top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm">
      API Connected
    </div>
  );
};

// Main App Component
const AppContent = () => {
  const { isConnected, isLoading } = useApi();

  // Show loading page while checking API connection
  if (isLoading) {
    return <LoadingPage />;
  }

  // Show error page if API is not connected
  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center text-white">
          <h1 className="text-4xl font-bold mb-4">Connection Error</h1>
          <p className="text-xl mb-6">Unable to connect to the API server</p>
          <p className="text-lg">Please make sure the backend server is running on port 8000</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-6 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <main>
      <ApiStatus />
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<Navigate to="/auth" replace />} />
          <Route 
            path="/auth" 
            element={
              <AnimatedPage>
                <AuthPage />
              </AnimatedPage>
            } 
          />
          <Route 
            path="/import" 
            element={
              <AnimatedPage>
                <ImportPage />
              </AnimatedPage>
            } 
          />
          <Route 
            path="/loading" 
            element={
              <AnimatedPage>
                <LoadingPage />
              </AnimatedPage>
            } 
          />
          <Route 
            path="/tags" 
            element={
              <AnimatedPage>
                <TagSelectionPage />
              </AnimatedPage>
            } 
          />
          <Route 
            path="/calibration" 
            element={
              <AnimatedPage>
                <CalibrationPage />
              </AnimatedPage>
            } 
          />
          <Route 
            path="/recommendations" 
            element={
              <AnimatedPage>
                <RecommendationsPage />
              </AnimatedPage>
            } 
          />
          <Route 
            path="/favorites" 
            element={
              <AnimatedPage>
                <FavoritesPage />
              </AnimatedPage>
            }
          />
        </Routes>
      </AnimatePresence>
    </main>
  );
};

export default function App() {
  return (
    <Router>
      <ApiProvider>
        <UserPreferencesProvider>
          <FavoritesProvider>
            <AppContent />
          </FavoritesProvider>
        </UserPreferencesProvider>
      </ApiProvider>
    </Router>
  );
}
