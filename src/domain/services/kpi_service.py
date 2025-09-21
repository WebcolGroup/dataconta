"""
Servicio de Dominio para Cálculo de KPIs
Contiene la lógica de negocio para procesar datos de ventas y calcular indicadores

Responsabilidad única: Calcular KPIs empresariales siguiendo reglas de negocio específicas
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
import pandas as pd

from src.domain.entities.kpis import KPIsVentas, VentaPorCliente, KPIsFinancieros


class KPICalculationService(ABC):
    """
    Servicio de dominio abstracto para cálculo de KPIs.
    Define los contratos para el cálculo de indicadores de negocio.
    """
    
    @abstractmethod
    def calcular_kpis_ventas(self, 
                           facturas_df: pd.DataFrame,
                           fecha_inicio: datetime,
                           fecha_fin: datetime) -> KPIsVentas:
        """
        Calcular KPIs de ventas basados en DataFrame de facturas.
        
        Args:
            facturas_df: DataFrame con datos de facturas
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            
        Returns:
            KPIsVentas calculados
        """
        pass
    
    @abstractmethod
    def consolidar_ventas_por_cliente(self, facturas_df: pd.DataFrame) -> List[VentaPorCliente]:
        """
        Consolidar ventas agrupadas por cliente.
        
        Args:
            facturas_df: DataFrame con datos de facturas
            
        Returns:
            Lista de VentaPorCliente ordenada por ventas descendente
        """
        pass


class KPICalculationServiceImpl(KPICalculationService):
    """
    Implementación concreta del servicio de cálculo de KPIs.
    Contiene toda la lógica de negocio para el cálculo de indicadores.
    """
    
    def calcular_kpis_ventas(self, 
                           facturas_df: pd.DataFrame,
                           fecha_inicio: datetime,
                           fecha_fin: datetime) -> KPIsVentas:
        """Calcular KPIs de ventas basados en DataFrame de facturas."""
        
        # Validar entrada
        if facturas_df is None or len(facturas_df) == 0:
            return self._crear_kpis_vacios(fecha_inicio, fecha_fin)
        
        # Validar columnas requeridas
        columnas_requeridas = {'total', 'cliente_nit', 'cliente_nombre'}
        if not columnas_requeridas.issubset(facturas_df.columns):
            raise ValueError(f"DataFrame debe contener columnas: {columnas_requeridas}")
        
        # Cálculos principales
        ventas_totales = self._calcular_ventas_totales(facturas_df)
        numero_facturas = len(facturas_df)
        ticket_promedio = self._calcular_ticket_promedio(ventas_totales, numero_facturas)
        
        # Consolidación por cliente
        ventas_por_cliente = self.consolidar_ventas_por_cliente(facturas_df)
        
        # Crear entidad de dominio
        return KPIsVentas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ventas_totales=ventas_totales,
            numero_facturas=numero_facturas,
            ticket_promedio=ticket_promedio,
            ventas_por_cliente=ventas_por_cliente,
            fecha_calculo=datetime.now(),
            estado_sistema='ACTIVO ✅' if numero_facturas > 0 else 'SIN DATOS ⚠️'
        )
    
    def consolidar_ventas_por_cliente(self, facturas_df: pd.DataFrame) -> List[VentaPorCliente]:
        """Consolidar ventas agrupadas por cliente."""
        
        # Agrupar por NIT de cliente y consolidar
        consolidacion = facturas_df.groupby('cliente_nit').agg({
            'total': 'sum',
            'cliente_nombre': 'first'  # Tomar el primer nombre encontrado
        }).reset_index()
        
        # Contar facturas por cliente
        facturas_por_cliente = facturas_df.groupby('cliente_nit').size().reset_index(name='numero_facturas')
        
        # Hacer merge para combinar información
        consolidacion = consolidacion.merge(facturas_por_cliente, on='cliente_nit')
        
        # Renombrar columnas para claridad
        consolidacion.columns = ['nit', 'total_ventas', 'nombre', 'numero_facturas']
        
        # Calcular ticket promedio por cliente
        consolidacion['ticket_promedio'] = (
            consolidacion['total_ventas'] / consolidacion['numero_facturas']
        ).round(2)
        
        # Crear objetos VentaPorCliente
        ventas_por_cliente = []
        for _, row in consolidacion.iterrows():
            venta_cliente = VentaPorCliente(
                nit=str(row['nit']),
                nombre=str(row['nombre']),
                total_ventas=Decimal(str(row['total_ventas'])),
                numero_facturas=int(row['numero_facturas']),
                ticket_promedio=Decimal(str(row['ticket_promedio']))
            )
            ventas_por_cliente.append(venta_cliente)
        
        # Ordenar por ventas totales descendente
        ventas_por_cliente.sort(key=lambda x: x.total_ventas, reverse=True)
        
        return ventas_por_cliente
    
    def calcular_kpis_financieros(self, 
                                kpis_ventas: KPIsVentas,
                                costos_df: Optional[pd.DataFrame] = None,
                                gastos_df: Optional[pd.DataFrame] = None) -> KPIsFinancieros:
        """
        Calcular KPIs financieros extendidos cuando se tienen datos de costos.
        
        Args:
            kpis_ventas: KPIs de ventas ya calculados
            costos_df: DataFrame opcional con costos
            gastos_df: DataFrame opcional con gastos
            
        Returns:
            KPIsFinancieros con márgenes calculados
        """
        costos_totales = None
        gastos_operacionales = None
        
        if costos_df is not None and 'monto' in costos_df.columns:
            costos_totales = Decimal(str(costos_df['monto'].sum()))
        
        if gastos_df is not None and 'monto' in gastos_df.columns:
            gastos_operacionales = Decimal(str(gastos_df['monto'].sum()))
        
        kpis_financieros = KPIsFinancieros(
            kpis_ventas=kpis_ventas,
            costos_totales=costos_totales,
            gastos_operacionales=gastos_operacionales
        )
        
        # Calcular márgenes
        kpis_financieros.calcular_margenes()
        
        return kpis_financieros
    
    def _calcular_ventas_totales(self, facturas_df: pd.DataFrame) -> Decimal:
        """Calcular ventas totales del período."""
        ventas_totales = facturas_df['total'].sum()
        return Decimal(str(ventas_totales))
    
    def _calcular_ticket_promedio(self, ventas_totales: Decimal, numero_facturas: int) -> Decimal:
        """Calcular ticket promedio."""
        if numero_facturas == 0:
            return Decimal('0.00')
        
        ticket = ventas_totales / Decimal(str(numero_facturas))
        return ticket.quantize(Decimal('0.01'))
    
    def _crear_kpis_vacios(self, fecha_inicio: datetime, fecha_fin: datetime) -> KPIsVentas:
        """Crear KPIs vacíos cuando no hay datos."""
        return KPIsVentas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ventas_totales=Decimal('0.00'),
            numero_facturas=0,
            ticket_promedio=Decimal('0.00'),
            ventas_por_cliente=[],
            fecha_calculo=datetime.now(),
            estado_sistema='SIN DATOS ⚠️'
        )
    
    def validar_consistencia_datos(self, facturas_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validar la consistencia y calidad de los datos de entrada.
        
        Args:
            facturas_df: DataFrame a validar
            
        Returns:
            Diccionario con resultados de validación
        """
        validacion = {
            'es_valido': True,
            'errores': [],
            'advertencias': [],
            'estadisticas': {}
        }
        
        if facturas_df is None or len(facturas_df) == 0:
            validacion['errores'].append('DataFrame vacío o nulo')
            validacion['es_valido'] = False
            return validacion
        
        # Validar columnas requeridas
        columnas_requeridas = {'total', 'cliente_nit', 'cliente_nombre'}
        columnas_faltantes = columnas_requeridas - set(facturas_df.columns)
        if columnas_faltantes:
            validacion['errores'].append(f'Columnas faltantes: {columnas_faltantes}')
            validacion['es_valido'] = False
        
        # Solo hacer validaciones adicionales si las columnas básicas existen
        if validacion['es_valido']:
            # Validar datos de totales
            if 'total' in facturas_df.columns:
                totales_negativos = (facturas_df['total'] < 0).sum()
                if totales_negativos > 0:
                    validacion['advertencias'].append(f'{totales_negativos} facturas con total negativo')
            
            # Validar NITs
            if 'cliente_nit' in facturas_df.columns:
                nits_vacios = facturas_df['cliente_nit'].isna().sum()
                if nits_vacios > 0:
                    validacion['advertencias'].append(f'{nits_vacios} facturas sin NIT de cliente')
            
            # Estadísticas básicas
            validacion['estadisticas'] = {
                'total_facturas': len(facturas_df),
                'rango_fechas': {
                    'min': facturas_df.index.min() if hasattr(facturas_df.index, 'min') else 'N/A',
                    'max': facturas_df.index.max() if hasattr(facturas_df.index, 'max') else 'N/A'
                },
                'total_ventas': float(facturas_df['total'].sum()) if 'total' in facturas_df.columns else 0,
                'clientes_unicos': facturas_df['cliente_nit'].nunique() if 'cliente_nit' in facturas_df.columns else 0
            }
        
        return validacion


