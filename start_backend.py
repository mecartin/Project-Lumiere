#!/usr/bin/env python3
"""
Startup script for the Project Lumiere backend server
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up the environment for the backend"""
    # Add backend directory to Python path
    backend_dir = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_dir))
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", str(backend_dir))
    
    # Set TMDB API key if available
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    if not tmdb_api_key:
        print("⚠️  Warning: TMDB_API_KEY environment variable not set")
        print("   Some features may not work properly")
        print("   You can set it with: export TMDB_API_KEY=your_api_key")

def install_requirements():
    """Install Python requirements if needed"""
    backend_dir = Path(__file__).parent / "backend"
    requirements_file = backend_dir / "requirements_py38.txt"
    
    if requirements_file.exists():
        print("📦 Installing Python requirements...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    else:
        print("⚠️  No requirements_py38.txt found")
    
    return True

def start_server():
    """Start the backend components"""
    backend_dir = Path(__file__).parent / "backend"
    
    print("🚀 Starting Project Lumiere Backend Components...")
    print(f"📁 Backend directory: {backend_dir}")
    print("🔧 Available components:")
    print("   - enricher.py: Movie data enrichment")
    print("   - ranker.py: Movie ranking and taste scoring")
    print("   - test_simple.py: TMDB API testing")
    print("=" * 50)
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Test core components
        print("🧪 Testing core components...")
        
        # Test TMDB API connection
        print("🔍 Testing TMDB API connection...")
        subprocess.run([sys.executable, "test_simple.py"], check=True)
        
        print("\n✅ Core components are ready!")
        print("💡 You can now use the individual components:")
        print("   python enricher.py")
        print("   python ranker.py")
        print("   python test_simple.py")
        
    except KeyboardInterrupt:
        print("\n🛑 Components stopped by user")
    except Exception as e:
        print(f"❌ Failed to start components: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🎬 Project Lumiere Backend Components")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return 1
    
    # Start components
    if not start_server():
        print("❌ Failed to start components")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 