import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Heart } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useFavorites } from '../contexts/FavoritesContext';
import { movieData } from '../data';

const FavoritesPage = () => {
    const { likedMovies, handleLikeToggle } = useFavorites();
    const navigate = useNavigate();
    const favorites = likedMovies;
    
    const [currentIndex, setCurrentIndex] = useState(0);
    const moviesPerPage = 4;
    
    const canGoNext = currentIndex + moviesPerPage < favorites.length;
    const canGoPrev = currentIndex > 0;

    // Modal state
    const [modalMovie, setModalMovie] = useState(null);

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
                onClick={() => navigate('/recommendations')} 
                className="absolute top-8 left-8 text-pink-700 hover:text-pink-900"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
            >
                <ChevronLeft size={32} />
            </motion.button>

            <div className="w-full max-w-6xl flex flex-col items-start">
                <h1 className="text-5xl font-bold text-[#D94686] mb-4 font-cinzel tracking-wider w-full text-left pl-8">
                    Your Favorites
                </h1>
                <div className="w-full flex items-center justify-center">
                    <motion.button 
                        onClick={prevFavorites} 
                        disabled={!canGoPrev}
                        className="text-[#333] disabled:opacity-30"
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                    >
                        <ChevronLeft size={48} />
                    </motion.button>

                    <div className="flex-1 grid grid-cols-4 gap-8 h-[450px] justify-start">
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
                                    <div className="bg-gray-200 w-full aspect-[2/3] rounded-lg shadow-lg mb-4 border-2 border-gray-300 overflow-hidden group cursor-pointer relative"
                                        onClick={() => setModalMovie(movie)}
                                    >
                                        <img src={movie.poster} alt={movie.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"/>
                                        <button
                                            className="absolute top-2 right-2 z-10 bg-white/80 rounded-full p-1 hover:bg-pink-100 transition"
                                            onClick={e => { e.stopPropagation(); handleLikeToggle(movie); }}
                                            aria-label={likedMovies.some(m => m.id === movie.id) ? 'Unlike' : 'Like'}
                                        >
                                            <Heart
                                                size={28}
                                                className={likedMovies.some(m => m.id === movie.id) ? 'text-pink-500' : 'text-gray-400'}
                                                fill={likedMovies.some(m => m.id === movie.id) ? 'currentColor' : 'none'}
                                                strokeWidth={likedMovies.some(m => m.id === movie.id) ? 2 : 1.5}
                                            />
                                        </button>
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

            {/* Glassmorphic Modal */}
            {modalMovie && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={() => setModalMovie(null)}>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="backdrop-blur-xl bg-black/70 border border-white/20 rounded-2xl shadow-2xl p-0 max-w-3xl w-full relative text-left cursor-auto text-white flex flex-col md:flex-row overflow-hidden"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex-shrink-0 flex items-center justify-center bg-black/40 p-8 md:p-10" style={{minWidth:'220px'}}>
                            <img src={modalMovie.poster} alt={modalMovie.title} className="w-44 h-64 md:w-48 md:h-72 object-cover rounded-xl shadow-md border border-white/30" />
                        </div>
                        <div className="flex-1 min-w-0 p-6 md:p-10 flex flex-col gap-2">
                            <button className="absolute top-4 right-4 text-pink-200 text-3xl font-bold hover:text-white/80" onClick={() => setModalMovie(null)}>&times;</button>
                            <h2 className="text-3xl md:text-4xl font-bold mb-1 text-pink-200 break-words leading-tight">{modalMovie.title} <span className="text-lg text-pink-400">({modalMovie.year})</span></h2>
                            <div className="flex flex-wrap gap-2 mb-2">
                                <span className="inline-block bg-pink-900/30 text-pink-200 px-3 py-1 rounded-full text-sm font-semibold">{modalMovie.rating}</span>
                                {modalMovie.streaming && <span className="inline-block bg-pink-900/30 text-pink-200 px-3 py-1 rounded-full text-sm font-semibold">{modalMovie.streaming}</span>}
                                {modalMovie.runtime && <span className="inline-block bg-pink-900/30 text-pink-200 px-3 py-1 rounded-full text-sm font-semibold">{modalMovie.runtime}</span>}
                            </div>
                            <div className="mb-2 text-pink-300 font-semibold text-base">
                                dir. {modalMovie.credits?.crew?.find(c => c.job === 'Director')?.name || modalMovie.director || 'Unknown'}
                            </div>
                            {(() => {
                                let castArr = [];
                                if (modalMovie.credits?.cast) {
                                    castArr = modalMovie.credits.cast.slice(0, 5).map(actor => actor.name);
                                } else if (modalMovie.cast && modalMovie.cast.length > 0) {
                                    castArr = modalMovie.cast.slice(0, 5);
                                }
                                return castArr.length > 0 ? (
                                    <div className="mb-2 text-pink-200 text-base whitespace-pre-line break-words">
                                        <span className="font-semibold">cast:</span> {castArr.join(', ')}
                                    </div>
                                ) : null;
                            })()}
                            {modalMovie.genres && modalMovie.genres.length > 0 && (
                                <div className="mb-2 text-pink-200 text-base">
                                    <span className="font-semibold">genres:</span> {modalMovie.genres.join(', ')}
                                </div>
                            )}
                            <div className="mb-2 text-pink-100 text-base whitespace-pre-line break-words leading-relaxed max-h-40 overflow-y-auto pr-2 favorites-modal-scrollbar">
                                {modalMovie.synopsis}
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

export default FavoritesPage; 