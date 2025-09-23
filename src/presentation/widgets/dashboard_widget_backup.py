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
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #1976d2;
                font-weight: bold;
                font-size: 11px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 3px solid #1976d2;
                color: #1976d2;
            }
            QTabBar::tab:hover {
                background: #dee2e6;
                color: #0d47a1;
            }
        """)
        
        # Tab 1: KPIs básicos (contenido existente)
        self.create_basic_kpis_tab()
        
        # Tab 2: Gráficos analíticos
        self.create_analytics_tab()
        
        layout.addWidget(self.tab_widget)
    
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
        """Crear la segunda tab con gráficos analíticos."""
        analytics_tab = QWidget()
        layout = QVBoxLayout(analytics_tab)
        
        # Scroll area para gráficos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setToolTip(
            "📊 Panel de Analytics Avanzado\n\n"
            "• 6 gráficos analíticos basados en datos reales\n"
            "• Actualización automática con KPIs\n"
            "• Desplázate para ver todos los gráficos\n\n"
            "💡 Tip: Usa la rueda del mouse o las barras de desplazamiento"
        )
        scroll_area.setToolTip(
            "📊 Panel de Analytics Avanzado\n\n"
            "• 6 gráficos analíticos basados en datos reales\n"
            "• Actualización automática con KPIs\n"
            "• Desplázate para ver todos los gráficos\n\n"
            "💡 Tip: Usa la rueda del mouse o las barras de desplazamiento"
        )
        
        # Widget contenedor de gráficos
        charts_widget = QWidget()
        charts_layout = QGridLayout(charts_widget)
        charts_layout.setSpacing(15)
        charts_layout.setContentsMargins(10, 10, 10, 10)
        
        if MATPLOTLIB_AVAILABLE:
            # Crear los 6 gráficos en layout 2x3
            self.create_chart_widgets(charts_layout)
        else:
            # Mensaje si matplotlib no está disponible
            no_charts_label = QLabel("""
            ⚠️ Gráficos no disponibles
            
            Para ver los gráficos analíticos, instale matplotlib:
            pip install matplotlib
            """)
            no_charts_label.setAlignment(Qt.AlignCenter)
            no_charts_label.setStyleSheet("""
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 20px;
                color: #856404;
                font-size: 14px;
            """)
            charts_layout.addWidget(no_charts_label, 0, 0, 1, 2)
        
        scroll_area.setWidget(charts_widget)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(analytics_tab, "� Analytics")
    
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
        # Definición de gráficos (título, función de creación, posición)
        chart_definitions = [
            ("📊 Ventas vs Facturas", self._create_sales_invoices_chart, 0, 0),
            ("👥 Top 10 Clientes", self._create_top_clients_chart, 0, 1),
            ("🥧 Concentración de Ventas", self._create_sales_distribution_chart, 1, 0),
            ("🎯 Mayor Ticket Promedio", self._create_avg_ticket_chart, 1, 1),
            ("💹 Ventas vs Facturas (Bubble)", self._create_bubble_chart, 2, 0),
            ("📈 Pareto de Clientes", self._create_pareto_chart, 2, 1)
        ]
        
        for title, chart_func, row, col in chart_definitions:
            chart_widget = self._create_chart_container(title, chart_func)
            layout.addWidget(chart_widget, row, col)
    
    def _create_chart_container(self, title: str, chart_func) -> QWidget:
        """
        Crear contenedor para un gráfico.
        
        Principios SOLID:
        - SRP: Solo crear el contenedor visual
        - OCP: Extensible para nuevos tipos de gráficos
        """
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        container.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título del gráfico
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #495057;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Agregar tooltip específico según el tipo de gráfico
        chart_tooltips = {
            "📊 Ventas vs Facturas": "Haz clic y mantén presionado para ver detalles del gráfico",
            "👥 Top 10 Clientes": "Identifica tus clientes más importantes por volumen de ventas",
            "🥧 Concentración de Ventas": "Analiza qué tan concentrado está tu negocio",
            "🎯 Mayor Ticket Promedio": "Descubre clientes con mayor valor por transacción",
            "💹 Ventas vs Facturas (Bubble)": "Análisis multidimensional: ventas, facturas y ticket promedio",
            "📈 Pareto de Clientes": "Aplica la regla 80/20 para optimizar tu estrategia comercial"
        }
        
        if title in chart_tooltips:
            title_label.setToolTip(chart_tooltips[title])
        
        layout.addWidget(title_label)
        
        # Crear el gráfico
        try:
            chart_widget = chart_func()
            if chart_widget:
                layout.addWidget(chart_widget)
            else:
                # Placeholder si no hay datos
                placeholder = QLabel("📊 Datos no disponibles\\nGenere KPIs primero")
                placeholder.setAlignment(Qt.AlignCenter)
                placeholder.setStyleSheet("color: #6c757d; font-style: italic;")
                layout.addWidget(placeholder)
        except Exception as e:
            # Error placeholder
            error_label = QLabel(f"❌ Error: {str(e)[:50]}...")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #dc3545; font-style: italic;")
            layout.addWidget(error_label)
        
        return container
    def create_kpis_section(self) -> QWidget:
        """Crear sección de KPIs replicando exactamente el diseño de dataconta_free_gui.py."""
        kpi_group = QGroupBox("📊 KPIs Básicos - Versión FREE")
        kpi_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        self.kpi_layout = QGridLayout(kpi_group)
        # Espaciados para acomodar 3 por fila (como en FREE GUI) - más margen superior para separar del título
        self.kpi_layout.setContentsMargins(8, 20, 8, 8)
        self.kpi_layout.setHorizontalSpacing(12)
        self.kpi_layout.setVerticalSpacing(12)
        
        # KPIs con datos por defecto y colores exactos de dataconta_free_gui.py
        kpi_data = {
            "ventas_totales": 0,
            "num_facturas": 0,
            "ticket_promedio": 0,
            "top_cliente": "Calculando...",
            "ultima_sync": "Ahora"
        }
        
        kpi_names = ["ventas_totales", "num_facturas", "ticket_promedio", "top_cliente", "ultima_sync"]
        kpis = [
            ("💰 Ventas Totales", f"${kpi_data.get('ventas_totales', 0):,.0f}", "#4caf50"),
            ("📄 Facturas Año", f"{kpi_data.get('num_facturas', 0):,}", "#2196f3"),
            ("🎯 Ticket Promedio", f"${kpi_data.get('ticket_promedio', 0):,.0f}", "#ff5722"),
            ("👑 Top Cliente", f"{kpi_data.get('top_cliente', 'Calculando...')[:25]}", "#ff9800"),
            ("🔄 Última Actualización", f"{kpi_data.get('ultima_sync', 'Ahora')}", "#9c27b0")
        ]
        
        # Crear widgets para cada KPI con el diseño exacto de FREE GUI
        for i, (label, value, color) in enumerate(kpis):
            kpi_frame = QFrame()
            kpi_frame.setFrameStyle(QFrame.Box)
            kpi_frame.setMinimumWidth(200)
            kpi_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            kpi_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 8px;
                }}
            """)
            
            kpi_layout_inner = QVBoxLayout(kpi_frame)
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
            label_widget.setWordWrap(True)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
            value_widget.setWordWrap(True)
            
            # Guardar referencia al widget de valor para actualizarlo después (usando nombres de FREE GUI)
            self.kpi_widgets[kpi_names[i]] = value_widget
            
            kpi_layout_inner.addWidget(label_widget)
            kpi_layout_inner.addWidget(value_widget)
            
            # Distribuir KPIs en múltiples filas para mejor responsive (3 por fila como FREE GUI)
            row = i // 3  # Máximo 3 KPIs por fila
            col = i % 3
            self.kpi_layout.addWidget(kpi_frame, row, col)
        
        return kpi_group
    
    def _get_kpi_columns(self) -> int:
        """Definir 3 columnas para mostrar 3 KPIs por fila (estilo FREE exacto)."""
        return 3
    
    def create_action_buttons(self) -> QWidget:
        """Crear botones de acción replicando el diseño exacto de dataconta_free_gui.py."""
        container = QWidget()
        buttons_layout = QVBoxLayout(container)
        
        # Botón actualizar KPIs con texto y estilo exactos de FREE GUI
        update_btn = QPushButton("🔄 Actualizar KPIs con Datos Reales")
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin: 10px 0px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        # Agregar logging al botón
        def on_kpis_button_click():
            print("🔴 BOTÓN KPIs PRESIONADO - emitiendo señal refresh_kpis_requested")
            self.refresh_kpis_requested.emit()
            print("📡 Señal refresh_kpis_requested emitida")
        
        update_btn.clicked.connect(on_kpis_button_click)
        
        # Botón TOP clientes con diseño exacto de FREE GUI
        top_clients_btn = QPushButton("👑 Ver TOP 10 Clientes Detallado")
        top_clients_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        top_clients_btn.clicked.connect(self.show_top_clients_detail)
        
        # Botón para generar visualizaciones KPI (solo si están disponibles)
        if CHARTS_AVAILABLE:
            charts_btn = QPushButton("📊 Generar Visualizaciones KPI")
            charts_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9c27b0;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 5px 0px;
                }
                QPushButton:hover {
                    background-color: #7b1fa2;
                }
            """)
            charts_btn.setToolTip(
                "📊 Generar gráficas automáticas de KPIs:\n\n"
                "• 📈 Evolución de ventas mensual\n"
                "• 👑 TOP 10 clientes consolidados\n"
                "• 📦 TOP 10 productos por ventas\n"
                "• 📊 Distribución estados facturas\n"
                "• 💰 Composición ventas vs impuestos\n\n"
                "🎯 Las gráficas se guardan en outputs/charts/\n"
                "📊 Usa datos reales del JSON de KPIs"
            )
            charts_btn.clicked.connect(self.generate_kpis_visualizations)
        
        buttons_layout.addWidget(update_btn)
        buttons_layout.addWidget(top_clients_btn)
        if CHARTS_AVAILABLE:
            buttons_layout.addWidget(charts_btn)
        return container
    
    def create_upgrade_section(self) -> QWidget:
        """Crear sección de información de upgrade y devolver el contenedor."""
        upgrade_group = QGroupBox("🚀 ¿Quiere más funcionalidades?")
        upgrade_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        upgrade_layout = QVBoxLayout(upgrade_group)
        upgrade_layout.setContentsMargins(8, 20, 8, 8)  # Margen superior para separar título del contenido
        
        upgrade_info = QLabel("""
        💡 EN DATACONTA PRO OBTIENE:
        • Análisis predictivo avanzado con IA
        • Hasta 2,000 facturas procesables
        • Reportes financieros ejecutivos
        • Dashboard BI interactivo en tiempo real
        • Exportaciones a Excel con gráficos
        • Soporte prioritario 24/7
        
        🎯 Versión FREE vs PRO:
        ✅ FREE: KPIs básicos, 100 facturas, CSV simple
        🚀 PRO: KPIs avanzados, 2,000 facturas, BI completo
        """)
        upgrade_info.setWordWrap(True)
        upgrade_info.setStyleSheet("""
            background-color: #e8f5e8; 
            padding: 15px; 
            border-radius: 8px;
            border: 2px solid #4caf50;
            font-size: 12px;
        """)
        
        upgrade_btn = QPushButton("🏆 Upgrade a DataConta PRO")
        upgrade_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        upgrade_btn.clicked.connect(self.pro_upgrade_requested.emit)
        
        upgrade_layout.addWidget(upgrade_info)
        upgrade_layout.addWidget(upgrade_btn)
        return upgrade_group
    
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
                from datetime import datetime
                now = datetime.now()
                success_message = f"✅ KPIs actualizados exitosamente\n⏰ {now.strftime('%Y-%m-%d %H:%M:%S')}"
                self.show_success_message(success_message)
                
        except Exception as e:
            print(f"❌ Error actualizando KPIs: {e}")
            self.show_error_message(f"Error actualizando KPIs: {str(e)}")
    
    def show_success_message(self, message: str):
            }
            
            print(f"🎯 Mapeo KPI creado: {len(kpi_mappings)} elementos")
            print(f"🎯 Widgets disponibles: {list(self.kpi_widgets.keys())}")
            
            # Actualizar widgets existentes usando las claves exactas de FREE GUI
            widgets_actualizados = 0
            for kpi_name, kpi_value in kpi_mappings.items():
                if kpi_name in self.kpi_widgets:
                    print(f"✅ Actualizando widget {kpi_name}: {kpi_value}")
                    self.kpi_widgets[kpi_name].setText(str(kpi_value))
                    widgets_actualizados += 1
                else:
                    print(f"⚠️  Widget {kpi_name} no encontrado")
            
            print(f"📊 Total widgets actualizados: {widgets_actualizados}/{len(kpi_mappings)}")
            
            self.update()
            print("🔄 Widget actualizado visualmente")
            
            # Mostrar mensaje solo si está habilitado (no durante carga automática)
            if show_message:
                QMessageBox.information(
                    self, 
                    "KPIs Actualizados", 
                    f"✅ KPIs calculados y actualizados en dashboard!\n\n"
                    f"💰 Ventas Totales: ${kpi_data.get('ventas_totales', 0):,.0f}\n"
                    f"📄 Total Facturas: {kpi_data.get('num_facturas', 0):,}\n"
                    f"🎯 Ticket Promedio: ${kpi_data.get('ticket_promedio', 0):,.0f}\n"
                    f"👤 Top Cliente: {kpi_data.get('top_cliente', 'N/A')[:30]}\n\n"
                    f"📁 KPIs guardados en: outputs/kpis/"
                )
            else:
                print("📊 Carga automática completada - sin mensaje")
            
        except Exception as e:
            print(f"❌ Error actualizando KPIs: {e}")
            if show_message:
                QMessageBox.warning(self, "Error", f"Error actualizando KPIs: {str(e)}")
    
    def show_success_message(self, message: str):
        """Mostrar mensaje de éxito."""
        QMessageBox.information(self, "Éxito", message)
    
    def show_error_message(self, message: str):
        """Mostrar mensaje de error."""
        QMessageBox.warning(self, "Error", message)
    
    def show_kpis_loading_message(self):
        """Mostrar mensaje de carga cuando se actualiza KPIs (similar a FREE GUI)."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Actualizando KPIs")
        msg_box.setText("🚀 Calculando KPIs reales desde Siigo API...")
        msg_box.setInformativeText("Por favor espere mientras se procesan los datos.")
        msg_box.setStandardButtons(QMessageBox.NoButton)
        msg_box.show()
        return msg_box
    # ---------- Métodos de creación de gráficos ----------
    
    def _get_kpis_data(self) -> dict:
        """Obtener datos de KPIs desde el archivo JSON más reciente."""
        try:
            kpis_dir = "outputs/kpis"
            if not os.path.exists(kpis_dir):
                return {}
            
            # Buscar el archivo JSON más reciente
            json_files = glob.glob(os.path.join(kpis_dir, "*.json"))
            if not json_files:
                return {}
            
            latest_file = max(json_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando KPIs: {e}")
            return {}
    
    def _create_sales_invoices_chart(self) -> QWidget:
        """Gráfico 1: Total ventas vs número de facturas (barras)."""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        kpis = self._get_kpis_data()
        if not kpis:
            return None
        
        # Crear figura matplotlib con mejor proporción
        fig = Figure(figsize=(7, 5), facecolor='#f8f9fa')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Datos
        ventas_totales = kpis.get('ventas_totales', 0) / 1_000_000  # En millones
        num_facturas = kpis.get('numero_facturas', 0)
        
        # Crear gráfico de barras
        categories = ['Ventas\n(Millones $)', 'Facturas\n(Miles)']
        values = [ventas_totales, num_facturas / 1000]  # Facturas en miles
        colors = ['#007bff', '#28a745']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7, width=0.6)
        ax.set_title('Ventas vs Facturas', fontsize=12, fontweight='bold', pad=20, color='#1976d2')
        ax.tick_params(axis='both', colors='#1976d2', labelsize=10)
        
        # Agregar valores en las barras con mejor posicionamiento
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
                   f'{value:.1f}', ha='center', va='bottom', fontsize=10, 
                   color='#1976d2', fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        # Configurar tooltip para el canvas
        canvas.setToolTip(
            "📊 Gráfico Ventas vs Facturas\n\n"
            "• Compara el monto total de ventas con el número de facturas\n"
            "• Ventas en millones de pesos colombianos\n"
            "• Facturas mostradas en miles para mejor visualización\n\n"
            "💡 Tip: Una relación alta ventas/facturas indica tickets promedio altos"
        )
        
        return canvas
    
    def _create_top_clients_chart(self) -> QWidget:
        """Gráfico 2: Top 10 clientes por ventas (barras horizontales)."""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        kpis = self._get_kpis_data()
        ventas_clientes = kpis.get('ventas_por_cliente', [])
        
        if not ventas_clientes:
            return None
        
        # Crear figura matplotlib con mayor altura
        fig = Figure(figsize=(8, 6), facecolor='#f8f9fa')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Top 10 clientes con nombres más cortos
        top_10 = ventas_clientes[:10]
        nombres = []
        for cliente in top_10:
            nombre_completo = cliente.get('nombre_display', f"Cliente {cliente.get('nit', 'N/A')}")
            # Truncar nombres largos y agregar ...
            if len(nombre_completo) > 20:
                nombre_corto = nombre_completo[:17] + "..."
            else:
                nombre_corto = nombre_completo
            nombres.append(nombre_corto)
        
        ventas = [cliente.get('total_ventas', 0) / 1_000_000 for cliente in top_10]
        
        # Crear gráfico de barras horizontales
        bars = ax.barh(nombres, ventas, color='#007bff', alpha=0.7, height=0.7)
        ax.set_title('Top 10 Clientes', fontsize=12, fontweight='bold', pad=20, color='#1976d2')
        ax.set_xlabel('Ventas (Millones $)', fontsize=11, color='#1976d2')
        ax.tick_params(axis='both', colors='#1976d2', labelsize=10)
        
        # Agregar valores en las barras
        for bar, value in zip(bars, ventas):
            width = bar.get_width()
            ax.text(width + max(ventas) * 0.02, bar.get_y() + bar.get_height()/2.,
                   f'{value:.1f}M', ha='left', va='center', fontsize=9, 
                   color='#1976d2', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='x')
        # Mejor ajuste de layout para nombres largos
        fig.subplots_adjust(left=0.25, right=0.95, top=0.85, bottom=0.1)
        fig.tight_layout(pad=2.0)
        
        # Configurar tooltip para el canvas
        canvas.setToolTip(
            "👥 Top 10 Clientes por Ventas\n\n"
            "• Ranking de clientes ordenado por monto total de ventas\n"
            "• Valores mostrados en millones de pesos (M)\n"
            "• Nombres truncados si son muy largos (...)\n\n"
            "💡 Tip: Identifica tus clientes más valiosos para estrategias VIP"
        )
        
        return canvas
    
    def _create_sales_distribution_chart(self) -> QWidget:
        """Gráfico 3: Distribución de ventas por cliente (pie chart)."""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        kpis = self._get_kpis_data()
        ventas_clientes = kpis.get('ventas_por_cliente', [])
        
        if not ventas_clientes:
            return None
        
        # Crear figura matplotlib con mejor proporción
        fig = Figure(figsize=(8, 6), facecolor='#f8f9fa')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Top 5 + otros con nombres optimizados
        top_5 = ventas_clientes[:5]
        otros_ventas = sum(cliente.get('total_ventas', 0) for cliente in ventas_clientes[5:])
        
        labels = []
        sizes = []
        
        for cliente in top_5:
            nombre = cliente.get('nombre_display', f"Cliente {cliente.get('nit', 'N/A')}")
            # Nombres más cortos para el pie chart
            if len(nombre) > 15:
                labels.append(nombre[:12] + "...")
            else:
                labels.append(nombre)
            sizes.append(cliente.get('total_ventas', 0))
        
        if otros_ventas > 0:
            labels.append('Otros')
            sizes.append(otros_ventas)
        
        # Crear pie chart con mejor configuración
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                         colors=colors, startangle=90, 
                                         textprops={'fontsize': 9},
                                         pctdistance=0.85)
        
        ax.set_title('Concentración de Ventas por Cliente', fontsize=12, fontweight='bold', 
                    pad=20, color='#1976d2')
        
        # Mejorar legibilidad de textos
        for text in texts:
            text.set_color('#1976d2')
            text.set_fontsize(9)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
            autotext.set_weight('bold')
        
        fig.tight_layout()
        
        # Configurar tooltip para el canvas
        canvas.setToolTip(
            "🥧 Concentración de Ventas por Cliente\n\n"
            "• Muestra el Top 5 de clientes + categoría 'Otros'\n"
            "• Porcentajes calculados sobre ventas totales\n"
            "• Ayuda a identificar la concentración del negocio\n\n"
            "💡 Tip: Alta concentración indica dependencia de pocos clientes\n"
            "📈 Regla 80/20: ¿El 80% de ventas viene del 20% de clientes?"
        )
        
        return canvas
    
    def _create_avg_ticket_chart(self) -> QWidget:
        """Gráfico 4: Clientes con mayor ticket promedio."""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        kpis = self._get_kpis_data()
        ventas_clientes = kpis.get('ventas_por_cliente', [])
        
        if not ventas_clientes:
            return None
        
        # Crear figura matplotlib
        fig = Figure(figsize=(6, 4), facecolor='#f8f9fa')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Top 10 por ticket promedio
        clientes_con_ticket = []
        for cliente in ventas_clientes:
            ticket = cliente.get('ticket_promedio', 0)
            if ticket > 0:
                clientes_con_ticket.append(cliente)
        
        # Ordenar por ticket promedio
        clientes_con_ticket.sort(key=lambda x: x.get('ticket_promedio', 0), reverse=True)
        top_10_ticket = clientes_con_ticket[:10]
        
        if not top_10_ticket:
            return None
        
        nombres = [cliente.get('nombre_display', f"Cliente {cliente.get('nit', 'N/A')}")[:15] 
                  for cliente in top_10_ticket]
        tickets = [cliente.get('ticket_promedio', 0) / 1_000_000 for cliente in top_10_ticket]
        
        # Crear figura matplotlib con mejor altura
        fig = Figure(figsize=(9, 6), facecolor='#f8f9fa')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Top 10 por ticket promedio con nombres optimizados
        clientes_con_ticket = []
        for cliente in ventas_clientes:
            ticket = cliente.get('ticket_promedio', 0)
            if ticket > 0:
                clientes_con_ticket.append(cliente)
        
        # Ordenar por ticket promedio
        clientes_con_ticket.sort(key=lambda x: x.get('ticket_promedio', 0), reverse=True)
        top_10_ticket = clientes_con_ticket[:8]  # Reducir a 8 para mejor visualización
        
        if not top_10_ticket:
            return None
        
        # Nombres más cortos y optimizados
        nombres = []
        for cliente in top_10_ticket:
            nombre_completo = cliente.get('nombre_display', f"Cliente {cliente.get('nit', 'N/A')}")
            if len(nombre_completo) > 12:
                nombres.append(nombre_completo[:9] + "...")
            else:
                nombres.append(nombre_completo)
        
        tickets = [cliente.get('ticket_promedio', 0) / 1_000_000 for cliente in top_10_ticket]
        
        # Crear gráfico de barras con mejor espaciado
        x_pos = range(len(nombres))
        bars = ax.bar(x_pos, tickets, color='#28a745', alpha=0.7, width=0.7)
        ax.set_title('Top Clientes - Mayor Ticket Promedio', fontsize=12, fontweight='bold', 
                    pad=20, color='#1976d2')
        ax.set_ylabel('Ticket Promedio (Millones $)', fontsize=11, color='#1976d2')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9, color='#1976d2')
        ax.tick_params(axis='both', colors='#1976d2')
        
        # Agregar valores en las barras
        for bar, value in zip(bars, tickets):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(tickets) * 0.02,
                   f'{value:.1f}M', ha='center', va='bottom', fontsize=9, 
                   color='#1976d2', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='y')
        # Mejor ajuste de layout para evitar amontonamiento de texto
        fig.subplots_adjust(left=0.15, right=0.95, top=0.85, bottom=0.25)
        fig.tight_layout(pad=2.0)
        
        # Configurar tooltip para el canvas
        canvas.setToolTip(
            "🎯 Clientes con Mayor Ticket Promedio\n\n"
            "• Top 8 clientes ordenados por ticket promedio más alto\n"
            "• Ticket promedio = Ventas totales ÷ Número de facturas\n"
            "• Valores en millones de pesos (M)\n\n"
            "💡 Tip: Clientes con ticket alto son ideales para productos premium\n"
            "📊 Identifica patrones de compra de alto valor"
        )

        return canvas
    
    def _create_bubble_chart(self) -> QWidget:
        """Gráfico 5: Scatter plot - Ventas vs Facturas (bubble chart)."""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        kpis = self._get_kpis_data()
        ventas_clientes = kpis.get('ventas_por_cliente', [])
        
        if not ventas_clientes:
            return None
        
        # Crear figura matplotlib con mejor proporción
        fig = Figure(figsize=(8, 6), facecolor='#f8f9fa')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Preparar datos para top 15 (reducido para mejor visualización)
        top_15 = ventas_clientes[:15]
        
        x = [cliente.get('numero_facturas', 1) for cliente in top_15]  # Número de facturas
        y = [cliente.get('total_ventas', 0) / 1_000_000 for cliente in top_15]  # Ventas en millones
        sizes = [max(50, min(300, cliente.get('ticket_promedio', 0) / 50_000)) for cliente in top_15]  # Tamaño controlado
        
        # Crear scatter plot con mejor configuración
        scatter = ax.scatter(x, y, s=sizes, alpha=0.7, c=range(len(x)), cmap='viridis', edgecolors='white')
        
        ax.set_title('Ventas vs Facturas por Cliente\n(Tamaño = Ticket Promedio)', 
                    fontsize=12, fontweight='bold', pad=20, color='#1976d2')
        ax.set_xlabel('Número de Facturas', fontsize=11, color='#1976d2')
        ax.set_ylabel('Ventas (Millones $)', fontsize=11, color='#1976d2')
        ax.tick_params(axis='both', colors='#1976d2', labelsize=10)
        
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        # Configurar tooltip para el canvas
        canvas.setToolTip(
            "💹 Análisis Bubble: Ventas vs Facturas\n\n"
            "• Eje X: Número de facturas por cliente\n"
            "• Eje Y: Ventas totales en millones\n"
            "• Tamaño burbuja: Proporcional al ticket promedio\n\n"
            "💡 Interpretación:\n"
            "  - Burbuja grande = Ticket promedio alto\n"
            "  - Posición derecha = Muchas facturas\n"
            "  - Posición arriba = Altas ventas\n\n"
            "🎯 Busca: Burbujas grandes en esquina superior derecha"
        )
        
        return canvas
    
    def _create_pareto_chart(self) -> QWidget:
        """Gráfico 6: Pareto de clientes (acumulado)."""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        kpis = self._get_kpis_data()
        ventas_clientes = kpis.get('ventas_por_cliente', [])
        
        if not ventas_clientes:
            return None
        
        # Crear figura matplotlib
        fig = Figure(figsize=(6, 4), facecolor='#f8f9fa')
        canvas = FigureCanvas(fig)
        ax1 = fig.add_subplot(111)
        
        # Top 15 para pareto
        top_15 = ventas_clientes[:15]
        ventas = [cliente.get('total_ventas', 0) for cliente in top_15]
        
        # Calcular porcentaje acumulado
        total_ventas = sum(ventas)
        porcentajes = [(v / total_ventas) * 100 for v in ventas]
        acumulado = np.cumsum(porcentajes)
        
        # Crear figura matplotlib con mejor proporción
        fig = Figure(figsize=(10, 6), facecolor='#f8f9fa')
        canvas = FigureCanvas(fig)
        ax1 = fig.add_subplot(111)
        
        # Top 12 para mejor visualización
        top_12 = ventas_clientes[:12]
        ventas = [cliente.get('total_ventas', 0) for cliente in top_12]
        
        # Calcular porcentaje acumulado
        total_ventas = sum(ventas)
        porcentajes = [(v / total_ventas) * 100 for v in ventas]
        acumulado = np.cumsum(porcentajes)
        
        # Gráfico de barras con mejor espaciado
        x_pos = range(len(ventas))
        bars = ax1.bar(x_pos, porcentajes, color='#007bff', alpha=0.7, width=0.8)
        ax1.set_ylabel('% Individual de Ventas', color='#007bff', fontsize=11, fontweight='bold')
        ax1.set_xlabel('Ranking de Clientes (Top 12)', fontsize=11, color='#1976d2')
        ax1.tick_params(axis='both', colors='#1976d2', labelsize=10)
        ax1.set_title('Análisis Pareto: Concentración de Ventas por Cliente', 
                     fontsize=12, fontweight='bold', pad=20, color='#1976d2')
        
        # Línea de pareto con mejor configuración
        ax2 = ax1.twinx()
        line = ax2.plot(x_pos, acumulado, color='#dc3545', marker='o', linewidth=3, 
                       markersize=6, markerfacecolor='white', markeredgecolor='#dc3545')
        ax2.set_ylabel('% Acumulado de Ventas', color='#dc3545', fontsize=11, fontweight='bold')
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='y', colors='#dc3545', labelsize=10)
        
        # Línea del 80% con mejor estilo
        ax2.axhline(y=80, color='#28a745', linestyle='--', alpha=0.8, linewidth=2)
        ax2.text(len(x_pos)*0.7, 82, '80% Regla de Pareto', 
                color='#28a745', fontweight='bold', fontsize=9)
        
        ax1.set_title('Pareto de Clientes', fontsize=12, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3)
        # Mejor ajuste de layout para doble eje
        fig.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)
        fig.tight_layout(pad=2.0)
        
        # Configurar tooltip para el canvas
        canvas.setToolTip(
            "📈 Análisis de Pareto - Regla 80/20\n\n"
            "• Barras azules: % individual de ventas por cliente\n"
            "• Línea roja: % acumulado de ventas\n"
            "• Línea verde: Marca del 80% (Regla de Pareto)\n\n"
            "💡 Principio de Pareto:\n"
            "  - ¿El 80% de ventas viene del 20% de clientes?\n"
            "  - Identifica el punto donde se cruza el 80%\n\n"
            "📊 Usa este análisis para:\n"
            "  - Enfocar esfuerzos comerciales\n"
            "  - Diseñar programas de fidelización\n"
            "  - Priorizar atención al cliente"
        )
        
        return canvas
    
    def resizeEvent(self, event):
        """Manejar redimensionamiento para diseño responsive."""
        super().resizeEvent(event)
        # Aquí se puede agregar lógica de reorganización si es necesario

    # ---------- Helpers de UI (cards y sombras) ----------
    def _wrap_in_card(self, inner: QWidget) -> QFrame:
        """Envuelve un widget en una 'card' con esquinas redondeadas y sombra."""
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
    
    def load_existing_kpis_sync(self) -> Optional[Dict[str, Any]]:
        """Cargar KPIs existentes desde el archivo más reciente (igual que dataconta_free_gui.py)."""
        try:
            kpis_dir = "outputs/kpis"
            
            if not os.path.exists(kpis_dir):
                return None
            
            pattern = os.path.join(kpis_dir, "kpis_siigo_*.json")
            kpi_files = glob.glob(pattern)
            
            if not kpi_files:
                return None
            
            latest_file = max(kpi_files, key=os.path.getmtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # MANEJAR DIFERENTES FORMATOS DE ARCHIVO:
            if 'kpis' in raw_data and 'metadata' in raw_data:
                # Formato API real
                kpis_data = raw_data['kpis']
            elif 'ventas_totales' in raw_data:
                # Formato simple
                kpis_data = raw_data
            else:
                return None
            
            return kpis_data
            
        except Exception as e:
            print(f"❌ Error cargando KPIs: {e}")
            return None
    
    def show_top_clients_detail(self):
        """Mostrar ventana detallada con el TOP 10 de clientes usando datos REALES del JSON."""
        try:
            # Cargar KPIs más recientes desde outputs/kpis
            kpis_data = self.load_existing_kpis_sync()
            
            if not kpis_data or 'ventas_por_cliente' not in kpis_data:
                QMessageBox.warning(
                    self, 
                    "Sin Datos", 
                    "No hay datos de clientes disponibles.\n\nAsegúrese de que existan archivos JSON en outputs/kpis/\ncon la estructura 'ventas_por_cliente'"
                )
                return
            
            ventas_clientes = kpis_data['ventas_por_cliente']
            
            if not ventas_clientes:
                QMessageBox.warning(self, "Sin Datos", "No hay datos de clientes para mostrar en el JSON.")
                return
            
            # Crear ventana emergente
            dialog = QWidget()
            dialog.setWindowTitle("🏆 TOP 10 CLIENTES - Análisis Detallado (Datos Reales)")
            dialog.setGeometry(200, 200, 950, 650)
            dialog.setStyleSheet("""
                QWidget {
                    background-color: #f5f5f5;
                    font-family: Arial;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Header informativo con datos reales
            ventas_totales = kpis_data.get('ventas_totales', 0)
            num_facturas = kpis_data.get('num_facturas', 0)
            ultima_sync = kpis_data.get('ultima_sync', 'N/A')
            
            header = QLabel(f"""
            🏆 TOP 10 CLIENTES - ANÁLISIS DETALLADO (DATOS REALES SIIGO API)
            
            📊 Total de clientes únicos: {len(ventas_clientes)}
            💰 Ventas totales: ${ventas_totales:,.0f}
            � Total facturas: {num_facturas:,}
            🕒 Última actualización: {ultima_sync}
            📅 Fuente: API Siigo - {datetime.now().strftime('%Y-%m-%d')}
            """)
            header.setStyleSheet("""
                background-color: #1976d2;
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            """)
            header.setWordWrap(True)
            layout.addWidget(header)
            
            # Tabla de clientes con datos reales
            table = QTableWidget()
            top_10 = ventas_clientes[:10]  # Solo top 10
            table.setRowCount(len(top_10))
            table.setColumnCount(6)  # Agregar columna adicional
            table.setHorizontalHeaderLabels([
                "🏆 Posición", "🆔 NIT/CC", "👤 Cliente", "💰 Monto Total", "📊 % del Total", "🎯 Categoría"
            ])
            
            for i, cliente in enumerate(top_10):
                # Posición con medallas
                if i == 0:
                    pos_text = "🥇 #1"
                    pos_color = QColor("#ffd700")  # Dorado
                elif i == 1:
                    pos_text = "🥈 #2"
                    pos_color = QColor("#c0c0c0")  # Plata
                elif i == 2:
                    pos_text = "🥉 #3"
                    pos_color = QColor("#cd7f32")  # Bronce
                else:
                    pos_text = f"#{i+1}"
                    pos_color = QColor("#f0f0f0")  # Gris claro
                
                pos_item = QTableWidgetItem(pos_text)
                pos_item.setTextAlignment(Qt.AlignCenter)
                pos_item.setBackground(pos_color)
                table.setItem(i, 0, pos_item)
                
                # NIT/CC
                nit_valor = str(cliente['nit'])
                nit_item = QTableWidgetItem(nit_valor)
                nit_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, 1, nit_item)
                
                # Nombre del cliente (usar el display que viene del JSON)
                cliente_display = cliente.get('nombre_display', cliente.get('nombre', f"Cliente NIT: {cliente['nit']}"))
                nombre_item = QTableWidgetItem(cliente_display)
                table.setItem(i, 2, nombre_item)
                
                # Monto total
                monto = float(cliente['total_ventas'])
                monto_item = QTableWidgetItem(f"${monto:,.0f}")
                monto_item.setTextAlignment(Qt.AlignRight)
                table.setItem(i, 3, monto_item)
                
                # Porcentaje del total
                porcentaje = (monto / ventas_totales * 100) if ventas_totales > 0 else 0
                pct_item = QTableWidgetItem(f"{porcentaje:.1f}%")
                pct_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, 4, pct_item)
                
                # Categoría VIP según monto real
                if monto >= 19000000:  # Basado en datos reales del JSON
                    categoria = "🌟 VIP GOLD"
                    cat_color = QColor("#fff3e0")
                elif monto >= 15000000:
                    categoria = "💎 VIP PLUS"
                    cat_color = QColor("#e8f5e8")
                elif monto >= 10000000:
                    categoria = "⭐ VIP"
                    cat_color = QColor("#e3f2fd")
                else:
                    categoria = "👤 Regular"
                    cat_color = QColor("#f3e5f5")
                
                cat_item = QTableWidgetItem(categoria)
                cat_item.setTextAlignment(Qt.AlignCenter)
                cat_item.setBackground(cat_color)
                table.setItem(i, 5, cat_item)
            
            # Configurar tabla
            table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #1976d2;
                    border-radius: 8px;
                    gridline-color: #e0e0e0;
                    background-color: white;
                    alternate-background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #1976d2;
                    color: white;
                    padding: 10px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QTableWidget::item {
                    padding: 8px;
                    font-size: 11px;
                }
            """)
            table.setAlternatingRowColors(True)
            table.resizeColumnsToContents()
            layout.addWidget(table)
            
            # Footer con estadísticas reales calculadas
            cliente_top1 = top_10[0] if top_10 else None
            top3_total = sum(float(c['total_ventas']) for c in top_10[:3])
            top5_total = sum(float(c['total_ventas']) for c in top_10[:5])
            top10_total = sum(float(c['total_ventas']) for c in top_10)
            
            footer_stats = f"""
            📈 ESTADÍSTICAS REALES (desde outputs/kpis JSON):
            
            🥇 Cliente #1: {cliente_top1.get('nombre_display', cliente_top1.get('nombre', 'N/A')) if cliente_top1 else 'N/A'}
            💰 Líder con: ${float(cliente_top1['total_ventas']):,.0f} ({((float(cliente_top1['total_ventas']) / ventas_totales) * 100):.1f}% del total)
            
            📊 Concentración de ventas:
            • Top 3 clientes: ${top3_total:,.0f} ({(top3_total / ventas_totales * 100):.1f}% del total)
            • Top 5 clientes: ${top5_total:,.0f} ({(top5_total / ventas_totales * 100):.1f}% del total)
            • Top 10 clientes: ${top10_total:,.0f} ({(top10_total / ventas_totales * 100):.1f}% del total)
            
            🎯 Clientes VIP+: {sum(1 for c in top_10 if float(c['total_ventas']) >= 15000000)} de {len(top_10)} clientes
            """
            
            footer = QLabel(footer_stats)
            footer.setStyleSheet("""
                background-color: #e8f5e8;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #4caf50;
                font-size: 11px;
                font-weight: bold;
            """)
            footer.setWordWrap(True)
            layout.addWidget(footer)
            
            # Botón cerrar
            close_btn = QPushButton("✅ Cerrar Análisis")
            close_btn.clicked.connect(dialog.close)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)
            
            # Mostrar ventana
            dialog.show()
            self.top_clients_window = dialog  # Mantener referencia
            
            # Log con datos reales del JSON
            cliente_principal = cliente_top1.get('cliente_display', 'N/A') if cliente_top1 else 'N/A'
            print(f"🏆 Mostrado TOP {len(top_10)} clientes REALES - Cliente #1: {cliente_principal}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error mostrando top clientes desde JSON:\n{str(e)}")
            print(f"❌ Error en show_top_clients_detail con datos JSON: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_kpis_visualizations(self):
        """Generar visualizaciones automáticas de los KPIs usando datos del JSON."""
        try:
            if not CHARTS_AVAILABLE:
                QMessageBox.warning(
                    self, 
                    "Función No Disponible",
                    "El módulo de visualizaciones no está disponible.\n\n"
                    "Para instalar las dependencias necesarias:\n"
                    "pip install matplotlib seaborn\n\n"
                    "Luego reinicie la aplicación."
                )
                return
            
            print("📊 Iniciando generación de visualizaciones KPI...")
            
            # Buscar el archivo KPI más reciente
            kpis_dir = "outputs/kpis"
            if not os.path.exists(kpis_dir):
                QMessageBox.warning(
                    self,
                    "Sin Datos KPI", 
                    "No se encontraron datos de KPIs.\n\n"
                    "Primero actualice los KPIs presionando:\n"
                    "'🔄 Actualizar KPIs con Datos Reales'"
                )
                return
            
            # Encontrar archivo KPI más reciente
            pattern = os.path.join(kpis_dir, "kpis_siigo_*.json")
            kpi_files = glob.glob(pattern)
            
            if not kpi_files:
                QMessageBox.warning(
                    self,
                    "Sin Archivos KPI",
                    "No se encontraron archivos JSON de KPIs.\n\n" 
                    "Genere los KPIs primero con el botón:\n"
                    "'🔄 Actualizar KPIs con Datos Reales'"
                )
                return
            
            # Usar el archivo más reciente
            latest_kpi_file = max(kpi_files, key=os.path.getmtime)
            
            print(f"📊 Usando archivo KPI: {os.path.basename(latest_kpi_file)}")
            
            # Generar todas las visualizaciones usando el módulo charts
            generated_files = generate_all_charts(latest_kpi_file)
            
            if not generated_files:
                QMessageBox.warning(
                    self,
                    "Error en Visualizaciones",
                    "No se pudieron generar las visualizaciones.\n"
                    "Revise los logs para más detalles."
                )
                return
            
            # Mostrar mensaje de éxito con detalles
            charts_list = "\n".join([
                f"• {chart_type.replace('_', ' ').title()}: {os.path.basename(path)}"
                for chart_type, path in generated_files.items()
            ])
            
            print(f"✅ Se generaron {len(generated_files)} visualizaciones exitosamente")
            
            QMessageBox.information(
                self,
                "✅ Visualizaciones Generadas",
                f"Se generaron {len(generated_files)} gráficas de KPIs:\n\n"
                f"{charts_list}\n\n"
                f"📁 Ubicación: outputs/charts/\n"
                f"📊 Datos desde: {os.path.basename(latest_kpi_file)}\n\n"
                f"Las gráficas incluyen:\n"
                f"📈 Evolución de ventas mensual\n"
                f"👑 Top 10 clientes consolidados\n" 
                f"📦 Top 10 productos por ventas\n"
                f"📊 Distribución estados facturas\n"
                f"💰 Composición ventas vs impuestos"
            )
            
        except Exception as e:
            print(f"❌ Error generando visualizaciones: {str(e)}")
            QMessageBox.critical(
                self, 
                "Error de Visualización",
                f"Error al generar visualizaciones:\n\n{str(e)}\n\n"
                f"Verifique que matplotlib y seaborn estén instalados."
            )
    
    def generate_kpis_visualizations(self):
        """Generar visualizaciones automáticas de los KPIs usando datos del JSON."""
        try:
            if not CHARTS_AVAILABLE:
                QMessageBox.warning(
                    self, 
                    "Función No Disponible",
                    "El módulo de visualizaciones no está disponible.\n\n"
                    "Para instalar las dependencias necesarias:\n"
                    "pip install matplotlib seaborn\n\n"
                    "Luego reinicie la aplicación."
                )
                return
            
            print("📊 Iniciando generación de visualizaciones KPI...")
            
            # Buscar el archivo KPI más reciente
            kpis_dir = "outputs/kpis"
            if not os.path.exists(kpis_dir):
                QMessageBox.warning(
                    self,
                    "Sin Datos KPI", 
                    "No se encontraron datos de KPIs.\n\n"
                    "Primero actualice los KPIs presionando:\n"
                    "'🔄 Actualizar KPIs con Datos Reales'"
                )
                return
            
            # Encontrar archivo KPI más reciente
            pattern = os.path.join(kpis_dir, "kpis_siigo_*.json")
            kpi_files = glob.glob(pattern)
            
            if not kpi_files:
                QMessageBox.warning(
                    self,
                    "Sin Archivos KPI",
                    "No se encontraron archivos JSON de KPIs.\n\n" 
                    "Genere los KPIs primero con el botón:\n"
                    "'🔄 Actualizar KPIs con Datos Reales'"
                )
                return
            
            # Usar el archivo más reciente
            latest_kpi_file = max(kpi_files, key=os.path.getmtime)
            
            print(f"📊 Usando archivo KPI: {os.path.basename(latest_kpi_file)}")
            
            # Generar todas las visualizaciones usando el módulo charts
            generated_files = generate_all_charts(latest_kpi_file)
            
            if not generated_files:
                QMessageBox.warning(
                    self,
                    "Error en Visualizaciones",
                    "No se pudieron generar las visualizaciones.\n"
                    "Revise los logs para más detalles."
                )
                return
            
            # Mostrar mensaje de éxito con detalles
            charts_list = "\n".join([
                f"• {chart_type.replace('_', ' ').title()}: {os.path.basename(path)}"
                for chart_type, path in generated_files.items()
            ])
            
            print(f"✅ Se generaron {len(generated_files)} visualizaciones exitosamente")
            
            QMessageBox.information(
                self,
                "✅ Visualizaciones Generadas",
                f"Se generaron {len(generated_files)} gráficas de KPIs:\n\n"
                f"{charts_list}\n\n"
                f"📁 Ubicación: outputs/charts/\n"
                f"📊 Datos desde: {os.path.basename(latest_kpi_file)}\n\n"
                f"Las gráficas incluyen:\n"
                f"📈 Evolución de ventas mensual\n"
                f"👑 Top 10 clientes consolidados\n" 
                f"📦 Top 10 productos por ventas\n"
                f"📊 Distribución estados facturas\n"
                f"💰 Composición ventas vs impuestos"
            )
            
        except Exception as e:
            print(f"❌ Error generando visualizaciones: {str(e)}")
            QMessageBox.critical(
                self, 
                "Error de Visualización",
                f"Error al generar visualizaciones:\n\n{str(e)}\n\n"
                f"Verifique que matplotlib y seaborn estén instalados."
            )