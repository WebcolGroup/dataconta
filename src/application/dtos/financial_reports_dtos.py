"""
DTOs (Data Transfer Objects) for Financial Reports.
These objects are used to transfer data between layers and API responses.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime


@dataclass
class EstadoResultadosDTO:
    """
    DTO para transferir datos del Estado de Resultados.
    Se usa para respuestas de API y comunicación entre capas.
    """
    
    fecha_inicio: str  # ISO format string
    fecha_fin: str     # ISO format string
    ventas_netas: float
    costo_ventas: float
    gastos_operativos: float
    utilidad_bruta: float
    utilidad_neta: float
    margen_bruto_porcentaje: float
    margen_neto_porcentaje: float
    empresa: Optional[str] = None
    moneda: str = "COP"
    
    @classmethod
    def from_domain(cls, estado_resultados) -> 'EstadoResultadosDTO':
        """Crear DTO desde entidad de dominio."""
        from src.domain.entities.financial_reports import EstadoResultados
        
        return cls(
            fecha_inicio=estado_resultados.fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin=estado_resultados.fecha_fin.strftime("%Y-%m-%d"),
            ventas_netas=float(estado_resultados.ventas_netas),
            costo_ventas=float(estado_resultados.costo_ventas),
            gastos_operativos=float(estado_resultados.gastos_operativos),
            utilidad_bruta=float(estado_resultados.utilidad_bruta),
            utilidad_neta=float(estado_resultados.utilidad_neta),
            margen_bruto_porcentaje=float(estado_resultados.calcular_margen_bruto_porcentaje()),
            margen_neto_porcentaje=float(estado_resultados.calcular_margen_neto_porcentaje()),
            empresa=estado_resultados.empresa,
            moneda=estado_resultados.moneda
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "ventas_netas": self.ventas_netas,
            "costo_ventas": self.costo_ventas,
            "gastos_operativos": self.gastos_operativos,
            "utilidad_bruta": self.utilidad_bruta,
            "utilidad_neta": self.utilidad_neta,
            "margen_bruto_porcentaje": self.margen_bruto_porcentaje,
            "margen_neto_porcentaje": self.margen_neto_porcentaje,
            "empresa": self.empresa,
            "moneda": self.moneda
        }


@dataclass
class BalanceGeneralDTO:
    """
    DTO para transferir datos del Balance General.
    """
    
    fecha_corte: str  # ISO format string
    activos_corrientes: float
    activos_no_corrientes: float
    total_activos: float
    pasivos_corrientes: float
    pasivos_no_corrientes: float
    total_pasivos: float
    capital: float
    utilidades_retenidas: float
    utilidades_ejercicio: float
    total_patrimonio: float
    ratio_liquidez: float
    ratio_endeudamiento: float
    ecuacion_contable_valida: bool
    empresa: Optional[str] = None
    moneda: str = "COP"
    
    @classmethod
    def from_domain(cls, balance_general) -> 'BalanceGeneralDTO':
        """Crear DTO desde entidad de dominio."""
        from src.domain.entities.financial_reports import BalanceGeneral
        
        return cls(
            fecha_corte=balance_general.fecha_corte.strftime("%Y-%m-%d"),
            activos_corrientes=float(balance_general.activos_corrientes),
            activos_no_corrientes=float(balance_general.activos_no_corrientes),
            total_activos=float(balance_general.total_activos),
            pasivos_corrientes=float(balance_general.pasivos_corrientes),
            pasivos_no_corrientes=float(balance_general.pasivos_no_corrientes),
            total_pasivos=float(balance_general.total_pasivos),
            capital=float(balance_general.capital),
            utilidades_retenidas=float(balance_general.utilidades_retenidas),
            utilidades_ejercicio=float(balance_general.utilidades_ejercicio),
            total_patrimonio=float(balance_general.total_patrimonio),
            ratio_liquidez=float(balance_general.calcular_ratio_liquidez()),
            ratio_endeudamiento=float(balance_general.calcular_ratio_endeudamiento()),
            ecuacion_contable_valida=balance_general.validar_ecuacion_contable(),
            empresa=balance_general.empresa,
            moneda=balance_general.moneda
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "fecha_corte": self.fecha_corte,
            "activos_corrientes": self.activos_corrientes,
            "activos_no_corrientes": self.activos_no_corrientes,
            "total_activos": self.total_activos,
            "pasivos_corrientes": self.pasivos_corrientes,
            "pasivos_no_corrientes": self.pasivos_no_corrientes,
            "total_pasivos": self.total_pasivos,
            "capital": self.capital,
            "utilidades_retenidas": self.utilidades_retenidas,
            "utilidades_ejercicio": self.utilidades_ejercicio,
            "total_patrimonio": self.total_patrimonio,
            "ratio_liquidez": self.ratio_liquidez,
            "ratio_endeudamiento": self.ratio_endeudamiento,
            "ecuacion_contable_valida": self.ecuacion_contable_valida,
            "empresa": self.empresa,
            "moneda": self.moneda
        }


@dataclass
class CuentaContableDTO:
    """
    DTO para transferir datos de cuentas contables.
    """
    
    codigo: str
    nombre: str
    tipo_cuenta: str
    subtipo: str
    saldo: float
    
    @classmethod
    def from_domain(cls, cuenta) -> 'CuentaContableDTO':
        """Crear DTO desde entidad de dominio."""
        from src.domain.entities.financial_reports import CuentaContable
        
        return cls(
            codigo=cuenta.codigo,
            nombre=cuenta.nombre,
            tipo_cuenta=cuenta.tipo_cuenta,
            subtipo=cuenta.subtipo,
            saldo=float(cuenta.saldo)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "tipo_cuenta": self.tipo_cuenta,
            "subtipo": self.subtipo,
            "saldo": self.saldo
        }


@dataclass
class PeriodoFiscalDTO:
    """
    DTO para transferir datos de períodos fiscales.
    """
    
    fecha_inicio: str  # ISO format string
    fecha_fin: str     # ISO format string
    nombre: str
    tipo_periodo: str
    duracion_dias: int
    
    @classmethod
    def from_domain(cls, periodo) -> 'PeriodoFiscalDTO':
        """Crear DTO desde entidad de dominio."""
        from src.domain.entities.financial_reports import PeriodoFiscal
        
        return cls(
            fecha_inicio=periodo.fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin=periodo.fecha_fin.strftime("%Y-%m-%d"),
            nombre=periodo.nombre,
            tipo_periodo=periodo.tipo_periodo,
            duracion_dias=periodo.duracion_dias()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "nombre": self.nombre,
            "tipo_periodo": self.tipo_periodo,
            "duracion_dias": self.duracion_dias
        }


@dataclass
class InformeFinancieroResumenDTO:
    """
    DTO para el informe financiero completo.
    """
    
    estado_resultados: EstadoResultadosDTO
    balance_general: BalanceGeneralDTO
    periodo: PeriodoFiscalDTO
    fecha_generacion: str  # ISO format string
    kpis_principales: Dict[str, float]
    coherencia_informes: bool
    
    @classmethod
    def from_domain(cls, informe) -> 'InformeFinancieroResumenDTO':
        """Crear DTO desde entidad de dominio."""
        from src.domain.entities.financial_reports import InformeFinancieroResumen
        
        return cls(
            estado_resultados=EstadoResultadosDTO.from_domain(informe.estado_resultados),
            balance_general=BalanceGeneralDTO.from_domain(informe.balance_general),
            periodo=PeriodoFiscalDTO.from_domain(informe.periodo),
            fecha_generacion=informe.fecha_generacion.isoformat(),
            kpis_principales=informe.calcular_kpis_principales(),
            coherencia_informes=informe.es_coherente()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario completo."""
        return {
            "estado_resultados": self.estado_resultados.to_dict(),
            "balance_general": self.balance_general.to_dict(),
            "periodo": self.periodo.to_dict(),
            "fecha_generacion": self.fecha_generacion,
            "kpis_principales": self.kpis_principales,
            "coherencia_informes": self.coherencia_informes
        }


