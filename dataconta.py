"""
DataConta FREE GUI - Versión NO Monolítica con Arquitectura Hexagonal

Este archivo es ahora el entrypoint canónico con el contenido completo de la versión no monolítica.
"""

# ==================== Imports - Librerías Estándar ====================
import sys
import os
import logging
from typing import Optional, Dict, Any

# ==================== Imports - PySide6 (Framework UI) ====================
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QFrame, QHBoxLayout, QLabel, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QColor

# ==================== Imports - Tema Material (Opcional) ====================
# Tema Material (opcional con fallback)
try:
    from qt_material import apply_stylesheet
except Exception:  # pragma: no cover - fallback si no está instalado
    apply_stylesheet = None

# ==================== Imports - Arquitectura Hexagonal ====================
from src.presentation.controllers.free_gui_controller import FreeGUIController
from src.application.services.kpi_service import KPIService
from src.application.services.export_service import ExportService
from src.infrastructure.adapters.free_gui_siigo_adapter import FreeGUISiigoAdapter
from src.infrastructure.adapters.file_storage_adapter import FileStorageAdapter
from src.infrastructure.adapters.logger_adapter import LoggerAdapter

# ==================== Imports - Widgets Especializados (NO monolíticos) ====================
from src.presentation.widgets.dashboard_widget import DashboardWidget
from src.presentation.widgets.export_widget import ExportWidget
from src.presentation.widgets.query_widget import QueryWidget
from src.presentation.widgets.tabs_widget import TabsWidget
from src.presentation.widgets.demo_handler_widget import DemoHandlerWidget
from src.ui.log_widget import LogWidget


# ==================== Clase Principal - DataConta Main Window ====================

