import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class TestBackend:
    def __init__(self):
        self.client = httpx.Client(base_url=BASE_URL)
        self.user_id = None
    
    async def test_root(self):
        """Test root endpoint"""
        print("1. Testing root endpoint...")
        response = self.client.get("/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✓ Root endpoint working\n")
    
    async def test_create_user(self):
        """Test user creation"""
        print("2. Testing user creation...")
        user_data = {
            "username": f"testuser_{datetime.now().timestamp()}",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "letterboxd_username": "MECCATTI"
        }
        response = self.client.post("/users/create", json=user_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            self.user_id = response.json()["id"]
            print(f"   ✓ User created with ID: {self.user_id}\n")
        else:
            print("   ✗ User creation failed\n")
    
    async def test_get_tags(self):
        """Test getting mood tags"""
        print("3. Testing mood tags endpoint...")
        
        # Get all tags
        response = self.client.get("/tags")
        print(f"   Status: {response.status_code}")
        print(f"   Total tags: {len(response.json())}")
        print(f"   Sample tags: {response.json()[:3]}")
        
        # Get tags by category
        response = self.client.get("/tags?category=emotion")
        print(f"   Emotion tags: {len(response.json())}")
        print("   ✓ Tags endpoint working\n")
    
    async def test_import_letterboxd(self):
        """Test Letterboxd import"""
        print("4. Testing Letterboxd import...")
        
        if not self.user_id:
            print("   ✗ No user ID available, skipping import test\n")
            return
        
        # Check if the zip file exists
        import os
        zip_path = "letterboxd-meccatti-2025-06-19-04-23-utc.zip"
        
        if not os.path.exists(zip_path):
            print(f"   ✗ Zip file not found: {zip_path}\n")
            return
        
        with open(zip_path, "rb") as f:
            files = {"file": ("letterboxd.zip", f, "application/zip")}
            response = httpx.post(
                f"{BASE_URL}/import/letterboxd/{self.user_id}",
                files=files
            )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Watched movies imported: {data['watched_count']}")
            print(f"   Ratings imported: {data['ratings_count']}")
            print("   ✓ Import successful\n")
        else:
            print(f"   ✗ Import failed: {response.text}\n")
    
    async def test_user_profile(self):
        """Test user profile generation"""
        print("5. Testing user profile...")
        
        if not self.user_id:
            print("   ✗ No user ID available, skipping profile test\n")
            return
        
        response = self.client.get(f"/users/{self.user_id}/profile")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()["profile"]
            print(f"   Total watched: {profile.get('total_watched', 0)}")
            print(f"   Average rating: {profile.get('avg_rating', 'N/A')}")
            print(f"   Genre preferences: {list(profile.get('genre_preferences', {}).keys())[:5]}")
            print("   ✓ Profile generated\n")
    
    async def test_recommendations(self):
        """Test movie recommendations"""
        print("6. Testing recommendations...")
        
        if not self.user_id:
            print("   ✗ No user ID available, skipping recommendations test\n")
            return
        
        # Test with some mood tags
        recommendation_data = {
            "user_id": self.user_id,
            "tag_ids": [1, 4, 20],  # melancholic, nostalgic, coming-of-age
            "filters": {
                "min_year": 1990,
                "max_runtime": 180
            }
        }
        
        response = self.client.post("/recommendations", json=recommendation_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Recommendations found: {data['count']}")
            if data['recommendations']:
                print(f"   Top recommendation: {data['recommendations'][0]['title']}")
                print(f"   Reason: {data['recommendations'][0]['reasons']}")
            print("   ✓ Recommendations working\n")
    
    async def test_user_stats(self):
        """Test user statistics"""
        print("7. Testing user statistics...")
        
        if not self.user_id:
            print("   ✗ No user ID available, skipping stats test\n")
            return
        
        response = self.client.get(f"/users/{self.user_id}/stats")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✓ Stats endpoint working\n")
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("🎬 TESTING PROJECT LUMIERE BACKEND 🎬\n")
        print("="*50 + "\n")
        
        try:
            await self.test_root()
            await self.test_create_user()
            await self.test_get_tags()
            await self.test_import_letterboxd()
            await self.test_user_profile()
            await self.test_recommendations()
            await self.test_user_stats()
            
            print("="*50)
            print("✅ All tests completed!")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
        finally:
            self.client.close()

if __name__ == "__main__":
    tester = TestBackend()
    asyncio.run(tester.run_all_tests())