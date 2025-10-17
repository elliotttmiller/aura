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

if __name__ == "__main__":
    main()
