"""
Widget especializado para generación de Estado de Resultados en Excel.
Extiende ReportesWidget con opciones de comparación y normativa colombiana.
"""

from datetime import datetime, date
from typing import Optional, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QPushButton, QDateEdit, QComboBox, QFrame, QMessageBox, QFormLayout
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

from src.domain.entities.estado_resultados import TipoComparacion


class ComparacionFilter(QWidget):
    """
    Componente especializado para filtro de comparación de períodos.
    
    Principios SOLID aplicados:
    - SRP: Solo maneja la selección de opciones de comparación
    - OCP: Extensible para nuevos tipos de comparación
    - ISP: Interfaz específica para comparaciones
    """
    
    # Señal emitida cuando cambia la configuración de comparación
    comparacion_changed = Signal(str, QDate, QDate)  # tipo, fecha_desde_comp, fecha_hasta_comp
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializar filtro de comparación.
        
        Args:
            parent: Widget padre opcional
        """
        super().__init__(parent)
        self.setObjectName("ComparacionFilter")
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Configurar la interfaz del filtro de comparación."""
        # Grupo contenedor con estilo
        group = QGroupBox("📊 Opciones de Comparación")
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
        
        # Selector de tipo de comparación
        self.tipo_comparacion = QComboBox()
        self.tipo_comparacion.addItems([
            "Sin comparación",
            "Período anterior (inmediatamente anterior)",
            "Mismo período del año anterior",
            "Período personalizado"
        ])
        self.tipo_comparacion.setCurrentIndex(0)  # Por defecto sin comparación
        self.tipo_comparacion.setStyleSheet("""
            QComboBox {
                padding: 10px 12px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 11pt;
                background-color: #ffffff;
                min-width: 200px;
            }
            QComboBox:focus {
                border-color: #1976d2;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #1976d2;
            }
        """)
        form_layout.addRow("🔄 Tipo de Comparación:", self.tipo_comparacion)
        
        # Contenedor para fechas personalizadas (inicialmente oculto)
        self.fechas_personalizadas_container = QWidget()
        fechas_layout = QFormLayout(self.fechas_personalizadas_container)
        fechas_layout.setContentsMargins(0, 10, 0, 0)
        fechas_layout.setSpacing(10)
        
        # Estilo para los campos de fecha
        date_style = """
            QDateEdit {
                padding: 8px 10px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 10pt;
                background-color: #ffffff;
                min-width: 130px;
            }
            QDateEdit:focus {
                border-color: #1976d2;
                background-color: #f8f9fa;
            }
            QDateEdit::drop-down {
                border: none;
                width: 25px;
            }
        """
        
        # Campo fecha desde comparación
        self.fecha_desde_comp = QDateEdit()
        self.fecha_desde_comp.setCalendarPopup(True)
        self.fecha_desde_comp.setDisplayFormat("dd/MM/yyyy")
        self.fecha_desde_comp.setDate(QDate.currentDate().addDays(-60))
        self.fecha_desde_comp.setStyleSheet(date_style)
        fechas_layout.addRow("📅 Desde (comparación):", self.fecha_desde_comp)
        
        # Campo fecha hasta comparación
        self.fecha_hasta_comp = QDateEdit()
        self.fecha_hasta_comp.setCalendarPopup(True)
        self.fecha_hasta_comp.setDisplayFormat("dd/MM/yyyy")
        self.fecha_hasta_comp.setDate(QDate.currentDate().addDays(-31))
        self.fecha_hasta_comp.setStyleSheet(date_style)
        fechas_layout.addRow("📅 Hasta (comparación):", self.fecha_hasta_comp)
        
        # Ocultar inicialmente
        self.fechas_personalizadas_container.setVisible(False)
        form_layout.addRow(self.fechas_personalizadas_container)
        
        # Información de la comparación seleccionada
        self.comparacion_info = QLabel()
        self.comparacion_info.setStyleSheet("""
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
        self._update_comparacion_info()
        form_layout.addRow("ℹ️ Información:", self.comparacion_info)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)
    
    def _connect_signals(self) -> None:
        """Conectar señales internas."""
        self.tipo_comparacion.currentTextChanged.connect(self._on_tipo_changed)
        self.fecha_desde_comp.dateChanged.connect(self._on_fecha_comp_changed)
        self.fecha_hasta_comp.dateChanged.connect(self._on_fecha_comp_changed)
    
    def _on_tipo_changed(self) -> None:
        """Manejar cambio en el tipo de comparación."""
        tipo_seleccionado = self.tipo_comparacion.currentText()
        
        # Mostrar/ocultar fechas personalizadas
        if "personalizado" in tipo_seleccionado.lower():
            self.fechas_personalizadas_container.setVisible(True)
        else:
            self.fechas_personalizadas_container.setVisible(False)
        
        self._update_comparacion_info()
        self._emit_comparacion_changed()
    
    def _on_fecha_comp_changed(self) -> None:
        """Manejar cambio en las fechas de comparación."""
        # Validar que fecha desde sea menor que fecha hasta
        if self.fecha_desde_comp.date() > self.fecha_hasta_comp.date():
            QMessageBox.warning(
                self,
                "⚠️ Rango de Fechas Inválido",
                "La fecha 'Desde' de comparación debe ser anterior a la fecha 'Hasta'."
            )
            return
        
        self._update_comparacion_info()
        self._emit_comparacion_changed()
    
    def _emit_comparacion_changed(self) -> None:
        """Emitir señal de cambio en la comparación."""
        tipo = self._get_tipo_comparacion_enum()
        fecha_desde, fecha_hasta = self.get_fechas_comparacion()
        self.comparacion_changed.emit(tipo, fecha_desde, fecha_hasta)
    
    def _update_comparacion_info(self) -> None:
        """Actualizar información de la comparación seleccionada."""
        tipo_seleccionado = self.tipo_comparacion.currentText()
        
        if "sin comparación" in tipo_seleccionado.lower():
            self.comparacion_info.setText("📊 Estado de Resultados simple sin comparación")
        elif "período anterior" in tipo_seleccionado.lower():
            self.comparacion_info.setText(
                "📈 Se comparará con el período inmediatamente anterior de la misma duración"
            )
        elif "año anterior" in tipo_seleccionado.lower():
            self.comparacion_info.setText(
                "📅 Se comparará con el mismo período del año anterior"
            )
        elif "personalizado" in tipo_seleccionado.lower():
            fecha_desde = self.fecha_desde_comp.date()
            fecha_hasta = self.fecha_hasta_comp.date()
            if fecha_desde.isValid() and fecha_hasta.isValid():
                days_diff = fecha_desde.daysTo(fecha_hasta) + 1
                self.comparacion_info.setText(
                    f"🔧 Comparación personalizada: {days_diff} días "
                    f"({fecha_desde.toString('dd/MM/yyyy')} - {fecha_hasta.toString('dd/MM/yyyy')})"
                )
            else:
                self.comparacion_info.setText("⚠️ Defina las fechas de comparación personalizada")
    
    def _get_tipo_comparacion_enum(self) -> str:
        """Obtener el enum correspondiente al tipo seleccionado."""
        tipo_seleccionado = self.tipo_comparacion.currentText().lower()
        
        if "período anterior" in tipo_seleccionado:
            return TipoComparacion.PERIODO_ANTERIOR
        elif "año anterior" in tipo_seleccionado:
            return TipoComparacion.MISMO_PERIODO_ANO_ANTERIOR
        elif "personalizado" in tipo_seleccionado:
            return TipoComparacion.PERSONALIZADO
        else:
            return TipoComparacion.SIN_COMPARACION
    
    def get_tipo_comparacion(self) -> str:
        """
        Obtener el tipo de comparación seleccionado.
        
        Returns:
            str: Tipo de comparación (enum)
        """
        return self._get_tipo_comparacion_enum()
    
    def get_fechas_comparacion(self) -> Tuple[Optional[QDate], Optional[QDate]]:
        """
        Obtener las fechas de comparación (solo para tipo personalizado).
        
        Returns:
            Tuple[Optional[QDate], Optional[QDate]]: Fecha desde y hasta de comparación
        """
        if self._get_tipo_comparacion_enum() == TipoComparacion.PERSONALIZADO:
            return self.fecha_desde_comp.date(), self.fecha_hasta_comp.date()
        return None, None
    
    def validate_comparacion(self) -> bool:
        """
        Validar que la configuración de comparación sea válida.
        
        Returns:
            bool: True si la configuración es válida
        """
        tipo = self._get_tipo_comparacion_enum()
        
        if tipo == TipoComparacion.PERSONALIZADO:
            fecha_desde, fecha_hasta = self.get_fechas_comparacion()
            
            if not fecha_desde or not fecha_hasta:
                return False
            
            if not fecha_desde.isValid() or not fecha_hasta.isValid():
                return False
            
            if fecha_desde > fecha_hasta:
                return False
            
            # Validar que no sea un rango demasiado largo
            if fecha_desde.daysTo(fecha_hasta) > 730:  # Máximo 2 años
                return False
        
        return True


class EstadoResultadosWidget(QWidget):
    """
    Widget especializado para generación de Estado de Resultados en Excel.
    
    Principios SOLID aplicados:
    - SRP: Solo maneja la UI para Estado de Resultados
    - OCP: Extensible para nuevas opciones de reporte
    - LSP: Substituible como cualquier QWidget
    - ISP: Interfaz específica para Estado de Resultados
    - DIP: Depende de abstracciones (filtros, servicios)
    """
    
    # Señal para comunicación con el controlador
    estado_resultados_excel_requested = Signal(
        QDate, QDate,  # fecha_desde, fecha_hasta (período actual)
        str,           # tipo_comparacion
        QDate, QDate   # fecha_desde_comp, fecha_hasta_comp (período comparación)
    )
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializar widget de Estado de Resultados.
        
        Args:
            parent: Widget padre opcional
        """
        super().__init__(parent)
        self.setObjectName("EstadoResultadosWidget")
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Configurar la interfaz del widget."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título principal
        titulo_group = self._create_titulo_section()
        main_layout.addWidget(titulo_group)
        
        # Filtro de rango de fechas (reutilizamos componente existente)
        from src.presentation.widgets.reportes_widget import DateRangeFilter
        self.date_filter = DateRangeFilter()
        main_layout.addWidget(self.date_filter)
        
        # Filtro de comparación
        self.comparacion_filter = ComparacionFilter()
        main_layout.addWidget(self.comparacion_filter)
        
        # Botón de generación
        self.btn_generar = self._create_generar_button()
        main_layout.addWidget(self.btn_generar)
        
        # Información normativa
        info_normativa = self._create_info_normativa()
        main_layout.addWidget(info_normativa)
        
        # Espaciador flexible
        main_layout.addStretch()
    
    def _create_titulo_section(self) -> QGroupBox:
        """Crear sección del título principal."""
        titulo_group = QGroupBox("📈 Estado de Resultados - Exportación Excel")
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
        🎯 <b>Estado de Resultados Colombiano</b>
        
        📊 Genere reportes de Estado de Resultados conforme a la normativa tributaria colombiana:
        • Cumple con Decreto 2420/2015 (Marco Técnico Normativo)
        • Estructura según Plan Único de Cuentas (PUC)
        • NIIF para PYMES aplicables en Colombia
        • Análisis comparativo entre períodos
        
        📋 Características del reporte:
        • Exportación en formato Excel profesional
        • Cálculos automáticos de márgenes y utilidades
        • Comparación con períodos anteriores
        • Variaciones absolutas y porcentuales
        """)
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("""
            background-color: #e8f5e8; 
            padding: 15px; 
            border-radius: 8px;
            border: 1px solid #c3e6cb;
            color: #155724;
            font-weight: normal;
            font-size: 12px;
            line-height: 1.5;
        """)
        titulo_layout.addWidget(descripcion)
        return titulo_group
    
    def _create_generar_button(self) -> QPushButton:
        """Crear botón para generar Estado de Resultados en Excel."""
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
        btn.clicked.connect(self._handle_generar_excel)
        btn.setStyleSheet("""
            QPushButton { 
                background-color: #007bff;
                color: white;
                padding: 20px 30px; 
                border: none;
                border-radius: 10px; 
                font-weight: bold; 
                font-size: 14pt;
                text-align: center;
                min-height: 60px;
                margin: 10px 0;
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
    
    def _create_info_normativa(self) -> QGroupBox:
        """Crear sección de información normativa."""
        info_group = QGroupBox("📋 Información Normativa")
        info_group.setStyleSheet("""
            QGroupBox { 
                border: 1px solid #dee2e6; 
                border-radius: 8px;
                font-weight: 600; 
                font-size: 13px;
                color: #495057;
                padding-top: 10px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """)
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(15, 20, 15, 15)
        
        normativa_text = QLabel("""
        ⚖️ <b>Marco Normativo Aplicado:</b>
        • <b>Decreto 2420/2015:</b> Marco Técnico Normativo de Información Financiera
        • <b>Decreto 2650/1993:</b> Plan Único de Cuentas para comerciantes
        • <b>Ley 1314/2009:</b> Principios de contabilidad generalmente aceptados
        • <b>NIIF para PYMES:</b> Normas internacionales aplicables en Colombia
        
        🏢 <b>Estructura del Estado de Resultados:</b>
        • Ingresos operacionales (Grupo 41)
        • Costos de ventas (Grupo 61)
        • Gastos de administración (Grupo 51)
        • Gastos de ventas (Grupo 52)
        • Gastos financieros (Grupo 53)
        • Impuestos (Grupo 54)
        
        📊 <b>Análisis Incluido:</b>
        • Utilidad bruta, operacional y neta
        • Márgenes porcentuales
        • Comparación entre períodos
        • Variaciones absolutas y relativas
        """)
        normativa_text.setWordWrap(True)
        normativa_text.setStyleSheet("""
            color: #495057;
            font-size: 11px;
            line-height: 1.4;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        """)
        info_layout.addWidget(normativa_text)
        return info_group
    
    def _connect_signals(self) -> None:
        """Conectar señales internas."""
        # Conectar cambios en filtros para validar formulario
        self.date_filter.date_range_changed.connect(self._validate_form)
        self.comparacion_filter.comparacion_changed.connect(self._validate_form)
        
        # Validación inicial
        self._validate_form()
    
    def _validate_form(self) -> None:
        """Validar formulario y habilitar/deshabilitar botón."""
        date_valid = self.date_filter.validate_range()
        comparacion_valid = self.comparacion_filter.validate_comparacion()
        
        is_valid = date_valid and comparacion_valid
        self.btn_generar.setEnabled(is_valid)
        
        if not is_valid:
            tooltip_errors = []
            if not date_valid:
                tooltip_errors.append("• Seleccione un rango de fechas válido")
            if not comparacion_valid:
                tooltip_errors.append("• Configure correctamente las opciones de comparación")
            
            self.btn_generar.setToolTip(
                "⚠️ Corrija los siguientes errores:\n" + "\n".join(tooltip_errors)
            )
    
    def _handle_generar_excel(self) -> None:
        """Manejar clic en generar Estado de Resultados en Excel."""
        # Validar formulario
        if not self.date_filter.validate_range() or not self.comparacion_filter.validate_comparacion():
            QMessageBox.warning(
                self,
                "⚠️ Formulario Inválido",
                "Por favor, corrija los errores en el formulario antes de generar el reporte.\n\n"
                "• Verifique que el rango de fechas sea válido\n"
                "• Configure correctamente las opciones de comparación\n"
                "• Asegúrese de que todos los campos requeridos estén completos"
            )
            return
        
        # Obtener datos del formulario
        fecha_desde, fecha_hasta = self.date_filter.get_date_range()
        tipo_comparacion = self.comparacion_filter.get_tipo_comparacion()
        fecha_desde_comp, fecha_hasta_comp = self.comparacion_filter.get_fechas_comparacion()
        
        # Preparar información de confirmación
        periodo_info = f"{fecha_desde.toString('dd/MM/yyyy')} - {fecha_hasta.toString('dd/MM/yyyy')}"
        dias_periodo = fecha_desde.daysTo(fecha_hasta) + 1
        
        comparacion_info = ""
        if tipo_comparacion != TipoComparacion.SIN_COMPARACION:
            if tipo_comparacion == TipoComparacion.PERIODO_ANTERIOR:
                comparacion_info = "<br>📊 <b>Comparación:</b> Período inmediatamente anterior"
            elif tipo_comparacion == TipoComparacion.MISMO_PERIODO_ANO_ANTERIOR:
                comparacion_info = "<br>📊 <b>Comparación:</b> Mismo período del año anterior"
            elif tipo_comparacion == TipoComparacion.PERSONALIZADO and fecha_desde_comp and fecha_hasta_comp:
                periodo_comp = f"{fecha_desde_comp.toString('dd/MM/yyyy')} - {fecha_hasta_comp.toString('dd/MM/yyyy')}"
                comparacion_info = f"<br>📊 <b>Comparación personalizada:</b> {periodo_comp}"
        
        # Confirmar con el usuario
        reply = QMessageBox.question(
            self,
            "📊 Generar Estado de Resultados Excel",
            f"🔍 <b>Confirmar generación de Estado de Resultados</b><br><br>"
            f"📅 <b>Período principal:</b> {periodo_info}<br>"
            f"📊 <b>Días:</b> {dias_periodo} días{comparacion_info}<br><br>"
            f"🏢 <b>Normativa aplicada:</b> Decreto 2420/2015, PUC colombiano<br>"
            f"📋 <b>Formato:</b> Excel (.xlsx) con análisis comparativo<br><br>"
            f"🔄 El sistema consultará las facturas de Siigo API para generar "
            f"un Estado de Resultados completo con cálculos automáticos de utilidades y márgenes.<br><br>"
            f"¿Desea continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Emitir señal para solicitar el reporte
            self.estado_resultados_excel_requested.emit(
                fecha_desde, fecha_hasta,
                tipo_comparacion,
                fecha_desde_comp or QDate(), fecha_hasta_comp or QDate()
            )
            
            # Mostrar mensaje de proceso iniciado
            QMessageBox.information(
                self,
                "🚀 Generando Estado de Resultados",
                "📊 <b>Estado de Resultados en proceso...</b><br><br>"
                "🔄 El sistema está:<br>"
                "• Consultando datos de Siigo API<br>"
                "• Aplicando estructura contable colombiana<br>"
                "• Calculando utilidades y márgenes<br>"
                "• Generando comparaciones entre períodos<br>"
                "• Creando archivo Excel profesional<br><br>"
                "⏳ Este proceso puede tomar unos momentos...<br><br>"
                "📁 El archivo se guardará en la carpeta 'outputs' cuando esté listo."
            )
    
    def show_success_message(self, file_path: str) -> None:
        """
        Mostrar mensaje de éxito cuando se genere el reporte.
        
        Args:
            file_path: Ruta del archivo Excel generado
        """
        QMessageBox.information(
            self,
            "✅ Estado de Resultados Generado",
            f"🎉 <b>Estado de Resultados generado exitosamente</b><br><br>"
            f"📁 <b>Archivo Excel:</b> {file_path}<br><br>"
            f"📊 <b>Contenido del reporte:</b><br>"
            f"• Estado de Resultados según normativa colombiana<br>"
            f"• Análisis comparativo entre períodos<br>"
            f"• Cálculos automáticos de utilidades y márgenes<br>"
            f"• Formato profesional con estilos y colores<br><br>"
            f"🔍 Puede abrir el archivo Excel para revisar el análisis financiero completo."
        )
    
    def show_error_message(self, error: str) -> None:
        """
        Mostrar mensaje de error cuando falle la generación.
        
        Args:
            error: Mensaje de error a mostrar
        """
        QMessageBox.critical(
            self,
            "❌ Error al Generar Estado de Resultados",
            f"💥 <b>No se pudo generar el Estado de Resultados</b><br><br>"
            f"🔍 <b>Error:</b> {error}<br><br>"
            f"🔧 <b>Posibles soluciones:</b><br>"
            f"• Verificar conexión con Siigo API<br>"
            f"• Revisar credenciales de acceso a Siigo<br>"
            f"• Validar que existan datos en el período seleccionado<br>"
            f"• Verificar permisos de escritura en carpeta 'outputs'<br>"
            f"• Consultar logs del sistema para más detalles<br><br>"
            f"📞 Si el problema persiste, contacte al soporte técnico."
        )