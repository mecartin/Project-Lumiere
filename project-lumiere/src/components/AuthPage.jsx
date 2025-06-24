// src/components/AuthPage.jsx
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const PageWrapper = ({ children, className = '' }) => (
    <div className={`w-full min-h-screen transition-opacity duration-1000 flex items-center justify-center p-4 sm:p-8 relative overflow-hidden ${className}`}>
        {children}
        <p className="absolute bottom-24 right-24 text-sm text-black/50 font-brittania text-right">designed by dan mccartin 2025</p>
    </div>
);

const AuthPage = () => {
    const navigate = useNavigate();
    const [isLogin, setIsLogin] = useState(true);
    const [signupStep, setSignupStep] = useState(1);

    const FormInput = ({ label, type = 'text', mode = 'light' }) => {
        const [showPassword, setShowPassword] = useState(false);
        const [inputValue, setInputValue] = useState('');
        const isPassword = type === 'password';
        const isDarkMode = mode === 'dark';

        return (
            <div className="flex flex-row items-center justify-end mb-4">
                <label className={`text-2xl font-brittania mr-4 ${isDarkMode ? 'text-lumiere-yellow' : 'text-red-800'}`}>{label}</label>
                <div className="relative w-96">
                    <input
                        type={isPassword && showPassword ? 'text' : type}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        className={`text-lg bg-transparent border-b-2 border-t-2 focus:outline-none p-2 w-full text-right font-mono font-bold ${
                            isDarkMode
                                ? 'border-lumiere-yellow text-lumiere-yellow placeholder-yellow-200/50 focus:border-yellow-200'
                                : 'border-red-800 text-red-900 placeholder-red-700/50 focus:border-red-600'
                        }`}
                    />
                    {isPassword && inputValue && (
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className={`absolute inset-y-0 left-0 flex items-center px-3 ${isDarkMode ? 'text-lumiere-yellow' : 'text-red-800'}`}
                        >
                            {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                        </button>
                    )}
                </div>
            </div>
        );
    };
    
    const AuthForm = () => {
        if (isLogin) {
            return (
                <motion.div key="login" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="flex flex-col items-end">
                    <h2 className="text-5xl text-red-800 font-brittania mb-6 tracking-wider">log in</h2>
                    <FormInput label="username" />
                    <FormInput label="password" type="password" />
                </motion.div>
            );
        }
        
        // Signup form
        return (
            <motion.div key="signup" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="flex flex-col items-end">
                <h2 className="text-5xl bg-red-800 text-lumiere-yellow font-brittania mb-6 tracking-wider px-4 py-1">sign up</h2>
                <AnimatePresence mode="wait">
                    {signupStep === 1 && (
                        <motion.div key="step1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                            <FormInput label="email" type="email" />
                            <FormInput label="username" />
                        </motion.div>
                    )}
                    {signupStep === 2 && (
                        <motion.div 
                            key="step2" 
                            initial={{ width: 0, opacity: 0 }} 
                            animate={{ width: 'auto', opacity: 1 }} 
                            exit={{ width: 0, opacity: 0 }}
                            transition={{ duration: 0.7, ease: [0.76, 0, 0.24, 1] }}
                            className="bg-red-800 p-4 rounded-lg overflow-hidden"
                        >
                            <FormInput label="password" type="password" mode="dark" />
                            <FormInput label="confirm password" type="password" mode="dark" />
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        );
    };

    const handleNext = () => {
        if (isLogin) {
            navigate('/import');
        } else {
            if (signupStep === 1) {
                setSignupStep(2);
            } else {
                navigate('/import');
            }
        }
    };
    
    const toggleForm = () => {
        setIsLogin(!isLogin);
        setSignupStep(1);
    }

    return (
        <PageWrapper className="bg-lumiere-yellow bg-grid-red">
            <div className="absolute top-24 left-24 text-center">
                <h1 className="text-7xl text-red-800 font-monoton tracking-widest">PROJECT</h1>
                <h1 className="text-7xl text-red-800 font-monoton tracking-widest">LUMIÈRE</h1>
            </div>
            
            <div className="absolute bottom-24 left-24 text-black font-broadway text-5xl">
                <p>the perfect film is</p>
                <p>just a scene away</p>
            </div>

            <div className="absolute top-24 right-32 flex flex-col items-end">
                <AnimatePresence mode="wait">
                    <AuthForm />
                </AnimatePresence>
                <div className="flex items-center mt-6">
                    <button onClick={toggleForm} className="text-xl text-red-800 hover:underline font-brittania">
                        {isLogin ? 'sign up?' : 'log in?'}
                    </button>
                    <button onClick={handleNext} className="ml-8 bg-red-800 text-lumiere-yellow px-10 py-2 font-brittania tracking-widest text-xl border-2 border-red-900 hover:bg-red-700 transition-colors">
                        next
                    </button>
                </div>
            </div>
        </PageWrapper>
    );
};

export default AuthPage;
