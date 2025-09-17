"""
InvoiceUseCases - Wrapper class for invoice use cases
Provides a unified interface for invoice operations compatible with GUI architecture.
"""

from typing import Dict, Any
from src.application.use_cases.invoice_use_cases import (
    GetInvoicesUseCase, GetInvoicesRequest,
    ExportInvoicesFromAPIToCSVUseCase, ExportInvoicesFromAPIToCSVRequest,
    CheckAPIStatusUseCase,
    ViewStoredFilesUseCase,
    ExportInvoiceToCSVUseCase,
    ExportToBIUseCase
)


class InvoiceUseCases:
    """
    Clase wrapper que unifica todos los casos de uso de facturas.
    Facilita la integración con la nueva arquitectura GUI.
    """
    
    def __init__(self, siigo_repository, file_repository, logger):
        """Inicializar casos de uso con dependencias"""
        self.siigo_repository = siigo_repository
        self.file_repository = file_repository
        self.logger = logger
        
        # Instanciar casos de uso individuales
        self.get_invoices = GetInvoicesUseCase(siigo_repository, file_repository, logger)
        self.check_api_status = CheckAPIStatusUseCase(siigo_repository, logger)
        self.view_stored_files = ViewStoredFilesUseCase(file_repository, logger)
        self.export_to_csv = ExportInvoiceToCSVUseCase(siigo_repository, None, file_repository, logger)
        self.export_from_api_to_csv = ExportInvoicesFromAPIToCSVUseCase(siigo_repository, None, file_repository, logger)
        self.export_to_bi = ExportToBIUseCase(siigo_repository, None, file_repository, logger)
    
    def export_invoices_json(self, limit: int = 100, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Exportar facturas a JSON"""
        try:
            request = GetInvoicesRequest(
                limit=limit,
                page_size=limit,
                date_start=date_from,
                date_end=date_to
            )
            
            response = self.get_invoices.execute(request)
            
            if response.success:
                return {
                    'success': True,
                    'file_path': response.file_path,
                    'count': len(response.invoices)
                }
            else:
                return {
                    'success': False,
                    'error': response.error
                }
                
        except Exception as e:
            self.logger.log_error(f"Error exportando facturas a JSON: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_invoices_csv(self, limit: int = 100, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Exportar facturas a CSV"""
        try:
            request = ExportInvoicesFromAPIToCSVRequest(
                limit=limit,
                page_size=limit,
                date_start=date_from,
                date_end=date_to
            )
            
            response = self.export_from_api_to_csv.execute(request)
            
            if response.success:
                return {
                    'success': True,
                    'file_path': response.file_path,
                    'count': response.total_records
                }
            else:
                return {
                    'success': False,
                    'error': response.error
                }
                
        except Exception as e:
            self.logger.log_error(f"Error exportando facturas a CSV: {e}")
            return {
                'success': False,
                'error': str(e)
            }