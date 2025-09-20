"""
Addon Interfaces - Ports para el sistema de addons
Siguiendo arquitectura hexagonal y principios SOLID
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum


class AddonStatus(Enum):
    """Estados posibles de un addon."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    LOADING = "loading"
    DISABLED = "disabled"


class AddonType(Enum):
    """Tipos de addons soportados."""
    UI_EXTENSION = "ui_extension"
    DATA_PROCESSOR = "data_processor"
    EXPORTER = "exporter"
    INTEGRATION = "integration"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    SECURITY = "security"
    UTILITY = "utility"


@dataclass
class AddonManifest:
    """Manifiesto de un addon con toda su metadata."""
    
    # Información básica
    name: str
    version: str
    description: str
    author: str
    
    # Configuración técnica
    addon_type: AddonType
    entry_point: str  # Clase principal del addon
    min_dataconta_version: str
    max_dataconta_version: Optional[str] = None
    
    # Dependencias y permisos
    dependencies: List[str] = None  # Dependencias Python
    requires_license: str = "FREE"  # FREE, PROFESSIONAL, ENTERPRISE
    permissions: List[str] = None   # Permisos requeridos
    
    # UI Integration
    menu_items: List[Dict[str, Any]] = None
    ui_components: List[str] = None
    
    # Metadata adicional
    license: str = "MIT"
    keywords: List[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    
    def __post_init__(self):
        """Inicializar listas vacías si son None."""
        if self.dependencies is None:
            self.dependencies = []
        if self.permissions is None:
            self.permissions = []
        if self.menu_items is None:
            self.menu_items = []
        if self.ui_components is None:
            self.ui_components = []
        if self.keywords is None:
            self.keywords = []


@dataclass
class AddonContext:
    """Contexto proporcionado a los addons para interactuar con DataConta."""
    
    # Referencias principales
    main_window: Any = None
    controller: Any = None
    logger: Any = None
    
    # Servicios disponibles
    kpi_service: Any = None
    export_service: Any = None
    file_storage: Any = None
    
    # Configuración
    app_config: Dict[str, Any] = None
    addon_config: Dict[str, Any] = None
    
    # Callbacks para interacción
    show_message: Callable[[str, str], None] = None
    show_error: Callable[[str, str], None] = None
    add_menu_item: Callable[[Dict[str, Any]], bool] = None
    
    def __post_init__(self):
        """Inicializar diccionarios vacíos si son None."""
        if self.app_config is None:
            self.app_config = {}
        if self.addon_config is None:
            self.addon_config = {}


class AddonBase(ABC):
    """
    Clase base abstracta para todos los addons.
    Define la interfaz que deben implementar todos los addons.
    """
    
    def __init__(self, context: AddonContext):
        """
        Inicializar addon con contexto.
        
        Args:
            context: Contexto de la aplicación para el addon
        """
        self.context = context
        self.manifest = None
        self.status = AddonStatus.INACTIVE
        self._is_initialized = False
    
    @abstractmethod
    def get_manifest(self) -> AddonManifest:
        """
        Obtener el manifiesto del addon.
        
        Returns:
            AddonManifest: Manifiesto con metadata del addon
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializar el addon.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Cerrar y limpiar recursos del addon.
        
        Returns:
            bool: True si el cierre fue exitoso
        """
        pass
    
    def activate(self) -> bool:
        """
        Activar el addon.
        
        Returns:
            bool: True si la activación fue exitosa
        """
        try:
            if not self._is_initialized:
                if not self.initialize():
                    return False
                self._is_initialized = True
                
            self.status = AddonStatus.ACTIVE
            return True
            
        except Exception as e:
            self.context.logger.error(f"Error activando addon {self.get_name()}: {e}")
            self.status = AddonStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """
        Desactivar el addon.
        
        Returns:
            bool: True si la desactivación fue exitosa
        """
        try:
            result = self.shutdown()
            self.status = AddonStatus.INACTIVE
            self._is_initialized = False
            return result
            
        except Exception as e:
            self.context.logger.error(f"Error desactivando addon {self.get_name()}: {e}")
            self.status = AddonStatus.ERROR
            return False
    
    def get_name(self) -> str:
        """Obtener nombre del addon."""
        manifest = self.get_manifest()
        return manifest.name if manifest else "Unknown"
    
    def get_version(self) -> str:
        """Obtener versión del addon."""
        manifest = self.get_manifest()
        return manifest.version if manifest else "0.0.0"
    
    def get_status(self) -> AddonStatus:
        """Obtener estado actual del addon."""
        return self.status
    
    def is_active(self) -> bool:
        """Verificar si el addon está activo."""
        return self.status == AddonStatus.ACTIVE
    
    # Métodos opcionales que los addons pueden implementar
    
    def register_menu_actions(self) -> Dict[str, Callable]:
        """
        Registrar acciones de menú del addon.
        
        Returns:
            Dict[str, Callable]: Diccionario de accion_id -> función
        """
        return {}
    
    def register_ui_components(self) -> Dict[str, Any]:
        """
        Registrar componentes UI del addon.
        
        Returns:
            Dict[str, Any]: Diccionario de componente_id -> widget/component
        """
        return {}
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """
        Obtener esquema de configuración del addon.
        
        Returns:
            Optional[Dict]: JSON Schema para configuración del addon
        """
        return None
    
    def handle_config_change(self, config: Dict[str, Any]) -> bool:
        """
        Manejar cambios en la configuración del addon.
        
        Args:
            config: Nueva configuración
            
        Returns:
            bool: True si el cambio fue procesado exitosamente
        """
        return True


class AddonRepository(ABC):
    """Puerto para repositorio de addons."""
    
    @abstractmethod
    def find_all_addons(self) -> List[str]:
        """
        Encontrar todos los addons disponibles.
        
        Returns:
            List[str]: Lista de paths a addons
        """
        pass
    
    @abstractmethod
    def load_addon_manifest(self, addon_path: str) -> Optional[AddonManifest]:
        """
        Cargar manifiesto de un addon.
        
        Args:
            addon_path: Path al addon
            
        Returns:
            Optional[AddonManifest]: Manifiesto o None si falla
        """
        pass
    
    @abstractmethod
    def validate_addon(self, addon_path: str) -> bool:
        """
        Validar estructura y contenido de un addon.
        
        Args:
            addon_path: Path al addon
            
        Returns:
            bool: True si el addon es válido
        """
        pass
    
    @abstractmethod
    def get_addon_config(self, addon_name: str) -> Dict[str, Any]:
        """
        Obtener configuración de un addon.
        
        Args:
            addon_name: Nombre del addon
            
        Returns:
            Dict[str, Any]: Configuración del addon
        """
        pass
    
    @abstractmethod
    def save_addon_config(self, addon_name: str, config: Dict[str, Any]) -> bool:
        """
        Guardar configuración de un addon.
        
        Args:
            addon_name: Nombre del addon
            config: Configuración a guardar
            
        Returns:
            bool: True si se guardó exitosamente
        """
        pass


class AddonManager(ABC):
    """Puerto para gestor principal de addons."""
    
    @abstractmethod
    def scan_addons(self) -> int:
        """
        Escanear y encontrar addons disponibles.
        
        Returns:
            int: Número de addons encontrados
        """
        pass
    
    @abstractmethod
    def load_addon(self, addon_name: str) -> bool:
        """
        Cargar un addon específico.
        
        Args:
            addon_name: Nombre del addon a cargar
            
        Returns:
            bool: True si se cargó exitosamente
        """
        pass
    
    @abstractmethod
    def unload_addon(self, addon_name: str) -> bool:
        """
        Descargar un addon específico.
        
        Args:
            addon_name: Nombre del addon a descargar
            
        Returns:
            bool: True si se descargó exitosamente
        """
        pass
    
    @abstractmethod
    def get_loaded_addons(self) -> List[str]:
        """
        Obtener lista de addons cargados.
        
        Returns:
            List[str]: Lista de nombres de addons cargados
        """
        pass
    
    @abstractmethod
    def get_addon_info(self, addon_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de un addon.
        
        Args:
            addon_name: Nombre del addon
            
        Returns:
            Optional[Dict]: Información del addon o None
        """
        pass
    
    @abstractmethod
    def is_addon_compatible(self, manifest: AddonManifest) -> bool:
        """
        Verificar si un addon es compatible con la versión actual.
        
        Args:
            manifest: Manifiesto del addon
            
        Returns:
            bool: True si es compatible
        """
        pass
    
    @abstractmethod
    def enable_addon(self, addon_name: str) -> bool:
        """
        Habilitar un addon.
        
        Args:
            addon_name: Nombre del addon
            
        Returns:
            bool: True si se habilitó exitosamente
        """
        pass
    
    @abstractmethod
    def disable_addon(self, addon_name: str) -> bool:
        """
        Deshabilitar un addon.
        
        Args:
            addon_name: Nombre del addon
            
        Returns:
            bool: True si se deshabilitó exitosamente
        """
        pass


class AddonLoader(ABC):
    """Puerto para cargador de addons."""
    
    @abstractmethod
    def load_addon_class(self, addon_path: str, entry_point: str) -> Optional[type]:
        """
        Cargar clase de un addon dinámicamente.
        
        Args:
            addon_path: Path al addon
            entry_point: Punto de entrada (clase principal)
            
        Returns:
            Optional[type]: Clase del addon o None si falla
        """
        pass
    
    @abstractmethod
    def create_addon_instance(self, addon_class: type, context: AddonContext) -> Optional[AddonBase]:
        """
        Crear instancia de un addon.
        
        Args:
            addon_class: Clase del addon
            context: Contexto de la aplicación
            
        Returns:
            Optional[AddonBase]: Instancia del addon o None si falla
        """
        pass
    
    @abstractmethod
    def validate_addon_class(self, addon_class: type) -> bool:
        """
        Validar que una clase sea un addon válido.
        
        Args:
            addon_class: Clase a validar
            
        Returns:
            bool: True si es válida
        """
        pass


class AddonRegistry(ABC):
    """Puerto para registro de addons activos."""
    
    @abstractmethod
    def register_addon(self, addon_name: str, addon_instance: AddonBase) -> bool:
        """
        Registrar una instancia de addon.
        
        Args:
            addon_name: Nombre del addon
            addon_instance: Instancia del addon
            
        Returns:
            bool: True si se registró exitosamente
        """
        pass
    
    @abstractmethod
    def unregister_addon(self, addon_name: str) -> bool:
        """
        Desregistrar un addon.
        
        Args:
            addon_name: Nombre del addon
            
        Returns:
            bool: True si se desregistró exitosamente
        """
        pass
    
    @abstractmethod
    def get_addon(self, addon_name: str) -> Optional[AddonBase]:
        """
        Obtener instancia de addon registrado.
        
        Args:
            addon_name: Nombre del addon
            
        Returns:
            Optional[AddonBase]: Instancia del addon o None
        """
        pass
    
    @abstractmethod
    def get_all_addons(self) -> Dict[str, AddonBase]:
        """
        Obtener todos los addons registrados.
        
        Returns:
            Dict[str, AddonBase]: Diccionario nombre -> instancia
        """
        pass
    
    @abstractmethod
    def get_addons_by_type(self, addon_type: AddonType) -> List[AddonBase]:
        """
        Obtener addons por tipo.
        
        Args:
            addon_type: Tipo de addon
            
        Returns:
            List[AddonBase]: Lista de addons del tipo especificado
        """
        pass
    
    @abstractmethod
    def get_active_addons(self) -> List[AddonBase]:
        """
        Obtener addons activos.
        
        Returns:
            List[AddonBase]: Lista de addons activos
        """
        pass
    
    @abstractmethod
    def execute_addon_action(self, addon_name: str, action: str, **kwargs) -> Any:
        """
        Ejecutar acción de un addon.
        
        Args:
            addon_name: Nombre del addon
            action: Nombre de la acción
            **kwargs: Argumentos de la acción
            
        Returns:
            Any: Resultado de la acción
        """
        pass