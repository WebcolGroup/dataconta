"""
Módulo de reportes para DataConta
"""

from .charts import (
    plot_evolucion_ventas,
    plot_ventas_por_cliente,
    plot_ventas_por_producto,
    plot_estados_facturas,
    plot_participacion_impuestos,
    generate_all_charts
)

__all__ = [
    'plot_evolucion_ventas',
    'plot_ventas_por_cliente', 
    'plot_ventas_por_producto',
    'plot_estados_facturas',
    'plot_participacion_impuestos',
    'generate_all_charts'
]