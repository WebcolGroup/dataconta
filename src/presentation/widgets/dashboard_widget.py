"""
Dashboard Widget - Componente UI especializado para KPIs y dashboard
Parte de la refactorización del monolito dataconta_free_gui_refactored.py

Responsabilidad única: UI del dashboard con KPIs, delegando toda la lógica al controlador
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QFrame, QSizePolicy, QMessageBox, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

# Importar módulo de visualizaciones
try:
    from dataconta.reports.charts import generate_all_charts
    CHARTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Módulo de gráficas no disponible: {e}")
    CHARTS_AVAILABLE = False


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
                    padding: 8px;
                }}
            """)
            
            kpi_layout_inner = QVBoxLayout(kpi_frame)
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
            label_widget.setWordWrap(True)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
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
    
    def update_kpis(self, kpi_data: Dict[str, Any], show_message: bool = True):
        """
        Actualizar KPIs en la interfaz usando las mismas claves que dataconta_free_gui.py.
        Incluye actualización de "Última Actualización" como en FREE GUI.
        
        Args:
            kpi_data: Diccionario con datos de KPIs del controlador
            show_message: Si mostrar mensaje de confirmación (False para carga automática)
        """
        try:
            print("🔥 ===== DASHBOARD update_kpis LLAMADO =====")
            print(f"📊 Datos KPI recibidos: {kpi_data is not None}")
            print(f"📊 Mostrar mensaje: {show_message}")
            if kpi_data:
                print(f"📊 Claves KPI: {list(kpi_data.keys())}")
                print(f"📊 Ventas totales: {kpi_data.get('ventas_totales', 'No disponible')}")
            
            from datetime import datetime
            
            # Determinar texto de última actualización según el contexto
            if show_message:
                ultima_sync_text = f"Actualizado {datetime.now().strftime('%H:%M:%S')}"
            else:
                # Para carga automática, mostrar "Cargado" en lugar de "Actualizado"
                ultima_sync_text = f"Cargado {datetime.now().strftime('%H:%M:%S')}"
            
            # Mapear datos usando las mismas claves que FREE GUI
            kpi_mappings = {
                "ventas_totales": f"${kpi_data.get('ventas_totales', 0):,.0f}",
                "num_facturas": f"{kpi_data.get('num_facturas', 0):,}",
                "ticket_promedio": f"${kpi_data.get('ticket_promedio', 0):,.0f}",
                "top_cliente": f"{kpi_data.get('top_cliente', 'Calculando...')[:25]}",
                "ultima_sync": ultima_sync_text
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