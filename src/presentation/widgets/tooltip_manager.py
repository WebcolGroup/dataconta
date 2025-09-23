"""
Manager de tooltips educativos para el dashboard.

Esta clase centraliza la configuración de tooltips con contenido
educativo y de ayuda para mejorar la comprensión del usuario.

Principios SOLID aplicados:
- SRP: Solo maneja tooltips
- OCP: Extensible para nuevos tipos de ayuda
- DIP: No depende de widgets específicos
"""

from PySide6.QtCore import Qt


class TooltipManager:
    """
    Manager centralizado para tooltips educativos del dashboard.
    
    Responsabilidad: Proveer contenido educativo mediante tooltips.
    """
    
    @staticmethod
    def get_chart_tooltip(chart_type: str) -> str:
        """
        Obtener tooltip educativo para un tipo de gráfico específico.
        
        Args:
            chart_type: Tipo de gráfico ('sales_invoices', 'top_clients', etc.)
            
        Returns:
            str: Texto del tooltip con información educativa
        """
        tooltips = {
            'sales_invoices': (
                "📊 VENTAS vs FACTURAS\n\n"
                "• Volumen de negocio: Total de ingresos\n"
                "• Actividad comercial: Número de transacciones\n"
                "• Balance saludable: Alta facturación con ventas proporcionales\n\n"
                "💡 Tip: Un negocio eficiente maximiza ventas minimizando facturas"
            ),
            
            'top_clients': (
                "👥 TOP 10 CLIENTES\n\n"
                "• Identifica tus clientes VIP más valiosos\n"
                "• Analiza la concentración de ingresos\n"
                "• Prioriza atención comercial estratégica\n\n"
                "💡 Regla 80/20: Pocos clientes generan la mayoría de ingresos"
            ),
            
            'sales_distribution': (
                "🥧 CONCENTRACIÓN DE VENTAS\n\n"
                "• Visualiza dependencia de clientes clave\n"
                "• Evalúa riesgo de concentración excesiva\n"
                "• Identifica oportunidades de diversificación\n\n"
                "⚠️ Alerta: >50% en pocos clientes = alto riesgo"
            ),
            
            'avg_ticket': (
                "🎯 MAYOR TICKET PROMEDIO\n\n"
                "• Clientes con compras de alto valor unitario\n"
                "• Oportunidades de upselling y cross-selling\n"
                "• Segmento premium para estrategias especiales\n\n"
                "💰 Estrategia: Replica el éxito con otros clientes"
            ),
            
            'bubble_chart': (
                "💹 ANÁLISIS MULTIDIMENSIONAL\n\n"
                "• Eje X: Frecuencia de compra (facturas)\n"
                "• Eje Y: Volumen de ventas totales\n"
                "• Tamaño burbuja: Ticket promedio\n\n"
                "📈 Identifica: Clientes frecuentes vs esporádicos de alto valor"
            ),
            
            'pareto': (
                "📈 ANÁLISIS PARETO\n\n"
                "• Principio 80/20 aplicado a ventas\n"
                "• Identifica el 20% de clientes que generan 80% ingresos\n"
                "• Línea verde marca el punto crítico del 80%\n\n"
                "🎯 Enfoque: Maximiza atención a clientes clave"
            )
        }
        
        return tooltips.get(chart_type, "Información no disponible")
    
    @staticmethod
    def get_kpi_tooltip(kpi_type: str) -> str:
        """
        Obtener tooltip educativo para un KPI específico.
        
        Args:
            kpi_type: Tipo de KPI ('total_sales', 'avg_ticket', etc.)
            
        Returns:
            str: Texto del tooltip con información educativa
        """
        tooltips = {
            'total_sales': (
                "💰 VENTAS TOTALES\n\n"
                "Suma de todas las facturas procesadas\n"
                "• Indicador de volumen de negocio\n"
                "• Base para análisis de crecimiento\n"
                "• Comparar con períodos anteriores"
            ),
            
            'total_invoices': (
                "📄 NÚMERO DE FACTURAS\n\n"
                "Total de transacciones registradas\n"
                "• Indica actividad comercial\n"
                "• Frecuencia de ventas\n"
                "• Base para calcular ticket promedio"
            ),
            
            'avg_ticket': (
                "🎯 TICKET PROMEDIO\n\n"
                "Ventas totales ÷ Número de facturas\n"
                "• Valor promedio por transacción\n"
                "• Indicador de estrategia de precios\n"
                "• Meta: Incrementar sin perder volumen"
            ),
            
            'top_client': (
                "🏆 CLIENTE PRINCIPAL\n\n"
                "Cliente con mayores ventas totales\n"
                "• Tu cliente más valioso\n"
                "• Requiere atención estratégica\n"
                "• Modelo para replicar éxito"
            ),
            
            'unique_clients': (
                "👥 CLIENTES ÚNICOS\n\n"
                "Número total de clientes diferentes\n"
                "• Base de clientes activa\n"
                "• Diversificación de riesgo\n"
                "• Potencial de crecimiento"
            )
        }
        
        return tooltips.get(kpi_type, "Información no disponible")
    
    @staticmethod
    def get_tab_tooltip(tab_name: str) -> str:
        """
        Obtener tooltip para las pestañas del dashboard.
        
        Args:
            tab_name: Nombre de la pestaña ('dashboard', 'analytics')
            
        Returns:
            str: Texto del tooltip
        """
        tooltips = {
            'dashboard': (
                "📊 DASHBOARD PRINCIPAL\n\n"
                "Vista general de métricas clave:\n"
                "• KPIs principales del negocio\n"
                "• Resumen ejecutivo de ventas\n"
                "• Indicadores de rendimiento"
            ),
            
            'analytics': (
                "📈 ANÁLISIS DETALLADO\n\n"
                "Visualizaciones avanzadas:\n"
                "• Gráficos interactivos de ventas\n"
                "• Análisis de clientes y comportamiento\n"
                "• Insights para toma de decisiones"
            )
        }
        
        return tooltips.get(tab_name, "Información no disponible")
    
    @staticmethod
    def apply_chart_tooltips(canvas_widget, chart_type: str):
        """
        Aplicar tooltip a un widget canvas de matplotlib.
        
        Args:
            canvas_widget: Widget de matplotlib canvas
            chart_type: Tipo de gráfico para el tooltip apropiado
        """
        if canvas_widget:
            tooltip_text = TooltipManager.get_chart_tooltip(chart_type)
            canvas_widget.setToolTip(tooltip_text)
            canvas_widget.setToolTipDuration(10000)  # 10 segundos
    
    @staticmethod
    def apply_kpi_tooltips(label_widget, kpi_type: str):
        """
        Aplicar tooltip a un widget label de KPI.
        
        Args:
            label_widget: Widget QLabel del KPI
            kpi_type: Tipo de KPI para el tooltip apropiado
        """
        if label_widget:
            tooltip_text = TooltipManager.get_kpi_tooltip(kpi_type)
            label_widget.setToolTip(tooltip_text)
            label_widget.setToolTipDuration(8000)  # 8 segundos
    
    @staticmethod
    def apply_tab_tooltips(tab_widget, tab_index: int, tab_name: str):
        """
        Aplicar tooltip a una pestaña del QTabWidget.
        
        Args:
            tab_widget: QTabWidget
            tab_index: Índice de la pestaña
            tab_name: Nombre de la pestaña para el tooltip apropiado
        """
        if tab_widget:
            tooltip_text = TooltipManager.get_tab_tooltip(tab_name)
            tab_widget.setTabToolTip(tab_index, tooltip_text)