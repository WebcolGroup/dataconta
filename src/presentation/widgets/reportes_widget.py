"""
Widget especializado para generación de reportes financieros.
Implementa arquitectura hexagonal y principios SOLID.
"""

from datetime import datetime, date
from typing import Optional, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QPushButton, QDateEdit, QFrame, QMessageBox, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont


class DateRangeFilter(QWidget):
    """
    Componente especializado para filtro de rango de fechas.
    
    Principios SOLID aplicados:
    - SRP: Solo maneja la selección de rango de fechas
    - OCP: Extensible para otros tipos de filtros
    - ISP: Interfaz específica para filtros de fecha
    """
    
    # Señal emitida cuando cambia el rango de fechas
    date_range_changed = Signal(QDate, QDate)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializar filtro de rango de fechas.
        
        Args:
            parent: Widget padre opcional
        """
        super().__init__(parent)
        self.setObjectName("DateRangeFilter")
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Configurar la interfaz del filtro de fechas."""
        # Grupo contenedor con estilo
        group = QGroupBox("📅 Filtro por Rango de Fechas")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 14px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """)
        
        # Layout del formulario
        form_layout = QFormLayout(group)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 25, 20, 20)
        
        # Estilo para los campos de fecha
        date_style = """
            QDateEdit {
                padding: 10px 12px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 11pt;
                background-color: #ffffff;
                min-width: 150px;
            }
            QDateEdit:focus {
                border-color: #1976d2;
                background-color: #f8f9fa;
            }
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }
            QDateEdit::down-arrow {
                image: none;
                border: none;
                width: 12px;
                height: 12px;
            }
        """
        
        # Campo fecha desde
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDisplayFormat("dd/MM/yyyy")
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))  # Por defecto últimos 30 días
        self.fecha_desde.setStyleSheet(date_style)
        form_layout.addRow("📅 Fecha Desde:", self.fecha_desde)
        
        # Campo fecha hasta
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDisplayFormat("dd/MM/yyyy")
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setStyleSheet(date_style)
        form_layout.addRow("📅 Fecha Hasta:", self.fecha_hasta)
        
        # Botones de rango rápido
        quick_buttons_layout = QHBoxLayout()
        quick_buttons = [
            ("7 días", 7),
            ("30 días", 30),
            ("90 días", 90),
            ("1 año", 365)
        ]
        
        for label, days in quick_buttons:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, d=days: self._set_quick_range(d))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 10pt;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
                QPushButton:pressed {
                    background-color: #1976d2;
                    color: white;
                }
            """)
            quick_buttons_layout.addWidget(btn)
        
        quick_buttons_layout.addStretch()
        form_layout.addRow("⚡ Rangos Rápidos:", quick_buttons_layout)
        
        # Información del rango seleccionado
        self.range_info = QLabel()
        self.range_info.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #dee2e6;
                margin-top: 5px;
            }
        """)
        self._update_range_info()
        form_layout.addRow("ℹ️ Información:", self.range_info)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)
    
    def _connect_signals(self) -> None:
        """Conectar señales internas."""
        self.fecha_desde.dateChanged.connect(self._on_date_changed)
        self.fecha_hasta.dateChanged.connect(self._on_date_changed)
    
    def _set_quick_range(self, days: int) -> None:
        """Establecer rango rápido de días."""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-days)
        
        self.fecha_desde.setDate(start_date)
        self.fecha_hasta.setDate(end_date)
    
    def _on_date_changed(self) -> None:
        """Manejar cambio en las fechas."""
        self._update_range_info()
        
        # Validar que fecha desde sea menor que fecha hasta
        if self.fecha_desde.date() > self.fecha_hasta.date():
            QMessageBox.warning(
                self,
                "⚠️ Rango de Fechas Inválido",
                "La fecha 'Desde' debe ser anterior a la fecha 'Hasta'."
            )
            return
        
        # Emitir señal de cambio
        self.date_range_changed.emit(self.fecha_desde.date(), self.fecha_hasta.date())
    
    def _update_range_info(self) -> None:
        """Actualizar información del rango seleccionado."""
        start_date = self.fecha_desde.date()
        end_date = self.fecha_hasta.date()
        
        if start_date.isValid() and end_date.isValid():
            days_diff = start_date.daysTo(end_date) + 1
            self.range_info.setText(
                f"📊 Rango seleccionado: {days_diff} días "
                f"({start_date.toString('dd/MM/yyyy')} - {end_date.toString('dd/MM/yyyy')})"
            )
        else:
            self.range_info.setText("⚠️ Seleccione un rango de fechas válido")
    
    def get_date_range(self) -> Tuple[QDate, QDate]:
        """
        Obtener el rango de fechas seleccionado.
        
        Returns:
            Tuple[QDate, QDate]: Fecha desde y fecha hasta
        """
        return self.fecha_desde.date(), self.fecha_hasta.date()
    
    def validate_range(self) -> bool:
        """
        Validar que el rango de fechas sea válido.
        
        Returns:
            bool: True si el rango es válido
        """
        start_date, end_date = self.get_date_range()
        
        if not start_date.isValid() or not end_date.isValid():
            return False
        
        if start_date > end_date:
            return False
        
        # Validar que no sea un rango demasiado largo (más de 2 años)
        max_days = 730  # 2 años aproximadamente
        if start_date.daysTo(end_date) > max_days:
            return False
        
        return True


class ReportesWidget(QWidget):
    """
    Widget especializado para generación de reportes financieros.
    
    Principios SOLID aplicados:
    - SRP: Solo maneja la UI para generación de reportes
    - OCP: Extensible para nuevos tipos de reportes
    - LSP: Substituible como cualquier QWidget
    - ISP: Interfaz específica para reportes
    - DIP: Depende de abstracciones (filtros, servicios)
    """
    
    # Señales para comunicación con el controlador
    estado_resultados_excel_requested = Signal(QDate, QDate, str)  # fecha_desde, fecha_hasta, tipo_comparacion (Excel)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializar widget de reportes.
        
        Args:
            parent: Widget padre opcional
        """
        super().__init__(parent)
        self.setObjectName("ReportesWidget")
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Configurar la interfaz del widget de reportes."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título principal
        titulo_group = self._create_titulo_section()
        main_layout.addWidget(titulo_group)
        
        # Filtro de rango de fechas
        self.date_filter = DateRangeFilter()
        main_layout.addWidget(self.date_filter)
        
        # Sección de reportes disponibles
        reportes_group = self._create_reportes_section()
        main_layout.addWidget(reportes_group)
        
        # Espaciador flexible
        main_layout.addStretch()
    
    def _create_titulo_section(self) -> QGroupBox:
        """Crear sección del título principal."""
        titulo_group = QGroupBox("📊 Centro de Reportes DataConta")
        titulo_group.setStyleSheet("""
            QGroupBox { 
                border: none; 
                font-weight: 700; 
                font-size: 16px;
                color: #1976d2;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        titulo_layout = QVBoxLayout(titulo_group)
        titulo_layout.setContentsMargins(15, 25, 15, 15)
        
        descripcion = QLabel("""
        🎯 Genere reportes financieros personalizados:
        
        📈 Estado de Resultados con filtros por fecha
        📊 Análisis de ingresos y gastos detallados
        🔍 Reportes basados en datos de Siigo API
        📋 Exportación en múltiples formatos
        """)
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("""
            background-color: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px;
            border: 1px solid #e9ecef;
            color: #495057;
            font-weight: normal;
            font-size: 12px;
            line-height: 1.5;
        """)
        titulo_layout.addWidget(descripcion)
        return titulo_group
    
    def _create_reportes_section(self) -> QGroupBox:
        """Crear sección de reportes disponibles."""
        reportes_group = QGroupBox("📋 Reportes Disponibles")
        reportes_group.setStyleSheet("""
            QGroupBox { 
                border: none; 
                font-weight: 700; 
                font-size: 15px;
                color: #2c3e50;
                padding-top: 10px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        reportes_layout = QVBoxLayout(reportes_group)
        reportes_layout.setSpacing(15)
        reportes_layout.setContentsMargins(15, 25, 15, 15)
        
        # Botón Estado de Resultados Excel
        self.btn_estado_resultados_excel = self._create_estado_resultados_excel_button()
        reportes_layout.addWidget(self.btn_estado_resultados_excel)
        
        # Placeholder para futuros reportes
        placeholder_info = QLabel("""
        🚧 Próximos reportes (en desarrollo):
        • Balance General
        • Flujo de Caja
        • Análisis de Clientes
        • Reportes de Impuestos
        """)
        placeholder_info.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border: 1px dashed #dee2e6;
            margin-top: 10px;
        """)
        reportes_layout.addWidget(placeholder_info)
        
        return reportes_group
    

    
    def _create_estado_resultados_excel_button(self) -> QPushButton:
        """Crear botón para generar estado de resultados en Excel."""
        btn = QPushButton("📊 Generar Estado de Resultados (Excel)")
        btn.setToolTip(
            "🔍 Generar Estado de Resultados en formato Excel:\n"
            "• Conforme a normativa tributaria colombiana\n"
            "• Análisis basado en datos de Siigo API\n"
            "• Exportación en formato .xlsx profesional\n"
            "• Incluye comparación entre períodos\n"
            "• Cálculos automáticos de márgenes\n\n"
            "📅 Configure las fechas y opciones de comparación"
        )
        btn.clicked.connect(self._handle_estado_resultados_excel)
        btn.setStyleSheet("""
            QPushButton { 
                background-color: #007bff;
                color: white;
                padding: 15px 25px; 
                border: none;
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 13pt;
                text-align: left;
                min-height: 50px;
            }
            QPushButton:hover { 
                background-color: #0056b3;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background-color: #004085;
                transform: translateY(0px);
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        return btn
    
    def _connect_signals(self) -> None:
        """Conectar señales internas."""
        # Conectar cambio de fechas para validar botón
        self.date_filter.date_range_changed.connect(self._validate_form)
        
        # Validación inicial
        self._validate_form()
    
    def _validate_form(self) -> None:
        """Validar formulario y habilitar/deshabilitar botones."""
        is_valid = self.date_filter.validate_range()
        self.btn_estado_resultados_excel.setEnabled(is_valid)
        
        if not is_valid:
            self.btn_estado_resultados_excel.setToolTip(
                "⚠️ Seleccione un rango de fechas válido para generar el reporte Excel"
            )
        else:
            # Restaurar tooltip original
            self.btn_estado_resultados_excel.setToolTip(
                "🔍 Generar Estado de Resultados en formato Excel:\n"
                "• Conforme a normativa tributaria colombiana\n"
                "• Análisis basado en datos de Siigo API\n"
                "• Exportación en formato .xlsx profesional\n"
                "• Incluye comparación entre períodos\n"
                "• Cálculos automáticos de márgenes\n\n"
                "📅 Configure las fechas y opciones de comparación"
            )
    

    
    def _handle_estado_resultados_excel(self) -> None:
        """Manejar clic en generar estado de resultados Excel."""
        print("DEBUG: 🔥 Botón Estado de Resultados Excel clickeado!")  # Debug temporal
        
        # Validar rango de fechas
        if not self.date_filter.validate_range():
            QMessageBox.warning(
                self,
                "⚠️ Rango de Fechas Inválido",
                "Por favor, seleccione un rango de fechas válido antes de generar el reporte.\n\n"
                "• La fecha 'Desde' debe ser anterior a la fecha 'Hasta'\n"
                "• El rango no debe exceder 2 años\n"
                "• Ambas fechas deben ser válidas"
            )
            return
        
        # Obtener rango de fechas
        fecha_desde, fecha_hasta = self.date_filter.get_date_range()
        
        # Confirmar con el usuario
        reply = QMessageBox.question(
            self,
            "📊 Generar Estado de Resultados Excel",
            f"🔍 <b>Confirmar generación de reporte Excel</b><br><br>"
            f"📅 <b>Período:</b> {fecha_desde.toString('dd/MM/yyyy')} - {fecha_hasta.toString('dd/MM/yyyy')}<br>"
            f"📊 <b>Días:</b> {fecha_desde.daysTo(fecha_hasta) + 1} días<br>"
            f"🏢 <b>Normativa:</b> Decreto 2420/2015, PUC colombiano<br><br>"
            f"🔄 El sistema consultará las facturas de Siigo API para generar "
            f"un Estado de Resultados en formato Excel (.xlsx) con análisis completo.<br><br>"
            f"¿Desea continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Emitir señal para solicitar el reporte Excel con comparación de período anterior
            self.estado_resultados_excel_requested.emit(fecha_desde, fecha_hasta, "periodo_anterior")
            
            # Mostrar mensaje de proceso iniciado
            QMessageBox.information(
                self,
                "🚀 Generando Estado de Resultados Excel",
                "📊 <b>Estado de Resultados Excel en proceso...</b><br><br>"
                "🔄 El sistema está:<br>"
                "• Consultando datos de Siigo API<br>"
                "• Aplicando normativa tributaria colombiana<br>"
                "• Calculando utilidades y márgenes<br>"
                "• Generando archivo Excel profesional<br><br>"
                "⏳ Este proceso puede tomar unos momentos...<br><br>"
                "📁 El archivo Excel se guardará en la carpeta 'outputs'."
            )
    
    def get_date_filter(self) -> DateRangeFilter:
        """
        Obtener referencia al filtro de fechas.
        
        Returns:
            DateRangeFilter: Componente de filtro de fechas
        """
        return self.date_filter
    
    def set_controller_reference(self, controller) -> None:
        """
        Establecer referencia al controlador (para inyección de dependencias).
        
        Args:
            controller: Referencia al controlador de la aplicación
        """
        # Este método permitirá conectar con el controlador cuando sea necesario
        # Siguiendo principio DIP - dependencia de abstracciones
        self._controller = controller
    
    def show_success_message(self, file_path: str) -> None:
        """
        Mostrar mensaje de éxito cuando se genere el reporte.
        
        Args:
            file_path: Ruta del archivo generado
        """
        QMessageBox.information(
            self,
            "✅ Reporte Generado",
            f"🎉 <b>Estado de Resultados generado exitosamente</b><br><br>"
            f"📁 <b>Archivo:</b> {file_path}<br><br>"
            f"📊 El reporte contiene el análisis financiero del período seleccionado "
            f"con datos actualizados de Siigo API.<br><br>"
            f"🔍 Puede revisar el archivo en la carpeta de salida."
        )
    
    def show_error_message(self, error: str) -> None:
        """
        Mostrar mensaje de error cuando falle la generación.
        
        Args:
            error: Mensaje de error a mostrar
        """
        QMessageBox.critical(
            self,
            "❌ Error al Generar Reporte",
            f"💥 <b>No se pudo generar el Estado de Resultados</b><br><br>"
            f"🔍 <b>Error:</b> {error}<br><br>"
            f"🔧 <b>Posibles soluciones:</b><br>"
            f"• Verificar conexión con Siigo API<br>"
            f"• Revisar credenciales de acceso<br>"
            f"• Validar el rango de fechas seleccionado<br>"
            f"• Consultar logs del sistema para más detalles"
        )