import React, { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useUserPreferences } from '../contexts/UserPreferencesContext';
import { keywords_default } from '../keywordsData';
import keywordService from '../services/keywordService';

// Import all paper images
function importAll(r) {
    return r.keys().map(r);
}
const paperImages = importAll(require.context('../assets/papers', false, /\.(png|jpe?g|svg)$/));

const PageWrapper = ({ children, className = '' }) => (
    <div className={`w-full min-h-screen font-serif transition-opacity duration-1000 flex flex-col items-center p-8 sm:p-12 relative ${className}`}>
        {children}
    </div>
);

const PaperTag = ({ tag, onClick, isSelected, style }) => {
    const [isHovered, setIsHovered] = useState(false);
    const shadow = 'drop-shadow(5px 10px 7.7px rgba(0,0,0,0.6))';
    const hoverShadow = 'drop-shadow(5px 10px 10px rgba(0,0,0,0.7))';

    return (
        <motion.button
            layoutId={tag}
            onClick={() => onClick(tag)}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className="relative focus:outline-none bg-cover bg-center"
            whileHover={{ y: -5, scale: 1.05, zIndex: 150 }}
            whileTap={{ scale: 0.95 }}
            style={{
                ...style,
                position: 'absolute',
                left: `${style.left}px`,
                top: `${style.top}px`,
                backgroundImage: `url(${style.image})`,
                filter: isSelected || isHovered ? hoverShadow : shadow,
            }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            animate={{
                rotate: style.rotate,
                scale: [1, 1.01, 1],
            }}
        >
            <div
                className="absolute inset-0 w-full h-full pointer-events-none"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 500 500' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.5' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
                    opacity: 0.15,
                }}
            />
            <motion.div
                className="absolute inset-0 w-full h-full pointer-events-none"
                style={{
                    backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 50%)',
                    mixBlendMode: 'overlay',
                    opacity: isHovered ? 1 : 0,
                    transition: 'opacity 0.3s ease',
                }}
            />
            <motion.span
                className={`absolute inset-0 flex items-center justify-center font-handwriting text-xl sm:text-2xl p-2 text-center transition-colors ${isHovered || isSelected ? 'text-gray-900' : 'text-gray-700'}`}
                style={{
                    wordBreak: 'break-word',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'normal',
                    maxWidth: '100%',
                    maxHeight: '100%',
                }}
                animate={{ rotate: isHovered ? (Math.random() * 4 - 2) : 0 }}
            >
                {tag}
            </motion.span>
        </motion.button>
    );
};

const SearchResult = ({ result, onClick, isSelected }) => (
    <motion.div
        className={`p-3 mb-2 rounded-lg cursor-pointer transition-all ${
            isSelected 
                ? 'bg-white text-lumiere-blue shadow-lg' 
                : 'bg-white/10 text-white hover:bg-white/20'
        }`}
        onClick={() => onClick(result)}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
    >
        <div className="font-work-sans text-sm">{result.keyword}</div>
    </motion.div>
);

