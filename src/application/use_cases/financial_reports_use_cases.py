"""
Use Cases for Financial Reports.
Application layer use cases for Estado de Resultados and Balance General.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import time

from src.application.ports.interfaces import (
    EstadoResultadosRepository, BalanceGeneralRepository, 
    InformeFinancieroRepository, Logger, FileStorage
)
from src.application.dtos.financial_reports_dtos import (
    EstadoResultadosDTO, BalanceGeneralDTO, InformeFinancieroResumenDTO,
    FinancialReportRequestDTO, FinancialReportResponseDTO, PeriodoFiscalDTO
)
from src.domain.entities.financial_reports import (
    EstadoResultados, BalanceGeneral, PeriodoFiscal, InformeFinancieroResumen
)
from src.domain.services.financial_reports_service import (
    EstadoResultadosService, BalanceGeneralService, InformeFinancieroService
)


class GetEstadoResultadosUseCase:
    """
    Caso de uso para obtener el Estado de Resultados.
    Coordina la obtención de datos y generación del informe.
    """
    
    def __init__(
        self,
        repository: EstadoResultadosRepository,
        service: EstadoResultadosService,
        file_storage: FileStorage,
        logger: Logger
    ):
        self._repository = repository
        self._service = service
        self._file_storage = file_storage
        self._logger = logger
    
    def execute(self, request: FinancialReportRequestDTO) -> FinancialReportResponseDTO:
        """
        Ejecutar la generación del Estado de Resultados.
        
        Args:
            request: Solicitud con parámetros del informe
            
        Returns:
            Respuesta con el informe generado
        """
        start_time = time.time()
        
        try:
            self._logger.info(f"Iniciando generación de Estado de Resultados: {request.fecha_inicio} - {request.fecha_fin}")
            
            # Validar solicitud
            if not request.is_valid():
                return FinancialReportResponseDTO(
                    success=False,
                    message="Solicitud inválida: faltan fecha_inicio y fecha_fin para Estado de Resultados"
                )
            
            # Crear período fiscal
            periodo = PeriodoFiscal(
                fecha_inicio=datetime.strptime(request.fecha_inicio, "%Y-%m-%d"),
                fecha_fin=datetime.strptime(request.fecha_fin, "%Y-%m-%d"),
                nombre=f"Período {request.fecha_inicio} - {request.fecha_fin}",
                tipo_periodo="personalizado"
            )
            
            # Obtener datos del repositorio
            estado_resultados = self._repository.obtener_estado_resultados(periodo)
            
            # Convertir a DTO
            estado_dto = EstadoResultadosDTO.from_domain(estado_resultados)
            
            # Preparar respuesta de datos
            response_data = {
                "estado_resultados": estado_dto.to_dict(),
                "periodo": PeriodoFiscalDTO.from_domain(periodo).to_dict()
            }
            
            # Incluir KPIs si se solicita
            if request.incluir_kpis:
                response_data["kpis"] = {
                    "margen_bruto_porcentaje": estado_dto.margen_bruto_porcentaje,
                    "margen_neto_porcentaje": estado_dto.margen_neto_porcentaje,
                    "eficiencia_operativa": self._calcular_eficiencia_operativa(estado_dto),
                    "crecimiento_estimado": self._estimar_crecimiento(periodo)
                }
            
            # Guardar archivo si se requiere
            file_path = None
            if request.formato_salida in ['json', 'csv']:
                file_path = self._guardar_informe(response_data, periodo, request.formato_salida)
            
            execution_time = time.time() - start_time
            
            self._logger.info(f"Estado de Resultados generado exitosamente en {execution_time:.2f}s")
            
            return FinancialReportResponseDTO(
                success=True,
                message="Estado de Resultados generado exitosamente",
                data=response_data,
                file_path=file_path,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error generando Estado de Resultados: {str(e)}"
            self._logger.error(error_msg)
            
            return FinancialReportResponseDTO(
                success=False,
                message=error_msg,
                execution_time_seconds=execution_time
            )
    
    def _calcular_eficiencia_operativa(self, estado_dto: EstadoResultadosDTO) -> float:
        """Calcular indicador de eficiencia operativa."""
        if estado_dto.ventas_netas == 0:
            return 0.0
        return (estado_dto.gastos_operativos / estado_dto.ventas_netas) * 100
    
    def _estimar_crecimiento(self, periodo: PeriodoFiscal) -> float:
        """Estimar crecimiento (placeholder - requiere datos históricos)."""
        # Por ahora retorna 0, en implementación real compararía con período anterior
        return 0.0
    
    def _guardar_informe(self, data: Dict[str, Any], periodo: PeriodoFiscal, formato: str) -> str:
        """Guardar informe en archivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"estado_resultados_{periodo.nombre.replace(' ', '_')}_{timestamp}.{formato}"
        
        return self._file_storage.save_data(data, filename)


