"""
Tests Package - DataConta
Estructura de pruebas siguiendo arquitectura hexagonal

Organización:
- tests/unit/domain/      -> Tests para entidades y servicios de dominio
- tests/unit/application/ -> Tests para casos de uso y servicios de aplicación  
- tests/integration/      -> Tests de integración entre capas
- tests/fixtures/         -> Datos de prueba y factories
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

__all__ = []