"""
License Manager - Centralized license validation and access control.
"""

from typing import Optional, Dict, Any
from src.domain.entities.invoice import License, LicenseType, LicenseLimits
from src.application.ports.interfaces import Logger


class LicenseManager:
    """
    Centralized manager for license validation and access control.
    
    This service acts as the single source of truth for license-based
    functionality access throughout the application.
    """
    
    def __init__(self, logger: Logger):
        self._logger = logger
        self._current_license: Optional[License] = None
        self._license_limits: Optional[LicenseLimits] = None
    
    def set_license(self, license_info: License) -> None:
        """Set the current license and update limits."""
        self._current_license = license_info
        self._license_limits = license_info.limits
        
        if license_info.is_valid():
            self._logger.info(f"License set successfully: {license_info.license_type.display_name}")
        else:
            self._logger.warning(f"Invalid license set: {license_info.status}")
    
    def get_license(self) -> Optional[License]:
        """Get the current license."""
        return self._current_license
    
    def get_license_type(self) -> LicenseType:
        """Get current license type, defaulting to FREE if not set."""
        if self._current_license:
            return self._current_license.license_type
        return LicenseType.FREE
    
    def get_license_display_name(self) -> str:
        """Get display name for current license."""
        return self.get_license_type().display_name
    
    def is_license_valid(self) -> bool:
        """Check if current license is valid."""
        return self._current_license is not None and self._current_license.is_valid()
    
    # ========================================================================================
    # ACCESS CONTROL METHODS
    # ========================================================================================
    
    def can_access_gui(self) -> bool:
        """Check if current license allows GUI access."""
        if not self.is_license_valid():
            return False
        return self._current_license.can_access_gui()
    
    def can_generate_financial_reports(self) -> bool:
        """Check if current license allows financial reports generation."""
        if not self.is_license_valid():
            return False
        return self._current_license.can_generate_financial_reports()
    
    def can_export_bi(self) -> bool:
        """Check if current license allows BI export."""
        if not self.is_license_valid():
            return False
        return self._current_license.can_export_bi()
    
    def can_use_advanced_features(self) -> bool:
        """Check if current license allows advanced features (Enterprise only)."""
        if not self.is_license_valid():
            return False
        return self.get_license_type().has_advanced_features
    
    def can_use_advanced_logging(self) -> bool:
        """Check if current license allows advanced logging."""
        if not self.is_license_valid():
            return False
        return self._license_limits.advanced_logging if self._license_limits else False
    
    def requires_online_validation(self) -> bool:
        """Check if current license requires online validation."""
        if not self.is_license_valid():
            return False
        return self._license_limits.online_validation if self._license_limits else False
    
    # ========================================================================================
    # LIMITS VALIDATION METHODS
    # ========================================================================================
    
    def validate_invoice_query_limit(self, requested_count: int) -> tuple[bool, str]:
        """
        Validate if requested invoice count is within license limits for query operations.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not self.is_license_valid():
            return False, "Licencia inválida o no configurada"
        
        max_allowed = self._current_license.get_max_invoices_query()
        
        if requested_count <= max_allowed:
            return True, ""
        
        return False, (
            f"Límite de licencia excedido. "
            f"Licencia {self.get_license_type().display_name} permite máximo {max_allowed:,} facturas por consulta. "
            f"Solicitado: {requested_count:,}"
        )
    
    def validate_bi_export_limit(self, requested_count: int) -> tuple[bool, str]:
        """
        Validate if requested invoice count is within license limits for BI export.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not self.is_license_valid():
            return False, "Licencia inválida o no configurada"
        
        if not self.can_export_bi():
            return False, f"Licencia {self.get_license_type().display_name} no incluye exportación BI"
        
        max_allowed = self._current_license.get_max_invoices_bi()
        
        if max_allowed is None:  # Unlimited (Enterprise)
            return True, ""
        
        if max_allowed == 0:  # No access (Free)
            return False, "Exportación BI no disponible en licencia gratuita"
        
        if requested_count <= max_allowed:
            return True, ""
        
        return False, (
            f"Límite de exportación BI excedido. "
            f"Licencia {self.get_license_type().display_name} permite máximo {max_allowed:,} facturas para BI. "
            f"Solicitado: {requested_count:,}"
        )
    
    def get_max_invoices_for_query(self) -> int:
        """Get maximum invoices allowed for query operations."""
        if not self.is_license_valid():
            return 100  # Conservative fallback
        return self._current_license.get_max_invoices_query()
    
    def get_max_invoices_for_bi(self) -> Optional[int]:
        """Get maximum invoices allowed for BI export. None = unlimited."""
        if not self.is_license_valid():
            return 0
        return self._current_license.get_max_invoices_bi()
    
    # ========================================================================================
    # FEATURE ACCESS METHODS  
    # ========================================================================================
    
    def get_available_features(self) -> list[str]:
        """Get list of available features for current license."""
        if not self.is_license_valid():
            return []
        return self._current_license.features.copy()
    
    def has_feature(self, feature: str) -> bool:
        """Check if current license has a specific feature."""
        if not self.is_license_valid():
            return False
        return self._current_license.has_feature(feature)
    
    def get_license_summary(self) -> Dict[str, Any]:
        """Get comprehensive license information summary."""
        if not self.is_license_valid():
            return {
                "type": "No License",
                "status": "Invalid",
                "gui_access": False,
                "financial_reports": False,
                "bi_export": False,
                "max_invoices_query": 0,
                "max_invoices_bi": 0,
                "features": []
            }
        
        return {
            "type": self.get_license_type().display_name,
            "status": self._current_license.status,
            "expires_at": self._current_license.expires_at.isoformat() if self._current_license.expires_at else None,
            "gui_access": self.can_access_gui(),
            "financial_reports": self.can_generate_financial_reports(),
            "bi_export": self.can_export_bi(),
            "advanced_features": self.can_use_advanced_features(),
            "max_invoices_query": self.get_max_invoices_for_query(),
            "max_invoices_bi": self.get_max_invoices_for_bi(),
            "features": self.get_available_features(),
            "online_validation": self.requires_online_validation(),
            "advanced_logging": self.can_use_advanced_logging()
        }
    
    def get_upgrade_message(self) -> str:
        """Get message suggesting license upgrade based on current tier."""
        current_type = self.get_license_type()
        
        if current_type == LicenseType.FREE:
            return (
                "💼 Actualice a Profesional para acceder a:\n"
                "• Interfaz gráfica completa\n"
                "• Informes financieros automatizados\n"
                "• Exportación BI hasta 2,000 facturas\n"
                "• Logging avanzado"
            )
        elif current_type == LicenseType.PROFESSIONAL:
            return (
                "🏢 Actualice a Enterprise para acceder a:\n"
                "• Exportación BI ilimitada (10k+ facturas/minuto)\n"
                "• Sincronización en tiempo real\n"
                "• Multiusuario y multiempresa\n"
                "• Exportación PDF/Excel\n"
                "• API REST e IA predictiva"
            )
        else:
            return "🎉 Tiene acceso completo a todas las funcionalidades Enterprise"