"""
Financial Reports Service Facade.
Application service that coordinates financial report generation.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from src.application.ports.interfaces import Logger, FileStorage
from src.application.use_cases.financial_reports_use_cases import (
    GetEstadoResultadosUseCase, GetBalanceGeneralUseCase, 
    GetInformeFinancieroCompletoUseCase
)
from src.application.dtos.financial_reports_dtos import (
    FinancialReportRequestDTO, FinancialReportResponseDTO
)


class FinancialReportsService:
    """
    Servicio de fachada para informes financieros.
    Coordina la ejecución de todos los casos de uso relacionados.
    """
    
    def __init__(
        self,
        estado_resultados_use_case: GetEstadoResultadosUseCase,
        balance_general_use_case: GetBalanceGeneralUseCase,
        informe_completo_use_case: GetInformeFinancieroCompletoUseCase,
        logger: Logger
    ):
        """
        Inicializar servicio de fachada.
        
        Args:
            estado_resultados_use_case: Caso de uso para Estado de Resultados
            balance_general_use_case: Caso de uso para Balance General
            informe_completo_use_case: Caso de uso para informe completo
            logger: Logger para registrar operaciones
        """
        self._estado_resultados_use_case = estado_resultados_use_case
        self._balance_general_use_case = balance_general_use_case
        self._informe_completo_use_case = informe_completo_use_case
        self._logger = logger
    
    def generar_estado_resultados(
        self,
        fecha_inicio: str,
        fecha_fin: str,
        formato_salida: str = "json",
        incluir_kpis: bool = True
    ) -> FinancialReportResponseDTO:
        """
        Generar Estado de Resultados.
        
        Args:
            fecha_inicio: Fecha inicio del período (YYYY-MM-DD)
            fecha_fin: Fecha fin del período (YYYY-MM-DD)
            formato_salida: Formato de salida ('json', 'csv')
            incluir_kpis: Si incluir KPIs calculados
            
        Returns:
            Respuesta con el Estado de Resultados generado
        """
        self._logger.info(f"Solicitando Estado de Resultados para período {fecha_inicio} - {fecha_fin}")
        
        request = FinancialReportRequestDTO(
            tipo_informe="estado_resultados",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            formato_salida=formato_salida,
            incluir_kpis=incluir_kpis
        )
        
        return self._estado_resultados_use_case.execute(request)
    
    def generar_balance_general(
        self,
        fecha_corte: str,
        formato_salida: str = "json",
        incluir_kpis: bool = True,
        incluir_detalle: bool = False
    ) -> FinancialReportResponseDTO:
        """
        Generar Balance General.
        
        Args:
            fecha_corte: Fecha de corte (YYYY-MM-DD)
            formato_salida: Formato de salida ('json', 'csv')
            incluir_kpis: Si incluir KPIs calculados
            incluir_detalle: Si incluir detalle de cuentas
            
        Returns:
            Respuesta con el Balance General generado
        """
        self._logger.info(f"Solicitando Balance General para fecha {fecha_corte}")
        
        request = FinancialReportRequestDTO(
            tipo_informe="balance_general",
            fecha_corte=fecha_corte,
            formato_salida=formato_salida,
            incluir_kpis=incluir_kpis,
            incluir_detalle=incluir_detalle
        )
        
        return self._balance_general_use_case.execute(request)
    
    def generar_informe_completo(
        self,
        fecha_inicio: str,
        fecha_fin: str,
        fecha_corte_balance: str,
        formato_salida: str = "json"
    ) -> FinancialReportResponseDTO:
        """
        Generar informe financiero completo.
        
        Args:
            fecha_inicio: Fecha inicio para Estado de Resultados (YYYY-MM-DD)
            fecha_fin: Fecha fin para Estado de Resultados (YYYY-MM-DD)
            fecha_corte_balance: Fecha corte para Balance General (YYYY-MM-DD)
            formato_salida: Formato de salida ('json', 'csv')
            
        Returns:
            Respuesta con el informe completo generado
        """
        self._logger.info("Solicitando informe financiero completo")
        
        request = FinancialReportRequestDTO(
            tipo_informe="completo",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            fecha_corte=fecha_corte_balance,
            formato_salida=formato_salida,
            incluir_kpis=True,
            incluir_detalle=False
        )
        
        return self._informe_completo_use_case.execute(request)
    
    def validar_parametros_estado_resultados(
        self,
        fecha_inicio: str,
        fecha_fin: str
    ) -> Dict[str, Any]:
        """
        Validar parámetros para Estado de Resultados.
        
        Args:
            fecha_inicio: Fecha inicio (YYYY-MM-DD)
            fecha_fin: Fecha fin (YYYY-MM-DD)
            
        Returns:
            Diccionario con resultado de validación
        """
        errors = []
        
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        except ValueError:
            errors.append("Fecha inicio inválida. Use formato YYYY-MM-DD")
            fecha_inicio_dt = None
        
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        except ValueError:
            errors.append("Fecha fin inválida. Use formato YYYY-MM-DD")
            fecha_fin_dt = None
        
        if fecha_inicio_dt and fecha_fin_dt:
            if fecha_inicio_dt > fecha_fin_dt:
                errors.append("Fecha inicio no puede ser posterior a fecha fin")
            
            # Validar que no sea un período muy largo (más de 2 años)
            if (fecha_fin_dt - fecha_inicio_dt).days > 730:
                errors.append("Período muy largo. Máximo 2 años permitidos")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "fecha_inicio_parsed": fecha_inicio_dt,
            "fecha_fin_parsed": fecha_fin_dt
        }
    
    def validar_parametros_balance_general(self, fecha_corte: str) -> Dict[str, Any]:
        """
        Validar parámetros para Balance General.
        
        Args:
            fecha_corte: Fecha de corte (YYYY-MM-DD)
            
        Returns:
            Diccionario con resultado de validación
        """
        errors = []
        
        try:
            fecha_corte_dt = datetime.strptime(fecha_corte, "%Y-%m-%d")
        except ValueError:
            errors.append("Fecha corte inválida. Use formato YYYY-MM-DD")
            fecha_corte_dt = None
        
        if fecha_corte_dt:
            # Validar que no sea una fecha futura
            if fecha_corte_dt > datetime.now():
                errors.append("Fecha de corte no puede ser futura")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "fecha_corte_parsed": fecha_corte_dt
        }
    
    def get_formatos_disponibles(self) -> List[str]:
        """Obtener formatos de salida disponibles."""
        return ["json", "csv"]
    
    def get_tipos_periodo_sugeridos(self) -> Dict[str, Dict[str, str]]:
        """
        Obtener períodos sugeridos comunes.
        
        Returns:
            Diccionario con períodos predefinidos
        """
        now = datetime.now()
        
        # Período actual
        inicio_mes = now.replace(day=1)
        
        # Año actual
        inicio_año = now.replace(month=1, day=1)
        
        # Año anterior
        inicio_año_anterior = datetime(now.year - 1, 1, 1)
        fin_año_anterior = datetime(now.year - 1, 12, 31)
        
        return {
            "mes_actual": {
                "nombre": f"{now.strftime('%B %Y')}",
                "fecha_inicio": inicio_mes.strftime("%Y-%m-%d"),
                "fecha_fin": now.strftime("%Y-%m-%d")
            },
            "año_actual": {
                "nombre": f"Año {now.year}",
                "fecha_inicio": inicio_año.strftime("%Y-%m-%d"),
                "fecha_fin": now.strftime("%Y-%m-%d")
            },
            "año_anterior": {
                "nombre": f"Año {now.year - 1}",
                "fecha_inicio": inicio_año_anterior.strftime("%Y-%m-%d"),
                "fecha_fin": fin_año_anterior.strftime("%Y-%m-%d")
            }
        }
    
    def get_fechas_corte_sugeridas(self) -> Dict[str, str]:
        """
        Obtener fechas de corte sugeridas para Balance General.
        
        Returns:
            Diccionario con fechas predefinidas
        """
        now = datetime.now()
        
        # Fin del mes anterior
        if now.month == 1:
            fin_mes_anterior = datetime(now.year - 1, 12, 31)
        else:
            import calendar
            dia_anterior = calendar.monthrange(now.year, now.month - 1)[1]
            fin_mes_anterior = datetime(now.year, now.month - 1, dia_anterior)
        
        # Fin del año anterior
        fin_año_anterior = datetime(now.year - 1, 12, 31)
        
        return {
            "hoy": now.strftime("%Y-%m-%d"),
            "fin_mes_anterior": fin_mes_anterior.strftime("%Y-%m-%d"),
            "fin_año_anterior": fin_año_anterior.strftime("%Y-%m-%d")
        }