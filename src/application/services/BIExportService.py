"""
DataConta - Business Intelligence Export Service
Service for generating star schema CSV files for Power BI consumption.
"""

from typing import List, Dict, Any, Set, Optional
from datetime import datetime
from decimal import Decimal

from src.application.ports.interfaces import Logger
from src.domain.entities.invoice import (
    FactInvoice, DimClient, DimSeller, DimProduct, DimPayment, DimDate
)
from src.domain.services.license_manager import LicenseManager
from src.infrastructure.utils.observation_extractor import ObservationExtractor
from src.infrastructure.utils.csv_writer import CSVWriter


class BIExportService:
    """
    Service for exporting invoice data to Business Intelligence star schema format.
    
    Generates fact table (invoices) and dimension tables (clients, sellers, products, 
    payments, dates) optimized for Power BI consumption.
    
    Now includes license validation for BI export operations.
    """
    
    def __init__(self, logger: Logger, license_manager: Optional[LicenseManager] = None):
        """Initialize the BI export service."""
        self._logger = logger
        self._license_manager = license_manager
        self._observation_extractor = ObservationExtractor(logger)
        self._csv_writer = CSVWriter(logger)
        
        # Collections for dimension deduplication
        self._clients: Dict[str, DimClient] = {}
        self._sellers: Dict[str, DimSeller] = {}
        self._products: Dict[str, DimProduct] = {}
        self._payments: Dict[str, DimPayment] = {}
        self._dates: Dict[str, DimDate] = {}
        self._facts: List[FactInvoice] = []
    
    def process_invoices_for_bi(self, invoices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process invoices and generate star schema data.
        
        Args:
            invoices_data: List of invoice dictionaries
            
        Returns:
            Dictionary with processing results and statistics
        """
        try:
            # Validate BI export license if license manager is available
            if self._license_manager:
                if not self._license_manager.can_export_bi():
                    raise ValueError(f"BI export not available for license {self._license_manager.get_license_display_name()}")
                
                # Validate count against BI limits
                is_valid, error_message = self._license_manager.validate_bi_export_limit(len(invoices_data))
                if not is_valid:
                    raise ValueError(error_message)
                
                self._logger.info(f"Starting BI export processing for {len(invoices_data)} invoices (License: {self._license_manager.get_license_display_name()})")
            else:
                self._logger.info(f"Starting BI export processing for {len(invoices_data)} invoices")
            
            # Clear previous data
            self._clear_collections()
            
            # Process each invoice
            processed_count = 0
            error_count = 0
            
            for invoice_data in invoices_data:
                try:
                    self._process_single_invoice(invoice_data)
                    processed_count += 1
                except Exception as e:
                    self._logger.error(f"Error processing invoice {invoice_data.get('id', 'unknown')}: {e}")
                    error_count += 1
            
            # Generate statistics
            stats = {
                "processed_invoices": processed_count,
                "error_invoices": error_count,
                "total_facts": len(self._facts),
                "unique_clients": len(self._clients),
                "unique_sellers": len(self._sellers),
                "unique_products": len(self._products),
                "unique_payments": len(self._payments),
                "unique_dates": len(self._dates)
            }
            
            # Add license information if available
            if self._license_manager:
                stats["license_info"] = {
                    "type": self._license_manager.get_license_display_name(),
                    "can_export_bi": self._license_manager.can_export_bi(),
                    "max_bi_invoices": self._license_manager.get_max_invoices_for_bi()
                }
            
            self._logger.info(f"BI processing completed: {stats}")
            return stats
            
        except Exception as e:
            self._logger.error(f"Error in BI export processing: {e}")
            raise
    
    def export_to_csv_files(self) -> Dict[str, bool]:
        """
        Export all star schema data to CSV files.
        
        Returns:
            Dictionary with filename as key and success status as value
        """
        try:
            self._logger.info("Starting CSV export for BI data")
            
            csv_data = {
                "fact_invoices.csv": {
                    "headers": FactInvoice.get_csv_headers(),
                    "rows": [fact.to_dict() for fact in self._facts]
                },
                "dim_clients.csv": {
                    "headers": DimClient.get_csv_headers(),
                    "rows": [client.to_dict() for client in self._clients.values()]
                },
                "dim_sellers.csv": {
                    "headers": DimSeller.get_csv_headers(),
                    "rows": [seller.to_dict() for seller in self._sellers.values()]
                },
                "dim_products.csv": {
                    "headers": DimProduct.get_csv_headers(),
                    "rows": [product.to_dict() for product in self._products.values()]
                },
                "dim_payments.csv": {
                    "headers": DimPayment.get_csv_headers(),
                    "rows": [payment.to_dict() for payment in self._payments.values()]
                },
                "dim_dates.csv": {
                    "headers": DimDate.get_csv_headers(),
                    "rows": [date.to_dict() for date in self._dates.values()]
                }
            }
            
            results = self._csv_writer.write_multiple_csvs(csv_data)
            
            self._logger.info(f"CSV export completed: {results}")
            return results
            
        except Exception as e:
            self._logger.error(f"Error exporting BI CSV files: {e}")
            raise
    
    def _clear_collections(self):
        """Clear all internal collections."""
        self._clients.clear()
        self._sellers.clear()
        self._products.clear()
        self._payments.clear()
        self._dates.clear()
        self._facts.clear()
    
    def _process_single_invoice(self, invoice_data: Dict[str, Any]):
        """Process a single invoice and extract all dimension and fact data."""
        invoice_id = str(invoice_data.get('id', ''))
        date_str = invoice_data.get('date', '')
        status = invoice_data.get('status', 'Unknown')
        observations = invoice_data.get('observations', '')
        
        # Process date dimension
        self._process_date_dimension(date_str)
        
        # Process customer dimension
        customer_data = invoice_data.get('customer', {})
        customer_id = str(customer_data.get('id', ''))
        self._process_client_dimension(customer_data, observations)
        
        # Process seller dimension
        seller_data = invoice_data.get('seller', {})
        seller_id = str(seller_data.get('id', ''))
        self._process_seller_dimension(seller_data)
        
        # Get totals
        totals = invoice_data.get('totals', {})
        subtotal = float(totals.get('subtotal', 0))
        descuento_total = float(totals.get('discount', 0))
        impuestos = float(totals.get('taxes', 0))
        total_factura = float(totals.get('total', 0))
        
        # Process items and payments (Cartesian product for facts)
        items = invoice_data.get('items', [])
        payments = invoice_data.get('payments', [])
        
        if not items:
            items = [{"code": "NO_ITEM", "description": "Sin items", "quantity": 0, "price": 0, "discount": 0, "total": 0}]
        
        if not payments:
            payments = [{"id": "NO_PAYMENT", "name": "Sin pago", "value": 0}]
        
        for item in items:
            # Process product dimension
            self._process_product_dimension(item)
            
            for payment in payments:
                # Process payment dimension
                self._process_payment_dimension(payment)
                
                # Create fact record
                fact = FactInvoice(
                    factura_id=invoice_id,
                    fecha=DimDate.from_date_string(date_str).fecha,
                    cliente_id=customer_id,
                    vendedor_id=seller_id,
                    producto_codigo=str(item.get('code', '')),
                    producto_cantidad=float(item.get('quantity', 0)),
                    producto_precio=float(item.get('price', 0)),
                    producto_descuento=float(item.get('discount', 0)),
                    producto_total=float(item.get('total', 0)),
                    pago_id=str(payment.get('id', '')),
                    subtotal=subtotal,
                    descuento_total=descuento_total,
                    impuestos=impuestos,
                    total=total_factura,
                    estado=status,
                    observaciones=observations[:500]  # Truncate long observations
                )
                
                self._facts.append(fact)
    
    def _process_client_dimension(self, customer_data: Dict[str, Any], observations: str):
        """Process and store client dimension data."""
        cliente_id = str(customer_data.get('id', ''))
        
        if cliente_id not in self._clients:
            # Extract client type and regime from observations
            tipo_cliente, regimen = self._observation_extractor.extract_client_info(observations)
            
            client = DimClient(
                cliente_id=cliente_id,
                identificacion=customer_data.get('identification', ''),
                nombre=customer_data.get('name', ''),
                email=customer_data.get('email', ''),
                tipo_cliente=tipo_cliente,
                regimen=regimen
            )
            
            self._clients[cliente_id] = client
    
    def _process_seller_dimension(self, seller_data: Dict[str, Any]):
        """Process and store seller dimension data."""
        seller_id = str(seller_data.get('id', ''))
        
        if seller_id not in self._sellers:
            seller = DimSeller(
                vendedor_id=seller_id,
                nombre=seller_data.get('name', ''),
                zona="No Especificado"  # Could be enhanced with additional data
            )
            
            self._sellers[seller_id] = seller
    
    def _process_product_dimension(self, item_data: Dict[str, Any]):
        """Process and store product dimension data."""
        product_code = str(item_data.get('code', ''))
        
        if product_code not in self._products:
            description = item_data.get('description', '')
            categoria = self._observation_extractor.extract_product_category(description)
            
            product = DimProduct(
                producto_codigo=product_code,
                descripcion=description,
                categoria=categoria,
                precio_estandar=float(item_data.get('price', 0))
            )
            
            self._products[product_code] = product
    
    def _process_payment_dimension(self, payment_data: Dict[str, Any]):
        """Process and store payment dimension data."""
        payment_id = str(payment_data.get('id', ''))
        
        if payment_id not in self._payments:
            payment_name = payment_data.get('name', '')
            categoria = self._observation_extractor.extract_payment_category(payment_name)
            
            payment = DimPayment(
                pago_id=payment_id,
                nombre=payment_name,
                categoria=categoria
            )
            
            self._payments[payment_id] = payment
    
    def _process_date_dimension(self, date_str: str):
        """Process and store date dimension data."""
        if not date_str:
            return
        
        dim_date = DimDate.from_date_string(date_str)
        
        if dim_date.fecha not in self._dates:
            self._dates[dim_date.fecha] = dim_date
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get current export statistics."""
        stats = {
            "facts_count": len(self._facts),
            "clients_count": len(self._clients),
            "sellers_count": len(self._sellers),
            "products_count": len(self._products),
            "payments_count": len(self._payments),
            "dates_count": len(self._dates),
            "output_directory": self._csv_writer.get_output_directory()
        }
        
        # Add license information if available
        if self._license_manager:
            stats["license_info"] = {
                "type": self._license_manager.get_license_display_name(),
                "can_export_bi": self._license_manager.can_export_bi(),
                "max_bi_invoices": self._license_manager.get_max_invoices_for_bi(),
                "bi_features_available": self._license_manager.has_feature("bi_export")
            }
        
        return stats
    
    def validate_star_schema(self) -> Dict[str, Any]:
        """
        Validate the generated star schema for consistency.
        
        Returns:
            Dictionary with validation results
        """
        try:
            validation = {
                "valid": True,
                "warnings": [],
                "errors": []
            }
            
            # Check for orphaned foreign keys in facts
            fact_client_ids = {fact.cliente_id for fact in self._facts}
            dim_client_ids = set(self._clients.keys())
            orphaned_clients = fact_client_ids - dim_client_ids
            
            if orphaned_clients:
                validation["warnings"].append(f"Orphaned client IDs in facts: {orphaned_clients}")
            
            # Check for missing required dimensions
            if not self._clients:
                validation["errors"].append("No clients dimension data")
                validation["valid"] = False
            
            if not self._facts:
                validation["errors"].append("No fact data")
                validation["valid"] = False
            
            self._logger.info(f"Star schema validation: {'PASSED' if validation['valid'] else 'FAILED'}")
            
            return validation
            
        except Exception as e:
            self._logger.error(f"Error validating star schema: {e}")
            return {"valid": False, "errors": [str(e)], "warnings": []}