const TagSelectionPage = () => {
    // Preload images
    useEffect(() => {
        paperImages.forEach((image) => {
            new Image().src = image;
        });
    }, []);
    
    const navigate = useNavigate();
    const { selectedTags, addTag, removeTag, tagCount, maxTags } = useUserPreferences();

    // Search state
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [showSearchResults, setShowSearchResults] = useState(false);

    const tagPositions = useMemo(() => {
        const usedPositions = [];
        const containerWidth = 1200;
        const containerHeight = window.innerHeight * 3;
        const minSpacing = 200; // Maximized minimum spacing between tags
        
        function generateNonOverlappingPosition(width, height) {
            let maxAttempts = 200; // Increased attempts for better positioning
            while (maxAttempts-- > 0) {
                const top = Math.random() * (containerHeight - height);
                const left = Math.random() * (containerWidth - width);
                const newPos = { left, top, width, height };
                
                // Check for overlap with existing positions
                const isOverlapping = usedPositions.some(pos => {
                    const horizontalOverlap = newPos.left < pos.left + pos.width + minSpacing &&
                                            newPos.left + newPos.width + minSpacing > pos.left;
                    const verticalOverlap = newPos.top < pos.top + pos.height + minSpacing &&
                                          newPos.top + newPos.height + minSpacing > pos.top;
                    return horizontalOverlap && verticalOverlap;
                });

                if (!isOverlapping) {
                    usedPositions.push(newPos);
                    return { top, left };
                }
            }
            
            // Fallback: find a position with minimal overlap
            let bestPosition = { top: Math.random() * (containerHeight - height), left: Math.random() * (containerWidth - width) };
            let minOverlap = Infinity;
            
            for (let attempt = 0; attempt < 50; attempt++) {
                const testTop = Math.random() * (containerHeight - height);
                const testLeft = Math.random() * (containerWidth - width);
                const testPos = { left: testLeft, top: testTop, width, height };
                
                let totalOverlap = 0;
                usedPositions.forEach(pos => {
                    const horizontalOverlap = Math.max(0, Math.min(testPos.left + testPos.width, pos.left + pos.width) - Math.max(testPos.left, pos.left));
                    const verticalOverlap = Math.max(0, Math.min(testPos.top + testPos.height, pos.top + pos.height) - Math.max(testPos.top, pos.top));
                    totalOverlap += horizontalOverlap * verticalOverlap;
                });
                
                if (totalOverlap < minOverlap) {
                    minOverlap = totalOverlap;
                    bestPosition = { top: testTop, left: testLeft };
                }
            }
            
            usedPositions.push({ ...bestPosition, width, height });
            return bestPosition;
        }

        return keywords_default.map((tag, i) => {
            const origins = ['top left', 'top right', 'bottom left', 'bottom right'];
            const image = paperImages[Math.floor(Math.random() * paperImages.length)];
            const width = 180 + Math.random() * 70;
            const height = (width / 2.5);
            const { top, left } = generateNonOverlappingPosition(width, height);
            return {
                id: tag,
                top: top,
                left: left,
                rotate: Math.random() * 12 - 6,
                width: width,
                height: height,
                image: image,
                zIndex: i,
                transformOrigin: origins[Math.floor(Math.random() * origins.length)],
            };
        });
    }, []);

    // Helper to generate a PaperTag style for a new keyword
    const generatePaperTagStyle = (tag) => {
        const origins = ['top left', 'top right', 'bottom left', 'bottom right'];
        const image = paperImages[Math.floor(Math.random() * paperImages.length)];
        const width = 180 + Math.random() * 70;
        const height = (width / 2.5);
        return {
            id: tag,
            top: 0,
            left: 0,
            rotate: Math.random() * 12 - 6,
            width: width,
            height: height,
            image: image,
            zIndex: 999,
            transformOrigin: origins[Math.floor(Math.random() * origins.length)],
        };
    };

    const handleTagClick = (tag) => {
        if (selectedTags.includes(tag)) {
            removeTag(tag);
        } else if (tagCount < maxTags) {
            addTag(tag);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            setSearchResults([]);
            setShowSearchResults(false);
            return;
        }

        setIsSearching(true);
        try {
            const results = await keywordService.searchKeywords(searchQuery, 10);
            setSearchResults(results);
            setShowSearchResults(true);
        } catch (error) {
            console.error('Search failed:', error);
            setSearchResults([]);
        } finally {
            setIsSearching(false);
        }
    };

    const handleSearchResultClick = (result) => {
        const keyword = result.keyword;
        if (!selectedTags.includes(keyword) && tagCount < maxTags) {
            addTag(keyword);
        }
        setSearchQuery('');
        setShowSearchResults(false);
    };

    const handleSearchInputChange = (e) => {
        const value = e.target.value;
        setSearchQuery(value);
        if (value.trim() === '') {
            setShowSearchResults(false);
        }
    };

    const handleSearchKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };
    
    const unselectedTags = tagPositions.filter(pos => !selectedTags.includes(pos.id));

    return (
        <div style={{ backgroundColor: '#426DF5', minHeight: '100vh', position: 'relative' }}>
            <LayoutGroup>
                <PageWrapper>
                    {/* Top Bar: Search | Heading */}
                    <div className="w-full flex flex-row items-start justify-between gap-8 mb-12 mt-4 px-2 sm:px-8">
                        {/* Main Heading only */}
                        <div className="flex-1 flex flex-col items-center justify-center min-w-0">
                            <h1 className="text-3xl sm:text-4xl md:text-5xl text-white font-didot text-center whitespace-normal break-words">
                                Compose your cinematic moodboard.
                            </h1>
                        </div>
                    </div>
                    {/* Main Content */}
                    <div className="w-full max-w-full mx-auto flex px-12 pt-8">
                        {/* Left column: tag count, search, selected tags */}
                        <div className="w-1/5 pr-8 flex flex-col gap-8 items-start">
                            {/* Tag Count in top left corner */}
                            <div className="mt-0 mb-2 self-start">
                                <h2 className="text-xl sm:text-2xl text-white font-work-sans">choose up to</h2>
                                <p className="text-3xl sm:text-4xl text-white font-bold font-work-sans">{maxTags} tags</p>
                            </div>
                            {/* Search Panel below tag count */}
                            <div className="w-full max-w-[220px]">
                                <h2 className="text-2xl text-white font-didot mb-2">Search Keywords</h2>
                                <div className="relative">
                                    <div className="flex mb-2 w-full">
                                        <input
                                            type="text"
                                            value={searchQuery}
                                            onChange={handleSearchInputChange}
                                            onKeyPress={handleSearchKeyPress}
                                            placeholder="Search keywords..."
                                            className="w-2/3 px-3 py-2 rounded-l-lg text-gray-800 font-work-sans focus:outline-none focus:ring-2 focus:ring-white/50"
                                        />
                                        <button
                                            onClick={handleSearch}
                                            disabled={isSearching}
                                            className="w-1/3 px-2 py-2 bg-white text-lumiere-blue font-bold rounded-r-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
                                        >
                                            {isSearching ? '...' : 'Search'}
                                        </button>
                                    </div>
                                    {showSearchResults && (
                                        <motion.div
                                            className="bg-white/10 backdrop-blur-sm rounded-lg p-4 max-h-96 overflow-y-auto border border-white/20"
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: 10 }}
                                        >
                                            {searchResults.length > 0 ? (
                                                searchResults.map((result, index) => (
                                                    <SearchResult
                                                        key={result.id || index}
                                                        result={result}
                                                        onClick={handleSearchResultClick}
                                                        isSelected={selectedTags.includes(result.keyword)}
                                                    />
                                                ))
                                            ) : (
                                                <div className="text-white/70 font-work-sans text-sm">
                                                    No keywords found
                                                </div>
                                            )}
                                        </motion.div>
                                    )}
                                </div>
                            </div>
                            {/* Selected Tags below search */}
                            <div className="w-full">
                                <h2 className="text-4xl text-white font-didot mb-8">Selected Tags</h2>
                                <div className="relative">
                                    <AnimatePresence>
                                        {selectedTags.map((tag, index) => {
                                            // Try to find style in tagPositions, else generate one for new tags
                                            const style = tagPositions.find(p => p.id === tag) || generatePaperTagStyle(tag);
                                            return <PaperTag key={tag} tag={tag} onClick={handleTagClick} isSelected={true} style={{ ...style, left: 0, top: index * 90, zIndex: 100+index }}/>
                                        })}
                                    </AnimatePresence>
                                </div>
                            </div>
                        </div>
                        {/* Divider */}
                        <div className="w-px bg-black/20 my-8"></div>
                        {/* Right column: tag cloud only */}
                        <div className="w-4/5 pl-8">
                            <div className="relative w-full" style={{ height: `${3 * window.innerHeight}px` }}>
                                <AnimatePresence>
                                    {unselectedTags.map(pos => (
                                        <PaperTag
                                            key={pos.id}
                                            tag={pos.id}
                                            onClick={handleTagClick}
                                            isSelected={false}
                                            style={pos}
                                        />
                                    ))}
                                </AnimatePresence>
                            </div>
                        </div>
                    </div>

                    <AnimatePresence>
                        {selectedTags.length > 0 && (
                            <motion.button
                                onClick={() => navigate('/calibration')}
                                className="fixed top-12 right-16 bg-white text-lumiere-blue font-bold text-xl px-12 py-3 rounded-lg shadow-lg hover:bg-gray-100 transition-all transform hover:scale-105 border-2 border-black z-[9999]"
                                initial={{ opacity: 0, y: -20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                style={{ zIndex: 9999 }}
                            >
                                Next
                            </motion.button>
                        )}
                    </AnimatePresence>
                </PageWrapper>
            </LayoutGroup>
            <p className="fixed bottom-4 right-4 text-xs text-white/50 font-work-sans z-20">designed by dan mccartin 2025</p>
        </div>
    );
};

export default TagSelectionPage; 