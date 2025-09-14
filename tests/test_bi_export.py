"""
Tests for DataConta BI Export Module.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.application.services.BIExportService import BIExportService
from src.application.use_cases.invoice_use_cases import ExportToBIUseCase, ExportToBIRequest
from src.infrastructure.utils.csv_writer import CSVWriter
from src.infrastructure.utils.observation_extractor import ObservationExtractor


class TestBIExportService(unittest.TestCase):
    """Test cases for BI Export Service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api_client = Mock()
        self.mock_file_storage = Mock()
        self.mock_logger = Mock()
        
        # Mock invoice data
        self.sample_invoice = {
            "id": "12345",
            "document": {
                "id": "67890",
                "number": 1001
            },
            "date": "2024-09-15",
            "customer": {
                "identification": "12345678",
                "name": ["Cliente", "Ejemplo"],
                "address": {
                    "city": "Bogotá"
                }
            },
            "seller": {
                "identification": "87654321",
                "name": ["Vendedor", "Ejemplo"]
            },
            "total": 150000,
            "items": [
                {
                    "product": {
                        "id": "PROD001",
                        "name": "Producto 1"
                    },
                    "quantity": 2,
                    "price": 50000
                },
                {
                    "product": {
                        "id": "PROD002",
                        "name": "Producto 2"
                    },
                    "quantity": 1,
                    "price": 50000
                }
            ],
            "payments": [
                {
                    "id": "PAY001",
                    "name": "Efectivo",
                    "value": 150000
                }
            ],
            "observations": "Cliente tipo PERSONA NATURAL - Régimen SIMPLIFICADO"
        }
        
        self.bi_service = BIExportService(
            self.mock_api_client,
            self.mock_file_storage,
            self.mock_logger
        )
    
    def test_observation_extractor(self):
        """Test observation extraction utility."""
        extractor = ObservationExtractor()
        
        # Test client type extraction
        observations = "Cliente tipo PERSONA NATURAL - Régimen SIMPLIFICADO"
        client_type = extractor.extract_client_type(observations)
        self.assertEqual(client_type, "PERSONA NATURAL")
        
        # Test regime extraction
        regime = extractor.extract_regime(observations)
        self.assertEqual(regime, "SIMPLIFICADO")
        
        # Test with different format
        observations2 = "Tipo: PERSONA JURÍDICA, Régimen: COMÚN"
        client_type2 = extractor.extract_client_type(observations2)
        regime2 = extractor.extract_regime(observations2)
        
        self.assertEqual(client_type2, "PERSONA JURÍDICA")
        self.assertEqual(regime2, "COMÚN")
    
    def test_csv_writer(self):
        """Test CSV writer utility."""
        writer = CSVWriter()
        
        # Test data preparation
        data = [
            {"name": "Juan", "age": 30, "city": "Bogotá"},
            {"name": "Ana", "age": 25, "city": "Medellín"}
        ]
        
        columns = ["name", "age", "city"]
        csv_content = writer._prepare_data_for_csv(data, columns)
        
        expected_lines = [
            "name,age,city",
            "Juan,30,Bogotá",
            "Ana,25,Medellín"
        ]
        
        self.assertEqual(csv_content.strip().split('\n'), expected_lines)
    
    @patch('src.infrastructure.utils.csv_writer.CSVWriter')
    def test_bi_export_service_process_invoices(self, mock_csv_writer):
        """Test BI export service processing invoices."""
        # Setup mocks
        self.mock_api_client.get_invoices.return_value = {
            "results": [self.sample_invoice]
        }
        
        mock_csv_instance = MagicMock()
        mock_csv_writer.return_value = mock_csv_instance
        mock_csv_instance.write_csv.return_value = True
        
        # Test processing
        result = self.bi_service.process_invoices_to_bi_format(
            start_date="2024-09-01",
            end_date="2024-09-15",
            max_records=100
        )
        
        # Verify results
        self.assertTrue(result['success'])
        self.assertIn('facts_count', result['statistics'])
        self.assertIn('clients_count', result['statistics'])
        self.assertIn('sellers_count', result['statistics'])
        self.assertIn('products_count', result['statistics'])
        self.assertIn('payments_count', result['statistics'])
        self.assertIn('dates_count', result['statistics'])
    
    def test_export_to_bi_use_case(self):
        """Test Export to BI Use Case."""
        # Setup
        mock_license_validator = Mock()
        mock_license_validator.validate.return_value = True
        
        use_case = ExportToBIUseCase(
            bi_export_service=self.bi_service,
            license_validator=mock_license_validator,
            logger=self.mock_logger
        )
        
        # Create request
        request = ExportToBIRequest(
            start_date="2024-09-01",
            end_date="2024-09-15",
            max_records=100,
            validate_schema=True
        )
        
        # Mock service response
        self.bi_service.process_invoices_to_bi_format = Mock(return_value={
            'success': True,
            'message': 'Export successful',
            'statistics': {
                'facts_count': 1,
                'clients_count': 1,
                'sellers_count': 1,
                'products_count': 2,
                'payments_count': 1,
                'dates_count': 1
            },
            'files_created': {
                'fact_invoices.csv': True,
                'dim_clients.csv': True,
                'dim_sellers.csv': True,
                'dim_products.csv': True,
                'dim_payments.csv': True,
                'dim_dates.csv': True
            }
        })
        
        # Execute use case
        result = use_case.execute(request, "test-license-key")
        
        # Verify
        self.assertTrue(result.success)
        self.assertIsNotNone(result.statistics)
        self.assertIsNotNone(result.files_created)
    
    def test_bi_entities_creation(self):
        """Test BI entities creation from invoice data."""
        from src.domain.entities.invoice import FactInvoice, DimClient, DimSeller
        
        # Test FactInvoice creation
        fact = FactInvoice(
            invoice_id="12345",
            client_key="C001",
            seller_key="S001",
            product_key="P001",
            payment_key="PAY001",
            date_key="20240915",
            quantity=2,
            unit_price=50000.0,
            total_amount=100000.0
        )
        
        self.assertEqual(fact.invoice_id, "12345")
        self.assertEqual(fact.quantity, 2)
        self.assertEqual(fact.total_amount, 100000.0)
        
        # Test DimClient creation
        client = DimClient(
            client_key="C001",
            identification="12345678",
            name="Cliente Ejemplo",
            client_type="PERSONA NATURAL",
            regime="SIMPLIFICADO",
            city="Bogotá"
        )
        
        self.assertEqual(client.client_key, "C001")
        self.assertEqual(client.client_type, "PERSONA NATURAL")
        
        # Test DimSeller creation
        seller = DimSeller(
            seller_key="S001",
            identification="87654321",
            name="Vendedor Ejemplo"
        )
        
        self.assertEqual(seller.seller_key, "S001")
        self.assertEqual(seller.name, "Vendedor Ejemplo")


class TestBIIntegration(unittest.TestCase):
    """Integration tests for BI export functionality."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.test_output_dir = Path("test_outputs")
        self.test_output_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)
    
    @patch('src.infrastructure.adapters.siigo_api_adapter.SiigoAPIAdapter')
    @patch('src.infrastructure.adapters.file_storage_adapter.FileStorageAdapter')
    def test_full_bi_export_workflow(self, mock_file_storage, mock_api_client):
        """Test complete BI export workflow."""
        # This would be a more comprehensive integration test
        # For now, we'll keep it simple
        self.assertTrue(True, "Integration test placeholder - implement as needed")


if __name__ == '__main__':
    # Create test outputs directory
    Path("test_outputs").mkdir(exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)