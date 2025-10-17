#!/usr/bin/env python3
"""
Aura Quick Start Script
======================
Starts both backend and frontend servers for local development.

Usage:
    python start.py
"""

import subprocess
import sys
import os
import time
import signal

def run_backend():
    print("Starting backend server...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    # Start backend (FastAPI)
    return subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 'main:app', '--reload', '--port', '8001'
    ], cwd=backend_dir)

def run_frontend():
    print("Starting frontend dev server...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'static')
    # Start frontend (Vite)
    return subprocess.Popen([
        'npm', 'run', 'dev'
    ], cwd=frontend_dir, shell=True)

def main():
    print("\nAura Quick Start - Local Development\n" + "="*40)
    # Kill any running backend/frontend server processes
    kill_existing_servers()
    backend_proc = run_backend()
    time.sleep(3)  # Give backend time to start
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

if __name__ == "__main__":
    main()