class GetBalanceGeneralUseCase:
    """
    Caso de uso para obtener el Balance General.
    """
    
    def __init__(
        self,
        repository: BalanceGeneralRepository,
        service: BalanceGeneralService,
        file_storage: FileStorage,
        logger: Logger
    ):
        self._repository = repository
        self._service = service
        self._file_storage = file_storage
        self._logger = logger
    
    def execute(self, request: FinancialReportRequestDTO) -> FinancialReportResponseDTO:
        """
        Ejecutar la generación del Balance General.
        
        Args:
            request: Solicitud con parámetros del informe
            
        Returns:
            Respuesta con el informe generado
        """
        start_time = time.time()
        
        try:
            self._logger.info(f"Iniciando generación de Balance General: {request.fecha_corte}")
            
            # Validar solicitud
            if not request.fecha_corte:
                return FinancialReportResponseDTO(
                    success=False,
                    message="Solicitud inválida: falta fecha_corte para Balance General"
                )
            
            # Convertir fecha de corte
            fecha_corte = datetime.strptime(request.fecha_corte, "%Y-%m-%d")
            
            # Obtener datos del repositorio
            balance_general = self._repository.obtener_balance_general(fecha_corte)
            
            # Convertir a DTO
            balance_dto = BalanceGeneralDTO.from_domain(balance_general)
            
            # Preparar respuesta de datos
            response_data = {
                "balance_general": balance_dto.to_dict()
            }
            
            # Incluir KPIs si se solicita
            if request.incluir_kpis:
                response_data["kpis"] = {
                    "ratio_liquidez": balance_dto.ratio_liquidez,
                    "ratio_endeudamiento": balance_dto.ratio_endeudamiento,
                    "solidez_patrimonial": self._calcular_solidez_patrimonial(balance_dto),
                    "capacidad_pago": self._calcular_capacidad_pago(balance_dto)
                }
            
            # Incluir detalles si se solicita
            if request.incluir_detalle:
                cuentas_balance = self._repository.obtener_balance_prueba(fecha_corte)
                response_data["detalle_cuentas"] = [cuenta.to_dict() for cuenta in cuentas_balance]
            
            # Guardar archivo si se requiere
            file_path = None
            if request.formato_salida in ['json', 'csv']:
                file_path = self._guardar_informe(response_data, fecha_corte, request.formato_salida)
            
            execution_time = time.time() - start_time
            
            self._logger.info(f"Balance General generado exitosamente en {execution_time:.2f}s")
            
            return FinancialReportResponseDTO(
                success=True,
                message="Balance General generado exitosamente",
                data=response_data,
                file_path=file_path,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error generando Balance General: {str(e)}"
            self._logger.error(error_msg)
            
            return FinancialReportResponseDTO(
                success=False,
                message=error_msg,
                execution_time_seconds=execution_time
            )
    
    def _calcular_solidez_patrimonial(self, balance_dto: BalanceGeneralDTO) -> float:
        """Calcular indicador de solidez patrimonial."""
        if balance_dto.total_activos == 0:
            return 0.0
        return (balance_dto.total_patrimonio / balance_dto.total_activos) * 100
    
    def _calcular_capacidad_pago(self, balance_dto: BalanceGeneralDTO) -> float:
        """Calcular capacidad de pago (activos/pasivos)."""
        if balance_dto.total_pasivos == 0:
            return float('inf')  # Sin pasivos = capacidad infinita
        return balance_dto.total_activos / balance_dto.total_pasivos
    
    def _guardar_informe(self, data: Dict[str, Any], fecha_corte: datetime, formato: str) -> str:
        """Guardar informe en archivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"balance_general_{fecha_corte.strftime('%Y%m%d')}_{timestamp}.{formato}"
        
        return self._file_storage.save_data(data, filename)


class GetInformeFinancieroCompletoUseCase:
    """
    Caso de uso para obtener informe financiero completo (Estado de Resultados + Balance General).
    """
    
    def __init__(
        self,
        repository: InformeFinancieroRepository,
        service: InformeFinancieroService,
        file_storage: FileStorage,
        logger: Logger
    ):
        self._repository = repository
        self._service = service
        self._file_storage = file_storage
        self._logger = logger
    
    def execute(self, request: FinancialReportRequestDTO) -> FinancialReportResponseDTO:
        """
        Ejecutar la generación del informe financiero completo.
        
        Args:
            request: Solicitud con parámetros del informe
            
        Returns:
            Respuesta con el informe completo generado
        """
        start_time = time.time()
        
        try:
            self._logger.info("Iniciando generación de informe financiero completo")
            
            # Validar solicitud
            if not (request.fecha_inicio and request.fecha_fin and request.fecha_corte):
                return FinancialReportResponseDTO(
                    success=False,
                    message="Solicitud inválida: faltan fechas requeridas para informe completo"
                )
            
            # Crear período fiscal
            periodo = PeriodoFiscal(
                fecha_inicio=datetime.strptime(request.fecha_inicio, "%Y-%m-%d"),
                fecha_fin=datetime.strptime(request.fecha_fin, "%Y-%m-%d"),
                nombre=f"Período {request.fecha_inicio} - {request.fecha_fin}",
                tipo_periodo="personalizado"
            )
            
            fecha_corte_balance = datetime.strptime(request.fecha_corte, "%Y-%m-%d")
            
            # Obtener informe completo del repositorio
            informe_completo = self._repository.generar_informe_completo(periodo, fecha_corte_balance)
            
            # Convertir a DTO
            informe_dto = InformeFinancieroResumenDTO.from_domain(informe_completo)
            
            # Preparar respuesta de datos
            response_data = informe_dto.to_dict()
            
            # Agregar análisis adicional
            response_data["analisis_financiero"] = self._generar_analisis_financiero(informe_dto)
            
            # Guardar archivo si se requiere
            file_path = None
            if request.formato_salida in ['json', 'csv']:
                file_path = self._guardar_informe(response_data, periodo, request.formato_salida)
            
            execution_time = time.time() - start_time
            
            self._logger.info(f"Informe financiero completo generado exitosamente en {execution_time:.2f}s")
            
            return FinancialReportResponseDTO(
                success=True,
                message="Informe financiero completo generado exitosamente",
                data=response_data,
                file_path=file_path,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error generando informe completo: {str(e)}"
            self._logger.error(error_msg)
            
            return FinancialReportResponseDTO(
                success=False,
                message=error_msg,
                execution_time_seconds=execution_time
            )
    
    def _generar_analisis_financiero(self, informe_dto: InformeFinancieroResumenDTO) -> Dict[str, Any]:
        """Generar análisis financiero basado en los KPIs."""
        
        kpis = informe_dto.kpis_principales
        
        # Análisis de rentabilidad
        rentabilidad_estado = "Excelente" if kpis["margen_neto"] > 15 else \
                             "Bueno" if kpis["margen_neto"] > 8 else \
                             "Regular" if kpis["margen_neto"] > 3 else "Bajo"
        
        # Análisis de liquidez
        liquidez_estado = "Excelente" if kpis["ratio_liquidez"] > 2 else \
                         "Bueno" if kpis["ratio_liquidez"] > 1.5 else \
                         "Aceptable" if kpis["ratio_liquidez"] > 1 else "Crítico"
        
        # Análisis de endeudamiento
        endeudamiento_estado = "Bajo" if kpis["ratio_endeudamiento"] < 0.3 else \
                              "Moderado" if kpis["ratio_endeudamiento"] < 0.6 else \
                              "Alto" if kpis["ratio_endeudamiento"] < 0.8 else "Crítico"
        
        return {
            "resumen_ejecutivo": {
                "rentabilidad": {
                    "estado": rentabilidad_estado,
                    "margen_neto": kpis["margen_neto"],
                    "recomendacion": self._get_recomendacion_rentabilidad(kpis["margen_neto"])
                },
                "liquidez": {
                    "estado": liquidez_estado,
                    "ratio": kpis["ratio_liquidez"],
                    "recomendacion": self._get_recomendacion_liquidez(kpis["ratio_liquidez"])
                },
                "endeudamiento": {
                    "estado": endeudamiento_estado,
                    "ratio": kpis["ratio_endeudamiento"],
                    "recomendacion": self._get_recomendacion_endeudamiento(kpis["ratio_endeudamiento"])
                }
            },
            "coherencia_informes": informe_dto.coherencia_informes,
            "alertas": self._generar_alertas(kpis)
        }
    
    def _get_recomendacion_rentabilidad(self, margen_neto: float) -> str:
        """Generar recomendación basada en margen neto."""
        if margen_neto > 15:
            return "Excelente rentabilidad. Mantener estrategia actual."
        elif margen_neto > 8:
            return "Buena rentabilidad. Explorar oportunidades de optimización."
        elif margen_neto > 3:
            return "Rentabilidad regular. Revisar estructura de costos y gastos."
        else:
            return "Rentabilidad baja. Urgente revisión de modelo de negocio."
    
    def _get_recomendacion_liquidez(self, ratio_liquidez: float) -> str:
        """Generar recomendación basada en ratio de liquidez."""
        if ratio_liquidez > 2:
            return "Excelente liquidez. Considerar inversiones productivas."
        elif ratio_liquidez > 1.5:
            return "Buena liquidez. Posición financiera sólida."
        elif ratio_liquidez > 1:
            return "Liquidez aceptable. Monitorear flujo de caja."
        else:
            return "Liquidez crítica. Urgente mejora en gestión de efectivo."
    
    def _get_recomendacion_endeudamiento(self, ratio_endeudamiento: float) -> str:
        """Generar recomendación basada en ratio de endeudamiento."""
        if ratio_endeudamiento < 0.3:
            return "Bajo endeudamiento. Capacidad para apalancamiento si es necesario."
        elif ratio_endeudamiento < 0.6:
            return "Endeudamiento moderado. Mantener control sobre nuevas deudas."
        elif ratio_endeudamiento < 0.8:
            return "Alto endeudamiento. Priorizar reducción de pasivos."
        else:
            return "Endeudamiento crítico. Urgente reestructuración financiera."
    
    def _generar_alertas(self, kpis: Dict[str, float]) -> List[str]:
        """Generar alertas basadas en KPIs críticos."""
        alertas = []
        
        if kpis["margen_neto"] < 3:
            alertas.append("⚠️ Margen neto crítico (<3%). Revisar urgentemente estructura de costos.")
        
        if kpis["ratio_liquidez"] < 1:
            alertas.append("⚠️ Ratio de liquidez crítico (<1.0). Problemas potenciales de flujo de caja.")
        
        if kpis["ratio_endeudamiento"] > 0.8:
            alertas.append("⚠️ Nivel de endeudamiento crítico (>80%). Alto riesgo financiero.")
        
        if kpis["roa"] < 5:
            alertas.append("⚠️ ROA bajo (<5%). Los activos no generan suficiente rentabilidad.")
        
        if kpis["roe"] < 10:
            alertas.append("⚠️ ROE bajo (<10%). Baja rentabilidad sobre el patrimonio.")
        
        return alertas
    
    def _guardar_informe(self, data: Dict[str, Any], periodo: PeriodoFiscal, formato: str) -> str:
        """Guardar informe completo en archivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"informe_financiero_completo_{periodo.nombre.replace(' ', '_')}_{timestamp}.{formato}"
        
        return self._file_storage.save_data(data, filename)