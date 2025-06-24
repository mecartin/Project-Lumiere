#!/usr/bin/env python3
"""
Test script to verify frontend-backend connection
"""

import requests
import json
import time
import sys
from pathlib import Path

class ConnectionTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []

    def test_backend_health(self):
        """Test if backend is responding"""
        print("🔍 Testing backend health...")
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is healthy")
                self.test_results.append(("Backend Health", "PASS"))
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                self.test_results.append(("Backend Health", "FAIL"))
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend not reachable: {e}")
            self.test_results.append(("Backend Health", "FAIL"))
            return False

    def test_backend_root(self):
        """Test backend root endpoint"""
        print("🔍 Testing backend root endpoint...")
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend root: {data.get('message', 'Unknown')}")
                self.test_results.append(("Backend Root", "PASS"))
                return True
            else:
                print(f"❌ Backend root failed: {response.status_code}")
                self.test_results.append(("Backend Root", "FAIL"))
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend root error: {e}")
            self.test_results.append(("Backend Root", "FAIL"))
            return False

    def test_user_creation(self):
        """Test user creation endpoint"""
        print("🔍 Testing user creation...")
        try:
            user_data = {
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "letterboxd_username": "testuser"
            }
            
            response = requests.post(
                f"{self.backend_url}/users/create",
                json=user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                print(f"✅ User created: {user['username']}")
                self.test_results.append(("User Creation", "PASS"))
                return user['id']
            else:
                print(f"❌ User creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results.append(("User Creation", "FAIL"))
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ User creation error: {e}")
            self.test_results.append(("User Creation", "FAIL"))
            return None

    def test_tags_endpoint(self):
        """Test tags endpoint"""
        print("🔍 Testing tags endpoint...")
        try:
            response = requests.get(f"{self.backend_url}/tags", timeout=5)
            if response.status_code == 200:
                tags = response.json()
                print(f"✅ Tags endpoint: {len(tags)} tags available")
                self.test_results.append(("Tags Endpoint", "PASS"))
                return True
            else:
                print(f"❌ Tags endpoint failed: {response.status_code}")
                self.test_results.append(("Tags Endpoint", "FAIL"))
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Tags endpoint error: {e}")
            self.test_results.append(("Tags Endpoint", "FAIL"))
            return False

    def test_recommendations_endpoint(self):
        """Test recommendations endpoint"""
        print("🔍 Testing recommendations endpoint...")
        try:
            # First create a user
            user_id = self.test_user_creation()
            if not user_id:
                print("❌ Skipping recommendations test - no user created")
                self.test_results.append(("Recommendations", "SKIP"))
                return False
            
            recommendation_data = {
                "user_id": user_id,
                "count": 5
            }
            
            response = requests.post(
                f"{self.backend_url}/recommendations",
                json=recommendation_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Recommendations: {data.get('count', 0)} movies")
                self.test_results.append(("Recommendations", "PASS"))
                return True
            else:
                print(f"❌ Recommendations failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results.append(("Recommendations", "FAIL"))
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Recommendations error: {e}")
            self.test_results.append(("Recommendations", "FAIL"))
            return False

    def test_frontend_availability(self):
        """Test if frontend is accessible"""
        print("🔍 Testing frontend availability...")
        try:
            response = requests.get(f"{self.frontend_url}", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend is accessible")
                self.test_results.append(("Frontend Access", "PASS"))
                return True
            else:
                print(f"❌ Frontend access failed: {response.status_code}")
                self.test_results.append(("Frontend Access", "FAIL"))
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Frontend not reachable: {e}")
            self.test_results.append(("Frontend Access", "FAIL"))
            return False

    def test_cors_headers(self):
        """Test CORS headers"""
        print("🔍 Testing CORS headers...")
        try:
            response = requests.options(f"{self.backend_url}/users/create", timeout=5)
            cors_headers = response.headers.get('access-control-allow-origin', '')
            
            if 'localhost:3000' in cors_headers or '*' in cors_headers:
                print("✅ CORS headers configured correctly")
                self.test_results.append(("CORS Headers", "PASS"))
                return True
            else:
                print(f"❌ CORS headers missing or incorrect: {cors_headers}")
                self.test_results.append(("CORS Headers", "FAIL"))
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ CORS test error: {e}")
            self.test_results.append(("CORS Headers", "FAIL"))
            return False

    def run_all_tests(self):
        """Run all connection tests"""
        print("🎬 Project Lumiere - Connection Test Suite")
        print("=" * 50)
        
        # Test backend
        self.test_backend_health()
        self.test_backend_root()
        self.test_tags_endpoint()
        self.test_recommendations_endpoint()
        
        # Test frontend
        self.test_frontend_availability()
        
        # Test integration
        self.test_cors_headers()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, result in self.test_results:
            status_icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
            print(f"{status_icon} {test_name}: {result}")
            
            if result == "PASS":
                passed += 1
            elif result == "FAIL":
                failed += 1
            else:
                skipped += 1
        
        print("\n" + "=" * 50)
        print(f"📈 Results: {passed} passed, {failed} failed, {skipped} skipped")
        
        if failed == 0:
            print("🎉 All tests passed! Frontend and backend are properly connected.")
        else:
            print("⚠️  Some tests failed. Check the backend server and configuration.")
        
        print("=" * 50)

def main():
    """Main function"""
    tester = ConnectionTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 