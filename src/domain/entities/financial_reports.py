"""
Domain entities for Financial Reports.
Contains the core business entities for Estado de Resultados and Estado de Situación Financiera.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class EstadoResultados:
    """
    Entidad de dominio para el Estado de Resultados (P&L).
    Representa la estructura fundamental del estado de resultados empresarial.
    """
    
    # Período del informe
    fecha_inicio: datetime
    fecha_fin: datetime
    
    # Componentes principales del estado de resultados
    ventas_netas: Decimal
    costo_ventas: Decimal  
    gastos_operativos: Decimal
    
    # Utilidades calculadas
    utilidad_bruta: Decimal
    utilidad_neta: Decimal
    
    # Información adicional
    empresa: Optional[str] = None
    moneda: str = "COP"
    
    def __post_init__(self):
        """Validar y calcular valores derivados."""
        # Convertir a Decimal si es necesario
        if not isinstance(self.ventas_netas, Decimal):
            self.ventas_netas = Decimal(str(self.ventas_netas))
        if not isinstance(self.costo_ventas, Decimal):
            self.costo_ventas = Decimal(str(self.costo_ventas))
        if not isinstance(self.gastos_operativos, Decimal):
            self.gastos_operativos = Decimal(str(self.gastos_operativos))
        if not isinstance(self.utilidad_bruta, Decimal):
            self.utilidad_bruta = Decimal(str(self.utilidad_bruta))
        if not isinstance(self.utilidad_neta, Decimal):
            self.utilidad_neta = Decimal(str(self.utilidad_neta))
    
    def calcular_utilidades(self) -> None:
        """Calcular las utilidades basadas en los componentes."""
        self.utilidad_bruta = self.ventas_netas - self.costo_ventas
        self.utilidad_neta = self.utilidad_bruta - self.gastos_operativos
    
    def calcular_margen_bruto_porcentaje(self) -> Decimal:
        """Calcular margen bruto como porcentaje."""
        if self.ventas_netas == 0:
            return Decimal('0.00')
        return (self.utilidad_bruta / self.ventas_netas) * 100
    
    def calcular_margen_neto_porcentaje(self) -> Decimal:
        """Calcular margen neto como porcentaje."""
        if self.ventas_netas == 0:
            return Decimal('0.00')
        return (self.utilidad_neta / self.ventas_netas) * 100
    
    def is_valid(self) -> bool:
        """Validar reglas de negocio del estado de resultados."""
        return (
            self.fecha_inicio is not None and
            self.fecha_fin is not None and
            self.fecha_inicio <= self.fecha_fin and
            self.ventas_netas >= 0 and
            self.costo_ventas >= 0 and
            self.gastos_operativos >= 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización."""
        return {
            "fecha_inicio": self.fecha_inicio.isoformat(),
            "fecha_fin": self.fecha_fin.isoformat(),
            "ventas_netas": float(self.ventas_netas),
            "costo_ventas": float(self.costo_ventas),
            "gastos_operativos": float(self.gastos_operativos),
            "utilidad_bruta": float(self.utilidad_bruta),
            "utilidad_neta": float(self.utilidad_neta),
            "margen_bruto_porcentaje": float(self.calcular_margen_bruto_porcentaje()),
            "margen_neto_porcentaje": float(self.calcular_margen_neto_porcentaje()),
            "empresa": self.empresa,
            "moneda": self.moneda
        }


