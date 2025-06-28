#!/usr/bin/env python3
"""
Backend startup script for Project Lumiere
Handles environment setup and starts the FastAPI server
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")

def setup_environment():
    """Setup environment variables and check dependencies"""
    print("🔧 Setting up Project Lumiere Backend...")
    
    # Load .env file if it exists
    load_env_file()
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    # Check for TMDB API key
    tmdb_key = os.getenv("TMDB_API_KEY")
    if not tmdb_key:
        print("⚠️  Warning: TMDB_API_KEY environment variable not set.")
        print("   The enrichment step will be skipped.")
        print("   To enable TMDB enrichment:")
        print("   1. Get your API key from: https://www.themoviedb.org/settings/api")
        print("   2. Set the environment variable:")
        print("      Windows CMD: set TMDB_API_KEY=your_api_key_here")
        print("      Windows PowerShell: $env:TMDB_API_KEY='your_api_key_here'")
        print("      Or create a .env file in the backend directory with:")
        print("      TMDB_API_KEY=your_api_key_here")
    else:
        print("✅ TMDB API key found")
    
    # Check for required Python packages
    required_packages = [
        "fastapi", "uvicorn", "pandas", "numpy", 
        "requests", "python-multipart"
    ]
    
    print("\n📦 Checking required packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install " + " ".join(missing_packages))
        sys.exit(1)
    
    print("✅ All required packages are installed")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Project Lumiere Backend Server...")
    print("=" * 60)
    print("📡 API Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_environment()
    start_server() 