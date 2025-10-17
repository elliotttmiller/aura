"""
AI Provider Manager - Unified Multi-Provider LLM Integration
==============================================================

This module provides a unified interface for seamlessly switching between
different AI providers (LM Studio, OpenAI, Google AI, Anthropic, etc.) with
zero configuration conflicts.

Key Features:
- Automatic provider detection based on API keys
- Unified interface for all providers
- Seamless fallback between providers
- API key management
- Provider-specific optimizations
- Rate limiting and retry logic

Part of the V36 Universal Artisan production implementation.
"""

# Load environment configuration first
from backend.config_init import ensure_config_loaded
ensure_config_loaded(verbose=False)

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import requests

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers."""
    LM_STUDIO = "lm_studio"
    OPENAI = "openai"
    GOOGLE_AI = "google_ai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"


class AIProviderConfig:
    """Configuration for a specific AI provider."""
    
    def __init__(
        self,
        provider: AIProvider,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: int = 60
    ):
        self.provider = provider
        self.api_key = api_key
        self.api_url = api_url
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.enabled = self._check_enabled()
    
    def _check_enabled(self) -> bool:
        """Check if this provider is properly configured."""
        if self.provider == AIProvider.LM_STUDIO:
            # LM Studio doesn't require API key, just check URL
            return self.api_url is not None
        elif self.provider == AIProvider.OLLAMA:
            # Ollama doesn't require API key either
            return self.api_url is not None
        else:
            # Other providers require API key
            return self.api_key is not None and len(self.api_key) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'provider': self.provider.value,
            'enabled': self.enabled,
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'has_api_key': bool(self.api_key)
        }


class AIProviderManager:
    """
    Unified manager for multiple AI providers.
    
    Handles automatic provider detection, selection, and failover.
    """
    
    def __init__(self):
        """Initialize the AI provider manager."""
        self.providers: Dict[AIProvider, AIProviderConfig] = {}
        self._load_providers_from_env()
        self.active_provider: Optional[AIProvider] = self._select_active_provider()
        
        logger.info(f"AI Provider Manager initialized")
        logger.info(f"Active provider: {self.active_provider.value if self.active_provider else 'None'}")
        logger.info(f"Available providers: {[p.value for p in self.get_available_providers()]}")
    
    def _load_providers_from_env(self):
        """Load provider configurations from environment variables."""
        
        # LM Studio Configuration
        lm_studio_url = os.getenv('LM_STUDIO_URL', 'http://localhost:1234/v1/chat/completions')
        lm_studio_model = os.getenv('LM_STUDIO_MODEL', 'llama-3.1-8b-instruct')
        self.providers[AIProvider.LM_STUDIO] = AIProviderConfig(
            provider=AIProvider.LM_STUDIO,
            api_url=lm_studio_url,
            model_name=lm_studio_model,
            temperature=float(os.getenv('LM_STUDIO_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LM_STUDIO_MAX_TOKENS', '1000'))
        )
        
        # OpenAI Configuration
        openai_api_key = os.getenv('OPENAI_API_KEY', '')
        openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.providers[AIProvider.OPENAI] = AIProviderConfig(
            provider=AIProvider.OPENAI,
            api_key=openai_api_key,
            api_url='https://api.openai.com/v1/chat/completions',
            model_name=openai_model,
            temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
        )
        
        # Google AI (Gemini) Configuration
        google_api_key = os.getenv('GOOGLE_API_KEY', '')
        google_model = os.getenv('GOOGLE_MODEL', 'gemini-pro')
        self.providers[AIProvider.GOOGLE_AI] = AIProviderConfig(
            provider=AIProvider.GOOGLE_AI,
            api_key=google_api_key,
            api_url=f'https://generativelanguage.googleapis.com/v1beta/models/{google_model}:generateContent',
            model_name=google_model,
            temperature=float(os.getenv('GOOGLE_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('GOOGLE_MAX_TOKENS', '1000'))
        )
        
        # Anthropic (Claude) Configuration
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        anthropic_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        self.providers[AIProvider.ANTHROPIC] = AIProviderConfig(
            provider=AIProvider.ANTHROPIC,
            api_key=anthropic_api_key,
            api_url='https://api.anthropic.com/v1/messages',
            model_name=anthropic_model,
            temperature=float(os.getenv('ANTHROPIC_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('ANTHROPIC_MAX_TOKENS', '1000'))
        )
        
        # Hugging Face Configuration
        hf_api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        hf_model = os.getenv('HUGGINGFACE_MODEL', 'meta-llama/Meta-Llama-3.1-8B-Instruct')
        self.providers[AIProvider.HUGGINGFACE] = AIProviderConfig(
            provider=AIProvider.HUGGINGFACE,
            api_key=hf_api_key,
            api_url=f'https://api-inference.huggingface.co/models/{hf_model}',
            model_name=hf_model,
            temperature=float(os.getenv('HUGGINGFACE_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('HUGGINGFACE_MAX_TOKENS', '1000'))
        )
        
        # Azure OpenAI Configuration
        azure_api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
        azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', '')
        self.providers[AIProvider.AZURE_OPENAI] = AIProviderConfig(
            provider=AIProvider.AZURE_OPENAI,
            api_key=azure_api_key,
            api_url=f'{azure_endpoint}/openai/deployments/{azure_deployment}/chat/completions?api-version=2024-02-15-preview',
            model_name=azure_deployment,
            temperature=float(os.getenv('AZURE_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('AZURE_MAX_TOKENS', '1000'))
        )
        
        # Ollama Configuration (local)
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
        ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1')
        self.providers[AIProvider.OLLAMA] = AIProviderConfig(
            provider=AIProvider.OLLAMA,
            api_url=ollama_url,
            model_name=ollama_model,
            temperature=float(os.getenv('OLLAMA_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('OLLAMA_MAX_TOKENS', '1000'))
        )
    
    def _select_active_provider(self) -> Optional[AIProvider]:
        """
        Select the active AI provider based on priority and availability.
        
        Priority order:
        1. Explicit AI_PROVIDER environment variable
        2. First available provider with API key
        3. LM Studio (local, no API key needed)
        4. Ollama (local, no API key needed)
        """
        # Check for explicit provider selection
        explicit_provider = os.getenv('AI_PROVIDER', '').lower()
        if explicit_provider:
            for provider, config in self.providers.items():
                if provider.value == explicit_provider and config.enabled:
                    logger.info(f"Using explicitly configured provider: {provider.value}")
                    return provider
        
        # Priority order for automatic selection
        priority_order = [
            AIProvider.OPENAI,
            AIProvider.ANTHROPIC,
            AIProvider.GOOGLE_AI,
            AIProvider.AZURE_OPENAI,
            AIProvider.HUGGINGFACE,
            AIProvider.LM_STUDIO,
            AIProvider.OLLAMA,
        ]
        
        for provider in priority_order:
            if provider in self.providers and self.providers[provider].enabled:
                logger.info(f"Auto-selected provider: {provider.value}")
                return provider
        
        logger.warning("No AI provider configured or available")
        return None
    
    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available (enabled) providers."""
        return [
            provider for provider, config in self.providers.items()
            if config.enabled
        ]
    
    def set_active_provider(self, provider: AIProvider) -> bool:
        """
        Manually set the active provider.
        
        Args:
            provider: The provider to activate
            
        Returns:
            True if successful, False if provider not available
        """
        if provider in self.providers and self.providers[provider].enabled:
            self.active_provider = provider
            logger.info(f"Switched to provider: {provider.value}")
            return True
        else:
            logger.error(f"Cannot switch to provider {provider.value}: not available")
            return False
    
    def call_llm(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        provider: Optional[AIProvider] = None
    ) -> str:
        """
        Call LLM with automatic provider selection and fallback.
        
        Args:
            prompt: The user prompt
            system_message: System message for context
            provider: Specific provider to use (None = use active)
            
        Returns:
            LLM response text
            
        Raises:
            RuntimeError: If all providers fail
        """
        # Determine which provider to use
        target_provider = provider or self.active_provider
        
        if not target_provider:
            raise RuntimeError("No AI provider available")
        
        # Try the target provider
        try:
            return self._call_provider(target_provider, prompt, system_message)
        except Exception as e:
            logger.warning(f"Provider {target_provider.value} failed: {e}")
            
            # Try fallback providers
            available = self.get_available_providers()
            for fallback_provider in available:
                if fallback_provider != target_provider:
                    try:
                        logger.info(f"Trying fallback provider: {fallback_provider.value}")
                        return self._call_provider(fallback_provider, prompt, system_message)
                    except Exception as fallback_error:
                        logger.warning(f"Fallback provider {fallback_provider.value} failed: {fallback_error}")
            
            raise RuntimeError(f"All AI providers failed. Last error: {e}")
    
    def _call_provider(
        self,
        provider: AIProvider,
        prompt: str,
        system_message: str
    ) -> str:
        """Call a specific AI provider."""
        config = self.providers[provider]
        
        if provider == AIProvider.OPENAI:
            return self._call_openai(config, prompt, system_message)
        elif provider == AIProvider.GOOGLE_AI:
            return self._call_google(config, prompt, system_message)
        elif provider == AIProvider.ANTHROPIC:
            return self._call_anthropic(config, prompt, system_message)
        elif provider == AIProvider.HUGGINGFACE:
            return self._call_huggingface(config, prompt, system_message)
        elif provider == AIProvider.LM_STUDIO:
            return self._call_lm_studio(config, prompt, system_message)
        elif provider == AIProvider.AZURE_OPENAI:
            return self._call_azure_openai(config, prompt, system_message)
        elif provider == AIProvider.OLLAMA:
            return self._call_ollama(config, prompt, system_message)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _call_openai(self, config: AIProviderConfig, prompt: str, system_message: str) -> str:
        """Call OpenAI API."""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config.model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }
        
        response = requests.post(config.api_url, headers=headers, json=data, timeout=config.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _call_google(self, config: AIProviderConfig, prompt: str, system_message: str) -> str:
        """Call Google AI (Gemini) API."""
        url = f"{config.api_url}?key={config.api_key}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": f"{system_message}\n\n{prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": config.temperature,
                "maxOutputTokens": config.max_tokens
            }
        }
        
        response = requests.post(url, json=data, timeout=config.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    
    def _call_anthropic(self, config: AIProviderConfig, prompt: str, system_message: str) -> str:
        """Call Anthropic (Claude) API."""
        headers = {
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config.model_name,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "system": system_message,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(config.api_url, headers=headers, json=data, timeout=config.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result['content'][0]['text']
    
    def _call_huggingface(self, config: AIProviderConfig, prompt: str, system_message: str) -> str:
        """Call Hugging Face API."""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format for Llama models
        formatted_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        data = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": config.max_tokens,
                "temperature": config.temperature,
                "return_full_text": False
            }
        }
        
        response = requests.post(config.api_url, headers=headers, json=data, timeout=config.timeout)
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0]['generated_text']
        return str(result)
    
    def _call_lm_studio(self, config: AIProviderConfig, prompt: str, system_message: str) -> str:
        """Call LM Studio API (OpenAI-compatible)."""
        data = {
            "model": config.model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }
        
        response = requests.post(config.api_url, json=data, timeout=config.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _call_azure_openai(self, config: AIProviderConfig, prompt: str, system_message: str) -> str:
        """Call Azure OpenAI API."""
        headers = {
            "api-key": config.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }
        
        response = requests.post(config.api_url, headers=headers, json=data, timeout=config.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _call_ollama(self, config: AIProviderConfig, prompt: str, system_message: str) -> str:
        """Call Ollama API."""
        data = {
            "model": config.model_name,
            "prompt": f"{system_message}\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens
            }
        }
        
        response = requests.post(config.api_url, json=data, timeout=config.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result['response']
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all providers."""
        return {
            'active_provider': self.active_provider.value if self.active_provider else None,
            'available_providers': [p.value for p in self.get_available_providers()],
            'providers': {
                provider.value: config.to_dict()
                for provider, config in self.providers.items()
            }
        }


# Global provider manager instance
_provider_manager: Optional[AIProviderManager] = None


def get_ai_provider_manager() -> AIProviderManager:
    """Get or create the global AI provider manager."""
    global _provider_manager
    
    if _provider_manager is None:
        _provider_manager = AIProviderManager()
    
    return _provider_manager


def call_llm(
    prompt: str,
    system_message: str = "You are a helpful assistant.",
    provider: Optional[str] = None
) -> str:
    """
    Convenience function to call LLM with automatic provider management.
    
    Args:
        prompt: User prompt
        system_message: System context
        provider: Optional provider name (e.g., 'openai', 'google_ai')
        
    Returns:
        LLM response
    """
    manager = get_ai_provider_manager()
    
    # Convert provider string to enum if provided
    provider_enum = None
    if provider:
        try:
            provider_enum = AIProvider(provider.lower())
        except ValueError:
            logger.warning(f"Unknown provider: {provider}, using default")
    
    return manager.call_llm(prompt, system_message, provider_enum)
