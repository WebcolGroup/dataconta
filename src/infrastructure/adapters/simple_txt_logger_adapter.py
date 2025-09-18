"""
Simple TXT Logger for FREE License
Sistema de logging simple a archivos de texto para usuarios de licencia gratuita.
Implementa logging básico sin dependencias externas complejas.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from enum import Enum

from src.domain.services.license_manager import LicenseManager


class LogLevel(Enum):
    """Niveles de logging simplificados para FREE."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class SimpleTxtLogger:
    """
    Logger simple para licencia FREE que escribe a archivos de texto.
    Diseñado para ser liviano y fácil de usar sin dependencias complejas.
    """
    
    def __init__(self, license_manager: LicenseManager, log_directory: str = "logs"):
        """
        Inicializar el logger simple.
        
        Args:
            license_manager: Gestor de licencias para validaciones
            log_directory: Directorio donde guardar los logs
        """
        self._license_manager = license_manager
        self._log_directory = Path(log_directory)
        self._current_session_id = None
        
        # Crear directorio de logs si no existe
        self._ensure_log_directory()
        
        # Iniciar sesión de logging
        self._start_session()
    
    def _ensure_log_directory(self):
        """Asegurar que el directorio de logs existe."""
        try:
            self._log_directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # Fallback a directorio actual si no se puede crear
            self._log_directory = Path(".")
    
    def _start_session(self):
        """Iniciar una nueva sesión de logging."""
        self._current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_session_start()
    
    def _log_session_start(self):
        """Registrar el inicio de la sesión."""
        session_info = f"""
{'='*60}
DATACONTA FREE - INICIO DE SESIÓN
{'='*60}
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sesión ID: {self._current_session_id}
Licencia: {self._license_manager.get_license_display_name() if self._license_manager else 'FREE'}
Versión: DATACONTA v3.0.0 FREE
{'='*60}
        """.strip()
        
        self._write_to_daily_log(session_info, LogLevel.INFO)
    
    def _get_daily_log_filename(self) -> Path:
        """Obtener el nombre del archivo de log diario."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self._log_directory / f"dataconta_free_{date_str}.txt"
    
    def _get_session_log_filename(self) -> Path:
        """Obtener el nombre del archivo de log de sesión."""
        return self._log_directory / f"session_{self._current_session_id}.txt"
    
    def _write_to_daily_log(self, message: str, level: LogLevel):
        """Escribir mensaje al log diario."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] [{level.value}] {message}\n"
            
            daily_log_file = self._get_daily_log_filename()
            with open(daily_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception:
            # Si no se puede escribir al archivo, continuar silenciosamente
            # para no interrumpir la funcionalidad principal
            pass
    
    def _write_to_session_log(self, message: str, level: LogLevel, context: Dict[str, Any] = None):
        """Escribir mensaje al log de sesión con contexto adicional."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level.value}] {message}"
            
            if context:
                context_str = " | ".join([f"{k}={v}" for k, v in context.items() if v is not None])
                if context_str:
                    log_entry += f" | {context_str}"
            
            log_entry += "\n"
            
            session_log_file = self._get_session_log_filename()
            with open(session_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception:
            # Si no se puede escribir al archivo, continuar silenciosamente
            pass
    
    def info(self, message: str, context: Dict[str, Any] = None):
        """Registrar mensaje informativo."""
        self._write_to_daily_log(message, LogLevel.INFO)
        self._write_to_session_log(message, LogLevel.INFO, context)
    
    def warning(self, message: str, context: Dict[str, Any] = None):
        """Registrar mensaje de advertencia."""
        self._write_to_daily_log(message, LogLevel.WARNING)
        self._write_to_session_log(message, LogLevel.WARNING, context)
    
    def error(self, message: str, context: Dict[str, Any] = None):
        """Registrar mensaje de error."""
        self._write_to_daily_log(message, LogLevel.ERROR)
        self._write_to_session_log(message, LogLevel.ERROR, context)
    
    def success(self, message: str, context: Dict[str, Any] = None):
        """Registrar mensaje de éxito."""
        self._write_to_daily_log(message, LogLevel.SUCCESS)
        self._write_to_session_log(message, LogLevel.SUCCESS, context)
    
    def log_operation(self, operation_name: str, success: bool, details: str = "", 
                     execution_time: float = None, records_count: int = None):
        """
        Registrar una operación completa con detalles.
        
        Args:
            operation_name: Nombre de la operación
            success: Si la operación fue exitosa
            details: Detalles adicionales
            execution_time: Tiempo de ejecución en segundos
            records_count: Cantidad de registros procesados
        """
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        status = "ÉXITO" if success else "ERROR"
        
        message = f"Operación: {operation_name} - {status}"
        if details:
            message += f" - {details}"
        
        context = {
            "operation": operation_name,
            "success": success,
            "execution_time_s": execution_time,
            "records_count": records_count
        }
        
        self._write_to_daily_log(message, level)
        self._write_to_session_log(message, level, context)
    
    def log_license_validation(self, action: str, allowed: bool, limit: int = None):
        """
        Registrar validación de licencia.
        
        Args:
            action: Acción que se intentó realizar
            allowed: Si la acción fue permitida
            limit: Límite aplicado por la licencia
        """
        level = LogLevel.INFO if allowed else LogLevel.WARNING
        status = "PERMITIDA" if allowed else "BLOQUEADA"
        
        message = f"Validación licencia: {action} - {status}"
        if limit:
            message += f" (límite: {limit})"
        
        context = {
            "license_action": action,
            "allowed": allowed,
            "limit": limit,
            "license_type": self._license_manager.get_license_display_name() if self._license_manager else "FREE"
        }
        
        self._write_to_daily_log(message, level)
        self._write_to_session_log(message, level, context)
    
    def log_export_operation(self, export_type: str, filename: str, records_count: int, 
                           file_size_bytes: int = None):
        """
        Registrar operación de exportación.
        
        Args:
            export_type: Tipo de exportación (JSON, CSV, etc.)
            filename: Nombre del archivo generado
            records_count: Cantidad de registros exportados
            file_size_bytes: Tamaño del archivo en bytes
        """
        message = f"Exportación {export_type}: {records_count} registros → {filename}"
        
        context = {
            "export_type": export_type,
            "filename": filename,
            "records_count": records_count,
            "file_size_bytes": file_size_bytes
        }
        
        self._write_to_daily_log(message, LogLevel.SUCCESS)
        self._write_to_session_log(message, LogLevel.SUCCESS, context)
    
    def log_user_action(self, action: str, details: str = ""):
        """
        Registrar acción del usuario.
        
        Args:
            action: Acción realizada por el usuario
            details: Detalles adicionales de la acción
        """
        message = f"Acción usuario: {action}"
        if details:
            message += f" - {details}"
        
        context = {
            "user_action": action,
            "details": details
        }
        
        self._write_to_daily_log(message, LogLevel.INFO)
        self._write_to_session_log(message, LogLevel.INFO, context)
    
    def get_recent_logs(self, max_lines: int = 20) -> str:
        """
        Obtener las líneas más recientes del log actual.
        
        Args:
            max_lines: Máximo número de líneas a devolver
            
        Returns:
            String con las líneas recientes del log
        """
        try:
            daily_log_file = self._get_daily_log_filename()
            
            if not daily_log_file.exists():
                return "No hay logs disponibles para hoy."
            
            with open(daily_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Devolver las últimas max_lines líneas
            recent_lines = lines[-max_lines:] if len(lines) > max_lines else lines
            
            return ''.join(recent_lines).strip()
            
        except Exception as e:
            return f"Error leyendo logs: {str(e)}"
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de la sesión actual.
        
        Returns:
            Diccionario con estadísticas de la sesión
        """
        try:
            session_log_file = self._get_session_log_filename()
            
            if not session_log_file.exists():
                return {"error": "No hay log de sesión disponible"}
            
            with open(session_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Contar eventos por nivel
            level_counts = {level.value: 0 for level in LogLevel}
            operations_count = 0
            export_count = 0
            
            for line in lines:
                for level in LogLevel:
                    if f"[{level.value}]" in line:
                        level_counts[level.value] += 1
                        break
                
                if "Operación:" in line:
                    operations_count += 1
                if "Exportación" in line:
                    export_count += 1
            
            return {
                "session_id": self._current_session_id,
                "total_events": len(lines),
                "level_counts": level_counts,
                "operations_count": operations_count,
                "exports_count": export_count,
                "log_file": str(session_log_file)
            }
            
        except Exception as e:
            return {"error": f"Error generando resumen: {str(e)}"}
    
    def close_session(self):
        """Cerrar la sesión de logging actual."""
        session_summary = self.get_session_summary()
        
        closing_info = f"""
{'='*60}
DATACONTA FREE - FIN DE SESIÓN
{'='*60}
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sesión ID: {self._current_session_id}
Total eventos: {session_summary.get('total_events', 0)}
Operaciones: {session_summary.get('operations_count', 0)}
Exportaciones: {session_summary.get('exports_count', 0)}
{'='*60}
        """.strip()
        
        self._write_to_daily_log(closing_info, LogLevel.INFO)
        self._write_to_session_log(closing_info, LogLevel.INFO)
    
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """
        Limpiar logs antiguos para ahorrar espacio.
        
        Args:
            days_to_keep: Número de días de logs a mantener
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            for log_file in self._log_directory.glob("*.txt"):
                if log_file.stat().st_mtime < cutoff_date:
                    try:
                        log_file.unlink()
                        self.info(f"Log antiguo eliminado: {log_file.name}")
                    except Exception:
                        # Ignorar errores al eliminar archivos
                        pass
                        
        except Exception as e:
            self.warning(f"Error limpiando logs antiguos: {str(e)}")


# ================================================================================================
# ADAPTER PARA INTEGRACIÓN CON EL SISTEMA EXISTENTE
# ================================================================================================

class SimpleTxtLoggerAdapter:
    """
    Adapter para integrar SimpleTxtLogger con la interfaz Logger existente.
    Permite usar el logger simple como drop-in replacement.
    """
    
    def __init__(self, license_manager: LicenseManager, log_directory: str = "logs"):
        self._txt_logger = SimpleTxtLogger(license_manager, log_directory)
    
    def info(self, message: str):
        """Log message de información."""
        self._txt_logger.info(message)
    
    def warning(self, message: str):
        """Log message de advertencia.""" 
        self._txt_logger.warning(message)
    
    def error(self, message: str):
        """Log message de error."""
        self._txt_logger.error(message)
    
    def debug(self, message: str):
        """Log message de debug (mapeado a info para FREE)."""
        self._txt_logger.info(f"DEBUG: {message}")
    
    def get_txt_logger(self) -> SimpleTxtLogger:
        """Obtener acceso al logger TXT completo."""
        return self._txt_logger