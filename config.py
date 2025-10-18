"""
Aura Environment Configuration Manager
======================================
Centralized environment variable management with validation and fallbacks.
This module handles loading .env files and providing typed configuration access throughout the Aura system.
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

	def _cache_config(self):
		"""Cache frequently accessed configuration values for quick access."""
		self.config_cache = {
			# Core system
			'environment': self.get('ENVIRONMENT', 'development'),
			'debug_mode': self.get_bool('DEBUG_MODE', False),
			'log_level': self.get('LOG_LEVEL', 'INFO'),

			# Backend
			'backend_host': self.get('BACKEND_HOST', '0.0.0.0'),
			'backend_port': self.get_int('BACKEND_PORT', 8001),
			'backend_workers': self.get_int('BACKEND_WORKERS', 1),

			# LM Studio (local LLM)
			'lm_studio_url': self.get('LM_STUDIO_URL', 'http://localhost:1234/v1/chat/completions'),
			'lm_studio_model': self.get('LM_STUDIO_MODEL_NAME', 'meta-llama-3.1-8b-instruct'),
			'lm_studio_timeout': self.get_int('LM_STUDIO_TIMEOUT', 30),
			'lm_studio_max_tokens': self.get_int('LM_STUDIO_MAX_TOKENS', 4096),
			'lm_studio_temperature': self.get_float('LM_STUDIO_TEMPERATURE', 0.7),

			# AI Server (external)
			'ai_server_url': self.get('AI_SERVER_URL', 'http://localhost:8002'),
			'ai_server_host': self.get('AI_SERVER_HOST', '0.0.0.0'),
			'ai_server_port': self.get_int('AI_SERVER_PORT', 8002),
			'ai_server_workers': self.get_int('AI_SERVER_WORKERS', 1),
			'ai_server_timeout': self.get_int('AI_SERVER_TIMEOUT', 300),

			# Sandbox mode
			'sandbox_mode': self.get_bool('SANDBOX_MODE', False),
			'sandbox_server_host': self.get('SANDBOX_SERVER_HOST', '0.0.0.0'),
			'sandbox_server_port': self.get_int('SANDBOX_SERVER_PORT', 8003),
			'sandbox_server_url': self.get('SANDBOX_SERVER_URL', ''),

			# Blender
			'blender_path': self.get('BLENDER_PATH', ''),
			'blender_background': self.get_bool('BLENDER_BACKGROUND', True),
			'blender_timeout': self.get_int('BLENDER_TIMEOUT', 300),
			'blender_addon_path': self.get('BLENDER_ADDON_PATH', ''),

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
		issues: Dict[str, List[str]] = {
			'missing': [],
			'invalid': [],
			'warnings': []
		}

		# Check Blender path if provided
		blender_path = self.get('BLENDER_PATH', '')
		if blender_path:
			p = Path(blender_path)
			if not p.exists():
				issues['invalid'].append(f"Blender executable not found: {p}")

		# Ensure directories are creatable
		for dir_key in ['OUTPUT_DIR', 'MODELS_DIR', 'CACHE_DIR', 'LOGS_DIR']:
			dir_path = Path(self.get(dir_key, '.'))
			try:
				dir_path.mkdir(parents=True, exist_ok=True)
			except Exception:
				issues['invalid'].append(f"Cannot create/access directory: {dir_path}")

		# Port conflict quick check
		ports = [
			self.get_int('LM_STUDIO_PORT', 1234),
			self.get_int('AI_SERVER_PORT', 8002),
			self.get_int('BACKEND_PORT', 8001),
			self.get_int('SANDBOX_SERVER_PORT', 8003),
		]
		if len(ports) != len(set(ports)):
			issues['invalid'].append('Port conflicts detected in configuration')

		# Warn on low resource defaults
		max_memory_gb = self.get_int('MAX_MEMORY_GB', 8)
		if max_memory_gb < 4:
			issues['warnings'].append('Low memory limit may affect performance')

		return issues

	def get_service_config(self, service_name: str) -> Dict[str, Any]:
		"""Get configuration for a specific service block."""
		if service_name == 'lm_studio':
			return {
				'url': self.config_cache.get('lm_studio_url'),
				'host': self.get('LM_STUDIO_HOST', 'localhost'),
				'port': self.get_int('LM_STUDIO_PORT', 1234),
				'model': self.config_cache.get('lm_studio_model'),
				'timeout': self.config_cache.get('lm_studio_timeout'),
				'max_tokens': self.config_cache.get('lm_studio_max_tokens'),
				'temperature': self.config_cache.get('lm_studio_temperature'),
			}
		elif service_name == 'ai_server':
			return {
				'url': self.config_cache.get('ai_server_url'),
				'host': self.config_cache.get('ai_server_host'),
				'port': self.config_cache.get('ai_server_port'),
				'workers': self.config_cache.get('ai_server_workers'),
				'timeout': self.config_cache.get('ai_server_timeout'),
			}
		elif service_name == 'backend':
			return {
				'host': self.config_cache.get('backend_host'),
				'port': self.config_cache.get('backend_port'),
				'workers': self.config_cache.get('backend_workers'),
			}
		elif service_name == 'sandbox':
			return {
				'host': self.config_cache.get('sandbox_server_host'),
				'port': self.config_cache.get('sandbox_server_port'),
				'url': self.config_cache.get('sandbox_server_url'),
				'enabled': self.config_cache.get('sandbox_mode'),
			}
		elif service_name == 'blender':
			return {
				'path': self.config_cache.get('blender_path'),
				'background': self.config_cache.get('blender_background'),
				'timeout': self.config_cache.get('blender_timeout'),
				'addon_path': self.config_cache.get('blender_addon_path'),
			}
		return {}

	def get_monitoring_config(self) -> Dict[str, Any]:
		"""Get monitoring and diagnostics configuration."""
		return {
			'metrics_enabled': self.get_bool('METRICS_ENABLED', True),
			'metrics_port': self.get_int('METRICS_PORT', 9090),
			'health_check_interval': self.get_int('HEALTH_CHECK_INTERVAL', 30),
			'performance_monitoring': self.get_bool('PERFORMANCE_MONITORING', True),
			'gpu_monitoring': self.get_bool('GPU_MONITORING', True),
			'memory_monitoring': self.get_bool('MEMORY_MONITORING', True),
		}

	def __getitem__(self, key: str) -> str:
		"""Allow dictionary-style access to environment variables."""
		return self.get(key)

	def __contains__(self, key: str) -> bool:
		"""Check if environment variable exists."""
		return os.getenv(key) is not None


# --- Global configuration instance and convenience functions ---
config = EnvironmentConfig()

def get_lm_studio_url() -> str:
	"""Get LM Studio URL."""
	return config.config_cache.get('lm_studio_url', '')

def get_ai_server_config() -> Dict[str, Any]:
	"""Get AI server configuration."""
	return config.get_service_config('ai_server')

def is_sandbox_mode() -> bool:
	"""Check if running in sandbox mode."""
	return config.config_cache.get('sandbox_mode', False)

def get_blender_path() -> str:
	"""Get Blender executable path."""
	return config.config_cache.get('blender_path', '')

def validate_system_config() -> Dict[str, List[str]]:
	"""Validate system configuration."""
	return config.validate_configuration()

