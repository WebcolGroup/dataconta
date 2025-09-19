"""
Console Logger Adapter - Infrastructure Layer
Implementa la interfaz Logger para logging en consola.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from src.application.ports.interfaces import Logger


class ConsoleLogger(Logger):
    """Logger que imprime mensajes en consola con timestamps."""
    
    def __init__(self, level: str = "INFO"):
        self.level = level.upper()
        self.levels = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }
    
    def _should_log(self, level: str) -> bool:
        """Verificar si debe logear según el nivel."""
        return self.levels.get(level.upper(), 1) >= self.levels.get(self.level, 1)
    
    def _format_message(self, level: str, message: str, **kwargs) -> str:
        """Formatear mensaje con timestamp y nivel."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        
        if kwargs:
            formatted += f" | Datos: {kwargs}"
        
        return formatted
    
    def debug(self, message: str, **kwargs) -> None:
        """Log mensaje debug."""
        if self._should_log("DEBUG"):
            print(self._format_message("DEBUG", message, **kwargs))
    
    def info(self, message: str, **kwargs) -> None:
        """Log mensaje informativo."""
        if self._should_log("INFO"):
            print(self._format_message("INFO", message, **kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log mensaje de advertencia."""
        if self._should_log("WARNING"):
            print(self._format_message("WARNING", message, **kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Log mensaje de error."""
        if self._should_log("ERROR"):
            print(self._format_message("ERROR", message, **kwargs))
    
    def critical(self, message: str, **kwargs) -> None:
        """Log mensaje crítico."""
        if self._should_log("CRITICAL"):
            print(self._format_message("CRITICAL", message, **kwargs))
    
    def log(self, level: str, message: str, **kwargs) -> None:
        """Log mensaje con nivel específico."""
        method_map = {
            "DEBUG": self.debug,
            "INFO": self.info,
            "WARNING": self.warning,
            "ERROR": self.error,
            "CRITICAL": self.critical
        }
        
        method = method_map.get(level.upper(), self.info)
        method(message, **kwargs)