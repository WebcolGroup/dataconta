"""
Basic Statistics Use Case for FREE license.
Proporciona métricas básicas para usuarios de licencia gratuita.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from src.application.ports.interfaces import (
    InvoiceRepository, 
    LicenseValidator, 
    Logger
)
from src.domain.entities.invoice import Invoice, InvoiceFilter
from src.domain.services.license_manager import LicenseManager


@dataclass
class BasicStatisticsRequest:
    """Request object for basic statistics."""
    start_date: str = None
    end_date: str = None
    max_records: int = 500


@dataclass
class BasicStatisticsResponse:
    """Response object for basic statistics."""
    success: bool
    statistics: Dict[str, Any] = None
    message: str = ""
    license_info: Dict[str, str] = None


class BasicStatisticsUseCase:
    """
    Use case para generar estadísticas básicas en licencia FREE.
    
    Calcula:
    - Total de facturas consultadas
    - Total vendido acumulado  
    - Número de clientes distintos
    - Facturas del mes actual
    - Promedio por factura
    """
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        license_validator: LicenseValidator,
        logger: Logger,
        license_manager: LicenseManager
    ):
        self._invoice_repository = invoice_repository
        self._license_validator = license_validator
        self._logger = logger
        self._license_manager = license_manager
    
    def execute(self, request: BasicStatisticsRequest, license_key: str) -> BasicStatisticsResponse:
        """Execute the basic statistics use case."""
        try:
            # Validate license first and set it in the manager
            license_info = self._license_validator.validate_license(license_key)
            if not license_info or not license_info.is_valid():
                self._logger.error("Invalid license for statistics calculation")
                return BasicStatisticsResponse(
                    success=False,
                    message="License validation failed"
                )
            
            # Set license in manager
            self._license_manager.set_license(license_info)
            
            self._logger.info(f"Calculating basic statistics (License: {self._license_manager.get_license_display_name()})")
            
            # Validate requested count against license limits
            is_valid, error_message = self._license_manager.validate_invoice_query_limit(request.max_records)
            if not is_valid:
                self._logger.warning(f"License limit validation failed: {error_message}")
                return BasicStatisticsResponse(
                    success=False,
                    message=f"{error_message}. {self._license_manager.get_upgrade_message()}"
                )
            
            # Apply license limits to request
            max_allowed = self._license_manager.get_max_invoices_for_query()
            if request.max_records > max_allowed:
                request.max_records = max_allowed
                self._logger.info(f"Limited statistics query to {max_allowed} invoices based on license")
            
            # Get invoices for statistics
            invoices = self._get_invoices_for_stats(request)
            
            if not invoices:
                return BasicStatisticsResponse(
                    success=False,
                    message="No se encontraron facturas para calcular estadísticas"
                )
            
            # Calculate statistics
            statistics = self._calculate_basic_statistics(invoices)
            
            # Add license information
            license_info_dict = {
                "type": self._license_manager.get_license_display_name(),
                "max_invoices": str(max_allowed),
                "query_limit": "500 facturas por consulta"
            }
            
            self._logger.info(f"Statistics calculated successfully: {len(invoices)} invoices processed")
            
            return BasicStatisticsResponse(
                success=True,
                statistics=statistics,
                license_info=license_info_dict,
                message=f"Estadísticas calculadas exitosamente con {len(invoices)} facturas"
            )
            
        except Exception as e:
            self._logger.error(f"Error in BasicStatisticsUseCase: {e}")
            return BasicStatisticsResponse(
                success=False,
                message=f"Error calculating statistics: {str(e)}"
            )
    
    def _get_invoices_for_stats(self, request: BasicStatisticsRequest) -> List[Invoice]:
        """Get invoices for statistics calculation."""
        # Create filter for invoice retrieval
        invoice_filter = InvoiceFilter(
            created_start=self._parse_date_string(request.start_date),
            created_end=self._parse_date_string(request.end_date),
            page_size=request.max_records
        )
        
        # If no date range specified, get recent invoices (last 6 months)
        if not request.start_date and not request.end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)  # 6 months
            invoice_filter.created_start = start_date
            invoice_filter.created_end = end_date
        
        return self._invoice_repository.get_invoices(invoice_filter)
    
    def _parse_date_string(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        if not date_str:
            return None
            
        # List of common date formats to try
        date_formats = [
            "%Y-%m-%d",           # 2024-01-01
            "%d/%m/%Y",           # 01/01/2024
            "%m/%d/%Y",           # 01/01/2024 (US format)
            "%Y-%m-%d %H:%M:%S",  # 2024-01-01 00:00:00
            "%Y-%m-%dT%H:%M:%S",  # 2024-01-01T00:00:00 (ISO format)
            "%Y-%m-%dT%H:%M:%SZ", # 2024-01-01T00:00:00Z (ISO format with Z)
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If no format worked, try fromisoformat as fallback
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            self._logger.warning(f"Unable to parse date string: {date_str}")
            return None
    
    def _calculate_basic_statistics(self, invoices: List[Invoice]) -> Dict[str, Any]:
        """Calculate basic statistics from invoices list."""
        if not invoices:
            return {
                "total_invoices": 0,
                "total_amount": 0.0,
                "unique_customers": 0,
                "current_month_invoices": 0,
                "average_invoice_amount": 0.0,
                "period_start": "N/A",
                "period_end": "N/A",
                "last_updated": datetime.now().isoformat()
            }
        
        # Basic calculations
        total_invoices = len(invoices)
        
        # Calculate total amount
        total_amount = 0.0
        for invoice in invoices:
            if invoice.total:
                total_amount += float(invoice.total)
            elif invoice.items:
                total_amount += float(invoice.calculate_total())
        
        # Unique customers
        unique_customers = set()
        for invoice in invoices:
            if invoice.customer and invoice.customer.identification:
                unique_customers.add(invoice.customer.identification)
        
        # Current month invoices
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_invoices = 0
        for invoice in invoices:
            if invoice.date and invoice.date >= current_month:
                current_month_invoices += 1
        
        # Period calculation
        invoice_dates = [inv.date for inv in invoices if inv.date]
        period_start = min(invoice_dates).isoformat() if invoice_dates else "N/A"
        period_end = max(invoice_dates).isoformat() if invoice_dates else "N/A"
        
        # Average invoice amount
        average_invoice_amount = total_amount / total_invoices if total_invoices > 0 else 0.0
        
        # Additional metrics for FREE version
        statistics = {
            "total_invoices": total_invoices,
            "total_amount": round(total_amount, 2),
            "unique_customers": len(unique_customers),
            "current_month_invoices": current_month_invoices,
            "average_invoice_amount": round(average_invoice_amount, 2),
            "period_start": period_start,
            "period_end": period_end,
            "last_updated": datetime.now().isoformat(),
            
            # Additional FREE metrics
            "invoices_with_items": sum(1 for inv in invoices if inv.items and len(inv.items) > 0),
            "total_items": sum(len(inv.items) for inv in invoices if inv.items),
            "invoices_this_week": self._count_invoices_this_week(invoices),
            "max_invoice_amount": self._get_max_invoice_amount(invoices),
            "min_invoice_amount": self._get_min_invoice_amount(invoices)
        }
        
        return statistics
    
    def _count_invoices_this_week(self, invoices: List[Invoice]) -> int:
        """Count invoices from this week."""
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        count = 0
        for invoice in invoices:
            if invoice.date and invoice.date >= week_start:
                count += 1
        
        return count
    
    def _get_max_invoice_amount(self, invoices: List[Invoice]) -> float:
        """Get maximum invoice amount."""
        max_amount = 0.0
        for invoice in invoices:
            amount = float(invoice.total) if invoice.total else float(invoice.calculate_total()) if invoice.items else 0.0
            if amount > max_amount:
                max_amount = amount
        return round(max_amount, 2)
    
    def _get_min_invoice_amount(self, invoices: List[Invoice]) -> float:
        """Get minimum invoice amount (excluding zero)."""
        min_amount = float('inf')
        for invoice in invoices:
            amount = float(invoice.total) if invoice.total else float(invoice.calculate_total()) if invoice.items else 0.0
            if amount > 0 and amount < min_amount:
                min_amount = amount
        
        return round(min_amount, 2) if min_amount != float('inf') else 0.0