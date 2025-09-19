"""
Dashboard Widget - Componente UI especializado para KPIs y dashboard
Parte de la refactorización del monolito dataconta_free_gui_refactored.py

Responsabilidad única: UI del dashboard con KPIs, delegando toda la lógica al controlador
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QFrame, QSizePolicy, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor


class DashboardWidget(QWidget):
    """
    Widget especializado para el dashboard de KPIs.
    
    Principios SOLID:
    - SRP: Solo maneja la UI del dashboard
    - OCP: Extensible para nuevos KPIs
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para dashboard
    - DIP: Depende de abstracciones (signals)
    """
    
    # Signals para comunicación con el controlador (inversión de dependencias)
    refresh_kpis_requested = Signal()
    show_top_clients_requested = Signal()
    pro_upgrade_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.kpi_widgets: Dict[str, QLabel] = {}
        self.kpi_layout: Optional[QGridLayout] = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz del dashboard."""
        layout = QVBoxLayout(self)

        # KPIs principales (en card)
        kpis = self.create_kpis_section()
        layout.addWidget(self._wrap_in_card(kpis))

        # Botones de acción (en card)
        actions = self.create_action_buttons()
        layout.addWidget(self._wrap_in_card(actions))

        # Información de upgrade (en card)
        upgrade = self.create_upgrade_section()
        layout.addWidget(self._wrap_in_card(upgrade))
    
    def create_kpis_section(self) -> QWidget:
        """Crear sección de KPIs y devolver el contenedor."""
        kpi_group = QGroupBox("📊 KPIs Básicos - DataConta FREE")
        kpi_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        self.kpi_layout = QGridLayout(kpi_group)
        # Espaciados para acomodar 4 por fila sin verse grandes - más margen superior para separar del título
        self.kpi_layout.setContentsMargins(8, 20, 8, 8)
        self.kpi_layout.setHorizontalSpacing(12)
        self.kpi_layout.setVerticalSpacing(12)
        
        # KPIs predeterminados
        default_kpis = {
            "Total Facturas": "0",
            "Ventas del Mes": "$0",
            "Cliente Top": "Cargando...",
            "Promedio Factura": "$0",
            "Total Año": "$0",
            "Facturas Pagadas": "0",
            "Facturas Pendientes": "0",
            "Mes con Más Ventas": "Cargando...",
            "Ticket Promedio": "$0"
        }
        
        # Crear widgets para cada KPI (estilo FREE: color de fondo por KPI)
        for i, (label, value) in enumerate(default_kpis.items()):
            color = self._kpi_color(label)
            kpi_widget = self._create_kpi_widget(label, value, color)
            
            # Distribución responsive
            columns = self._get_kpi_columns()
            row = i // columns
            col = i % columns
            self.kpi_layout.addWidget(kpi_widget, row, col)
        
        return kpi_group
    
    def _create_kpi_widget(self, label: str, value: str, bg_color: Optional[str] = None) -> QFrame:
        """Crear widget individual para un KPI (estilo moderno)."""
        kpi_frame = QFrame()
        kpi_frame.setFrameStyle(QFrame.StyledPanel)
        kpi_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        color = bg_color or "#1976d2"
        kpi_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                margin: 4px;
                padding: 6px;
                min-height: 45px;
            }}
        """)
        layout = QVBoxLayout(kpi_frame)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(3)

        # Título y valor con texto blanco sobre fondo de color (estilo FREE)
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignLeft)
        label_widget.setStyleSheet("color: white; font-size: 12px; font-weight: 700;")
        label_widget.setWordWrap(True)

        value_widget = QLabel(value)
        value_widget.setAlignment(Qt.AlignLeft)
        value_widget.setStyleSheet("color: white; font-size: 16px; font-weight: 800;")
        value_widget.setWordWrap(True)

        layout.addWidget(label_widget)
        layout.addWidget(value_widget)

        # Guardar referencia para actualizaciones
        self.kpi_widgets[label] = value_widget

        # Agregar sombra ligera
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 4)
        kpi_frame.setGraphicsEffect(shadow)

        return kpi_frame

    

    
    def _get_kpi_columns(self) -> int:
        """Definir 3 columnas para mostrar 3 KPIs por fila (estilo FREE)."""
        return 3

    def _kpi_color(self, label: str) -> str:
        """Color de fondo por KPI (similar a la versión FREE)."""
        mapping = {
            "Total Año": "#4caf50",
            "Total Facturas": "#2196f3",
            "Promedio Factura": "#ff5722",
            "Ticket Promedio": "#ff5722",
            "Cliente Top": "#ff9800",
            "Ventas del Mes": "#1976d2",
            "Facturas Pagadas": "#43a047",
            "Facturas Pendientes": "#f9a825",
            "Mes con Más Ventas": "#7b1fa2",
        }
        return mapping.get(label, "#1976d2")
    
    def create_action_buttons(self) -> QWidget:
        """Crear botones de acción y devolver un contenedor."""
        container = QWidget()
        buttons_layout = QVBoxLayout(container)
        
        # Botón actualizar KPIs
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
        update_btn.clicked.connect(self.refresh_kpis_requested.emit)
        
        # Botón TOP clientes
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
        top_clients_btn.clicked.connect(self.show_top_clients_requested.emit)
        
        buttons_layout.addWidget(update_btn)
        buttons_layout.addWidget(top_clients_btn)
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
            font-size: 13px;
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
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        upgrade_btn.clicked.connect(self.pro_upgrade_requested.emit)
        
        upgrade_layout.addWidget(upgrade_info)
        upgrade_layout.addWidget(upgrade_btn)
        return upgrade_group
    
    def update_kpis(self, kpi_data: Dict[str, Any]):
        """
        Actualizar KPIs en la interfaz.
        
        Args:
            kpi_data: Diccionario con datos de KPIs del controlador
        """
        try:
            # Mapear datos a widgets
            kpi_mappings = {
                "Total Facturas": f"{kpi_data.get('num_facturas', 0):,}",
                "Ventas del Mes": f"${kpi_data.get('ventas_totales_mes', 0):,.2f}",
                "Cliente Top": kpi_data.get('top_cliente', 'N/A'),
                "Promedio Factura": f"${kpi_data.get('ticket_promedio', 0):,.2f}",
                "Total Año": f"${kpi_data.get('ventas_totales', 0):,.2f}",
                "Facturas Pagadas": f"{kpi_data.get('facturas_pagadas', 0):,}",
                "Facturas Pendientes": f"{kpi_data.get('facturas_pendientes', 0):,}",
                "Mes con Más Ventas": kpi_data.get('mejor_mes', 'N/A'),
                "Ticket Promedio": f"${kpi_data.get('ticket_promedio', 0):,.2f}"
            }
            
            # Actualizar widgets existentes
            for kpi_name, kpi_value in kpi_mappings.items():
                if kpi_name in self.kpi_widgets:
                    self.kpi_widgets[kpi_name].setText(str(kpi_value))
            
            self.update()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error actualizando KPIs: {str(e)}")
    
    def show_success_message(self, message: str):
        """Mostrar mensaje de éxito."""
        QMessageBox.information(self, "Éxito", message)
    
    def show_error_message(self, message: str):
        """Mostrar mensaje de error."""
        QMessageBox.warning(self, "Error", message)
    
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