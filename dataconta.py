"""
DataConta FREE GUI - Versión NO Monolítica con Arquitectura Hexagonal

Este archivo es ahora el entrypoint canónico con el contenido completo de la versión no monolítica.
"""

# ==================== Imports - Librerías Est        # LogWidget removido - logs ahora disponibles en tab Ayuda modal==================
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

# ==================== Imports - Sistema de Addons ====================
from src.infrastructure.factories.addon_factory import AddonFactory

# ==================== Imports - Widgets Especializados (NO monolíticos) ====================
from src.presentation.widgets.dashboard_widget import DashboardWidget
from src.presentation.widgets.export_widget import ExportWidget
from src.presentation.widgets.query_widget import QueryWidget
from src.presentation.widgets.tabs_widget import TabsWidget
from src.presentation.widgets.demo_handler_widget import DemoHandlerWidget
# LogWidget removido - logs ahora disponibles en modal de tab Ayuda


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
        
        self.init_ui()
        self.setup_window()
        self.connect_signals()
        self._load_initial_data()
    
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
            
            # Comentado: Ahora el widget maneja directamente la funcionalidad TOP clientes
            # dashboard_widget.show_top_clients_requested.connect(
            #     self.demo_handler.show_top_clients_demo
            # )
            dashboard_widget.pro_upgrade_requested.connect(
                self.demo_handler.show_pro_upgrade_demo
            )
            
            # Conectar señal de controlador de vuelta al dashboard
            print("🔗 Conectando señal kpis_calculated...")
            self.controller.kpis_calculated.connect(
                lambda kpi_data: self._handle_kpis_update(dashboard_widget, kpi_data)
            )
            print("✅ Señal kpis_calculated conectada con manejo inteligente")
        else:
            print("❌ dashboard_widget es None - no se pueden conectar señales")
        
        # Export widget eliminado - funcionalidad movida a ExportarWidget
        # Las exportaciones ahora se manejan desde el tab "Exportar"
        
        # Query signals
        query_widget = self.tabs_widget.get_query_widget()
        if query_widget:
            query_widget.search_invoices_requested.connect(
                self._handle_invoice_search
            )
            query_widget.clear_filters_requested.connect(
                self._handle_clear_filters
            )
            # Signal para carga de estados
            query_widget.load_statuses_requested.connect(
                self._handle_load_statuses
            )
        
        # Exportar widget signals (formerly Siigo API)
        exportar_widget = self.tabs_widget.get_exportar_widget()
        if exportar_widget:
            exportar_widget.export_siigo_csv_requested.connect(
                self._handle_siigo_csv_export
            )
            exportar_widget.export_siigo_excel_requested.connect(
                self._handle_siigo_excel_export
            )
        
        # Reportes widget signals
        reportes_widget = self.tabs_widget.get_reportes_widget()
        if reportes_widget:
            print("🔗 Conectando señales de reportes...")
            reportes_widget.estado_resultados_requested.connect(
                self.controller.handle_estado_resultados_request
            )
            print("✅ Señal estado_resultados_requested conectada")
            
            # Conectar nueva señal de Estado de Resultados Excel
            if hasattr(reportes_widget, 'estado_resultados_excel_requested'):
                reportes_widget.estado_resultados_excel_requested.connect(
                    self.controller.handle_estado_resultados_excel_request
                )
                print("✅ Señal estado_resultados_excel_requested conectada")
            
            # Conectar señal de éxito/error del controlador al widget
            self.controller.estado_resultados_generated.connect(
                lambda file_path, summary: reportes_widget.show_success_message(file_path)
            )
        else:
            print("❌ reportes_widget es None - no se pueden conectar señales")
            exportar_widget.test_connection_requested.connect(
                self.demo_handler.show_siigo_connection_demo
            )
        
        # LogWidget removido - logs ahora disponibles en tab Ayuda modal
        
        # Initialize logging with welcome message
        self.log_message("🆓 DataConta FREE iniciado - Arquitectura NO Monolítica")
        self.log_message("📊 Componentes especializados cargados correctamente")
    
    # ---------- Métodos de Actualización de UI ----------
    def _handle_kpis_update(self, dashboard_widget, kpi_data: Dict[str, Any]):
        """Manejar actualización de KPIs con contexto automático vs manual."""
        try:
            # Determinar si es carga automática basándose en el estado actual
            is_auto_load = not hasattr(self, '_kpis_manually_requested')
            
            # Actualizar dashboard con o sin mensaje según el contexto
            dashboard_widget.update_kpis(kpi_data, show_message=not is_auto_load)
            
            # Marcar que ya se procesaron KPIs iniciales
            self._kpis_manually_requested = True
            
        except Exception as e:
            print(f"❌ Error manejando actualización de KPIs: {e}")
    
    def update_kpis_display(self, kpi_data: Dict[str, Any]):
        """Actualizar KPIs en el dashboard widget."""
        if self.tabs_widget:
            dashboard_widget = self.tabs_widget.get_dashboard_widget()
            if dashboard_widget:
                dashboard_widget.update_kpis(kpi_data)
    
    # ---------- Handlers de Acciones (Delegación a Controlador y Demo Handler) ----------
    def _handle_invoice_search(self, filters: Dict[str, Any]):
        """Manejar búsqueda de facturas con API real de Siigo."""
        try:
            query_widget = self.tabs_widget.get_query_widget() if self.tabs_widget else None
            if not query_widget:
                return
                
            # Mostrar mensaje de carga
            query_widget.show_success_message("Búsqueda", "🔄 Consultando API de Siigo...")
            
            # Realizar búsqueda real con el controlador
            facturas = self.controller.search_invoices_with_pagination(filters)
            
            if facturas:
                # Mostrar resultados
                query_widget.update_results(facturas)
                query_widget.show_search_results_summary(len(facturas), filters)
                
                # Log de éxito
                self.controller._logger.info(f"✅ Búsqueda completada: {len(facturas)} facturas encontradas")
            else:
                # No se encontraron facturas
                query_widget._show_no_results_message()
                query_widget.show_success_message("Sin Resultados", "🔍 No se encontraron facturas con los criterios especificados.")
                
        except Exception as e:
            self.controller._logger.error(f"❌ Error en búsqueda de facturas: {e}")
            query_widget = self.tabs_widget.get_query_widget() if self.tabs_widget else None
            if query_widget:
                query_widget.show_error_message("Error de Búsqueda", f"Error consultando API: {str(e)}")
    
    def _handle_clear_filters(self):
        """Manejar limpieza de filtros."""
        if self.tabs_widget:
            query_widget = self.tabs_widget.get_query_widget()
            if query_widget:
                # Delegar al demo handler para mostrar mensaje
                self.demo_handler.show_clear_filters_demo()
    
    def _handle_load_statuses(self):
        """Manejar carga de estados para dropdown."""
        try:
            self.controller._logger.info("🔄 Cargando estados de facturas...")
            print(f"[DEBUG Dataconta] 🔄 Iniciando carga de estados...")
            
            statuses = self.controller.load_invoice_statuses()
            print(f"[DEBUG Dataconta] 📊 Controlador devolvió {len(statuses)} estados")
            
            query_widget = self.tabs_widget.get_query_widget()
            if query_widget and statuses:
                print(f"[DEBUG Dataconta] ✅ Widget encontrado, enviando {len(statuses)} estados")
                query_widget.update_statuses(statuses)
                self.controller._logger.info(f"✅ {len(statuses)} estados cargados en dropdown")
            else:
                print(f"[DEBUG Dataconta] ❌ Widget={query_widget is not None}, estados={len(statuses) if statuses else 0}")
                self.controller._logger.warning("⚠️ No se encontraron estados para cargar")
                
        except Exception as e:
            print(f"[DEBUG Dataconta] ❌ Error cargando estados: {e}")
            import traceback
            print(f"[DEBUG Dataconta] 📋 Traceback: {traceback.format_exc()}")
            self.controller._logger.error(f"❌ Error cargando estados: {e}")
            query_widget = self.tabs_widget.get_query_widget() if self.tabs_widget else None
            if query_widget:
                query_widget.show_error_message("Error de Carga", f"No se pudieron cargar los estados: {str(e)}")
    
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
        Centralized logging method - LogWidget removido, logs disponibles en tab Ayuda.
        
        Args:
            message (str): The message to log
        """
        try:
            # Log to console and app.log file - LogWidget removido por modal en tab Ayuda
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
            # TODO: También escribir a app.log si se requiere logging a archivo
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
    
    def _load_initial_data(self):
        """Cargar datos iniciales después de conectar señales."""
        try:
            print("[DATACONTA] 🔄 Iniciando carga de datos iniciales...")
            
            query_widget = self.tabs_widget.get_query_widget()
            if query_widget:
                print("[DATACONTA] ✅ QueryWidget encontrado, solicitando datos iniciales")
                query_widget.request_initial_data()
            else:
                print("[DATACONTA] ❌ No se encontró QueryWidget")
                
        except Exception as e:
            print(f"[DATACONTA] ❌ Error cargando datos iniciales: {e}")


# ==================== Factory Function (Inyección de Dependencias) ====================

def create_dataconta_app() -> DataContaMainWindow:
    """
    Factory function para crear la aplicación con arquitectura hexagonal NO monolítica.
    
    NUEVO: Ahora incluye sistema de addons integrado de forma transparente.
    
    Implementa inyección de dependencias completa siguiendo principios SOLID.
    
    Returns:
        DataContaMainWindow: Instancia NO monolítica de la aplicación con addons
    """
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear adaptador de logger (Infrastructure Layer)
    logger = LoggerAdapter(name="dataconta_non_monolithic")
    logger.info("🏗️ Iniciando DataConta")
    
    # ==================== NUEVO: SISTEMA DE ADDONS ====================
    # Inicializar sistema de addons (completamente opcional y no-invasivo)
    addon_system = None
    
    try:
        logger.info("🔌 Inicializando sistema de addons...")
        
        # Crear sistema de addons usando factory pattern
        addon_system = AddonFactory.create_complete_addon_system(
            repository_path="addons/",
            logger=logger
        )
        
        # Cargar addons disponibles
        loaded_addons = addon_system.load_all_addons()
        active_addons = addon_system.get_active_addons()
        
        if active_addons:
            logger.info(f"✅ Sistema de addons inicializado: {len(active_addons)} addons activos")
            for addon in active_addons:
                logger.info(f"  📦 {addon.get_name()} v{addon.get_version()}")
        else:
            logger.info("ℹ️  Sistema de addons listo (no hay addons instalados)")
            
    except Exception as e:
        logger.warning(f"⚠️  Sistema de addons no disponible: {e}")
        # Continúa normalmente sin addons - NO es un error crítico
        addon_system = None
    
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
    
    # ==================== NUEVO: INTEGRAR ADDONS CON UI ====================
    # Vincular sistema de addons con la interfaz (si está disponible)
    if addon_system:
        try:
            # Agregar referencia del addon system a la ventana principal
            main_window.addon_system = addon_system
            logger.info("🎛️  Sistema de addons vinculado con interfaz")
            
        except Exception as e:
            logger.warning(f"⚠️  Error integrando addons con UI: {e}")
    
    logger.info("✅ DataConta NO Monolítico creado exitosamente")
    
    # ==================== NUEVO: LOG DE ESTADÍSTICAS ====================
    if addon_system:
        active_addons = addon_system.get_active_addons()
        if active_addons:
            stats = {
                'total_addons': len(active_addons),
                'addon_names': [addon.get_name() for addon in active_addons]
            }
            logger.info(f"📊 Estadísticas de addons: {stats}")
    
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
        print("🚀 Iniciando DataConta FREE - Versión NO Monolítica con Addons")
        print("=" * 70)
        print("📊 Componentes especializados:")
        print("  • DashboardWidget: UI de KPIs")
        print("  • ExportWidget: UI de exportaciones")  
        print("  • QueryWidget: UI de consultas")
        print("  • MainWindow: Solo coordinación")
        print("  🔌 • Sistema de Addons: Extensibilidad de comunidad")
        print("=" * 70)
        
        # Crear aplicación NO monolítica
        main_window = create_dataconta_app()
        main_window.show()
        
        print("✅ Aplicación NO Monolítica iniciada correctamente")
        
        # Verificar configuración de Siigo API después de mostrar la ventana principal
        from src.presentation.widgets.ayuda_widget import SiigoConfigDialog
        
        # Pequeña pausa para que la ventana principal se renderice completamente
        app.processEvents()
        
        # Auto-abrir configurador de Siigo si es necesario
        if SiigoConfigDialog.needs_configuration():
            print("⚙️ Configuración de Siigo API requerida - abriendo configurador...")
            SiigoConfigDialog.auto_open_if_needed(main_window)
        
        # Ejecutar la aplicación
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error iniciando aplicación NO monolítica: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())