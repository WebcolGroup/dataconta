"""
Application ports - Interfaces that define contracts for external dependencies.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.domain.entities.invoice import Invoice, InvoiceFilter, License, APICredentials
from src.domain.entities.financial_reports import (
    EstadoResultados, BalanceGeneral, CuentaContable, 
    PeriodoFiscal, InformeFinancieroResumen
)


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


# ========================================================================================
# PUERTOS PARA INFORMES FINANCIEROS (Estado de Resultados y Estado de Situación Financiera)
# ========================================================================================

class EstadoResultadosRepository(ABC):
    """Port for Estado de Resultados (P&L) data access."""
    
    @abstractmethod
    def obtener_estado_resultados(self, periodo: PeriodoFiscal) -> EstadoResultados:
        """
        Obtener Estado de Resultados para un período específico.
        
        Args:
            periodo: Período fiscal para el cual generar el informe
            
        Returns:
            EstadoResultados con los datos calculados
        """
        pass
    
    @abstractmethod
    def obtener_ventas_periodo(self, periodo: PeriodoFiscal) -> List[Dict[str, Any]]:
        """
        Obtener todas las ventas (facturas) del período.
        
        Args:
            periodo: Período fiscal
            
        Returns:
            Lista de facturas/ventas del período
        """
        pass
    
    @abstractmethod
    def obtener_compras_periodo(self, periodo: PeriodoFiscal) -> List[Dict[str, Any]]:
        """
        Obtener todas las compras del período.
        
        Args:
            periodo: Período fiscal
            
        Returns:
            Lista de compras del período
        """
        pass
    
    @abstractmethod
    def obtener_gastos_periodo(self, periodo: PeriodoFiscal) -> List[Dict[str, Any]]:
        """
        Obtener todos los gastos operativos del período.
        
        Args:
            periodo: Período fiscal
            
        Returns:
            Lista de gastos operativos del período
        """
        pass


class BalanceGeneralRepository(ABC):
    """Port for Estado de Situación Financiera data access."""
    
    @abstractmethod
    def obtener_balance_general(self, fecha_corte: datetime) -> BalanceGeneral:
        """
        Obtener Balance General para una fecha de corte específica.
        
        Args:
            fecha_corte: Fecha de corte para el balance
            
        Returns:
            BalanceGeneral con los datos calculados
        """
        pass
    
    @abstractmethod
    def obtener_balance_prueba(self, fecha_corte: datetime) -> List[CuentaContable]:
        """
        Obtener balance de prueba para una fecha específica.
        
        Args:
            fecha_corte: Fecha de corte para el balance
            
        Returns:
            Lista de cuentas contables con sus saldos
        """
        pass
    
    @abstractmethod
    def obtener_activos_corrientes(self, fecha_corte: datetime) -> List[CuentaContable]:
        """Obtener cuentas de activos corrientes."""
        pass
    
    @abstractmethod
    def obtener_activos_no_corrientes(self, fecha_corte: datetime) -> List[CuentaContable]:
        """Obtener cuentas de activos no corrientes."""
        pass
    
    @abstractmethod
    def obtener_pasivos_corrientes(self, fecha_corte: datetime) -> List[CuentaContable]:
        """Obtener cuentas de pasivos corrientes."""
        pass
    
    @abstractmethod
    def obtener_pasivos_no_corrientes(self, fecha_corte: datetime) -> List[CuentaContable]:
        """Obtener cuentas de pasivos no corrientes."""
        pass
    
    @abstractmethod
    def obtener_patrimonio(self, fecha_corte: datetime) -> List[CuentaContable]:
        """Obtener cuentas de patrimonio."""
        pass


class CatalogoContableRepository(ABC):
    """Port for chart of accounts management."""
    
    @abstractmethod
    def obtener_cuenta(self, codigo_cuenta: str) -> Optional[CuentaContable]:
        """Obtener una cuenta específica por código."""
        pass
    
    @abstractmethod
    def obtener_cuentas_por_tipo(self, tipo_cuenta: str) -> List[CuentaContable]:
        """Obtener todas las cuentas de un tipo específico."""
        pass
    
    @abstractmethod
    def obtener_catalogo_completo(self) -> List[CuentaContable]:
        """Obtener el catálogo completo de cuentas."""
        pass


class InformeFinancieroRepository(ABC):
    """Port for comprehensive financial report generation."""
    
    @abstractmethod
    def generar_informe_completo(
        self, 
        periodo: PeriodoFiscal, 
        fecha_corte_balance: datetime
    ) -> InformeFinancieroResumen:
        """
        Generar informe financiero completo combinando Estado de Resultados y Balance General.
        
        Args:
            periodo: Período para el Estado de Resultados
            fecha_corte_balance: Fecha de corte para el Balance General
            
        Returns:
            InformeFinancieroResumen completo con ambos informes y KPIs
        """
        pass
    
    @abstractmethod
    def validar_coherencia_informes(
        self, 
        estado_resultados: EstadoResultados, 
        balance_general: BalanceGeneral
    ) -> bool:
        """Validar que los informes sean coherentes entre sí."""
        pass


class SiigoFinancialAPIClient(ABC):
    """Port específico para consumir APIs financieras de Siigo."""
    
    @abstractmethod
    def obtener_facturas_periodo(
        self, 
        fecha_inicio: str, 
        fecha_fin: str,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtener facturas de un período desde la API de Siigo."""
        pass
    
    @abstractmethod
    def obtener_notas_credito_periodo(
        self, 
        fecha_inicio: str, 
        fecha_fin: str,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtener notas de crédito de un período desde la API de Siigo."""
        pass
    
    @abstractmethod
    def obtener_compras_periodo(
        self, 
        fecha_inicio: str, 
        fecha_fin: str,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtener compras de un período desde la API de Siigo."""
        pass
    
    @abstractmethod
    def obtener_asientos_contables_periodo(
        self, 
        fecha_inicio: str, 
        fecha_fin: str,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtener asientos contables de un período desde la API de Siigo."""
        pass
    
    @abstractmethod
    def obtener_balance_prueba(self, fecha_corte: str) -> Dict[str, Any]:
        """Obtener balance de prueba desde la API de Siigo."""
        pass