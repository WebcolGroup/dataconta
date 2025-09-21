"""
Test unitario para KPIApplicationService.
Valida la orquestación correcta sin lógica de negocio propia.
"""

import unittest
import pandas as pd
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from src.application.services.kpi_service import KPIApplicationService
from src.domain.entities.kpis import KPIsVentas, VentaPorCliente


class TestKPIApplicationService(unittest.TestCase):
    """Test suite for KPIApplicationService."""
    
    def setUp(self):
        """Configurar mocks y datos de prueba."""
        # Mocks de dependencias
        self.mock_invoice_repository = Mock()
        self.mock_file_storage = Mock()
        self.mock_kpi_calculation_service = Mock()
        self.mock_kpi_analysis_service = Mock()
        self.mock_logger = Mock()
        
        # Instanciar servicio con dependencias inyectadas
        self.app_service = KPIApplicationService(
            invoice_repository=self.mock_invoice_repository,
            file_storage=self.mock_file_storage,
            kpi_calculation_service=self.mock_kpi_calculation_service,
            kpi_analysis_service=self.mock_kpi_analysis_service,
            logger=self.mock_logger
        )
        
        # Datos de prueba
        self.fecha_inicio = datetime(2024, 1, 1)
        self.fecha_fin = datetime(2024, 12, 31)
        
        # Mock del resultado de KPIs
        ventas_cliente = [
            VentaPorCliente(
                nit="123456789",
                nombre="Cliente Test",
                total_ventas=Decimal("1000000.00"),
                numero_facturas=10,
                ticket_promedio=Decimal("100000.00")
            )
        ]
        
        self.mock_kpis = KPIsVentas(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin,
            ventas_totales=Decimal("1000000.00"),
            numero_facturas=10,
            ticket_promedio=Decimal("100000.00"),
            ventas_por_cliente=ventas_cliente,
            fecha_calculo=datetime.now(),
            estado_sistema="ACTIVO ✅"
        )
    
    def test_calculate_kpis_for_period_exitoso(self):
        """Test cálculo exitoso de KPIs para un período."""
        # Mock _obtener_facturas_dataframe method
        with patch.object(self.app_service, '_obtener_facturas_dataframe') as mock_obtener:
            mock_obtener.return_value = pd.DataFrame([
                {'total': 500000.0, 'cliente_nit': '123456789'},
                {'total': 500000.0, 'cliente_nit': '123456789'}
            ])
            
            # Mock services
            self.mock_kpi_calculation_service.validar_consistencia_datos.return_value = {'es_valido': True, 'errores': []}
            self.mock_kpi_calculation_service.calcular_kpis_ventas.return_value = self.mock_kpis
            self.mock_kpi_analysis_service.generar_insights.return_value = ["Insight 1", "Insight 2"]
            
            # Mock _guardar_kpis method
            with patch.object(self.app_service, '_guardar_kpis') as mock_guardar:
                # Ejecutar
                resultado = self.app_service.calculate_kpis_for_period(
                    fecha_inicio=self.fecha_inicio,
                    fecha_fin=self.fecha_fin
                )
            
            # Verificar orquestación correcta
            mock_obtener.assert_called_once_with(self.fecha_inicio, self.fecha_fin)
            self.mock_kpi_calculation_service.validar_consistencia_datos.assert_called_once()
            self.mock_kpi_calculation_service.calcular_kpis_ventas.assert_called_once()
            self.mock_kpi_analysis_service.generar_insights.assert_called_once()
            mock_guardar.assert_called_once()
        
        # Verificar resultado
        self.assertIsInstance(resultado, dict)
        self.assertIn('ventas_totales', resultado)
        self.assertIn('insights', resultado)
    
    def test_calculate_kpis_sin_datos(self):
        """Test manejo de período sin datos."""
        # Mock sin datos
        with patch.object(self.app_service, '_obtener_facturas_dataframe') as mock_obtener:
            mock_obtener.return_value = None
            self.mock_kpi_calculation_service.calcular_kpis_ventas.return_value = self.mock_kpis
            
            # Ejecutar
            resultado = self.app_service.calculate_kpis_for_period(
                fecha_inicio=self.fecha_inicio,
                fecha_fin=self.fecha_fin
            )
        
        # Verificar resultado
        self.assertIsInstance(resultado, dict)
    
    def test_calculate_kpis_error_validacion(self):
        """Test manejo de errores de validación."""
        # Mock error de validación
        with patch.object(self.app_service, '_obtener_facturas_dataframe') as mock_obtener:
            mock_obtener.return_value = pd.DataFrame([{'total': 100}])
            self.mock_kpi_calculation_service.validar_consistencia_datos.return_value = {
                'es_valido': False, 
                'errores': ['Error de validación']
            }
            
            # Ejecutar y verificar excepción
            with self.assertRaises(ValueError):
                self.app_service.calculate_kpis_for_period(
                    fecha_inicio=self.fecha_inicio,
                    fecha_fin=self.fecha_fin
                )
    
    def test_calculate_kpis_for_current_year(self):
        """Test cálculo de KPIs para año actual."""
        with patch.object(self.app_service, 'calculate_kpis_for_period') as mock_calc:
            mock_calc.return_value = {'test': 'data'}
            
            resultado = self.app_service.calculate_kpis_for_current_year()
            
            self.assertIsInstance(resultado, dict)
            mock_calc.assert_called_once()
    
    def test_constructor_requires_dependencies(self):
        """Test que el constructor requiere todas las dependencias."""
        with self.assertRaises(TypeError):
            KPIApplicationService()


if __name__ == '__main__':
    unittest.main()