# ========================================================================================
# DTOs PARA RESPUESTAS DE LA API DE SIIGO
# ========================================================================================

@dataclass
class SiigoInvoiceDTO:
    """
    DTO para facturas de Siigo API.
    Estructura básica de respuesta de /v1/invoices
    """
    
    id: str
    document_id: str
    number: str
    name: str
    date: str
    customer: Dict[str, Any]
    items: List[Dict[str, Any]]
    payments: List[Dict[str, Any]]
    total: float
    subtotal: float
    discount: float
    taxes: List[Dict[str, Any]]
    retentions: List[Dict[str, Any]]
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SiigoInvoiceDTO':
        """Crear DTO desde respuesta de API."""
        return cls(
            id=data.get('id', ''),
            document_id=data.get('document_id', ''),
            number=data.get('number', ''),
            name=data.get('name', ''),
            date=data.get('date', ''),
            customer=data.get('customer', {}),
            items=data.get('items', []),
            payments=data.get('payments', []),
            total=float(data.get('total', 0)),
            subtotal=float(data.get('subtotal', 0)),
            discount=float(data.get('discount', 0)),
            taxes=data.get('taxes', []),
            retentions=data.get('retentions', [])
        )


@dataclass
class SiigoCreditNoteDTO:
    """
    DTO para notas de crédito de Siigo API.
    """
    
    id: str
    document_id: str
    number: str
    date: str
    customer: Dict[str, Any]
    total: float
    reference_invoice: Dict[str, Any]
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SiigoCreditNoteDTO':
        """Crear DTO desde respuesta de API."""
        return cls(
            id=data.get('id', ''),
            document_id=data.get('document_id', ''),
            number=data.get('number', ''),
            date=data.get('date', ''),
            customer=data.get('customer', {}),
            total=float(data.get('total', 0)),
            reference_invoice=data.get('reference_invoice', {})
        )


