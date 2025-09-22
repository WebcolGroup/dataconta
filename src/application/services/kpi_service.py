"""
KPI Service - Application Layer
Caso de uso para el cálculo de KPIs financieros.
Orquesta llamadas al dominio sin contener lógica de negocio propia.
"""

import os
import json
import glob
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.application.ports.interfaces import InvoiceRepository, FileStorage, Logger
from src.domain.entities.invoice import InvoiceFilter
from src.domain.entities.kpis import KPIsVentas
from src.domain.services.kpi_service import KPICalculationService, KPIAnalysisService


@dataclass
class KPIData:
    """Data class para los KPIs calculados (compatibilidad hacia atrás)."""
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


class KPIApplicationService:
    """
    Servicio de aplicación para KPIs.
    Orquesta operaciones sin contener lógica de negocio.
    """
    
    def __init__(self, 
                 invoice_repository: InvoiceRepository,
                 file_storage: FileStorage,
                 kpi_calculation_service: KPICalculationService,
                 kpi_analysis_service: KPIAnalysisService,
                 logger: Logger):
        self._invoice_repository = invoice_repository
        self._file_storage = file_storage
        self._kpi_calculation_service = kpi_calculation_service
        self._kpi_analysis_service = kpi_analysis_service
        self._logger = logger
    
    def calculate_kpis_for_period(self, 
                                 fecha_inicio: datetime, 
                                 fecha_fin: datetime) -> Dict[str, Any]:
        """
        Calcular KPIs para un período específico.
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            
        Returns:
            Diccionario con KPIs calculados
        """
        try:
            self._logger.info(f"📊 Calculando KPIs para período {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
            
            # 1. Obtener datos del repositorio (Infrastructure)
            facturas_df = self._obtener_facturas_dataframe(fecha_inicio, fecha_fin)
            
            if facturas_df is None or len(facturas_df) == 0:
                self._logger.warning("⚠️ No hay facturas para el período especificado")
                kpis_vacios = self._kpi_calculation_service.calcular_kpis_ventas(
                    pd.DataFrame(), fecha_inicio, fecha_fin
                )
                return kpis_vacios.to_dict()
            
            # 2. Validar datos (Domain)
            validacion = self._kpi_calculation_service.validar_consistencia_datos(facturas_df)
            if not validacion['es_valido']:
                raise ValueError(f"Datos inválidos: {validacion['errores']}")
            
            # 3. Calcular KPIs usando servicio de dominio
            kpis_ventas = self._kpi_calculation_service.calcular_kpis_ventas(
                facturas_df, fecha_inicio, fecha_fin
            )
            
            # 4. Generar insights (Domain)
            insights = self._kpi_analysis_service.generar_insights(kpis_ventas)
            
            # 5. Persistir resultados (Infrastructure)
            result = kpis_ventas.to_dict()
            result['insights'] = insights
            result['validacion'] = validacion
            
            self._guardar_kpis(result, fecha_inicio, fecha_fin)
            
            self._logger.info(f"✅ KPIs calculados exitosamente: {kpis_ventas.numero_facturas} facturas")
            
            return result
            
        except Exception as e:
            self._logger.error(f"❌ Error calculando KPIs: {e}")
            raise
    
    def calculate_kpis_for_current_year(self) -> Dict[str, Any]:
        """Calcular KPIs para el año actual."""
        current_year = date.today().year
        fecha_inicio = datetime(current_year, 1, 1)
        fecha_fin = datetime(current_year, 12, 31)
        
        return self.calculate_kpis_for_period(fecha_inicio, fecha_fin)
    
    def load_existing_kpis(self) -> Optional[Dict[str, Any]]:
        """
        Cargar KPIs existentes desde el archivo más reciente.
        Busca archivos en outputs/kpis/ con formatos kpis_calculados_* o kpis_siigo_*.
        
        Returns:
            Dict con los KPIs si se encuentra archivo, None si no hay archivos
        """
        try:
            kpis_dir = "outputs/kpis"
            
            if not os.path.exists(kpis_dir):
                self._logger.warning(f"⚠️ Directorio {kpis_dir} no existe")
                return None
            
            # Buscar ambos tipos de archivos KPIs
            patterns = [
                os.path.join(kpis_dir, "kpis_calculados_*.json"),
                os.path.join(kpis_dir, "kpis_siigo_*.json")
            ]
            
            kpi_files = []
            for pattern in patterns:
                kpi_files.extend(glob.glob(pattern))
            
            if not kpi_files:
                self._logger.info("ℹ️ No se encontraron archivos KPIs existentes")
                return None
            
            # Obtener el archivo más reciente
            latest_file = max(kpi_files, key=os.path.getmtime)
            self._logger.info(f"📂 Cargando KPIs desde: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Manejar diferentes formatos de archivo
            if 'kpis' in raw_data and 'metadata' in raw_data:
                # Formato API real con estructura compleja
                kpis_data = raw_data['kpis']
            elif 'ventas_totales' in raw_data:
                # Formato simple directo
                kpis_data = raw_data
            else:
                self._logger.warning("⚠️ Formato de archivo KPIs no reconocido")
                return None
            
            self._logger.info("✅ KPIs existentes cargados correctamente")
            return kpis_data
            
        except Exception as e:
            self._logger.error(f"❌ Error cargando KPIs existentes: {e}")
            return None
    
    def _obtener_facturas_dataframe(self, fecha_inicio: datetime, fecha_fin: datetime) -> Optional[pd.DataFrame]:
        """
        Obtener facturas como DataFrame desde el repositorio.
        Adaptador entre dominio y capa de infraestructura.
        """
        try:
            # Verificar si el repositorio tiene método directo para DataFrame
            if hasattr(self._invoice_repository, 'download_invoices_dataframes'):
                fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
                fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
                
                encabezados_df, _ = self._invoice_repository.download_invoices_dataframes(
                    fecha_inicio=fecha_inicio_str,
                    fecha_fin=fecha_fin_str
                )
                return encabezados_df
                
            else:
                # Fallback: usar método estándar y convertir a DataFrame
                filters = InvoiceFilter(
                    created_start=fecha_inicio,
                    created_end=fecha_fin
                )
                
                invoices = self._invoice_repository.get_invoices(filters)
                return self._convert_invoices_to_dataframe(invoices)
                
        except Exception as e:
            self._logger.error(f"❌ Error obteniendo facturas: {e}")
            return None
    
    def _convert_invoices_to_dataframe(self, invoices: List[Any]) -> pd.DataFrame:
        """Convertir lista de facturas a DataFrame."""
        if not invoices:
            return pd.DataFrame()
            
        datos = []
        for invoice in invoices:
            datos.append({
                'factura_id': invoice.id,
                'fecha': invoice.date,
                'cliente_nombre': invoice.customer.name if invoice.customer else 'Cliente Sin Nombre',
                'cliente_nit': invoice.customer.identification if invoice.customer else '',
                'total': float(invoice.total),
                'estado': invoice.status,
            })
        
        return pd.DataFrame(datos)
    
    def _guardar_kpis(self, kpis_data: Dict[str, Any], fecha_inicio: datetime, fecha_fin: datetime) -> None:
        """Guardar KPIs usando el file storage con formato consistente."""
        try:
            # Usar formato consistente con el dashboard: kpis_siigo_YYYY_timestamp
            year = fecha_inicio.year
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kpis/kpis_siigo_{year}_{timestamp}"
            
            # Limpiar archivos KPIs antiguos antes de guardar (mantener solo 1)
            if hasattr(self._file_storage, 'clean_old_files'):
                self._file_storage.clean_old_files("kpis", "kpis_*.json", keep_latest=0)
            
            file_path = self._file_storage.save_data(kpis_data, filename)
            self._logger.info(f"💾 KPIs guardados en: {file_path}")
            
        except Exception as e:
            self._logger.error(f"❌ Error guardando KPIs: {e}")


# Mantener compatibilidad con código existente
class KPIService(KPIApplicationService):
    """Alias para compatibilidad hacia atrás."""
    
    def __init__(self, invoice_repository: InvoiceRepository, file_storage: FileStorage, logger: Logger):
        # Para compatibilidad, crear servicios de dominio internamente
        from src.domain.services.kpi_service import KPICalculationServiceImpl, KPIAnalysisService
        
        kpi_calc_service = KPICalculationServiceImpl()
        kpi_analysis_service = KPIAnalysisService(kpi_calc_service)
        
        super().__init__(
            invoice_repository=invoice_repository,
            file_storage=file_storage,
            kpi_calculation_service=kpi_calc_service,
            kpi_analysis_service=kpi_analysis_service,
            logger=logger
        )
    
    def calculate_real_kpis(self, invoices_data: Optional[List[Any]] = None) -> KPIData:
        """Método para compatibilidad hacia atrás."""
        try:
            # Si se pasan datos de facturas, convertirlos
            if invoices_data:
                df = self._convert_invoices_to_dataframe(invoices_data)
                fecha_inicio = datetime.now().replace(month=1, day=1)
                fecha_fin = datetime.now().replace(month=12, day=31)
                
                kpis_ventas = self._kpi_calculation_service.calcular_kpis_ventas(
                    df, fecha_inicio, fecha_fin
                )
                return self._convert_kpis_ventas_to_legacy(kpis_ventas)
            else:
                # Calcular para año actual
                result = self.calculate_kpis_for_current_year()
                return self._convert_to_legacy_kpidata(result)
            
        except Exception as e:
            self._logger.error(f"❌ Error en calculate_real_kpis: {e}")
            return self._get_default_kpis()
    
    def _convert_to_legacy_kpidata(self, result: Dict[str, Any]) -> KPIData:
        """Convertir resultado nuevo al formato legacy KPIData."""
        return KPIData(
            ventas_totales=result.get('ventas_totales', 0),
            num_facturas=result.get('numero_facturas', 0),
            ticket_promedio=result.get('ticket_promedio', 0),
            ventas_por_cliente=result.get('ventas_por_cliente', []),
            ventas_por_producto=[],  # No implementado aún
            top_5_clientes=result.get('ventas_por_cliente', [])[:5],
            top_5_productos=[],  # No implementado aún
            participacion_impuestos=0.0,  # No implementado aún
            evolucion_ventas=[],  # No implementado aún
            estados_facturas=[],  # No implementado aún
            top_cliente=result.get('cliente_top', {}).get('nombre', 'N/A') if result.get('cliente_top') else 'N/A',
            top_cliente_monto=result.get('cliente_top', {}).get('monto', 0) if result.get('cliente_top') else 0,
            top_cliente_nit=result.get('cliente_top', {}).get('nit', '') if result.get('cliente_top') else '',
            top_5_resumen=result.get('ventas_por_cliente', [])[:5],
            ultima_sync=datetime.now().strftime("%H:%M:%S"),
            estado_sistema=result.get('estado_sistema', 'ACTIVO ✅')
        )
    
    def _convert_kpis_ventas_to_legacy(self, kpis: KPIsVentas) -> KPIData:
        """Convertir KPIsVentas a KPIData legacy."""
        return KPIData(
            ventas_totales=float(kpis.ventas_totales),
            num_facturas=kpis.numero_facturas,
            ticket_promedio=float(kpis.ticket_promedio),
            ventas_por_cliente=[
                {
                    'nit': v.nit,
                    'nombre': v.nombre_display,
                    'total': float(v.total_ventas),
                    'facturas': v.numero_facturas
                }
                for v in kpis.ventas_por_cliente
            ],
            ventas_por_producto=[],
            top_5_clientes=[
                {
                    'nit': v.nit,
                    'nombre': v.nombre_display,
                    'total': float(v.total_ventas)
                }
                for v in kpis.obtener_top_clientes(5)
            ],
            top_5_productos=[],
            participacion_impuestos=0.0,
            evolucion_ventas=[],
            estados_facturas=[],
            top_cliente=kpis.cliente_top.nombre_display if kpis.cliente_top else 'N/A',
            top_cliente_monto=float(kpis.cliente_top.total_ventas) if kpis.cliente_top else 0,
            top_cliente_nit=kpis.cliente_top.nit if kpis.cliente_top else '',
            top_5_resumen=[
                {
                    'cliente': v.nombre_display,
                    'ventas': float(v.total_ventas)
                }
                for v in kpis.obtener_top_clientes(5)
            ],
            ultima_sync=kpis.fecha_calculo.strftime("%H:%M:%S"),
            estado_sistema=kpis.estado_sistema
        )
    
    def _get_default_kpis(self) -> KPIData:
        """Obtener KPIs por defecto cuando hay error."""
        return KPIData(
            ventas_totales=0.0,
            num_facturas=0,
            ticket_promedio=0.0,
            ventas_por_cliente=[],
            ventas_por_producto=[],
            top_5_clientes=[],
            top_5_productos=[],
            participacion_impuestos=0.0,
            evolucion_ventas=[],
            estados_facturas=[],
            top_cliente='N/A',
            top_cliente_monto=0.0,
            top_cliente_nit='',
            top_5_resumen=[],
            ultima_sync=datetime.now().strftime("%H:%M:%S"),
            estado_sistema='SIN DATOS ⚠️'
        )