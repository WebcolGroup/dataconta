"""
Tabs Widget - Componente UI especializado para navegación con tabs
Parte de la refactorización del monolito dataconta_free_gui_refactored.py

Responsabilidad única: UI de navegación con tabs y estilo FREE
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QScrollArea, QFrame
)
from PySide6.QtCore import Qt

# Imports de widgets especializados
from src.presentation.widgets.dashboard_widget import DashboardWidget
from src.presentation.widgets.query_widget import QueryWidget
from src.presentation.widgets.exportar_widget import ExportarWidget
from src.presentation.widgets.reportes_widget import ReportesWidget
from src.presentation.widgets.ayuda_widget import AyudaWidget
from src.presentation.widgets.upgrade_widget import UpgradeWidget


class TabsWidget(QWidget):
    """
    Widget especializado para navegación con tabs estilo FREE.
    
    Principios SOLID:
    - SRP: Solo maneja la UI de navegación con tabs
    - OCP: Extensible para nuevas tabs
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para navegación
    - DIP: Depende de abstracciones (widgets especializados)
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Referencias a widgets especializados
        self.dashboard_widget: Optional[DashboardWidget] = None
        self.query_widget: Optional[QueryWidget] = None
        self.exportar_widget: Optional[ExportarWidget] = None
        self.reportes_widget: Optional[ReportesWidget] = None
        self.upgrade_widget: Optional[UpgradeWidget] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz del widget de tabs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear tabs con estilo FREE
        tabs = self._create_free_tabs()
        layout.addWidget(tabs)
    
    def _create_free_tabs(self) -> QTabWidget:
        """Crear pestañas estilo PRO para versión FREE."""
        tab_widget = QTabWidget()
        tab_widget.setObjectName("MainTabs")
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #1976d2;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #e3f2fd;
                color: #1976d2;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #1976d2;
                color: white;
            }
        """)
        
        # Tab 1: Dashboard FREE con KPIs básicos
        dashboard_tab = self._create_dashboard_free()
        tab_widget.addTab(dashboard_tab, "📊 Dashboard FREE")
        
        # Tab 2: Consulta de facturas
        queries_tab = self._create_queries_free()
        tab_widget.addTab(queries_tab, "🔍 Consultar Facturas")
        
        # Tab 3: Exportar facturas desde API Siigo  
        exportar_tab = self._create_exportar_tab()
        tab_widget.addTab(exportar_tab, "📤 Exportar")
        
        # Tab 4: Reportes financieros
        reportes_tab = self._create_reportes_tab()
        tab_widget.addTab(reportes_tab, "📊 Reportes")
        
        # Tab 5: Ayuda y soporte
        ayuda_tab = self._create_ayuda_tab()
        tab_widget.addTab(ayuda_tab, "❓ Ayuda")
        
        # Tab 6: Funciones PRO (con avisos) 
        pro_tab = self._create_pro_preview_tab()
        tab_widget.addTab(pro_tab, "⭐ Funciones PRO")
        
        return tab_widget
    
    def _create_dashboard_free(self) -> QWidget:
        """Crear tab de dashboard FREE."""
        self.dashboard_widget = DashboardWidget()
        dashboard_scroll = QScrollArea()
        dashboard_scroll.setWidget(self.dashboard_widget)
        dashboard_scroll.setWidgetResizable(True)
        dashboard_scroll.setFrameShape(QFrame.NoFrame)
        return dashboard_scroll
    
    def _create_queries_free(self) -> QWidget:
        """Crear tab de consultas FREE."""
        self.query_widget = QueryWidget()
        query_scroll = QScrollArea()
        query_scroll.setWidget(self.query_widget)
        query_scroll.setWidgetResizable(True)
        query_scroll.setFrameShape(QFrame.NoFrame)
        return query_scroll
    
    def _create_exportar_tab(self) -> QWidget:
        """Crear tab de exportar facturas."""
        self.exportar_widget = ExportarWidget()
        exportar_scroll = QScrollArea()
        exportar_scroll.setWidget(self.exportar_widget)
        exportar_scroll.setWidgetResizable(True)
        exportar_scroll.setFrameShape(QFrame.NoFrame)
        return exportar_scroll
    
    def _create_reportes_tab(self) -> QWidget:
        """Crear tab de reportes financieros."""
        self.reportes_widget = ReportesWidget()
        reportes_scroll = QScrollArea()
        reportes_scroll.setWidget(self.reportes_widget)
        reportes_scroll.setWidgetResizable(True)
        reportes_scroll.setFrameShape(QFrame.NoFrame)
        return reportes_scroll
    
    def _create_ayuda_tab(self) -> QWidget:
        """Crear tab de ayuda con submenús usando AyudaWidget especializado."""
        self.ayuda_widget = AyudaWidget()
        
        # Crear scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.ayuda_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        return scroll_area
    
    # ==================== Getters para acceder a widgets especializados ====================
    
    def get_dashboard_widget(self) -> Optional[DashboardWidget]:
        """Obtener referencia al dashboard widget."""
        return self.dashboard_widget
    
    def get_query_widget(self) -> Optional[QueryWidget]:
        """Obtener referencia al query widget."""
        return self.query_widget
    
    def get_exportar_widget(self) -> Optional[ExportarWidget]:
        """Obtener referencia al exportar widget."""
        return self.exportar_widget
    
    def get_reportes_widget(self) -> Optional[ReportesWidget]:
        """Obtener referencia al reportes widget."""
        return self.reportes_widget
    
    def get_ayuda_widget(self) -> Optional[AyudaWidget]:
        """Obtener referencia al ayuda widget."""
        return getattr(self, 'ayuda_widget', None)
    
    def get_upgrade_widget(self) -> Optional[UpgradeWidget]:
        """Obtener referencia al upgrade widget."""
        return self.upgrade_widget
    
    # ==================== Funciones PRO (al final del archivo) ====================
    
    def _create_pro_preview_tab(self) -> QWidget:
        """Crear tab de funciones PRO usando UpgradeWidget especializado."""
        self.upgrade_widget = UpgradeWidget()
        
        # Crear scroll area para el widget de upgrade
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.upgrade_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        return scroll_area
    
