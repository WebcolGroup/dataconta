"""
Wrapper class for invoice use cases.
"""

from typing import TYPE_CHECKING

from src.application.ports.interfaces import (
    InvoiceRepository, 
    LicenseValidator, 
    FileStorage, 
    Logger, 
    UserInterface,
    InvoiceProcessor,
    CSVExporter
)
from src.domain.services.license_manager import LicenseManager

from .invoice_use_cases import (
    GetInvoicesUseCase,
    CheckAPIStatusUseCase,
    ViewStoredFilesUseCase,
    ExportInvoiceToCSVUseCase,
    ExportInvoicesFromAPIToCSVUseCase,
    ExportToBIUseCase
)


class InvoiceUseCases:
    """Wrapper class for all invoice-related use cases."""
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        license_validator: LicenseValidator,
        license_manager: LicenseManager,
        file_storage: FileStorage,
        logger: Logger,
        user_interface: UserInterface,
        invoice_processor: InvoiceProcessor,
        csv_exporter: CSVExporter,
        bi_export_service=None
    ):
        # Initialize all use cases with required dependencies including license_manager
        self.get_invoices = GetInvoicesUseCase(
            invoice_repository=invoice_repository,
            license_validator=license_validator,
            file_storage=file_storage,
            logger=logger,
            license_manager=license_manager
        )
        
        self.check_api_status = CheckAPIStatusUseCase(
            invoice_repository=invoice_repository,
            license_validator=license_validator,
            logger=logger,
            license_manager=license_manager
        )
        
        self.view_files = ViewStoredFilesUseCase(
            file_storage=file_storage,
            logger=logger
        )
        
        self.export_to_csv = ExportInvoiceToCSVUseCase(
            invoice_processor=invoice_processor,
            csv_exporter=csv_exporter,
            license_validator=license_validator,
            logger=logger,
            license_manager=license_manager
        )
        
        self.export_from_api_to_csv = ExportInvoicesFromAPIToCSVUseCase(
            invoice_repository=invoice_repository,
            invoice_processor=invoice_processor,
            csv_exporter=csv_exporter,
            license_validator=license_validator,
            logger=logger,
            license_manager=license_manager
        )
        
        self.export_to_bi = ExportToBIUseCase(
            invoice_repository=invoice_repository,
            bi_export_service=bi_export_service,
            license_validator=license_validator,
            logger=logger,
            license_manager=license_manager
        )