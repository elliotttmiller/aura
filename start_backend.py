#!/usr/bin/env python3
"""
Aura Backend Startup Script
============================

This script ensures proper environment configuration loading before starting
the FastAPI backend server.

Usage:
    python start.py
    python start.py --port 8001 --host 0.0.0.0
"""

import sys
import os
from pathlib import Path

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
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
except KeyboardInterrupt:
    print("\n\n" + "=" * 80)
    print("Server stopped by user")
    print("=" * 80)
except Exception as e:
    print(f"\n⚠ Server error: {e}")
    sys.exit(1)
