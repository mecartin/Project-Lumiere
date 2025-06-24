import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useFavorites } from '../contexts/FavoritesContext';
import { movieData } from '../data';

const FavoritesPage = () => {
    const { likedMovies } = useFavorites();
    const navigate = useNavigate();
    const favorites = movieData.filter(movie => likedMovies.includes(movie.id));
    
    const [currentIndex, setCurrentIndex] = useState(0);
    const moviesPerPage = 4;
    
    const canGoNext = currentIndex + moviesPerPage < favorites.length;
    const canGoPrev = currentIndex > 0;

    const nextFavorites = () => {
        if (canGoNext) {
            setCurrentIndex(currentIndex + moviesPerPage);
        }
    };

    const prevFavorites = () => {
        if (canGoPrev) {
            setCurrentIndex(currentIndex - moviesPerPage);
        }
    };

    const cardVariants = {
        hidden: { opacity: 0, scale: 0.8 },
        visible: i => ({
            opacity: 1,
            scale: 1,
            transition: {
                delay: i * 0.1,
                duration: 0.5,
                type: 'spring',
                stiffness: 100
            }
        }),
        exit: { opacity: 0, scale: 0.8 }
    };

    return (
        <div className="bg-[#FFF0F5] min-h-screen w-full flex flex-col items-center justify-center p-8 font-serif-vintage text-pink-700">
             <motion.button 
                onClick={() => navigate(-1)} 
                className="absolute top-8 left-8 text-pink-700 hover:text-pink-900"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
            >
                <ChevronLeft size={32} />
            </motion.button>

            <h1 className="text-5xl font-bold text-[#D94686] mb-12 font-cinzel tracking-wider">
                Your Favorites
            </h1>
            
            <div className="w-full max-w-6xl flex items-center justify-center">
                <motion.button 
                    onClick={prevFavorites} 
                    disabled={!canGoPrev}
                    className="text-[#333] disabled:opacity-30"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                >
                    <ChevronLeft size={48} />
                </motion.button>

                <div className="flex-1 grid grid-cols-4 gap-8 mx-8 h-[450px]">
                    <AnimatePresence mode="wait">
                        {favorites.slice(currentIndex, currentIndex + moviesPerPage).map((movie, i) => (
                            <motion.div
                                key={movie.id}
                                custom={i}
                                variants={cardVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                                className="text-center flex flex-col justify-start"
                            >
                                <div className="bg-gray-200 w-full aspect-[2/3] rounded-lg shadow-lg mb-4 border-2 border-gray-300 overflow-hidden group">
                                    <img src={movie.poster} alt={movie.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"/>
                                </div>
                                <p className="text-xl text-[#D94686] font-eb-garamond">{movie.title}</p>
                            </motion.div>
                        ))}
                         {/* Fill empty spots to prevent layout shift */}
                        {Array(moviesPerPage - favorites.slice(currentIndex, currentIndex + moviesPerPage).length).fill(null).map((_, i) => (
                            <div key={`placeholder-${i}`} className="w-full aspect-[2/3]"></div>
                        ))}
                    </AnimatePresence>
                </div>

                <motion.button 
                    onClick={nextFavorites} 
                    disabled={!canGoNext}
                    className="text-[#333] disabled:opacity-30"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                >
                    <ChevronRight size={48} />
                </motion.button>
            </div>
        </div>
    );
};

export default FavoritesPage; 