"""
Estado de Resultados - Entidad de Dominio
Representa el Estado de Resultados según normativa tributaria colombiana (Decreto 2420/2015)

Responsabilidad única: Modelar Estado de Resultados con cálculos tributarios correctos
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class PeriodoComparacion:
    """Representa un periodo para comparación en Estado de Resultados."""
    fecha_inicio: datetime
    fecha_fin: datetime
    nombre: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_fin': self.fecha_fin.isoformat(),
            'nombre': self.nombre
        }


@dataclass
class LineaEstadoResultados:
    """Representa una línea individual del Estado de Resultados."""
    codigo: str
    descripcion: str
    valor_actual: Decimal
    valor_anterior: Optional[Decimal] = None
    
    @property
    def variacion_absoluta(self) -> Optional[Decimal]:
        """Calcular variación absoluta respecto al periodo anterior."""
        if self.valor_anterior is None:
            return None
        return self.valor_actual - self.valor_anterior
    
    @property
    def variacion_porcentual(self) -> Optional[Decimal]:
        """Calcular variación porcentual respecto al periodo anterior."""
        if self.valor_anterior is None or self.valor_anterior == 0:
            return None
        return ((self.valor_actual - self.valor_anterior) / abs(self.valor_anterior)) * Decimal('100')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigo': self.codigo,
            'descripcion': self.descripcion,
            'valor_actual': float(self.valor_actual),
            'valor_anterior': float(self.valor_anterior) if self.valor_anterior else None,
            'variacion_absoluta': float(self.variacion_absoluta) if self.variacion_absoluta else None,
            'variacion_porcentual': float(self.variacion_porcentual) if self.variacion_porcentual else None
        }


class EstadoResultados:
    """
    Entidad de dominio que representa un Estado de Resultados según normativa colombiana.
    
    Principios SOLID aplicados:
    - SRP: Solo maneja el Estado de Resultados y sus cálculos
    - OCP: Extensible para nuevos tipos de cálculos tributarios
    - LSP: Puede ser sustituido por subclases especializadas
    - ISP: Interfaces específicas para cada tipo de cálculo
    - DIP: No depende de implementaciones concretas
    
    Normativa aplicada:
    - Decreto 2420/2015 - Marco Técnico Normativo de Información Financiera
    - Ley 1314/2009 - Regulación de la información financiera
    - NIIF para PYMES - Normas Internacionales de Información Financiera
    """
    
    def __init__(self, periodo_actual: PeriodoComparacion, periodo_anterior: Optional[PeriodoComparacion] = None):
        self.periodo_actual = periodo_actual
        self.periodo_anterior = periodo_anterior
        self.fecha_generacion = datetime.now()
        
        # Secciones del Estado de Resultados según normativa colombiana
        self._ingresos: List[LineaEstadoResultados] = []
        self._costos_ventas: List[LineaEstadoResultados] = []
        self._gastos_administracion: List[LineaEstadoResultados] = []
        self._gastos_ventas: List[LineaEstadoResultados] = []
        self._otros_ingresos: List[LineaEstadoResultados] = []
        self._otros_gastos: List[LineaEstadoResultados] = []
        self._gastos_financieros: List[LineaEstadoResultados] = []
        self._impuestos: List[LineaEstadoResultados] = []
    
    # ==================== Métodos de Construcción ====================
    
    def agregar_ingreso(self, codigo: str, descripcion: str, valor_actual: Decimal, valor_anterior: Optional[Decimal] = None):
        """Agregar línea de ingresos operacionales."""
        linea = LineaEstadoResultados(codigo, descripcion, valor_actual, valor_anterior)
        self._ingresos.append(linea)
    
    def agregar_costo_ventas(self, codigo: str, descripcion: str, valor_actual: Decimal, valor_anterior: Optional[Decimal] = None):
        """Agregar línea de costos de ventas."""
        linea = LineaEstadoResultados(codigo, descripcion, valor_actual, valor_anterior)
        self._costos_ventas.append(linea)
    
    def agregar_gasto_administracion(self, codigo: str, descripcion: str, valor_actual: Decimal, valor_anterior: Optional[Decimal] = None):
        """Agregar línea de gastos de administración."""
        linea = LineaEstadoResultados(codigo, descripcion, valor_actual, valor_anterior)
        self._gastos_administracion.append(linea)
    
    def agregar_gasto_ventas(self, codigo: str, descripcion: str, valor_actual: Decimal, valor_anterior: Optional[Decimal] = None):
        """Agregar línea de gastos de ventas."""
        linea = LineaEstadoResultados(codigo, descripcion, valor_actual, valor_anterior)
        self._gastos_ventas.append(linea)
    
    def agregar_otro_ingreso(self, codigo: str, descripcion: str, valor_actual: Decimal, valor_anterior: Optional[Decimal] = None):
        """Agregar línea de otros ingresos no operacionales."""
        linea = LineaEstadoResultados(codigo, descripcion, valor_actual, valor_anterior)
        self._otros_ingresos.append(linea)
    
    def agregar_otro_gasto(self, codigo: str, descripcion: str, valor_actual: Decimal, valor_anterior: Optional[Decimal] = None):
        """Agregar línea de otros gastos no operacionales."""
        linea = LineaEstadoResultados(codigo, descripcion, valor_actual, valor_anterior)
        self._otros_gastos.append(linea)
    
    def agregar_gasto_financiero(self, codigo: str, descripcion: str, valor_actual: Decimal, valor_anterior: Optional[Decimal] = None):
        """Agregar línea de gastos financieros."""
        linea = LineaEstadoResultados(codigo, descripcion, valor_actual, valor_anterior)
        self._gastos_financieros.append(linea)
    
    def agregar_impuesto(self, codigo: str, descripcion: str, valor_actual: Decimal, valor_anterior: Optional[Decimal] = None):
        """Agregar línea de impuestos."""
        linea = LineaEstadoResultados(codigo, descripcion, valor_actual, valor_anterior)
        self._impuestos.append(linea)
    
    # ==================== Cálculos Principales ====================
    
    @property
    def total_ingresos_operacionales(self) -> Decimal:
        """Total de ingresos operacionales (ventas netas)."""
        return sum(linea.valor_actual for linea in self._ingresos)
    
    @property
    def total_costos_ventas(self) -> Decimal:
        """Total de costos de ventas."""
        return sum(linea.valor_actual for linea in self._costos_ventas)
    
    @property
    def utilidad_bruta(self) -> Decimal:
        """Utilidad Bruta = Ingresos Operacionales - Costos de Ventas."""
        return self.total_ingresos_operacionales - self.total_costos_ventas
    
    @property
    def total_gastos_operacionales(self) -> Decimal:
        """Total de gastos operacionales (administración + ventas)."""
        gastos_admin = sum(linea.valor_actual for linea in self._gastos_administracion)
        gastos_ventas = sum(linea.valor_actual for linea in self._gastos_ventas)
        return gastos_admin + gastos_ventas
    
    @property
    def utilidad_operacional(self) -> Decimal:
        """Utilidad Operacional = Utilidad Bruta - Gastos Operacionales."""
        return self.utilidad_bruta - self.total_gastos_operacionales
    
    @property
    def total_otros_ingresos(self) -> Decimal:
        """Total de otros ingresos no operacionales."""
        return sum(linea.valor_actual for linea in self._otros_ingresos)
    
    @property
    def total_otros_gastos(self) -> Decimal:
        """Total de otros gastos no operacionales."""
        return sum(linea.valor_actual for linea in self._otros_gastos)
    
    @property
    def total_gastos_financieros(self) -> Decimal:
        """Total de gastos financieros."""
        return sum(linea.valor_actual for linea in self._gastos_financieros)
    
    @property
    def utilidad_antes_impuestos(self) -> Decimal:
        """Utilidad antes de impuestos = Utilidad Operacional + Otros Ingresos - Otros Gastos - Gastos Financieros."""
        return (self.utilidad_operacional + 
                self.total_otros_ingresos - 
                self.total_otros_gastos - 
                self.total_gastos_financieros)
    
    @property
    def total_impuestos(self) -> Decimal:
        """Total de impuestos (renta y complementarios)."""
        return sum(linea.valor_actual for linea in self._impuestos)
    
    @property
    def utilidad_neta(self) -> Decimal:
        """Utilidad Neta = Utilidad antes de impuestos - Impuestos."""
        return self.utilidad_antes_impuestos - self.total_impuestos
    
    # ==================== Cálculos de Márgenes ====================
    
    @property
    def margen_bruto(self) -> Optional[Decimal]:
        """Margen Bruto % = (Utilidad Bruta / Ingresos Operacionales) * 100."""
        if self.total_ingresos_operacionales == 0:
            return None
        return (self.utilidad_bruta / self.total_ingresos_operacionales * Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def margen_operacional(self) -> Optional[Decimal]:
        """Margen Operacional % = (Utilidad Operacional / Ingresos Operacionales) * 100."""
        if self.total_ingresos_operacionales == 0:
            return None
        return (self.utilidad_operacional / self.total_ingresos_operacionales * Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def margen_neto(self) -> Optional[Decimal]:
        """Margen Neto % = (Utilidad Neta / Ingresos Operacionales) * 100."""
        if self.total_ingresos_operacionales == 0:
            return None
        return (self.utilidad_neta / self.total_ingresos_operacionales * Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # ==================== Métodos de Acceso ====================
    
    def get_ingresos(self) -> List[LineaEstadoResultados]:
        """Obtener lista de ingresos operacionales."""
        return self._ingresos.copy()
    
    def get_costos_ventas(self) -> List[LineaEstadoResultados]:
        """Obtener lista de costos de ventas."""
        return self._costos_ventas.copy()
    
    def get_gastos_administracion(self) -> List[LineaEstadoResultados]:
        """Obtener lista de gastos de administración."""
        return self._gastos_administracion.copy()
    
    def get_gastos_ventas(self) -> List[LineaEstadoResultados]:
        """Obtener lista de gastos de ventas."""
        return self._gastos_ventas.copy()
    
    def get_otros_ingresos(self) -> List[LineaEstadoResultados]:
        """Obtener lista de otros ingresos."""
        return self._otros_ingresos.copy()
    
    def get_otros_gastos(self) -> List[LineaEstadoResultados]:
        """Obtener lista de otros gastos."""
        return self._otros_gastos.copy()
    
    def get_gastos_financieros(self) -> List[LineaEstadoResultados]:
        """Obtener lista de gastos financieros."""
        return self._gastos_financieros.copy()
    
    def get_impuestos(self) -> List[LineaEstadoResultados]:
        """Obtener lista de impuestos."""
        return self._impuestos.copy()
    
    # ==================== Serialización ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir Estado de Resultados a diccionario."""
        return {
            'fecha_generacion': self.fecha_generacion.isoformat(),
            'periodo_actual': self.periodo_actual.to_dict(),
            'periodo_anterior': self.periodo_anterior.to_dict() if self.periodo_anterior else None,
            
            # Totales principales
            'total_ingresos_operacionales': float(self.total_ingresos_operacionales),
            'total_costos_ventas': float(self.total_costos_ventas),
            'utilidad_bruta': float(self.utilidad_bruta),
            'total_gastos_operacionales': float(self.total_gastos_operacionales),
            'utilidad_operacional': float(self.utilidad_operacional),
            'total_otros_ingresos': float(self.total_otros_ingresos),
            'total_otros_gastos': float(self.total_otros_gastos),
            'total_gastos_financieros': float(self.total_gastos_financieros),
            'utilidad_antes_impuestos': float(self.utilidad_antes_impuestos),
            'total_impuestos': float(self.total_impuestos),
            'utilidad_neta': float(self.utilidad_neta),
            
            # Márgenes
            'margen_bruto': float(self.margen_bruto) if self.margen_bruto else None,
            'margen_operacional': float(self.margen_operacional) if self.margen_operacional else None,
            'margen_neto': float(self.margen_neto) if self.margen_neto else None,
            
            # Detalle por secciones
            'ingresos': [linea.to_dict() for linea in self._ingresos],
            'costos_ventas': [linea.to_dict() for linea in self._costos_ventas],
            'gastos_administracion': [linea.to_dict() for linea in self._gastos_administracion],
            'gastos_ventas': [linea.to_dict() for linea in self._gastos_ventas],
            'otros_ingresos': [linea.to_dict() for linea in self._otros_ingresos],
            'otros_gastos': [linea.to_dict() for linea in self._otros_gastos],
            'gastos_financieros': [linea.to_dict() for linea in self._gastos_financieros],
            'impuestos': [linea.to_dict() for linea in self._impuestos]
        }
    
    def __str__(self) -> str:
        """Representación en string del Estado de Resultados."""
        return (f"Estado de Resultados - {self.periodo_actual.nombre}\n"
                f"Ingresos: ${self.total_ingresos_operacionales:,.2f}\n"
                f"Utilidad Bruta: ${self.utilidad_bruta:,.2f}\n"
                f"Utilidad Operacional: ${self.utilidad_operacional:,.2f}\n"
                f"Utilidad Neta: ${self.utilidad_neta:,.2f}")


# ==================== Enums y Constantes ====================

class TipoComparacion:
    """Tipos de comparación disponibles para el Estado de Resultados."""
    PERIODO_ANTERIOR = "periodo_anterior"
    MISMO_PERIODO_ANO_ANTERIOR = "mismo_periodo_ano_anterior"  
    PERSONALIZADO = "personalizado"
    
    @classmethod
    def get_opciones(cls) -> List[Dict[str, str]]:
        """Obtener opciones disponibles para dropdown."""
        return [
            {'value': cls.PERIODO_ANTERIOR, 'label': 'Periodo inmediatamente anterior'},
            {'value': cls.MISMO_PERIODO_ANO_ANTERIOR, 'label': 'Mismo periodo año anterior'},
            {'value': cls.PERSONALIZADO, 'label': 'Personalizado'}
        ]