class DataContaMainWindow(QMainWindow):
    """
    Ventana principal NO monolítica de DataConta FREE.
    
    Responsabilidades:
    - Coordinar componentes UI especializados
    - Manejar la comunicación entre widgets y controlador
    - Gestionar el layout principal y navegación
    
    NO ES RESPONSABLE DE:
    - Lógica de negocio (delegada al controlador)
    - Creación detallada de widgets (delegada a componentes especializados)
    - Manejo directo de datos (delegado a servicios)
    """
    
    # ---------- Constructor y Configuración Inicial ----------
    def __init__(self, controller: FreeGUIController):
        super().__init__()
        self.controller = controller
        self.controller.set_gui_reference(self)
        
        # Componente de navegación especializado
        self.tabs_widget: Optional[TabsWidget] = None
        
        # Componente especializado para demos (desacoplamiento completo)
        self.demo_handler = DemoHandlerWidget(self)
        
        # Componente especializado para logs (visualización de actividades)
        self.log_widget: Optional[LogWidget] = None
        
        self.init_ui()
        self.setup_window()
        self.connect_signals()
    
    # ---------- Configuración de Ventana ----------
    def setup_window(self):
        """Configurar ventana principal."""
        self.setWindowTitle("🆓 DataConta FREE - Análisis Financiero y Contable")
        
        # Tamaño dinámico
        screen = QApplication.primaryScreen().geometry()
        min_width = max(800, int(screen.width() * 0.6))
        min_height = max(600, int(screen.height() * 0.7))
        self.setMinimumSize(min_width, min_height)
        
        # Tamaño inicial
        initial_width = min(1200, int(screen.width() * 0.8))
        initial_height = min(800, int(screen.height() * 0.85))
        self.resize(initial_width, initial_height)
        
        # Centrar ventana
        self.move(
            (screen.width() - initial_width) // 2,
            (screen.height() - initial_height) // 2
        )
        
        # Maximizar ventana siempre
        self.showMaximized()
        
        # Aplicar estilos globales (complementarios al tema Material)
        self.setStyleSheet(self._get_global_styles())
    
    # ---------- Inicialización de UI ----------
    def init_ui(self):
        """Inicializar interfaz de usuario con componentes especializados."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header envuelto en tarjeta
        header_card = self._wrap_in_card(self._create_header())
        main_layout.addWidget(header_card)
        
        # Tabs con componentes especializados usando TabsWidget desacoplado
        self.tabs_widget = TabsWidget()
        tabs_card = self._wrap_in_card(self.tabs_widget)
        main_layout.addWidget(tabs_card)
        
        # LogWidget especializado (parte inferior)
        self.log_widget = LogWidget()
        log_card = self._wrap_in_card(self.log_widget)
        main_layout.addWidget(log_card)
    
    # ---------- Creación de Componentes UI ----------
    def _create_header(self) -> QWidget:
        """Crear header simple y elegante (contenido, sin card externa)."""
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 18, 20, 18)

        # Título principal
        title_label = QLabel("🆓 DataConta FREE ")
        title_label.setObjectName("HeaderTitle")
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: 700;
        """)

        # Subtítulo
        subtitle_label = QLabel("📊  Análisis Financiero y Contable")
        subtitle_label.setObjectName("HeaderSubtitle")
        subtitle_label.setStyleSheet("""
            color: #E3F2FD;
            font-size: 14px;
            font-weight: 600;
        """)

        # Layout para textos
        text_layout = QVBoxLayout()
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        # Fondo gradiente para el header
        header_frame.setStyleSheet("""
            QFrame#HeaderFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1976d2, stop: 0.5 #42a5f5, stop: 1 #1976d2);
                border-radius: 12px;
            }
        """)
        return header_frame
    
    # ---------- Conexión de Signals (Comunicación entre Componentes) ----------
    def connect_signals(self):
        """Conectar signals de los widgets con el controlador."""
        if not self.tabs_widget:
            return
            
        # Dashboard signals
        dashboard_widget = self.tabs_widget.get_dashboard_widget()
        if dashboard_widget:
            print("🔗 Conectando señales de dashboard...")
            dashboard_widget.refresh_kpis_requested.connect(
                self.controller.refresh_kpis
            )
            print("✅ Señal refresh_kpis_requested conectada")
            
            dashboard_widget.show_top_clients_requested.connect(
                self.demo_handler.show_top_clients_demo
            )
            dashboard_widget.pro_upgrade_requested.connect(
                self.demo_handler.show_pro_upgrade_demo
            )
            
            # Conectar señal de controlador de vuelta al dashboard
            print("🔗 Conectando señal kpis_calculated...")
            self.controller.kpis_calculated.connect(
                dashboard_widget.update_kpis
            )
            print("✅ Señal kpis_calculated conectada")
        else:
            print("❌ dashboard_widget es None - no se pueden conectar señales")
        
        # Export signals
        export_widget = self.tabs_widget.get_export_widget()
        if export_widget:
            export_widget.export_csv_requested.connect(
                self.controller.export_csv_real
            )
            export_widget.export_csv_simple_requested.connect(
                self.controller.export_csv_simple
            )
            export_widget.export_excel_requested.connect(
                self.controller.export_excel_real
            )
            export_widget.siigo_csv_export_requested.connect(
                self._handle_siigo_csv_export
            )
            export_widget.siigo_excel_export_requested.connect(
                self._handle_siigo_excel_export
            )
            export_widget.test_connection_requested.connect(
                self.demo_handler.show_siigo_connection_demo
            )
        
        # Query signals
        query_widget = self.tabs_widget.get_query_widget()
        if query_widget:
            query_widget.search_invoices_requested.connect(
                self._handle_invoice_search
            )
            query_widget.clear_filters_requested.connect(
                self._handle_clear_filters
            )
        
        # Siigo API signals
        siigo_api_widget = self.tabs_widget.get_siigo_api_widget()
        if siigo_api_widget:
            siigo_api_widget.export_siigo_csv_requested.connect(
                self._handle_siigo_csv_export
            )
            siigo_api_widget.export_siigo_excel_requested.connect(
                self._handle_siigo_excel_export
            )
            siigo_api_widget.test_connection_requested.connect(
                self.demo_handler.show_siigo_connection_demo
            )
        
        # LogWidget signals (if available)
        if self.log_widget:
            self.log_widget.log_cleared.connect(
                lambda: self.log_message("🗑️ Logs limpiados por usuario")
            )
            self.log_widget.log_exported.connect(
                lambda filepath: self.log_message(f"💾 Logs exportados a: {filepath}")
            )
        
        # Initialize logging with welcome message
        self.log_message("🆓 DataConta FREE iniciado - Arquitectura NO Monolítica")
        self.log_message("📊 Componentes especializados cargados correctamente")
    
    # ---------- Métodos de Actualización de UI ----------
    def update_kpis_display(self, kpi_data: Dict[str, Any]):
        """Actualizar KPIs en el dashboard widget."""
        if self.tabs_widget:
            dashboard_widget = self.tabs_widget.get_dashboard_widget()
            if dashboard_widget:
                dashboard_widget.update_kpis(kpi_data)
    
    # ---------- Handlers de Acciones (Delegación a Controlador y Demo Handler) ----------
    def _handle_invoice_search(self, filters: Dict[str, Any]):
        """Manejar búsqueda de facturas."""
        try:
            # Delegar al demo handler para obtener datos demo
            demo_invoices = self.demo_handler.show_invoice_search_demo(filters)
            
            query_widget = self.tabs_widget.get_query_widget() if self.tabs_widget else None
            if query_widget:
                query_widget.update_results(demo_invoices)
                query_widget.show_search_results_summary(len(demo_invoices), filters)
                
        except Exception as e:
            query_widget = self.tabs_widget.get_query_widget() if self.tabs_widget else None
            if query_widget:
                query_widget.show_error_message("Error de Búsqueda", str(e))
    
    def _handle_clear_filters(self):
        """Manejar limpieza de filtros."""
        if self.tabs_widget:
            query_widget = self.tabs_widget.get_query_widget()
            if query_widget:
                # Delegar al demo handler para mostrar mensaje
                self.demo_handler.show_clear_filters_demo()
    
    def _handle_siigo_csv_export(self):
        """Manejar exportación CSV desde Siigo."""
        try:
            # Delegar al controlador
            if hasattr(self.controller, 'export_siigo_csv_with_filters'):
                self.controller.export_siigo_csv_with_filters()
            else:
                self.controller.export_csv_real(100)
            
            # Delegar demo al handler
            self.demo_handler.show_export_success_demo("csv")
        except Exception as e:
            # Delegar error al handler
            self.demo_handler.show_export_error_demo(str(e))
    
    def _handle_siigo_excel_export(self):
        """Manejar exportación Excel desde Siigo."""
        try:
            # Delegar al controlador
            if hasattr(self.controller, 'export_siigo_excel_with_filters'):
                self.controller.export_siigo_excel_with_filters()
            else:
                self.controller.export_excel_real(100)
            
            # Delegar demo al handler
            self.demo_handler.show_export_success_demo("excel")
        except Exception as e:
            # Delegar error al handler
            self.demo_handler.show_export_error_demo(str(e))
    
    # ---------- Estilos y Helpers de UI ----------
    def _get_global_styles(self) -> str:
        """Obtener estilos globales de la aplicación."""
        return """
            QMainWindow { background-color: #f5f5f5; }
            /* Card container */
            QFrame#CardFrame {
                background: #ffffff;
                border-radius: 14px;
                border: 1px solid rgba(0,0,0,0.08);
            }

            /* Tablas (QTableView/QTableWidget) - Estilo Material */
            QTableView, QTableWidget {
                background: #ffffff;
                alternate-background-color: #fafafa;
                gridline-color: rgba(0,0,0,0.06);
                selection-background-color: #1976d2;
                selection-color: #ffffff;
                border: none;
            }
            QHeaderView::section {
                background: #f5f5f5;
                color: #37474f;
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid rgba(0,0,0,0.08);
                font-weight: 600;
                font-size: 12px;
            }
            QTableView::item { padding: 8px 12px; }
            QTableView::item:hover { background: #e3f2fd; }
            QTableView::item:selected {
                background: #1976d2;
                color: #ffffff;
            }
            /* Header vertical más limpio */
            QTableView QHeaderView::section:vertical {
                background: transparent;
                border: none;
            }
        """
    
    # ---------- Logging Functionality ----------
    def log_message(self, message: str):
        """
        Centralized logging method that sends messages to LogWidget.
        
        Args:
            message (str): The message to log
        """
        try:
            if self.log_widget:
                self.log_widget.log_message(message)
            else:
                # Fallback to console if LogWidget not available
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {message}")
        except Exception as e:
            print(f"Error in log_message: {e}")
    
    # ---------- Helper Methods ----------
    def _wrap_in_card(self, inner: QWidget) -> QFrame:
        """Envuelve un widget en una 'card' con esquinas redondeadas y sombra."""
        card = QFrame()
        card.setObjectName("CardFrame")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.addWidget(inner)

        # Sombra sutil estilo Material
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)
        return card


