"""
Test para entidades de KPIs - Domain Layer
Tests unitarios para validar la lógica de negocio de los KPIs
"""

import unittest
from datetime import datetime
from decimal import Decimal

from src.domain.entities.kpis import VentaPorCliente, KPIsVentas, KPIsFinancieros


class TestVentaPorCliente(unittest.TestCase):
    """Tests para la entidad VentaPorCliente."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.venta_cliente = VentaPorCliente(
            nit="123456789",
            nombre="Cliente Prueba S.A.S",
            total_ventas=Decimal("1500000.00"),
            numero_facturas=5,
            ticket_promedio=Decimal("300000.00")
        )
    
    def test_creacion_venta_cliente(self):
        """Test crear VentaPorCliente válida."""
        self.assertEqual(self.venta_cliente.nit, "123456789")
        self.assertEqual(self.venta_cliente.nombre, "Cliente Prueba S.A.S")
        self.assertEqual(self.venta_cliente.total_ventas, Decimal("1500000.00"))
        self.assertEqual(self.venta_cliente.numero_facturas, 5)
        self.assertEqual(self.venta_cliente.ticket_promedio, Decimal("300000.00"))
    
    def test_nombre_display_con_nombre(self):
        """Test nombre_display cuando hay nombre válido."""
        self.assertEqual(self.venta_cliente.nombre_display, "Cliente Prueba S.A.S")
    
    def test_nombre_display_sin_nombre(self):
        """Test nombre_display cuando no hay nombre o es genérico."""
        venta_sin_nombre = VentaPorCliente(
            nit="987654321",
            nombre="Cliente Sin Nombre",
            total_ventas=Decimal("500000.00"),
            numero_facturas=2,
            ticket_promedio=Decimal("250000.00")
        )
        
        self.assertEqual(venta_sin_nombre.nombre_display, "Cliente NIT: 987654321")
    
    def test_conversion_tipos(self):
        """Test conversión automática de tipos a Decimal."""
        venta_float = VentaPorCliente(
            nit="555555555",
            nombre="Cliente Float",
            total_ventas=1000000.0,  # float
            numero_facturas=3,
            ticket_promedio=333333.33  # float
        )
        
        self.assertIsInstance(venta_float.total_ventas, Decimal)
        self.assertIsInstance(venta_float.ticket_promedio, Decimal)


class TestKPIsVentas(unittest.TestCase):
    """Tests para la entidad KPIsVentas."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.fecha_inicio = datetime(2024, 1, 1)
        self.fecha_fin = datetime(2024, 12, 31)
        self.fecha_calculo = datetime(2024, 6, 15, 14, 30, 0)
        
        self.ventas_cliente = [
            VentaPorCliente(
                nit="123456789",
                nombre="Cliente A",
                total_ventas=Decimal("2000000.00"),
                numero_facturas=8,
                ticket_promedio=Decimal("250000.00")
            ),
            VentaPorCliente(
                nit="987654321", 
                nombre="Cliente B",
                total_ventas=Decimal("1500000.00"),
                numero_facturas=5,
                ticket_promedio=Decimal("300000.00")
            ),
        ]
        
        self.kpis_ventas = KPIsVentas(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin,
            ventas_totales=Decimal("3500000.00"),
            numero_facturas=13,
            ticket_promedio=Decimal("269230.77"),
            ventas_por_cliente=self.ventas_cliente,
            fecha_calculo=self.fecha_calculo,
            estado_sistema="ACTIVO ✅"
        )
    
    def test_creacion_kpis_ventas(self):
        """Test crear KPIsVentas válidos."""
        self.assertEqual(self.kpis_ventas.ventas_totales, Decimal("3500000.00"))
        self.assertEqual(self.kpis_ventas.numero_facturas, 13)
        self.assertEqual(len(self.kpis_ventas.ventas_por_cliente), 2)
        self.assertEqual(self.kpis_ventas.estado_sistema, "ACTIVO ✅")
    
    def test_cliente_top(self):
        """Test identificación del cliente con mayores ventas."""
        cliente_top = self.kpis_ventas.cliente_top
        
        self.assertIsNotNone(cliente_top)
        self.assertEqual(cliente_top.nit, "123456789")
        self.assertEqual(cliente_top.nombre, "Cliente A")
        self.assertEqual(cliente_top.total_ventas, Decimal("2000000.00"))
    
    def test_numero_clientes_activos(self):
        """Test conteo de clientes activos."""
        self.assertEqual(self.kpis_ventas.numero_clientes_activos, 2)
    
    def test_concentracion_cliente_top(self):
        """Test cálculo de concentración del cliente principal."""
        concentracion = self.kpis_ventas.calcular_concentracion_cliente_top()
        
        # Cliente top: 2,000,000 / Total: 3,500,000 = 57.14%
        self.assertIsNotNone(concentracion)
        self.assertAlmostEqual(float(concentracion), 57.14, places=2)
    
    def test_top_clientes_limitados(self):
        """Test obtener top N clientes."""
        top_3 = self.kpis_ventas.obtener_top_clientes(3)
        
        # Solo tenemos 2 clientes, debería devolver 2
        self.assertEqual(len(top_3), 2)
        
        # Verificar orden (descendente por ventas)
        self.assertEqual(top_3[0].total_ventas, Decimal("2000000.00"))
        self.assertEqual(top_3[1].total_ventas, Decimal("1500000.00"))
    
    def test_estadisticas_avanzadas(self):
        """Test cálculo de estadísticas avanzadas."""
        stats = self.kpis_ventas.calcular_estadisticas_avanzadas()
        
        self.assertEqual(stats['clientes_activos'], 2)
        self.assertAlmostEqual(stats['concentracion_top'], 57.14, places=2)
        self.assertEqual(stats['venta_minima'], 1500000.0)
        self.assertEqual(stats['venta_maxima'], 2000000.0)
        self.assertEqual(stats['distribucion_ventas'], 'muy_concentrada')  # Corregir expectativa
    
    def test_validacion_consistencia(self):
        """Test validación de consistencia de datos."""
        # KPIs válidos
        self.assertTrue(self.kpis_ventas.es_valido())
        
        # Test de KPIs con inconsistencia - debe lanzar error en construcción
        with self.assertRaises(ValueError) as context:
            KPIsVentas(
                fecha_inicio=self.fecha_inicio,
                fecha_fin=self.fecha_fin,
                ventas_totales=Decimal("9999999.99"),  # No coincide con suma de clientes
                numero_facturas=13,
                ticket_promedio=Decimal("269230.77"),
                ventas_por_cliente=self.ventas_cliente,
                fecha_calculo=self.fecha_calculo,
                estado_sistema="ACTIVO ✅"
            )
        
        # Verificar que el error contiene el mensaje esperado
        self.assertIn("Inconsistencia en ventas", str(context.exception))
    
    def test_to_dict(self):
        """Test conversión a diccionario."""
        dict_result = self.kpis_ventas.to_dict()
        
        # Verificar campos principales
        self.assertEqual(dict_result['ventas_totales'], 3500000.0)
        self.assertEqual(dict_result['numero_facturas'], 13)
        self.assertEqual(len(dict_result['ventas_por_cliente']), 2)
        
        # Verificar cliente top
        self.assertIsNotNone(dict_result['cliente_top'])
        self.assertEqual(dict_result['cliente_top']['nombre'], 'Cliente A')
        
        # Verificar estadísticas avanzadas
        self.assertIn('estadisticas_avanzadas', dict_result)


