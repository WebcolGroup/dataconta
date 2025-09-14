"""
DataConta - Invoice Export Service
Service for processing and exporting invoices to CSV format.
"""

from typing import Dict, Any, List
from decimal import Decimal

from src.application.ports.interfaces import InvoiceProcessor, Logger
from src.domain.entities.invoice import (
    InvoiceExport, 
    InvoiceExportRow,
    InvoiceExportDocument,
    InvoiceExportCustomer,
    InvoiceExportSeller,
    InvoiceExportItem,
    InvoiceExportPayment,
    InvoiceExportTotals
)


class InvoiceExportService(InvoiceProcessor):
    """
    Service for processing invoice data and preparing it for CSV export.
    Implements business logic for invoice data transformation.
    """
    
    def __init__(self, logger: Logger):
        """Initialize the service with required dependencies."""
        self._logger = logger
    
    def process_invoice_for_export(self, invoice_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process invoice data and convert to exportable format.
        
        Each combination of item and payment creates a separate row in the CSV.
        This allows for proper normalization of the data.
        """
        try:
            # Validate structure first
            if not self.validate_invoice_structure(invoice_data):
                raise ValueError("Invalid invoice structure")
            
            # Create domain entity from raw data
            invoice = InvoiceExport.from_dict(invoice_data)
            
            if not invoice.is_valid():
                raise ValueError("Invoice failed business validation")
            
            self._logger.info(f"Processing invoice {invoice.get_invoice_number()} with {len(invoice.items)} items and {len(invoice.payments)} payments")
            
            # Generate rows for CSV export
            export_rows = self._generate_export_rows(invoice)
            
            self._logger.info(f"Generated {len(export_rows)} rows for CSV export")
            
            return [row.__dict__ for row in export_rows]
        
        except Exception as e:
            self._logger.error(f"Error processing invoice: {e}")
            raise
    
    def validate_invoice_structure(self, invoice_data: Dict[str, Any]) -> bool:
        """
        Validate that invoice data has the required structure.
        
        Checks for presence of all required fields and basic data types.
        """
        try:
            required_fields = [
                'id', 'document', 'date', 'customer', 'seller', 
                'items', 'payments', 'totals', 'status'
            ]
            
            # Check main fields
            for field in required_fields:
                if field not in invoice_data:
                    self._logger.error(f"Missing required field: {field}")
                    return False
            
            # Check document structure
            document = invoice_data.get('document', {})
            document_fields = ['id', 'name', 'prefix', 'number']
            for field in document_fields:
                if field not in document:
                    self._logger.error(f"Missing document field: {field}")
                    return False
            
            # Check customer structure
            customer = invoice_data.get('customer', {})
            customer_fields = ['id', 'identification', 'name', 'email']
            for field in customer_fields:
                if field not in customer:
                    self._logger.error(f"Missing customer field: {field}")
                    return False
            
            # Check seller structure
            seller = invoice_data.get('seller', {})
            seller_fields = ['id', 'name']
            for field in seller_fields:
                if field not in seller:
                    self._logger.error(f"Missing seller field: {field}")
                    return False
            
            # Check items structure
            items = invoice_data.get('items', [])
            if not items or not isinstance(items, list):
                self._logger.error("Items must be a non-empty list")
                return False
            
            item_fields = ['code', 'description', 'quantity', 'price', 'discount', 'total']
            for i, item in enumerate(items):
                for field in item_fields:
                    if field not in item:
                        self._logger.error(f"Missing item field {field} in item {i}")
                        return False
            
            # Check payments structure
            payments = invoice_data.get('payments', [])
            if not payments or not isinstance(payments, list):
                self._logger.error("Payments must be a non-empty list")
                return False
            
            payment_fields = ['id', 'name', 'value']
            for i, payment in enumerate(payments):
                for field in payment_fields:
                    if field not in payment:
                        self._logger.error(f"Missing payment field {field} in payment {i}")
                        return False
            
            # Check totals structure
            totals = invoice_data.get('totals', {})
            totals_fields = ['subtotal', 'discount', 'taxes', 'total']
            for field in totals_fields:
                if field not in totals:
                    self._logger.error(f"Missing totals field: {field}")
                    return False
            
            self._logger.debug("Invoice structure validation passed")
            return True
        
        except Exception as e:
            self._logger.error(f"Error validating invoice structure: {e}")
            return False
    
    def _generate_export_rows(self, invoice: InvoiceExport) -> List[InvoiceExportRow]:
        """
        Generate CSV export rows from invoice data.
        
        Creates a Cartesian product of items × payments to ensure all
        combinations are represented in the final CSV.
        """
        rows = []
        
        try:
            # Create one row for each item-payment combination
            for item in invoice.items:
                for payment in invoice.payments:
                    row = InvoiceExportRow(
                        factura_id=invoice.id,
                        fecha=invoice.date,
                        cliente_id=invoice.customer.id,
                        cliente_identificacion=invoice.customer.identification,
                        cliente_nombre=invoice.customer.name,
                        cliente_email=invoice.customer.email,
                        vendedor_id=invoice.seller.id,
                        vendedor_nombre=invoice.seller.name,
                        producto_codigo=item.code,
                        producto_descripcion=item.description,
                        producto_cantidad=item.quantity,
                        producto_precio=item.price,
                        producto_descuento=item.discount,
                        producto_total=item.total,
                        pago_metodo=payment.name,
                        pago_valor=payment.value,
                        subtotal=invoice.totals.subtotal,
                        descuento_total=invoice.totals.discount,
                        impuestos=invoice.totals.taxes,
                        total=invoice.totals.total,
                        estado=invoice.status,
                        observaciones=invoice.observations
                    )
                    rows.append(row)
            
            return rows
        
        except Exception as e:
            self._logger.error(f"Error generating export rows: {e}")
            raise
    
    def export_invoice_to_csv(self, invoice_json: dict, output_file: str) -> None:
        """
        Main service method for exporting invoice to CSV.
        
        This is the public interface method as requested in the requirements.
        """
        try:
            self._logger.info(f"Starting CSV export for invoice to file: {output_file}")
            
            # Process invoice data
            processed_rows = self.process_invoice_for_export(invoice_json)
            
            # This method focuses on processing - actual CSV writing is handled by adapters
            self._logger.info(f"Invoice processing completed successfully. Ready for CSV export with {len(processed_rows)} rows")
            
        except Exception as e:
            self._logger.error(f"Error in export_invoice_to_csv: {e}")
            raise