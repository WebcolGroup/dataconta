"""
UI Interfaces - Domain Layer
Define contratos que debe cumplir la capa de UI sin acoplarse a implementaciones específicas.
Mantiene la inversión de dependencias de la arquitectura hexagonal.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class UINotificationType(Enum):
    """Tipos de notificaciones para la UI"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"


@dataclass
class UIMenuOption:
    """Opción de menú para la interfaz de usuario"""
    id: str
    title: str
    description: str
    emoji: str
    action: Callable[[], None]
    enabled: bool = True
    license_required: str = "FREE"


@dataclass
class UINotification:
    """Notificación para mostrar al usuario"""
    title: str
    message: str
    notification_type: UINotificationType
    details: Optional[str] = None
    duration: Optional[int] = None  # En milisegundos, None = indefinido


@dataclass
class UIProgressInfo:
    """Información de progreso para operaciones largas"""
    title: str
    message: str
    current: int = 0
    maximum: int = 100
    is_indeterminate: bool = False


class UIUserInteraction(ABC):
    """
    Interfaz para interacciones con el usuario.
    Define métodos que la UI debe implementar para mostrar información y obtener input del usuario.
    """
    
    @abstractmethod
    def show_notification(self, notification: UINotification) -> None:
        """
        Mostrar una notificación al usuario.
        
        Args:
            notification: Información de la notificación
        """
        pass
    
    @abstractmethod
    def ask_confirmation(self, title: str, message: str) -> bool:
        """
        Pedir confirmación al usuario.
        
        Args:
            title: Título de la confirmación
            message: Mensaje de confirmación
            
        Returns:
            True si el usuario confirma, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_user_input(self, title: str, message: str, default_value: str = "") -> Optional[str]:
        """
        Obtener input de texto del usuario.
        
        Args:
            title: Título del diálogo
            message: Mensaje/prompt para el usuario
            default_value: Valor por defecto
            
        Returns:
            Texto ingresado por el usuario o None si cancela
        """
        pass
    
    @abstractmethod
    def select_from_list(self, title: str, message: str, options: List[str]) -> Optional[str]:
        """
        Permitir al usuario seleccionar de una lista de opciones.
        
        Args:
            title: Título del diálogo
            message: Mensaje explicativo
            options: Lista de opciones disponibles
            
        Returns:
            Opción seleccionada o None si cancela
        """
        pass
    
    @abstractmethod
    def show_progress(self, progress_info: UIProgressInfo) -> None:
        """
        Mostrar progreso de una operación.
        
        Args:
            progress_info: Información del progreso
        """
        pass
    
    @abstractmethod
    def hide_progress(self) -> None:
        """Ocultar el indicador de progreso."""
        pass


class UIMenuController(ABC):
    """
    Interfaz para el controlador principal de menús.
    Define cómo debe comportarse la ventana principal de la aplicación.
    """
    
    @abstractmethod
    def setup_menu_options(self, menu_sections: Dict[str, List[UIMenuOption]]) -> None:
        """
        Configurar las opciones de menú en la UI.
        
        Args:
            menu_sections: Diccionario con secciones del menú y sus opciones
        """
        pass
    
    @abstractmethod
    def enable_option(self, option_id: str, enabled: bool = True) -> None:
        """
        Habilitar/deshabilitar una opción específica.
        
        Args:
            option_id: ID de la opción
            enabled: True para habilitar, False para deshabilitar
        """
        pass
    
    @abstractmethod
    def update_license_status(self, license_type: str, is_valid: bool) -> None:
        """
        Actualizar el estado de la licencia en la UI.
        
        Args:
            license_type: Tipo de licencia
            is_valid: Si la licencia es válida
        """
        pass
    
    @abstractmethod
    def show_main_window(self) -> None:
        """Mostrar la ventana principal."""
        pass
    
    @abstractmethod
    def close_application(self) -> None:
        """Cerrar la aplicación."""
        pass


class UIFileOperations(ABC):
    """
    Interfaz para operaciones con archivos desde la UI.
    """
    
    @abstractmethod
    def select_save_file(self, title: str, default_filename: str, file_filter: str) -> Optional[str]:
        """
        Permitir al usuario seleccionar dónde guardar un archivo.
        
        Args:
            title: Título del diálogo
            default_filename: Nombre por defecto
            file_filter: Filtro de archivos (ej: "CSV files (*.csv)")
            
        Returns:
            Ruta seleccionada o None si cancela
        """
        pass
    
    @abstractmethod
    def select_open_file(self, title: str, file_filter: str) -> Optional[str]:
        """
        Permitir al usuario seleccionar un archivo para abrir.
        
        Args:
            title: Título del diálogo
            file_filter: Filtro de archivos
            
        Returns:
            Ruta seleccionada o None si cancela
        """
        pass
    
    @abstractmethod
    def select_directory(self, title: str, default_path: str = "") -> Optional[str]:
        """
        Permitir al usuario seleccionar un directorio.
        
        Args:
            title: Título del diálogo
            default_path: Directorio por defecto
            
        Returns:
            Directorio seleccionado o None si cancela
        """
        pass


class UIDataPresentation(ABC):
    """
    Interfaz para presentar datos al usuario.
    """
    
    @abstractmethod
    def show_data_table(self, title: str, headers: List[str], data: List[List[Any]]) -> None:
        """
        Mostrar datos en formato tabla.
        
        Args:
            title: Título de la ventana/tabla
            headers: Encabezados de columnas
            data: Datos a mostrar (lista de filas)
        """
        pass
    
    @abstractmethod
    def show_report_results(self, title: str, content: str, format_type: str = "text") -> None:
        """
        Mostrar resultados de un reporte.
        
        Args:
            title: Título del reporte
            content: Contenido del reporte
            format_type: Tipo de formato (text, html, json)
        """
        pass


class UIApplicationController(ABC):
    """
    Controlador principal de la aplicación UI.
    Coordina todas las interfaces y maneja el flujo principal.
    """
    
    @abstractmethod
    def initialize_ui(self) -> None:
        """Inicializar todos los componentes de la UI."""
        pass
    
    @abstractmethod
    def start_application(self) -> None:
        """Iniciar la aplicación con interfaz gráfica."""
        pass
    
    @abstractmethod
    def get_menu_controller(self) -> UIMenuController:
        """Obtener el controlador de menús."""
        pass
    
    @abstractmethod
    def get_user_interaction(self) -> UIUserInteraction:
        """Obtener el manejador de interacciones con usuario."""
        pass
    
    @abstractmethod
    def get_file_operations(self) -> UIFileOperations:
        """Obtener el manejador de operaciones con archivos."""
        pass
    
    @abstractmethod
    def get_data_presentation(self) -> UIDataPresentation:
        """Obtener el manejador de presentación de datos."""
        pass