@dataclass
class BalanceGeneral:
    """
    Entidad de dominio para el Estado de Situación Financiera.
    Representa la situación financiera de la empresa en un momento específico.
    """
    
    # Fecha de corte del balance
    fecha_corte: datetime
    
    # Activos
    activos_corrientes: Decimal
    activos_no_corrientes: Decimal
    total_activos: Decimal
    
    # Pasivos
    pasivos_corrientes: Decimal
    pasivos_no_corrientes: Decimal
    total_pasivos: Decimal
    
    # Patrimonio
    capital: Decimal
    utilidades_retenidas: Decimal
    utilidades_ejercicio: Decimal
    total_patrimonio: Decimal
    
    # Información adicional
    empresa: Optional[str] = None
    moneda: str = "COP"
    
    def __post_init__(self):
        """Validar y convertir valores a Decimal."""
        # Convertir todos los valores a Decimal
        decimal_fields = [
            'activos_corrientes', 'activos_no_corrientes', 'total_activos',
            'pasivos_corrientes', 'pasivos_no_corrientes', 'total_pasivos',
            'capital', 'utilidades_retenidas', 'utilidades_ejercicio', 'total_patrimonio'
        ]
        
        for field in decimal_fields:
            value = getattr(self, field)
            if not isinstance(value, Decimal):
                setattr(self, field, Decimal(str(value)))
    
    def calcular_totales(self) -> None:
        """Calcular los totales basados en los componentes."""
        self.total_activos = self.activos_corrientes + self.activos_no_corrientes
        self.total_pasivos = self.pasivos_corrientes + self.pasivos_no_corrientes
        self.total_patrimonio = self.capital + self.utilidades_retenidas + self.utilidades_ejercicio
    
    def validar_ecuacion_contable(self) -> bool:
        """Validar que se cumpla la ecuación contable: Activos = Pasivos + Patrimonio."""
        total_pasivos_patrimonio = self.total_pasivos + self.total_patrimonio
        # Permitir pequeñas diferencias por redondeo
        diferencia = abs(self.total_activos - total_pasivos_patrimonio)
        return diferencia <= Decimal('0.01')
    
    def calcular_ratio_liquidez(self) -> Decimal:
        """Calcular ratio de liquidez corriente."""
        if self.pasivos_corrientes == 0:
            return Decimal('0.00')
        return self.activos_corrientes / self.pasivos_corrientes
    
    def calcular_ratio_endeudamiento(self) -> Decimal:
        """Calcular ratio de endeudamiento."""
        if self.total_activos == 0:
            return Decimal('0.00')
        return self.total_pasivos / self.total_activos
    
    def is_valid(self) -> bool:
        """Validar reglas de negocio del estado de situación financiera."""
        return (
            self.fecha_corte is not None and
            self.total_activos >= 0 and
            self.total_pasivos >= 0 and
            self.total_patrimonio >= 0 and
            self.validar_ecuacion_contable()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización."""
        return {
            "fecha_corte": self.fecha_corte.isoformat(),
            "activos_corrientes": float(self.activos_corrientes),
            "activos_no_corrientes": float(self.activos_no_corrientes),
            "total_activos": float(self.total_activos),
            "pasivos_corrientes": float(self.pasivos_corrientes),
            "pasivos_no_corrientes": float(self.pasivos_no_corrientes),
            "total_pasivos": float(self.total_pasivos),
            "capital": float(self.capital),
            "utilidades_retenidas": float(self.utilidades_retenidas),
            "utilidades_ejercicio": float(self.utilidades_ejercicio),
            "total_patrimonio": float(self.total_patrimonio),
            "ratio_liquidez": float(self.calcular_ratio_liquidez()),
            "ratio_endeudamiento": float(self.calcular_ratio_endeudamiento()),
            "ecuacion_contable_valida": self.validar_ecuacion_contable(),
            "empresa": self.empresa,
            "moneda": self.moneda
        }


@dataclass
class CuentaContable:
    """
    Entidad que representa una cuenta contable del catálogo.
    Utilizada para clasificar las transacciones en el estado de resultados y balance.
    """
    
    codigo: str
    nombre: str
    tipo_cuenta: str  # 'activo', 'pasivo', 'patrimonio', 'ingreso', 'gasto'
    subtipo: str  # 'corriente', 'no_corriente', 'operativo', etc.
    saldo: Decimal
    
    def __post_init__(self):
        """Convertir saldo a Decimal."""
        if not isinstance(self.saldo, Decimal):
            self.saldo = Decimal(str(self.saldo))
    
    def es_activo(self) -> bool:
        """Verificar si es cuenta de activo."""
        return self.tipo_cuenta.lower() == 'activo'
    
    def es_pasivo(self) -> bool:
        """Verificar si es cuenta de pasivo."""
        return self.tipo_cuenta.lower() == 'pasivo'
    
    def es_patrimonio(self) -> bool:
        """Verificar si es cuenta de patrimonio."""
        return self.tipo_cuenta.lower() == 'patrimonio'
    
    def es_ingreso(self) -> bool:
        """Verificar si es cuenta de ingreso."""
        return self.tipo_cuenta.lower() == 'ingreso'
    
    def es_gasto(self) -> bool:
        """Verificar si es cuenta de gasto."""
        return self.tipo_cuenta.lower() == 'gasto'
    
    def es_corriente(self) -> bool:
        """Verificar si es cuenta corriente."""
        return self.subtipo.lower() == 'corriente'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "tipo_cuenta": self.tipo_cuenta,
            "subtipo": self.subtipo,
            "saldo": float(self.saldo)
        }


@dataclass
class PeriodoFiscal:
    """
    Entidad que representa un período fiscal para los informes.
    """
    
    fecha_inicio: datetime
    fecha_fin: datetime
    nombre: str  # "2025-Q1", "2025-Enero", etc.
    tipo_periodo: str  # "mensual", "trimestral", "anual"
    
    def es_valido(self) -> bool:
        """Validar que el período sea válido."""
        return (
            self.fecha_inicio is not None and
            self.fecha_fin is not None and
            self.fecha_inicio <= self.fecha_fin
        )
    
    def duracion_dias(self) -> int:
        """Calcular duración en días."""
        return (self.fecha_fin - self.fecha_inicio).days + 1
    
    def contiene_fecha(self, fecha: datetime) -> bool:
        """Verificar si una fecha está dentro del período."""
        return self.fecha_inicio <= fecha <= self.fecha_fin
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "fecha_inicio": self.fecha_inicio.isoformat(),
            "fecha_fin": self.fecha_fin.isoformat(),
            "nombre": self.nombre,
            "tipo_periodo": self.tipo_periodo,
            "duracion_dias": self.duracion_dias()
        }


@dataclass
class InformeFinancieroResumen:
    """
    Entidad que combina el Estado de Resultados y Estado de Situación Financiera
    para proporcionar una vista integral de la situación financiera.
    """
    
    estado_resultados: EstadoResultados
    balance_general: BalanceGeneral
    periodo: PeriodoFiscal
    fecha_generacion: datetime
    
    def __post_init__(self):
        """Validar coherencia entre los informes."""
        if self.fecha_generacion is None:
            self.fecha_generacion = datetime.now()
    
    def es_coherente(self) -> bool:
        """Validar que los informes sean coherentes entre sí."""
        # Las utilidades del ejercicio en el balance deben coincidir
        # con la utilidad neta del estado de resultados
        diferencia = abs(
            self.balance_general.utilidades_ejercicio - 
            self.estado_resultados.utilidad_neta
        )
        return diferencia <= Decimal('0.01')
    
    def calcular_kpis_principales(self) -> Dict[str, float]:
        """Calcular KPIs principales combinando ambos informes."""
        return {
            "margen_bruto": float(self.estado_resultados.calcular_margen_bruto_porcentaje()),
            "margen_neto": float(self.estado_resultados.calcular_margen_neto_porcentaje()),
            "ratio_liquidez": float(self.balance_general.calcular_ratio_liquidez()),
            "ratio_endeudamiento": float(self.balance_general.calcular_ratio_endeudamiento()),
            "roa": float(self._calcular_roa()),
            "roe": float(self._calcular_roe())
        }
    
    def _calcular_roa(self) -> Decimal:
        """Calcular Return on Assets."""
        if self.balance_general.total_activos == 0:
            return Decimal('0.00')
        return (self.estado_resultados.utilidad_neta / self.balance_general.total_activos) * 100
    
    def _calcular_roe(self) -> Decimal:
        """Calcular Return on Equity."""
        if self.balance_general.total_patrimonio == 0:
            return Decimal('0.00')
        return (self.estado_resultados.utilidad_neta / self.balance_general.total_patrimonio) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario completo."""
        return {
            "estado_resultados": self.estado_resultados.to_dict(),
            "balance_general": self.balance_general.to_dict(),
            "periodo": self.periodo.to_dict(),
            "fecha_generacion": self.fecha_generacion.isoformat(),
            "kpis_principales": self.calcular_kpis_principales(),
            "coherencia_informes": self.es_coherente()
        }