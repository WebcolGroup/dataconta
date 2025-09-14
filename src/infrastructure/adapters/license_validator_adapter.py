"""
License validation adapter - Implementation of LicenseValidator port.
"""

import requests
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from src.application.ports.interfaces import LicenseValidator as LicenseValidatorPort, Logger
from src.domain.entities.invoice import License


class LicenseValidatorAdapter(LicenseValidatorPort):
    """Adapter for license validation."""
    
    def __init__(self, license_url: str, logger: Logger):
        self._license_url = license_url
        self._logger = logger
        self._session = requests.Session()
        self._session.timeout = 30
        self._session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'SiigoAPI-CLI/1.0'
        })
    
    def validate_license(self, license_key: str) -> License:
        """Validate a license key and return license information."""
        try:
            if not self._validate_inputs(license_key):
                return License(
                    key=license_key,
                    status='invalid',
                    expires_at=None,
                    features=[]
                )
            
            # Special handling for demo license
            if license_key == "DEMO-TEST-2024-LOCAL":
                self._logger.info("Using demo license for local testing")
                return License(
                    key=license_key,
                    status='active',
                    expires_at=None,  # No expiration for demo
                    features=['invoice_query', 'api_access', 'file_storage']
                )
            
            # Try online validation first
            try:
                return self._validate_online(license_key)
            except requests.exceptions.ConnectionError:
                self._logger.warning("License service unavailable, attempting offline validation")
                return self._validate_offline(license_key)
            
        except Exception as e:
            self._logger.error(f"Error validating license: {e}")
            return License(
                key=license_key,
                status='error',
                expires_at=None,
                features=[]
            )
    
    def is_license_valid(self, license_key: str) -> bool:
        """Check if a license key is valid."""
        license_info = self.validate_license(license_key)
        return license_info.is_valid()
    
    def _validate_inputs(self, license_key: str) -> bool:
        """Validate input parameters."""
        if not license_key or not license_key.strip():
            self._logger.error("License key is empty or not provided")
            return False
        
        if not self._license_url or not self._license_url.strip():
            self._logger.error("License URL is empty or not provided")
            return False
        
        try:
            parsed_url = urlparse(self._license_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                self._logger.error(f"Invalid license URL format: {self._license_url}")
                return False
        except Exception as e:
            self._logger.error(f"Error parsing license URL: {e}")
            return False
        
        return True
    
    def _validate_online(self, license_key: str) -> License:
        """Perform online license validation."""
        validation_data = {
            'license_key': license_key,
            'product': 'siigo-api-cli',
            'version': '1.0.0'
        }
        
        self._logger.info(f"Validating license online with URL: {self._license_url}")
        
        response = self._session.post(
            self._license_url,
            json=validation_data,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            is_valid = response_data.get('valid', False)
            status = 'active' if is_valid else 'invalid'
            expires_at = None
            
            if response_data.get('expires_at'):
                expires_at = datetime.fromisoformat(response_data['expires_at'])
            
            features = response_data.get('features', [])
            
            if is_valid:
                self._logger.info(f"License is valid. Status: {status}")
            else:
                error_message = response_data.get('message', 'License validation failed')
                self._logger.error(f"License is invalid: {error_message}")
            
            return License(
                key=license_key,
                status=status,
                expires_at=expires_at,
                features=features
            )
        else:
            # Handle error response
            try:
                error_data = response.json()
                error_message = error_data.get('message', 'Unknown error')
            except (ValueError, KeyError):
                error_message = response.text or f"HTTP {response.status_code}"
            
            self._logger.error(f"License validation failed: {response.status_code} - {error_message}")
            raise Exception(f"Online validation failed: {error_message}")
    
    def _validate_offline(self, license_key: str) -> License:
        """Perform offline license validation."""
        # Simple offline validation based on license key format
        if self._validate_offline_license_key(license_key):
            self._logger.info("Offline license validation successful")
            return License(
                key=license_key,
                status='active',
                expires_at=None,  # Cannot determine expiration offline
                features=['invoice_query', 'api_access']  # Basic features
            )
        else:
            self._logger.error("Offline license validation failed")
            return License(
                key=license_key,
                status='invalid',
                expires_at=None,
                features=[]
            )
    
    def _validate_offline_license_key(self, license_key: str) -> bool:
        """Simple offline license key validation."""
        # Special case for demo/test license
        if license_key == "DEMO-TEST-2024-LOCAL":
            self._logger.info("Using demo license for local testing")
            return True
        
        # Simple validation: check if key has expected format
        if len(license_key) < 10:
            return False
        
        # Check if key contains required segments (example format: XXXX-XXXX-XXXX)
        if '-' in license_key:
            segments = license_key.split('-')
            if len(segments) >= 3 and all(len(segment) >= 4 for segment in segments):
                return True
        
        return False