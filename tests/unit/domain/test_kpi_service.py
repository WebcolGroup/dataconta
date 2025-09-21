"""
Test para servicios de KPIs - Domain Layer
Tests unitarios para validar la lógica de cálculo de KPIs
"""

import unittest
import pandas as pd
from datetime import datetime
from decimal import Decimal

from src.domain.services.kpi_service import KPICalculationServiceImpl, KPIAnalysisService
from src.domain.entities.kpis import KPIsVentas


class TestKPICalculationService(unittest.TestCase):
    """Tests para el servicio de cálculo de KPIs."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.service = KPICalculationServiceImpl()
        self.fecha_inicio = datetime(2024, 1, 1)
        self.fecha_fin = datetime(2024, 12, 31)
        
        # DataFrame de prueba
        self.facturas_data = pd.DataFrame([
            {
                'total': 500000.0,
                'cliente_nit': '123456789',
                'cliente_nombre': 'Cliente A S.A.S'
            },
            {
                'total': 300000.0,
                'cliente_nit': '987654321',
                'cliente_nombre': 'Cliente B Ltda'
            },
            {
                'total': 700000.0,
                'cliente_nit': '123456789',
                'cliente_nombre': 'Cliente A S.A.S'
            }
        ])
    
    def test_calcular_kpis_ventas_exitoso(self):
        """Test cálculo exitoso de KPIs desde DataFrame."""
        kpis = self.service.calcular_kpis_ventas(
            self.facturas_data, 
            self.fecha_inicio, 
            self.fecha_fin
        )
        
        # Verificar cálculos básicos
        self.assertEqual(kpis.ventas_totales, Decimal("1500000.00"))
        self.assertEqual(kpis.numero_facturas, 3)
        self.assertEqual(kpis.ticket_promedio, Decimal("500000.00"))
        
        # Verificar consolidación por cliente
        self.assertEqual(len(kpis.ventas_por_cliente), 2)
        
        # Cliente top debería ser 123456789 con 1,200,000
        cliente_top = kpis.cliente_top
        self.assertEqual(cliente_top.nit, '123456789')
        self.assertEqual(cliente_top.total_ventas, Decimal("1200000.00"))
        self.assertEqual(cliente_top.numero_facturas, 2)
    
    def test_calcular_kpis_dataframe_vacio(self):
        """Test manejo de DataFrame vacío."""
        df_vacio = pd.DataFrame()
        
        kpis = self.service.calcular_kpis_ventas(
            df_vacio,
            self.fecha_inicio,
            self.fecha_fin
        )
        
        # Verificar KPIs vacíos
        self.assertEqual(kpis.ventas_totales, Decimal("0.00"))
        self.assertEqual(kpis.numero_facturas, 0)
        self.assertEqual(len(kpis.ventas_por_cliente), 0)
        self.assertEqual(kpis.estado_sistema, 'SIN DATOS ⚠️')
    
    def test_consolidar_ventas_por_cliente(self):
        """Test consolidación de ventas por cliente."""
        ventas_consolidadas = self.service.consolidar_ventas_por_cliente(self.facturas_data)
        
        # Verificar que se consolidaron correctamente
        self.assertEqual(len(ventas_consolidadas), 2)
        
        # Verificar cliente con mayores ventas (123456789)
        cliente_top = ventas_consolidadas[0]
        self.assertEqual(cliente_top.nit, '123456789')
        self.assertEqual(cliente_top.total_ventas, Decimal("1200000.00"))  # 500,000 + 700,000
        self.assertEqual(cliente_top.numero_facturas, 2)
        self.assertEqual(cliente_top.ticket_promedio, Decimal("600000.00"))  # 1,200,000 / 2
    
    def test_validar_consistencia_datos(self):
        """Test validación de consistencia de datos."""
        # Datos válidos
        validacion = self.service.validar_consistencia_datos(self.facturas_data)
        
        self.assertTrue(validacion['es_valido'])
        self.assertEqual(len(validacion['errores']), 0)
        self.assertEqual(validacion['estadisticas']['total_facturas'], 3)
        self.assertEqual(validacion['estadisticas']['total_ventas'], 1500000.0)
        self.assertEqual(validacion['estadisticas']['clientes_unicos'], 2)
    
    def test_validar_datos_con_errores(self):
        """Test validación de datos con errores."""
        # DataFrame sin columnas requeridas
        df_invalido = pd.DataFrame([{'precio': 100}])
        
        validacion = self.service.validar_consistencia_datos(df_invalido)
        
        self.assertFalse(validacion['es_valido'])
        self.assertGreater(len(validacion['errores']), 0)
    
    def test_columnas_requeridas_faltantes(self):
        """Test error cuando faltan columnas requeridas."""
        df_sin_columnas = pd.DataFrame([
            {'precio': 500000.0},  # Falta 'total', 'cliente_nit', etc.
        ])
        
        with self.assertRaises(ValueError) as context:
            self.service.calcular_kpis_ventas(
                df_sin_columnas,
                self.fecha_inicio,
                self.fecha_fin
            )
        
        self.assertIn("DataFrame debe contener columnas", str(context.exception))


class TestKPIAnalysisService(unittest.TestCase):
    """Tests para el servicio de análisis de KPIs."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        calculation_service = KPICalculationServiceImpl()
        self.analysis_service = KPIAnalysisService(calculation_service)
        
        # KPIs de prueba
        from src.domain.entities.kpis import VentaPorCliente
        
        ventas_cliente = [
            VentaPorCliente(
                nit="123456789",
                nombre="Cliente Dominante",
                total_ventas=Decimal("8000000.00"),  # 80% del total
                numero_facturas=10,
                ticket_promedio=Decimal("800000.00")
            ),
            VentaPorCliente(
                nit="987654321",
                nombre="Cliente Menor",
                total_ventas=Decimal("2000000.00"),  # 20% del total
                numero_facturas=5,
                ticket_promedio=Decimal("400000.00")
            )
        ]
        
        self.kpis_concentrados = KPIsVentas(
            fecha_inicio=datetime(2024, 1, 1),
            fecha_fin=datetime(2024, 12, 31),
            ventas_totales=Decimal("10000000.00"),
            numero_facturas=15,
            ticket_promedio=Decimal("666666.67"),
            ventas_por_cliente=ventas_cliente,
            fecha_calculo=datetime.now(),
            estado_sistema="ACTIVO ✅"
        )
    
    def test_generar_insights(self):
        """Test generación de insights completos."""
        insights = self.analysis_service.generar_insights(self.kpis_concentrados)
        
        # Verificar estructura de insights
        self.assertIn('resumen_ejecutivo', insights)
        self.assertIn('analisis_clientes', insights)
        self.assertIn('oportunidades', insights)
        self.assertIn('alertas', insights)
        self.assertIn('recomendaciones', insights)
        
        # Verificar análisis de concentración
        analisis_clientes = insights['analisis_clientes']
        self.assertEqual(analisis_clientes['concentracion_top'], 80.0)
        self.assertEqual(analisis_clientes['nivel_riesgo'], 'muy_alto')
        self.assertEqual(analisis_clientes['cliente_principal'], 'Cliente Dominante')
    
    def test_identificar_alertas(self):
        """Test identificación de alertas de riesgo."""
        alertas = self.analysis_service._identificar_alertas(self.kpis_concentrados)
        
        # Con 80% de concentración debería generar alerta
        self.assertIn('Alta concentración de riesgo en cliente principal', alertas)
    
    def test_generar_recomendaciones(self):
        """Test generación de recomendaciones."""
        recomendaciones = self.analysis_service._generar_recomendaciones(self.kpis_concentrados)
        
        # Con alta concentración debería recomendar diversificación
        self.assertGreater(len(recomendaciones), 0)
        encontro_diversificacion = any(
            'diversificación' in rec.lower() for rec in recomendaciones
        )
        self.assertTrue(encontro_diversificacion)
    
    def test_evaluar_riesgo_concentracion(self):
        """Test evaluación de niveles de riesgo."""
        # Riesgo muy alto (70%+)
        riesgo_muy_alto = self.analysis_service._evaluar_riesgo_concentracion(Decimal('80'))
        self.assertEqual(riesgo_muy_alto, 'muy_alto')
        
        # Riesgo alto (50-69%)
        riesgo_alto = self.analysis_service._evaluar_riesgo_concentracion(Decimal('60'))
        self.assertEqual(riesgo_alto, 'alto')
        
        # Riesgo medio (30-49%)
        riesgo_medio = self.analysis_service._evaluar_riesgo_concentracion(Decimal('40'))
        self.assertEqual(riesgo_medio, 'medio')
        
        # Riesgo bajo (<30%)
        riesgo_bajo = self.analysis_service._evaluar_riesgo_concentracion(Decimal('20'))
        self.assertEqual(riesgo_bajo, 'bajo')


if __name__ == '__main__':
    unittest.main()