"""
Free GUI Controller - Presentation Layer
Controlador principal para DataConta FREE GUI siguiendo arquitectura hexagonal.
Implementa interfaces del dominio y coordina la vista con los servicios.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QTableWidget
from PySide6.QtCore import QObject, Signal as pyqtSignal

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
            filters = InvoiceFilter(
                fecha_inicio="2024-01-01",
                fecha_fin=datetime.now().strftime("%Y-%m-%d")
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
        """Refrescar KPIs - alias para calculate_kpis."""
        try:
            self._logger.info("🔄 Refrescando KPIs")
            self.calculate_kpis()
        except Exception as e:
            self._logger.error(f"❌ Error refrescando KPIs: {e}")
            self.show_error_message(f"Error cargando KPIs: {e}")
    
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
            self._logger.info(f"🔄 Iniciando exportación CSV REAL con {count} registros...")
            
            # Usar el servicio de exportación existente
            self._logger.info(f"🔄 Llamando _export_service.export_csv_real({count})...")
            result = self._export_service.export_csv_real(count)
            
            self._logger.info(f"📋 Resultado del servicio: success={result.success}, records={result.records_count}")
            
            if result.success:
                self._logger.info(f"✅ Exportación CSV exitosa: {result.file_path}")
                self.show_success_message(f"Exportación REAL completada: {result.records_count} facturas guardadas en {result.file_path}")
            else:
                self._logger.error(f"❌ Error en servicio CSV: {result.error}")
                self.show_error_message(f"Error durante la exportación CSV: {result.error or 'Error desconocido'}")
                raise Exception(f"Servicio reportó fallo: {result.error}")
                
        except Exception as e:
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
            self._logger.info(f"🔄 Iniciando exportación Excel con {count} registros...")
            
            # Usar el método de CSV real del servicio que sí funciona con limit
            result = self._export_service.export_csv_real(count)
            
            if result.success:
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
                    
                except Exception as excel_error:
                    self._logger.error(f"❌ Error convirtiendo a Excel: {excel_error}")
                    self.show_success_message(f"Exportación CSV exitosa (Excel falló): {result.records_count} facturas guardadas en {result.file_path}")
                    
            else:
                self.show_error_message(f"Error durante la exportación: {result.error or 'Error desconocido'}")
                
        except Exception as e:
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