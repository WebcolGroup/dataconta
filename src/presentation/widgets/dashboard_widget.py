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
                    padding: 15px;
                }}
            """)
            
            kpi_layout_inner = QVBoxLayout(kpi_frame)
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
            label_widget.setWordWrap(True)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
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
        Actualizar KPIs en la interfaz usando las mismas claves que dataconta_free_gui.py.
        Incluye actualización de "Última Actualización" como en FREE GUI.
        
        Args:
            kpi_data: Diccionario con datos de KPIs del controlador
        """
        try:
            print("🔥 ===== DASHBOARD update_kpis LLAMADO =====")
            print(f"📊 Datos KPI recibidos: {kpi_data is not None}")
            if kpi_data:
                print(f"📊 Claves KPI: {list(kpi_data.keys())}")
                print(f"📊 Ventas totales: {kpi_data.get('ventas_totales', 'No disponible')}")
            
            from datetime import datetime
            
            # Mapear datos usando las mismas claves que FREE GUI
            kpi_mappings = {
                "ventas_totales": f"${kpi_data.get('ventas_totales', 0):,.0f}",
                "num_facturas": f"{kpi_data.get('num_facturas', 0):,}",
                "ticket_promedio": f"${kpi_data.get('ticket_promedio', 0):,.0f}",
                "top_cliente": f"{kpi_data.get('top_cliente', 'Calculando...')[:25]}",
                "ultima_sync": f"Actualizado {datetime.now().strftime('%H:%M:%S')}"
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
            
            # Mostrar mensaje de éxito (como en FREE GUI)
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
            
        except Exception as e:
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