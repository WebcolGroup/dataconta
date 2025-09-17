"""
License validation adapter - Implementation of LicenseValidator port with tiered licensing.
"""

import requests
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from src.application.ports.interfaces import LicenseValidator as LicenseValidatorPort, Logger
from src.domain.entities.invoice import License, LicenseType


class LicenseValidatorAdapter(LicenseValidatorPort):
    """Adapter for license validation with tiered licensing support."""
    
    def __init__(self, license_url: str, logger: Logger):
        self._license_url = license_url
        self._logger = logger
        self._session = requests.Session()
        self._session.timeout = 30
        self._session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'DataConta/2.1.0'
        })
        
        # Predefined license patterns for different tiers
        self._license_patterns = {
            LicenseType.FREE: ["FREE-", "DEMO-", "TEST-"],
            LicenseType.PROFESSIONAL: ["PROF-", "PRO-", "BUSINESS-"],
            LicenseType.ENTERPRISE: ["ENT-", "ENTERPRISE-", "CORP-"]
        }
    
    def validate_license(self, license_key: str) -> License:
        """Validate a license key and return license information with tier support."""
        try:
            if not self._validate_inputs(license_key):
                return self._create_invalid_license(license_key)
            
            # Special handling for demo licenses
            if self._is_demo_license(license_key):
                return self._create_demo_license(license_key)
            
            # Try online validation first if not in FREE tier
            license_type = self._detect_license_type(license_key)
            if license_type != LicenseType.FREE:
                try:
                    return self._validate_online(license_key, license_type)
                except requests.exceptions.ConnectionError:
                    self._logger.warning("License service unavailable, attempting offline validation")
                    return self._validate_offline(license_key, license_type)
            else:
                # FREE licenses always use offline validation
                return self._validate_offline(license_key, license_type)
            
        except Exception as e:
            self._logger.error(f"Error validating license: {e}")
            return self._create_error_license(license_key)
    
    def is_license_valid(self, license_key: str) -> bool:
        """Check if a license key is valid."""
        license_info = self.validate_license(license_key)
        return license_info.is_valid()
    
    def get_license_type_from_key(self, license_key: str) -> LicenseType:
        """Detect license type from key pattern."""
        return self._detect_license_type(license_key)
    
    def _detect_license_type(self, license_key: str) -> LicenseType:
        """Detect license type based on key pattern."""
        license_key_upper = license_key.upper()
        
        # Check patterns for each license type
        for license_type, patterns in self._license_patterns.items():
            if any(license_key_upper.startswith(pattern) for pattern in patterns):
                return license_type
        
        # Default fallback: detect by length and complexity
        if len(license_key) >= 25 and license_key.count('-') >= 4:
            return LicenseType.ENTERPRISE
        elif len(license_key) >= 15 and license_key.count('-') >= 3:
            return LicenseType.PROFESSIONAL
        else:
            return LicenseType.FREE
    
    def _is_demo_license(self, license_key: str) -> bool:
        """Check if this is a demo license."""
        demo_keys = [
            "DEMO-TEST-2024-LOCAL",
            "FREE-DEMO-2025",
            "TEST-LOCAL-DATACONTA"
        ]
        return license_key in demo_keys
    
    def _create_demo_license(self, license_key: str) -> License:
        """Create a demo license with appropriate tier."""
        self._logger.info("Using demo license for local testing")
        
        # Determine demo license type
        if "FREE" in license_key.upper():
            license_type = LicenseType.FREE
            features = ['invoice_query', 'api_access', 'file_storage']
        elif "PROF" in license_key.upper() or "PRO" in license_key.upper():
            license_type = LicenseType.PROFESSIONAL  
            features = ['invoice_query', 'api_access', 'file_storage', 'gui_access', 'financial_reports', 'bi_export_limited']
        else:
            # Default demo is FREE
            license_type = LicenseType.FREE
            features = ['invoice_query', 'api_access', 'file_storage']
        
        return License(
            key=license_key,
            license_type=license_type,
            status='active',
            expires_at=None,  # No expiration for demo
            features=features
        )
    
    def _create_invalid_license(self, license_key: str) -> License:
        """Create an invalid license."""
        return License(
            key=license_key,
            license_type=LicenseType.FREE,  # Default to most restrictive
            status='invalid',
            expires_at=None,
            features=[]
        )
    
    def _create_error_license(self, license_key: str) -> License:
        """Create an error license."""
        return License(
            key=license_key,
            license_type=LicenseType.FREE,  # Default to most restrictive
            status='error',
            expires_at=None,
            features=[]
        )
    
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
    
    def _validate_online(self, license_key: str, license_type: LicenseType) -> License:
        """Perform online license validation with tier support."""
        validation_data = {
            'license_key': license_key,
            'product': 'dataconta',
            'version': '2.1.0',
            'requested_tier': license_type.value
        }
        
        self._logger.info(f"Validating {license_type.value} license online with URL: {self._license_url}")
        
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
            
            # Get tier from response or use detected tier
            tier_str = response_data.get('tier', license_type.value)
            confirmed_license_type = LicenseType(tier_str) if tier_str in [t.value for t in LicenseType] else license_type
            
            features = self._get_features_for_license_type(confirmed_license_type)
            
            if is_valid:
                self._logger.info(f"License is valid. Type: {confirmed_license_type.value}, Status: {status}")
            else:
                error_message = response_data.get('message', 'License validation failed')
                self._logger.error(f"License is invalid: {error_message}")
            
            return License(
                key=license_key,
                license_type=confirmed_license_type,
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
    
    def _validate_offline(self, license_key: str, license_type: LicenseType) -> License:
        """Perform offline license validation with tier support."""
        if self._validate_offline_license_key(license_key):
            self._logger.info(f"Offline license validation successful for {license_type.value}")
            
            features = self._get_features_for_license_type(license_type)
            
            return License(
                key=license_key,
                license_type=license_type,
                status='active',
                expires_at=None,  # Cannot determine expiration offline
                features=features
            )
        else:
            self._logger.error("Offline license validation failed")
            return License(
                key=license_key,
                license_type=LicenseType.FREE,  # Fallback to most restrictive
                status='invalid',
                expires_at=None,
                features=[]
            )
    
    def _get_features_for_license_type(self, license_type: LicenseType) -> list[str]:
        """Get available features based on license type."""
        base_features = ['invoice_query', 'api_access', 'file_storage']
        
        if license_type == LicenseType.FREE:
            return base_features
        
        elif license_type == LicenseType.PROFESSIONAL:
            return base_features + [
                'gui_access',
                'financial_reports', 
                'bi_export_limited',
                'advanced_logging',
                'online_validation'
            ]
        
        elif license_type == LicenseType.ENTERPRISE:
            return base_features + [
                'gui_access',
                'financial_reports',
                'bi_export_unlimited', 
                'advanced_logging',
                'online_validation',
                'real_time_sync',
                'multi_user',
                'multi_company',
                'advanced_security',
                'pdf_export',
                'excel_export',
                'api_rest',
                'ai_predictions'
            ]
        
        return base_features
    
    def _validate_offline_license_key(self, license_key: str) -> bool:
        """Enhanced offline license key validation with tier support."""
        # Special case for demo/test licenses
        if self._is_demo_license(license_key):
            self._logger.info("Using demo license for local testing")
            return True
        
        # Simple validation: check if key has expected format
        if len(license_key) < 8:
            return False
        
        # Check different patterns based on license type
        license_type = self._detect_license_type(license_key)
        
        if license_type == LicenseType.FREE:
            # Less strict validation for FREE licenses
            return len(license_key) >= 8 and any(c.isalnum() for c in license_key)
        
        elif license_type == LicenseType.PROFESSIONAL:
            # Medium validation for PROFESSIONAL licenses
            if '-' in license_key:
                segments = license_key.split('-')
                return len(segments) >= 3 and all(len(segment) >= 3 for segment in segments)
            return len(license_key) >= 12
        
        elif license_type == LicenseType.ENTERPRISE:
            # Strict validation for ENTERPRISE licenses  
            if '-' in license_key:
                segments = license_key.split('-')
                return (len(segments) >= 4 and 
                       all(len(segment) >= 4 for segment in segments) and
                       len(license_key) >= 20)
            return len(license_key) >= 25
        
        return False