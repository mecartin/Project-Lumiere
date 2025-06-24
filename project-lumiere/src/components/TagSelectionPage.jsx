// src/components/TagSelectionPage.jsx
import React, { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useUserPreferences } from '../contexts/UserPreferencesContext';
import { emotionTags } from '../data';

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

const TagSelectionPage = () => {
    // Preload images
    useEffect(() => {
        paperImages.forEach((image) => {
            new Image().src = image;
        });
    }, []);
    
    const navigate = useNavigate();
    const { selectedTags, addTag, removeTag, tagCount, maxTags } = useUserPreferences();

    const tagPositions = useMemo(() => {
        const usedPositions = [];
        
        function generateNonOverlappingPosition(width, height) {
            let maxAttempts = 100;
            while (maxAttempts-- > 0) {
                const top = Math.random() * ((window.innerHeight * 3) - height);
                const left = Math.random() * (1200 - width);
                const newPos = { left, top, width, height };
                const isOverlapping = usedPositions.some(pos => (
                    newPos.left < pos.left + pos.width &&
                    newPos.left + newPos.width > pos.left &&
                    newPos.top < pos.top + pos.height &&
                    newPos.top + newPos.height > pos.top
                ));

                if (!isOverlapping) {
                    usedPositions.push(newPos);
                    return { top, left };
                }
            }
            return { top: Math.random() * ((window.innerHeight * 3) - height), left: Math.random() * (1200 - width) }; // Fallback
        }

        return emotionTags.map((tag, i) => {
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

    const handleTagClick = (tag) => {
        if (selectedTags.includes(tag)) {
            removeTag(tag);
        } else if (tagCount < maxTags) {
            addTag(tag);
        }
    };
    
    const unselectedTags = tagPositions.filter(pos => !selectedTags.includes(pos.id));

    return (
        <div style={{ backgroundColor: '#426DF5', minHeight: '100vh', position: 'relative' }}>
            <LayoutGroup>
                <PageWrapper>
                    <div className="w-full max-w-full mx-auto flex px-12">
                        <div className="w-1/5 pt-32 pr-8">
                            <h2 className="text-4xl text-white font-didot mb-8">Selected Tags</h2>
                            <div className="relative">
                                <AnimatePresence>
                                    {selectedTags.map((tag, index) => {
                                        const style = tagPositions.find(p => p.id === tag);
                                        return <PaperTag key={tag} tag={tag} onClick={handleTagClick} isSelected={true} style={{ ...style, left: 0, top: index * 90, zIndex: 100+index }}/>
                                    })}
                                </AnimatePresence>
                            </div>
                        </div>

                        <div className="w-px bg-black/20 my-32"></div>

                        <div className="w-4/5 pl-8">
                            <div className="w-full flex justify-between items-start mb-8">
                                <h1 className="text-4xl sm:text-5xl text-white font-didot w-2/3">Compose your cinematic moodboard.</h1>
                                <div className="text-right">
                                    <h2 className="text-2xl sm:text-3xl text-white font-work-sans">choose up to</h2>
                                    <p className="text-4xl sm:text-5xl text-white font-work-sans font-bold">{maxTags - tagCount} tags</p>
                                </div>
                            </div>

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
                                className="fixed top-12 right-16 bg-white text-lumiere-blue font-bold text-xl px-12 py-3 rounded-lg shadow-lg hover:bg-gray-100 transition-all transform hover:scale-105 z-50"
                                initial={{ opacity: 0, y: -20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
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
