"""
Basic Statistics Service
Servicio para generar estadísticas básicas de facturas para licencia FREE.
Implementa cálculos simples con restricciones de licencia aplicadas.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from src.domain.entities.invoice import Invoice
from src.application.ports.interfaces import InvoiceRepository
from src.domain.services.license_manager import LicenseManager


@dataclass
class BasicStatisticsRequest:
    """Request para generar estadísticas básicas."""
    start_date: str = None
    end_date: str = None
    max_records: int = 100  # Límite para FREE


@dataclass
class BasicStatisticsResponse:
    """Response con estadísticas básicas calculadas."""
    success: bool
    message: str
    statistics: Dict[str, Any] = None
    period_info: Dict[str, str] = None
    license_info: Dict[str, str] = None


class BasicStatisticsService:
    """
    Servicio para generar estadísticas básicas de facturas.
    Diseñado específicamente para licencia FREE con limitaciones aplicadas.
    """
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        license_manager: LicenseManager
    ):
        self._invoice_repository = invoice_repository
        self._license_manager = license_manager
    
    def calculate_basic_statistics(self, request: BasicStatisticsRequest) -> BasicStatisticsResponse:
        """
        Calcular estadísticas básicas con limitaciones de licencia FREE.
        """
        try:
            # Validar límites de licencia
            if not self._license_manager.validate_invoice_query_limit(request.max_records):
                max_allowed = self._license_manager.get_max_invoices_for_query()
                return BasicStatisticsResponse(
                    success=False,
                    message=f"Límite excedido. Licencia FREE permite máximo {max_allowed} facturas para estadísticas."
                )
            
            # Obtener facturas para el cálculo
            invoices = self._fetch_invoices_for_statistics(request)
            
            if not invoices:
                return BasicStatisticsResponse(
                    success=True,
                    message="No se encontraron facturas para el período especificado",
                    statistics=self._get_empty_statistics(),
                    period_info=self._get_period_info(request),
                    license_info=self._get_license_info()
                )
            
            # Calcular estadísticas básicas
            statistics = self._calculate_statistics(invoices)
            
            return BasicStatisticsResponse(
                success=True,
                message=f"Estadísticas calculadas exitosamente para {len(invoices)} facturas",
                statistics=statistics,
                period_info=self._get_period_info(request),
                license_info=self._get_license_info()
            )
            
        except Exception as e:
            return BasicStatisticsResponse(
                success=False,
                message=f"Error calculando estadísticas: {str(e)}"
            )
    
    def _fetch_invoices_for_statistics(self, request: BasicStatisticsRequest) -> List[Invoice]:
        """Obtener facturas para el cálculo de estadísticas."""
        from src.application.use_cases.invoice_use_cases import InvoiceFilter
        
        # Crear filtro para las facturas
        invoice_filter = InvoiceFilter(
            document_id=None,
            created_start=request.start_date,
            created_end=request.end_date
        )
        
        # Aplicar límite de licencia FREE
        limit = min(request.max_records, self._license_manager.get_max_invoices_for_query())
        
        # Obtener facturas del repositorio
        invoices = self._invoice_repository.get_invoices(invoice_filter, limit)
        
        return invoices
    
    def _calculate_statistics(self, invoices: List[Invoice]) -> Dict[str, Any]:
        """Calcular las estadísticas básicas de las facturas."""
        
        # Estadísticas básicas
        total_invoices = len(invoices)
        total_amount = 0.0
        unique_customers = set()
        unique_sellers = set()
        total_items = 0
        payment_methods = {}
        monthly_distribution = {}
        
        for invoice in invoices:
            # Calcular monto total
            if invoice.total:
                total_amount += float(invoice.total)
            elif invoice.items:
                total_amount += float(invoice.calculate_total())
            
            # Clientes únicos
            if invoice.customer and invoice.customer.identification:
                unique_customers.add(invoice.customer.identification)
            
            # Vendedores únicos
            if invoice.seller:
                unique_sellers.add(invoice.seller)
            
            # Total de items
            if invoice.items:
                total_items += len(invoice.items)
            
            # Métodos de pago
            if invoice.payments:
                for payment in invoice.payments:
                    payment_id = payment.id if payment.id else "Unknown"
                    if payment_id not in payment_methods:
                        payment_methods[payment_id] = 0
                    payment_methods[payment_id] += 1
            
            # Distribución mensual
            if invoice.date:
                month_key = invoice.date.strftime("%Y-%m")
                if month_key not in monthly_distribution:
                    monthly_distribution[month_key] = {"count": 0, "amount": 0.0}
                monthly_distribution[month_key]["count"] += 1
                
                if invoice.total:
                    monthly_distribution[month_key]["amount"] += float(invoice.total)
                elif invoice.items:
                    monthly_distribution[month_key]["amount"] += float(invoice.calculate_total())
        
        # Promedios
        average_invoice_amount = total_amount / total_invoices if total_invoices > 0 else 0.0
        average_items_per_invoice = total_items / total_invoices if total_invoices > 0 else 0.0
        
        return {
            # Estadísticas principales
            "total_invoices": total_invoices,
            "total_amount": round(total_amount, 2),
            "unique_customers": len(unique_customers),
            "unique_sellers": len(unique_sellers),
            "total_items": total_items,
            
            # Promedios
            "average_invoice_amount": round(average_invoice_amount, 2),
            "average_items_per_invoice": round(average_items_per_invoice, 2),
            
            # Distribuciones (limitadas para FREE)
            "top_payment_methods": dict(list(sorted(payment_methods.items(), key=lambda x: x[1], reverse=True))[:3]),
            "monthly_distribution": dict(list(monthly_distribution.items())[:6]),  # Últimos 6 meses
            
            # Rangos de valores (básicos)
            "amount_range": {
                "min": round(min([float(inv.total) if inv.total else float(inv.calculate_total()) if inv.items else 0 for inv in invoices], default=0), 2),
                "max": round(max([float(inv.total) if inv.total else float(inv.calculate_total()) if inv.items else 0 for inv in invoices], default=0), 2)
            }
        }
    
    def _get_empty_statistics(self) -> Dict[str, Any]:
        """Obtener estructura de estadísticas vacías."""
        return {
            "total_invoices": 0,
            "total_amount": 0.0,
            "unique_customers": 0,
            "unique_sellers": 0,
            "total_items": 0,
            "average_invoice_amount": 0.0,
            "average_items_per_invoice": 0.0,
            "top_payment_methods": {},
            "monthly_distribution": {},
            "amount_range": {"min": 0.0, "max": 0.0}
        }
    
    def _get_period_info(self, request: BasicStatisticsRequest) -> Dict[str, str]:
        """Obtener información del período de análisis."""
        period_info = {
            "calculated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "max_records": str(request.max_records),
            "license_limit": str(self._license_manager.get_max_invoices_for_query())
        }
        
        if request.start_date:
            period_info["start_date"] = request.start_date
        else:
            period_info["start_date"] = "Sin límite inicial"
        
        if request.end_date:
            period_info["end_date"] = request.end_date
        else:
            period_info["end_date"] = "Sin límite final"
        
        return period_info
    
    def _get_license_info(self) -> Dict[str, str]:
        """Obtener información de la licencia."""
        return {
            "type": self._license_manager.get_license_display_name(),
            "max_invoices_query": str(self._license_manager.get_max_invoices_for_query()),
            "is_gui_lite": str(self._license_manager.is_gui_lite_mode()),
            "restrictions": "Estadísticas básicas únicamente" if self._license_manager.is_gui_lite_mode() else "Acceso completo"
        }
    
    def get_statistics_summary_text(self, statistics: Dict[str, Any]) -> str:
        """
        Generar un resumen de texto de las estadísticas para mostrar en UI.
        """
        if not statistics:
            return "No hay estadísticas disponibles."
        
        summary_lines = [
            "📊 RESUMEN ESTADÍSTICAS BÁSICAS (FREE)",
            "=" * 40,
            f"📄 Total de Facturas: {statistics.get('total_invoices', 0)}",
            f"💰 Monto Total: ${statistics.get('total_amount', 0):,.2f}",
            f"👥 Clientes Únicos: {statistics.get('unique_customers', 0)}",
            f"🏢 Vendedores: {statistics.get('unique_sellers', 0)}",
            f"📦 Total Items: {statistics.get('total_items', 0)}",
            "",
            "📈 PROMEDIOS:",
            f"💵 Promedio por Factura: ${statistics.get('average_invoice_amount', 0):,.2f}",
            f"📦 Items promedio/Factura: {statistics.get('average_items_per_invoice', 0):.1f}",
            "",
            "💳 MÉTODOS DE PAGO MÁS USADOS:"
        ]
        
        # Agregar métodos de pago
        payment_methods = statistics.get('top_payment_methods', {})
        if payment_methods:
            for method, count in list(payment_methods.items())[:3]:
                summary_lines.append(f"  • {method}: {count} facturas")
        else:
            summary_lines.append("  • No hay datos de métodos de pago")
        
        summary_lines.extend([
            "",
            "📅 DISTRIBUCIÓN MENSUAL:"
        ])
        
        # Agregar distribución mensual
        monthly_dist = statistics.get('monthly_distribution', {})
        if monthly_dist:
            for month, data in list(monthly_dist.items())[:3]:
                summary_lines.append(f"  • {month}: {data['count']} facturas, ${data['amount']:,.2f}")
        else:
            summary_lines.append("  • No hay datos de distribución mensual")
        
        # Información de rango
        amount_range = statistics.get('amount_range', {})
        if amount_range and amount_range['max'] > 0:
            summary_lines.extend([
                "",
                "💹 RANGO DE VALORES:",
                f"  • Factura mínima: ${amount_range['min']:,.2f}",
                f"  • Factura máxima: ${amount_range['max']:,.2f}"
            ])
        
        summary_lines.extend([
            "",
            "⚠️  LIMITACIÓN FREE: Estadísticas basadas en máximo 100 facturas",
            "🚀 Actualiza a PRO/ENTERPRISE para análisis completo"
        ])
        
        return "\n".join(summary_lines)
    
    def get_statistics_for_gui_panel(self, statistics: Dict[str, Any]) -> Dict[str, str]:
        """
        Preparar estadísticas formateadas para mostrar en panel GUI.
        """
        if not statistics:
            return {
                "total_invoices": "0",
                "total_amount": "$0.00",
                "unique_customers": "0",
                "avg_invoice": "$0.00"
            }
        
        return {
            "total_invoices": f"{statistics.get('total_invoices', 0):,}",
            "total_amount": f"${statistics.get('total_amount', 0):,.2f}",
            "unique_customers": f"{statistics.get('unique_customers', 0):,}",
            "avg_invoice": f"${statistics.get('average_invoice_amount', 0):,.2f}"
        }


# ================================================================================================
# ESTADÍSTICAS USE CASE PARA INTEGRACIÓN CON LA APLICACIÓN
# ================================================================================================

@dataclass
class CalculateBasicStatisticsUseCase:
    """Use case para calcular estadísticas básicas integrado con la aplicación."""
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        license_manager: LicenseManager
    ):
        self._statistics_service = BasicStatisticsService(invoice_repository, license_manager)
    
    def execute(self, request: BasicStatisticsRequest) -> BasicStatisticsResponse:
        """Ejecutar el cálculo de estadísticas básicas."""
        return self._statistics_service.calculate_basic_statistics(request)
    
    def get_formatted_summary(self, statistics: Dict[str, Any]) -> str:
        """Obtener resumen formateado para mostrar en CLI o GUI."""
        return self._statistics_service.get_statistics_summary_text(statistics)
    
    def get_gui_panel_data(self, statistics: Dict[str, Any]) -> Dict[str, str]:
        """Obtener datos formateados para panel GUI."""
        return self._statistics_service.get_statistics_for_gui_panel(statistics)