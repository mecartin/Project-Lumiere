// src/components/RecommendationsPage.jsx
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useFavorites } from '../contexts/FavoritesContext';
import { useUserPreferences } from '../contexts/UserPreferencesContext';
import { useApi } from '../contexts/ApiContext';
import apiService from '../services/api';

// --- Sub-Components ---

const StatusIndicator = ({ status }) => {
    if (!status.isLoading && !status.error && !status.message) return null;

    return (
        <motion.div 
            className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 bg-black/80 text-white px-6 py-3 rounded-lg shadow-lg"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
        >
            <div className="flex items-center space-x-3">
                {status.isLoading && (
                    <motion.div 
                        className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                )}
                <span className="font-vt323 text-lg">
                    {status.error ? `❌ ${status.error}` : status.message}
                </span>
            </div>
        </motion.div>
    );
};

const CassetteShelf = ({ movies, hoveredIndex, setHoveredIndex, onSelectMovie, isInitialLoad, tilts }) => {
    return (
        <div className="w-full bg-retro-blue p-2 shadow-lg">
            <div className="bg-retro-orange w-full h-48 flex justify-start items-end px-4 space-x-2 overflow-x-auto scrollbar-hide">
                {movies.map((movie, index) => (
                    <motion.div
                        key={movie.id}
                        className="relative h-40 rounded-t-md cursor-pointer flex-shrink-0"
                        style={{ 
                            transformOrigin: 'bottom center',
                            zIndex: hoveredIndex === index ? 10 : index,
                        }}
                        onMouseEnter={() => setHoveredIndex(index)}
                        onMouseLeave={() => setHoveredIndex(null)}
                        onClick={() => onSelectMovie(movie)}
                        initial={{ y: -200, opacity: 0, width: '48px' }}
                        animate={{ 
                            y: hoveredIndex === index ? -15 : 0,
                            opacity: 1,
                            rotate: hoveredIndex === index ? 0 : (tilts[index] || 0),
                            width: hoveredIndex === index ? '106px' : '48px'
                        }}
                        transition={{ type: 'spring', stiffness: 150, damping: 20, delay: isInitialLoad ? index * 0.05 : 0 }}
                    >
                        <div className="w-full h-full bg-[#333] rounded-t-md p-0.5 border-t border-l border-r border-gray-400/30 shadow-inner">
                            <div className="relative w-full h-full bg-black rounded-sm overflow-hidden">
                                <AnimatePresence>
                                    {hoveredIndex === index || movie.showPoster ? (
                                        <motion.img
                                            src={movie.poster || `https://placehold.co/400x600/9ca3af/ffffff?text=${encodeURIComponent(movie.title)}`}
                                            alt={movie.title}
                                            className="w-full h-full object-cover rounded-t-sm"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            exit={{ opacity: 0 }}
                                            onError={(e) => {
                                                e.target.src = `https://placehold.co/400x600/9ca3af/ffffff?text=${encodeURIComponent(movie.title)}`;
                                            }}
                                        />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center overflow-hidden">
                                            <span className="text-white/70 font-vt323 text-lg -rotate-90 whitespace-nowrap tracking-widest">
                                                LUMIERE
                                            </span>
                                        </div>
                                    )}
                                </AnimatePresence>
                                {/* VHS texture lines */}
                                {(hoveredIndex !== index && !movie.showPoster) && (
                                    <div className="absolute inset-0">
                                        <div className="absolute top-[30%] left-0 w-full h-[2px] bg-white/5" />
                                        <div className="absolute top-[65%] left-0 w-full h-[1px] bg-white/10" />
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

const VCRConsole = ({ inputValue, setInputValue, hoveredMovieTitle }) => (
    <div className="bg-retro-gray p-4 rounded-lg shadow-md border-b-4 border-retro-dark-gray/50 h-[340px] flex flex-col justify-center">
        <div className="bg-black p-2">
            <input
                type="text"
                value={hoveredMovieTitle ?? inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={hoveredMovieTitle ? '' : 'insert movie'}
                readOnly={!!hoveredMovieTitle}
                className="w-full bg-transparent text-retro-cyan font-vt323 text-2xl focus:outline-none placeholder-retro-cyan/50"
            />
        </div>
        <div className="flex justify-between mt-2">
            <div className="flex space-x-2">
                <div className="w-8 h-5 bg-retro-dark-gray rounded-sm"/>
                <div className="w-8 h-5 bg-retro-dark-gray rounded-sm"/>
            </div>
            <div className="flex space-x-2">
                <div className="w-5 h-5 bg-retro-dark-gray rounded-sm"/>
                <div className="w-5 h-5 bg-retro-dark-gray rounded-sm"/>
            </div>
        </div>
    </div>
);

const CRTScreen = ({ movie, hoveredIndex, selectedId }) => {
    const { likedMovies, handleLikeToggle } = useFavorites();
    const isLiked = movie ? likedMovies.includes(movie.id) : false;

    const [typedText, setTypedText] = useState('');
    const baseText = selectedId ? `NOW SHOWING: ${movie.title}` : hoveredIndex !== null ? 'click poster to see details' : 'hover over cassette to explore';

    useEffect(() => {
        setTypedText('');
        let i = 0;
        const typingInterval = setInterval(() => {
            if (i < baseText.length) {
                setTypedText(prev => prev + baseText.charAt(i));
                i++;
            } else {
                clearInterval(typingInterval);
            }
        }, 30);
        return () => clearInterval(typingInterval);
    }, [baseText]);

    return (
        <div className="bg-black p-1 rounded-lg">
             <div className="bg-retro-screen-blue h-[340px] p-4 font-vt323 text-retro-cyan text-2xl border-2 border-black">
                <AnimatePresence mode="wait">
                    {movie && selectedId === movie.id ? (
                        <motion.div key={movie.id} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}>
                            <div className="flex justify-between items-start">
                                <h2 className="text-4xl">{movie.title} <span className="text-retro-cyan/70">{movie.year}</span></h2>
                                <p className="text-4xl text-retro-yellow">{movie.rating}</p>
                            </div>
                            <p className="text-lg text-retro-cyan/80">dir. by {movie.director} • {movie.cast.join(', ')}</p>
                            <div className="flex space-x-2 my-2">
                                {movie.genres.map(g => <span key={g} className="text-sm bg-retro-blue text-white px-2 py-1">{g}</span>)}
                            </div>
                            <p className="text-xl leading-tight my-2">{movie.synopsis}</p>
                             <div className="flex justify-between items-center mt-3">
                                <span className="font-bold text-retro-red border border-retro-red px-2 py-1 text-lg">{movie.streaming}</span>
                                <motion.button whileHover={{ scale: 1.2 }} whileTap={{ scale: 0.9 }} onClick={() => handleLikeToggle(movie.id)}>
                                    <Heart 
                                        className={`transition-colors duration-300 ${isLiked ? 'text-retro-red' : 'text-retro-cyan/30'}`}
                                        fill={isLiked ? 'currentColor' : 'none'}
                                        strokeWidth={isLiked ? 2 : 1.5}
                                        size={32} 
                                    />
                                </motion.button>
                            </div>
                        </motion.div>
                    ) : (
                         <motion.p key={typedText} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}>
                            {typedText}<span className="animate-ping">_</span>
                        </motion.p>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

// --- Main Page Component ---

const RecommendationsPage = () => {
    const [hoveredIndex, setHoveredIndex] = useState(null);
    const [selectedId, setSelectedId] = useState(null);
    const [inputValue, setInputValue] = useState('');
    const [isInitialLoad, setIsInitialLoad] = useState(true);
    const [tilts, setTilts] = useState([]);
    const [movies, setMovies] = useState([]);
    const navigate = useNavigate();
    
    const { selectedTags, calibrationSettings, recommendationStatus, setRecommendationLoading, setRecommendationError, clearRecommendationStatus, getApiFilters, getTagIds } = useUserPreferences();
    const { isConnected } = useApi();

    // Fetch recommendations from API using user preferences
    useEffect(() => {
        const fetchRecommendations = async () => {
            try {
                setRecommendationLoading(true, 'Analyzing your cinematic preferences...');
                
                console.log('🎯 Fetching tag-based recommendations with:', {
                    tags: selectedTags,
                    calibrationSettings
                });

                // Use the new tag-based recommendation algorithm
                if (selectedTags.length > 0) {
                    try {
                        const response = await apiService.getTagBasedRecommendations(
                            selectedTags,
                            calibrationSettings,
                            null, // userMovies - would be loaded from user's movie history
                            20
                        );
                        
                        if (response && response.recommendations) {
                            // Transform the API response to match our frontend format
                            const transformedMovies = response.recommendations.map(movie => ({
                                id: movie.tmdb_id,
                                title: movie.title,
                                year: movie.release_date?.substring(0, 4) || 'Unknown',
                                director: 'Unknown', // Would need to be extracted from movie details
                                cast: [], // Would need to be extracted from movie details
                                runtime: `${movie.runtime || 0} mins`,
                                genres: movie.genres || [],
                                rating: `${movie.vote_average?.toFixed(1) || 'N/A'}/10`,
                                synopsis: movie.overview || 'No synopsis available.',
                                streaming: getRandomStreamingService(),
                                poster: movie.poster_path ? apiService.getMoviePosterUrl(movie.poster_path) : null,
                                score: movie.final_score || 0,
                                similarity_score: movie.similarity_score || 0,
                                familiarity_score: movie.familiarity_score || 0,
                                source_tags: movie.source_tags || [],
                                reasons: movie.source_tags || []
                            }));
                            
                            setMovies(transformedMovies);
                            setRecommendationLoading(false, `Found ${transformedMovies.length} perfect matches based on your ${selectedTags.length} selected tags!`);
                            
                            console.log('✅ Tag-based recommendations loaded:', transformedMovies.length, 'movies');
                            console.log('📊 Processing time:', response.processing_time, 'seconds');
                            console.log('🎭 User profile summary:', response.user_profile_summary);
                        } else {
                            throw new Error('No recommendations returned from tag-based API');
                        }
                    } catch (tagError) {
                        console.warn('Tag-based recommendations failed, falling back to discovery:', tagError);
                        
                        // Fallback to discovery recommendations
                        setRecommendationLoading(true, 'Exploring new discoveries...');
                        const discoveryResponse = await apiService.getDiscoveryRecommendations({
                            count: 20
                        });
                        
                        if (discoveryResponse && discoveryResponse.recommendations) {
                            const transformedMovies = discoveryResponse.recommendations.map(movie => ({
                                id: movie.id,
                                title: movie.title,
                                year: movie.year?.toString() || 'Unknown',
                                director: movie.directors?.[0] || 'Unknown',
                                cast: movie.cast?.slice(0, 3) || [],
                                runtime: `${movie.runtime || 0} mins`,
                                genres: movie.genres || [],
                                rating: `${movie.vote_average?.toFixed(1) || 'N/A'}/10`,
                                synopsis: movie.overview || 'No synopsis available.',
                                streaming: getRandomStreamingService(),
                                poster: movie.poster_path ? apiService.getMoviePosterUrl(movie.poster_path) : null,
                                score: movie.score || 0,
                                popularity: movie.popularity || 0,
                                reasons: movie.reasons || []
                            }));
                            
                            setMovies(transformedMovies);
                            setRecommendationLoading(false, `Found ${transformedMovies.length} amazing discoveries!`);
                            
                            console.log('✅ Discovery recommendations loaded:', transformedMovies.length, 'movies');
                        } else {
                            throw new Error('Discovery recommendations also failed');
                        }
                    }
                } else {
                    // No tags selected, use discovery recommendations
                    setRecommendationLoading(true, 'Exploring new discoveries...');
                    const discoveryResponse = await apiService.getDiscoveryRecommendations({
                        count: 20
                    });
                    
                    if (discoveryResponse && discoveryResponse.recommendations) {
                        const transformedMovies = discoveryResponse.recommendations.map(movie => ({
                            id: movie.id,
                            title: movie.title,
                            year: movie.year?.toString() || 'Unknown',
                            director: movie.directors?.[0] || 'Unknown',
                            cast: movie.cast?.slice(0, 3) || [],
                            runtime: `${movie.runtime || 0} mins`,
                            genres: movie.genres || [],
                            rating: `${movie.vote_average?.toFixed(1) || 'N/A'}/10`,
                            synopsis: movie.overview || 'No synopsis available.',
                            streaming: getRandomStreamingService(),
                            poster: movie.poster_path ? apiService.getMoviePosterUrl(movie.poster_path) : null,
                            score: movie.score || 0,
                            popularity: movie.popularity || 0,
                            reasons: movie.reasons || []
                        }));
                        
                        setMovies(transformedMovies);
                        setRecommendationLoading(false, `Found ${transformedMovies.length} amazing discoveries!`);
                        
                        console.log('✅ Discovery recommendations loaded:', transformedMovies.length, 'movies');
                    } else {
                        // Final fallback to static data
                        setRecommendationLoading(true, 'Loading curated selections...');
                        const fallbackMovies = getFallbackMovies();
                        setMovies(fallbackMovies);
                        setRecommendationLoading(false, `Loaded ${fallbackMovies.length} curated films`);
                        
                        console.log('✅ Fallback movies loaded:', fallbackMovies.length, 'movies');
                    }
                }
            } catch (error) {
                console.error('Failed to fetch recommendations:', error);
                setRecommendationError('Failed to load recommendations. Using curated selections.');
                setMovies(getFallbackMovies());
            }
        };

        if (isConnected) {
            fetchRecommendations();
        } else {
            setRecommendationError('API not connected. Using demo data.');
            setMovies(getFallbackMovies());
        }
    }, [isConnected, selectedTags, calibrationSettings]);

    useEffect(() => {
        const timer = setTimeout(() => setIsInitialLoad(false), 2000); 
        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        setTilts(movies.map(() => Math.random() * 6 - 3));
    }, [movies]);
    
    const selectedMovie = movies.find(m => m.id === selectedId);

    const handleSelectMovie = (movie) => {
        console.log('Selecting movie:', movie.id, movie.title);
        setSelectedId(prevId => {
            const newId = prevId === movie.id ? null : movie.id;
            console.log('Selected ID changed from', prevId, 'to', newId);
            return newId;
        });
    };
    
    const filteredMovies = movies.filter(movie =>
        movie.title.toLowerCase().includes(inputValue.toLowerCase())
    ).slice(0, 20).map(movie => {
        const showPoster = movie.id === selectedId;
        console.log(`Movie ${movie.id} (${movie.title}): showPoster=${showPoster}, selectedId=${selectedId}`);
        return { ...movie, showPoster };
    });

    const hoveredMovie = hoveredIndex !== null ? filteredMovies[hoveredIndex] : null;

    // Helper functions
    const getRandomStreamingService = () => {
        const services = ['NETFLIX', 'HBO MAX', 'HULU', 'DISNEY+', 'AMAZON PRIME', 'APPLE TV+'];
        return services[Math.floor(Math.random() * services.length)];
    };

    const getFallbackMovies = () => {
        return [
            {
                id: 1,
                title: "Avatar",
                year: "2009",
                director: "James Cameron",
                cast: ["Zoe Saldaña", "Sigourney Weaver", "Stephen Lang"],
                runtime: "162 mins",
                genres: ["Science Fiction", "Fantasy"],
                rating: "7.9/10",
                synopsis: "On the lush alien world of Pandora, ex-Marine Jake Sully is thrust into an interstellar conflict between greedy human colonizers and the indigenous Na'vi.",
                streaming: "NETFLIX",
                poster: "https://placehold.co/400x600/9ca3af/ffffff?text=Avatar",
                score: 0.85,
                popularity: 0.9,
                reasons: ["Epic scale", "Visual effects", "Environmental themes"]
            },
            {
                id: 2,
                title: "Inception",
                year: "2010",
                director: "Christopher Nolan",
                cast: ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"],
                runtime: "148 mins",
                genres: ["Sci-Fi", "Thriller"],
                rating: "8.8/10",
                synopsis: "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                streaming: "HBO MAX",
                poster: "https://placehold.co/400x600/9ca3af/ffffff?text=Inception",
                score: 0.92,
                popularity: 0.88,
                reasons: ["Mind-bending plot", "Complex narrative", "Visual innovation"]
            },
            {
                id: 3,
                title: "Parasite",
                year: "2019",
                director: "Bong Joon Ho",
                cast: ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong"],
                runtime: "132 mins",
                genres: ["Thriller", "Comedy", "Drama"],
                rating: "8.6/10",
                synopsis: "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
                streaming: "HULU",
                poster: "https://placehold.co/400x600/9ca3af/ffffff?text=Parasite",
                score: 0.89,
                popularity: 0.85,
                reasons: ["Social commentary", "Dark comedy", "Unpredictable plot"]
            }
        ];
    };
 
    return (
        <div className="bg-retro-bg min-h-screen w-full flex flex-col items-center justify-between p-4 sm:p-8">
            <StatusIndicator status={recommendationStatus} />
            
            <div className="w-full max-w-7xl">
                <div className="relative text-center">
                    <h1 className="text-6xl text-retro-blue text-center font-broadway my-4 tracking-wider [text-shadow:_2px_2px_0px_#F0EAD6,_4px_4px_0px_#000]">
                        LUMIERE'S PICKS
                    </h1>
                    <motion.button 
                        onClick={() => navigate('/favorites')}
                        className="absolute top-1/2 -translate-y-1/2 right-0 text-retro-red p-2"
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                    >
                        <Heart size={32} fill="currentColor" />
                    </motion.button>
                </div>
                
                <CassetteShelf
                    movies={filteredMovies}
                    hoveredIndex={hoveredIndex}
                    setHoveredIndex={setHoveredIndex}
                    onSelectMovie={handleSelectMovie}
                    isInitialLoad={isInitialLoad}
                    tilts={tilts}
                />
                <div className="w-full mt-8 grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                    <VCRConsole 
                        inputValue={inputValue}
                        setInputValue={setInputValue}
                        hoveredMovieTitle={hoveredMovie ? hoveredMovie.title : null}
                    />
                    <CRTScreen 
                        movie={selectedMovie}
                        hoveredIndex={hoveredIndex}
                        selectedId={selectedId}
                    />
                </div>
            </div>
            <button onClick={() => navigate('/tags')} className="mt-8 text-retro-red underline font-sans text-lg">
                Start Over
            </button>
        </div>
    );
};
 
export default RecommendationsPage;