class TestKPIsFinancieros(unittest.TestCase):
    """Tests para la entidad KPIsFinancieros."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        fecha_inicio = datetime(2024, 1, 1)
        fecha_fin = datetime(2024, 12, 31)
        
        ventas_cliente = [
            VentaPorCliente(
                nit="123456789",
                nombre="Cliente Test",
                total_ventas=Decimal("1000000.00"),
                numero_facturas=4,
                ticket_promedio=Decimal("250000.00")
            )
        ]
        
        self.kpis_ventas = KPIsVentas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ventas_totales=Decimal("1000000.00"),
            numero_facturas=4,
            ticket_promedio=Decimal("250000.00"),
            ventas_por_cliente=ventas_cliente,
            fecha_calculo=datetime.now(),
            estado_sistema="ACTIVO ✅"
        )
        
        self.kpis_financieros = KPIsFinancieros(
            kpis_ventas=self.kpis_ventas,
            costos_totales=Decimal("600000.00"),
            gastos_operacionales=Decimal("200000.00")
        )
    
    def test_creacion_kpis_financieros(self):
        """Test crear KPIsFinancieros válidos."""
        self.assertEqual(self.kpis_financieros.costos_totales, Decimal("600000.00"))
        self.assertEqual(self.kpis_financieros.gastos_operacionales, Decimal("200000.00"))
        self.assertIsNone(self.kpis_financieros.margen_bruto)  # Sin calcular aún
    
    def test_calculo_margenes(self):
        """Test cálculo de márgenes financieros."""
        self.kpis_financieros.calcular_margenes()
        
        # Margen bruto = (Ventas - Costos) / Ventas * 100
        # (1,000,000 - 600,000) / 1,000,000 * 100 = 40%
        self.assertIsNotNone(self.kpis_financieros.margen_bruto)
        self.assertEqual(self.kpis_financieros.margen_bruto, Decimal("40.00"))
        
        # Margen operacional = (Ventas - Costos - Gastos) / Ventas * 100  
        # (1,000,000 - 600,000 - 200,000) / 1,000,000 * 100 = 20%
        self.assertIsNotNone(self.kpis_financieros.margen_operacional)
        self.assertEqual(self.kpis_financieros.margen_operacional, Decimal("20.00"))


if __name__ == '__main__':
    unittest.main()