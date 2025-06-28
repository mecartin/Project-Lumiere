// src/components/ImportPage.jsx
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const PageWrapper = ({ children, className = '' }) => (
    <div className={`w-full min-h-screen font-brittania transition-opacity duration-1000 flex flex-col items-center justify-center p-4 sm:p-8 relative overflow-hidden ${className}`}>
        {children}
        <p className="absolute bottom-8 text-sm text-black/50">designed by dan mccartin 2025</p>
    </div>
);

const ImportPage = () => {
    const navigate = useNavigate();
    const [selectedFile, setSelectedFile] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [processingStatus, setProcessingStatus] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const [showNextButton, setShowNextButton] = useState(false);
    const fileInputRef = useRef(null);
    
    const handleDownloadClick = () => {
        window.open('https://letterboxd.com/user/exportdata', '_blank');
    };
    
    const handleUploadClick = () => {
        fileInputRef.current.click();
    };
    
    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (file) {
            // Check if it's a ZIP file by extension (more reliable than MIME type)
            const fileName = file.name.toLowerCase();
            const isZipFile = fileName.endsWith('.zip') || 
                             file.type === 'application/zip' || 
                             file.type === 'application/x-zip-compressed' ||
                             file.type === 'application/octet-stream';
            
            if (isZipFile) {
                setSelectedFile(file);
                await uploadAndProcessFile(file);
            } else {
                alert('Please select a valid ZIP file (.zip extension)');
                console.log('File rejected:', {
                    name: file.name,
                    type: file.type,
                    size: file.size
                });
            }
        }
    };
    
    const uploadAndProcessFile = async (file) => {
        setIsProcessing(true);
        setProcessingStatus({
            status: 'uploading',
            progress: 0,
            current_step: 'Uploading file...',
            message: 'Sending your Letterboxd data to our servers...'
        });
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('http://localhost:8000/process-letterboxd', {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const result = await response.json();
            setSessionId(result.session_id);
            
            // Start polling for status
            pollProcessingStatus(result.session_id);
            
        } catch (error) {
            console.error('Upload error:', error);
            setProcessingStatus({
                status: 'error',
                progress: 0,
                current_step: 'Error',
                message: 'Failed to upload file. Please try again.'
            });
            setIsProcessing(false);
        }
    };
    
    const pollProcessingStatus = async (sessionId) => {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`http://localhost:8000/processing-status/${sessionId}`);
                if (!response.ok) {
                    throw new Error('Status check failed');
                }
                
                const status = await response.json();
                setProcessingStatus(status);
                
                if (status.status === 'completed') {
                    clearInterval(pollInterval);
                    setIsProcessing(false);
                    setShowNextButton(true);
                    console.log('Processing completed:', status.result);
                } else if (status.status === 'error') {
                    clearInterval(pollInterval);
                    setIsProcessing(false);
                    alert('Processing failed: ' + status.message);
                }
                
            } catch (error) {
                console.error('Status polling error:', error);
                clearInterval(pollInterval);
                setIsProcessing(false);
                setProcessingStatus({
                    status: 'error',
                    progress: 0,
                    current_step: 'Error',
                    message: 'Failed to check processing status.'
                });
            }
        }, 2000); // Poll every 2 seconds
    };
    
    const handleNextClick = () => {
        // Navigate to the next page (you can customize this)
        navigate('/tags');
    };
    
    return (
        <PageWrapper className="bg-lumiere-yellow bg-grid-import text-center">
            <div className="flex flex-col items-center justify-center text-black">
                <h1 className="text-8xl font-monoton tracking-widest text-red-800 relative pb-2">
                    LOAD THE REEL
                    <span className="absolute bottom-0 left-0 right-0 h-1 bg-red-800"></span>
                </h1>
                <p className="text-4xl mt-4 font-brittania">import your letterboxd data</p>
                
                {!isProcessing && !showNextButton && (
                    <div className="mt-16 flex flex-col items-center space-y-8">
                        <button 
                            onClick={handleDownloadClick}
                            className="bg-lumiere-green text-white font-bold text-3xl px-12 py-4 rounded-lg border-4 border-black hover:bg-green-600 transition-colors transform hover:scale-105"
                        >
                            download letterboxd data
                        </button>
                        <button 
                            onClick={handleUploadClick}
                            className="bg-lumiere-orange text-black font-bold text-3xl px-20 py-4 rounded-lg border-4 border-black hover:bg-orange-600 transition-colors transform hover:scale-105"
                        >
                            upload zip file
                        </button>
                        {/* Hidden file input */}
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".zip"
                            onChange={handleFileChange}
                            style={{ display: 'none' }}
                        />
                    </div>
                )}
                
                {selectedFile && !isProcessing && !showNextButton && (
                    <p className="mt-4 text-lg font-brittania text-green-800">
                        Selected: {selectedFile.name}
                    </p>
                )}
                
                {isProcessing && processingStatus && (
                    <div className="mt-16 flex flex-col items-center space-y-6">
                        <div className="bg-white p-8 rounded-lg border-4 border-black max-w-md">
                            <h3 className="text-2xl font-brittania mb-4">{processingStatus.current_step}</h3>
                            <p className="text-lg mb-4">{processingStatus.message}</p>
                            
                            {/* Progress bar */}
                            <div className="w-full bg-gray-200 rounded-full h-4 border-2 border-black">
                                <div 
                                    className="bg-lumiere-green h-full rounded-full transition-all duration-500"
                                    style={{ width: `${processingStatus.progress}%` }}
                                ></div>
                            </div>
                            <p className="text-center mt-2 font-bold">{processingStatus.progress}%</p>
                        </div>
                    </div>
                )}
                
                {showNextButton && (
                    <div className="mt-16 flex flex-col items-center space-y-8">
                        <div className="bg-white p-8 rounded-lg border-4 border-black max-w-md">
                            <h3 className="text-2xl font-brittania mb-4 text-green-800">✓ Processing Complete!</h3>
                            {processingStatus?.result && (
                                <div className="text-left space-y-2 mb-6">
                                    <p><strong>Total movies processed:</strong> {processingStatus.result.total_movies}</p>
                                    <p><strong>Movies ranked:</strong> {processingStatus.result.ranked_movies}</p>
                                    <p><strong>Movies enriched:</strong> {processingStatus.result.enriched_movies}</p>
                                    <p><strong>Favorite films found:</strong> {processingStatus.result.favorite_films}</p>
                                </div>
                            )}
                            <button 
                                onClick={handleNextClick}
                                className="bg-lumiere-green text-white font-bold text-2xl px-8 py-3 rounded-lg border-4 border-black hover:bg-green-600 transition-colors transform hover:scale-105"
                            >
                                Continue to Tags
                            </button>
                        </div>
                    </div>
                )}
                
                {!isProcessing && !showNextButton && (
                    <button onClick={() => navigate('/tags')} className="mt-8 text-xl font-brittania hover:underline">
                        or choose your favorites here
                    </button>
                )}
            </div>
        </PageWrapper>
    );
};

export default ImportPage;
