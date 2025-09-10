"""
Aura V24 Environment Configuration Manager
==========================================

Centralized environment variable management with validation and fallbacks.
This module handles loading .env files and providing typed configuration
access throughout the Aura system.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

# Import dotenv with graceful fallback
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available, using system environment only")

logger = logging.getLogger(__name__)

class EnvironmentConfig:
    """Centralized configuration manager for Aura system."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.env_file = env_file or '.env'
        self.config_cache: Dict[str, Any] = {}
        self._load_environment()
        
    def _load_environment(self):
        """Load environment variables from .env file if available."""
        if DOTENV_AVAILABLE:
            env_path = Path(self.env_file)
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"Loaded environment from {env_path}")
            else:
                logger.warning(f"Environment file {env_path} not found, using system environment")
        
        # Cache frequently accessed configurations
        self._cache_config()
    
    def _cache_config(self):
        """Cache frequently accessed configuration values."""
        self.config_cache = {
            # Core system
            'environment': self.get('ENVIRONMENT', 'development'),
            'debug_mode': self.get_bool('DEBUG_MODE', True),
            'log_level': self.get('LOG_LEVEL', 'INFO'),
            
            # LM Studio
            'lm_studio_url': self.get('LM_STUDIO_URL', 'http://localhost:1234/v1/chat/completions'),
            'lm_studio_model': self.get('LM_STUDIO_MODEL_NAME', 'meta-llama-3.1-8b-instruct'),
            'lm_studio_timeout': self.get_int('LM_STUDIO_TIMEOUT', 30),
            
            # AI Server
            'ai_server_host': self.get('AI_SERVER_HOST', '0.0.0.0'),
            'ai_server_port': self.get_int('AI_SERVER_PORT', 8002),
            'ai_server_url': self.get('AI_SERVER_URL', 'http://localhost:8002'),
            
            # Backend
            'backend_host': self.get('BACKEND_HOST', 'localhost'),
            'backend_port': self.get_int('BACKEND_PORT', 8001),
            
            # Sandbox
            'sandbox_mode': self.get_bool('SANDBOX_MODE', False),
            'sandbox_port': self.get_int('SANDBOX_SERVER_PORT', 8003),
            
            # Blender
            'blender_path': self.get('BLENDER_PATH', ''),
            'blender_background': self.get_bool('BLENDER_BACKGROUND', True),
            'blender_timeout': self.get_int('BLENDER_TIMEOUT', 120),
            
            # Directories
            'output_dir': self.get('OUTPUT_DIR', './output'),
            'models_dir': self.get('MODELS_DIR', './models'),
            'cache_dir': self.get('CACHE_DIR', './cache'),
            'logs_dir': self.get('LOGS_DIR', './logs'),
        }
    
    def get(self, key: str, default: Any = None) -> str:
        """Get string environment variable with optional default."""
        return os.getenv(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable with optional default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}, using default {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float environment variable with optional default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float value for {key}: {value}, using default {default}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable with optional default."""
        value = os.getenv(key, '').lower()
        if value in ('true', '1', 'yes', 'on'):
            return True
        elif value in ('false', '0', 'no', 'off'):
            return False
        return default
    
    def get_list(self, key: str, default: List[str] = None, separator: str = ',') -> List[str]:
        """Get list environment variable with optional default."""
        if default is None:
            default = []
        value = os.getenv(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(separator)]
    
    def require(self, key: str) -> str:
        """Get required environment variable, raise error if not found."""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable {key} not set")
        return value
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate current configuration and return any issues."""
        issues = {
            'missing': [],
            'invalid': [],
            'warnings': []
        }
        
        # Check required paths
        if self.get('BLENDER_PATH'):
            blender_path = Path(self.get('BLENDER_PATH'))
            if not blender_path.exists():
                issues['invalid'].append(f"Blender executable not found: {blender_path}")
        
        # Check directory permissions
        for dir_key in ['OUTPUT_DIR', 'MODELS_DIR', 'CACHE_DIR', 'LOGS_DIR']:
            dir_path = Path(self.get(dir_key, '.'))
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                issues['invalid'].append(f"Cannot create directory: {dir_path}")
        
        # Check port conflicts
        ports = [
            self.get_int('LM_STUDIO_PORT', 1234),
            self.get_int('AI_SERVER_PORT', 8002),
            self.get_int('BACKEND_PORT', 8001),
            self.get_int('SANDBOX_SERVER_PORT', 8003)
        ]
        if len(ports) != len(set(ports)):
            issues['invalid'].append("Port conflicts detected in configuration")
        
        # Check resource limits
        max_memory = self.get_int('MAX_MEMORY_GB', 8)
        if max_memory < 4:
            issues['warnings'].append("Low memory limit may affect performance")
        
        return issues
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        service_configs = {
            'lm_studio': {
                'host': self.get('LM_STUDIO_HOST', 'localhost'),
                'port': self.get_int('LM_STUDIO_PORT', 1234),
                'url': self.get('LM_STUDIO_URL'),
                'model': self.get('LM_STUDIO_MODEL_NAME'),
                'timeout': self.get_int('LM_STUDIO_TIMEOUT', 30),
                'max_tokens': self.get_int('LM_STUDIO_MAX_TOKENS', 4096),
                'temperature': self.get_float('LM_STUDIO_TEMPERATURE', 0.7)
            },
            'ai_server': {
                'host': self.get('AI_SERVER_HOST', '0.0.0.0'),
                'port': self.get_int('AI_SERVER_PORT', 8002),
                'url': self.get('AI_SERVER_URL'),
                'workers': self.get_int('AI_SERVER_WORKERS', 1),
                'timeout': self.get_int('AI_SERVER_TIMEOUT', 300)
            },
            'backend': {
                'host': self.get('BACKEND_HOST', 'localhost'),
                'port': self.get_int('BACKEND_PORT', 8001),
                'url': self.get('BACKEND_URL'),
                'workers': self.get_int('BACKEND_WORKERS', 1)
            },
            'sandbox': {
                'host': self.get('SANDBOX_SERVER_HOST', '0.0.0.0'),
                'port': self.get_int('SANDBOX_SERVER_PORT', 8003),
                'url': self.get('SANDBOX_SERVER_URL'),
                'enabled': self.get_bool('SANDBOX_MODE', False)
            },
            'blender': {
                'path': self.get('BLENDER_PATH'),
                'background': self.get_bool('BLENDER_BACKGROUND', True),
                'timeout': self.get_int('BLENDER_TIMEOUT', 120),
                'addon_path': self.get('BLENDER_ADDON_PATH', '.')
            }
        }
        
        return service_configs.get(service_name, {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring and diagnostics configuration."""
        return {
            'metrics_enabled': self.get_bool('METRICS_ENABLED', True),
            'metrics_port': self.get_int('METRICS_PORT', 9090),
            'health_check_interval': self.get_int('HEALTH_CHECK_INTERVAL', 30),
            'performance_monitoring': self.get_bool('PERFORMANCE_MONITORING', True),
            'gpu_monitoring': self.get_bool('GPU_MONITORING', True),
            'memory_monitoring': self.get_bool('MEMORY_MONITORING', True)
        }
    
    def __getitem__(self, key: str) -> str:
        """Allow dictionary-style access to environment variables."""
        return self.get(key)
    
    def __contains__(self, key: str) -> bool:
        """Check if environment variable exists."""
        return os.getenv(key) is not None

# Global configuration instance
config = EnvironmentConfig()

# Convenience functions for common access patterns
def get_lm_studio_url() -> str:
    """Get LM Studio URL."""
    return config.config_cache['lm_studio_url']

def get_ai_server_config() -> Dict[str, Any]:
    """Get AI server configuration."""
    return config.get_service_config('ai_server')

def is_sandbox_mode() -> bool:
    """Check if running in sandbox mode."""
    return config.config_cache['sandbox_mode']

def get_blender_path() -> str:
    """Get Blender executable path."""
    return config.config_cache['blender_path']

def validate_system_config() -> Dict[str, List[str]]:
    """Validate system configuration."""
    return config.validate_configuration()