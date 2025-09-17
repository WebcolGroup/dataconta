"""
Domain services for Financial Reports.
Contains business logic for Estado de Resultados and Estado de Situación Financiera.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from src.domain.entities.financial_reports import (
    EstadoResultados, BalanceGeneral, CuentaContable, 
    PeriodoFiscal, InformeFinancieroResumen
)


class EstadoResultadosService(ABC):
    """
    Servicio de dominio para el cálculo del Estado de Resultados.
    Contiene la lógica de negocio para procesar datos financieros.
    """
    
    @abstractmethod
    def calcular_estado_resultados(
        self, 
        ventas: List[Dict[str, Any]], 
        compras: List[Dict[str, Any]], 
        gastos: List[Dict[str, Any]],
        periodo: PeriodoFiscal
    ) -> EstadoResultados:
        """
        Calcular Estado de Resultados basado en datos transaccionales.
        
        Args:
            ventas: Lista de facturas/ventas del período
            compras: Lista de compras del período  
            gastos: Lista de gastos operativos del período
            periodo: Período fiscal del informe
            
        Returns:
            EstadoResultados calculado
        """
        pass
    
    @abstractmethod
    def procesar_ventas(self, ventas: List[Dict[str, Any]]) -> Decimal:
        """Procesar y sumar todas las ventas del período."""
        pass
    
    @abstractmethod
    def procesar_costo_ventas(self, compras: List[Dict[str, Any]]) -> Decimal:
        """Procesar y calcular el costo de ventas."""
        pass
    
    @abstractmethod
    def procesar_gastos_operativos(self, gastos: List[Dict[str, Any]]) -> Decimal:
        """Procesar y sumar todos los gastos operativos."""
        pass


class BalanceGeneralService(ABC):
    """
    Servicio de dominio para el cálculo del Estado de Situación Financiera.
    """
    
    @abstractmethod
    def calcular_balance_general(
        self, 
        cuentas_balance: List[CuentaContable],
        fecha_corte: datetime
    ) -> BalanceGeneral:
        """
        Calcular Estado de Situación Financiera basado en el balance de prueba.
        
        Args:
            cuentas_balance: Lista de cuentas con saldos
            fecha_corte: Fecha de corte del balance
            
        Returns:
            BalanceGeneral calculado
        """
        pass
    
    @abstractmethod
    def clasificar_activos_corrientes(self, cuentas: List[CuentaContable]) -> Decimal:
        """Clasificar y sumar activos corrientes."""
        pass
    
    @abstractmethod
    def clasificar_activos_no_corrientes(self, cuentas: List[CuentaContable]) -> Decimal:
        """Clasificar y sumar activos no corrientes."""
        pass
    
    @abstractmethod
    def clasificar_pasivos_corrientes(self, cuentas: List[CuentaContable]) -> Decimal:
        """Clasificar y sumar pasivos corrientes."""
        pass
    
    @abstractmethod
    def clasificar_pasivos_no_corrientes(self, cuentas: List[CuentaContable]) -> Decimal:
        """Clasificar y sumar pasivos no corrientes."""
        pass
    
    @abstractmethod
    def clasificar_patrimonio(self, cuentas: List[CuentaContable]) -> Dict[str, Decimal]:
        """Clasificar cuentas de patrimonio (capital, utilidades, etc.)."""
        pass


class InformeFinancieroService(ABC):
    """
    Servicio de dominio para generar informes financieros completos.
    """
    
    @abstractmethod
    def generar_informe_completo(
        self,
        estado_resultados: EstadoResultados,
        balance_general: BalanceGeneral,
        periodo: PeriodoFiscal
    ) -> InformeFinancieroResumen:
        """
        Generar informe financiero completo combinando ambos estados.
        
        Args:
            estado_resultados: Estado de Resultados calculado
            balance_general: Estado de Situación Financiera calculado
            periodo: Período del informe
            
        Returns:
            InformeFinancieroResumen completo
        """
        pass
    
    @abstractmethod
    def validar_coherencia(
        self,
        estado_resultados: EstadoResultados,
        balance_general: BalanceGeneral
    ) -> bool:
        """Validar coherencia entre ambos informes."""
        pass
    
    @abstractmethod
    def calcular_kpis_financieros(
        self,
        estado_resultados: EstadoResultados,
        balance_general: BalanceGeneral
    ) -> Dict[str, float]:
        """Calcular KPIs financieros principales."""
        pass


# ========================================================================================
# IMPLEMENTACIONES CONCRETAS
# ========================================================================================

class EstadoResultadosServiceImpl(EstadoResultadosService):
    """
    Implementación concreta del servicio de Estado de Resultados.
    """
    
    def calcular_estado_resultados(
        self, 
        ventas: List[Dict[str, Any]], 
        compras: List[Dict[str, Any]], 
        gastos: List[Dict[str, Any]],
        periodo: PeriodoFiscal
    ) -> EstadoResultados:
        """Calcular Estado de Resultados."""
        
        # Procesar componentes
        ventas_netas = self.procesar_ventas(ventas)
        costo_ventas = self.procesar_costo_ventas(compras)
        gastos_operativos = self.procesar_gastos_operativos(gastos)
        
        # Crear estado de resultados
        estado = EstadoResultados(
            fecha_inicio=periodo.fecha_inicio,
            fecha_fin=periodo.fecha_fin,
            ventas_netas=ventas_netas,
            costo_ventas=costo_ventas,
            gastos_operativos=gastos_operativos,
            utilidad_bruta=Decimal('0'),  # Se calcula en post_init
            utilidad_neta=Decimal('0')    # Se calcula en post_init
        )
        
        # Calcular utilidades
        estado.calcular_utilidades()
        
        return estado
    
    def procesar_ventas(self, ventas: List[Dict[str, Any]]) -> Decimal:
        """Procesar y sumar todas las ventas."""
        total_ventas = Decimal('0')
        
        for venta in ventas:
            # Procesar facturas de Siigo
            total = venta.get('total', 0)
            if isinstance(total, (int, float, str)):
                total_ventas += Decimal(str(total))
        
        return total_ventas
    
    def procesar_costo_ventas(self, compras: List[Dict[str, Any]]) -> Decimal:
        """Procesar y calcular costo de ventas."""
        total_costo = Decimal('0')
        
        for compra in compras:
            # Procesar compras de Siigo
            total = compra.get('total', 0)
            if isinstance(total, (int, float, str)):
                total_costo += Decimal(str(total))
        
        return total_costo
    
    def procesar_gastos_operativos(self, gastos: List[Dict[str, Any]]) -> Decimal:
        """Procesar gastos operativos."""
        total_gastos = Decimal('0')
        
        for gasto in gastos:
            # Procesar asientos contables de gastos
            if 'entries' in gasto:
                for entry in gasto['entries']:
                    # Solo considerar débitos en cuentas de gasto
                    account_code = entry.get('account_code', '')
                    if account_code.startswith('5'):  # Cuentas de gasto en Colombia
                        debit = entry.get('debit', 0)
                        if isinstance(debit, (int, float, str)) and debit:
                            total_gastos += Decimal(str(debit))
        
        return total_gastos


class BalanceGeneralServiceImpl(BalanceGeneralService):
    """
    Implementación concreta del servicio de Estado de Situación Financiera.
    """
    
    def calcular_balance_general(
        self, 
        cuentas_balance: List[CuentaContable],
        fecha_corte: datetime
    ) -> BalanceGeneral:
        """Calcular Estado de Situación Financiera."""
        
        # Clasificar cuentas
        activos_corrientes = self.clasificar_activos_corrientes(cuentas_balance)
        activos_no_corrientes = self.clasificar_activos_no_corrientes(cuentas_balance)
        pasivos_corrientes = self.clasificar_pasivos_corrientes(cuentas_balance)
        pasivos_no_corrientes = self.clasificar_pasivos_no_corrientes(cuentas_balance)
        patrimonio_data = self.clasificar_patrimonio(cuentas_balance)
        
        # Crear balance
        balance = BalanceGeneral(
            fecha_corte=fecha_corte,
            activos_corrientes=activos_corrientes,
            activos_no_corrientes=activos_no_corrientes,
            total_activos=Decimal('0'),  # Se calcula en post_init
            pasivos_corrientes=pasivos_corrientes,
            pasivos_no_corrientes=pasivos_no_corrientes,
            total_pasivos=Decimal('0'),  # Se calcula en post_init
            capital=patrimonio_data.get('capital', Decimal('0')),
            utilidades_retenidas=patrimonio_data.get('utilidades_retenidas', Decimal('0')),
            utilidades_ejercicio=patrimonio_data.get('utilidades_ejercicio', Decimal('0')),
            total_patrimonio=Decimal('0')  # Se calcula en post_init
        )
        
        # Calcular totales
        balance.calcular_totales()
        
        return balance
    
    def clasificar_activos_corrientes(self, cuentas: List[CuentaContable]) -> Decimal:
        """Clasificar activos corrientes."""
        total = Decimal('0')
        
        for cuenta in cuentas:
            if cuenta.es_activo() and cuenta.es_corriente():
                total += cuenta.saldo
        
        return total
    
    def clasificar_activos_no_corrientes(self, cuentas: List[CuentaContable]) -> Decimal:
        """Clasificar activos no corrientes."""
        total = Decimal('0')
        
        for cuenta in cuentas:
            if cuenta.es_activo() and not cuenta.es_corriente():
                total += cuenta.saldo
        
        return total
    
    def clasificar_pasivos_corrientes(self, cuentas: List[CuentaContable]) -> Decimal:
        """Clasificar pasivos corrientes."""
        total = Decimal('0')
        
        for cuenta in cuentas:
            if cuenta.es_pasivo() and cuenta.es_corriente():
                total += cuenta.saldo
        
        return total
    
    def clasificar_pasivos_no_corrientes(self, cuentas: List[CuentaContable]) -> Decimal:
        """Clasificar pasivos no corrientes."""
        total = Decimal('0')
        
        for cuenta in cuentas:
            if cuenta.es_pasivo() and not cuenta.es_corriente():
                total += cuenta.saldo
        
        return total
    
    def clasificar_patrimonio(self, cuentas: List[CuentaContable]) -> Dict[str, Decimal]:
        """Clasificar cuentas de patrimonio."""
        patrimonio = {
            'capital': Decimal('0'),
            'utilidades_retenidas': Decimal('0'),
            'utilidades_ejercicio': Decimal('0')
        }
        
        for cuenta in cuentas:
            if cuenta.es_patrimonio():
                if 'capital' in cuenta.nombre.lower():
                    patrimonio['capital'] += cuenta.saldo
                elif 'utilidad' in cuenta.nombre.lower():
                    if 'ejercicio' in cuenta.nombre.lower() or 'periodo' in cuenta.nombre.lower():
                        patrimonio['utilidades_ejercicio'] += cuenta.saldo
                    else:
                        patrimonio['utilidades_retenidas'] += cuenta.saldo
        
        return patrimonio


class InformeFinancieroServiceImpl(InformeFinancieroService):
    """
    Implementación concreta del servicio de informes financieros.
    """
    
    def generar_informe_completo(
        self,
        estado_resultados: EstadoResultados,
        balance_general: BalanceGeneral,
        periodo: PeriodoFiscal
    ) -> InformeFinancieroResumen:
        """Generar informe financiero completo."""
        
        informe = InformeFinancieroResumen(
            estado_resultados=estado_resultados,
            balance_general=balance_general,
            periodo=periodo,
            fecha_generacion=datetime.now()
        )
        
        return informe
    
    def validar_coherencia(
        self,
        estado_resultados: EstadoResultados,
        balance_general: BalanceGeneral
    ) -> bool:
        """Validar coherencia entre informes."""
        
        # La utilidad neta del Estado de Resultados debe coincidir
        # con las utilidades del ejercicio en el Balance
        diferencia = abs(
            balance_general.utilidades_ejercicio - 
            estado_resultados.utilidad_neta
        )
        
        return diferencia <= Decimal('0.01')
    
    def calcular_kpis_financieros(
        self,
        estado_resultados: EstadoResultados,
        balance_general: BalanceGeneral
    ) -> Dict[str, float]:
        """Calcular KPIs financieros."""
        
        return {
            "margen_bruto": float(estado_resultados.calcular_margen_bruto_porcentaje()),
            "margen_neto": float(estado_resultados.calcular_margen_neto_porcentaje()),
            "ratio_liquidez": float(balance_general.calcular_ratio_liquidez()),
            "ratio_endeudamiento": float(balance_general.calcular_ratio_endeudamiento()),
            "roa": float(self._calcular_roa(estado_resultados, balance_general)),
            "roe": float(self._calcular_roe(estado_resultados, balance_general))
        }
    
    def _calcular_roa(self, estado: EstadoResultados, balance: BalanceGeneral) -> Decimal:
        """Calcular Return on Assets."""
        if balance.total_activos == 0:
            return Decimal('0.00')
        return (estado.utilidad_neta / balance.total_activos) * 100
    
    def _calcular_roe(self, estado: EstadoResultados, balance: BalanceGeneral) -> Decimal:
        """Calcular Return on Equity."""
        if balance.total_patrimonio == 0:
            return Decimal('0.00')
        return (estado.utilidad_neta / balance.total_patrimonio) * 100