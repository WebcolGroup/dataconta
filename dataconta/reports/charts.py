"""
Módulo de Visualización de KPIs para DataConta FREE
Genera gráficas automáticas a partir de los datos de KPIs de Siigo API
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import seaborn as sns

# Configurar matplotlib para mejorar la calidad visual
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def ensure_charts_directory() -> str:
    """Asegurar que el directorio de gráficas existe."""
    charts_dir = os.path.join("outputs", "charts")
    os.makedirs(charts_dir, exist_ok=True)
    return charts_dir

def save_chart(fig, filename: str) -> str:
    """Guardar gráfica en el directorio de salida."""
    charts_dir = ensure_charts_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.png"
    filepath = os.path.join(charts_dir, full_filename)
    
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Gráfica guardada: {filepath}")
    return filepath

def plot_evolucion_ventas(data: List[Dict[str, Any]]) -> str:
    """
    Generar gráfica de evolución de ventas por mes.
    
    Args:
        data: Lista con formato [{"mes": "2025-01", "total": 51299420.0}, ...]
    
    Returns:
        str: Ruta del archivo PNG generado
    """
    try:
        if not data:
            raise ValueError("No hay datos de evolución de ventas")
        
        # Preparar datos
        meses = [item['mes'] for item in data]
        ventas = [item['total'] for item in data]
        
        # Convertir meses a fechas para mejor visualización
        fechas = [datetime.strptime(mes + "-01", "%Y-%m-%d") for mes in meses]
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Línea principal
        ax.plot(fechas, ventas, marker='o', linewidth=3, markersize=8, color='#2E86AB')
        
        # Formato del eje x
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        # Formato del eje y (moneda)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Títulos y etiquetas
        ax.set_title('Evolución de Ventas Mensual', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Período', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ventas Totales (COP)', fontsize=12, fontweight='bold')
        
        # Grid y estilo
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f8f9fa')
        
        # Agregar valores en cada punto
        for i, (fecha, venta) in enumerate(zip(fechas, ventas)):
            ax.annotate(f'${venta:,.0f}', 
                       (fecha, venta), 
                       textcoords="offset points", 
                       xytext=(0,10), 
                       ha='center',
                       fontsize=9,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return save_chart(fig, "evolucion_ventas")
        
    except Exception as e:
        print(f"❌ Error generando evolución de ventas: {str(e)}")
        return ""
    finally:
        plt.close()

def plot_ventas_por_cliente(data: List[Dict[str, Any]], top_n: int = 10) -> str:
    """
    Generar gráfica de ventas por cliente (barras horizontales).
    
    Args:
        data: Lista con formato [{"cliente_nombre": "webcol", "total": 19516000.0}, ...]
        top_n: Número de clientes top a mostrar
    
    Returns:
        str: Ruta del archivo PNG generado
    """
    try:
        if not data:
            raise ValueError("No hay datos de ventas por cliente")
        
        # Consolidar por NIT para evitar duplicados (como en la GUI)
        clientes_consolidados = {}
        for item in data:
            nit = item.get('nit', 'N/A')
            nombre = item.get('nombre', f'Cliente NIT: {nit}')
            nombre_display = item.get('nombre_display', nombre)
            total = item.get('total_ventas', 0)
            
            # Usar nombre display si está disponible, sino usar nombre, sino usar NIT
            display_name = nombre_display if nombre_display != "Cliente Sin Nombre" else f'Cliente NIT: {nit}'
            
            if nit in clientes_consolidados:
                clientes_consolidados[nit]['total'] += total
            else:
                clientes_consolidados[nit] = {
                    'cliente_nombre': display_name,
                    'total': total
                }
        
        # Convertir a lista y ordenar
        clientes_list = list(clientes_consolidados.values())
        clientes_list.sort(key=lambda x: x['total'], reverse=True)
        clientes_top = clientes_list[:top_n]
        
        # Preparar datos
        nombres = [cliente['cliente_nombre'] for cliente in clientes_top]
        ventas = [cliente['total'] for cliente in clientes_top]
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Barras horizontales con gradiente de colores
        colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(nombres)))
        bars = ax.barh(nombres, ventas, color=colors)
        
        # Formato del eje x (moneda)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Títulos y etiquetas
        ax.set_title(f'Top {top_n} Clientes por Ventas', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Ventas Totales (COP)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Clientes', fontsize=12, fontweight='bold')
        
        # Grid y estilo
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_facecolor('#f8f9fa')
        
        # Agregar valores al final de cada barra
        for i, (bar, venta) in enumerate(zip(bars, ventas)):
            width = bar.get_width()
            ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                   f'${venta:,.0f}', 
                   ha='left', va='center', fontweight='bold', fontsize=9)
        
        # Ajustar márgenes para nombres largos
        plt.subplots_adjust(left=0.2)
        plt.tight_layout()
        return save_chart(fig, "ventas_por_cliente")
        
    except Exception as e:
        print(f"❌ Error generando ventas por cliente: {str(e)}")
        return ""
    finally:
        plt.close()

def plot_ventas_por_producto(data: List[Dict[str, Any]], top_n: int = 10) -> str:
    """
    Generar gráfica de ventas por producto (barras verticales).
    
    Args:
        data: Lista con formato [{"producto_nombre": "Servicio...", "subtotal": 42216000.0}, ...]
        top_n: Número de productos top a mostrar
    
    Returns:
        str: Ruta del archivo PNG generado
    """
    try:
        if not data:
            raise ValueError("No hay datos de ventas por producto")
        
        # Ordenar por subtotal y tomar top N
        productos_ordenados = sorted(data, key=lambda x: x.get('subtotal', 0), reverse=True)
        productos_top = productos_ordenados[:top_n]
        
        # Preparar datos
        nombres = []
        subtotales = []
        
        for producto in productos_top:
            nombre = producto.get('producto_nombre', 'Producto desconocido')
            # Truncar nombres muy largos para mejor visualización
            if len(nombre) > 40:
                nombre = nombre[:37] + "..."
            nombres.append(nombre)
            subtotales.append(producto.get('subtotal', 0))
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Barras verticales con gradiente de colores
        colors = plt.cm.Greens(np.linspace(0.4, 0.8, len(nombres)))
        bars = ax.bar(range(len(nombres)), subtotales, color=colors)
        
        # Formato del eje y (moneda)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Configurar etiquetas del eje x
        ax.set_xticks(range(len(nombres)))
        ax.set_xticklabels(nombres, rotation=45, ha='right')
        
        # Títulos y etiquetas
        ax.set_title(f'Top {top_n} Productos por Ventas', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Productos', fontsize=12, fontweight='bold')
        ax.set_ylabel('Subtotal Ventas (COP)', fontsize=12, fontweight='bold')
        
        # Grid y estilo
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor('#f8f9fa')
        
        # Agregar valores encima de cada barra
        for bar, subtotal in zip(bars, subtotales):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'${subtotal:,.0f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=9,
                   rotation=90)
        
        plt.tight_layout()
        return save_chart(fig, "ventas_por_producto")
        
    except Exception as e:
        print(f"❌ Error generando ventas por producto: {str(e)}")
        return ""
    finally:
        plt.close()

def plot_estados_facturas(data: List[Dict[str, Any]]) -> str:
    """
    Generar gráfica de distribución por estado de facturas (torta/pie chart).
    
    Args:
        data: Lista con formato [{"estado": "unknown", "payment_status": "pendiente", "cantidad": 61}, ...]
    
    Returns:
        str: Ruta del archivo PNG generado
    """
    try:
        if not data:
            raise ValueError("No hay datos de estados de facturas")
        
        # Preparar datos
        labels = []
        valores = []
        
        for item in data:
            estado = item.get('estado', 'N/A')
            payment_status = item.get('payment_status', 'N/A')
            cantidad = item.get('cantidad', 0)
            
            # Crear etiqueta más descriptiva
            label = f'{estado}\n({payment_status})'
            labels.append(label)
            valores.append(cantidad)
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Colores para las diferentes categorías
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        
        # Gráfica de torta
        wedges, texts, autotexts = ax.pie(valores, 
                                         labels=labels,
                                         autopct='%1.1f%%',
                                         colors=colors[:len(valores)],
                                         startangle=90,
                                         explode=[0.1 if i == 0 else 0 for i in range(len(valores))])
        
        # Mejorar el formato del texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        
        # Título
        ax.set_title('Distribución de Estados de Facturas', fontsize=16, fontweight='bold', pad=20)
        
        # Asegurar que el gráfico sea circular
        ax.axis('equal')
        
        plt.tight_layout()
        return save_chart(fig, "estados_facturas")
        
    except Exception as e:
        print(f"❌ Error generando estados de facturas: {str(e)}")
        return ""
    finally:
        plt.close()

def plot_participacion_impuestos(kpis_data: Dict[str, Any]) -> str:
    """
    Generar gráfica de participación de impuestos vs subtotal (torta/pie chart).
    
    Args:
        kpis_data: Diccionario completo de KPIs que incluye participacion_impuestos y ventas_totales
    
    Returns:
        str: Ruta del archivo PNG generado
    """
    try:
        participacion_impuestos = kpis_data.get('participacion_impuestos', 0)
        ventas_totales = kpis_data.get('ventas_totales', 0)
        
        if ventas_totales == 0:
            raise ValueError("No hay datos de ventas totales")
        
        # Calcular valores
        valor_impuestos = ventas_totales * participacion_impuestos
        valor_subtotal = ventas_totales - valor_impuestos
        
        # Si no hay impuestos, mostrar solo subtotal
        if participacion_impuestos == 0:
            labels = ['Subtotal (Sin impuestos)']
            valores = [ventas_totales]
            colors = ['#4ECDC4']
        else:
            labels = ['Subtotal', 'Impuestos']
            valores = [valor_subtotal, valor_impuestos]
            colors = ['#4ECDC4', '#FF6B6B']
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Gráfica de torta
        def autopct_format(pct):
            if pct > 0:
                idx = int(pct/100 * len(valores)) if int(pct/100 * len(valores)) < len(valores) else len(valores)-1
                return f'{pct:.1f}%\n${valores[idx]:,.0f}'
            return ''
        
        wedges, texts, autotexts = ax.pie(valores,
                                         labels=labels,
                                         autopct=autopct_format,
                                         colors=colors,
                                         startangle=90,
                                         explode=[0.05 for _ in range(len(valores))])
        
        # Mejorar el formato del texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        
        # Título
        titulo = f'Composición de Ventas Totales\nTotal: ${ventas_totales:,.0f} COP'
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        
        # Asegurar que el gráfico sea circular
        ax.axis('equal')
        
        plt.tight_layout()
        return save_chart(fig, "participacion_impuestos")
        
    except Exception as e:
        print(f"❌ Error generando participación de impuestos: {str(e)}")
        return ""
    finally:
        plt.close()

def generate_all_charts(kpis_file_path: str) -> Dict[str, str]:
    """
    Generar todas las gráficas a partir de un archivo JSON de KPIs.
    
    Args:
        kpis_file_path: Ruta al archivo JSON de KPIs
    
    Returns:
        dict: Diccionario con las rutas de los archivos generados
    """
    try:
        # Cargar datos JSON
        with open(kpis_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Los datos están directamente en el JSON, no dentro de una clave 'kpis'
        kpis = data
        if not kpis or not isinstance(kpis, dict):
            raise ValueError("No se encontraron datos de KPIs en el archivo")
        
        print(f"📊 Generando visualizaciones desde: {kpis_file_path}")
        
        generated_files = {}
        
        # 1. Evolución de ventas
        if 'evolucion_ventas' in kpis:
            file_path = plot_evolucion_ventas(kpis['evolucion_ventas'])
            if file_path:
                generated_files['evolucion_ventas'] = file_path
        
        # 2. Ventas por cliente
        if 'ventas_por_cliente' in kpis:
            file_path = plot_ventas_por_cliente(kpis['ventas_por_cliente'])
            if file_path:
                generated_files['ventas_por_cliente'] = file_path
        
        # 3. Ventas por producto
        if 'ventas_por_producto' in kpis:
            file_path = plot_ventas_por_producto(kpis['ventas_por_producto'])
            if file_path:
                generated_files['ventas_por_producto'] = file_path
        
        # 4. Estados de facturas
        if 'estados_facturas' in kpis:
            file_path = plot_estados_facturas(kpis['estados_facturas'])
            if file_path:
                generated_files['estados_facturas'] = file_path
        
        # 5. Participación de impuestos
        file_path = plot_participacion_impuestos(kpis)
        if file_path:
            generated_files['participacion_impuestos'] = file_path
        
        print(f"✅ Se generaron {len(generated_files)} visualizaciones exitosamente")
        return generated_files
        
    except Exception as e:
        print(f"❌ Error generando visualizaciones: {str(e)}")
        return {}

# Función de ejemplo para uso directo
def main():
    """Función principal para pruebas."""
    kpis_file = "outputs/kpis/kpis_siigo_2025_20250918_121146.json"
    if os.path.exists(kpis_file):
        results = generate_all_charts(kpis_file)
        print("\n📊 Archivos generados:")
        for chart_type, file_path in results.items():
            print(f"  • {chart_type}: {file_path}")
    else:
        print(f"❌ No se encontró el archivo: {kpis_file}")

if __name__ == "__main__":
    main()