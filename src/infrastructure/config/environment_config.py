"""
Configuration provider - Implementation of ConfigurationProvider port.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from src.application.ports.interfaces import ConfigurationProvider, Logger
from src.domain.entities.invoice import APICredentials


class EnvironmentConfigurationProvider(ConfigurationProvider):
    """Configuration provider using environment variables."""
    
    def __init__(self, logger: Logger, env_file: str = ".env"):
        self._logger = logger
        self._load_environment(env_file)
    
    def get_api_credentials(self) -> APICredentials:
        """Get API credentials from configuration."""
        return APICredentials(
            username=os.getenv('SIIGO_USER', ''),
            access_key=os.getenv('SIIGO_ACCESS_KEY', ''),
            api_url=os.getenv('SIIGO_API_URL', ''),
            partner_id=os.getenv('PARTNER_ID')
        )
    
    def get_license_key(self) -> str:
        """Get license key from configuration."""
        return os.getenv('LICENSE_KEY', '')
    
    def get_license_url(self) -> str:
        """Get license validation URL from configuration."""
        return os.getenv('LICENSE_URL', '')
    
    def get_output_directory(self) -> str:
        """Get output directory path from configuration."""
        return os.getenv('OUTPUT_DIR', './outputs')
    
    def _load_environment(self, env_file: str) -> None:
        """Load environment variables from .env file."""
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(env_path)
            self._logger.info("Environment variables loaded successfully")
        else:
            self._logger.warning(f"{env_file} file not found")
    
    def validate_configuration(self) -> tuple[bool, list[str]]:
        """Validate that all required configuration is present."""
        required_vars = [
            'SIIGO_API_URL',
            'SIIGO_USER',
            'SIIGO_ACCESS_KEY',
            'LICENSE_URL',
            'LICENSE_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            self._logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False, missing_vars
        
        return True, []