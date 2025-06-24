// src/components/LoadingPage.jsx
import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

const PageWrapper = ({ children, className = '' }) => (
    <div className={`w-full min-h-screen font-vt323 transition-opacity duration-1000 flex flex-col items-center justify-center p-4 sm:p-8 relative overflow-hidden ${className}`}>
        {children}
        <p className="absolute bottom-4 right-4 text-xs text-lumiere-loading-text/50">designed by dan mccartin 2025</p>
    </div>
);

const LoadingPage = () => {
    const navigate = useNavigate();
    const [lines, setLines] = useState([]);
    const loadingSteps = useMemo(() => [
        "> Establishing connection to Letterboxd Archive...",
        "> Retrieving cinematic memories... COMPLETE",
        "> Parsing narrative patterns... SUCCESSFUL",
        "> Synthesizing taste genome from viewing history... DONE",
        "> Cross-referencing global film indexes",
        "> Filtering for auteur bias, era leanings, and aesthetic gravity...",
        "> Selecting your Core 40: 'The Essential Cuts'... COMPILED",
        "> Initializing emotional interface and genre biters... STANDING BY",
        "> Calibrating for user interaction... READY",
        "> ",
        "> Project Lumière is lit.",
        "> ",
        "> Begin transmission? (Y/N)"
    ], []);

    useEffect(() => {
        const timer = setTimeout(() => {
            if (lines.length < loadingSteps.length) {
                setLines(prev => [...prev, loadingSteps[lines.length]]);
            } else {
                 setTimeout(() => navigate('/tags'), 1000);
            }
        }, lines.length === 0 ? 500 : Math.random() * 300 + 100);

        return () => clearTimeout(timer);
    }, [lines, navigate, loadingSteps]);

    return (
        <PageWrapper className="bg-lumiere-dark-bg bg-grid-loading items-start">
            <div className="text-lumiere-loading-text text-2xl sm:text-3xl p-4 sm:p-8">
                {lines.map((line, i) => (
                    <p key={i} className="flex">
                        <span className="whitespace-pre">{line}</span>
                        {i === lines.length - 1 && i < loadingSteps.length-1 && <span className="animate-pulse">_</span>}
                         {i === loadingSteps.length-1 && <span className="ml-2 animate-pulse">Y_</span>}
                    </p>
                ))}
            </div>
        </PageWrapper>
    );
};

export default LoadingPage;
