"""
Fábrica de gráficos matplotlib para el dashboard.

Esta clase se encarga exclusivamente de crear las visualizaciones
de datos usando matplotlib, siguiendo el principio de responsabilidad única.

Principios SOLID aplicados:
- SRP: Solo crea gráficos matplotlib
- OCP: Extensible para nuevos tipos de gráficos
- DIP: Depende de abstracciones (datos JSON)
"""

import os
import glob
import json
import numpy as np
from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget

# Importaciones condicionales para matplotlib
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartFactory:
    """
    Fábrica de gráficos matplotlib para el dashboard.
    
    Responsabilidad: Crear visualizaciones de datos usando matplotlib.
    """
    
    def __init__(self):
        """Inicializar la fábrica de gráficos."""
        self._kpis_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp = 0
    
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
    
    def create_sales_invoices_chart(self) -> Optional[QWidget]:
        """
        Gráfico 1: Total ventas vs número de facturas (barras).
        
        Returns:
            QWidget: Canvas de matplotlib o None si no hay datos
        """
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
    # Título oculto, el card lo muestra externamente
        ax.tick_params(axis='both', colors='#1976d2', labelsize=10)
        
        # Agregar valores en las barras con mejor posicionamiento
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
                   f'{value:.1f}', ha='center', va='bottom', fontsize=10, 
                   color='#1976d2', fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        return canvas
    
    def create_top_clients_chart(self) -> Optional[QWidget]:
        """
        Gráfico 2: Top 10 clientes por ventas (barras horizontales).
        
        Returns:
            QWidget: Canvas de matplotlib o None si no hay datos
        """
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
    # Título oculto, el card lo muestra externamente
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
        
        return canvas
    
    def create_sales_distribution_chart(self) -> Optional[QWidget]:
        """
        Gráfico 3: Distribución de ventas por cliente (pie chart).
        
        Returns:
            QWidget: Canvas de matplotlib o None si no hay datos
        """
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
        
        # Crear pie chart con mejor configuración según Copilot Prompt
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%',
                                         colors=colors, startangle=90, 
                                         labeldistance=1.1, pctdistance=0.8,
                                         textprops={'fontsize': 8})
        
    # Título oculto, el card lo muestra externamente
        
        # Leyenda externa según Copilot Prompt
        ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
        
        # Mejorar legibilidad de porcentajes
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
            autotext.set_weight('bold')
        
        fig.tight_layout()
        
        return canvas
    
    def create_avg_ticket_chart(self) -> Optional[QWidget]:
        """
        Gráfico 4: Clientes con mayor ticket promedio.
        
        Returns:
            QWidget: Canvas de matplotlib o None si no hay datos
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        kpis = self._get_kpis_data()
        ventas_clientes = kpis.get('ventas_por_cliente', [])
        
        if not ventas_clientes:
            return None
        
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
        top_8_ticket = clientes_con_ticket[:8]  # Reducir a 8 para mejor visualización
        
        if not top_8_ticket:
            return None
        
        # Nombres más cortos y optimizados
        nombres = []
        for cliente in top_8_ticket:
            nombre_completo = cliente.get('nombre_display', f"Cliente {cliente.get('nit', 'N/A')}")
            if len(nombre_completo) > 12:
                nombres.append(nombre_completo[:9] + "...")
            else:
                nombres.append(nombre_completo)
        
        tickets = [cliente.get('ticket_promedio', 0) / 1_000_000 for cliente in top_8_ticket]
        
        # Crear gráfico de barras según Copilot Prompt
        x_pos = range(len(nombres))
        bars = ax.bar(x_pos, tickets, color='#28a745', alpha=0.7, width=0.7)
    # Título oculto, el card lo muestra externamente
        ax.set_ylabel('Ticket Promedio (Millones $)', fontsize=11, color='#1976d2')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(nombres, rotation=45, ha='right', fontsize=8, color='#1976d2')
        ax.tick_params(axis='both', colors='#1976d2')
        
        # Usar bar_label según Copilot Prompt
        ax.bar_label(bars, labels=[f'{v:.1f}M' for v in tickets], 
                    fontsize=8, color='#1976d2', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='y')
        # Usar tight_layout según Copilot Prompt
        fig.tight_layout()

        return canvas
    
    def create_bubble_chart(self) -> Optional[QWidget]:
        """
        Gráfico 5: Scatter plot - Ventas vs Facturas (bubble chart).
        
        Returns:
            QWidget: Canvas de matplotlib o None si no hay datos
        """
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
        
    # Título oculto, el card lo muestra externamente
        ax.set_xlabel('Número de Facturas', fontsize=11, color='#1976d2')
        ax.set_ylabel('Ventas (Millones $)', fontsize=11, color='#1976d2')
        ax.tick_params(axis='both', colors='#1976d2', labelsize=10)
        
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        return canvas
    
    def create_pareto_chart(self) -> Optional[QWidget]:
        """
        Gráfico 6: Pareto de clientes (acumulado).
        
        Returns:
            QWidget: Canvas de matplotlib o None si no hay datos
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        kpis = self._get_kpis_data()
        ventas_clientes = kpis.get('ventas_por_cliente', [])
        
        if not ventas_clientes:
            return None
        
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
    # Título oculto, el card lo muestra externamente
        
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
        
        ax1.grid(True, alpha=0.3)
        # Mejor ajuste de layout para doble eje
        fig.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)
        fig.tight_layout(pad=2.0)
        
        return canvas
    
    def get_chart_definitions(self):
        """
        Obtener definiciones de gráficos disponibles.
        
        Returns:
            list: Lista de tuplas (título, método_creación, fila, columna)
        """
        return [
            ("📊 Ventas vs Facturas", self.create_sales_invoices_chart, 0, 0),
            ("👥 Top 10 Clientes", self.create_top_clients_chart, 0, 1),
            ("🥧 Concentración de Ventas", self.create_sales_distribution_chart, 1, 0),
            ("🎯 Mayor Ticket Promedio", self.create_avg_ticket_chart, 1, 1),
            ("💹 Ventas vs Facturas (Bubble)", self.create_bubble_chart, 2, 0),
            ("📈 Pareto de Clientes", self.create_pareto_chart, 2, 1)
        ]