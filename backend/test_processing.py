#!/usr/bin/env python3
"""
Test script for the Letterboxd processing workflow
"""

import os
import sys
import requests
import time
from pathlib import Path

def test_processing_workflow():
    """Test the complete processing workflow"""
    
    # Check if we have a test zip file
    test_zip = None
    for file in os.listdir('.'):
        if file.endswith('.zip') and 'letterboxd' in file.lower():
            test_zip = file
            break
    
    if not test_zip:
        print("❌ No Letterboxd zip file found for testing")
        print("Please place a Letterboxd export zip file in the backend directory")
        return False
    
    print(f"📁 Found test file: {test_zip}")
    
    # Test the API endpoints
    base_url = "http://localhost:8000"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("Make sure the backend server is running with: python app.py")
        return False
    
    # Test file upload
    try:
        with open(test_zip, 'rb') as f:
            files = {'file': (test_zip, f, 'application/zip')}
            response = requests.post(f"{base_url}/process-letterboxd", files=files)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print(f"✅ File upload successful, session ID: {session_id}")
        else:
            print(f"❌ File upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return False
    
    # Monitor processing status
    print("\n🔄 Monitoring processing status...")
    max_wait_time = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{base_url}/processing-status/{session_id}")
            if response.status_code == 200:
                status = response.json()
                print(f"📊 Status: {status['status']} - {status['progress']}% - {status['current_step']}")
                
                if status['status'] == 'completed':
                    print("🎉 Processing completed successfully!")
                    print(f"📈 Results: {status['result']}")
                    return True
                elif status['status'] == 'error':
                    print(f"❌ Processing failed: {status['message']}")
                    return False
                    
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return False
            
        time.sleep(5)  # Check every 5 seconds
    
    print("⏰ Processing timed out")
    return False

if __name__ == "__main__":
    print("🧪 Testing Letterboxd Processing Workflow")
    print("=" * 50)
    
    success = test_processing_workflow()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1) 