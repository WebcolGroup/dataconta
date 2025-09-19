"""
KPI Service - Application Layer
Servicio para el cálculo de KPIs financieros desde datos de Siigo API.
Mantiene la lógica de negocio separada de la UI según arquitectura hexagonal.
"""

import os
import json
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.application.ports.interfaces import InvoiceRepository, FileStorage, Logger
from src.domain.entities.invoice import InvoiceFilter


@dataclass
class KPIData:
    """Data class para los KPIs calculados."""
    ventas_totales: float
    num_facturas: int
    ticket_promedio: float
    ventas_por_cliente: List[Dict[str, Any]]
    ventas_por_producto: List[Dict[str, Any]]
    top_5_clientes: List[Dict[str, Any]]
    top_5_productos: List[Dict[str, Any]]
    participacion_impuestos: float
    evolucion_ventas: List[Dict[str, Any]]
    estados_facturas: List[Dict[str, Any]]
    top_cliente: str
    top_cliente_monto: float
    top_cliente_nit: str
    top_5_resumen: List[Dict[str, Any]]
    ultima_sync: str
    estado_sistema: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir KPIData a diccionario."""
        return {
            'ventas_totales': self.ventas_totales,
            'num_facturas': self.num_facturas,
            'ticket_promedio': self.ticket_promedio,
            'ventas_por_cliente': self.ventas_por_cliente,
            'ventas_por_producto': self.ventas_por_producto,
            'top_5_clientes': self.top_5_clientes,
            'top_5_productos': self.top_5_productos,
            'participacion_impuestos': self.participacion_impuestos,
            'evolucion_ventas': self.evolucion_ventas,
            'estados_facturas': self.estados_facturas,
            'top_cliente': self.top_cliente,
            'top_cliente_monto': self.top_cliente_monto,
            'top_cliente_nit': self.top_cliente_nit,
            'top_5_resumen': self.top_5_resumen,
            'ultima_sync': self.ultima_sync,
            'estado_sistema': self.estado_sistema
        }
    
    def to_json(self) -> str:
        """Convertir KPIData a JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class KPIService:
    """Servicio para cálculo y gestión de KPIs financieros."""
    
    def __init__(self, 
                 invoice_repository: InvoiceRepository, 
                 file_storage: FileStorage, 
                 logger: Logger):
        self._invoice_repository = invoice_repository
        self._file_storage = file_storage
        self._logger = logger
    
    def calculate_real_kpis(self, year: Optional[int] = None) -> KPIData:
        """
        Calcular KPIs reales desde datos de Siigo para el año especificado.
        
        Args:
            year: Año para el cálculo (por defecto año actual)
            
        Returns:
            KPIData: Datos de KPIs calculados
        """
        try:
            if year is None:
                year = date.today().year
            
            self._logger.info(f"📊 Calculando KPIs para el año {year}")
            
            # Configurar filtros para el año
            from datetime import datetime
            filters = InvoiceFilter(
                created_start=datetime(year, 1, 1),
                created_end=datetime(year, 12, 31)
            )
            
            # Obtener facturas del repositorio
            invoices = self._invoice_repository.get_invoices(filters)
            
            if not invoices:
                self._logger.warning("⚠️ No hay facturas para calcular KPIs")
                return self._get_default_kpis()
            
            # Convertir a DataFrames para análisis
            encabezados_data = []
            detalle_data = []
            
            for invoice in invoices:
                # Datos del encabezado
                encabezados_data.append({
                    'factura_id': invoice.id,
                    'fecha': invoice.date,
                    'cliente_nombre': invoice.customer.name if invoice.customer else 'Sin Nombre',
                    'cliente_nit': invoice.customer.identification if invoice.customer else '',
                    'total': float(invoice.total),
                    'impuestos': sum(float(tax.value) for tax in invoice.taxes) if invoice.taxes else 0,
                    'estado': invoice.status,
                    'payment_status': getattr(invoice, 'payment_status', 'unknown')
                })
                
                # Datos del detalle
                if invoice.items:
                    for item in invoice.items:
                        detalle_data.append({
                            'factura_id': invoice.id,
                            'producto_codigo': item.code,
                            'producto_nombre': item.description,
                            'cantidad': float(item.quantity),
                            'precio_unitario': float(item.price),
                            'subtotal': float(item.quantity) * float(item.price),
                            'impuestos': sum(float(tax.value) for tax in item.taxes) if item.taxes else 0
                        })
            
            encabezados_df = pd.DataFrame(encabezados_data)
            detalle_df = pd.DataFrame(detalle_data)
            
            # Calcular KPIs
            kpis = self._calculate_kpis_from_dataframes(encabezados_df, detalle_df)
            
            # Guardar KPIs
            self._save_kpis_to_file(kpis.__dict__, year)
            
            self._logger.info(f"✅ KPIs calculados: {kpis.num_facturas} facturas, ${kpis.ventas_totales:,.0f} en ventas")
            
            return kpis
            
        except Exception as e:
            self._logger.error(f"❌ Error calculando KPIs: {e}")
            return self._get_default_kpis()
    
    def _calculate_kpis_from_dataframes(self, encabezados_df: pd.DataFrame, detalle_df: pd.DataFrame) -> KPIData:
        """Calcular KPIs desde DataFrames procesados."""
        
        # 1. Ventas totales
        ventas_totales = float(encabezados_df['total'].sum())
        
        # 2. Número de facturas
        num_facturas = len(encabezados_df)
        
        # 3. Ticket promedio
        ticket_promedio = ventas_totales / num_facturas if num_facturas > 0 else 0
        
        # 4. Ventas por cliente (consolidado por NIT)
        ventas_consolidadas = encabezados_df.groupby('cliente_nit').agg({
            'total': 'sum',
            'cliente_nombre': 'first'
        }).reset_index()
        
        # Limpiar nombres de clientes
        ventas_consolidadas['cliente_display'] = ventas_consolidadas.apply(
            lambda row: row['cliente_nombre'] if row['cliente_nombre'] != 'Sin Nombre' 
                       else f"Cliente NIT: {row['cliente_nit']}", axis=1
        )
        
        ventas_por_cliente = ventas_consolidadas.sort_values('total', ascending=False)
        
        # 5. Ventas por producto/servicio
        ventas_por_producto = []
        if len(detalle_df) > 0:
            productos_agrupados = detalle_df.groupby(['producto_codigo', 'producto_nombre'])['subtotal'].sum().reset_index()
            ventas_por_producto = productos_agrupados.sort_values('subtotal', ascending=False)
        
        # 6. Top 5 clientes
        top_5_clientes = ventas_por_cliente.head(5).to_dict('records')
        
        # 7. Top 5 productos
        top_5_productos = []
        if len(detalle_df) > 0:
            top_productos = detalle_df.groupby(['producto_codigo', 'producto_nombre'])['cantidad'].sum().reset_index()
            top_5_productos = top_productos.sort_values('cantidad', ascending=False).head(5).to_dict('records')
        
        # 8. Participación de impuestos
        total_impuestos = float(encabezados_df['impuestos'].sum())
        participacion_impuestos = (total_impuestos / ventas_totales) * 100 if ventas_totales > 0 else 0
        
        # 9. Evolución de ventas mensual
        encabezados_df['fecha'] = pd.to_datetime(encabezados_df['fecha'], errors='coerce')
        encabezados_df['mes'] = encabezados_df['fecha'].dt.to_period('M')
        evolucion_mensual = encabezados_df.groupby('mes')['total'].sum().reset_index()
        evolucion_mensual['mes'] = evolucion_mensual['mes'].astype(str)
        evolucion_ventas = evolucion_mensual.to_dict('records')
        
        # 10. Estados de facturas
        estados_facturas = encabezados_df.groupby(['estado', 'payment_status']).size().reset_index(name='cantidad')
        
        # Datos adicionales para dashboard
        top_cliente = 'N/A'
        top_cliente_monto = 0
        top_cliente_nit = ''
        top_5_resumen = []
        
        if len(ventas_por_cliente) > 0:
            top_cliente_info = ventas_por_cliente.iloc[0]
            top_cliente = top_cliente_info['cliente_display']
            top_cliente_monto = float(top_cliente_info['total'])
            top_cliente_nit = top_cliente_info['cliente_nit']
            
            # Crear resumen del top 5
            for i in range(min(5, len(ventas_por_cliente))):
                cliente = ventas_por_cliente.iloc[i]
                top_5_resumen.append({
                    'posicion': i + 1,
                    'nombre': cliente['cliente_display'],
                    'nit': cliente['cliente_nit'],
                    'total': float(cliente['total']),
                    'porcentaje': (float(cliente['total']) / ventas_totales) * 100
                })
        
        return KPIData(
            ventas_totales=ventas_totales,
            num_facturas=num_facturas,
            ticket_promedio=ticket_promedio,
            ventas_por_cliente=ventas_por_cliente.to_dict('records'),
            ventas_por_producto=ventas_por_producto.to_dict('records') if len(ventas_por_producto) > 0 else [],
            top_5_clientes=top_5_clientes,
            top_5_productos=top_5_productos,
            participacion_impuestos=participacion_impuestos,
            evolucion_ventas=evolucion_ventas,
            estados_facturas=estados_facturas.to_dict('records'),
            top_cliente=top_cliente,
            top_cliente_monto=top_cliente_monto,
            top_cliente_nit=top_cliente_nit,
            top_5_resumen=top_5_resumen,
            ultima_sync=datetime.now().strftime("%H:%M:%S"),
            estado_sistema='ACTIVO ✅'
        )
    
    def _save_kpis_to_file(self, kpis_data: Dict[str, Any], year: int) -> str:
        """Guardar KPIs en archivo JSON."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kpis_siigo_{year}_{timestamp}.json"
            
            kpis_with_meta = {
                'metadata': {
                    'generado_en': datetime.now().isoformat(),
                    'año': year,
                    'version': 'DataConta FREE v1.0',
                    'fuente': 'API Siigo'
                },
                'kpis': kpis_data
            }
            
            file_path = self._file_storage.save_data(kpis_with_meta, filename)
            self._logger.info(f"💾 KPIs guardados: {filename}")
            return file_path
            
        except Exception as e:
            self._logger.error(f"❌ Error guardando KPIs: {e}")
            return ""
    
    def _get_default_kpis(self) -> KPIData:
        """Obtener KPIs por defecto cuando hay error o no hay datos."""
        return KPIData(
            ventas_totales=0,
            num_facturas=0,
            ticket_promedio=0,
            ventas_por_cliente=[],
            ventas_por_producto=[],
            top_5_clientes=[],
            top_5_productos=[],
            participacion_impuestos=0,
            evolucion_ventas=[],
            estados_facturas=[],
            top_cliente='Sin datos',
            top_cliente_monto=0,
            top_cliente_nit='',
            top_5_resumen=[],
            ultima_sync=datetime.now().strftime("%H:%M:%S"),
            estado_sistema='SIN DATOS ⚠️'
        )
    
    def load_existing_kpis(self) -> Optional[KPIData]:
        """Cargar KPIs existentes desde el archivo más reciente."""
        try:
            import glob
            
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
            
            # Manejar diferentes formatos
            if 'kpis' in raw_data and 'metadata' in raw_data:
                kpis_dict = raw_data['kpis']
            elif 'ventas_totales' in raw_data:
                kpis_dict = raw_data
            else:
                return None
            
            # Preparar datos con valores por defecto para campos faltantes
            default_kpis = self._get_default_kpis()
            merged_data = {}
            
            # Copiar todos los campos del default
            for field in KPIData.__dataclass_fields__:
                merged_data[field] = getattr(default_kpis, field)
            
            # Sobrescribir con datos existentes cuando estén disponibles
            for key, value in kpis_dict.items():
                if key in KPIData.__dataclass_fields__:
                    merged_data[key] = value
            
            # Convertir dict a KPIData
            return KPIData(**merged_data)
            
        except Exception as e:
            self._logger.error(f"❌ Error cargando KPIs: {e}")
            return None