"""
Infrastructure Factories Package
Contiene factories para crear componentes de infraestructura con dependencias inyectadas.
"""

from .application_factory import DataContaApplicationFactory, DependencyContainer

__all__ = [
    'DataContaApplicationFactory',
    'DependencyContainer'
]