"""
UI Package - Interfaz gráfica de usuario
Contiene todos los componentes de la interfaz PySide6 para DATACONTA.
Mantiene arquitectura hexagonal y principios SOLID.
"""

from typing import TYPE_CHECKING

# Importaciones condicionales para evitar errores durante desarrollo
if TYPE_CHECKING:
    from src.ui.components.main_window import MainWindow
    from src.ui.adapters.ui_adapters import UIControllerAdapter, BusinessLogicAdapter, MenuActionsAdapter

__all__ = [
    "MainWindow",
    "UIControllerAdapter", 
    "BusinessLogicAdapter",
    "MenuActionsAdapter"
]