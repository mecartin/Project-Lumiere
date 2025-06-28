#!/usr/bin/env python3
"""
Test script for TMDB API key setup
"""

import os
import sys
from enricher import MovieTasteEnricher

def test_tmdb_connection():
    """Test TMDB API connection"""
    print("🔑 Testing TMDB API Setup...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("❌ TMDB_API_KEY environment variable not set!")
        print("\nTo set it up:")
        print("1. Get your API key from: https://www.themoviedb.org/settings/api")
        print("2. Set the environment variable:")
        print("   Windows CMD: set TMDB_API_KEY=your_key_here")
        print("   Windows PowerShell: $env:TMDB_API_KEY='your_key_here'")
        print("   Or create a .env file in the backend directory")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test the connection
    try:
        enricher = MovieTasteEnricher(api_key)
        success = enricher.test_api_connection()
        
        if success:
            print("🎉 TMDB API connection successful!")
            print("✅ Your API key is working correctly")
            return True
        else:
            print("❌ TMDB API connection failed")
            print("Please check your API key and try again")
            return False
            
    except Exception as e:
        print(f"❌ Error testing TMDB API: {e}")
        return False

if __name__ == "__main__":
    success = test_tmdb_connection()
    
    if success:
        print("\n🎬 You're all set! The enrichment step will now work.")
        print("Try uploading your Letterboxd data again to see the enhanced results!")
    else:
        print("\n🔧 Please fix the API key setup and try again.")
        sys.exit(1) 