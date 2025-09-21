"""
Pruebas unitarias para el servicio de exportación
Valida exportaciones CSV/Excel con diferentes formatos y datos.
"""

import pytest
import os
import pandas as pd
from datetime import datetime, date
from unittest.mock import Mock, patch, mock_open
from typing import List, Dict, Any

from src.application.services.export_service import ExportService, ExportResult
from src.domain.entities.invoice import InvoiceFilter


@pytest.mark.unit
@pytest.mark.export
class TestExportService:
    """Pruebas unitarias para ExportService."""

    def test_export_to_csv_success(self, export_service, sample_invoice_data, temp_output_dir):
        """Test exportación exitosa a CSV."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        # Configurar filtros
        date_filter = InvoiceFilter(
            created_start=datetime(2025, 1, 1),
            created_end=datetime(2025, 1, 31)
        )
        
        # Ejecutar exportación
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            mock_to_csv.return_value = None
            result = export_service.export_to_csv(date_filter, temp_output_dir)
        
        # Verificar resultado
        assert isinstance(result, ExportResult)
        assert result.success is True
        assert result.records_exported == 3
        assert result.file_path.endswith('.csv')
        assert result.error_message is None
        
        # Verificar que se llamó a to_csv
        mock_to_csv.assert_called_once()

    def test_export_to_excel_success(self, export_service, sample_invoice_data, temp_output_dir):
        """Test exportación exitosa a Excel."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        date_filter = InvoiceFilter(
            created_start=datetime(2025, 1, 1),
            created_end=datetime(2025, 1, 31)
        )
        
        # Mock del ExcelWriter
        with patch('pandas.ExcelWriter') as mock_excel_writer:
            mock_writer_instance = Mock()
            mock_excel_writer.return_value.__enter__.return_value = mock_writer_instance
            
            with patch('pandas.DataFrame.to_excel') as mock_to_excel:
                result = export_service.export_to_excel(date_filter, temp_output_dir)
        
        # Verificar resultado
        assert isinstance(result, ExportResult)
        assert result.success is True
        assert result.records_exported == 3
        assert result.file_path.endswith('.xlsx')
        assert result.error_message is None

    def test_export_empty_data(self, export_service, temp_output_dir):
        """Test exportación con datos vacíos."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = []
        
        date_filter = InvoiceFilter(
            created_start=datetime(2025, 1, 1),
            created_end=datetime(2025, 1, 31)
        )
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            result = export_service.export_to_csv(date_filter, temp_output_dir)
        
        # Debe manejar datos vacíos correctamente
        assert isinstance(result, ExportResult)
        assert result.records_exported == 0
        # Puede ser exitoso o fallar dependiendo de la implementación

    def test_export_invalid_path(self, export_service, sample_invoice_data):
        """Test exportación con path inválido."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        date_filter = InvoiceFilter(
            date_start=date(2025, 1, 1),
            date_end=date(2025, 1, 31)
        )
        
        # Path inválido
        invalid_path = "/path/that/does/not/exist"
        
        result = export_service.export_to_csv(date_filter, invalid_path)
        
        # Debe manejar el error apropiadamente
        assert isinstance(result, ExportResult)
        assert result.success is False
        assert result.error_message is not None

    def test_export_data_transformation(self, export_service, sample_invoice_data):
        """Test transformación correcta de datos para exportación."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        # Obtener datos transformados
        transformed_data = export_service._transform_invoices_for_export(sample_invoice_data)
        
        # Verificar estructura
        assert isinstance(transformed_data, list)
        assert len(transformed_data) == 3
        
        # Verificar campos requeridos en el primer registro
        first_record = transformed_data[0]
        required_fields = [
            'numero_factura', 'fecha', 'cliente_nombre', 'cliente_nit',
            'subtotal', 'impuestos', 'total', 'estado'
        ]
        
        for field in required_fields:
            assert field in first_record, f"Campo '{field}' faltante en exportación"
        
        # Verificar formato de datos
        assert isinstance(first_record['total'], (int, float))
        assert isinstance(first_record['fecha'], str)

    def test_export_with_filters(self, export_service, sample_invoice_data, temp_output_dir):
        """Test exportación con diferentes filtros aplicados."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        # Filtro por estado
        filter_by_status = InvoiceFilter(
            date_start=date(2025, 1, 1),
            date_end=date(2025, 1, 31),
            status='active'
        )
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            result = export_service.export_to_csv(filter_by_status, temp_output_dir)
        
        assert result.success is True
        # Verificar que se aplicaron los filtros correctamente
        call_args = export_service._invoice_repository.get_invoices_by_filter.call_args[0][0]
        assert call_args.status == 'active'

    def test_export_file_naming(self, export_service, sample_invoice_data, temp_output_dir):
        """Test convención de nombres de archivos exportados."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        date_filter = InvoiceFilter(
            date_start=date(2025, 1, 1),
            date_end=date(2025, 1, 31)
        )
        
        with patch('pandas.DataFrame.to_csv'):
            result = export_service.export_to_csv(date_filter, temp_output_dir)
        
        # Verificar patrón de nombre
        filename = os.path.basename(result.file_path)
        assert 'facturas_' in filename
        assert filename.endswith('.csv')
        assert len(filename) > 15  # Debe incluir timestamp

    def test_export_error_handling(self, export_service, sample_invoice_data, temp_output_dir):
        """Test manejo de errores durante exportación."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        date_filter = InvoiceFilter(
            date_start=date(2025, 1, 1),
            date_end=date(2025, 1, 31)
        )
        
        # Simular error en pandas
        with patch('pandas.DataFrame.to_csv', side_effect=Exception("Error simulado")):
            result = export_service.export_to_csv(date_filter, temp_output_dir)
        
        # Debe capturar y reportar el error
        assert isinstance(result, ExportResult)
        assert result.success is False
        assert result.error_message is not None
        assert "Error simulado" in result.error_message

    @pytest.mark.integration
    def test_export_csv_integration(self, export_service, sample_invoice_data, temp_output_dir):
        """Test integración completa de exportación CSV."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        date_filter = InvoiceFilter(
            date_start=date(2025, 1, 1),
            date_end=date(2025, 1, 31)
        )
        
        # Exportación real (sin mocks)
        result = export_service.export_to_csv(date_filter, temp_output_dir)
        
        # Verificar que el archivo se creó
        assert result.success is True
        assert os.path.exists(result.file_path)
        
        # Leer y verificar contenido
        df = pd.read_csv(result.file_path)
        assert len(df) == 3
        assert 'numero_factura' in df.columns
        assert 'total' in df.columns

    @pytest.mark.integration  
    def test_export_excel_integration(self, export_service, sample_invoice_data, temp_output_dir):
        """Test integración completa de exportación Excel."""
        export_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        date_filter = InvoiceFilter(
            date_start=date(2025, 1, 1),
            date_end=date(2025, 1, 31)
        )
        
        # Exportación real
        result = export_service.export_to_excel(date_filter, temp_output_dir)
        
        # Verificar archivo
        assert result.success is True
        assert os.path.exists(result.file_path)
        
        # Leer y verificar contenido Excel
        df = pd.read_excel(result.file_path, sheet_name='Facturas')
        assert len(df) == 3
        assert 'numero_factura' in df.columns

    def test_export_large_dataset_performance(self, export_service, temp_output_dir):
        """Test rendimiento con dataset grande."""
        # Generar dataset grande
        large_dataset = []
        for i in range(10000):
            invoice = {
                'id': f'INV{i:06d}',
                'number': f'F{i:06d}',
                'date': '2025-01-15',
                'customer': {
                    'identification': f'{12345678 + i}',
                    'name': f'Cliente {i}',
                    'branch_office': 0
                },
                'total': 100000 + i,
                'subtotal': 84000 + i,
                'total_tax': 16000,
                'status': 'active',
                'items': []
            }
            large_dataset.append(invoice)
        
        export_service._invoice_repository.get_invoices_by_filter.return_value = large_dataset
        
        date_filter = InvoiceFilter(
            date_start=date(2025, 1, 1),
            date_end=date(2025, 1, 31)
        )
        
        # Medir tiempo de exportación
        import time
        start_time = time.time()
        result = export_service.export_to_csv(date_filter, temp_output_dir)
        end_time = time.time()
        
        # Verificar resultado y rendimiento
        assert result.success is True
        assert result.records_exported == 10000
        
        execution_time = end_time - start_time
        assert execution_time < 30.0, f"Exportación tardó {execution_time:.2f}s, esperado < 30s"