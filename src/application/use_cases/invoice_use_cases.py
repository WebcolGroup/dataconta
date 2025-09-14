"""
Use cases for invoice management.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.application.ports.interfaces import (
    InvoiceRepository, 
    LicenseValidator, 
    FileStorage, 
    Logger, 
    UserInterface,
    InvoiceProcessor,
    CSVExporter
)
from src.domain.entities.invoice import Invoice, InvoiceFilter, License


@dataclass
class GetInvoicesRequest:
    """Request object for getting invoices."""
    document_id: str = None
    created_start: str = None
    created_end: str = None


@dataclass
class GetInvoicesResponse:
    """Response object for getting invoices."""
    invoices: List[Invoice]
    total_count: int
    success: bool
    message: str = ""


class GetInvoicesUseCase:
    """Use case for retrieving invoices."""
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        license_validator: LicenseValidator,
        file_storage: FileStorage,
        logger: Logger
    ):
        self._invoice_repository = invoice_repository
        self._license_validator = license_validator
        self._file_storage = file_storage
        self._logger = logger
    
    def execute(self, request: GetInvoicesRequest, license_key: str) -> GetInvoicesResponse:
        """Execute the get invoices use case."""
        try:
            # Validate license first
            if not self._license_validator.is_license_valid(license_key):
                self._logger.error("Invalid license for invoice retrieval")
                return GetInvoicesResponse(
                    invoices=[],
                    total_count=0,
                    success=False,
                    message="License validation failed"
                )
            
            # Create filter from request
            invoice_filter = InvoiceFilter(
                document_id=request.document_id,
                created_start=self._parse_date_string(request.created_start),
                created_end=self._parse_date_string(request.created_end)
            )
            
            # Get invoices from repository
            self._logger.info("Retrieving invoices from repository")
            invoices = self._invoice_repository.get_invoices(invoice_filter)
            
            # Save results to file storage
            if invoices:
                invoice_data = [self._invoice_to_dict(inv) for inv in invoices]
                filename = f"invoices_{len(invoices)}_items"
                self._file_storage.save_data(
                    {"invoices": invoice_data, "total": len(invoices)},
                    filename
                )
                self._logger.info(f"Saved {len(invoices)} invoices to storage")
            
            return GetInvoicesResponse(
                invoices=invoices,
                total_count=len(invoices),
                success=True,
                message=f"Successfully retrieved {len(invoices)} invoices"
            )
            
        except Exception as e:
            self._logger.error(f"Error in GetInvoicesUseCase: {e}")
            return GetInvoicesResponse(
                invoices=[],
                total_count=0,
                success=False,
                message=f"Error retrieving invoices: {str(e)}"
            )
    
    def _parse_date_string(self, date_str: str) -> datetime:
        """
        Parse date string to datetime object.
        Supports multiple date formats commonly used.
        """
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
    
    def _invoice_to_dict(self, invoice: Invoice) -> Dict[str, Any]:
        """Convert invoice entity to dictionary for storage."""
        return {
            "id": invoice.id,
            "document_id": invoice.document_id,
            "number": invoice.number,
            "name": invoice.name,
            "date": invoice.date.isoformat() if invoice.date else None,
            "total": float(invoice.calculate_total()),
            "customer": {
                "identification": invoice.customer.identification,
                "name": invoice.customer.name,
                "commercial_name": invoice.customer.commercial_name
            } if invoice.customer else None,
            "items_count": len(invoice.items) if invoice.items else 0
        }


class CheckAPIStatusUseCase:
    """Use case for checking API status."""
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        license_validator: LicenseValidator,
        logger: Logger
    ):
        self._invoice_repository = invoice_repository
        self._license_validator = license_validator
        self._logger = logger
    
    def execute(self, license_key: str) -> Dict[str, Any]:
        """Execute the check API status use case."""
        try:
            # Validate license
            license_valid = self._license_validator.is_license_valid(license_key)
            
            if not license_valid:
                self._logger.warning("License validation failed during API status check")
                return {
                    "api_available": False,
                    "license_valid": False,
                    "message": "Invalid license"
                }
            
            # Try to connect to API by making a simple request
            try:
                # This will test the connection
                test_filter = InvoiceFilter(page_size=1)
                self._invoice_repository.get_invoices(test_filter)
                api_available = True
                message = "API is available and accessible"
                self._logger.info("API status check successful")
            except Exception as e:
                api_available = False
                message = f"API connection failed: {str(e)}"
                self._logger.error(f"API status check failed: {e}")
            
            return {
                "api_available": api_available,
                "license_valid": license_valid,
                "message": message
            }
            
        except Exception as e:
            self._logger.error(f"Error in CheckAPIStatusUseCase: {e}")
            return {
                "api_available": False,
                "license_valid": False,
                "message": f"Status check error: {str(e)}"
            }


class ViewStoredFilesUseCase:
    """Use case for viewing stored files."""
    
    def __init__(self, file_storage: FileStorage, logger: Logger):
        self._file_storage = file_storage
        self._logger = logger
    
    def execute(self) -> Dict[str, Any]:
        """Execute the view stored files use case."""
        try:
            files = self._file_storage.list_files()
            
            file_info = []
            for filename in files:
                info = self._file_storage.get_file_info(filename)
                file_info.append({
                    "name": filename,
                    "size": info.get("size", 0),
                    "modified": info.get("modified", "Unknown")
                })
            
            self._logger.info(f"Listed {len(files)} stored files")
            
            return {
                "success": True,
                "files": file_info,
                "total_files": len(files),
                "message": f"Found {len(files)} stored files"
            }
            
        except Exception as e:
            self._logger.error(f"Error in ViewStoredFilesUseCase: {e}")
            return {
                "success": False,
                "files": [],
                "total_files": 0,
                "message": f"Error listing files: {str(e)}"
            }


# ========================================================================================
# NUEVO CASO DE USO PARA EXPORTACIÓN DE FACTURAS (DataConta Export Service)  
# ========================================================================================

@dataclass
class ExportInvoiceToCSVRequest:
    """Request object for exporting invoice to CSV."""
    invoice_data: Dict[str, Any]
    output_filename: str = None


@dataclass
class ExportInvoicesFromAPIToCSVRequest:
    """Request object for exporting invoices from API to CSV."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_records: int = 100
    output_filename: str = None


