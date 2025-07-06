"""
Proper API server startup with correct module paths
"""
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set environment variable for module loading
os.environ["PYTHONPATH"] = current_dir

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Honeypot Detector API Server...")
    print(f"📁 Working directory: {current_dir}")
    print("📝 API Documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 Dashboard API: http://localhost:8000/api/v1/dashboard/stats")
    print("🛡️  Analysis API: http://localhost:8000/api/v1/analyze")
    print()

    try:
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
        )
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("🔧 Trying alternative startup method...")

        # Try importing the app directly
        try:
            from api.main import app

            uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
        except Exception as e2:
            print(f"❌ Alternative startup also failed: {e2}")
            print("🚨 Please check your Python environment and dependencies")
