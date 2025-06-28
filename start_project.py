#!/usr/bin/env python3
"""
Combined startup script for Project Lumiere
Starts both frontend and backend servers
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

class ProjectLumiere:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "project-lumiere"
        self.backend_process = None
        self.frontend_process = None
        self.running = True

    def setup_environment(self):
        """Set up the environment"""
        print("🎬 Project Lumiere - Full Stack Startup")
        print("=" * 50)
        
        # Check if directories exist
        if not self.backend_dir.exists():
            print(f"❌ Backend directory not found: {self.backend_dir}")
            return False
        
        if not self.frontend_dir.exists():
            print(f"❌ Frontend directory not found: {self.frontend_dir}")
            return False
        
        # Set environment variables
        os.environ.setdefault("PYTHONPATH", str(self.backend_dir))
        
        # Add Node.js to PATH if not already there
        nodejs_path = r"C:\Program Files\nodejs"
        if nodejs_path not in os.environ.get("PATH", ""):
            current_path = os.environ.get("PATH", "")
            os.environ["PATH"] = f"{nodejs_path};{current_path}"
            print(f"✅ Added Node.js to PATH: {nodejs_path}")
        
        # Check TMDB API key
        tmdb_api_key = os.getenv("TMDB_API_KEY")
        if not tmdb_api_key:
            print("⚠️  Warning: TMDB_API_KEY environment variable not set")
            print("   Some features may not work properly")
            print("   You can set it with: export TMDB_API_KEY=your_api_key")
        
        return True

    def install_backend_requirements(self):
        """Install backend Python requirements"""
        requirements_file = self.backend_dir / "requirements.txt"
        
        if requirements_file.exists():
            print("📦 Installing backend requirements...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True, capture_output=True)
                print("✅ Backend requirements installed")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install backend requirements: {e}")
                return False
        else:
            print("⚠️  No backend requirements.txt found")
            return True

    def install_frontend_dependencies(self):
        """Install frontend npm dependencies"""
        package_json = self.frontend_dir / "package.json"
        
        if package_json.exists():
            print("📦 Installing frontend dependencies...")
            try:
                # Use npm from the Node.js installation directory
                npm_path = r"C:\Program Files\nodejs\npm.cmd"
                if os.path.exists(npm_path):
                    subprocess.run([
                        npm_path, "install"
                    ], cwd=self.frontend_dir, check=True, capture_output=True)
                else:
                    # Fallback to npm from PATH
                    subprocess.run([
                        "npm", "install"
                    ], cwd=self.frontend_dir, check=True, capture_output=True)
                print("✅ Frontend dependencies installed")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install frontend dependencies: {e}")
                return False
        else:
            print("⚠️  No frontend package.json found")
            return True

    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting backend server...")
        
        try:
            os.chdir(self.backend_dir)
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "app:app", 
                "--host", "0.0.0.0", 
                "--port", "8000", 
                "--reload",
                "--log-level", "info"
            ])
            
            # Wait a moment for server to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend server started at http://localhost:8000")
                return True
            else:
                print("❌ Backend server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False

    def start_frontend(self):
        """Start the frontend development server"""
        print("🚀 Starting frontend server...")
        
        try:
            os.chdir(self.frontend_dir)
            
            # Use npm from the Node.js installation directory
            npm_path = r"C:\Program Files\nodejs\npm.cmd"
            if os.path.exists(npm_path):
                self.frontend_process = subprocess.Popen([
                    npm_path, "start"
                ], cwd=self.frontend_dir)
            else:
                # Fallback to npm from PATH
                self.frontend_process = subprocess.Popen([
                    "npm", "start"
                ], cwd=self.frontend_dir)
            
            # Wait a moment for server to start
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend server started at http://localhost:3000")
                return True
            else:
                print("❌ Frontend server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False

    def start_backend_thread(self):
        """Start backend in a separate thread"""
        if not self.start_backend():
            self.running = False

    def start_frontend_thread(self):
        """Start frontend in a separate thread"""
        if not self.start_frontend():
            self.running = False

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down Project Lumiere...")
        self.running = False
        self.cleanup()

    def cleanup(self):
        """Clean up processes"""
        if self.backend_process:
            print("🛑 Stopping backend server...")
            self.backend_process.terminate()
            self.backend_process.wait()
        
        if self.frontend_process:
            print("🛑 Stopping frontend server...")
            self.frontend_process.terminate()
            self.frontend_process.wait()
        
        print("✅ Project Lumiere stopped")

    def run(self):
        """Main run method"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Setup environment
        if not self.setup_environment():
            return 1
        
        # Install dependencies
        if not self.install_backend_requirements():
            return 1
        
        if not self.install_frontend_dependencies():
            return 1
        
        print("=" * 50)
        print("🌐 Starting servers...")
        print("📱 Frontend: http://localhost:3000")
        print("🔧 Backend:  http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("=" * 50)
        
        # Start servers in separate threads
        backend_thread = threading.Thread(target=self.start_backend_thread)
        frontend_thread = threading.Thread(target=self.start_frontend_thread)
        
        backend_thread.start()
        time.sleep(2)  # Give backend a head start
        frontend_thread.start()
        
        # Wait for threads to complete
        backend_thread.join()
        frontend_thread.join()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)
        
        return 0

def main():
    """Main function"""
    project = ProjectLumiere()
    return project.run()

if __name__ == "__main__":
    sys.exit(main()) 