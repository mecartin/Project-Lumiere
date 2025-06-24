import React, { useEffect } from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';

const Knob = ({ value, onChange }) => {
    const y = useMotionValue(0);
    const rotation = useTransform(y, [-100, 100], [-150, 150]);
    
    const handleDrag = (event, info) => {
        const newY = y.get() + info.delta.y;
        y.set(newY);
    };
    
    const transformedValue = useTransform(rotation, (v) => Math.round((v + 150) / 30));

    useEffect(() => {
        const unsubscribe = transformedValue.onChange(v => {
            if (v >= 1 && v <= 10) onChange(v);
        });
        return unsubscribe;
    }, [transformedValue, onChange]);

    const handleWheel = (e) => {
        const delta = Math.sign(e.deltaY);
        const newVal = Math.min(10, Math.max(1, value - delta));
        onChange(newVal);
    };

    return (
        <div className="relative">
            <motion.div 
                className="relative w-16 h-16 cursor-ns-resize"
                onPan={handleDrag}
                onWheel={handleWheel}
            >
                {/* Tick marks around the knob */}
                <div className="absolute inset-0 rounded-full">
                    {[...Array(10)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute w-0.5 h-2 bg-wa-text/30"
                            style={{
                                top: '2px',
                                left: '50%',
                                transform: `translateX(-50%) rotate(${i * 36}deg)`,
                                transformOrigin: '50% 28px'
                            }}
                        />
                    ))}
                </div>
                
                {/* Main knob body with brushed metal effect */}
                <div 
                    className="absolute inset-0 rounded-full border-2 border-wa-text shadow-inner shadow-wa-text/20"
                    style={{
                        background: `
                            radial-gradient(circle at 30% 30%, #F2E9DC 0%, #B5A89F 50%, #8B7D6B 100%),
                            repeating-linear-gradient(
                                45deg,
                                transparent,
                                transparent 2px,
                                rgba(0,0,0,0.1) 2px,
                                rgba(0,0,0,0.1) 4px
                            )
                        `
                    }}
                />
                
                <motion.div 
                    className="absolute inset-1 rounded-full bg-wa-bg"
                    style={{ rotate: rotation }}
                >
                    <div className="absolute top-1 left-1/2 -ml-0.5 w-1 h-3 bg-wa-text rounded-full shadow-md"></div>
                </motion.div>
            </motion.div>
            
            {/* Value display */}
            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-wa-text text-xs font-spectral">
                {value}
            </div>
        </div>
    );
};

export default Knob; 