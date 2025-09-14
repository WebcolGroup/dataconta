"""
Application ports - Interfaces that define contracts for external dependencies.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.domain.entities.invoice import Invoice, InvoiceFilter, License, APICredentials


class InvoiceRepository(ABC):
    """Port for invoice data access."""
    
    @abstractmethod
    def get_invoices(self, filters: InvoiceFilter) -> List[Invoice]:
        """Retrieve invoices based on filters."""
        pass
    
    @abstractmethod
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """Get a specific invoice by ID."""
        pass


class LicenseValidator(ABC):
    """Port for license validation."""
    
    @abstractmethod
    def validate_license(self, license_key: str) -> License:
        """Validate a license key and return license information."""
        pass
    
    @abstractmethod
    def is_license_valid(self, license_key: str) -> bool:
        """Check if a license key is valid."""
        pass


class FileStorage(ABC):
    """Port for file storage operations."""
    
    @abstractmethod
    def save_data(self, data: Dict[str, Any], filename: str) -> str:
        """Save data to file and return the file path."""
        pass
    
    @abstractmethod
    def list_files(self) -> List[str]:
        """List all saved files."""
        pass
    
    @abstractmethod
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get information about a specific file."""
        pass


class APIClient(ABC):
    """Port for API client operations."""
    
    @abstractmethod
    def authenticate(self, credentials: APICredentials) -> bool:
        """Authenticate with the API."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if API connection is active."""
        pass
    
    @abstractmethod
    def get_invoices(self, filters: InvoiceFilter) -> List[Dict[str, Any]]:
        """Retrieve invoices from the API."""
        pass


class Logger(ABC):
    """Port for logging operations."""
    
    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message."""
        pass
    
    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message."""
        pass


class UserInterface(ABC):
    """Port for user interface operations."""
    
    @abstractmethod
    def show_menu(self) -> str:
        """Display menu and return user selection."""
        pass
    
    @abstractmethod
    def get_invoice_filters(self) -> InvoiceFilter:
        """Get invoice filters from user input."""
        pass
    
    @abstractmethod
    def display_invoices(self, invoices: List[Invoice]) -> None:
        """Display invoices to user."""
        pass
    
    @abstractmethod
    def display_message(self, message: str, level: str = 'info') -> None:
        """Display a message to the user."""
        pass
    
    @abstractmethod
    def display_files(self, files: List[str]) -> None:
        """Display list of files to user."""
        pass


class ConfigurationProvider(ABC):
    """Port for configuration management."""
    
    @abstractmethod
    def get_api_credentials(self) -> APICredentials:
        """Get API credentials from configuration."""
        pass
    
    @abstractmethod
    def get_license_key(self) -> str:
        """Get license key from configuration."""
        pass
    
    @abstractmethod
    def get_license_url(self) -> str:
        """Get license validation URL from configuration."""
        pass
    
    @abstractmethod
    def get_output_directory(self) -> str:
        """Get output directory path from configuration."""
        pass


# ========================================================================================
# NUEVOS PUERTOS PARA EXPORTACIÓN DE FACTURAS (DataConta Export Service)
# ========================================================================================

class CSVExporter(ABC):
    """Port for CSV file export operations."""
    
    @abstractmethod
    def write_csv(self, file_path: str, headers: List[str], rows: List[List[str]]) -> bool:
        """
        Write data to CSV file.
        
        Args:
            file_path: Full path to the output CSV file
            headers: List of column headers
            rows: List of data rows (each row is a list of values)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def ensure_output_directory(self, directory_path: str) -> bool:
        """
        Ensure output directory exists.
        
        Args:
            directory_path: Path to the output directory
            
        Returns:
            True if directory exists or was created successfully
        """
        pass


class InvoiceProcessor(ABC):
    """Port for processing invoice data."""
    
    @abstractmethod
    def process_invoice_for_export(self, invoice_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process invoice data and convert to exportable format.
        
        Args:
            invoice_data: Raw invoice data from JSON
            
        Returns:
            List of processed rows ready for CSV export
        """
        pass
    
    @abstractmethod
    def validate_invoice_structure(self, invoice_data: Dict[str, Any]) -> bool:
        """
        Validate that invoice data has the required structure.
        
        Args:
            invoice_data: Raw invoice data to validate
            
        Returns:
            True if structure is valid, False otherwise
        """
        pass