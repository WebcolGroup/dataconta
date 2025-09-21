"""
Test para Application Services - Application Layer
Tests unitarios para validar servicios de aplicación y orquestación
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from decimal import Decimal
import pandas as pd

from src.application.services.kpi_service import KPIApplicationService
from src.domain.entities.kpis import KPIsVentas, VentaPorCliente


class TestKPIApplicationService(unittest.TestCase):
    """Tests para el servicio de aplicación de KPIs."""
    
    def setUp(self):
        """Configurar mocks y datos de prueba."""
        # Mocks de dependencias
        self.mock_domain_service = Mock()
        self.mock_siigo_adapter = Mock()
        self.mock_export_service = Mock()
        self.mock_validation_service = Mock()
        
        # Instanciar servicio con dependencias inyectadas
        self.app_service = KPIApplicationService(
            kpi_calculation_service=self.mock_domain_service,
            siigo_adapter=self.mock_siigo_adapter,
            export_service=self.mock_export_service,
            validation_service=self.mock_validation_service
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
        # Configurar mocks
        mock_facturas_df = pd.DataFrame([
            {'total': 500000.0, 'cliente_nit': '123456789', 'cliente_nombre': 'Cliente Test'},
            {'total': 500000.0, 'cliente_nit': '123456789', 'cliente_nombre': 'Cliente Test'}
        ])
        
        self.mock_siigo_adapter.obtener_facturas_periodo.return_value = mock_facturas_df
        self.mock_validation_service.validar_datos_facturas.return_value = {'es_valido': True, 'errores': []}
        self.mock_domain_service.calcular_kpis_ventas.return_value = self.mock_kpis
        
        # Ejecutar
        resultado = self.app_service.calculate_kpis_for_period(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin
        )
        
        # Verificar orquestación correcta
        self.mock_siigo_adapter.obtener_facturas_periodo.assert_called_once_with(
            self.fecha_inicio, self.fecha_fin
        )
        self.mock_validation_service.validar_datos_facturas.assert_called_once()
        self.mock_domain_service.calcular_kpis_ventas.assert_called_once()
        
        # Verificar resultado
        self.assertIsInstance(resultado, dict)
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['kpis'], self.mock_kpis)
        self.assertIsNone(resultado['error'])
    
    def test_calculate_kpis_datos_invalidos(self):
        """Test manejo de datos inválidos."""
        # Mock datos inválidos
        self.mock_siigo_adapter.obtener_facturas_periodo.return_value = pd.DataFrame()
        self.mock_validation_service.validar_datos_facturas.return_value = {
            'es_valido': False, 
            'errores': ['No hay datos para el período']
        }
        
        # Ejecutar
        resultado = self.app_service.calculate_kpis_for_period(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin
        )
        
        # Verificar que no se llamó al dominio
        self.mock_domain_service.calcular_kpis_ventas.assert_not_called()
        
        # Verificar resultado de error
        self.assertFalse(resultado['success'])
        self.assertIsNone(resultado['kpis'])
        self.assertIn('validación', resultado['error'])
    
    def test_calculate_kpis_error_siigo(self):
        """Test manejo de errores del adapter Siigo."""
        # Mock error en Siigo
        self.mock_siigo_adapter.obtener_facturas_periodo.side_effect = Exception("Error API Siigo")
        
        # Ejecutar
        resultado = self.app_service.calculate_kpis_for_period(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin
        )
        
        # Verificar manejo de error
        self.assertFalse(resultado['success'])
        self.assertIsNone(resultado['kpis'])
        self.assertIn('Error API Siigo', resultado['error'])
    
    def test_export_kpis_to_excel_exitoso(self):
        """Test exportación exitosa a Excel."""
        # Configurar mocks
        mock_file_path = "c:\\temp\\kpis_2024.xlsx"
        self.mock_export_service.exportar_kpis_excel.return_value = {
            'success': True,
            'file_path': mock_file_path,
            'error': None
        }
        
        # Ejecutar
        resultado = self.app_service.export_kpis_to_excel(
            kpis=self.mock_kpis,
            output_path="c:\\temp\\"
        )
        
        # Verificar llamada al servicio de exportación
        self.mock_export_service.exportar_kpis_excel.assert_called_once_with(
            kpis=self.mock_kpis,
            output_path="c:\\temp\\"
        )
        
        # Verificar resultado
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['file_path'], mock_file_path)
        self.assertIsNone(resultado['error'])
    
    def test_export_kpis_error_exportacion(self):
        """Test error en exportación a Excel."""
        # Mock error en exportación
        self.mock_export_service.exportar_kpis_excel.return_value = {
            'success': False,
            'file_path': None,
            'error': 'No se puede escribir archivo'
        }
        
        # Ejecutar
        resultado = self.app_service.export_kpis_to_excel(
            kpis=self.mock_kpis,
            output_path="c:\\temp\\"
        )
        
        # Verificar resultado de error
        self.assertFalse(resultado['success'])
        self.assertIsNone(resultado['file_path'])
        self.assertEqual(resultado['error'], 'No se puede escribir archivo')
    
    def test_get_kpis_summary(self):
        """Test obtención de resumen de KPIs."""
        resultado = self.app_service.get_kpis_summary(self.mock_kpis)
        
        # Verificar estructura del resumen
        self.assertIn('ventas_totales', resultado)
        self.assertIn('numero_facturas', resultado)
        self.assertIn('ticket_promedio', resultado)
        self.assertIn('numero_clientes', resultado)
        self.assertIn('cliente_principal', resultado)
        self.assertIn('fecha_calculo', resultado)
        
        # Verificar valores
        self.assertEqual(resultado['ventas_totales'], self.mock_kpis.ventas_totales)
        self.assertEqual(resultado['numero_facturas'], self.mock_kpis.numero_facturas)
        self.assertEqual(resultado['numero_clientes'], len(self.mock_kpis.ventas_por_cliente))
    
    def test_validate_date_range_valido(self):
        """Test validación de rango de fechas válido."""
        resultado = self.app_service.validate_date_range(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin
        )
        
        self.assertTrue(resultado['es_valido'])
        self.assertEqual(len(resultado['errores']), 0)
    
    def test_validate_date_range_invalido(self):
        """Test validación de rango de fechas inválido."""
        fecha_inicio_posterior = datetime(2024, 12, 31)
        fecha_fin_anterior = datetime(2024, 1, 1)
        
        resultado = self.app_service.validate_date_range(
            fecha_inicio=fecha_inicio_posterior,
            fecha_fin=fecha_fin_anterior
        )
        
        self.assertFalse(resultado['es_valido'])
        self.assertGreater(len(resultado['errores']), 0)
        self.assertIn('posterior', resultado['errores'][0])
    
    def test_validate_date_range_muy_amplio(self):
        """Test validación de rango muy amplio."""
        fecha_inicio_muy_antigua = datetime(2020, 1, 1)
        fecha_fin_actual = datetime.now()
        
        resultado = self.app_service.validate_date_range(
            fecha_inicio=fecha_inicio_muy_antigua,
            fecha_fin=fecha_fin_actual
        )
        
        # Debería incluir advertencia sobre período muy amplio
        self.assertTrue(resultado['es_valido'])  # Válido pero con advertencia
        self.assertIn('advertencias', resultado)
    
    def test_calculate_and_export_flujo_completo(self):
        """Test del flujo completo: calcular y exportar."""
        # Configurar todos los mocks para flujo exitoso
        mock_facturas_df = pd.DataFrame([
            {'total': 1000000.0, 'cliente_nit': '123456789', 'cliente_nombre': 'Cliente Test'}
        ])
        
        self.mock_siigo_adapter.obtener_facturas_periodo.return_value = mock_facturas_df
        self.mock_validation_service.validar_datos_facturas.return_value = {'es_valido': True, 'errores': []}
        self.mock_domain_service.calcular_kpis_ventas.return_value = self.mock_kpis
        self.mock_export_service.exportar_kpis_excel.return_value = {
            'success': True,
            'file_path': 'c:\\temp\\kpis.xlsx',
            'error': None
        }
        
        # Ejecutar flujo completo
        resultado = self.app_service.calculate_and_export_kpis(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin,
            export_path="c:\\temp\\"
        )
        
        # Verificar que se orquestaron todas las operaciones
        self.mock_siigo_adapter.obtener_facturas_periodo.assert_called_once()
        self.mock_validation_service.validar_datos_facturas.assert_called_once()
        self.mock_domain_service.calcular_kpis_ventas.assert_called_once()
        self.mock_export_service.exportar_kpis_excel.assert_called_once()
        
        # Verificar resultado exitoso
        self.assertTrue(resultado['success'])
        self.assertIn('file_path', resultado)
        self.assertIsNone(resultado['error'])
    
    def test_sin_dependencias_inyectadas(self):
        """Test comportamiento con dependencias faltantes."""
        # Crear servicio sin todas las dependencias
        service_incompleto = KPIApplicationService(
            kpi_calculation_service=self.mock_domain_service
            # Faltan otras dependencias
        )
        
        # Debería poder funcionar con operaciones básicas
        resultado = service_incompleto.get_kpis_summary(self.mock_kpis)
        self.assertIn('ventas_totales', resultado)
        
        # Pero fallar en operaciones que requieren dependencias faltantes
        with self.assertRaises(AttributeError):
            service_incompleto.calculate_kpis_for_period(
                fecha_inicio=self.fecha_inicio,
                fecha_fin=self.fecha_fin
            )


if __name__ == '__main__':
    unittest.main()