import React from 'react';
import { motion } from 'framer-motion';

const LEDIndicator = ({ active, index, value, onClick }) => {
    const isOn = index < value;
    const color = isOn ? (index < 5 ? 'wa-led-green' : 'wa-led-red') : 'wa-bg';
    const glowColor = isOn ? (index < 5 ? '#7EB77F' : '#D36B5A') : 'transparent';

    return (
        <motion.button 
            onClick={onClick}
            className="relative group"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
        >
            {/* Glassmorphism effect */}
            <div className="relative">
                {/* Outer glow */}
                {isOn && (
                    <motion.div
                        className="absolute inset-0 rounded-full"
                        animate={{
                            boxShadow: [
                                `0 0 8px 2px ${glowColor}`,
                                `0 0 12px 4px ${glowColor}`,
                                `0 0 8px 2px ${glowColor}`
                            ]
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                    />
                )}
                
                {/* Main LED body */}
                <div 
                    className={`
                        w-6 h-6 rounded-full border-2 border-wa-text/10 
                        transition-all duration-300 ease-out
                        ${isOn ? 'shadow-inner' : 'shadow-inner shadow-wa-text/20'}
                    `}
                    style={{
                        backgroundColor: `var(--tw-color-${color}, ${color})`,
                        boxShadow: isOn 
                            ? `inset 0 0 4px rgba(255,255,255,0.6), inset 0 0 8px rgba(255,255,255,0.3)`
                            : 'inset 0 0 4px rgba(0,0,0,0.3)',
                        backdropFilter: isOn ? 'blur(1px)' : 'none',
                    }}
                >
                    {/* Inner highlight for glass effect */}
                    {isOn && (
                        <div 
                            className="absolute inset-1 rounded-full opacity-60"
                            style={{
                                background: `radial-gradient(circle at 30% 30%, rgba(255,255,255,0.8) 0%, transparent 70%)`
                            }}
                        />
                    )}
                </div>
                
                {/* Hover effect */}
                <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <div className="absolute inset-0 rounded-full bg-white/20 blur-sm" />
                </div>
            </div>
        </motion.button>
    );
};

export default LEDIndicator; 