"""
Quick Backend Startup Script
=============================

Starts the FastAPI backend server with proper configuration.

Usage:
    python start_backend.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Get backend directory
    backend_dir = Path(__file__).parent / "backend"
    
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        return 1
    
    # Check if main.py exists
    main_py = backend_dir / "main.py"
    if not main_py.exists():
        print(f"❌ Backend main.py not found: {main_py}")
        return 1
    
    print("🚀 Starting Aura Backend Server...")
    print(f"📂 Working directory: {backend_dir}")
    print(f"🐍 Python: {sys.executable}")
    print("\n" + "=" * 80)
    print("Press Ctrl+C to stop the server")
    print("=" * 80 + "\n")
    
    try:
        # Start the backend server
        subprocess.run(
            [sys.executable, "main.py"],
            cwd=str(backend_dir),
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
