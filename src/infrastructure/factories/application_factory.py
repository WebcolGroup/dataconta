"""
Application Factory - Infrastructure Layer
Factory para crear la aplicación completa con todas las dependencias inyectadas.
Implementa el patrón Factory siguiendo principios de arquitectura hexagonal.
"""

import logging
from typing import Optional

# Domain Services
from src.domain.services.kpi_service import KPICalculationServiceImpl, KPIAnalysisService

# Application Services
from src.application.services.kpi_service import KPIApplicationService
from src.application.services.export_service import ExportService

# Infrastructure Adapters
from src.infrastructure.adapters.free_gui_siigo_adapter import FreeGUISiigoAdapter
from src.infrastructure.adapters.file_storage_adapter import FileStorageAdapter
from src.infrastructure.adapters.logger_adapter import LoggerAdapter

# Presentation Layer
from src.presentation.controllers.free_gui_controller import FreeGUIController

# Note: DataContaMainWindow will be injected as parameter to avoid circular imports


class DataContaApplicationFactory:
    """
    Factory para crear la aplicación completa con arquitectura hexagonal.
    Implementa inyección de dependencias siguiendo principios SOLID.
    """
    
    @classmethod
    def create_controller_for_main_window(cls):
        """
        Crear controlador configurado para inyectar en la ventana principal.
        
        Returns:
            Controller configurado con todas las dependencias
        """
        # 1. Crear adaptadores de infraestructura (Outside -> Inside)
        logger = cls._create_logger()
        file_storage = cls._create_file_storage(logger)
        invoice_repository = cls._create_invoice_repository(logger)
        
        # 2. Crear servicios de dominio (Core)
        kpi_calculation_service = cls._create_kpi_calculation_service()
        kpi_analysis_service = cls._create_kpi_analysis_service(kpi_calculation_service)
        
        # 3. Crear servicios de aplicación (Application Layer)
        kpi_service = cls._create_kpi_application_service(
            invoice_repository, file_storage, kpi_calculation_service, kpi_analysis_service, logger
        )
        export_service = cls._create_export_service(invoice_repository, file_storage, logger)
        
        # 4. Crear controlador (Presentation Layer)
        controller = cls._create_controller(
            kpi_service, export_service, invoice_repository, logger, file_storage
        )

        logger.info("✅ Controller creado exitosamente con arquitectura hexagonal")
        
        return controller
    
    @classmethod
    def _create_logger(cls) -> LoggerAdapter:
        """Crear adaptador de logging."""
        logging.basicConfig(level=logging.INFO)
        return LoggerAdapter(name="dataconta_refactored")
    
    @classmethod
    def _create_file_storage(cls, logger: LoggerAdapter) -> FileStorageAdapter:
        """Crear adaptador de almacenamiento de archivos."""
        return FileStorageAdapter(output_directory="./outputs", logger=logger)
    
    @classmethod
    def _create_invoice_repository(cls, logger: LoggerAdapter) -> FreeGUISiigoAdapter:
        """Crear repositorio de facturas."""
        return FreeGUISiigoAdapter(logger=logger)
    
    @classmethod
    def _create_kpi_calculation_service(cls) -> KPICalculationServiceImpl:
        """Crear servicio de dominio para cálculo de KPIs."""
        return KPICalculationServiceImpl()
    
    @classmethod
    def _create_kpi_analysis_service(cls, kpi_calculation_service: KPICalculationServiceImpl) -> KPIAnalysisService:
        """Crear servicio de dominio para análisis de KPIs."""
        return KPIAnalysisService(kpi_calculation_service)
    
    @classmethod
    def _create_kpi_application_service(cls, 
                                       invoice_repository: FreeGUISiigoAdapter,
                                       file_storage: FileStorageAdapter,
                                       kpi_calculation_service: KPICalculationServiceImpl,
                                       kpi_analysis_service: KPIAnalysisService,
                                       logger: LoggerAdapter) -> KPIApplicationService:
        """Crear servicio de aplicación para KPIs."""
        return KPIApplicationService(
            invoice_repository=invoice_repository,
            file_storage=file_storage,
            kpi_calculation_service=kpi_calculation_service,
            kpi_analysis_service=kpi_analysis_service,
            logger=logger
        )
    
    @classmethod
    def _create_export_service(cls, 
                              invoice_repository: FreeGUISiigoAdapter,
                              file_storage: FileStorageAdapter,
                              logger: LoggerAdapter) -> ExportService:
        """Crear servicio de exportación."""
        return ExportService(
            invoice_repository=invoice_repository,
            file_storage=file_storage,
            logger=logger
        )
    
    @classmethod
    def _create_controller(cls,
                          kpi_service: KPIApplicationService,
                          export_service: ExportService,
                          invoice_repository: FreeGUISiigoAdapter,
                          logger: LoggerAdapter,
                          file_storage: FileStorageAdapter) -> FreeGUIController:
        """Crear controlador de presentación."""
        return FreeGUIController(
            kpi_service=kpi_service,
            export_service=export_service,
            invoice_repository=invoice_repository,
            logger=logger,
            file_storage=file_storage
        )
    
    @classmethod
    def create_addon_system(cls, logger: Optional[LoggerAdapter] = None) -> Optional[object]:
        """
        Crear sistema de addons (opcional).
        
        Args:
            logger: Logger opcional para el sistema de addons
            
        Returns:
            Sistema de addons o None si no está disponible
        """
        try:
            from src.infrastructure.factories.addon_factory import AddonFactory
            
            if logger is None:
                logger = cls._create_logger()
            
            return AddonFactory.create_complete_addon_system(
                repository_path="addons/",
                logger=logger
            )
            
        except ImportError:
            # Sistema de addons no disponible
            return None
        except Exception as e:
            if logger:
                logger.warning(f"⚠️  No se pudo inicializar sistema de addons: {e}")
            return None


class DependencyContainer:
    """
    Contenedor de dependencias para casos de uso específicos.
    Útil para testing y configuraciones especiales.
    """
    
    def __init__(self):
        self._instances = {}
        self._singletons = {}
    
    def register_singleton(self, interface: type, implementation: object) -> None:
        """Registrar una instancia como singleton."""
        self._singletons[interface] = implementation
    
    def register_factory(self, interface: type, factory_func: callable) -> None:
        """Registrar una factory function para crear instancias."""
        self._instances[interface] = factory_func
    
    def get(self, interface: type) -> object:
        """Obtener instancia del contenedor."""
        # Verificar singletons primero
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Crear nueva instancia usando factory
        if interface in self._instances:
            instance = self._instances[interface]()
            return instance
        
        raise ValueError(f"No hay registro para {interface}")
    
    def create_for_testing(self):
        """
        Crear controller con mocks para testing.
        
        Returns:
            Controller con dependencias mockeadas
        """
        # Esta implementación se completaría para testing
        # Por ahora, delegamos al factory principal
        return DataContaApplicationFactory.create_main_window()