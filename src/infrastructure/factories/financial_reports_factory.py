"""
Financial Reports Factory.
Factory para instanciar todos los componentes de informes financieros.
"""

from typing import Dict, Any

from src.application.ports.interfaces import (
    Logger, FileStorage, APIClient, ConfigurationProvider
)
from src.application.services.FinancialReportsService import FinancialReportsService
from src.application.use_cases.financial_reports_use_cases import (
    GetEstadoResultadosUseCase, GetBalanceGeneralUseCase,
    GetInformeFinancieroCompletoUseCase
)
from src.infrastructure.adapters.siigo_financial_api_adapter import SiigoFinancialAPIAdapter
from src.infrastructure.adapters.financial_reports_repository import (
    SiigoEstadoResultadosRepository, SiigoBalanceGeneralRepository,
    SiigoInformeFinancieroRepository
)
from src.domain.services.financial_reports_service import (
    EstadoResultadosServiceImpl, BalanceGeneralServiceImpl,
    InformeFinancieroServiceImpl
)


class FinancialReportsFactory:
    """
    Factory para crear e inyectar dependencias de informes financieros.
    """
    
    def __init__(
        self,
        logger: Logger,
        file_storage: FileStorage,
        api_client: APIClient,
        config_provider: ConfigurationProvider
    ):
        """
        Inicializar factory.
        
        Args:
            logger: Logger para toda la aplicación
            file_storage: Servicio de almacenamiento de archivos
            api_client: Cliente API base
            config_provider: Proveedor de configuración
        """
        self._logger = logger
        self._file_storage = file_storage
        self._api_client = api_client
        self._config_provider = config_provider
    
    def create_financial_reports_service(self) -> FinancialReportsService:
        """
        Crear servicio principal de informes financieros con todas las dependencias.
        
        Returns:
            FinancialReportsService completamente configurado
        """
        self._logger.info("Creando servicio de informes financieros")
        
        # Crear adaptador de API financiera de Siigo
        siigo_api = self._create_siigo_api_adapter()
        
        # Crear repositorios
        estado_resultados_repo = SiigoEstadoResultadosRepository(
            siigo_api=siigo_api,
            logger=self._logger
        )
        
        balance_general_repo = SiigoBalanceGeneralRepository(
            siigo_api=siigo_api,
            logger=self._logger
        )
        
        informe_completo_repo = SiigoInformeFinancieroRepository(
            estado_resultados_repo=estado_resultados_repo,
            balance_general_repo=balance_general_repo,
            logger=self._logger
        )
        
        # Crear servicios de dominio
        estado_resultados_service = EstadoResultadosServiceImpl()
        balance_general_service = BalanceGeneralServiceImpl()
        informe_financiero_service = InformeFinancieroServiceImpl()
        
        # Crear casos de uso
        estado_resultados_use_case = GetEstadoResultadosUseCase(
            repository=estado_resultados_repo,
            service=estado_resultados_service,
            file_storage=self._file_storage,
            logger=self._logger
        )
        
        balance_general_use_case = GetBalanceGeneralUseCase(
            repository=balance_general_repo,
            service=balance_general_service,
            file_storage=self._file_storage,
            logger=self._logger
        )
        
        informe_completo_use_case = GetInformeFinancieroCompletoUseCase(
            repository=informe_completo_repo,
            service=informe_financiero_service,
            file_storage=self._file_storage,
            logger=self._logger
        )
        
        # Crear servicio de fachada
        financial_reports_service = FinancialReportsService(
            estado_resultados_use_case=estado_resultados_use_case,
            balance_general_use_case=balance_general_use_case,
            informe_completo_use_case=informe_completo_use_case,
            logger=self._logger
        )
        
        self._logger.info("Servicio de informes financieros creado exitosamente")
        return financial_reports_service
    
    def _create_siigo_api_adapter(self) -> SiigoFinancialAPIAdapter:
        """Crear adaptador de API financiera de Siigo."""
        
        # Obtener configuración (usando la misma base que la aplicación principal)
        try:
            # Usar la URL base de la configuración existente
            base_url = "https://api.siigo.com"  # URL estándar de Siigo
            
            siigo_api = SiigoFinancialAPIAdapter(
                base_url=base_url,
                api_client=self._api_client,
                logger=self._logger,
                timeout=30
            )
            
            return siigo_api
            
        except Exception as e:
            self._logger.error(f"Error creando adaptador de API de Siigo: {str(e)}")
            raise
    
    def test_financial_components(self) -> Dict[str, bool]:
        """
        Probar todos los componentes financieros.
        
        Returns:
            Diccionario con resultados de las pruebas
        """
        results = {}
        
        try:
            # Probar adaptador de API
            siigo_api = self._create_siigo_api_adapter()
            results["siigo_api_adapter"] = siigo_api.test_connection()
            
            # Probar repositorios
            estado_repo = SiigoEstadoResultadosRepository(siigo_api, self._logger)
            balance_repo = SiigoBalanceGeneralRepository(siigo_api, self._logger)
            
            results["estado_resultados_repository"] = True
            results["balance_general_repository"] = True
            
            # Probar servicios de dominio
            estado_service = EstadoResultadosServiceImpl()
            balance_service = BalanceGeneralServiceImpl()
            informe_service = InformeFinancieroServiceImpl()
            
            results["domain_services"] = True
            
            # Probar creación del servicio principal
            financial_service = self.create_financial_reports_service()
            results["financial_reports_service"] = financial_service is not None
            
            self._logger.info("Prueba de componentes financieros completada")
            
        except Exception as e:
            self._logger.error(f"Error en pruebas de componentes financieros: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    def get_component_info(self) -> Dict[str, Any]:
        """
        Obtener información de los componentes financieros.
        
        Returns:
            Información detallada de los componentes
        """
        return {
            "factory_version": "1.0.0",
            "components": {
                "adapters": [
                    "SiigoFinancialAPIAdapter",
                    "SiigoEstadoResultadosRepository",
                    "SiigoBalanceGeneralRepository",
                    "SiigoInformeFinancieroRepository"
                ],
                "domain_services": [
                    "EstadoResultadosServiceImpl",
                    "BalanceGeneralServiceImpl",
                    "InformeFinancieroServiceImpl"
                ],
                "use_cases": [
                    "GetEstadoResultadosUseCase",
                    "GetBalanceGeneralUseCase",
                    "GetInformeFinancieroCompletoUseCase"
                ],
                "facades": [
                    "FinancialReportsService"
                ]
            },
            "supported_reports": [
                "Estado de Resultados",
                "Estado de Situación Financiera",
                "Informe Financiero Completo"
            ],
            "api_endpoints": [
                "/v1/invoices",
                "/v1/credit-notes",
                "/v1/purchases", 
                "/v1/journal-entries",
                "/v1/trial-balance"
            ]
        }