@dataclass
class SiigoPurchaseDTO:
    """
    DTO para compras de Siigo API.
    """
    
    id: str
    document_id: str
    number: str
    date: str
    supplier: Dict[str, Any]
    items: List[Dict[str, Any]]
    total: float
    subtotal: float
    taxes: List[Dict[str, Any]]
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SiigoPurchaseDTO':
        """Crear DTO desde respuesta de API."""
        return cls(
            id=data.get('id', ''),
            document_id=data.get('document_id', ''),
            number=data.get('number', ''),
            date=data.get('date', ''),
            supplier=data.get('supplier', {}),
            items=data.get('items', []),
            total=float(data.get('total', 0)),
            subtotal=float(data.get('subtotal', 0)),
            taxes=data.get('taxes', [])
        )


@dataclass
class SiigoJournalEntryDTO:
    """
    DTO para asientos contables de Siigo API.
    """
    
    id: str
    number: str
    date: str
    reference: str
    observations: str
    entries: List[Dict[str, Any]]  # Lista de movimientos
    total_debit: float
    total_credit: float
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SiigoJournalEntryDTO':
        """Crear DTO desde respuesta de API."""
        return cls(
            id=data.get('id', ''),
            number=data.get('number', ''),
            date=data.get('date', ''),
            reference=data.get('reference', ''),
            observations=data.get('observations', ''),
            entries=data.get('entries', []),
            total_debit=float(data.get('total_debit', 0)),
            total_credit=float(data.get('total_credit', 0))
        )


@dataclass
class SiigoTrialBalanceDTO:
    """
    DTO para balance de prueba de Siigo API.
    """
    
    fecha_corte: str
    accounts: List[Dict[str, Any]]  # Lista de cuentas con saldos
    total_debits: float
    total_credits: float
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SiigoTrialBalanceDTO':
        """Crear DTO desde respuesta de API."""
        return cls(
            fecha_corte=data.get('fecha_corte', ''),
            accounts=data.get('accounts', []),
            total_debits=float(data.get('total_debits', 0)),
            total_credits=float(data.get('total_credits', 0))
        )


# ========================================================================================
# DTOs PARA RESPUESTAS DE USUARIO (CLI)
# ========================================================================================

@dataclass
class FinancialReportRequestDTO:
    """
    DTO para solicitudes de informes financieros desde el CLI.
    """
    
    tipo_informe: str  # 'estado_resultados', 'balance_general', 'completo'
    fecha_inicio: Optional[str] = None  # Para Estado de Resultados
    fecha_fin: Optional[str] = None     # Para Estado de Resultados
    fecha_corte: Optional[str] = None   # Para Balance General
    formato_salida: str = 'json'       # 'json', 'csv', 'excel'
    incluir_kpis: bool = True
    incluir_detalle: bool = False
    
    def is_valid(self) -> bool:
        """Validar que la solicitud tenga los datos necesarios."""
        if self.tipo_informe == 'estado_resultados':
            return self.fecha_inicio is not None and self.fecha_fin is not None
        elif self.tipo_informe == 'balance_general':
            return self.fecha_corte is not None
        elif self.tipo_informe == 'completo':
            return (
                self.fecha_inicio is not None and 
                self.fecha_fin is not None and 
                self.fecha_corte is not None
            )
        return False


@dataclass
class FinancialReportResponseDTO:
    """
    DTO para respuestas de informes financieros hacia el CLI.
    """
    
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    execution_time_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "file_path": self.file_path,
            "execution_time_seconds": self.execution_time_seconds
        }