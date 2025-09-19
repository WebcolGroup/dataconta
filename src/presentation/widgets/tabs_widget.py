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
from src.presentation.widgets.export_widget import ExportWidget
from src.presentation.widgets.query_widget import QueryWidget
from src.presentation.widgets.siigo_api_widget import SiigoApiWidget


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
        self.export_widget: Optional[ExportWidget] = None
        self.query_widget: Optional[QueryWidget] = None
        self.siigo_api_widget: Optional[SiigoApiWidget] = None
        
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
        
        # Tab 3: Exportaciones (FUNCIONALIDAD EXISTENTE)
        export_tab = self._create_export_free()
        tab_widget.addTab(export_tab, "📤 Exportar CSV")
        
        # Tab 4: Nueva funcionalidad - Descarga API Siigo  
        siigo_tab = self._create_siigo_api_tab()
        tab_widget.addTab(siigo_tab, "🌐 API Siigo")
        
        # Tab 5: Funciones PRO (con avisos)
        pro_tab = self._create_pro_preview_tab()
        tab_widget.addTab(pro_tab, "🏆 Funciones PRO")
        
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
    
    def _create_export_free(self) -> QWidget:
        """Crear tab de exportaciones FREE."""
        self.export_widget = ExportWidget()
        export_scroll = QScrollArea()
        export_scroll.setWidget(self.export_widget)
        export_scroll.setWidgetResizable(True)
        export_scroll.setFrameShape(QFrame.NoFrame)
        return export_scroll
    
    def _create_siigo_api_tab(self) -> QWidget:
        """Crear tab de API Siigo."""
        self.siigo_api_widget = SiigoApiWidget()
        siigo_scroll = QScrollArea()
        siigo_scroll.setWidget(self.siigo_api_widget)
        siigo_scroll.setWidgetResizable(True)
        siigo_scroll.setFrameShape(QFrame.NoFrame)
        return siigo_scroll
    
    def _create_pro_preview_tab(self) -> QWidget:
        """Crear tab de preview PRO (placeholder por ahora)."""
        # TODO: Crear widget especializado para preview PRO
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.addWidget(self._create_placeholder_content("🏆 Funciones PRO", 
                                                         "Preview de funcionalidades exclusivas PRO"))
        return placeholder
    
    def _create_placeholder_content(self, title: str, description: str) -> QWidget:
        """Crear contenido placeholder para tabs pendientes."""
        from PySide6.QtWidgets import QLabel, QGroupBox
        
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        layout = QVBoxLayout(group)
        
        info_label = QLabel(f"""
        {description}
        
        🚧 EN DESARROLLO
        
        Esta funcionalidad está siendo desarrollada como parte del 
        desacoplamiento de la arquitectura monolítica.
        
        📐 Principios aplicados:
        • SRP: Responsabilidad única por widget
        • Modular: Cada tab es un componente independiente
        • Extensible: Fácil agregar nuevas tabs
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            background-color: rgba(25, 118, 210, 0.08);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(25, 118, 210, 0.35);
            color: #1976d2;
            font-size: 12px;
            font-weight: bold;
            line-height: 1.4;
        """)
        
        layout.addWidget(info_label)
        return group
    
    # ==================== Getters para acceder a widgets especializados ====================
    
    def get_dashboard_widget(self) -> Optional[DashboardWidget]:
        """Obtener referencia al dashboard widget."""
        return self.dashboard_widget
    
    def get_export_widget(self) -> Optional[ExportWidget]:
        """Obtener referencia al export widget."""
        return self.export_widget
    
    def get_query_widget(self) -> Optional[QueryWidget]:
        """Obtener referencia al query widget."""
        return self.query_widget
    
    def get_siigo_api_widget(self) -> Optional[SiigoApiWidget]:
        """Obtener referencia al siigo api widget."""
        return self.siigo_api_widget