class KPIAnalysisService:
    """
    Servicio para análisis avanzado de KPIs.
    Proporciona insights y recomendaciones basadas en los indicadores.
    """
    
    def __init__(self, kpi_service: KPICalculationService):
        self.kpi_service = kpi_service
    
    def generar_insights(self, kpis: KPIsVentas) -> Dict[str, Any]:
        """
        Generar insights y recomendaciones basadas en los KPIs.
        
        Args:
            kpis: KPIs calculados
            
        Returns:
            Diccionario con insights y recomendaciones
        """
        insights = {
            'resumen_ejecutivo': self._generar_resumen_ejecutivo(kpis),
            'analisis_clientes': self._analizar_concentracion_clientes(kpis),
            'oportunidades': self._identificar_oportunidades(kpis),
            'alertas': self._identificar_alertas(kpis),
            'recomendaciones': self._generar_recomendaciones(kpis)
        }
        
        return insights
    
    def _generar_resumen_ejecutivo(self, kpis: KPIsVentas) -> Dict[str, str]:
        """Generar resumen ejecutivo de los KPIs."""
        return {
            'periodo': f"{kpis.fecha_inicio.strftime('%d/%m/%Y')} - {kpis.fecha_fin.strftime('%d/%m/%Y')}",
            'performance': 'Excelente' if kpis.numero_facturas > 100 else 'Regular' if kpis.numero_facturas > 50 else 'Bajo',
            'diversificacion': kpis._clasificar_distribucion(),
            'estado_general': kpis.estado_sistema
        }
    
    def _analizar_concentracion_clientes(self, kpis: KPIsVentas) -> Dict[str, Any]:
        """Analizar concentración de ventas por cliente."""
        concentracion = kpis.calcular_concentracion_cliente_top()
        
        return {
            'concentracion_top': float(concentracion) if concentracion else 0,
            'nivel_riesgo': self._evaluar_riesgo_concentracion(concentracion),
            'cliente_principal': kpis.cliente_top.nombre_display if kpis.cliente_top else 'N/A',
            'diversificacion': len(kpis.ventas_por_cliente)
        }
    
    def _identificar_oportunidades(self, kpis: KPIsVentas) -> List[str]:
        """Identificar oportunidades de mejora."""
        oportunidades = []
        
        if kpis.numero_clientes_activos < 20:
            oportunidades.append("Expandir base de clientes")
        
        concentracion = kpis.calcular_concentracion_cliente_top()
        if concentracion and concentracion > 40:
            oportunidades.append("Diversificar cartera de clientes")
        
        if kpis.ticket_promedio < 50000:  # Umbral configurable
            oportunidades.append("Incrementar ticket promedio")
        
        return oportunidades
    
    def _identificar_alertas(self, kpis: KPIsVentas) -> List[str]:
        """Identificar alertas de riesgo."""
        alertas = []
        
        if kpis.numero_facturas == 0:
            alertas.append("Sin actividad comercial en el período")
        
        concentracion = kpis.calcular_concentracion_cliente_top()
        if concentracion and concentracion > 60:
            alertas.append("Alta concentración de riesgo en cliente principal")
        
        return alertas
    
    def _generar_recomendaciones(self, kpis: KPIsVentas) -> List[str]:
        """Generar recomendaciones estratégicas."""
        recomendaciones = []
        
        # Análisis de concentración
        concentracion = kpis.calcular_concentracion_cliente_top()
        if concentracion and concentracion > 50:
            recomendaciones.append("Implementar estrategia de diversificación de clientes")
        
        # Análisis de ticket promedio
        if kpis.numero_clientes_activos > 0:
            tickets = [v.ticket_promedio for v in kpis.ventas_por_cliente]
            ticket_mediano = sorted(tickets)[len(tickets)//2]
            
            if kpis.ticket_promedio < ticket_mediano * Decimal('0.8'):
                recomendaciones.append("Enfocar esfuerzos en aumentar ticket promedio")
        
        # Análisis de actividad
        if kpis.numero_facturas < 10:
            recomendaciones.append("Incrementar frecuencia de ventas")
        
        return recomendaciones
    
    def _evaluar_riesgo_concentracion(self, concentracion: Optional[Decimal]) -> str:
        """Evaluar nivel de riesgo por concentración."""
        if concentracion is None:
            return 'sin_datos'
        
        if concentracion >= 70:
            return 'muy_alto'
        elif concentracion >= 50:
            return 'alto'
        elif concentracion >= 30:
            return 'medio'
        else:
            return 'bajo'