"""
Archivo __init__.py para el paquete de widgets especializados.
Permite importaciones centralizadas de todos los widgets NO monolíticos.
"""

from .dashboard_widget import DashboardWidget
from .export_widget import ExportWidget
from .query_widget import QueryWidget
from .demo_handler_widget import DemoHandlerWidget

__all__ = [
    'DashboardWidget',
    'ExportWidget', 
    'QueryWidget',
    'DemoHandlerWidget'
]