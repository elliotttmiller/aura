"""
Aura Configuration Initializer
================================

This module ensures dotenv is properly loaded before any other imports.
Import this at the very top of main.py and other entry points.

Usage:
    from backend.config_init import ensure_config_loaded
    ensure_config_loaded()  # Call before any other imports
"""

import os
import sys
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] CONFIG %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Track if we've already initialized
_CONFIG_INITIALIZED = False


def find_project_root() -> Path:
    """
    Find the project root directory.
    
    Looks for markers like .env.example, .git, backend/, etc.
    """
    current = Path(__file__).parent.parent  # Start from repo root
    
    # Check current and parent directories
    for parent in [current] + list(current.parents)[:3]:
        markers = [
            parent / '.env.example',
            parent / '.git',
            parent / 'backend',
            parent / '3d_models',
        ]
        if any(marker.exists() for marker in markers):
            return parent
    
    # Fallback to directory containing this file
    return Path(__file__).parent.parent


def ensure_config_loaded(env_file: str = None, verbose: bool = True) -> bool:
    """
    Ensure .env configuration is loaded.
    
    This function:
    1. Finds the project root
    2. Loads .env files in priority order
    3. Validates critical configuration
    4. Only runs once (subsequent calls are no-ops)
    
    Args:
        env_file: Optional explicit .env file path
        verbose: Log detailed information
        
    Returns:
        True if config was loaded/already loaded, False if dotenv unavailable
    """
    global _CONFIG_INITIALIZED
    
    if _CONFIG_INITIALIZED:
        if verbose:
            logger.debug("Configuration already initialized")
        return True
    
    try:
        from dotenv import load_dotenv, find_dotenv
        dotenv_available = True
    except ImportError:
        logger.warning(
            "python-dotenv not installed. Install with: pip install python-dotenv"
        )
        logger.warning("Using system environment variables only")
        _CONFIG_INITIALIZED = True
        return False
    
    # Find project root
    project_root = find_project_root()
    if verbose:
        logger.info(f"Project root: {project_root}")
    
    loaded_files = []
    
    # Priority 1: Explicit env_file
    if env_file:
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(env_path, override=False)
            loaded_files.append(str(env_path))
    
    # Priority 2: Project root .env
    root_env = project_root / '.env'
    if root_env.exists():
        load_dotenv(root_env, override=False)
        loaded_files.append(str(root_env))
    
    # Priority 3: Auto-find .env
    found_env = find_dotenv(usecwd=True)
    if found_env and found_env not in loaded_files:
        load_dotenv(found_env, override=False)
        loaded_files.append(found_env)
    
    # Log results
    if loaded_files:
        if verbose:
            for env_file in loaded_files:
                logger.info(f"✓ Loaded: {env_file}")
            logger.info(f"✓ Configuration loaded from {len(loaded_files)} file(s)")
    else:
        logger.warning("⚠ No .env file found")
        logger.info(f"  Create {project_root / '.env'} from .env.example")
    
    _CONFIG_INITIALIZED = True
    return True


def get_project_root() -> Path:
    """Get the project root directory."""
    return find_project_root()


def validate_critical_config() -> dict:
    """
    Validate that critical configuration is present.
    
    Returns:
        Dict with validation results
    """
    validation = {
        'status': 'ok',
        'warnings': [],
        'errors': [],
        'config_loaded': _CONFIG_INITIALIZED
    }
    
    # Check critical env vars
    critical_vars = {
        'BACKEND_PORT': '8001',
        'BACKEND_HOST': 'localhost',
    }
    
    for var, default in critical_vars.items():
        value = os.getenv(var)
        if not value:
            validation['warnings'].append(f"{var} not set, will use default: {default}")
    
    # Check optional but recommended vars
    recommended_vars = [
        'OPENAI_API_KEY',
        'GOOGLE_API_KEY', 
        'LM_STUDIO_URL',
        'BLENDER_PATH',
    ]
    
    has_ai_provider = False
    for var in recommended_vars:
        if os.getenv(var):
            has_ai_provider = True
            break
    
    if not has_ai_provider:
        validation['warnings'].append(
            "No AI provider configured (OpenAI, Google AI, or LM Studio)"
        )
    
    if validation['errors']:
        validation['status'] = 'error'
    elif validation['warnings']:
        validation['status'] = 'warning'
    
    return validation


# Auto-initialize when module is imported
if __name__ != '__main__':
    # Auto-load config when imported (but not when run as script)
    ensure_config_loaded(verbose=False)
