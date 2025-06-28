// src/components/RecommendationsPage.jsx
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useFavorites } from '../contexts/FavoritesContext';
import { useUserPreferences } from '../contexts/UserPreferencesContext';
import { useApi } from '../contexts/ApiContext';
import apiService from '../services/api';
import LoadingPage from './LoadingPage';

// --- PageWrapper Component ---
const PageWrapper = ({ children, className = '' }) => (
    <div className={`w-full min-h-screen font-vt323 transition-opacity duration-1000 flex flex-col items-center justify-center p-4 sm:p-8 relative overflow-hidden ${className}`}>
        {children}
        <p className="absolute bottom-4 right-4 text-xs text-lumiere-loading-text/50">designed by dan mccartin 2025</p>
    </div>
);

// --- Sub-Components ---

const CassetteShelf = ({ movies, hoveredIndex, setHoveredIndex, onSelectMovie, isInitialLoad, tilts, selectedId }) => {
    return (
        <div className="w-full bg-retro-blue p-2 shadow-lg">
            <div className="bg-retro-orange w-full h-48 flex justify-start items-end px-4 space-x-2 overflow-x-auto scrollbar-hide">
                {movies.map((movie, index) => {
                    const isSelected = movie.id === selectedId;
                    const isHovered = hoveredIndex === index;
                    return (
                    <motion.div
                        key={movie.id}
                        className="relative h-40 rounded-t-md cursor-pointer flex-shrink-0"
                        style={{ 
                            transformOrigin: 'bottom center',
                                zIndex: isSelected ? 20 : isHovered ? 10 : index,
                        }}
                        onMouseEnter={() => setHoveredIndex(index)}
                        onMouseLeave={() => setHoveredIndex(null)}
                        onClick={() => onSelectMovie(movie)}
                        initial={{ y: -200, opacity: 0, width: '48px' }}
                        animate={{ 
                                y: isSelected || isHovered ? -15 : 0,
                            opacity: 1,
                                rotate: isSelected || isHovered ? 0 : (tilts[index] || 0),
                                width: isSelected || isHovered ? '106px' : '48px'
                        }}
                        transition={{ type: 'spring', stiffness: 150, damping: 20, delay: isInitialLoad ? index * 0.05 : 0 }}
                    >
                        <div className="w-full h-full bg-[#333] rounded-t-md p-0.5 border-t border-l border-r border-gray-400/30 shadow-inner">
                            <div className="relative w-full h-full bg-black rounded-sm overflow-hidden">
                                <AnimatePresence>
                                        {isSelected || isHovered ? (
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
                                    {!(isSelected || isHovered) && (
                                    <div className="absolute inset-0">
                                        <div className="absolute top-[30%] left-0 w-full h-[2px] bg-white/5" />
                                        <div className="absolute top-[65%] left-0 w-full h-[1px] bg-white/10" />
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                    );
                })}
            </div>
        </div>
    );
};

const VCRConsole = ({ inputValue, setInputValue, hoveredMovie }) => {
    // Extract director and cast if hoveredMovie is present
    let director = 'Unknown';
    if (hoveredMovie?.credits?.crew) {
        const found = hoveredMovie.credits.crew.find(c => c.job === 'Director');
        director = found ? found.name : (hoveredMovie.director || 'Unknown');
    } else if (hoveredMovie?.director) {
        director = hoveredMovie.director;
    }
    const cast = hoveredMovie?.cast || (hoveredMovie?.credits?.cast?.slice(0, 3).map(actor => actor.name)) || [];
    return (
    <div className="bg-retro-gray p-4 rounded-lg shadow-md border-b-4 border-retro-dark-gray/50 h-[340px] flex flex-col justify-center">
        <div className="bg-black p-2">
            <input
                type="text"
                    value={hoveredMovie ? hoveredMovie.title : inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                    placeholder={hoveredMovie ? '' : 'insert movie'}
                    readOnly={!!hoveredMovie}
                className="w-full bg-transparent text-retro-cyan font-vt323 text-2xl focus:outline-none placeholder-retro-cyan/50"
            />
        </div>
            {/* Show director and cast if hoveredMovie is present */}
            {hoveredMovie && (
                <div className="mt-2 text-retro-cyan/80 font-vt323 text-base bg-black/40 rounded p-2">
                    <div>
                        <span>dir. <span className="font-bold text-retro-cyan/90">{director || 'Unknown'}</span></span>
                    </div>
                    {cast.length > 0 && (
                        <div className="mt-1 text-retro-cyan/60">
                            cast: {cast.join(', ')}
                        </div>
                    )}
                </div>
            )}
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
};

const CRTScreen = ({ movie, hoveredIndex, selectedId }) => {
    const { likedMovies, handleLikeToggle } = useFavorites();
    const isLiked = movie ? likedMovies.some(m => m.id === movie.id) : false;

    const [typedText, setTypedText] = useState('');
    const baseText = selectedId && movie ? `NOW SHOWING: ${movie.title}` : hoveredIndex !== null ? 'click poster to see details' : 'hover over cassette to explore';

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

    // If no movie, just show the idle/typing state
    if (!movie) {
        return (
            <div className="bg-black p-1 rounded-lg">
                <div className="bg-retro-screen-blue h-[340px] p-4 font-vt323 text-retro-cyan text-2xl border-2 border-black flex items-center justify-center">
                    <motion.p key={typedText} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}>
                        {typedText}<span className="animate-ping">_</span>
                    </motion.p>
                </div>
            </div>
        );
    }

    // Extract director and cast from movie data
    const getDirector = (movie) => {
        // Prefer credits if available
        if (movie.credits?.crew) {
            const director = movie.credits.crew.find(c => c.job === 'Director');
            return director ? director.name : (movie.director || 'Unknown');
        }
        return movie.director || 'Unknown';
    };

    const getCast = (movie) => {
        // Prefer credits if available
        if (movie.credits?.cast) {
            return movie.credits.cast.slice(0, 3).map(actor => actor.name);
        }
        return movie.cast && movie.cast.length > 0 ? movie.cast : [];
    };

    const director = movie ? getDirector(movie) : '';
    const cast = movie ? getCast(movie) : [];

    return (
        <div className="bg-black p-1 rounded-lg relative overflow-hidden">
            {/* CRT scanlines and glow */}
            <div className="absolute inset-0 pointer-events-none z-10">
                {/* Scanlines */}
                <div className="h-full w-full opacity-20" style={{background: 'repeating-linear-gradient(0deg, transparent, transparent 6px, #00fff7 7px, transparent 8px)'}} />
                {/* Glow */}
                <div className="absolute inset-0" style={{boxShadow: '0 0 32px 8px #00fff7, 0 0 8px 2px #fff inset', opacity: 0.15}} />
            </div>
            <div className="bg-retro-screen-blue h-[340px] p-4 font-vt323 text-retro-cyan text-2xl border-2 border-black relative z-20">
                <AnimatePresence mode="wait">
                    {movie && selectedId === movie.id ? (
                        <motion.div key={movie.id} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}>
                            <div className="flex justify-between items-start">
                                <h2 className="text-4xl">{movie.title} <span className="text-retro-cyan/70">{movie.year}</span></h2>
                                <p className="text-4xl text-retro-yellow">{movie.rating}</p>
                            </div>
                            {/* SYNOPSIS BOX: director/cast + synopsis, scrollable, retro scrollbar, no horizontal scroll */}
                            <div className="relative w-full max-h-32 min-h-[4rem] overflow-y-auto overflow-x-hidden bg-black/30 rounded-md p-2 mt-2 mb-2 retro-synopsis-scroll">
                                <div className="mb-1 text-base text-retro-cyan/70 font-vt323">
                                    <span>dir. by <span className="font-bold text-retro-cyan/90">{director}</span></span>
                                    {cast.length > 0 && (
                                        <span> &nbsp;•&nbsp; <span className="text-retro-cyan/60">{cast.join(', ')}</span></span>
                                    )}
                                </div>
                                <p className="text-base md:text-lg text-retro-cyan/80 leading-tight whitespace-pre-line break-words">
                                    {movie.synopsis}
                                </p>
                            </div>
                            <div className="flex justify-between items-center mt-3">
                                <span className="font-bold text-retro-red border border-retro-red px-2 py-1 text-lg">{movie.streaming}</span>
                                <motion.button whileHover={{ scale: 1.2 }} whileTap={{ scale: 0.9 }} onClick={() => handleLikeToggle(movie)}>
                                    <Heart 
                                        className={`transition-colors duration-300 ${isLiked ? 'text-pink-500' : 'text-gray-400'}`}
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

// --- Matrix Loading Steps for Recommendations ---
const MatrixLoading = ({ onFinish, apiData }) => {
    const [step, setStep] = useState(0);
    
    console.log('🎬 MatrixLoading received apiData:', apiData);
    
    // Generate dynamic loading steps based on real API data
    const generateLoadingSteps = () => {
        if (!apiData) {
            return [
                '[ INITIALIZING RECOMMENDER SYSTEM v1.0 ]',
                '> Boot sequence complete...  ',
                '> Beginning tag-based matrix traversal...',
                '',
                '[ BUILDING USER PROFILE ]',
                '> 🎭 Detected: 0 known actors  ',
                '> 🧠 Memory: empty slate – fresh canvas',
                '',
                '[ APPLYING FILTERS ]',
                '> 🎬 Years: 1980-2010  ',
                '> 🕰️ Runtime: 90–150 mins  ',
                '> 📈 Sort by: popularity descending  ',
                '> 🎯 Total Filters Applied: 5  ',
                '',
                '[ TAG SCAN: INITIATED ]',
                '> 🔍 Scanning tags...  ',
                '',
                '[ 📦 SUPERLIST CREATED ]',
                '> Total unique films: 0  ',
                '> 🧹 Removing watched entries... 0 purged  ',
                '> 🎞️ Remaining: 0 candidates',
                '',
                '[ 📊 FAMILIARITY MATRIX ACTIVATED ]',
                '> Preference level: 5  ',
                '> Filtering for balance... ✅ 0 valid entries',
                '',
                '[ 🧬 SIMILARITY ENGINE ENGAGED ]',
                '> Cross-referencing profiles... 🔄  ',
                '> Final synthesis complete.',
                '',
                '[ ✅ RECOMMENDATION READY ]',
                '> 🎬 Top 0 film recommendations generated',
            ];
        }
        
        const { selected_tags, tag_results, total_movies, watched_removed, remaining_movies, familiarity_level, known_actors } = apiData;
        
        // Generate tag scan steps dynamically
        const tagScanSteps = selected_tags.map(tag => {
            const count = tag_results[tag] || 0;
            const dots = '.'.repeat(Math.max(10, 20 - tag.length));
            return `> 🔍 Scanning tag: [${tag}] ${dots} ✅ ${count} match${count !== 1 ? 'es' : ''} found  `;
        });
        
        return [
            '[ INITIALIZING RECOMMENDER SYSTEM v1.0 ]',
            '> Boot sequence complete...  ',
            '> Beginning tag-based matrix traversal...',
            '',
            '[ BUILDING USER PROFILE ]',
            `> 🎭 Detected: ${known_actors} known actors  `,
            '> 🧠 Memory: empty slate – fresh canvas',
            '',
            '[ APPLYING FILTERS ]',
            '> 🎬 Years: 1980-2010  ',
            '> 🕰️ Runtime: 90–150 mins  ',
            '> 📈 Sort by: popularity descending  ',
            '> 🎯 Total Filters Applied: 5  ',
            '',
            '[ TAG SCAN: INITIATED ]',
            ...tagScanSteps,
            '',
            '[ 📦 SUPERLIST CREATED ]',
            `> Total unique films: ${total_movies}  `,
            `> 🧹 Removing watched entries... ${watched_removed} purged  `,
            `> 🎞️ Remaining: ${remaining_movies} candidates`,
            '',
            '[ 📊 FAMILIARITY MATRIX ACTIVATED ]',
            `> Preference level: ${familiarity_level}  `,
            `> Filtering for balance... ✅ ${remaining_movies} valid entries`,
            '',
            '[ 🧬 SIMILARITY ENGINE ENGAGED ]',
            '> Cross-referencing profiles... 🔄  ',
            '> Final synthesis complete.',
            '',
            '[ ✅ RECOMMENDATION READY ]',
            `> 🎬 Top ${apiData.recommendations?.length || 0} film recommendations generated`,
        ];
    };
    
    const loadingSteps = generateLoadingSteps();
    
    useEffect(() => {
        if (step < loadingSteps.length - 1) {
            const timer = setTimeout(() => setStep(step + 1), 900);
            return () => clearTimeout(timer);
        } else {
            const timer = setTimeout(() => onFinish(), 1200);
            return () => clearTimeout(timer);
        }
    }, [step, onFinish, loadingSteps.length]);
    
    return (
        <PageWrapper className="bg-lumiere-dark-bg bg-grid-loading items-start">
            <div className="text-lumiere-loading-text text-2xl sm:text-3xl p-4 sm:p-8 min-h-[40vh] flex flex-col justify-center">
                <p className="whitespace-pre animate-fade-in-matrix">{loadingSteps[step]}<span className="animate-pulse">_</span></p>
            </div>
        </PageWrapper>
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
    const location = useLocation();
    
    // Cache tracking
    const hasLoadedRecommendations = useRef(false);
    const lastTagsHash = useRef('');
    const lastCalibrationHash = useRef('');
    const isFetching = useRef(false);
    
    const { selectedTags, calibrationSettings, setRecommendationError, clearRecommendationStatus, getApiFilters, getTagIds } = useUserPreferences();
    const { isConnected } = useApi();
    const { likedMovies = [] } = useFavorites();
    
    // Only show matrix loading when coming from tag selection or calibration
    const shouldShowMatrixLoading = location.state?.from === '/tags' || location.state?.from === '/calibration';
    const [showMatrixLoading, setShowMatrixLoading] = useState(shouldShowMatrixLoading);
    const [apiResponseData, setApiResponseData] = useState(null);

    // Create hash for current tags and calibration settings
    const currentTagsHash = JSON.stringify(selectedTags.sort());
    const currentCalibrationHash = JSON.stringify(calibrationSettings);

    // Fetch recommendations from API using user preferences
    useEffect(() => {
        // Check if we need to fetch recommendations
        const tagsChanged = currentTagsHash !== lastTagsHash.current;
        const calibrationChanged = currentCalibrationHash !== lastCalibrationHash.current;
        const needsFetch = !hasLoadedRecommendations.current || tagsChanged || calibrationChanged;

        if (!needsFetch || isFetching.current) {
            console.log('📋 Using cached recommendations or fetch already in progress');
            return;
        }

        const fetchRecommendations = async () => {
            if (isFetching.current) {
                console.log('🔄 Fetch already in progress, skipping');
                return;
            }
            
            isFetching.current = true;
            
            try {
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
                        
                        // Store API response data for matrix loading screen
                        if (response) {
                            const matrixData = {
                                selected_tags: selectedTags,
                                tag_results: response.tag_results || response.tag_matches || {},
                                total_movies: response.total_movies || response.superlist_count || 0,
                                watched_removed: response.watched_removed || response.filtered_count || 0,
                                remaining_movies: response.remaining_movies || response.final_count || 0,
                                familiarity_level: calibrationSettings.familiarity || 5,
                                known_actors: response.known_actors || response.user_profile?.known_actors || 0,
                                recommendations: response.recommendations || []
                            };
                            setApiResponseData(matrixData);
                        }
                        
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
                                reasons: movie.source_tags || [],
                                credits: movie.credits // <-- Pass credits for director/cast info
                            }));
                            
                            setMovies(transformedMovies);
                            
                            // Update cache tracking
                            hasLoadedRecommendations.current = true;
                            lastTagsHash.current = currentTagsHash;
                            lastCalibrationHash.current = currentCalibrationHash;
                            
                            console.log('✅ Tag-based recommendations loaded:', transformedMovies.length, 'movies');
                            console.log('📊 Processing time:', response.processing_time, 'seconds');
                            console.log('🎭 User profile summary:', response.user_profile_summary);
                        } else {
                            throw new Error('No recommendations returned from tag-based API');
                        }
                    } catch (tagError) {
                        console.warn('Tag-based recommendations failed, falling back to discovery:', tagError);
                        
                        // Fallback to discovery recommendations
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
                                similarity_score: movie.similarity_score || 0,
                                familiarity_score: movie.familiarity_score || 0,
                                source_tags: movie.source_tags || [],
                                reasons: movie.reasons || [],
                                credits: movie.credits || {}
                            }));
                            
                            setMovies(transformedMovies);
                            
                            // Update cache tracking
                            hasLoadedRecommendations.current = true;
                            lastTagsHash.current = currentTagsHash;
                            lastCalibrationHash.current = currentCalibrationHash;
                            
                            console.log('✅ Discovery recommendations loaded:', transformedMovies.length, 'movies');
                        } else {
                            throw new Error('No recommendations returned from discovery API');
                        }
                    }
                } else {
                    // No tags selected, use fallback movies
                    const fallbackMovies = getFallbackMovies();
                    setMovies(fallbackMovies);
                    
                    // Update cache tracking
                    hasLoadedRecommendations.current = true;
                    lastTagsHash.current = currentTagsHash;
                    lastCalibrationHash.current = currentCalibrationHash;
                        
                        console.log('✅ Fallback movies loaded:', fallbackMovies.length, 'movies');
                }
                
                // Clear any previous errors
                clearRecommendationStatus();
                
            } catch (error) {
                console.error('❌ Failed to fetch recommendations:', error);
                setRecommendationError('Failed to load recommendations. Please try again.');
                
                // Use fallback movies on error
                const fallbackMovies = getFallbackMovies();
                setMovies(fallbackMovies);
                
                // Update cache tracking even on error to prevent infinite retries
                hasLoadedRecommendations.current = true;
                lastTagsHash.current = currentTagsHash;
                lastCalibrationHash.current = currentCalibrationHash;
            } finally {
                isFetching.current = false;
            }
        };
        
            fetchRecommendations();
    }, [selectedTags, calibrationSettings, currentTagsHash, currentCalibrationHash, clearRecommendationStatus, setRecommendationError]);

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
        setSelectedId(movie.id);
    };
    
    // Filter out already seen movies (likedMovies)
    const filteredMovies = movies.filter(movie => !likedMovies.includes(movie.id))
        .filter(movie => movie.title.toLowerCase().includes(inputValue.toLowerCase()))
        .slice(0, 20)
        .map(movie => {
            const showPoster = movie.id === selectedId;
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

    // When recommendations are loaded, hide the loading
    useEffect(() => {
        if (movies.length > 0) {
            setShowMatrixLoading(false);
        }
    }, [movies]);

    if (showMatrixLoading) {
        return <MatrixLoading onFinish={() => setShowMatrixLoading(false)} apiData={apiResponseData} />;
    }
 
    return (
        <div className="bg-retro-bg min-h-screen w-full flex flex-col items-center justify-between p-4 sm:p-8">
            <div className="w-full max-w-7xl">
                <div className="relative text-center">
                    <h1 className="text-6xl text-retro-blue text-center font-broadway my-4 tracking-wider [text-shadow:_2px_2px_0px_#F0EAD6,_4px_4px_0px_#000]">
                        LUMIERE'S PICKS
                    </h1>
                    <motion.button 
                        onClick={() => navigate('/favorites', { state: { from: '/recommendations' } })}
                        className="absolute top-1/2 -translate-y-1/2 right-0 text-pink-500 hover:text-pink-700 p-2"
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
                    selectedId={selectedId}
                />
                <div className="w-full mt-8 grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                    <VCRConsole 
                        inputValue={inputValue}
                        setInputValue={setInputValue}
                        hoveredMovie={hoveredMovie}
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
