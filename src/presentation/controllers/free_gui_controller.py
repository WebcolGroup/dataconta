"""
Free GUI Controller - Presentation Layer
Controlador principal para DataConta FREE GUI siguiendo arquitectura hexagonal.
Implementa interfaces del dominio y coordina la vista con los servicios.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QTableWidget
from PySide6.QtCore import QObject, Signal as pyqtSignal, QDate

from src.domain.interfaces.ui_interfaces import UIMenuController, UIUserInteraction
from src.domain.interfaces.ui_interfaces import UIFileOperations, UIDataPresentation
from src.domain.entities.invoice import InvoiceFilter
from src.application.services.kpi_service import KPIService, KPIData
from src.application.services.export_service import ExportService, ExportResult
from src.application.ports.interfaces import InvoiceRepository, Logger, FileStorage

# Debug Tools - Agregado automáticamente
try:
    from debug_tools import (
        debug_method, debug_controller_action, debug_context, 
        get_debug_logger, debug_invoice_processing, debug_export_operation
    )
    DEBUG_AVAILABLE = True
except ImportError:
    # Definir decoradores dummy si debug_tools no está disponible
    def debug_method(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def debug_controller_action(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def get_debug_logger():
        return None
    
    DEBUG_AVAILABLE = False
# End Debug Tools


# Debug Tools - Agregado automáticamente
try:
    from debug_tools import (
        debug_method, debug_controller_action, debug_context, 
        get_debug_logger, debug_invoice_processing, debug_export_operation
    )
    DEBUG_AVAILABLE = True
except ImportError:
    # Definir decoradores dummy si debug_tools no está disponible
    def debug_method(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def debug_controller_action(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def get_debug_logger():
        return None
    
    DEBUG_AVAILABLE = False
# End Debug Tools



class FreeGUIController(QObject):
    """
    Controlador principal para DataConta FREE GUI.
    Implementa todas las interfaces UI del dominio y coordina con servicios.
    """
    
    # Signals para comunicación con UI
    data_loaded = pyqtSignal()
    export_completed = pyqtSignal(str)
    kpis_calculated = pyqtSignal(dict)
    estado_resultados_generated = pyqtSignal(str, str)  # file_path, summary
    
    def __init__(self, 
                 kpi_service: KPIService, 
                 export_service: ExportService,
                 invoice_repository: InvoiceRepository,
                 logger: Logger,
                 file_storage: FileStorage):
        super().__init__()
        
        # Dependency Injection
        self._kpi_service = kpi_service
        self._export_service = export_service
        self._invoice_repository = invoice_repository
        self._logger = logger
        self._file_storage = file_storage
        
        # Estado interno
        self._invoices_data = []
        self._current_kpis: Optional[KPIData] = None
        self._gui_reference = None  # Referencia a la ventana principal
        
        # Configurar sistema de seguridad API
        self._setup_api_security()
        
        # Cargar KPIs existentes automáticamente al inicializar
        self._auto_load_existing_kpis()
        
        # 🔧 DEBUG: Autenticar al inicializar
        print("🔌 ===== INICIALIZANDO CONTROLADOR =====")
        print(f"📱 Invoice Repository: {type(self._invoice_repository).__name__}")
        
        # Intentar autenticación inmediata
        if hasattr(self._invoice_repository, 'authenticate'):
            print("🔐 Intentando autenticación automática...")
            auth_result = self._invoice_repository.authenticate()
            print(f"🔐 Resultado autenticación: {auth_result}")
        
        # Verificar conexión
        if hasattr(self._invoice_repository, 'is_connected'):
            connection_status = self._invoice_repository.is_connected()
            print(f"🌐 Estado conexión: {connection_status}")
            
        print("✅ ===== CONTROLADOR INICIALIZADO =====")
        print()
        
        self._logger.info("🎮 FreeGUIController inicializado")
    
    def set_gui_reference(self, gui_instance):
        """Establecer referencia a la instancia de GUI para callbacks."""
        self._gui_reference = gui_instance
        self._logger.info("🖼️ Referencia GUI establecida")
    
    # ==================== UIMenuController Implementation ====================
    
    def setup_menu_options(self, menu_sections: Dict[str, List]) -> None:
        """Configurar opciones de menú."""
        self._logger.info("📋 Configurando opciones de menú")
    
    def enable_option(self, option_id: str, enabled: bool = True) -> None:
        """Habilitar/deshabilitar opción."""
        self._logger.info(f"🎯 {'Habilitando' if enabled else 'Deshabilitando'} opción: {option_id}")
    
    def update_license_status(self, license_type: str, is_valid: bool) -> None:
        """Actualizar estado de licencia."""
        self._logger.info(f"📜 Licencia {license_type}: {'Válida' if is_valid else 'Inválida'}")
    
    def show_main_window(self) -> None:
        """Mostrar ventana principal."""
        self._logger.info("📋 Mostrando ventana principal")
        if self._gui_reference:
            self._gui_reference.show()
    
    def close_application(self) -> None:
        """Cerrar aplicación."""
        self._logger.info("🚪 Cerrando aplicación")
        if self._gui_reference:
            self._gui_reference.close()
    
    # ==================== UIUserInteraction Implementation ====================
    
    def show_notification(self, notification) -> None:
        """Mostrar notificación."""
        self._logger.info(f"🔔 Notificación: {notification}")
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        """Pedir confirmación."""
        return self.confirm_action(f"{title}: {message}")
    
    def get_user_input(self, title: str, message: str, default_value: str = "") -> Optional[str]:
        """Obtener entrada del usuario."""
        return default_value
    
    def select_from_list(self, title: str, message: str, options: List[str]) -> Optional[str]:
        """Seleccionar de lista."""
        return options[0] if options else None
    
    def show_progress(self, progress_info) -> None:
        """Mostrar progreso."""
        self._logger.info(f"📊 Progreso: {progress_info}")
    
    def hide_progress(self) -> None:
        """Ocultar progreso."""
        self._logger.info("📊 Ocultando progreso")
    
    # ==================== UIFileOperations Implementation ====================
    
    def select_save_file(self, title: str, default_filename: str, file_filter: str) -> Optional[str]:
        """Seleccionar archivo para guardar."""
        return f"outputs/{default_filename}"
    
    def select_open_file(self, title: str, file_filter: str) -> Optional[str]:
        """Seleccionar archivo para abrir."""
        return "outputs/sample_file.json"
    
    def select_directory(self, title: str, default_path: str = "") -> Optional[str]:
        """Seleccionar directorio."""
        return "outputs/"
    
    # ==================== UIDataPresentation Implementation ====================
    
    def show_report_results(self, title: str, content: str, format_type: str = "text") -> None:
        """Mostrar resultados de reporte."""
        self._logger.info(f"� Mostrando reporte: {title} ({format_type})")
    
    # ==================== Utility Methods ====================
    
    def confirm_action(self, message: str) -> bool:
        """Confirmar acción del usuario."""
        try:
            if not self._gui_reference:
                return False
            
            reply = QMessageBox.question(
                self._gui_reference,
                "Confirmar Acción",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            confirmed = reply == QMessageBox.StandardButton.Yes
            self._logger.info(f"✅ Confirmación usuario: {confirmed}")
            return confirmed
            
        except Exception as e:
            self._logger.error(f"❌ Error confirmando acción: {e}")
            return False
    
    def select_from_options(self, options: List[str], prompt: str) -> str:
        """Seleccionar de lista de opciones."""
        # En GUI esto se maneja con comboboxes o listas
        return options[0] if options else ""
    
    # ==================== UIVisualization Implementation ====================
    
    def show_chart(self, chart_data: Dict[str, Any], chart_type: str) -> None:
        """Mostrar gráfico."""
        try:
            self._logger.info(f"📊 Mostrando gráfico: {chart_type}")
            
            if not self._gui_reference or not hasattr(self._gui_reference, 'update_charts'):
                self._logger.warning("⚠️ No se puede mostrar gráfico - referencia GUI no disponible")
                return
            
            # Delegar a la GUI para mostrar el gráfico
            self._gui_reference.update_charts(chart_data, chart_type)
            self._logger.info("✅ Gráfico mostrado correctamente")
            
        except Exception as e:
            self._logger.error(f"❌ Error mostrando gráfico: {e}")
    
    def update_visualization(self, data: Dict[str, Any]) -> None:
        """Actualizar visualización."""
        try:
            self._logger.info("🔄 Actualizando visualizaciones")
            
            if self._gui_reference and hasattr(self._gui_reference, 'refresh_all_tabs'):
                self._gui_reference.refresh_all_tabs()
                self._logger.info("✅ Visualizaciones actualizadas")
                
        except Exception as e:
            self._logger.error(f"❌ Error actualizando visualización: {e}")
    
    def hide_visualization(self) -> None:
        """Ocultar visualización."""
        self._logger.info("👁️ Ocultando visualizaciones")
    
    # ==================== UINotification Implementation ====================
    
    def show_success_message(self, message: str) -> None:
        """Mostrar mensaje de éxito."""
        try:
            self._logger.info(f"✅ Éxito: {message}")
            
            if self._gui_reference:
                QMessageBox.information(self._gui_reference, "Éxito", message)
                
        except Exception as e:
            self._logger.error(f"❌ Error mostrando mensaje de éxito: {e}")
    
    def show_error_message(self, message: str) -> None:
        """Mostrar mensaje de error."""
        try:
            self._logger.error(f"❌ Error UI: {message}")
            
            if self._gui_reference:
                QMessageBox.critical(self._gui_reference, "Error", message)
                
        except Exception as e:
            self._logger.error(f"❌ Error mostrando mensaje de error: {e}")
    
    def show_warning_message(self, message: str) -> None:
        """Mostrar mensaje de advertencia."""
        try:
            self._logger.warning(f"⚠️ Advertencia: {message}")
            
            if self._gui_reference:
                QMessageBox.warning(self._gui_reference, "Advertencia", message)
                
        except Exception as e:
            self._logger.error(f"❌ Error mostrando advertencia: {e}")
    
    def show_info_message(self, message: str) -> None:
        """Mostrar mensaje informativo."""
        try:
            self._logger.info(f"ℹ️ Info: {message}")
            
            if self._gui_reference:
                QMessageBox.information(self._gui_reference, "Información", message)
                
        except Exception as e:
            self._logger.error(f"❌ Error mostrando mensaje info: {e}")
    
    # ==================== UIDataDisplay Implementation ====================
    
    def display_table_data(self, data: List[Dict[str, Any]], table_widget: Any) -> None:
        """Mostrar datos en tabla."""
        try:
            if not isinstance(table_widget, QTableWidget):
                self._logger.error("❌ Widget no es QTableWidget")
                return
            
            if not data:
                table_widget.setRowCount(0)
                return
            
            # Configurar tabla
            columns = list(data[0].keys())
            table_widget.setColumnCount(len(columns))
            table_widget.setHorizontalHeaderLabels(columns)
            table_widget.setRowCount(len(data))
            
            # Llenar datos
            for row_idx, row_data in enumerate(data):
                for col_idx, column in enumerate(columns):
                    value = str(row_data.get(column, ""))
                    table_widget.setItem(row_idx, col_idx, value)
            
            self._logger.info(f"✅ Tabla actualizada: {len(data)} filas, {len(columns)} columnas")
            
        except Exception as e:
            self._logger.error(f"❌ Error mostrando tabla: {e}")
    
    def update_summary_stats(self, stats: Dict[str, Any]) -> None:
        """Actualizar estadísticas resumen."""
        try:
            self._logger.info("📈 Actualizando estadísticas resumen")
            
            if self._gui_reference and hasattr(self._gui_reference, 'update_kpi_displays'):
                self._gui_reference.update_kpi_displays(stats)
                self._logger.info("✅ Estadísticas actualizadas")
                
        except Exception as e:
            self._logger.error(f"❌ Error actualizando estadísticas: {e}")
    
    def refresh_data_display(self) -> None:
        """Refrescar visualización de datos."""
        try:
            self._logger.info("🔄 Refrescando visualización de datos")
            
            if self._current_kpis:
                self.update_summary_stats(self._current_kpis.to_dict())
                
            self.data_loaded.emit()  # Signal para UI
            
        except Exception as e:
            self._logger.error(f"❌ Error refrescando datos: {e}")
    
    # ==================== UIExport Implementation ====================
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """Exportar datos a CSV."""
        try:
            # Usar ExportService
            result = self._export_service.export_csv_real(
                data, 
                filename,
                include_metadata=True
            )
            
            if result.success:
                self.show_success_message(f"Datos exportados a: {result.file_path}")
                self.export_completed.emit(result.file_path or "")
                return True
            else:
                self.show_error_message(f"Error exportando: {result.error}")
                return False
                
        except Exception as e:
            self._logger.error(f"❌ Error exportando CSV: {e}")
            self.show_error_message(f"Error exportando CSV: {e}")
            return False
    
    def generate_estado_resultados(self, fecha_desde: str, fecha_hasta: str) -> bool:
        """
        Generar Estado de Resultados para el rango de fechas especificado.
        
        Args:
            fecha_desde: Fecha inicio en formato YYYY-MM-DD
            fecha_hasta: Fecha fin en formato YYYY-MM-DD
            
        Returns:
            bool: True si se generó exitosamente
        """
        try:
            self._logger.info(f"🔄 Generando Estado de Resultados: {fecha_desde} - {fecha_hasta}")
            
            # Validar conexión
            if not self._invoice_repository.is_connected():
                self._logger.error("❌ No hay conexión con Siigo API")
                self.show_error_message("No se puede generar el reporte. Verifique la conexión con Siigo API.")
                return False
            
            # Obtener facturas del período
            from datetime import datetime
            fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d")
            fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            
            filtro = InvoiceFilter(
                created_start=fecha_desde_dt,
                created_end=fecha_hasta_dt
            )
            
            facturas = self._invoice_repository.get_invoices(filtro)
            
            if not facturas:
                self._logger.warning("⚠️ No se encontraron facturas para el período especificado")
                self.show_info_message("No se encontraron facturas para el período especificado.")
                return False
            
            # Procesar datos para estado de resultados
            estado_resultados = self._process_estado_resultados(facturas, fecha_desde, fecha_hasta)
            
            # Generar archivo usando export_service
            filename = f"estado_resultados_Período_{fecha_desde}_-_{fecha_hasta}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            result = self._export_service.export_json_real(
                data=estado_resultados,
                filename=filename
            )
            
            if result.success:
                summary = f"Estado de Resultados generado: {len(facturas)} facturas procesadas"
                self._logger.info(f"✅ {summary}")
                self.show_success_message(f"Estado de Resultados generado exitosamente:\n{result.file_path}")
                self.estado_resultados_generated.emit(result.file_path or "", summary)
                return True
            else:
                self._logger.error(f"❌ Error generando estado de resultados: {result.error}")
                self.show_error_message(f"Error generando estado de resultados: {result.error}")
                return False
                
        except Exception as e:
            self._logger.error(f"❌ Error generando Estado de Resultados: {e}")
            self.show_error_message(f"Error generando Estado de Resultados: {e}")
            return False
    
    def handle_estado_resultados_request(self, fecha_desde: QDate, fecha_hasta: QDate) -> None:
        """
        Manejar solicitud de estado de resultados desde widget (wrapper para QDate).
        
        Args:
            fecha_desde: Fecha inicio como QDate
            fecha_hasta: Fecha fin como QDate
        """
        try:
            # Convertir QDate a string
            fecha_desde_str = fecha_desde.toString("yyyy-MM-dd")
            fecha_hasta_str = fecha_hasta.toString("yyyy-MM-dd")
            
            # Llamar al método principal
            self.generate_estado_resultados(fecha_desde_str, fecha_hasta_str)
            
        except Exception as e:
            self._logger.error(f"❌ Error manejando solicitud de estado de resultados: {e}")
            self.show_error_message(f"Error procesando solicitud: {e}")
    
    def handle_estado_resultados_excel_request(self, 
                                                   fecha_desde: QDate, 
                                                   fecha_hasta: QDate,
                                                   tipo_comparacion: str = "SIN_COMPARACION",
                                                   fecha_desde_comp: Optional[QDate] = None,
                                                   fecha_hasta_comp: Optional[QDate] = None) -> None:
        """
        Manejar solicitud de Estado de Resultados en Excel desde widget.
        
        Args:
            fecha_desde: Fecha inicio período actual como QDate
            fecha_hasta: Fecha fin período actual como QDate
            tipo_comparacion: Tipo de comparación (enum)
            fecha_desde_comp: Fecha inicio período comparación (opcional)
            fecha_hasta_comp: Fecha fin período comparación (opcional)
        """
        print(f"DEBUG: 🎯 CONTROLADOR - handle_estado_resultados_excel_request llamado! Fechas: {fecha_desde.toString('dd/MM/yyyy')} - {fecha_hasta.toString('dd/MM/yyyy')}")  # Debug temporal
        print(f"DEBUG: 🔍 Tipo comparación recibido: '{tipo_comparacion}'")  # Debug nuevo
        print(f"DEBUG: 🗓️ Fechas comparación: {fecha_desde_comp} - {fecha_hasta_comp}")  # Debug nuevo
        
        # Show loading indicator
        if hasattr(self._gui_reference, 'show_loading'):
            self._gui_reference.show_loading("📊 Generando Estado de Resultados Excel...")
        
        # Usar asyncio para ejecutar el método asincrónico
        import asyncio
        try:
            # Crear un nuevo loop si no existe uno
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Ejecutar el método asincrónico
            loop.run_until_complete(
                self._handle_estado_resultados_excel_async(
                    fecha_desde, fecha_hasta, tipo_comparacion, 
                    fecha_desde_comp, fecha_hasta_comp
                )
            )
        except Exception as e:
            # Hide loading indicator in case of error
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            print(f"DEBUG: ❌ Error en controlador: {e}")  # Debug temporal
            self._logger.error(f"❌ Error en handle_estado_resultados_excel_request: {e}")
            self.show_error_message(f"Error procesando solicitud de Estado de Resultados Excel: {e}")
    
    async def _handle_estado_resultados_excel_async(self, 
                                                   fecha_desde: QDate, 
                                                   fecha_hasta: QDate,
                                                   tipo_comparacion: str = "SIN_COMPARACION",
                                                   fecha_desde_comp: Optional[QDate] = None,
                                                   fecha_hasta_comp: Optional[QDate] = None) -> None:
        """
        Método asincrónico interno para manejar Estado de Resultados en Excel.
        """
        try:
            self._logger.info("📊 Iniciando generación de Estado de Resultados Excel")
            
            # Update loading message
            if hasattr(self._gui_reference, 'update_loading_message'):
                self._gui_reference.update_loading_message("📊 Preparando Estado de Resultados...")
            
            # Importar ReportService y excepciones
            from src.application.services.report_service import ReportService
            from src.domain.exceptions.estado_resultados_exceptions import (
                EstadoResultadosError, SiigoAPIError, DataValidationError, 
                ExcelGenerationError, DateRangeError
            )
            
            # Crear instancia del servicio
            report_service = ReportService(self._invoice_repository, self._logger, self._file_storage)
            
            # Update loading message
            if hasattr(self._gui_reference, 'update_loading_message'):
                self._gui_reference.update_loading_message("🗓️ Procesando fechas...")
            
            # Convertir QDate a datetime
            fecha_desde_dt = datetime.strptime(fecha_desde.toString("yyyy-MM-dd"), "%Y-%m-%d")
            fecha_hasta_dt = datetime.strptime(fecha_hasta.toString("yyyy-MM-dd"), "%Y-%m-%d")
            
            fecha_desde_comp_dt = None
            fecha_hasta_comp_dt = None
            
            if fecha_desde_comp and fecha_desde_comp.isValid():
                fecha_desde_comp_dt = datetime.strptime(fecha_desde_comp.toString("yyyy-MM-dd"), "%Y-%m-%d")
            if fecha_hasta_comp and fecha_hasta_comp.isValid():
                fecha_hasta_comp_dt = datetime.strptime(fecha_hasta_comp.toString("yyyy-MM-dd"), "%Y-%m-%d")
            
            # Update loading message
            if hasattr(self._gui_reference, 'update_loading_message'):
                self._gui_reference.update_loading_message("📡 Descargando datos contables...")
            
            # Generar Estado de Resultados Excel
            file_path = await report_service.generar_estado_resultados_excel(
                fecha_desde_dt,
                fecha_hasta_dt,
                tipo_comparacion,
                fecha_desde_comp_dt,
                fecha_hasta_comp_dt
            )
            
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
            
            # Emitir señal de éxito
            self.estado_resultados_generated.emit(
                file_path, 
                f"Estado de Resultados Excel generado para período {fecha_desde.toString('dd/MM/yyyy')} - {fecha_hasta.toString('dd/MM/yyyy')}"
            )
            
            self._logger.info(f"✅ Estado de Resultados Excel generado exitosamente: {file_path}")
            
        except DateRangeError as e:
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            error_msg = f"Rango de fechas inválido: {e.message}"
            if e.details:
                error_msg += f" ({e.details})"
            self._logger.error(f"❌ {error_msg}")
            self.show_error_message(error_msg)
            
        except SiigoAPIError as e:
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            error_msg = f"Error de Siigo API: {e.message}"
            if e.details:
                error_msg += f"\n\nDetalles técnicos: {e.details}"
            self._logger.error(f"❌ {error_msg}")
            self.show_error_message(f"Error de conexión con Siigo API:\n{e.message}")
            
        except DataValidationError as e:
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            error_msg = f"Error en validación de datos: {e.message}"
            if e.details:
                error_msg += f" ({e.details})"
            self._logger.error(f"❌ {error_msg}")
            self.show_error_message(f"Los datos contables no son válidos:\n{e.message}")
            
        except ExcelGenerationError as e:
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            error_msg = f"Error generando archivo Excel: {e.message}"
            if e.details:
                error_msg += f" ({e.details})"
            self._logger.error(f"❌ {error_msg}")
            self.show_error_message(f"No se pudo generar el archivo Excel:\n{e.message}")
            
        except EstadoResultadosError as e:
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            error_msg = f"Error en Estado de Resultados: {e.message}"
            if e.details:
                error_msg += f" ({e.details})"
            self._logger.error(f"❌ {error_msg}")
            self.show_error_message(f"Error generando Estado de Resultados:\n{e.message}")
            
        except Exception as e:
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            self._logger.error(f"❌ Error inesperado generando Estado de Resultados Excel: {e}")
            self.show_error_message(f"Error inesperado generando Estado de Resultados Excel: {e}")
    
    def _process_estado_resultados(self, facturas: List, fecha_desde: str, fecha_hasta: str) -> Dict[str, Any]:
        """
        Procesar facturas para generar estructura de estado de resultados.
        
        Args:
            facturas: Lista de facturas obtenidas de Siigo (Invoice objects)
            fecha_desde: Fecha inicio del período
            fecha_hasta: Fecha fin del período
            
        Returns:
            Dict con estructura de estado de resultados
        """
        from src.domain.entities.invoice import Invoice
        
        total_ingresos = 0
        total_impuestos = 0
        facturas_procesadas = []
        
        for factura in facturas:
            # Verificar si es una Invoice entity o un dict
            if isinstance(factura, Invoice):
                # Procesar Invoice entity - mantener consistencia de tipos usando Decimal
                from decimal import Decimal
                
                # Calcular subtotal (suma de items sin impuestos)
                subtotal_decimal = factura.calculate_total() or Decimal('0')
                
                # Obtener total de la factura (con impuestos)
                total_decimal = factura.total or subtotal_decimal
                
                # Calcular impuestos como diferencia
                impuestos_decimal = total_decimal - subtotal_decimal if total_decimal > subtotal_decimal else Decimal('0')
                
                # Convertir a float solo para almacenamiento final
                subtotal = float(subtotal_decimal)
                total_factura = float(total_decimal)
                impuestos = float(impuestos_decimal)
                
                total_ingresos += subtotal
                total_impuestos += impuestos
                
                facturas_procesadas.append({
                    'numero': str(factura.number or ''),
                    'fecha': factura.date.isoformat() if factura.date else '',
                    'cliente': factura.customer.identification if factura.customer else '',
                    'subtotal': subtotal,
                    'impuestos': impuestos,
                    'total': total_factura
                })
            else:
                # Fallback para dict (compatibilidad)
                subtotal = float(factura.get('subtotal', 0)) if isinstance(factura, dict) else 0
                impuestos = float(factura.get('total_tax', 0)) if isinstance(factura, dict) else 0
                total_factura = float(factura.get('total', 0)) if isinstance(factura, dict) else 0
                
                total_ingresos += subtotal
                total_impuestos += impuestos
                
                facturas_procesadas.append({
                    'numero': factura.get('number', '') if isinstance(factura, dict) else str(factura),
                    'fecha': factura.get('date', '') if isinstance(factura, dict) else '',
                    'cliente': factura.get('customer', {}).get('identification', '') if isinstance(factura, dict) else '',
                    'subtotal': subtotal,
                    'impuestos': impuestos,
                    'total': total_factura
                })
        
        return {
            'metadata': {
                'tipo_reporte': 'Estado de Resultados',
                'fecha_generacion': datetime.now().isoformat(),
                'periodo': {
                    'fecha_inicio': fecha_desde,
                    'fecha_fin': fecha_hasta
                },
                'total_facturas': len(facturas)
            },
            'resumen_financiero': {
                'ingresos_brutos': total_ingresos,
                'total_impuestos': total_impuestos,
                'ingresos_netos': total_ingresos - total_impuestos,
                'promedio_factura': total_ingresos / len(facturas) if facturas else 0
            },
            'detalle_facturas': facturas_procesadas,
            'analisis': {
                'factura_mayor': max(facturas_procesadas, key=lambda x: x['total']) if facturas_procesadas else None,
                'factura_menor': min(facturas_procesadas, key=lambda x: x['total']) if facturas_procesadas else None,
                'distribucion_impuestos': {
                    'porcentaje_impuestos': (total_impuestos / (total_ingresos + total_impuestos) * 100) if total_ingresos > 0 else 0
                }
            }
        }
    
    def export_to_excel(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """Exportar datos a Excel."""
        try:
            # Usar ExportService - método Siigo sin parámetros específicos de data
            result = self._export_service.export_siigo_invoices_to_excel()
            
            if result.success:
                self.show_success_message(f"Datos exportados a: {result.file_path}")
                self.export_completed.emit(result.file_path or "")
                return True
            else:
                self.show_error_message(f"Error exportando: {result.error}")
                return False
                
        except Exception as e:
            self._logger.error(f"❌ Error exportando Excel: {e}")
            self.show_error_message(f"Error exportando Excel: {e}")
            return False
    
    def save_report(self, report_data: Dict[str, Any], format_type: str) -> bool:
        """Guardar reporte."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_dataconta_free_{timestamp}"
            
            if format_type.lower() == "csv":
                return self.export_to_csv([report_data], filename + ".csv")
            elif format_type.lower() == "excel":
                return self.export_to_excel([report_data], filename + ".xlsx")
            else:
                self.show_error_message(f"Formato no soportado: {format_type}")
                return False
                
        except Exception as e:
            self._logger.error(f"❌ Error guardando reporte: {e}")
            return False
    
    # ==================== Métodos específicos del controlador ====================
    
    def authenticate_and_load_data(self) -> None:
        """Autenticar con API y cargar datos."""
        try:
            self._logger.info("🔐 Iniciando autenticación y carga de datos")
            
            # Intentar autenticación
            if not self._invoice_repository.is_connected():
                if not self._invoice_repository.authenticate():
                    self.show_error_message("Error de autenticación con Siigo API")
                    return
            
            # Cargar datos con filtros básicos
            from datetime import datetime
            filters = InvoiceFilter(
                created_start=datetime(2024, 1, 1),
                created_end=datetime.now()
            )
            
            self._invoices_data = self._invoice_repository.get_invoices(filters)
            
            if self._invoices_data:
                self.show_success_message(f"✅ {len(self._invoices_data)} facturas cargadas")
                self.refresh_data_display()
            else:
                self.show_warning_message("No se encontraron facturas")
                
        except Exception as e:
            self._logger.error(f"❌ Error autenticando y cargando datos: {e}")
            self.show_error_message(f"Error cargando datos: {e}")
    
    def calculate_kpis(self) -> None:
        """Calcular KPIs usando el servicio."""
        try:
            if not self._invoices_data:
                self.show_warning_message("Primero debe cargar los datos")
                return
            
            self._logger.info("📊 Calculando KPIs")
            
            # Usar KPIService
            self._current_kpis = self._kpi_service.calculate_real_kpis(self._invoices_data)
            
            if self._current_kpis:
                self.update_summary_stats(self._current_kpis.to_dict())
                self.kpis_calculated.emit(self._current_kpis.to_dict())
                self.show_success_message("KPIs calculados correctamente")
            else:
                self.show_error_message("Error calculando KPIs")
                
        except Exception as e:
            self._logger.error(f"❌ Error calculando KPIs: {e}")
            self.show_error_message(f"Error calculando KPIs: {e}")
    
    def export_data(self) -> None:
        """Exportar datos actuales."""
        try:
            if not self._invoices_data:
                self.show_warning_message("No hay datos para exportar")
                return
            
            # Convertir invoices a dict para exportación
            export_data = []
            for invoice in self._invoices_data:
                export_data.append({
                    'id': invoice.id,
                    'fecha': invoice.date,
                    'cliente': invoice.customer.name,
                    'nit': invoice.customer.identification,
                    'total': invoice.total,
                    'estado': invoice.status
                })
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"facturas_dataconta_free_{timestamp}.csv"
            
            success = self.export_to_csv(export_data, filename)
            
            if not success:
                self.show_error_message("Error exportando datos")
                
        except Exception as e:
            self._logger.error(f"❌ Error exportando datos: {e}")
            self.show_error_message(f"Error exportando datos: {e}")
    
    def show_visualizations(self) -> None:
        """Mostrar visualizaciones."""
        try:
            if not self._current_kpis:
                self.show_warning_message("Primero debe calcular los KPIs")
                return
            
            # Preparar datos para gráficos
            chart_data = {
                'ventas_totales': self._current_kpis.ventas_totales_mes,
                'facturas_emitidas': self._current_kpis.facturas_emitidas,
                'clientes_activos': self._current_kpis.clientes_activos,
                'ticket_promedio': self._current_kpis.ticket_promedio
            }
            
            self.show_chart(chart_data, "dashboard")
            
        except Exception as e:
            self._logger.error(f"❌ Error mostrando visualizaciones: {e}")
            self.show_error_message(f"Error mostrando visualizaciones: {e}")
    
    def refresh_kpis(self) -> None:
        """Refrescar KPIs - replicar funcionalidad exacta de dataconta_free_gui.py."""
        try:
            # Show loading indicator
            print(f"🔍 refresh_kpis: _gui_reference type: {type(self._gui_reference)}")
            print(f"🔍 refresh_kpis: hasattr show_loading: {hasattr(self._gui_reference, 'show_loading')}")
            if hasattr(self._gui_reference, 'show_loading'):
                print("🔄 Calling show_loading...")
                self._gui_reference.show_loading("📊 Calculando KPIs...")
                print("✅ show_loading called successfully")
                
            self._logger.info("� Calculando KPIs reales desde Siigo API...")
            
            # Eliminar archivos JSON de KPIs anteriores (como en FREE GUI)
            self._delete_old_kpis()
            
            # Calcular KPIs usando la misma lógica que FREE GUI
            kpis_data = self._calculate_real_kpis_like_free_gui()
            
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
            
            if kpis_data:
                self._logger.info("✅ KPIs calculados exitosamente, emitiendo señal...")
                # Emitir señal con los KPIs calculados
                self.kpis_calculated.emit(kpis_data)
                self._logger.info("📡 Señal kpis_calculated emitida")
                
                # Mostrar mensaje de éxito (como en FREE GUI)
                success_message = (
                    f"✅ KPIs calculados y actualizados en dashboard!\n\n"
                    f"💰 Ventas Totales: ${kpis_data.get('ventas_totales', 0):,.0f}\n"
                    f"📄 Total Facturas: {kpis_data.get('num_facturas', 0):,}\n"
                    f"🎯 Ticket Promedio: ${kpis_data.get('ticket_promedio', 0):,.0f}\n"
                    f"👤 Top Cliente: {kpis_data.get('top_cliente', 'N/A')[:30]}\n\n"
                    f"📁 KPIs guardados en: outputs/kpis/"
                )
                self._logger.info(f"💬 Mostrando mensaje de éxito: {len(success_message)} caracteres")
                self.show_success_message(success_message)
            else:
                self._logger.error("❌ kpis_data es None o vacío")
                self.show_error_message("❌ Error calculando KPIs reales")
                
        except Exception as e:
            # Hide loading indicator in case of error
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            self._logger.error(f"❌ Error refrescando KPIs: {e}")
            self.show_error_message(f"❌ Error calculando KPIs reales:\n{str(e)}")
    
    def _auto_load_existing_kpis(self) -> None:
        """Cargar KPIs existentes automáticamente al inicializar (sin mostrar mensajes)."""
        try:
            self._logger.info("🔄 Carga automática de KPIs existentes al inicializar")
            
            # Usar QTimer para retrasar ligeramente y permitir que la UI se conecte
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, self._perform_auto_kpi_load)
                
        except Exception as e:
            self._logger.error(f"❌ Error en carga automática de KPIs: {e}")
    
    def _perform_auto_kpi_load(self) -> None:
        """Realizar la carga automática de KPIs después del delay."""
        try:
            # Intentar cargar KPIs desde el servicio
            existing_kpis = self._kpi_service.load_existing_kpis()
            
            if existing_kpis:
                self._current_kpis = existing_kpis
                # Emitir señal sin mostrar mensajes (carga silenciosa)
                self.kpis_calculated.emit(existing_kpis.to_dict())
                self._logger.info(f"✅ KPIs cargados automáticamente: ${existing_kpis.ventas_totales:,.2f}")
            else:
                self._logger.info("📂 No hay KPIs existentes - se mostrarán valores por defecto")
                
        except Exception as e:
            self._logger.error(f"❌ Error en carga automática de KPIs: {e}")
    
    def load_existing_kpis(self) -> None:
        """Cargar KPIs existentes desde archivos almacenados."""
        try:
            self._logger.info("📂 Cargando KPIs existentes")
            
            # Intentar cargar KPIs desde el servicio
            existing_kpis = self._kpi_service.load_existing_kpis()
            
            if existing_kpis:
                self._current_kpis = existing_kpis
                self.update_summary_stats(existing_kpis.to_dict())
                self.kpis_calculated.emit(existing_kpis.to_dict())
                self.show_success_message("KPIs cargados correctamente")
            else:
                self.show_warning_message("No se encontraron KPIs guardados. Calculando nuevos...")
                self.calculate_kpis()
                
        except Exception as e:
            self._logger.error(f"❌ Error cargando KPIs existentes: {e}")
            self.show_error_message(f"Error cargando KPIs: {e}")
    
    def update_summary_stats(self, kpi_data: Dict[str, Any]) -> None:
        """Actualizar estadísticas en la interfaz."""
        try:
            if hasattr(self, '_gui_reference') and self._gui_reference:
                # Llamar al método de actualización de la GUI
                self._gui_reference.update_kpis_display(kpi_data)
                self._logger.info(f"✅ GUI actualizada con KPIs: Ventas ${kpi_data.get('ventas_totales', 0):,.2f}")
            else:
                self._logger.warning("❌ No se puede actualizar GUI: Referencia no establecida")
                
        except Exception as e:
            self._logger.error(f"❌ Error actualizando estadísticas: {e}")
    
    def export_csv_real(self, count: int = 100):
        """Exportar facturas reales a CSV."""
        try:
            # Show loading indicator
            if hasattr(self._gui_reference, 'show_loading'):
                self._gui_reference.show_loading("📊 Exportando facturas a CSV...")
                
            self._logger.info(f"🔄 Iniciando exportación CSV REAL con {count} registros...")
            
            # Update loading message
            if hasattr(self._gui_reference, 'update_loading_message'):
                self._gui_reference.update_loading_message("📡 Obteniendo datos de Siigo...")
            
            # Usar el servicio de exportación existente
            self._logger.info(f"🔄 Llamando _export_service.export_csv_real({count})...")
            result = self._export_service.export_csv_real(count)
            
            self._logger.info(f"📋 Resultado del servicio: success={result.success}, records={result.records_count}")
            
            if result.success:
                self._logger.info(f"✅ Exportación CSV exitosa: {result.file_path}")
                self.show_success_message(f"Exportación REAL completada: {result.records_count} facturas guardadas en {result.file_path}")
                
                # Hide loading indicator
                if hasattr(self._gui_reference, 'hide_loading'):
                    self._gui_reference.hide_loading()
            else:
                # Hide loading indicator
                if hasattr(self._gui_reference, 'hide_loading'):
                    self._gui_reference.hide_loading()
                    
                self._logger.error(f"❌ Error en servicio CSV: {result.error}")
                self.show_error_message(f"Error durante la exportación CSV: {result.error or 'Error desconocido'}")
                raise Exception(f"Servicio reportó fallo: {result.error}")
                
        except Exception as e:
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            self._logger.error(f"❌ Error exportando CSV: {e}")
            self.show_error_message(f"Error exportando CSV: {e}")
            raise  # Re-lanzar para que la GUI sepa que falló
    
    def export_csv_simple(self):
        """Exportar CSV simple con 5 registros."""
        try:
            self._logger.info("🔄 Iniciando exportación CSV simple REAL...")
            
            self._logger.info("🔄 Llamando _export_service.export_csv_simple_real()...")
            result = self._export_service.export_csv_simple_real()
            
            self._logger.info(f"📋 Resultado del servicio simple: success={result.success}, records={result.records_count}")
            
            if result.success:
                self._logger.info(f"✅ Exportación CSV simple exitosa: {result.file_path}")
                self.show_success_message(f"Exportación simple REAL completada: {result.records_count} facturas guardadas en {result.file_path}")
            else:
                self._logger.error(f"❌ Error en servicio CSV simple: {result.error}")
                self.show_error_message(f"Error durante la exportación simple: {result.error or 'Error desconocido'}")
                raise Exception(f"Servicio simple reportó fallo: {result.error}")
        
        except Exception as e:
            self._logger.error(f"❌ Error exportación simple: {e}")
            self.show_error_message(f"Error en exportación simple: {e}")
            raise  # Re-lanzar para que la GUI sepa que falló
    
    def export_excel_real(self, count: int = 100):
        """Exportar facturas reales a Excel usando datos de Siigo."""
        try:
            # Show loading indicator
            if hasattr(self._gui_reference, 'show_loading'):
                self._gui_reference.show_loading("📊 Exportando facturas a Excel...")
                
            self._logger.info(f"🔄 Iniciando exportación Excel con {count} registros...")
            
            # Update loading message
            if hasattr(self._gui_reference, 'update_loading_message'):
                self._gui_reference.update_loading_message("📡 Obteniendo datos de Siigo...")
            
            # Usar el método de CSV real del servicio que sí funciona con limit
            result = self._export_service.export_csv_real(count)
            
            if result.success:
                # Update loading message
                if hasattr(self._gui_reference, 'update_loading_message'):
                    self._gui_reference.update_loading_message("💾 Generando archivo Excel...")
                    
                # Ahora convertir el CSV a Excel
                try:
                    import pandas as pd
                    from datetime import datetime
                    
                    # Leer el CSV generado
                    df = pd.read_csv(result.file_path)
                    
                    # Crear archivo Excel
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    excel_filename = f"outputs/facturas_reales_FREE_{count}_{timestamp}.xlsx"
                    
                    # Guardar como Excel con formato
                    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Facturas Reales', index=False)
                        
                        # Agregar hoja de resumen
                        summary_data = {
                            'Métrica': ['Total Facturas', 'Valor Total', 'Promedio por Factura'],
                            'Valor': [
                                len(df),
                                f"${df['total'].str.replace(',', '').astype(float).sum():,.0f}" if 'total' in df.columns else "N/A",
                                f"${df['total'].str.replace(',', '').astype(float).mean():,.0f}" if 'total' in df.columns else "N/A"
                            ]
                        }
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    self._logger.info(f"✅ Exportación Excel exitosa: {excel_filename}")
                    self.show_success_message(f"Exportación Excel REAL completada: {result.records_count} facturas guardadas en {excel_filename}")
                    
                    # Hide loading indicator
                    if hasattr(self._gui_reference, 'hide_loading'):
                        self._gui_reference.hide_loading()
                    
                except Exception as excel_error:
                    # Hide loading indicator
                    if hasattr(self._gui_reference, 'hide_loading'):
                        self._gui_reference.hide_loading()
                        
                    self._logger.error(f"❌ Error convirtiendo a Excel: {excel_error}")
                    self.show_success_message(f"Exportación CSV exitosa (Excel falló): {result.records_count} facturas guardadas en {result.file_path}")
                    
            else:
                # Hide loading indicator
                if hasattr(self._gui_reference, 'hide_loading'):
                    self._gui_reference.hide_loading()
                    
                self.show_error_message(f"Error durante la exportación: {result.error or 'Error desconocido'}")
                
        except Exception as e:
            # Hide loading indicator
            if hasattr(self._gui_reference, 'hide_loading'):
                self._gui_reference.hide_loading()
                
            self._logger.error(f"❌ Error exportando Excel: {e}")
            self.show_error_message(f"Error exportando Excel: {e}")
            raise  # Re-lanzar para que la GUI sepa que falló

    # ==================== Métodos con Filtros ====================

    def export_csv_real_with_filters(self, count: int, fecha_inicio: str = None, fecha_fin: str = None, cliente_filtro: str = None):
        """Exportar facturas reales a CSV con filtros aplicados."""
        try:
            self._logger.info(f"🔄 Iniciando exportación CSV REAL con filtros: count={count}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}, cliente={cliente_filtro}")
            
            # Validar filtros
            filter_info = []
            if fecha_inicio:
                filter_info.append(f"Desde: {fecha_inicio}")
            if fecha_fin:
                filter_info.append(f"Hasta: {fecha_fin}")
            if cliente_filtro:
                filter_info.append(f"Cliente: {cliente_filtro}")
            
            self._logger.info(f"📋 Filtros aplicados: {', '.join(filter_info) if filter_info else 'Sin filtros'}")
            
            # Si no hay filtros, usar método normal
            if not (fecha_inicio or fecha_fin or cliente_filtro):
                self._logger.info("🔄 Sin filtros especificados, usando método regular...")
                return self.export_csv_real(count)
            
            # Usar el servicio de exportación con filtros
            from ...domain.entities.invoice import InvoiceFilter
            from datetime import datetime
            
            # Convertir strings de fecha a datetime si están presentes
            created_start = None
            created_end = None
            
            if fecha_inicio:
                try:
                    created_start = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                except ValueError:
                    self._logger.warning(f"Formato de fecha inicio inválido: {fecha_inicio}")
                    
            if fecha_fin:
                try:
                    created_end = datetime.strptime(fecha_fin, '%Y-%m-%d')
                except ValueError:
                    self._logger.warning(f"Formato de fecha fin inválido: {fecha_fin}")
            
            invoice_filter = InvoiceFilter(
                created_start=created_start,
                created_end=created_end,
                page_size=count
            )
            
            # Nota: client_name no está soportado en InvoiceFilter actual
            if cliente_filtro:
                self._logger.info(f"📋 Filtro de cliente '{cliente_filtro}' registrado pero no aplicado (no soportado por InvoiceFilter)")
            
            self._logger.info(f"🔄 Llamando _export_service.export_csv_real({count}) con filtros...")
            result = self._export_service.export_csv_real(count, invoice_filter)
            
            self._logger.info(f"📋 Resultado del servicio con filtros: success={result.success}, records={result.records_count}")
            
            if result.success:
                self._logger.info(f"✅ Exportación CSV con filtros exitosa: {result.file_path}")
                filter_summary = ', '.join(filter_info) if filter_info else 'Sin filtros'
                self.show_success_message(f"Exportación REAL con filtros completada: {result.records_count} facturas guardadas en {result.file_path}\\n\\nFiltros: {filter_summary}")
            else:
                self._logger.error(f"❌ Error en servicio CSV con filtros: {result.error}")
                self.show_error_message(f"Error durante la exportación con filtros: {result.error or 'Error desconocido'}")
                raise Exception(f"Servicio con filtros reportó fallo: {result.error}")
                
        except Exception as e:
            self._logger.error(f"❌ Error exportando CSV con filtros: {e}")
            self.show_error_message(f"Error exportando CSV con filtros: {e}")
            raise

    def export_excel_real_with_filters(self, count: int, fecha_inicio: str = None, fecha_fin: str = None, cliente_filtro: str = None):
        """Exportar facturas reales a Excel con filtros aplicados."""
        try:
            self._logger.info(f"🔄 Iniciando exportación Excel REAL con filtros: count={count}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}, cliente={cliente_filtro}")
            
            # Validar filtros
            filter_info = []
            if fecha_inicio:
                filter_info.append(f"Desde: {fecha_inicio}")
            if fecha_fin:
                filter_info.append(f"Hasta: {fecha_fin}")
            if cliente_filtro:
                filter_info.append(f"Cliente: {cliente_filtro}")
            
            self._logger.info(f"📋 Filtros aplicados: {', '.join(filter_info) if filter_info else 'Sin filtros'}")
            
            # Si no hay filtros, usar método normal
            if not (fecha_inicio or fecha_fin or cliente_filtro):
                self._logger.info("🔄 Sin filtros especificados, usando método Excel regular...")
                return self.export_excel_real(count)
            
            # Usar el servicio de exportación con filtros (primero CSV, luego convertir)
            from ...domain.entities.invoice import InvoiceFilter
            from datetime import datetime
            
            # Convertir strings de fecha a datetime si están presentes
            created_start = None
            created_end = None
            
            if fecha_inicio:
                try:
                    created_start = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                except ValueError:
                    self._logger.warning(f"Formato de fecha inicio inválido: {fecha_inicio}")
                    
            if fecha_fin:
                try:
                    created_end = datetime.strptime(fecha_fin, '%Y-%m-%d')
                except ValueError:
                    self._logger.warning(f"Formato de fecha fin inválido: {fecha_fin}")
            
            invoice_filter = InvoiceFilter(
                created_start=created_start,
                created_end=created_end,
                page_size=count
            )
            
            # Nota: client_name no está soportado en InvoiceFilter actual
            if cliente_filtro:
                self._logger.info(f"📋 Filtro de cliente '{cliente_filtro}' registrado pero no aplicado (no soportado por InvoiceFilter)")
            
            self._logger.info(f"🔄 Llamando _export_service.export_csv_real({count}) con filtros para conversión Excel...")
            result = self._export_service.export_csv_real(count, invoice_filter)
            
            if result.success:
                # Ahora convertir el CSV filtrado a Excel
                try:
                    import pandas as pd
                    from datetime import datetime
                    
                    # Leer el CSV generado
                    df = pd.read_csv(result.file_path)
                    
                    # Crear archivo Excel con información de filtros
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    excel_filename = f"outputs/facturas_reales_filtradas_FREE_{count}_{timestamp}.xlsx"
                    
                    # Guardar como Excel con formato
                    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Facturas Filtradas', index=False)
                        
                        # Agregar hoja de resumen con filtros
                        summary_data = {
                            'Métrica': ['Total Facturas', 'Valor Total', 'Promedio por Factura', 'Filtros Aplicados'],
                            'Valor': [
                                len(df),
                                f"${df['total'].str.replace(',', '').astype(float).sum():,.0f}" if 'total' in df.columns else "N/A",
                                f"${df['total'].str.replace(',', '').astype(float).mean():,.0f}" if 'total' in df.columns else "N/A",
                                ', '.join(filter_info) if filter_info else 'Sin filtros'
                            ]
                        }
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    self._logger.info(f"✅ Exportación Excel con filtros exitosa: {excel_filename}")
                    filter_summary = ', '.join(filter_info) if filter_info else 'Sin filtros'
                    self.show_success_message(f"Exportación Excel REAL con filtros completada: {result.records_count} facturas guardadas en {excel_filename}\\n\\nFiltros: {filter_summary}")
                    
                except Exception as excel_error:
                    self._logger.error(f"❌ Error convirtiendo CSV filtrado a Excel: {excel_error}")
                    filter_summary = ', '.join(filter_info) if filter_info else 'Sin filtros'
                    self.show_success_message(f"Exportación CSV con filtros exitosa (Excel falló): {result.records_count} facturas guardadas en {result.file_path}\\n\\nFiltros: {filter_summary}")
                    
            else:
                self._logger.error(f"❌ Error en servicio con filtros para Excel: {result.error}")
                self.show_error_message(f"Error durante la exportación Excel con filtros: {result.error or 'Error desconocido'}")
                raise Exception(f"Servicio con filtros para Excel reportó fallo: {result.error}")
                
        except Exception as e:
            self._logger.error(f"❌ Error exportando Excel con filtros: {e}")
            self.show_error_message(f"Error exportando Excel con filtros: {e}")
            raise

    def export_siigo_csv_with_filters(self, fecha_inicio: str = None, fecha_fin: str = None):
        """Exportar desde Siigo API a CSV con filtros de fecha específicos."""
        try:
            self._logger.info(f"🔄 Iniciando exportación Siigo CSV con filtros: fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}")
            
            # Usar método con filtros pero con cantidad predeterminada para Siigo
            self.export_csv_real_with_filters(100, fecha_inicio, fecha_fin, None)
            
        except Exception as e:
            self._logger.error(f"❌ Error exportando Siigo CSV con filtros: {e}")
            self.show_error_message(f"Error exportando desde API Siigo (CSV): {e}")
            raise

    def export_siigo_excel_with_filters(self, fecha_inicio: str = None, fecha_fin: str = None):
        """Exportar desde Siigo API a Excel con filtros de fecha específicos."""
        try:
            self._logger.info(f"🔄 Iniciando exportación Siigo Excel con filtros: fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}")
            
            # Usar método con filtros pero con cantidad predeterminada para Siigo
            self.export_excel_real_with_filters(100, fecha_inicio, fecha_fin, None)
            
        except Exception as e:
            self._logger.error(f"❌ Error exportando Siigo Excel con filtros: {e}")
            self.show_error_message(f"Error exportando desde API Siigo (Excel): {e}")
            raise
    
    # ==================== KPIs Methods (FREE GUI Compatible) ====================
    
    def _delete_old_kpis(self) -> None:
        """Eliminar archivos JSON de KPIs anteriores (replicar FREE GUI)."""
        try:
            import os
            import glob
            
            kpis_dir = "outputs/kpis"
            if os.path.exists(kpis_dir):
                # Buscar todos los archivos KPIs anteriores
                pattern = os.path.join(kpis_dir, "kpis_siigo_*.json")
                old_files = glob.glob(pattern)
                
                for file_path in old_files:
                    try:
                        os.remove(file_path)
                        self._logger.info(f"🗑️  Archivo KPI antiguo eliminado: {os.path.basename(file_path)}")
                    except Exception as e:
                        self._logger.warning(f"⚠️  No se pudo eliminar {file_path}: {e}")
                        
                if old_files:
                    self._logger.info(f"🧹 {len(old_files)} archivos KPI antiguos procesados")
                    
        except Exception as e:
            self._logger.error(f"❌ Error eliminando KPIs antiguos: {e}")

    def _calculate_real_kpis_like_free_gui(self) -> Dict[str, Any]:
        """Calcular KPIs reales delegando al servicio de dominio."""
        try:
            self._logger.info("📊 ===== INICIANDO cálculo de KPIs =====")
            
            # Update loading message
            if hasattr(self._gui_reference, 'update_loading_message'):
                self._gui_reference.update_loading_message("📊 Preparando cálculo de KPIs...")
            
            # Configurar rango para año actual
            from datetime import datetime, date
            current_year = date.today().year
            fecha_inicio = datetime(current_year, 1, 1)
            fecha_fin = datetime(current_year, 12, 31)
            
            self._logger.info(f"📊 Calculando KPIs para el año {current_year}...")
            
            # Update loading message
            if hasattr(self._gui_reference, 'update_loading_message'):
                self._gui_reference.update_loading_message("📡 Descargando datos de Siigo API...")
            
            # DELEGAR AL SERVICIO DE APLICACIÓN (que usa el dominio)
            result = self._kpi_service.calculate_kpis_for_period(fecha_inicio, fecha_fin)
            
            # Update loading message
            if hasattr(self._gui_reference, 'update_loading_message'):
                self._gui_reference.update_loading_message("💾 Guardando resultados...")
            
            # Adaptar resultado para compatibilidad con GUI
            kpis = self._adapt_domain_result_to_legacy_format(result)
            
            self._logger.info(f"✅ KPIs calculados: {kpis.get('num_facturas', 0)} facturas")
            self._logger.info("✅ ===== FINALIZANDO cálculo de KPIs =====")
            
            return kpis
            
        except Exception as e:
            self._logger.error(f"❌ Error calculando KPIs: {e}")
            return self._get_default_kpis_like_free_gui()
    
    def _adapt_domain_result_to_legacy_format(self, domain_result: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptar resultado del dominio al formato esperado por la GUI legacy."""
        try:
            # Mapear campos del dominio al formato legacy
            legacy_kpis = {
                'ventas_totales': domain_result.get('ventas_totales', 0),
                'num_facturas': domain_result.get('numero_facturas', 0),
                'ticket_promedio': domain_result.get('ticket_promedio', 0),
                'ultima_sync': datetime.now().strftime("%H:%M:%S"),
                'estado_sistema': domain_result.get('estado_sistema', 'ACTIVO ✅'),
            }
            
            # Procesar ventas por cliente
            ventas_por_cliente = domain_result.get('ventas_por_cliente', [])
            legacy_kpis['ventas_por_cliente'] = [
                {
                    'cliente_nit': cliente['nit'],
                    'cliente_display': cliente['nombre_display'],
                    'total': cliente['total_ventas']
                }
                for cliente in ventas_por_cliente
            ]
            
            # Información del cliente top
            cliente_top = domain_result.get('cliente_top')
            if cliente_top:
                legacy_kpis['top_cliente'] = cliente_top.get('nombre', 'N/A')
                legacy_kpis['top_cliente_monto'] = cliente_top.get('monto', 0)
                legacy_kpis['top_cliente_nit'] = cliente_top.get('nit', '')
            else:
                legacy_kpis['top_cliente'] = 'N/A'
                legacy_kpis['top_cliente_monto'] = 0
                legacy_kpis['top_cliente_nit'] = ''
            
            return legacy_kpis
            
        except Exception as e:
            self._logger.error(f"❌ Error adaptando resultado del dominio: {e}")
            return self._get_default_kpis_like_free_gui()
            return self._get_default_kpis_like_free_gui()
    
    def _get_default_kpis_like_free_gui(self) -> Dict[str, Any]:
        """Obtener KPIs por defecto cuando hay error o no hay datos (igual que FREE GUI)."""
        from datetime import datetime
        return {
            'ventas_totales': 0,
            'num_facturas': 0,
            'ticket_promedio': 0,
            'ventas_por_cliente': [],
            'top_cliente': 'N/A',
            'top_cliente_monto': 0,
            'ultima_sync': datetime.now().strftime("%H:%M:%S"),
            'estado_sistema': 'SIN DATOS ⚠️'
        }
    
    def _save_kpis_to_file_like_free_gui(self, kpis_data: Dict[str, Any], year: int) -> None:
        """Guardar KPIs en archivo JSON (igual que FREE GUI)."""
        try:
            import json
            import os
            from datetime import datetime
            
            # Crear directorio si no existe
            os.makedirs("outputs", exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y_%m%d_%H%M%S")
            filename = f"kpis_siigo_{year}_{timestamp}.json"
            filepath = os.path.join("outputs", filename)
            
            # Guardar KPIs
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(kpis_data, f, ensure_ascii=False, indent=2, default=str)
            
            file_size = os.path.getsize(filepath) / 1024
            self._logger.info(f"💾 KPIs guardados: {filename} ({file_size:.1f} KB)")
            
        except Exception as e:
            self._logger.error(f"❌ Error guardando KPIs: {e}")
    
    def search_invoices_with_pagination(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Buscar facturas con paginación limitada a 500 registros.
        
        Args:
            filters: Filtros de búsqueda (fecha_inicio, fecha_fin, cliente)
            
        Returns:
            Lista de facturas con máximo 500 registros
        """
        try:
            from src.domain.entities.invoice import InvoiceFilter
            from datetime import datetime
            
            self._logger.info(f"🔍 Iniciando búsqueda de facturas con filtros: {filters}")
            
            # Crear filtro para la API
            filtro = InvoiceFilter()
            
            # Mapear filtros del widget a filtros de la API
            if 'fecha_inicio' in filters:
                filtro.created_start = filters['fecha_inicio']
            if 'fecha_fin' in filters:
                filtro.created_end = filters['fecha_fin']
            if 'customer_id' in filters:
                filtro.customer_id = filters['customer_id']
            if 'status' in filters:
                filtro.status = filters['status']
                
            # Configurar paginación (máximo 500 facturas)
            max_facturas = 500
            facturas_encontradas = []
            pagina_actual = 1
            facturas_por_pagina = 100  # API de Siigo máximo 100 por página
            
            while len(facturas_encontradas) < max_facturas:
                # Configurar filtro de página
                filtro.page = pagina_actual
                filtro.page_size = min(facturas_por_pagina, max_facturas - len(facturas_encontradas))
                
                self._logger.info(f"📡 Consultando página {pagina_actual}, {filtro.page_size} registros")
                
                # Obtener facturas de esta página
                facturas_pagina = self._invoice_repository.get_invoices(filtro)
                
                if not facturas_pagina:
                    self._logger.info(f"📄 Página {pagina_actual} vacía, finalizando búsqueda")
                    break
                
                # Filtrar por cliente si se especificó
                if 'cliente' in filters and filters['cliente']:
                    cliente_filtro = filters['cliente'].lower()
                    facturas_pagina = [
                        f for f in facturas_pagina 
                        if f.customer and cliente_filtro in (f.customer.name or '').lower()
                    ]
                
                facturas_encontradas.extend(facturas_pagina)
                self._logger.info(f"✅ Página {pagina_actual}: {len(facturas_pagina)} facturas, total: {len(facturas_encontradas)}")
                
                # Si obtuvimos menos facturas de las esperadas, no hay más páginas
                if len(facturas_pagina) < filtro.page_size:
                    break
                    
                pagina_actual += 1
                
                # Límite de seguridad: máximo 5 páginas (500 facturas)
                if pagina_actual > 5:
                    break
            
            # Convertir entidades Invoice a diccionarios para el widget
            facturas_formateadas = []
            for factura in facturas_encontradas:
                try:
                    factura_dict = {
                        'numero': factura.number or 'N/A',
                        'fecha': factura.date.strftime('%Y-%m-%d') if factura.date else 'N/A',
                        'cliente': factura.customer.name if factura.customer else 'N/A',
                        'monto': float(factura.total) if factura.total else 0.0,
                        'estado': 'Activa'  # Por simplicidad en versión FREE
                    }
                    facturas_formateadas.append(factura_dict)
                except Exception as e:
                    self._logger.warning(f"⚠️ Error formateando factura {factura.id}: {e}")
                    continue
            
            self._logger.info(f"✅ Búsqueda completada: {len(facturas_formateadas)} facturas encontradas")
            return facturas_formateadas
            
        except Exception as e:
            self._logger.error(f"❌ Error en búsqueda de facturas: {e}")
            return []

    def _save_kpis_to_file_like_free_gui(self, kpis_data: dict, year: int) -> None:
        """Guardar KPIs en archivo JSON replicando formato de dataconta_free_gui.py."""
        try:
            import os
            import json
            from datetime import datetime
            
            # Crear directorio si no existe
            kpis_dir = "outputs/kpis"
            os.makedirs(kpis_dir, exist_ok=True)
            
            # Nombre de archivo con timestamp (igual que FREE GUI)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{kpis_dir}/kpis_siigo_{year}_{timestamp}.json"
            
            # Agregar metadatos (igual que FREE GUI)
            kpis_with_meta = {
                'metadata': {
                    'generado_en': datetime.now().isoformat(),
                    'año': year,
                    'version': 'DataConta Hexagonal v1.0',
                    'fuente': 'API Siigo'
                },
                'kpis': kpis_data
            }
            
            # Guardar archivo
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(kpis_with_meta, f, indent=2, ensure_ascii=False, default=str)
            
            file_size = os.path.getsize(filename) / 1024
            self._logger.info(f"💾 KPIs guardados: {filename} ({file_size:.1f} KB)")
            
        except Exception as e:
            self._logger.error(f"❌ Error guardando KPIs: {e}")
    
    def load_customers_for_dropdown(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Cargar lista de clientes desde API Siigo para dropdown.
        Limitado para versión FREE.
        
        Args:
            limit: Máximo número de clientes (FREE: 50)
            
        Returns:
            Lista de diccionarios con datos de clientes
        """
        try:
            self._logger.info(f"🔄 Cargando clientes para dropdown (límite: {limit})")
            
            # Verificar si el adaptador soporta el método get_customers
            if hasattr(self._invoice_repository, 'get_customers'):
                customers = self._invoice_repository.get_customers(limit)
                self._logger.info(f"✅ Cargados {len(customers)} clientes desde API")
                return customers
            else:
                self._logger.warning("⚠️ Adaptador no soporta get_customers")
                return []
                
        except Exception as e:
            self._logger.error(f"❌ Error cargando clientes: {e}")
            return []
    
    def load_invoice_statuses(self) -> List[Dict[str, str]]:
        """
        Cargar estados disponibles para facturas.
        
        Returns:
            Lista de diccionarios con value y label de estados
        """
        try:
            self._logger.info("🔄 Cargando estados de facturas")
            
            # Verificar si el adaptador soporta el método get_invoice_statuses
            if hasattr(self._invoice_repository, 'get_invoice_statuses'):
                statuses = self._invoice_repository.get_invoice_statuses()
                self._logger.info(f"✅ Cargados {len(statuses)} estados desde API")
                return statuses
            else:
                # Estados por defecto si no hay soporte
                default_statuses = [
                    {'value': '', 'label': 'Todos los Estados'},
                    {'value': 'open', 'label': '🔓 Abierta'},
                    {'value': 'closed', 'label': '🔒 Cerrada'},
                    {'value': 'cancelled', 'label': '❌ Anulada'}
                ]
                self._logger.info(f"ℹ️ Usando estados por defecto: {len(default_statuses)}")
                return default_statuses
                
        except Exception as e:
            self._logger.error(f"❌ Error cargando estados: {e}")
            return [{'value': '', 'label': 'Todos los Estados'}]
    
    # ==================== Sistema de Seguridad API ====================
    
    def _setup_api_security(self):
        """Configurar sistema de seguridad para operaciones API peligrosas."""
        try:
            # Verificar si el adaptador soporta seguridad
            if hasattr(self._invoice_repository, 'set_safety_callback'):
                self._invoice_repository.set_safety_callback(self._confirm_dangerous_operation)
                self._logger.info("🛡️ Sistema de seguridad API configurado")
            else:
                self._logger.warning("⚠️ Adaptador no soporta sistema de seguridad")
                
        except Exception as e:
            self._logger.error(f"❌ Error configurando seguridad API: {e}")
    
    def _confirm_dangerous_operation(self, method: str, url: str, data: Dict[str, Any]) -> bool:
        """Solicitar confirmación del usuario para operaciones peligrosas."""
        try:
            # Importar el modal de seguridad
            from src.presentation.widgets.api_safety_modal import APISafetyModal, OperationType
            
            # Mapear método HTTP a OperationType
            operation_type_map = {
                'POST': OperationType.POST,
                'PUT': OperationType.PUT,
                'PATCH': OperationType.PATCH,
                'DELETE': OperationType.DELETE
            }
            
            operation_type = operation_type_map.get(method.upper())
            if not operation_type:
                self._logger.error(f"Tipo de operación no reconocido: {method}")
                return False
            
            # Mostrar modal de confirmación
            parent = self._gui_reference if self._gui_reference else None
            approved = APISafetyModal.confirm_operation(
                operation_type=operation_type,
                endpoint=url,
                payload=data,
                parent=parent
            )
            
            # Log del resultado
            if approved:
                self._logger.info(f"✅ Usuario aprobó: {method} {url}")
                self._log_approved_operation(method, url, data)
            else:
                self._logger.warning(f"❌ Usuario rechazó: {method} {url}")
                self._log_rejected_operation(method, url, data)
            
            return approved
            
        except Exception as e:
            self._logger.error(f"❌ Error en confirmación de operación: {e}")
            return False
    
    def _log_approved_operation(self, method: str, url: str, data: Dict[str, Any]):
        """Registrar operación aprobada para auditoría."""
        try:
            audit_log = {
                'timestamp': datetime.now().isoformat(),
                'action': 'OPERATION_APPROVED',
                'method': method,
                'endpoint': url,
                'data_size': len(str(data)) if data else 0,
                'user_approved': True
            }
            
            self._logger.info(f"📋 Operación aprobada: {audit_log}")
            
        except Exception as e:
            self._logger.error(f"❌ Error registrando operación aprobada: {e}")
    
    def _log_rejected_operation(self, method: str, url: str, data: Dict[str, Any]):
        """Registrar operación rechazada para auditoría."""
        try:
            audit_log = {
                'timestamp': datetime.now().isoformat(),
                'action': 'OPERATION_REJECTED',
                'method': method,
                'endpoint': url,
                'data_size': len(str(data)) if data else 0,
                'user_approved': False
            }
            
            self._logger.warning(f"🚫 Operación rechazada: {audit_log}")
            
        except Exception as e:
            self._logger.error(f"❌ Error registrando operación rechazada: {e}")
    
    # ==================== Métodos seguros para operaciones API ====================
    
    def safe_create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear factura de forma segura con confirmación del usuario."""
        try:
            if hasattr(self._invoice_repository, 'safe_create_invoice'):
                result = self._invoice_repository.safe_create_invoice(invoice_data)
                self._logger.info("✅ Factura creada exitosamente")
                return result
            else:
                raise Exception("Adaptador no soporta creación segura")
                
        except PermissionError as e:
            self._show_permission_denied_message("creación de factura", str(e))
            raise
        except Exception as e:
            self._show_error_message(f"Error creando factura: {e}")
            raise
    
    def safe_update_invoice(self, invoice_id: str, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar factura de forma segura con confirmación del usuario."""
        try:
            if hasattr(self._invoice_repository, 'safe_update_invoice'):
                result = self._invoice_repository.safe_update_invoice(invoice_id, invoice_data)
                self._logger.info(f"✅ Factura {invoice_id} actualizada exitosamente")
                return result
            else:
                raise Exception("Adaptador no soporta actualización segura")
                
        except PermissionError as e:
            self._show_permission_denied_message("actualización de factura", str(e))
            raise
        except Exception as e:
            self._show_error_message(f"Error actualizando factura: {e}")
            raise
    
    def safe_delete_invoice(self, invoice_id: str) -> bool:
        """Eliminar factura de forma segura con confirmación del usuario."""
        try:
            if hasattr(self._invoice_repository, 'safe_delete_invoice'):
                result = self._invoice_repository.safe_delete_invoice(invoice_id)
                self._logger.info(f"✅ Factura {invoice_id} eliminada exitosamente")
                return result
            else:
                raise Exception("Adaptador no soporta eliminación segura")
                
        except PermissionError as e:
            self._show_permission_denied_message("eliminación de factura", str(e))
            raise
        except Exception as e:
            self._show_error_message(f"Error eliminando factura: {e}")
            raise
    
    def _show_permission_denied_message(self, operation: str, details: str):
        """Mostrar mensaje de operación denegada."""
        if self._gui_reference:
            QMessageBox.warning(
                self._gui_reference,
                "🚫 Operación Denegada",
                f"La {operation} fue cancelada por el usuario.\n\n"
                f"Detalles: {details}\n\n"
                f"Para realizar esta operación, debe aprobarla en el modal de confirmación."
            )
    
    def _show_error_message(self, message: str):
        """Mostrar mensaje de error al usuario."""
        if self._gui_reference:
            QMessageBox.critical(
                self._gui_reference,
                "❌ Error",
                message
            )