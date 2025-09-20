"""
Query Widget - Componente UI especializado para consultas de facturas
Parte de la refactorización del monolito dataconta_free_gui_refactored.py

Responsabilidad única: UI de consultas y filtros, delegando toda la lógica al controlador
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QFrame, QDateEdit, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QHeaderView, QMessageBox, QGraphicsDropShadowEffect,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor


class QueryWidget(QWidget):
    """
    Widget especializado para consultas de facturas.
    
    Principios SOLID:
    - SRP: Solo maneja la UI de consultas
    - OCP: Extensible para nuevos filtros
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para consultas
    - DIP: Depende de abstracciones (signals)
    """
    
    # Signals para comunicación con el controlador
    search_invoices_requested = Signal(dict)  # filters
    clear_filters_requested = Signal()
    load_statuses_requested = Signal()   # Solicitar carga de estados
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.date_start: Optional[QDateEdit] = None
        self.date_end: Optional[QDateEdit] = None
        self.client_filter: Optional[QLineEdit] = None
        self.customer_id_input: Optional[QLineEdit] = None   # Campo de texto para ID cliente
        self.status_combo: Optional[QComboBox] = None       # Dropdown de estados
        self.results_table: Optional[QTableWidget] = None
        self.init_ui()
        self.setup_default_dates()
    
    def init_ui(self):
        """Inicializar interfaz de consultas."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Crear scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f1f1f1;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
            QScrollBar:horizontal {
                background-color: #f1f1f1;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a8a8a8;
            }
        """)
        
        # Widget contenedor para el contenido scrolleable
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # Sección de filtros (card)
        filters = self.create_filters_section()
        layout.addWidget(self._wrap_in_card(filters))

        # Botones de acción (card)
        actions = self.create_action_buttons()
        layout.addWidget(self._wrap_in_card(actions))

        # Tabla de resultados (card)
        results = self.create_results_table()
        layout.addWidget(self._wrap_in_card(results))
        
        # Configurar scroll area
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def create_filters_section(self) -> QWidget:
        """Crear sección de filtros de búsqueda (devuelve contenedor)."""
        filters_group = QGroupBox("🔍 Consulta de Facturas - Versión FREE")
        filters_group.setStyleSheet("""
            QGroupBox {
                font-weight: 700;
                font-size: 14px;
                color: #2c3e50;
                padding-top: 10px;
                margin-top: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
                color: #2980b9;
                font-weight: bold;
            }
        """)
        filters_layout = QGridLayout(filters_group)
        filters_layout.setContentsMargins(15, 20, 15, 15)  # left, top, right, bottom
        filters_layout.setSpacing(10)  # Espacio entre elementos
        
        # Filtros de fecha
        filters_layout.addWidget(QLabel("📅 Fecha Inicio:"), 0, 0)
        self.date_start = QDateEdit()
        self.date_start.setToolTip(self._get_date_start_tooltip())
        self.date_start.setCalendarPopup(True)
        filters_layout.addWidget(self.date_start, 0, 1)
        
        filters_layout.addWidget(QLabel("📅 Fecha Fin:"), 0, 2)
        self.date_end = QDateEdit()
        self.date_end.setToolTip(self._get_date_end_tooltip())
        self.date_end.setCalendarPopup(True)
        filters_layout.addWidget(self.date_end, 0, 3)
        
        # Filtro de cliente (texto libre - mantener compatibilidad)
        filters_layout.addWidget(QLabel("🏢 Cliente (texto):"), 1, 0)
        self.client_filter = QLineEdit()
        self.client_filter.setToolTip(self._get_client_filter_tooltip())
        self.client_filter.setPlaceholderText("Ingrese nombre del cliente")
        filters_layout.addWidget(self.client_filter, 1, 1)
        
        # Filtro de cliente específico (por ID de texto)
        filters_layout.addWidget(QLabel("👤 Cliente ID:"), 1, 2)
        self.customer_id_input = QLineEdit()
        self.customer_id_input.setToolTip(self._get_customer_id_tooltip())
        self.customer_id_input.setPlaceholderText("ID del cliente (opcional)")
        filters_layout.addWidget(self.customer_id_input, 1, 3)
        
        # Filtro de estado de factura
        filters_layout.addWidget(QLabel("📄 Estado:"), 2, 0)
        self.status_combo = QComboBox()
        self.status_combo.setToolTip(self._get_status_filter_tooltip())
        self.status_combo.addItem("Todos los Estados", "")
        filters_layout.addWidget(self.status_combo, 2, 1)
        
        return filters_group
    
    def create_action_buttons(self) -> QWidget:
        """Crear botones de búsqueda y limpieza (devuelve contenedor)."""
        container = QWidget()
        buttons_layout = QHBoxLayout(container)
        
        # Botón buscar
        search_btn = QPushButton("🔍 Buscar Facturas")
        search_btn.setStyleSheet(self._get_search_button_style())
        search_btn.clicked.connect(self._on_search_clicked)
        
        # Botón limpiar
        clear_btn = QPushButton("🧹 Limpiar Filtros")
        clear_btn.setStyleSheet(self._get_clear_button_style())
        clear_btn.clicked.connect(self._on_clear_clicked)
        
        buttons_layout.addWidget(search_btn)
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addStretch()
        
        return container
    
    def create_results_table(self) -> QWidget:
        """Crear tabla de resultados (devuelve contenedor)."""
        container = QWidget()
        v = QVBoxLayout(container)
        v.addWidget(QLabel("📊 Resultados de Búsqueda:"))
        
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_table.setShowGrid(False)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Establecer tamaño mínimo y política de expansión
        self.results_table.setMinimumHeight(200)
        self.results_table.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )

        # Headers y dimensiones
        h_header = self.results_table.horizontalHeader()
        h_header.setStretchLastSection(True)
        h_header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        h_header.setHighlightSections(False)
        h_header.setFixedHeight(36)

        v_header = self.results_table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(40)
        
        # Configurar columnas por defecto
        self._setup_default_table()
        v.addWidget(self.results_table)
        return container
    
    def setup_default_dates(self):
        """Configurar fechas por defecto."""
        if self.date_start and self.date_end:
            # Fecha inicio: hace 30 días
            self.date_start.setDate(QDate.currentDate().addDays(-30))
            # Fecha fin: hoy
            self.date_end.setDate(QDate.currentDate())
        
        self._logger_message("📅 Fechas por defecto configuradas")
        
    def request_initial_data(self):
        """Solicitar carga inicial de datos (debe llamarse después de conectar señales)."""
        self._logger_message("🔄 Solicitando carga de estados...")
        self._logger_message(f"🔍 Status combo inicializado: {self.status_combo is not None}")
        if self.status_combo:
            self._logger_message(f"📊 Estado combo actual: {self.status_combo.count()} elementos")
        self.load_statuses_requested.emit()
    
    def _setup_default_table(self):
        """Configurar tabla con estructura por defecto."""
        if self.results_table:
            headers = ["Número", "Fecha", "Cliente", "Monto", "Estado"]
            self.results_table.setColumnCount(len(headers))
            self.results_table.setHorizontalHeaderLabels(headers)
            
            # Ajustar columnas
            header = self.results_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.Interactive)
            
            # Mensaje inicial
            self._show_empty_table_message()
    
    def _show_empty_table_message(self):
        """Mostrar mensaje en tabla vacía."""
        if self.results_table:
            self.results_table.setRowCount(1)
            self.results_table.setColumnCount(1)
            self.results_table.setHorizontalHeaderLabels(["Estado"])
            
            message_item = QTableWidgetItem("🔍 Use los filtros de búsqueda para consultar facturas")
            message_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(0, 0, message_item)
    
    def _on_search_clicked(self):
        """Manejar clic en botón de búsqueda."""
        filters = self._get_current_filters()
        self.search_invoices_requested.emit(filters)
    
    def _on_clear_clicked(self):
        """Manejar clic en botón limpiar."""
        self.clear_filters()
        self.clear_filters_requested.emit()
    
    def _get_current_filters(self) -> Dict[str, Any]:
        """Obtener filtros actuales del formulario."""
        filters = {}
        
        if self.date_start:
            filters['fecha_inicio'] = self.date_start.date().toString('yyyy-MM-dd')
        
        if self.date_end:
            filters['fecha_fin'] = self.date_end.date().toString('yyyy-MM-dd')
        
        if self.client_filter and self.client_filter.text().strip():
            filters['cliente'] = self.client_filter.text().strip()
            
        # Filtro por ID de cliente específico (campo de texto)
        if self.customer_id_input and self.customer_id_input.text().strip():
            filters['customer_id'] = self.customer_id_input.text().strip()
            
        # Nuevo: Filtro por estado de factura
        if self.status_combo and self.status_combo.currentData():
            filters['status'] = self.status_combo.currentData()
        
        return filters
    
    def clear_filters(self):
        """Limpiar todos los filtros."""
        if self.date_start:
            self.date_start.setDate(QDate.currentDate().addDays(-30))
        
        if self.date_end:
            self.date_end.setDate(QDate.currentDate())
        
        if self.client_filter:
            self.client_filter.clear()
            
        # Limpiar campo de ID de cliente
        if self.customer_id_input:
            self.customer_id_input.clear()
            
        # Limpiar combo de estado
        if self.status_combo:
            self.status_combo.setCurrentIndex(0)  # "Todos los Estados"
        
        # Limpiar tabla
        self._show_empty_table_message()
    
    def update_results(self, invoices: List[Dict[str, Any]]):
        """
        Actualizar tabla con resultados de búsqueda.
        
        Args:
            invoices: Lista de facturas del controlador
        """
        try:
            if not invoices:
                self._show_no_results_message()
                return
            
            # Configurar tabla
            self.results_table.setRowCount(len(invoices))
            self.results_table.setColumnCount(5)
            self.results_table.setHorizontalHeaderLabels([
                "Número", "Fecha", "Cliente", "Monto", "Estado"
            ])
            
            # Llenar datos
            for row, invoice in enumerate(invoices):
                self.results_table.setItem(row, 0, QTableWidgetItem(
                    str(invoice.get('numero', 'N/A'))
                ))
                self.results_table.setItem(row, 1, QTableWidgetItem(
                    str(invoice.get('fecha', 'N/A'))
                ))
                self.results_table.setItem(row, 2, QTableWidgetItem(
                    str(invoice.get('cliente', 'N/A'))
                ))
                self.results_table.setItem(row, 3, QTableWidgetItem(
                    f"${invoice.get('monto', 0):,.2f}"
                ))
                self.results_table.setItem(row, 4, QTableWidgetItem(
                    str(invoice.get('estado', 'N/A'))
                ))
            
            # Ajustar columnas
            self.results_table.resizeColumnsToContents()
            
        except Exception as e:
            self._show_error_in_table(f"Error mostrando resultados: {str(e)}")
    
    def _show_no_results_message(self):
        """Mostrar mensaje cuando no hay resultados."""
        self.results_table.setRowCount(1)
        self.results_table.setColumnCount(1)
        self.results_table.setHorizontalHeaderLabels(["Resultado"])
        
        message_item = QTableWidgetItem("🔍 No se encontraron facturas con los filtros especificados")
        message_item.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(0, 0, message_item)
    
    def _show_error_in_table(self, error_message: str):
        """Mostrar mensaje de error en la tabla."""
        self.results_table.setRowCount(1)
        self.results_table.setColumnCount(1)
        self.results_table.setHorizontalHeaderLabels(["Error"])
        
        error_item = QTableWidgetItem(f"❌ {error_message}")
        error_item.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(0, 0, error_item)
    
    def _get_date_start_tooltip(self) -> str:
        """Tooltip para fecha inicio."""
        return (
            "📅 Fecha de inicio del rango de búsqueda:\n"
            "• Seleccione la fecha más antigua\n"
            "• Formato: DD/MM/AAAA\n"
            "• Por defecto: Hace 30 días\n\n"
            "🔍 Filtra facturas desde esta fecha"
        )
    
    def _get_date_end_tooltip(self) -> str:
        """Tooltip para fecha fin."""
        return (
            "📅 Fecha final del rango de búsqueda:\n"
            "• Seleccione la fecha más reciente\n"
            "• Formato: DD/MM/AAAA\n"
            "• Por defecto: Hoy\n\n"
            "🔍 Filtra facturas hasta esta fecha"
        )
    
    def _get_client_filter_tooltip(self) -> str:
        """Tooltip para filtro de cliente."""
        return (
            "💼 Filtro por nombre de cliente (búsqueda de texto):\n"
            "• Escriba el nombre completo o parcial\n"
            "• Búsqueda no sensible a mayúsculas\n"
            "• Ejemplo: 'Acme Corp' o 'acme'\n\n"
            "🔍 Búsqueda inteligente de clientes"
        )
    
    def _get_customer_id_tooltip(self) -> str:
        """Tooltip para filtro de ID de cliente específico."""
        return (
            "🆔 Filtro por ID de cliente específico:\n"
            "• Ingrese el ID interno del cliente\n"
            "• Campo opcional para búsqueda exacta\n"
            "• Ejemplo: '380d1165-503b-49d6-ad70-973e1723a41a'\n\n"
            "🎯 Búsqueda precisa por ID de cliente"
        )
    
    def _get_status_filter_tooltip(self) -> str:
        """Tooltip para filtro de estado de factura."""
        return (
            "📋 Filtro por estado de factura:\n"
            "• Abierta: Factura activa/pendiente\n"
            "• Cerrada: Factura finalizada/pagada\n"
            "• Anulada: Factura cancelada\n"
            "• Todos: Sin filtro de estado\n\n"
            "🔄 Estados según API Siigo"
        )
    
    def update_statuses(self, statuses: List[Dict[str, str]]):
        """Actualizar lista de estados en el combo desde el controlador."""
        try:
            if not self.status_combo:
                self._logger_message("❌ status_combo no está inicializado")
                return
                
            self._logger_message(f"🔄 Recibidos {len(statuses)} estados para cargar")
            
            # Limpiar combo actual
            self.status_combo.clear()
            
            # Agregar estados con debug
            for status in statuses:
                label = status.get('label', 'Sin Nombre')
                value = status.get('value', '')
                self.status_combo.addItem(label, value)
                self._logger_message(f"   + Estado agregado: {label} = {value}")
            
            self._logger_message(f"✅ Cargados {len(statuses)} estados en dropdown")
            self._logger_message(f"📊 Total elementos en combo: {self.status_combo.count()}")
            
        except Exception as e:
            self._logger_message(f"❌ Error actualizando estados: {e}")
            import traceback
            self._logger_message(f"📋 Traceback: {traceback.format_exc()}")
    
    def _logger_message(self, message: str):
        """Helper para logging (por ahora print, después se puede conectar al logger)."""
        print(f"[QueryWidget] {message}")
    
    def _get_search_button_style(self) -> str:
        """Estilo para botón de búsqueda."""
        return """
            QPushButton {
                background-color: #2196f3;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """
    
    def _get_clear_button_style(self) -> str:
        """Estilo para botón limpiar."""
        return """
            QPushButton {
                background-color: #757575;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """
    
    def show_success_message(self, title: str, message: str):
        """Mostrar mensaje de éxito."""
        QMessageBox.information(self, title, message)
    
    def show_error_message(self, title: str, message: str):
        """Mostrar mensaje de error."""
        QMessageBox.warning(self, title, message)
    
    def show_search_results_summary(self, count: int, filters: Dict[str, Any]):
        """Mostrar resumen de resultados de búsqueda."""
        filter_text = []
        if 'fecha_inicio' in filters:
            filter_text.append(f"Desde: {filters['fecha_inicio']}")
        if 'fecha_fin' in filters:
            filter_text.append(f"Hasta: {filters['fecha_fin']}")
        if 'cliente' in filters:
            filter_text.append(f"Cliente: {filters['cliente']}")
        
        filters_str = ", ".join(filter_text) if filter_text else "Sin filtros"
        
        QMessageBox.information(
            self, 
            "Resultados de Búsqueda", 
            f"🔍 Se encontraron {count} facturas\n\n"
            f"Filtros aplicados: {filters_str}"
        )

    # ---------- Helpers de UI (cards y sombras) ----------
    def _wrap_in_card(self, inner: QWidget) -> QFrame:
        card = QFrame()
        card.setObjectName("CardFrame")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.addWidget(inner)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)
        return card