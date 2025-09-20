"""
Addon Factory
Factory para crear e inyectar todas las dependencias del sistema de addons.
Sigue principios SOLID y arquitectura hexagonal.
"""

from typing import Any, Dict, Optional

from src.application.ports.addon_interfaces import (
    AddonManager, AddonRepository, AddonLoader, AddonRegistry, AddonContext
)
from src.application.ports.interfaces import Logger
from src.infrastructure.adapters.addon_manager_adapter import (
    AddonManagerImpl, FileSystemAddonRepository, 
    DynamicAddonLoader, InMemoryAddonRegistry
)


class AddonFactory:
    """
    Factory para crear e inyectar todas las dependencias del sistema de addons.
    
    Implementa el patrón Factory siguiendo arquitectura hexagonal:
    - Crea implementaciones concretas de los puertos
    - Inyecta dependencias siguiendo principio de inversión de dependencias
    - Mantiene el core limpio de detalles de implementación
    """
    
    def __init__(
        self,
        logger: Logger,
        main_window: Any = None,
        controller: Any = None,
        kpi_service: Any = None,
        export_service: Any = None,
        file_storage: Any = None,
        addons_path: str = "addons",
        dataconta_version: str = "3.0.0"
    ):
        """
        Inicializar factory con dependencias principales.
        
        Args:
            logger: Logger para toda la aplicación
            main_window: Referencia a ventana principal (opcional)
            controller: Controlador principal (opcional)
            kpi_service: Servicio de KPIs (opcional)
            export_service: Servicio de exportación (opcional)
            file_storage: Servicio de almacenamiento (opcional)
            addons_path: Path donde buscar addons
            dataconta_version: Versión actual de DataConta
        """
        self._logger = logger
        self._main_window = main_window
        self._controller = controller
        self._kpi_service = kpi_service
        self._export_service = export_service
        self._file_storage = file_storage
        self._addons_path = addons_path
        self._dataconta_version = dataconta_version
        
        # Instancias singleton de componentes
        self._repository: Optional[AddonRepository] = None
        self._loader: Optional[AddonLoader] = None
        self._registry: Optional[AddonRegistry] = None
        self._manager: Optional[AddonManager] = None
        self._context: Optional[AddonContext] = None
        
    def create_addon_repository(self) -> AddonRepository:
        """
        Crear repositorio de addons.
        
        Returns:
            AddonRepository: Implementación concreta del repositorio
        """
        if self._repository is None:
            self._repository = FileSystemAddonRepository(
                addons_path=self._addons_path,
                logger=self._logger
            )
            self._logger.info("✅ AddonRepository creado (FileSystem)")
            
        return self._repository
    
    def create_addon_loader(self) -> AddonLoader:
        """
        Crear cargador de addons.
        
        Returns:
            AddonLoader: Implementación concreta del cargador
        """
        if self._loader is None:
            self._loader = DynamicAddonLoader(
                logger=self._logger
            )
            self._logger.info("✅ AddonLoader creado (Dynamic)")
            
        return self._loader
    
    def create_addon_registry(self) -> AddonRegistry:
        """
        Crear registro de addons.
        
        Returns:
            AddonRegistry: Implementación concreta del registro
        """
        if self._registry is None:
            self._registry = InMemoryAddonRegistry(
                logger=self._logger
            )
            self._logger.info("✅ AddonRegistry creado (InMemory)")
            
        return self._registry
    
    def create_addon_context(self) -> AddonContext:
        """
        Crear contexto para addons.
        
        Returns:
            AddonContext: Contexto con todas las dependencias disponibles
        """
        if self._context is None:
            self._context = AddonContext(
                main_window=self._main_window,
                controller=self._controller,
                logger=self._logger,
                kpi_service=self._kpi_service,
                export_service=self._export_service,
                file_storage=self._file_storage,
                app_config=self._get_app_config(),
                addon_config={},
                show_message=self._create_show_message_callback(),
                show_error=self._create_show_error_callback(),
                add_menu_item=self._create_add_menu_item_callback()
            )
            self._logger.info("✅ AddonContext creado con todas las dependencias")
            
        return self._context
    
    def create_addon_manager(self) -> AddonManager:
        """
        Crear gestor principal de addons.
        
        Returns:
            AddonManager: Implementación completa del gestor
        """
        if self._manager is None:
            # Crear todas las dependencias
            repository = self.create_addon_repository()
            loader = self.create_addon_loader()
            registry = self.create_addon_registry()
            context = self.create_addon_context()
            
            # Crear el gestor con todas las dependencias inyectadas
            self._manager = AddonManagerImpl(
                repository=repository,
                loader=loader,
                registry=registry,
                context=context,
                dataconta_version=self._dataconta_version,
                logger=self._logger
            )
            
            self._logger.info("✅ AddonManager creado con todas las dependencias inyectadas")
            
        return self._manager
    
    def create_complete_addon_system(self) -> AddonManager:
        """
        Crear sistema completo de addons con inicialización.
        
        Returns:
            AddonManager: Gestor completamente inicializado
        """
        try:
            self._logger.info("🔌 Inicializando sistema completo de addons...")
            
            # Crear gestor
            manager = self.create_addon_manager()
            
            # Escanear addons disponibles
            addon_count = manager.scan_addons()
            self._logger.info(f"📦 {addon_count} addons encontrados")
            
            # Auto-cargar addons habilitados (opcional)
            self._auto_load_enabled_addons(manager)
            
            self._logger.info("✅ Sistema de addons inicializado completamente")
            return manager
            
        except Exception as e:
            self._logger.error(f"❌ Error inicializando sistema de addons: {e}")
            raise
    
    def _get_app_config(self) -> Dict[str, Any]:
        """Obtener configuración de la aplicación."""
        return {
            'version': self._dataconta_version,
            'addons_path': self._addons_path,
            'logging_enabled': True,
            'debug_mode': False
        }
    
    def _create_show_message_callback(self):
        """Crear callback para mostrar mensajes."""
        def show_message(title: str, message: str):
            try:
                if self._main_window and hasattr(self._main_window, 'show_success_message'):
                    # Usar método de la ventana principal si está disponible
                    self._main_window.show_success_message(title, message)
                else:
                    # Fallback a logging
                    self._logger.info(f"{title}: {message}")
            except Exception as e:
                self._logger.error(f"Error mostrando mensaje: {e}")
                
        return show_message
    
    def _create_show_error_callback(self):
        """Crear callback para mostrar errores."""
        def show_error(title: str, message: str):
            try:
                if self._main_window and hasattr(self._main_window, 'show_error_message'):
                    # Usar método de la ventana principal si está disponible
                    self._main_window.show_error_message(title, message)
                else:
                    # Fallback a logging
                    self._logger.error(f"{title}: {message}")
            except Exception as e:
                self._logger.error(f"Error mostrando error: {e}")
                
        return show_error
    
    def _create_add_menu_item_callback(self):
        """Crear callback para agregar items de menú."""
        def add_menu_item(menu_item: Dict[str, Any]) -> bool:
            try:
                # TODO: Integrar con sistema de menús dinámicos cuando esté disponible
                if self._main_window and hasattr(self._main_window, 'add_menu_item'):
                    return self._main_window.add_menu_item(menu_item)
                else:
                    # Por ahora solo loggear
                    self._logger.info(f"Menu item solicitado: {menu_item}")
                    return True
            except Exception as e:
                self._logger.error(f"Error agregando menu item: {e}")
                return False
                
        return add_menu_item
    
    def _auto_load_enabled_addons(self, manager: AddonManager):
        """Auto-cargar addons que estén marcados como habilitados."""
        try:
            # TODO: Implementar lógica de auto-carga basada en configuración
            # Por ahora, intentar cargar todos los addons encontrados
            loaded_addons = manager.get_loaded_addons()
            self._logger.info(f"📦 Auto-carga completada. {len(loaded_addons)} addons cargados")
            
        except Exception as e:
            self._logger.error(f"Error en auto-carga de addons: {e}")
    
    def update_dependencies(
        self,
        main_window: Any = None,
        controller: Any = None,
        kpi_service: Any = None,
        export_service: Any = None,
        file_storage: Any = None
    ):
        """
        Actualizar dependencias del factory.
        
        Args:
            main_window: Nueva referencia a ventana principal
            controller: Nuevo controlador
            kpi_service: Nuevo servicio de KPIs
            export_service: Nuevo servicio de exportación
            file_storage: Nuevo servicio de almacenamiento
        """
        if main_window is not None:
            self._main_window = main_window
            
        if controller is not None:
            self._controller = controller
            
        if kpi_service is not None:
            self._kpi_service = kpi_service
            
        if export_service is not None:
            self._export_service = export_service
            
        if file_storage is not None:
            self._file_storage = file_storage
        
        # Invalidar contexto para que se regenere con nuevas dependencias
        self._context = None
        
        self._logger.info("🔄 Dependencias del AddonFactory actualizadas")
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Obtener información del sistema de addons.
        
        Returns:
            Dict con información del estado del sistema
        """
        try:
            info = {
                'factory_version': '1.0.0',
                'dataconta_version': self._dataconta_version,
                'addons_path': self._addons_path,
                'components_created': {
                    'repository': self._repository is not None,
                    'loader': self._loader is not None,
                    'registry': self._registry is not None,
                    'manager': self._manager is not None,
                    'context': self._context is not None
                },
                'dependencies': {
                    'logger': self._logger is not None,
                    'main_window': self._main_window is not None,
                    'controller': self._controller is not None,
                    'kpi_service': self._kpi_service is not None,
                    'export_service': self._export_service is not None,
                    'file_storage': self._file_storage is not None
                }
            }
            
            # Información adicional si el manager está creado
            if self._manager:
                info['loaded_addons'] = self._manager.get_loaded_addons()
                
            return info
            
        except Exception as e:
            self._logger.error(f"Error obteniendo información del sistema: {e}")
            return {'error': str(e)}


def create_addon_factory(
    logger,
    main_window=None,
    controller=None,
    kpi_service=None,
    export_service=None,
    file_storage=None,
    addons_path="addons",
    dataconta_version="3.0.0"
) -> AddonFactory:
    """
    Función helper para crear AddonFactory con configuración estándar.
    
    Args:
        logger: Logger principal
        main_window: Ventana principal (opcional)
        controller: Controlador principal (opcional)
        kpi_service: Servicio de KPIs (opcional)
        export_service: Servicio de exportación (opcional)
        file_storage: Servicio de almacenamiento (opcional)
        addons_path: Path de addons (por defecto "addons")
        dataconta_version: Versión de DataConta (por defecto "3.0.0")
        
    Returns:
        AddonFactory: Factory configurado y listo para usar
    """
    return AddonFactory(
        logger=logger,
        main_window=main_window,
        controller=controller,
        kpi_service=kpi_service,
        export_service=export_service,
        file_storage=file_storage,
        addons_path=addons_path,
        dataconta_version=dataconta_version
    )