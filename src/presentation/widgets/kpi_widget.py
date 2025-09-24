"""
Widget especializado para mostrar KPIs del dashboard.

Esta clase se encarga exclusivamente de mostrar y actualizar
los indicadores clave de rendimiento (KPIs).

Principios SOLID aplicados:
- SRP: Solo maneja KPIs
- OCP: Extensible para nuevos KPIs
- DIP: Depende de abstracciones (datos JSON)
"""

import os
import glob
import json
from typing import Dict, Any, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .tooltip_manager import TooltipManager


class KPIWidget(QWidget):
    """
    Widget especializado para mostrar KPIs del dashboard.
    
    Responsabilidad: Mostrar y actualizar indicadores clave de rendimiento.
    """
    
    def __init__(self, parent=None):
        """
        Inicializar el widget de KPIs.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self._kpis_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp = 0
        self._kpi_labels = {}
        self._setup_ui()
        # Forzar recarga de datos y actualización de KPIs al iniciar
        self.refresh_data()
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario del widget de KPIs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título de la sección KPIs
        title_label = QLabel("📊 Indicadores Clave de Rendimiento")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1976d2; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Crear contenedor de KPIs en dos filas
        self._create_kpi_grid(layout)
        
        layout.addStretch()
    
    def _create_kpi_grid(self, parent_layout):
        """
        Crear la grilla de KPIs organizados en dos filas.
        
        Args:
            parent_layout: Layout padre donde agregar los KPIs
        """
        # Primera fila de KPIs
        first_row = QHBoxLayout()
        first_row.setSpacing(15)
        
        self._kpi_labels['ventas'] = self._create_kpi_card(
            "💰", "Ventas Totales", "$0", "#28a745"
        )
        self._kpi_labels['facturas'] = self._create_kpi_card(
            "📄", "Número de Facturas", "0", "#007bff"
        )
        self._kpi_labels['ticket'] = self._create_kpi_card(
            "🎯", "Ticket Promedio", "$0", "#fd7e14"
        )
        
        first_row.addWidget(self._kpi_labels['ventas'])
        first_row.addWidget(self._kpi_labels['facturas'])
        first_row.addWidget(self._kpi_labels['ticket'])
        
        parent_layout.addLayout(first_row)
        
        # Segunda fila de KPIs
        second_row = QHBoxLayout()
        second_row.setSpacing(15)
        
        self._kpi_labels['cliente_top'] = self._create_kpi_card(
            "🏆", "Cliente Principal", "N/A", "#dc3545"
        )
        self._kpi_labels['clientes'] = self._create_kpi_card(
            "👥", "Clientes Únicos", "0", "#6f42c1"
        )
        self._kpi_labels['utilidad_neta'] = self._create_kpi_card(
            "💸", "Utilidad Neta", "$0", "#17a2b8"
        )
        self._kpi_labels['cuentas_cobrar'] = self._create_kpi_card(
            "📥", "Cuentas por Cobrar", "$0", "#ffc107"
        )
        self._kpi_labels['cuentas_pagar'] = self._create_kpi_card(
            "📤", "Cuentas por Pagar", "$0", "#e83e8c"
        )
        # Spacer para centrar los KPIs
        second_row.addStretch()
        second_row.addWidget(self._kpi_labels['cliente_top'])
        second_row.addWidget(self._kpi_labels['clientes'])
        second_row.addWidget(self._kpi_labels['utilidad_neta'])
        second_row.addWidget(self._kpi_labels['cuentas_cobrar'])
        second_row.addWidget(self._kpi_labels['cuentas_pagar'])
        second_row.addStretch()
        parent_layout.addLayout(second_row)
    
    def _create_kpi_card(self, icon: str, title: str, value: str, color: str) -> QFrame:
        """
        Crear una tarjeta individual de KPI.
        
        Args:
            icon: Emoji o símbolo del KPI
            title: Título descriptivo
            value: Valor inicial
            color: Color del borde y elementos
            
        Returns:
            QFrame: Tarjeta de KPI configurada
        """
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        # Icono
        icon_label = QLabel(icon)
        icon_font = QFont("Segoe UI Emoji", 18)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_label.setStyleSheet("color: white;")
        layout.addWidget(icon_label)
        # Título
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        # Valor
        value_label = QLabel(value)
        value_font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        value_label.setFont(value_font)
        value_label.setStyleSheet("color: black;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        value_label.setWordWrap(True)
        layout.addWidget(value_label)
        # Guardar referencia al label de valor para actualizaciones
        card.value_label = value_label
        card.setMinimumSize(180, 100)
        card.setMaximumHeight(120)
        return card
    
    def _get_kpis_data(self) -> Dict[str, Any]:
        """
        Obtener datos de KPIs desde el archivo JSON más reciente con cache.
        
        Returns:
            dict: Datos de KPIs o diccionario vacío si no hay datos
        """
        try:
            kpis_dir = "outputs/kpis"
            if not os.path.exists(kpis_dir):
                return {}
            
            # Buscar el archivo JSON más reciente
            json_files = glob.glob(os.path.join(kpis_dir, "*.json"))
            if not json_files:
                return {}
            
            latest_file = max(json_files, key=os.path.getmtime)
            file_timestamp = os.path.getmtime(latest_file)
            
            # Usar cache si el archivo no ha cambiado
            if (self._kpis_cache is not None and 
                file_timestamp <= self._cache_timestamp):
                return self._kpis_cache
            
            # Cargar datos frescos
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Actualizar cache
            self._kpis_cache = data
            self._cache_timestamp = file_timestamp
            
            return data
            
        except Exception as e:
            print(f"Error cargando KPIs: {e}")
            return {}
    
    def _format_currency(self, amount: float) -> str:
        """
        Formatear cantidad como moneda colombiana.
        
        Args:
            amount: Cantidad a formatear
            
        Returns:
            str: Cantidad formateada como moneda
        """
        if amount >= 1_000_000_000:
            return f"${amount/1_000_000_000:.1f}B"
        elif amount >= 1_000_000:
            return f"${amount/1_000_000:.1f}M"
        elif amount >= 1_000:
            return f"${amount/1_000:.1f}K"
        else:
            return f"${amount:,.0f}"
    
    def _format_number(self, number: int) -> str:
        """
        Formatear número con separadores de miles.
        
        Args:
            number: Número a formatear
            
        Returns:
            str: Número formateado
        """
        if number >= 1_000_000:
            return f"{number/1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number/1_000:.1f}K"
        else:
            return f"{number:,}"
    
    def update_kpis(self, kpi_data: Dict[str, Any] = None):
        """Actualizar todos los KPIs con los datos más recientes o datos proporcionados."""
        # Forzar limpieza de cache antes de cada actualización
        self._kpis_cache = None
        self._cache_timestamp = 0
        kpis = kpi_data if kpi_data is not None else self._get_kpis_data()

        print("[DEBUG] KPIWidget.update_kpis received:", kpis)

        if not kpis:
            print("[DEBUG] No KPI data found, showing defaults.")
            self._update_kpi_value('ventas', "$0")
            self._update_kpi_value('facturas', "0")
            self._update_kpi_value('ticket', "$0")
            self._update_kpi_value('cliente_top', "Sin datos")
            self._update_kpi_value('clientes', "0")
            self._update_kpi_value('utilidad_neta', "$0")
            self._update_kpi_value('cuentas_cobrar', "$0")
            self._update_kpi_value('cuentas_pagar', "$0")
            return

        # Actualizar KPIs con datos reales y debug prints
        ventas_totales = kpis.get('ventas_totales', 0)
        print(f"[DEBUG] ventas_totales: {ventas_totales}")
        self._update_kpi_value('ventas', self._format_currency(ventas_totales))

        numero_facturas = kpis.get('numero_facturas', kpis.get('num_facturas', 0))
        print(f"[DEBUG] numero_facturas: {numero_facturas}")
        self._update_kpi_value('facturas', self._format_number(numero_facturas))

        ticket_promedio = kpis.get('ticket_promedio', 0)
        print(f"[DEBUG] ticket_promedio: {ticket_promedio}")
        self._update_kpi_value('ticket', self._format_currency(ticket_promedio))

        # Cliente principal
        ventas_clientes = kpis.get('ventas_por_cliente', [])
        print(f"[DEBUG] ventas_por_cliente: {ventas_clientes[:1]}")
        if ventas_clientes:
            top_cliente = ventas_clientes[0]
            nombre = top_cliente.get('nombre_display', f"NIT {top_cliente.get('nit', 'N/A')}")
            if len(nombre) > 25:
                nombre = nombre[:22] + "..."
            print(f"[DEBUG] cliente_top: {nombre}")
            self._update_kpi_value('cliente_top', nombre)
        else:
            print("[DEBUG] No top client found.")
            self._update_kpi_value('cliente_top', "Sin datos")

        clientes_unicos = kpis.get('clientes_unicos', 0)
        print(f"[DEBUG] clientes_unicos: {clientes_unicos}")
        self._update_kpi_value('clientes', self._format_number(clientes_unicos))

        # Nuevos KPIs
        utilidad_neta = kpis.get('utilidad_neta', 0)
        print(f"[DEBUG] utilidad_neta: {utilidad_neta}")
        self._update_kpi_value('utilidad_neta', self._format_currency(utilidad_neta))
        cuentas_cobrar = kpis.get('cuentas_por_cobrar', 0)
        print(f"[DEBUG] cuentas_por_cobrar: {cuentas_cobrar}")
        self._update_kpi_value('cuentas_cobrar', self._format_currency(cuentas_cobrar))
        cuentas_pagar = kpis.get('cuentas_por_pagar', 0)
        print(f"[DEBUG] cuentas_por_pagar: {cuentas_pagar}")
        self._update_kpi_value('cuentas_pagar', self._format_currency(cuentas_pagar))

        # Aplicar tooltips educativos
        self._apply_tooltips()
    
    def _update_kpi_value(self, kpi_key: str, new_value: str):
        """
        Actualizar el valor de un KPI específico.
        
        Args:
            kpi_key: Clave del KPI a actualizar
            new_value: Nuevo valor a mostrar
        """
        if kpi_key in self._kpi_labels:
            kpi_card = self._kpi_labels[kpi_key]
            if hasattr(kpi_card, 'value_label'):
                print(f"[DEBUG] Updating KPI '{kpi_key}' with value: {new_value}")
                kpi_card.value_label.setText(new_value)
                kpi_card.value_label.repaint()
                kpi_card.repaint()
    
    def _apply_tooltips(self):
        """Aplicar tooltips educativos a todos los KPIs."""
        tooltip_mapping = {
            'ventas': 'total_sales',
            'facturas': 'total_invoices', 
            'ticket': 'avg_ticket',
            'cliente_top': 'top_client',
            'clientes': 'unique_clients',
            'utilidad_neta': 'net_profit',
            'cuentas_cobrar': 'accounts_receivable',
            'cuentas_pagar': 'accounts_payable'
        }
        
        for kpi_key, tooltip_type in tooltip_mapping.items():
            if kpi_key in self._kpi_labels:
                TooltipManager.apply_kpi_tooltips(
                    self._kpi_labels[kpi_key], 
                    tooltip_type
                )
    
    def refresh_data(self):
        """Refrescar datos forzando actualización del cache."""
        self._kpis_cache = None
        self._cache_timestamp = 0
        self.update_kpis()