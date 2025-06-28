import React, { createContext, useState, useContext } from 'react';

const FavoritesContext = createContext();

export const useFavorites = () => useContext(FavoritesContext);

export const FavoritesProvider = ({ children }) => {
    const [likedMovies, setLikedMovies] = useState([]);

    const handleLikeToggle = (movie) => {
        setLikedMovies(prev => {
            const exists = prev.some(m => m.id === movie.id);
            if (exists) {
                return prev.filter(m => m.id !== movie.id);
            } else {
                return [...prev, movie];
            }
        });
    };

    const value = {
        likedMovies,
        handleLikeToggle,
    };

    return (
        <FavoritesContext.Provider value={value}>
            {children}
        </FavoritesContext.Provider>
    );
}; 