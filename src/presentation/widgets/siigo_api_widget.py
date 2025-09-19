"""
Siigo API Widget - Componente UI especializado para descarga de facturas desde API Siigo
Parte de la refactorización del monolito dataconta_free_gui_refactored.py

Responsabilidad única: UI para interacción con API Siigo y filtros de descarga
"""

from typing import Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QFrame, QScrollArea, QLineEdit, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, Signal


class SiigoApiWidget(QWidget):
    """
    Widget especializado para descarga de facturas desde API Siigo.
    
    Principios SOLID:
    - SRP: Solo maneja la UI de API Siigo
    - OCP: Extensible para nuevos filtros y funcionalidades
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para API Siigo
    - DIP: Depende de abstracciones (signals)
    """
    
    # Signals para comunicación con el controlador (inversión de dependencias)
    export_siigo_csv_requested = Signal()
    export_siigo_excel_requested = Signal()
    test_connection_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Referencias a widgets de filtros
        self.siigo_date_start: Optional[QDateEdit] = None
        self.siigo_date_end: Optional[QDateEdit] = None
        self.siigo_client_id: Optional[QLineEdit] = None
        self.siigo_nit: Optional[QLineEdit] = None
        self.siigo_status: Optional[QComboBox] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz del widget de API Siigo."""
        # Widget contenedor principal con scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear scroll area para hacer el área de API Siigo responsive
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Widget interno con el contenido
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Grupo de configuración de filtros
        filters_group = self.create_filters_section()
        layout.addWidget(filters_group)
        
        # Botones de exportación
        buttons_group = self.create_buttons_section()
        layout.addWidget(buttons_group)
        
        layout.addStretch()
        
        # Configurar el scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def create_filters_section(self) -> QGroupBox:
        """Crear sección de filtros para API Siigo."""
        filters_group = QGroupBox("🌐 Descarga de Facturas desde API Siigo - DATOS REALES")
        filters_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        filters_layout = QGridLayout(filters_group)
        filters_layout.setContentsMargins(8, 20, 8, 8)  # Margen superior para separar título del contenido
        
        # Información de la API
        api_info = QLabel("""
        🔥 NUEVA FUNCIONALIDAD - DESCARGA DIRECTA DESDE SIIGO:
        
        ✅ API CONFIGURADA: erikagarcia1179@hotmail.com  
        ✅ CONEXIÓN REAL: Datos directos desde Siigo API
        ✅ FILTROS AVANZADOS: Por fechas, cliente, NIT, estado
        ✅ DOBLE EXPORT: CSV + Excel con dos hojas
        
        📊 Funcionalidad: Descarga facturas reales con filtros opcionales
        🎯 Resultado: Dos datasets (Encabezados + Detalle de ítems)
        """)
        api_info.setWordWrap(True)
        api_info.setStyleSheet("""
            background-color: #e3f2fd; 
            padding: 15px; 
            border-radius: 8px;
            border: 2px solid #1976d2;
            color: #1565c0;
            font-weight: bold;
            font-size: 12px;
        """)
        
        # Filtros de fecha
        filters_layout.addWidget(QLabel("📅 Fecha Inicio:"), 1, 0)
        self.siigo_date_start = QDateEdit()
        self.siigo_date_start.setToolTip(
            "🌐 Fecha inicio para API Siigo:\n"
            "• Descarga facturas desde esta fecha\n"
            "• Conecta directamente a Siigo\n"
            "• Por defecto: Hace 30 días\n\n"
            "🚀 100% datos reales desde Siigo API"
        )
        self.siigo_date_start.setCalendarPopup(True)
        self.siigo_date_start.setDate(datetime.now().date().replace(day=1))  # Primer día del mes
        filters_layout.addWidget(self.siigo_date_start, 1, 1)
        
        filters_layout.addWidget(QLabel("📅 Fecha Fin:"), 1, 2)
        self.siigo_date_end = QDateEdit()
        self.siigo_date_end.setToolTip(
            "🌐 Fecha fin para API Siigo:\n"
            "• Descarga facturas hasta esta fecha\n"
            "• Máximo rango: 1 año\n"
            "• Por defecto: Hoy\n\n"
            "🚀 Datos en tiempo real desde Siigo"
        )
        self.siigo_date_end.setCalendarPopup(True)
        self.siigo_date_end.setDate(datetime.now().date())  # Hoy
        filters_layout.addWidget(self.siigo_date_end, 1, 3)
        
        # Filtros de cliente
        filters_layout.addWidget(QLabel("🏢 Cliente ID:"), 2, 0)
        self.siigo_client_id = QLineEdit()
        self.siigo_client_id.setToolTip(
            "🆔 ID de cliente en Siigo (opcional):\n"
            "• Número interno de Siigo\n"
            "• Filtra facturas de cliente específico\n"
            "• Ejemplo: 12345\n\n"
            "⚡ Deje vacío para todos los clientes"
        )
        self.siigo_client_id.setPlaceholderText("ID del cliente (opcional)")
        filters_layout.addWidget(self.siigo_client_id, 2, 1)
        
        filters_layout.addWidget(QLabel("🆔 CC/NIT:"), 2, 2)
        self.siigo_nit = QLineEdit()
        self.siigo_nit.setToolTip(
            "🆔 NIT del cliente (opcional):\n"
            "• Número de identificación tributaria\n"
            "• Formato: 123456789-0\n"
            "• Filtra por documento específico\n\n"
            "⚡ Deje vacío para todos los NITs"
        )
        self.siigo_nit.setPlaceholderText("Cédula o NIT (opcional)")
        filters_layout.addWidget(self.siigo_nit, 2, 3)
        
        # Estado
        filters_layout.addWidget(QLabel("📋 Estado:"), 3, 0)
        self.siigo_status = QComboBox()
        self.siigo_status.setToolTip(
            "📈 Estado de facturas en Siigo:\n"
            "• Todas: Sin filtro\n"
            "• Pagada: Facturas cobradas\n"
            "• Abierta: Pendientes de pago\n"
            "• Vencida: En mora\n\n"
            "🌐 Estados sincronizados con Siigo"
        )
        self.siigo_status.addItems(["Todos", "abierta", "cerrada", "anulada"])
        filters_layout.addWidget(self.siigo_status, 3, 1)
        
        filters_layout.addWidget(api_info, 0, 0, 1, 4)
        
        return filters_group
    
    def create_buttons_section(self) -> QGroupBox:
        """Crear sección de botones de exportación."""
        buttons_group = QGroupBox("📤 Exportar Facturas Reales desde Siigo API")
        buttons_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        buttons_layout = QGridLayout(buttons_group)
        buttons_layout.setContentsMargins(8, 20, 8, 8)  # Margen superior para separar título del contenido
        
        siigo_btn_style = """
            QPushButton { 
                background-color: #1976d2; 
                color: white; 
                padding: 15px; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 12pt;
                border: none;
            }
            QPushButton:hover { 
                background-color: #1565c0; 
            }
        """
        
        # Botón CSV
        csv_siigo_btn = QPushButton("📊 Descargar y Exportar a CSV")
        csv_siigo_btn.setToolTip(
            "🌐 Descarga DIRECTA desde API Siigo:\n"
            "• Conecta en tiempo real a Siigo\n"
            "• Aplica todos los filtros configurados\n"
            "• Genera 2 archivos CSV:\n"
            "  - facturas_encabezados.csv\n"
            "  - facturas_detalle.csv\n\n"
            "🔥 100% datos reales desde Siigo API\n"
            "📊 Procesa encabezados + items detallados"
        )
        csv_siigo_btn.setStyleSheet(siigo_btn_style)
        csv_siigo_btn.clicked.connect(self.export_siigo_csv_requested.emit)
        buttons_layout.addWidget(csv_siigo_btn, 0, 0)
        
        # Botón Excel
        excel_siigo_btn = QPushButton("📄 Descargar y Exportar a Excel")
        excel_siigo_btn.setToolTip(
            "📄 Descarga desde API Siigo a Excel:\n"
            "• Un archivo .xlsx con 2 hojas:\n"
            "  - Hoja 'Encabezados'\n"
            "  - Hoja 'Detalle'\n"
            "• Formato profesional listo para análisis\n"
            "• Compatible con Power BI y tablas dinámicas\n\n"
            "🔥 Datos reales desde Siigo API\n"
            "📊 Ideal para reportes ejecutivos"
        )
        excel_siigo_btn.setStyleSheet(siigo_btn_style.replace("#1976d2", "#4caf50").replace("#1565c0", "#388e3c"))
        excel_siigo_btn.clicked.connect(self.export_siigo_excel_requested.emit)
        buttons_layout.addWidget(excel_siigo_btn, 0, 1)
        
        # Botón de prueba rápida
        test_btn = QPushButton("⚡ Prueba Rápida (Sin filtros)")
        test_btn.setToolTip(
            "⚡ Prueba de conectividad API Siigo:\n"
            "• Descarga facturas recientes\n"
            "• Sin aplicar filtros\n"
            "• Valida autenticación y conexión\n"
            "• Genera CSV de prueba\n\n"
            "🔧 Perfecto para:\n"
            "• Verificar configuración API\n"
            "• Probar credenciales\n"
            "• Validar estructura de datos"
        )
        test_btn.setStyleSheet(siigo_btn_style.replace("#1976d2", "#ff9800").replace("#1565c0", "#f57c00"))
        test_btn.clicked.connect(self.test_connection_requested.emit)
        buttons_layout.addWidget(test_btn, 1, 0, 1, 2)
        
        return buttons_group
    
    # ==================== Métodos para obtener valores de filtros ====================
    
    def get_date_start(self) -> str:
        """Obtener fecha de inicio seleccionada."""
        if self.siigo_date_start:
            return self.siigo_date_start.date().toString("yyyy-MM-dd")
        return ""
    
    def get_date_end(self) -> str:
        """Obtener fecha de fin seleccionada."""
        if self.siigo_date_end:
            return self.siigo_date_end.date().toString("yyyy-MM-dd")
        return ""
    
    def get_client_id(self) -> str:
        """Obtener ID de cliente."""
        if self.siigo_client_id:
            return self.siigo_client_id.text().strip()
        return ""
    
    def get_nit(self) -> str:
        """Obtener NIT del cliente."""
        if self.siigo_nit:
            return self.siigo_nit.text().strip()
        return ""
    
    def get_status(self) -> str:
        """Obtener estado seleccionado."""
        if self.siigo_status:
            status = self.siigo_status.currentText()
            return "" if status == "Todos" else status
        return ""
    
    def get_filters(self) -> dict:
        """Obtener todos los filtros como diccionario."""
        return {
            "date_start": self.get_date_start(),
            "date_end": self.get_date_end(),
            "client_id": self.get_client_id(),
            "nit": self.get_nit(),
            "status": self.get_status()
        }
    
    # ==================== Métodos de UI ====================
    
    def show_success_message(self, title: str, message: str):
        """Mostrar mensaje de éxito."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)
    
    def show_error_message(self, title: str, message: str):
        """Mostrar mensaje de error."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, title, message)
    
    def clear_filters(self):
        """Limpiar todos los filtros."""
        if self.siigo_date_start:
            self.siigo_date_start.setDate(datetime.now().date().replace(day=1))
        if self.siigo_date_end:
            self.siigo_date_end.setDate(datetime.now().date())
        if self.siigo_client_id:
            self.siigo_client_id.clear()
        if self.siigo_nit:
            self.siigo_nit.clear()
        if self.siigo_status:
            self.siigo_status.setCurrentIndex(0)  # "Todos"