@dataclass
class ExportToBIRequest:
    """Request object for exporting invoices to BI star schema."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_records: int = 100
    validate_schema: bool = True


@dataclass
class ExportInvoiceToCSVResponse:
    """Response object for exporting invoice to CSV."""
    success: bool
    file_path: str = ""
    rows_exported: int = 0
    message: str = ""


@dataclass
class ExportToBIResponse:
    """Response object for BI export."""
    success: bool
    files_created: Dict[str, bool] = None
    statistics: Dict[str, Any] = None
    validation_results: Dict[str, Any] = None
    message: str = ""
    
    def __post_init__(self):
        """Initialize default values."""
        if self.files_created is None:
            self.files_created = {}
        if self.statistics is None:
            self.statistics = {}
        if self.validation_results is None:
            self.validation_results = {}


class ExportInvoiceToCSVUseCase:
    """
    Use case for exporting invoice data to CSV format.
    
    This use case orchestrates the export process by:
    1. Validating license
    2. Processing invoice data using InvoiceExportService
    3. Writing CSV file using CSVExporter
    4. Returning export results
    """
    
    def __init__(
        self,
        invoice_processor: InvoiceProcessor,
        csv_exporter: CSVExporter,
        license_validator: LicenseValidator,
        logger: Logger,
        output_directory: str = "src/infrastructure/output"
    ):
        """Initialize the use case with required dependencies."""
        self._invoice_processor = invoice_processor
        self._csv_exporter = csv_exporter
        self._license_validator = license_validator
        self._logger = logger
        self._output_directory = output_directory
    
    def execute(
        self, 
        request: ExportInvoiceToCSVRequest, 
        license_key: str
    ) -> ExportInvoiceToCSVResponse:
        """Execute the export invoice to CSV use case."""
        try:
            # Validate license first
            if not self._license_validator.is_license_valid(license_key):
                self._logger.error("Invalid license for CSV export")
                return ExportInvoiceToCSVResponse(
                    success=False,
                    message="License validation failed"
                )
            
            self._logger.info("Starting invoice CSV export process")
            
            # Process invoice data
            processed_rows_data = self._invoice_processor.process_invoice_for_export(
                request.invoice_data
            )
            
            if not processed_rows_data:
                return ExportInvoiceToCSVResponse(
                    success=False,
                    message="No data to export"
                )
            
            # Convert processed data to CSV format
            from src.domain.entities.invoice import InvoiceExportRow
            
            headers = InvoiceExportRow.get_csv_headers()
            csv_rows = []
            
            for row_data in processed_rows_data:
                # Create InvoiceExportRow from processed data
                row = InvoiceExportRow(**row_data)
                csv_rows.append(row.to_csv_row())
            
            # Generate output filename if not provided
            if not request.output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                invoice_id = request.invoice_data.get('id', 'unknown')
                request.output_filename = f"invoice_export_{invoice_id}_{timestamp}.csv"
            
            # Ensure filename has .csv extension
            if not request.output_filename.endswith('.csv'):
                request.output_filename += '.csv'
            
            # Full file path
            file_path = os.path.join(self._output_directory, request.output_filename)
            
            # Write CSV file
            if self._csv_exporter.write_csv(file_path, headers, csv_rows):
                self._logger.info(f"CSV export successful: {file_path} ({len(csv_rows)} rows)")
                return ExportInvoiceToCSVResponse(
                    success=True,
                    file_path=file_path,
                    rows_exported=len(csv_rows),
                    message=f"Successfully exported {len(csv_rows)} rows to {request.output_filename}"
                )
            else:
                return ExportInvoiceToCSVResponse(
                    success=False,
                    message="Failed to write CSV file"
                )
        
        except Exception as e:
            self._logger.error(f"Error in ExportInvoiceToCSVUseCase: {e}")
            return ExportInvoiceToCSVResponse(
                success=False,
                message=f"Export error: {str(e)}"
            )


class ExportInvoicesFromAPIToCSVUseCase:
    """
    Use case for exporting invoices from API directly to CSV format.
    
    This use case orchestrates the export process by:
    1. Validating license
    2. Getting invoices from API using parameters
    3. Processing each invoice using InvoiceExportService
    4. Writing CSV file using CSVExporter
    5. Returning export results
    """
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        invoice_processor: InvoiceProcessor,
        csv_exporter: CSVExporter,
        license_validator: LicenseValidator,
        logger: Logger
    ):
        """Initialize the use case with required dependencies."""
        self._invoice_repository = invoice_repository
        self._invoice_processor = invoice_processor
        self._csv_exporter = csv_exporter
        self._license_validator = license_validator
        self._logger = logger
    
    def execute(
        self, 
        request: ExportInvoicesFromAPIToCSVRequest, 
        license_key: str
    ) -> ExportInvoiceToCSVResponse:
        """Execute the export invoices from API to CSV use case."""
        try:
            # Validate license first
            if not self._license_validator.is_license_valid(license_key):
                self._logger.error("Invalid license for CSV export")
                return ExportInvoiceToCSVResponse(
                    success=False,
                    message="License validation failed"
                )
            
            self._logger.info("Starting invoices CSV export from API")
            
            # Create invoice filter from request parameters
            from datetime import datetime
            
            created_start = None
            created_end = None
            
            if request.start_date:
                try:
                    created_start = datetime.fromisoformat(request.start_date)
                except:
                    self._logger.warning(f"Invalid start_date format: {request.start_date}")
            
            if request.end_date:
                try:
                    created_end = datetime.fromisoformat(request.end_date)
                except:
                    self._logger.warning(f"Invalid end_date format: {request.end_date}")
            
            invoice_filter = InvoiceFilter(
                created_start=created_start,
                created_end=created_end,
                page_size=request.max_records
            )
            
            # Get invoices from API
            invoices = self._invoice_repository.get_invoices(invoice_filter)
            
            if not invoices:
                return ExportInvoiceToCSVResponse(
                    success=False,
                    message="No invoices found with the specified criteria"
                )
            
            self._logger.info(f"Found {len(invoices)} invoices to export")
            
            # Process each invoice and collect rows
            all_csv_rows = []
            headers = None
            
            for invoice in invoices:
                # Convert invoice to dict for processing
                invoice_data = self._invoice_to_dict(invoice)
                
                # Process invoice data
                processed_rows_data = self._invoice_processor.process_invoice_for_export(
                    invoice_data
                )
                
                if processed_rows_data:
                    # Convert processed data to CSV format
                    from src.domain.entities.invoice import InvoiceExportRow
                    
                    if headers is None:
                        headers = InvoiceExportRow.get_csv_headers()
                    
                    for row_data in processed_rows_data:
                        # Create InvoiceExportRow from processed data
                        row = InvoiceExportRow(**row_data)
                        all_csv_rows.append(row.to_csv_row())
            
            if not all_csv_rows:
                return ExportInvoiceToCSVResponse(
                    success=False,
                    message="No data could be processed for export"
                )
            
            # Generate output filename if not provided
            if not request.output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                request.output_filename = f"invoices_export_{len(all_csv_rows)}_items_{timestamp}.csv"
            
            # Ensure filename has .csv extension
            if not request.output_filename.endswith('.csv'):
                request.output_filename += '.csv'
            
            # Write CSV file
            if self._csv_exporter.write_csv(request.output_filename, headers, all_csv_rows):
                self._logger.info(f"CSV export successful: {request.output_filename} ({len(all_csv_rows)} rows)")
                return ExportInvoiceToCSVResponse(
                    success=True,
                    file_path=request.output_filename,
                    rows_exported=len(all_csv_rows),
                    message=f"Successfully exported {len(all_csv_rows)} rows from {len(invoices)} invoices to {request.output_filename}"
                )
            else:
                return ExportInvoiceToCSVResponse(
                    success=False,
                    message="Failed to write CSV file"
                )
        
        except Exception as e:
            self._logger.error(f"Error in ExportInvoicesFromAPIToCSVUseCase: {e}")
            return ExportInvoiceToCSVResponse(
                success=False,
                message=f"Export error: {str(e)}"
            )
    
    def _invoice_to_dict(self, invoice: Invoice) -> Dict[str, Any]:
        """Convert Invoice entity to dictionary for processing."""
        return {
            "id": invoice.id,
            "document": {
                "id": invoice.document_id,
                "name": "FV",
                "prefix": "FV",
                "number": invoice.number
            },
            "date": invoice.date.isoformat() if invoice.date else "",
            "customer": {
                "id": 1,
                "identification": invoice.customer.identification if invoice.customer else "",
                "name": " ".join(invoice.customer.name) if invoice.customer and invoice.customer.name else "",
                "email": "cliente@ejemplo.com"
            },
            "seller": {
                "id": invoice.seller or 1,
                "name": f"Seller_{invoice.seller}" if invoice.seller else "Default Seller"
            },
            "items": [
                {
                    "code": item.code,
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "price": float(item.price),
                    "discount": float(item.discount),
                    "total": float(item.calculate_total())
                }
                for item in invoice.items
            ],
            "payments": [
                {
                    "id": payment.id,
                    "name": f"Payment_{payment.id}",
                    "value": float(payment.value)
                }
                for payment in (invoice.payments or [])
            ],
            "totals": {
                "subtotal": float(invoice.calculate_total()) if invoice.items else 0,
                "discount": 0,
                "taxes": 0,
                "total": float(invoice.total) if invoice.total else float(invoice.calculate_total())
            },
            "status": "Open",
            "observations": invoice.observations or ""
        }


# ========================================================================================
# BUSINESS INTELLIGENCE EXPORT USE CASE
# ========================================================================================

class ExportToBIUseCase:
    """
    Use case for exporting invoices to Business Intelligence star schema format.
    
    This use case orchestrates the BI export process by:
    1. Validating license
    2. Retrieving invoices from API
    3. Processing invoices through BIExportService
    4. Generating star schema CSV files
    5. Validating the generated schema
    6. Returning export results
    """
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        bi_export_service,  # BIExportService - avoiding circular import
        license_validator: LicenseValidator,
        logger: Logger
    ):
        """Initialize the BI export use case with required dependencies."""
        self._invoice_repository = invoice_repository
        self._bi_export_service = bi_export_service
        self._license_validator = license_validator
        self._logger = logger
    
    def execute(self, request: ExportToBIRequest, license_key: str) -> ExportToBIResponse:
        """Execute the BI export use case."""
        try:
            # Validate license first
            if not self._license_validator.is_license_valid(license_key):
                self._logger.error("Invalid license for BI export")
                return ExportToBIResponse(
                    success=False,
                    message="License validation failed"
                )
            
            self._logger.info("Starting BI export process")
            
            # Create invoice filter from request parameters
            from datetime import datetime
            
            created_start = None
            created_end = None
            
            if request.start_date:
                try:
                    created_start = datetime.fromisoformat(request.start_date)
                except:
                    self._logger.warning(f"Invalid start_date format: {request.start_date}")
            
            if request.end_date:
                try:
                    created_end = datetime.fromisoformat(request.end_date)
                except:
                    self._logger.warning(f"Invalid end_date format: {request.end_date}")
            
            invoice_filter = InvoiceFilter(
                created_start=created_start,
                created_end=created_end,
                page_size=request.max_records
            )
            
            # Retrieve invoices from repository
            invoices = self._invoice_repository.get_invoices(invoice_filter)
            
            if not invoices:
                return ExportToBIResponse(
                    success=False,
                    message="No invoices found for the specified criteria"
                )
            
            self._logger.info(f"Retrieved {len(invoices)} invoices for BI export")
            
            # Convert invoices to dictionary format for processing
            invoices_data = []
            for invoice in invoices:
                invoice_dict = self._invoice_to_dict(invoice)
                invoices_data.append(invoice_dict)
            
            # Process invoices through BI export service
            processing_stats = self._bi_export_service.process_invoices_for_bi(invoices_data)
            
            # Export to CSV files
            export_results = self._bi_export_service.export_to_csv_files()
            
            # Validate schema if requested
            validation_results = {}
            if request.validate_schema:
                validation_results = self._bi_export_service.validate_star_schema()
            
            # Get final statistics
            final_stats = self._bi_export_service.get_export_statistics()
            
            # Check if all files were created successfully
            all_files_success = all(export_results.values())
            
            if all_files_success:
                success_files = len([r for r in export_results.values() if r])
                self._logger.info(f"BI export successful: {success_files} CSV files created")
                
                return ExportToBIResponse(
                    success=True,
                    files_created=export_results,
                    statistics=final_stats,
                    validation_results=validation_results,
                    message=f"Successfully exported {processing_stats.get('processed_invoices', 0)} invoices to {success_files} CSV files"
                )
            else:
                failed_files = [filename for filename, success in export_results.items() if not success]
                self._logger.error(f"BI export partially failed. Failed files: {failed_files}")
                
                return ExportToBIResponse(
                    success=False,
                    files_created=export_results,
                    statistics=final_stats,
                    validation_results=validation_results,
                    message=f"Export partially failed. Could not create: {', '.join(failed_files)}"
                )
        
        except Exception as e:
            self._logger.error(f"Error in ExportToBIUseCase: {e}")
            return ExportToBIResponse(
                success=False,
                message=f"Export error: {str(e)}"
            )
    
    def _invoice_to_dict(self, invoice: Invoice) -> Dict[str, Any]:
        """Convert Invoice entity to dictionary for BI processing."""
        return {
            "id": invoice.id,
            "document": {
                "id": invoice.document_id,
                "name": "FV",
                "prefix": "FV",
                "number": invoice.number
            },
            "date": invoice.date.isoformat() if invoice.date else "",
            "customer": {
                "id": 1,
                "identification": invoice.customer.identification if invoice.customer else "",
                "name": " ".join(invoice.customer.name) if invoice.customer and invoice.customer.name else "",
                "email": "cliente@ejemplo.com"
            },
            "seller": {
                "id": invoice.seller or 1,
                "name": f"Seller_{invoice.seller}" if invoice.seller else "Default Seller"
            },
            "items": [
                {
                    "code": item.code,
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "price": float(item.price),
                    "discount": float(item.discount),
                    "total": float(item.calculate_total())
                }
                for item in invoice.items
            ],
            "payments": [
                {
                    "id": payment.id,
                    "name": f"Payment_{payment.id}",
                    "value": float(payment.value)
                }
                for payment in (invoice.payments or [])
            ],
            "totals": {
                "subtotal": float(invoice.calculate_total()) if invoice.items else 0,
                "discount": 0,
                "taxes": 0,
                "total": float(invoice.total) if invoice.total else float(invoice.calculate_total())
            },
            "status": "Open",
            "observations": invoice.observations or ""
        }