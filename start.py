#!/usr/bin/env python3
"""
Aura Quick Start Script
======================
Starts both backend and frontend servers for local development.

Usage:
    python start.py
"""


import sys
import os
import time
from pathlib import Path
import subprocess

def kill_existing_servers():
    """Find and kill any running backend (uvicorn) and frontend (vite) server processes."""
    import psutil
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
            # Kill uvicorn (backend)
            if 'uvicorn' in cmdline and 'main:app' in cmdline:
                print(f"Killing backend server (PID {proc.pid})...")
                proc.kill()
                killed = True
            # Kill vite (frontend)
            elif ('vite' in cmdline or 'npm run dev' in cmdline) and 'frontend' in cmdline:
                print(f"Killing frontend server (PID {proc.pid})...")
                proc.kill()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if killed:
        print("Old server processes terminated.\n")
    else:
        print("No old server processes found.\n")

def run_frontend():
    print("Starting frontend dev server...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'static')
    return subprocess.Popen([
        'npm', 'run', 'dev'
    ], cwd=frontend_dir, shell=True)

def run_backend_with_config():
    # --- Begin migrated backend startup workflow ---
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    # CRITICAL: Load environment configuration FIRST
    from backend.config_init import ensure_config_loaded, validate_critical_config, get_project_root

    print("=" * 80)
    print("Aura Backend Server - Starting...")
    print("=" * 80)

    # Load configuration
    print("\n[1/4] Loading environment configuration...")
    config_loaded = ensure_config_loaded(verbose=True)

    # Validate configuration
    print("\n[2/4] Validating configuration...")
    validation = validate_critical_config()
    print(f"  Status: {validation['status']}")
    if validation['warnings']:
        print(f"  Warnings: {len(validation['warnings'])}")
        for warning in validation['warnings']:
            print(f"    - {warning}")
    if validation['errors']:
        print(f"  Errors: {len(validation['errors'])}")
        for error in validation['errors']:
            print(f"    - {error}")
        print("\n⚠ Critical configuration errors found!")
        sys.exit(1)

    # Import config to get settings
    print("\n[3/4] Importing application...")
    from config import config

    # Get server configuration
    host = os.getenv('BACKEND_HOST', '0.0.0.0')
    port = int(os.getenv('BACKEND_PORT', '8001'))
    workers = int(os.getenv('BACKEND_WORKERS', '1'))
    reload = config.get_bool('DEBUG_MODE', False)

    # Parse command line arguments
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == '--port' and i + 1 < len(sys.argv) - 1:
                port = int(sys.argv[i + 2])
            elif arg == '--host' and i + 1 < len(sys.argv) - 1:
                host = sys.argv[i + 2]
            elif arg == '--reload':
                reload = True

    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Workers: {workers}")
    print(f"  Reload: {reload}")

    # Start server
    print("\n[4/4] Starting FastAPI server...")
    print("=" * 80)

    try:
        import uvicorn
        backend_proc = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'backend.main:app', '--host', str(host), '--port', str(port), '--log-level', 'info'
        ] + (["--reload"] if reload else []))
        return backend_proc
    except Exception as e:
        print(f"\n⚠ Server error: {e}")
        sys.exit(1)

def main():
    print("\nAura Quick Start - Full System\n" + "="*40)
    kill_existing_servers()
    backend_proc = run_backend_with_config()
    time.sleep(3)
    frontend_proc = run_frontend()
    print("\nServers are starting. Access frontend at http://localhost:5173\n")
    print("Press Ctrl+C to stop both servers.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("All servers stopped.")

if __name__ == "__main__":
    main()