# ==================== Factory Function (Inyección de Dependencias) ====================

def create_dataconta_app() -> DataContaMainWindow:
    """
    Factory function para crear la aplicación con arquitectura hexagonal NO monolítica.
    
    Implementa inyección de dependencias completa siguiendo principios SOLID.
    
    Returns:
        DataContaMainWindow: Instancia NO monolítica de la aplicación
    """
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear adaptador de logger (Infrastructure Layer)
    logger = LoggerAdapter(name="dataconta_non_monolithic")
    logger.info("🏗️ Iniciando DataConta")
    
    # Crear adaptadores de infraestructura
    siigo_adapter = FreeGUISiigoAdapter(logger=logger)
    file_storage = FileStorageAdapter(output_directory="./outputs", logger=logger)
    
    # Crear servicios de aplicación
    kpi_service = KPIService(
        invoice_repository=siigo_adapter,
        file_storage=file_storage,
        logger=logger
    )
    
    export_service = ExportService(
        invoice_repository=siigo_adapter,
        file_storage=file_storage,
        logger=logger
    )
    
    # Crear controlador (Application Layer)
    controller = FreeGUIController(
        kpi_service=kpi_service,
        export_service=export_service,
        invoice_repository=siigo_adapter,
        logger=logger,
        file_storage=file_storage
    )
    
    # Crear GUI NO monolítica (Presentation Layer)
    main_window = DataContaMainWindow(controller)
    
    logger.info("✅ DataConta NO Monolítico creado exitosamente")
    return main_window


# ==================== Main Application Entry Point ====================

def main():
    """Función principal de la aplicación NO monolítica."""
    app = QApplication(sys.argv)
    
    try:
        # Aplicar tema Material si está disponible
        if apply_stylesheet is not None:
            try:
                apply_stylesheet(app, theme="light_blue_500.xml")
            except Exception:
                # Fallback silencioso si el tema no puede cargarse
                pass
        print("🚀 Iniciando DataConta FREE - Versión NO Monolítica")
        print("=" * 60)
        print("📊 Componentes especializados:")
        print("  • DashboardWidget: UI de KPIs")
        print("  • ExportWidget: UI de exportaciones")  
        print("  • QueryWidget: UI de consultas")
        print("  • MainWindow: Solo coordinación")
        print("=" * 60)
        
        # Crear aplicación NO monolítica
        main_window = create_dataconta_app()
        main_window.show()
        
        print("✅ Aplicación NO Monolítica iniciada correctamente")
        
        # Ejecutar la aplicación
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error iniciando aplicación NO monolítica: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())