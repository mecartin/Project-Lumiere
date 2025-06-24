// src/components/ImportPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

const PageWrapper = ({ children, className = '' }) => (
    <div className={`w-full min-h-screen font-brittania transition-opacity duration-1000 flex flex-col items-center justify-center p-4 sm:p-8 relative overflow-hidden ${className}`}>
        {children}
        <p className="absolute bottom-8 text-sm text-black/50">designed by dan mccartin 2025</p>
    </div>
);

const ImportPage = () => {
    const navigate = useNavigate();
    
    return (
        <PageWrapper className="bg-lumiere-yellow bg-grid-import text-center">
            <div className="flex flex-col items-center justify-center text-black">
                <h1 className="text-8xl font-monoton tracking-widest text-red-800 relative pb-2">
                    LOAD THE REEL
                    <span className="absolute bottom-0 left-0 right-0 h-1 bg-red-800"></span>
                </h1>
                <p className="text-4xl mt-4 font-brittania">import your letterboxd data</p>
                <div className="mt-16 flex flex-col items-center space-y-8">
                    <button className="bg-lumiere-green text-white font-bold text-3xl px-12 py-4 rounded-lg border-4 border-black hover:bg-green-600 transition-colors transform hover:scale-105">
                        click here to download zip
                    </button>
                    <button onClick={() => navigate('/loading')} className="bg-lumiere-orange text-black font-bold text-3xl px-20 py-4 rounded-lg border-4 border-black hover:bg-orange-600 transition-colors transform hover:scale-105">
                        upload here
                    </button>
                </div>
                <button onClick={() => navigate('/tags')} className="mt-8 text-xl font-brittania hover:underline">
                    or choose your favorites here
                </button>
            </div>
        </PageWrapper>
    );
};

export default ImportPage;
