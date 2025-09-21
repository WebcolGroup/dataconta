"""
KPIs - Entidades de Dominio
Representan los Key Performance Indicators (Indicadores Clave de Rendimiento) del negocio

Responsabilidad única: Modelar KPIs empresariales con reglas de negocio específicas
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class VentaPorCliente:
    """Representa las ventas agregadas por cliente."""
    nit: str
    nombre: str
    total_ventas: Decimal
    numero_facturas: int
    ticket_promedio: Decimal
    
    def __post_init__(self):
        """Validar y calcular valores derivados."""
        if not isinstance(self.total_ventas, Decimal):
            self.total_ventas = Decimal(str(self.total_ventas))
        
        if not isinstance(self.ticket_promedio, Decimal):
            self.ticket_promedio = Decimal(str(self.ticket_promedio))
    
    @property
    def nombre_display(self) -> str:
        """Nombre para mostrar, con fallback al NIT si no hay nombre."""
        if self.nombre and self.nombre != 'Cliente Sin Nombre':
            return self.nombre
        return f"Cliente NIT: {self.nit}"


@dataclass
class KPIsVentas:
    """
    Entidad de dominio para los KPIs de ventas.
    
    Principios SOLID aplicados:
    - SRP: Solo maneja KPIs de ventas y sus cálculos
    - OCP: Extensible para nuevos tipos de KPIs
    - LSP: Puede ser sustituido por especializaciones
    - ISP: Interface específica para KPIs de ventas
    - DIP: No depende de implementaciones concretas
    """
    
    # Período del análisis
    fecha_inicio: datetime
    fecha_fin: datetime
    
    # KPIs principales
    ventas_totales: Decimal
    numero_facturas: int
    ticket_promedio: Decimal
    
    # Análisis por cliente
    ventas_por_cliente: List[VentaPorCliente]
    
    # Metadatos
    fecha_calculo: datetime
    estado_sistema: str
    
    def __post_init__(self):
        """Validar y calcular valores derivados."""
        # Convertir a Decimal si es necesario
        if not isinstance(self.ventas_totales, Decimal):
            self.ventas_totales = Decimal(str(self.ventas_totales))
        
        if not isinstance(self.ticket_promedio, Decimal):
            self.ticket_promedio = Decimal(str(self.ticket_promedio))
        
        # Validar consistencia de datos
        self._validar_consistencia()
        
        # Calcular ticket promedio si no está establecido
        if self.ticket_promedio == 0 and self.numero_facturas > 0:
            self.ticket_promedio = self.ventas_totales / Decimal(str(self.numero_facturas))
            self.ticket_promedio = self.ticket_promedio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _validar_consistencia(self) -> None:
        """Validar consistencia interna de los KPIs."""
        if self.ventas_totales < 0:
            raise ValueError("Las ventas totales no pueden ser negativas")
        
        if self.numero_facturas < 0:
            raise ValueError("El número de facturas no puede ser negativo")
        
        if self.fecha_inicio > self.fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")
        
        # Validar consistencia con ventas por cliente
        total_por_clientes = sum(venta.total_ventas for venta in self.ventas_por_cliente)
        diferencia = abs(self.ventas_totales - total_por_clientes)
        
        # Permitir diferencias menores por redondeos
        if diferencia > Decimal('0.01'):
            raise ValueError(f"Inconsistencia en ventas: total={self.ventas_totales}, suma_clientes={total_por_clientes}")
    
    @property
    def cliente_top(self) -> Optional[VentaPorCliente]:
        """Cliente con mayores ventas en el período."""
        if not self.ventas_por_cliente:
            return None
        return max(self.ventas_por_cliente, key=lambda x: x.total_ventas)
    
    @property
    def numero_clientes_activos(self) -> int:
        """Número de clientes que realizaron compras en el período."""
        return len(self.ventas_por_cliente)
    
    def calcular_concentracion_cliente_top(self) -> Optional[Decimal]:
        """Calcular % de concentración del cliente principal."""
        if not self.cliente_top or self.ventas_totales == 0:
            return None
        
        concentracion = (self.cliente_top.total_ventas / self.ventas_totales) * 100
        return concentracion.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def obtener_top_clientes(self, limite: int = 10) -> List[VentaPorCliente]:
        """Obtener los N clientes con mayores ventas."""
        return sorted(
            self.ventas_por_cliente, 
            key=lambda x: x.total_ventas, 
            reverse=True
        )[:limite]
    
    def calcular_estadisticas_avanzadas(self) -> Dict[str, Any]:
        """Calcular estadísticas avanzadas de los KPIs."""
        if not self.ventas_por_cliente:
            return {
                'clientes_activos': 0,
                'concentracion_top': None,
                'ticket_promedio_mercado': None,
                'distribucion_ventas': 'sin_datos'
            }
        
        # Estadísticas básicas
        ventas_lista = [float(v.total_ventas) for v in self.ventas_por_cliente]
        
        # Ticket promedio del mercado (promedio de todos los tickets promedio por cliente)
        tickets_promedio = [float(v.ticket_promedio) for v in self.ventas_por_cliente if v.ticket_promedio > 0]
        ticket_mercado = sum(tickets_promedio) / len(tickets_promedio) if tickets_promedio else 0
        
        return {
            'clientes_activos': self.numero_clientes_activos,
            'concentracion_top': float(self.calcular_concentracion_cliente_top() or 0),
            'ticket_promedio_mercado': ticket_mercado,
            'venta_minima': min(ventas_lista) if ventas_lista else 0,
            'venta_maxima': max(ventas_lista) if ventas_lista else 0,
            'distribucion_ventas': self._clasificar_distribucion()
        }
    
    def _clasificar_distribucion(self) -> str:
        """Clasificar el tipo de distribución de ventas."""
        if not self.ventas_por_cliente:
            return 'sin_datos'
        
        concentracion = self.calcular_concentracion_cliente_top()
        if concentracion is None:
            return 'sin_datos'
        
        if concentracion >= 50:
            return 'muy_concentrada'
        elif concentracion >= 30:
            return 'concentrada'
        elif concentracion >= 15:
            return 'moderada'
        else:
            return 'distribuida'
    
    def es_valido(self) -> bool:
        """Validar que los KPIs sean válidos para uso."""
        try:
            self._validar_consistencia()
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir KPIs a diccionario para serialización."""
        return {
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_fin': self.fecha_fin.isoformat(),
            'ventas_totales': float(self.ventas_totales),
            'numero_facturas': self.numero_facturas,
            'ticket_promedio': float(self.ticket_promedio),
            'ventas_por_cliente': [
                {
                    'nit': v.nit,
                    'nombre': v.nombre,
                    'nombre_display': v.nombre_display,
                    'total_ventas': float(v.total_ventas),
                    'numero_facturas': v.numero_facturas,
                    'ticket_promedio': float(v.ticket_promedio)
                }
                for v in self.ventas_por_cliente
            ],
            'cliente_top': {
                'nombre': self.cliente_top.nombre_display,
                'nit': self.cliente_top.nit,
                'monto': float(self.cliente_top.total_ventas)
            } if self.cliente_top else None,
            'fecha_calculo': self.fecha_calculo.isoformat(),
            'estado_sistema': self.estado_sistema,
            'estadisticas_avanzadas': self.calcular_estadisticas_avanzadas()
        }


@dataclass 
class KPIsFinancieros:
    """Entidad para KPIs financieros más avanzados."""
    
    # KPIs base
    kpis_ventas: KPIsVentas
    
    # Costos (cuando estén disponibles)
    costos_totales: Optional[Decimal] = None
    gastos_operacionales: Optional[Decimal] = None
    
    # Márgenes calculados
    margen_bruto: Optional[Decimal] = None
    margen_operacional: Optional[Decimal] = None
    
    def calcular_margenes(self) -> None:
        """Calcular márgenes cuando se tienen costos disponibles."""
        if self.costos_totales is not None and self.kpis_ventas.ventas_totales > 0:
            utilidad_bruta = self.kpis_ventas.ventas_totales - self.costos_totales
            self.margen_bruto = (utilidad_bruta / self.kpis_ventas.ventas_totales * 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        if (self.gastos_operacionales is not None and 
            self.margen_bruto is not None and 
            self.kpis_ventas.ventas_totales > 0):
            
            utilidad_operacional = (self.kpis_ventas.ventas_totales - 
                                  (self.costos_totales or Decimal('0')) - 
                                  self.gastos_operacionales)
            
            self.margen_operacional = (utilidad_operacional / self.kpis_ventas.ventas_totales * 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )