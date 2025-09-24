"""
Dashboard Widget - Componente UI refactorizado para KPIs y dashboard
Implementación modular siguiendo principios SOLID

Responsabilidad única: Coordinación de componentes del dashboard
Componentes modulares: ChartFactory, KPIWidget, TooltipManager
"""

import os
import glob
import json
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
        
        # Cargar KPIs automáticamente si existen datos JSON
        self.load_initial_kpis()
    
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
        """Crear la primera tab con KPIs básicos usando componentes modulares y visualización de tarjetas."""
        basic_tab = QWidget()
        layout = QVBoxLayout(basic_tab)

        # KPIs Section usando el KPIWidget modular (muestra todos los KPIs definidos)
        layout.addWidget(self.kpi_widget)

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
    
    def create_kpis_section(self) -> QWidget:
        """Crear sección de KPIs replicando exactamente el diseño del archivo backup."""
        kpi_group = QGroupBox("📊 KPIs Básicos - Versión FREE")
        kpi_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        self.kpi_layout = QGridLayout(kpi_group)
        # Espaciados para acomodar 3 por fila (como en FREE GUI) - más margen superior para separar del título
        self.kpi_layout.setContentsMargins(8, 20, 8, 8)
        self.kpi_layout.setHorizontalSpacing(12)
        self.kpi_layout.setVerticalSpacing(12)
        
        # KPIs con datos por defecto y colores exactos del archivo backup
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
        
        # Crear widgets para cada KPI con el diseño exacto del backup
        for i, (label, value, color) in enumerate(kpis):
            kpi_frame = QFrame()
            kpi_frame.setFrameStyle(QFrame.Box)
            kpi_frame.setMinimumWidth(200)
            kpi_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            # Override ALL colors to white background, black text
            kpi_frame.setStyleSheet("""
                QFrame {
                    background-color: white !important;
                    border-radius: 8px;
                    padding: 8px;
                    border: 1px solid #bbb;
                }
            """)

            kpi_layout_inner = QVBoxLayout(kpi_frame)
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: black !important; font-size: 10px; font-weight: bold; background: transparent !important;")
            label_widget.setWordWrap(True)
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: black !important; font-size: 13px; font-weight: bold; background: transparent !important;")
            value_widget.setWordWrap(True)
            # Guardar referencia al widget de valor para actualizarlo después (usando nombres del backup)
            self.kpi_widgets[kpi_names[i]] = value_widget
            kpi_layout_inner.addWidget(label_widget)
            kpi_layout_inner.addWidget(value_widget)
            # Distribuir KPIs en múltiples filas para mejor responsive (3 por fila como backup)
            row = i // 3  # Máximo 3 KPIs por fila
            col = i % 3
            self.kpi_layout.addWidget(kpi_frame, row, col)
        
        return kpi_group
    
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
    
    def create_action_buttons(self) -> QWidget:
        """Crear botones de acción replicando el diseño exacto del archivo backup."""
        container = QWidget()
        buttons_layout = QVBoxLayout(container)
        
        # Botón actualizar KPIs con texto y estilo exactos del backup
        update_btn = QPushButton("🔄 Actualizar KPIs con Datos Reales")
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        update_btn.clicked.connect(self.refresh_kpis_requested.emit)
        buttons_layout.addWidget(update_btn)
        
        # Botón TOP clientes con diseño exacto de FREE GUI y mismo ancho que el botón de arriba
        clients_btn = QPushButton("👑 Ver TOP 10 Clientes Detallado")
        clients_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
        """)
        clients_btn.clicked.connect(self.show_top_clients_detail)
        buttons_layout.addWidget(clients_btn)
        
        # Botón para generar visualizaciones KPI (solo si están disponibles)
        if CHARTS_AVAILABLE:
            charts_btn = QPushButton("📊 Generar Visualizaciones KPI")
            charts_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9c27b0;
                    color: white;
                    border: none;
                    padding: 15px 25px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #7b1fa2;
                }
                QPushButton:pressed {
                    background-color: #6a1b9a;
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
            import glob
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
            📄 Total facturas: {num_facturas:,}
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
            cliente_principal = cliente_top1.get('nombre_display', 'N/A') if cliente_top1 else 'N/A'
            print(f"🏆 Mostrado TOP {len(top_10)} clientes REALES - Cliente #1: {cliente_principal}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error mostrando top clientes desde JSON:\n{str(e)}")
            print(f"❌ Error en show_top_clients_detail con datos JSON: {e}")
            import traceback
            traceback.print_exc()

    def update_kpis(self, kpi_data: Dict[str, Any] = None, show_message: bool = True):
        """
        Actualizar KPIs delegando a KPIWidget modular.
        Args:
            kpi_data: Diccionario con datos de KPIs del controlador (opcional)
            show_message: Si mostrar mensaje de confirmación
        """
        try:
            print("🔥 ===== DASHBOARD update_kpis DELEGADO A KPIWidget =====")
            print(f"📊 Datos KPI recibidos: {kpi_data is not None}")
            print(f"📊 Mostrar mensaje: {show_message}")

            # Si no se pasan datos, intentar cargar desde JSON
            if not kpi_data:
                kpi_files = glob.glob("outputs/kpis/kpis_siigo_*.json")
                if kpi_files:
                    latest_file = max(kpi_files, key=os.path.getmtime)
                    try:
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            kpi_data = json.load(f)
                        print(f"📂 Datos cargados desde: {latest_file}")
                    except Exception as e:
                        print(f"⚠️ Error cargando datos JSON: {e}")

            # Delegar actualización a KPIWidget modular
            if kpi_data:
                # Si el JSON tiene 'kpis', extraer solo ese diccionario
                if isinstance(kpi_data, dict) and 'kpis' in kpi_data:
                    kpi_data = kpi_data['kpis']
                self.kpi_widget.update_kpis(kpi_data)
                # Forzar actualización visual del widget y sus hijos
                self.kpi_widget.repaint()
                self.kpi_widget.update()
                for child in self.kpi_widget.findChildren(QWidget):
                    child.repaint()
                    child.update()
                print("🎨 KPIs actualizados en KPIWidget modular.")
            else:
                print("⚠️ No hay datos de KPI para actualizar en KPIWidget.")

            # Mostrar mensaje de éxito si se requiere
            if show_message and kpi_data:
                now = datetime.now()
                success_message = f"✅ KPIs actualizados exitosamente\n⏰ {now.strftime('%Y-%m-%d %H:%M:%S')}"
                ventas = kpi_data.get('ventas_totales', 0)
                facturas = kpi_data.get('numero_facturas', kpi_data.get('num_facturas', 0))
                ticket = kpi_data.get('ticket_promedio', 0)
                if ventas:
                    success_message += f"\n💰 Ventas Totales: ${ventas:,.0f}"
                if facturas:
                    success_message += f"\n📄 Total Facturas: {facturas:,}"
                if ticket:
                    success_message += f"\n🎯 Ticket Promedio: ${ticket:,.0f}"
                print(success_message)
        except Exception as e:
            print(f"❌ Error actualizando KPIs: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Error actualizando KPIs: {str(e)}")
    
    def load_initial_kpis(self):
        """Cargar KPIs iniciales desde el archivo JSON más reciente si existe."""
        try:
            kpi_files = glob.glob("outputs/kpis/kpis_siigo_*.json")
            if kpi_files:
                print("🔄 Cargando KPIs iniciales...")
                self.update_kpis(None, show_message=False)  # Cargar desde JSON sin mostrar mensaje
        except Exception as e:
            print(f"⚠️ No se pudieron cargar KPIs iniciales: {e}")
    
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