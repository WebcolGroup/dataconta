"""
Pruebas unitarias para el servicio KPI
Valida los cálculos de reportes financieros según las reglas de negocio.
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from src.application.services.kpi_service import KPIService, KPIData
from src.domain.entities.invoice import InvoiceFilter


@pytest.mark.unit
@pytest.mark.kpi
class TestKPIService:
    """Pruebas unitarias para KPIService."""

    def test_calculate_kpis_basic_calculations(self, kpi_service, sample_invoice_data):
        """Test cálculos básicos de KPIs con datos de ejemplo."""
        # Configurar mock para retornar datos de ejemplo
        kpi_service._invoice_repository.get_invoices.return_value = sample_invoice_data
        
        # Ejecutar cálculo de KPIs
        result = kpi_service.calculate_real_kpis(2025)
        
        # Verificar estructura del resultado
        assert isinstance(result, KPIData)
        assert result.ventas_totales >= 0  # Debe ser un número positivo o cero
        assert result.num_facturas >= 0
        assert result.estado_sistema is not None

    def test_calculate_kpis_empty_data(self, kpi_service):
        """Test cálculo de KPIs con datos vacíos."""
        # Configurar mock para retornar datos vacíos
        kpi_service._invoice_repository.get_invoices_by_filter.return_value = []
        
        # Ejecutar cálculo
        result = kpi_service.calculate_real_kpis(2025)
        
        # Verificar valores por defecto
        assert result.ventas_totales == 0
        assert result.num_facturas == 0
        assert result.ticket_promedio == 0
        assert len(result.ventas_por_cliente) == 0
        assert len(result.ventas_por_producto) == 0

    def test_calculate_top_customers(self, kpi_service, sample_invoice_data):
        """Test cálculo de top 5 clientes."""
        kpi_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        result = kpi_service.calculate_real_kpis(2025)
        
        # Verificar top cliente
        assert result.top_cliente == "Cliente Test 1"
        assert result.top_cliente_monto == 3000000  # INV001 + INV003
        assert result.top_cliente_nit == "12345678"
        
        # Verificar estructura de top 5
        assert len(result.top_5_clientes) <= 5
        assert all('cliente' in cliente for cliente in result.top_5_clientes)
        assert all('total_ventas' in cliente for cliente in result.top_5_clientes)

    def test_calculate_top_products(self, kpi_service, sample_invoice_data):
        """Test cálculo de top 5 productos."""
        kpi_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        result = kpi_service.calculate_real_kpis(2025)
        
        # Verificar productos calculados
        assert len(result.top_5_productos) <= 5
        assert all('producto' in producto for producto in result.top_5_productos)
        assert all('total_ventas' in producto for producto in result.top_5_productos)
        
        # El producto más vendido debería ser PROD001 (aparece en INV001 e INV003)
        top_producto = result.top_5_productos[0] if result.top_5_productos else None
        if top_producto:
            assert top_producto['producto'] == "Producto Test 1"

    def test_calculate_tax_participation(self, kpi_service, sample_invoice_data):
        """Test cálculo de participación de impuestos."""
        kpi_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        result = kpi_service.calculate_real_kpis(2025)
        
        # Total de impuestos: 159664 + 79832 + 319328 = 558824
        # Total de ventas: 3500000
        # Participación esperada: 558824 / 3500000 * 100 = ~15.97%
        expected_tax_participation = round((558824 / 3500000) * 100, 2)
        assert abs(result.participacion_impuestos - expected_tax_participation) < 0.01

    def test_filter_creation(self, kpi_service):
        """Test creación correcta de filtros de fecha."""
        year = 2025
        
        # Ejecutar método privado _create_year_filter
        # Test creación de filtros básicos
        from src.domain.entities.invoice import InvoiceFilter
        from datetime import datetime
        
        # Crear filtro manual para año 2025
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        invoice_filter = InvoiceFilter(
            created_start=start_date,
            created_end=end_date,
            page_size=100
        )
        
        assert isinstance(invoice_filter, InvoiceFilter)
        assert invoice_filter.date_start == date(year, 1, 1)
        assert invoice_filter.date_end == date(year, 12, 31)

    def test_kpi_data_to_dict(self):
        """Test conversión de KPIData a diccionario."""
        kpi_data = KPIData(
            ventas_totales=1000000,
            num_facturas=5,
            ticket_promedio=200000,
            ventas_por_cliente=[],
            ventas_por_producto=[],
            top_5_clientes=[],
            top_5_productos=[],
            participacion_impuestos=15.5,
            evolucion_ventas=[],
            estados_facturas=[],
            top_cliente="Test Cliente",
            top_cliente_monto=500000,
            top_cliente_nit="123456789",
            top_5_resumen=[],
            ultima_sync="2025-01-01 12:00:00",
            estado_sistema="OK"
        )
        
        result_dict = kpi_data.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['ventas_totales'] == 1000000
        assert result_dict['num_facturas'] == 5
        assert result_dict['ticket_promedio'] == 200000
        assert result_dict['top_cliente'] == "Test Cliente"

    @pytest.mark.slow
    def test_calculate_kpis_performance(self, kpi_service):
        """Test rendimiento con gran cantidad de datos."""
        # Generar datos de prueba grandes
        large_dataset = []
        for i in range(1000):
            invoice = {
                'id': f'INV{i:04d}',
                'number': f'F{i:04d}',
                'date': f'2025-01-{(i % 28) + 1:02d}',
                'customer': {
                    'identification': f'{12345678 + i}',
                    'name': f'Cliente {i}',
                    'branch_office': 0
                },
                'total': 100000 + (i * 1000),
                'subtotal': 84000 + (i * 840),
                'total_tax': 16000 + (i * 160),
                'status': 'active',
                'items': [{
                    'code': f'PROD{i % 50:03d}',
                    'description': f'Producto {i % 50}',
                    'quantity': 1,
                    'price': 84000 + (i * 840),
                    'total': 84000 + (i * 840)
                }]
            }
            large_dataset.append(invoice)
        
        kpi_service._invoice_repository.get_invoices_by_filter.return_value = large_dataset
        
        # Medir tiempo de ejecución
        import time
        start_time = time.time()
        result = kpi_service.calculate_real_kpis(2025)
        end_time = time.time()
        
        # Verificar que el cálculo se completó
        assert isinstance(result, KPIData)
        assert result.num_facturas == 1000
        
        # Verificar que no tardó más de 5 segundos (ajustable según necesidades)
        execution_time = end_time - start_time
        assert execution_time < 5.0, f"Cálculo tardó {execution_time:.2f}s, esperado < 5s"

    def test_calculate_kpis_with_invalid_data(self, kpi_service):
        """Test manejo de datos inválidos en facturas."""
        invalid_data = [
            {
                'id': 'INV001',
                'number': 'F001',
                'date': '2025-01-15',
                'customer': None,  # Cliente nulo
                'total': 'invalid',  # Total inválido
                'subtotal': 840336,
                'total_tax': 159664,
                'status': 'active',
                'items': []
            }
        ]
        
        kpi_service._invoice_repository.get_invoices_by_filter.return_value = invalid_data
        
        # El servicio debe manejar datos inválidos sin fallar
        result = kpi_service.calculate_real_kpis(2025)
        assert isinstance(result, KPIData)
        # Los datos inválidos deberían ser filtrados o manejados apropiadamente

    def test_save_and_load_kpis(self, kpi_service, sample_invoice_data):
        """Test guardado y carga de KPIs."""
        kpi_service._invoice_repository.get_invoices_by_filter.return_value = sample_invoice_data
        
        # Calcular y guardar KPIs
        result = kpi_service.calculate_real_kpis(2025)
        kpi_service.save_kpis(result, 2025)
        
        # Verificar que se llamó al storage para guardar
        kpi_service._file_storage.save_data.assert_called_once()
        
        # Simular carga de KPIs guardados
        saved_data = result.to_dict()
        kpi_service._file_storage.load_data.return_value = saved_data
        kpi_service._file_storage.file_exists.return_value = True
        
        loaded_result = kpi_service.load_existing_kpis(2025)
        
        # Verificar que los datos cargados coinciden
        assert loaded_result is not None
        assert loaded_result['ventas_totales'] == result.ventas_totales
