"""
Dashboard Widget - Componente UI refactorizado para KPIs y dashboard
Implementación modular siguiendo principios SOLID

Responsabilidad única: Coordinación de componentes del dashboard
Componentes modulares: ChartFactory, KPIWidget, TooltipManager
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QFrame, QSizePolicy, QMessageBox, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QTabWidget, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

# Importar componentes modulares del dashboard
from .charts.chart_factory import ChartFactory
from .kpi_widget import KPIWidget
from .tooltip_manager import TooltipManager

# Importar módulo de visualizaciones
try:
    from dataconta.reports.charts import generate_all_charts
    CHARTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Módulo de gráficas no disponible: {e}")
    CHARTS_AVAILABLE = False


class DashboardWidget(QWidget):
    """
    Widget especializado para el dashboard de KPIs refactorizado.
    
    Principios SOLID aplicados:
    - SRP: Coordina componentes del dashboard
    - OCP: Extensible mediante componentes modulares
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para dashboard
    - DIP: Usa abstracciones (ChartFactory, KPIWidget, TooltipManager)
    """
    
    # Signals para comunicación con el controlador (inversión de dependencias)
    refresh_kpis_requested = Signal()
    show_top_clients_requested = Signal()
    pro_upgrade_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Inicializar componentes modulares
        self.chart_factory = ChartFactory()
        self.kpi_widget = KPIWidget(self)
        
        # Widgets del dashboard
        self.kpi_widgets: Dict[str, QLabel] = {}
        self.kpi_layout: Optional[QGridLayout] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz del dashboard con tabs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear QTabWidget principal
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background: #e9ecef;
                padding: 12px 24px;
                margin-right: 2px;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                font-size: 11px;
                font-weight: bold;
                color: #495057;
            }
            QTabBar::tab:selected {
                background: #007bff;
                color: white;
                border-color: #007bff;
            }
            QTabBar::tab:hover:!selected {
                background: #f8f9fa;
                border-color: #007bff;
            }
        """)
        
        layout.addWidget(self.tab_widget)
        
        # Crear las dos pestañas principales
        self.create_basic_kpis_tab()
        self.create_analytics_tab()
    
    def create_basic_kpis_tab(self):
        """Crear la primera tab con KPIs básicos usando componentes modulares."""
        basic_tab = QWidget()
        layout = QVBoxLayout(basic_tab)
        
        # KPI Widget modular (reemplaza create_kpis_section)
        layout.addWidget(self._wrap_in_card(self.kpi_widget))

        # Botones de acción (en card)
        actions = self.create_action_buttons()
        layout.addWidget(self._wrap_in_card(actions))

        # Información de upgrade (en card)
        upgrade = self.create_upgrade_section()
        layout.addWidget(self._wrap_in_card(upgrade))
        
        # Aplicar tooltip educativo a la pestaña
        tab_index = self.tab_widget.addTab(basic_tab, "📊 KPIs Básicos")
        TooltipManager.apply_tab_tooltips(self.tab_widget, tab_index, 'dashboard')
    
    def create_analytics_tab(self):
        """Crear la segunda tab con gráficos analíticos usando ChartFactory."""
        analytics_tab = QWidget()
        layout = QVBoxLayout(analytics_tab)
        
        # Scroll area para gráficos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget contenedor de gráficos
        charts_widget = QWidget()
        charts_layout = QGridLayout(charts_widget)
        charts_layout.setSpacing(15)
        charts_layout.setContentsMargins(10, 10, 10, 10)
        
        # Crear los 6 gráficos usando ChartFactory modular
        self.create_modular_chart_widgets(charts_layout)
        
        scroll_area.setWidget(charts_widget)
        layout.addWidget(scroll_area)
        
        # Aplicar tooltip educativo a la pestaña
        tab_index = self.tab_widget.addTab(analytics_tab, "📈 Analytics")
        TooltipManager.apply_tab_tooltips(self.tab_widget, tab_index, 'analytics')
    
    def create_modular_chart_widgets(self, layout: QGridLayout):
        """
        Crear los 6 widgets de gráficos usando ChartFactory modular.
        
        Refactorización SOLID:
        - SRP: ChartFactory se encarga solo de crear gráficos
        - DIP: Usa abstracciones (métodos de factory)
        """
        # Obtener definiciones de gráficos de ChartFactory
        chart_definitions = self.chart_factory.get_chart_definitions()
        
        for title, create_method, row, col in chart_definitions:
            # Crear gráfico usando ChartFactory
            chart_canvas = create_method()
            
            if chart_canvas:
                # Crear wrapper con título
                chart_widget = self.create_chart_wrapper(title, chart_canvas)
                layout.addWidget(chart_widget, row, col)
                
                # Aplicar tooltip educativo basado en el tipo de gráfico
                chart_type = self._get_chart_type_from_title(title)
                TooltipManager.apply_chart_tooltips(chart_canvas, chart_type)
            else:
                # Widget de placeholder si no hay datos
                placeholder = self.create_chart_placeholder(title)
                layout.addWidget(placeholder, row, col)
    
    def _get_chart_type_from_title(self, title: str) -> str:
        """Mapear título de gráfico a tipo para tooltips."""
        title_to_type = {
            "📊 Ventas vs Facturas": "sales_invoices",
            "👥 Top 10 Clientes": "top_clients",
            "🥧 Concentración de Ventas": "sales_distribution",
            "🎯 Mayor Ticket Promedio": "avg_ticket",
            "💹 Ventas vs Facturas (Bubble)": "bubble_chart",
            "📈 Pareto de Clientes": "pareto"
        }
        return title_to_type.get(title, "sales_invoices")
    
    def create_chart_wrapper(self, title: str, canvas) -> QWidget:
        """
        Crear wrapper para gráfico con título.
        
        Args:
            title: Título del gráfico
            canvas: Canvas de matplotlib
            
        Returns:
            QWidget: Widget contenedor del gráfico
        """
        wrapper = QFrame()
        wrapper.setFrameStyle(QFrame.Shape.StyledPanel)
        wrapper.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Título del gráfico
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1976d2; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Canvas del gráfico
        layout.addWidget(canvas)
        
        return wrapper
    
    def create_chart_placeholder(self, title: str) -> QWidget:
        """
        Crear placeholder cuando no hay datos para el gráfico.
        
        Args:
            title: Título del gráfico
            
        Returns:
            QWidget: Widget placeholder
        """
        placeholder = QFrame()
        placeholder.setFrameStyle(QFrame.Shape.StyledPanel)
        placeholder.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #6c757d;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Mensaje de no datos
        no_data_label = QLabel("📊\n\nDatos no disponibles\nGenerar KPIs para mostrar gráfico")
        no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_data_label.setStyleSheet("color: #6c757d; font-size: 12px; line-height: 1.5;")
        layout.addWidget(no_data_label)
        
        layout.addStretch()
        
        return placeholder
    
    def create_action_buttons(self):
        """Crear sección de botones de acción."""
        actions_widget = QWidget()
        layout = QHBoxLayout(actions_widget)
        layout.setSpacing(15)
        
        # Botón para generar KPIs
        generate_button = QPushButton("🔄 Actualizar KPIs")
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        generate_button.clicked.connect(self.refresh_kpis_requested.emit)
        layout.addWidget(generate_button)
        
        # Botón para ver top clientes
        top_clients_button = QPushButton("👥 Ver Top Clientes")
        top_clients_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        top_clients_button.clicked.connect(self.show_top_clients_requested.emit)
        layout.addWidget(top_clients_button)
        
        layout.addStretch()
        
        return actions_widget
    
    def create_upgrade_section(self):
        """Crear sección de upgrade a PRO."""
        upgrade_widget = QWidget()
        layout = QVBoxLayout(upgrade_widget)
        
        # Título
        title_label = QLabel("🚀 Dataconta PRO")
        title_font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #fd7e14; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel("Desbloquea funcionalidades avanzadas:")
        desc_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Features list
        features = QLabel("• Reportes personalizados\n• Exportación avanzada\n• Análisis predictivos")
        features.setStyleSheet("color: #495057; font-size: 11px; margin: 10px;")
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features)
        
        # Botón upgrade
        upgrade_button = QPushButton("💎 Actualizar a PRO")
        upgrade_button.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8620f;
            }
        """)
        upgrade_button.clicked.connect(self.pro_upgrade_requested.emit)
        layout.addWidget(upgrade_button)
        
        return upgrade_widget
    
    def _wrap_in_card(self, widget: QWidget) -> QFrame:
        """Envolver widget en una tarjeta con estilo."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 12px;
                padding: 15px;
                margin: 8px;
            }
        """)
        
        # Añadir sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(widget)
        
        return card
    
    def update_kpis(self, kpi_data: Dict[str, Any], show_message: bool = True):
        """
        Actualizar KPIs usando el KPIWidget modular.
        
        Args:
            kpi_data: Diccionario con datos de KPIs del controlador
            show_message: Si mostrar mensaje de confirmación
        """
        try:
            print("🔥 ===== DASHBOARD update_kpis REFACTORIZADO =====")
            print(f"📊 Datos KPI recibidos: {kpi_data is not None}")
            print(f"📊 Mostrar mensaje: {show_message}")
            
            # Actualizar KPIWidget modular
            if hasattr(self, 'kpi_widget') and self.kpi_widget:
                self.kpi_widget.update_kpis()
                print("✅ KPIWidget actualizado exitosamente")
            
            # Mostrar mensaje de éxito si se requiere
            if show_message and kpi_data:
                now = datetime.now()
                success_message = f"✅ KPIs actualizados exitosamente\n⏰ {now.strftime('%Y-%m-%d %H:%M:%S')}"
                self.show_success_message(success_message)
                
        except Exception as e:
            print(f"❌ Error actualizando KPIs: {e}")
            self.show_error_message(f"Error actualizando KPIs: {str(e)}")
    
    def show_success_message(self, message: str):
        """Mostrar mensaje de éxito."""
        QMessageBox.information(self, "Éxito", message)
    
    def show_error_message(self, message: str):
        """Mostrar mensaje de error."""
        QMessageBox.critical(self, "Error", message)
    
    def show_kpis_loading_message(self):
        """Mostrar mensaje de carga de KPIs."""
        QMessageBox.information(
            self,
            "Generando KPIs",
            "⏳ Generando KPIs...\n\n"
            "Este proceso puede tomar unos minutos dependiendo\n"
            "de la cantidad de facturas a procesar.\n\n"
            "Por favor espere..."
        )
    
    def resizeEvent(self, event):
        """Manejar redimensionamiento del widget."""
        super().resizeEvent(event)
        
        # Ajustar tamaño de gráficos si es necesario
        if hasattr(self, 'chart_factory'):
            # Los gráficos se redimensionan automáticamente con matplotlib
            pass
    
    def show_top_clients_detail(self):
        """Mostrar detalle de top clientes (método legacy simplificado)."""
        try:
            # Implementación simplificada usando el componente modular
            print("📊 Mostrando detalle de top clientes...")
            self.show_top_clients_requested.emit()
            
        except Exception as e:
            print(f"❌ Error mostrando top clientes: {e}")
            self.show_error_message(f"Error mostrando top clientes: {str(e)}")