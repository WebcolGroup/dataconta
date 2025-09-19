"""
Free GUI Infrastructure Adapter - Infrastructure Layer
Adapter para la GUI FREE que maneja la conexión con API Siigo específicamente 
para la funcionalidad limitada de la versión gratuita.
"""

import os
import requests
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dotenv import load_dotenv

from src.application.ports.interfaces import InvoiceRepository, APIClient, Logger
from src.domain.entities.invoice import Invoice, InvoiceFilter, Customer, InvoiceItem, APICredentials


class FreeGUISiigoAdapter(InvoiceRepository, APIClient):
    """Adapter específico para GUI FREE - conexión con API Siigo limitada."""
    
    def __init__(self, logger: Logger):
        self._logger = logger
        self._access_token: Optional[str] = None
        self._is_authenticated = False
        load_dotenv()
    
    def authenticate(self, credentials: Optional[APICredentials] = None) -> bool:
        """Autenticar con API Siigo usando credenciales del .env."""
        try:
            # Obtener credenciales del .env si no se proporcionan
            if not credentials:
                api_url = os.getenv('SIIGO_API_URL', 'https://api.siigo.com')
                access_key = os.getenv('SIIGO_ACCESS_KEY')
                partner_id = os.getenv('PARTNER_ID', 'SandboxSiigoAPI')
                user = os.getenv('SIIGO_USER')
                
                if not access_key or not user:
                    self._logger.error("Credenciales Siigo no encontradas en .env")
                    return False
                
                credentials = APICredentials(
                    username=user,
                    password=access_key,  # En Siigo, password es el access_key
                    api_url=api_url,
                    partner_id=partner_id
                )
            
            self._logger.info("🔐 Iniciando autenticación con Siigo API...")
            
            # Headers para autenticación
            auth_headers = {
                'Content-Type': 'application/json',
                'Partner-Id': credentials.partner_id or 'SandboxSiigoAPI'
            }
            
            # Payload para obtener token
            auth_payload = {
                'username': credentials.username,
                'access_key': credentials.password  # access_key va en password
            }
            
            auth_url = f"{credentials.api_url}/auth"
            self._logger.info(f"📡 POST {auth_url}")
            
            # Realizar autenticación
            response = requests.post(
                auth_url, 
                json=auth_payload, 
                headers=auth_headers, 
                timeout=15
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self._access_token = auth_data.get('access_token')
                
                if self._access_token:
                    self._is_authenticated = True
                    self._logger.info("✅ Autenticación Siigo exitosa")
                    return True
                else:
                    self._logger.error("❌ No se recibió access_token")
                    return False
            else:
                self._logger.error(f"❌ Error autenticación: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self._logger.error(f"❌ Error en autenticación: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Verificar si hay conexión activa con API."""
        return self._is_authenticated and self._access_token is not None
    
    def get_invoices(self, filters: InvoiceFilter) -> List[Invoice]:
        """Obtener facturas desde API Siigo con filtros."""
        try:
            if not self.is_connected():
                if not self.authenticate():
                    self._logger.error("❌ No se pudo autenticar con Siigo")
                    return []
            
            encabezados_df, detalle_df = self.download_invoices_dataframes(
                fecha_inicio=filters.fecha_inicio,
                fecha_fin=filters.fecha_fin,
                cliente_id=filters.cliente_id,
                nit=filters.nit,
                estado=filters.estado
            )
            
            if encabezados_df is None or len(encabezados_df) == 0:
                return []
            
            # Convertir DataFrames a objetos Invoice
            invoices = []
            for _, row in encabezados_df.iterrows():
                # Crear customer
                customer = Customer(
                    id=str(row.get('cliente_nit', '')),
                    name=row.get('cliente_nombre', 'Sin Nombre'),
                    identification=str(row.get('cliente_nit', '')),
                    email=row.get('email', ''),
                    phone=row.get('phone', '')
                )
                
                # Obtener items de esta factura desde detalle_df
                items = []
                if detalle_df is not None and len(detalle_df) > 0:
                    factura_items = detalle_df[detalle_df['factura_id'] == row['factura_id']]
                    for _, item_row in factura_items.iterrows():
                        item = InvoiceItem(
                            code=str(item_row.get('producto_codigo', '')),
                            description=str(item_row.get('producto_nombre', '')),
                            quantity=float(item_row.get('cantidad', 0)),
                            price=float(item_row.get('precio_unitario', 0)),
                            taxes=[]  # Simplificado para FREE
                        )
                        items.append(item)
                
                # Crear invoice
                invoice = Invoice(
                    id=str(row['factura_id']),
                    date=str(row.get('fecha', '')),
                    due_date=str(row.get('due_date', '')),
                    customer=customer,
                    items=items,
                    subtotal=float(row.get('total', 0)) * 0.81,  # Aproximación
                    total=float(row.get('total', 0)),
                    status=str(row.get('estado', 'unknown')),
                    taxes=[]  # Simplificado para FREE
                )
                
                # Agregar campos adicionales como atributos
                invoice.payment_status = row.get('payment_status', 'unknown')
                invoice.seller_id = row.get('seller_id', '')
                
                invoices.append(invoice)
            
            self._logger.info(f"✅ {len(invoices)} facturas convertidas a objetos Invoice")
            return invoices
            
        except Exception as e:
            self._logger.error(f"❌ Error obteniendo facturas: {e}")
            return []
    
    def download_invoices_dataframes(self, 
                                   fecha_inicio: Optional[str] = None, 
                                   fecha_fin: Optional[str] = None,
                                   cliente_id: Optional[str] = None, 
                                   cc: Optional[str] = None, 
                                   nit: Optional[str] = None, 
                                   estado: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Descargar facturas desde API Siigo y retornar como DataFrames.
        Mantiene la funcionalidad original del archivo monolítico.
        """
        try:
            if not self.is_connected():
                self._logger.error("❌ No hay conexión con API Siigo")
                return None, None
            
            api_url = os.getenv('SIIGO_API_URL', 'https://api.siigo.com')
            partner_id = os.getenv('PARTNER_ID', 'SandboxSiigoAPI')
            
            # Headers para petición de facturas
            headers = {
                'Authorization': f'Bearer {self._access_token}',
                'Partner-Id': partner_id,
                'Content-Type': 'application/json'
            }
            
            # Construir parámetros
            base_params = {}
            if fecha_inicio:
                base_params['created_start'] = fecha_inicio
            if fecha_fin:
                base_params['created_end'] = fecha_fin
            if cliente_id:
                base_params['customer_id'] = cliente_id
            if cc:
                base_params['customer_identification'] = cc
            if nit:
                base_params['customer_identification'] = nit
            if estado:
                estado_map = {
                    'abierta': 'open',
                    'cerrada': 'closed', 
                    'anulada': 'cancelled'
                }
                base_params['status'] = estado_map.get(estado.lower(), estado)
            
            # Paginación completa
            all_invoices_data = []
            page = 1
            page_size = 100
            total_downloaded = 0
            
            self._logger.info(f"🔍 Filtros: {base_params}")
            
            while True:
                params = base_params.copy()
                params['page'] = page
                params['page_size'] = page_size
                
                url = f"{api_url}/v1/invoices"
                self._logger.info(f"📡 GET {url} - Página {page}")
                
                try:
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    
                    if response.status_code != 200:
                        self._logger.error(f"❌ Error API página {page}: {response.status_code}")
                        break
                    
                    response_data = response.json()
                    page_invoices = []
                    
                    if isinstance(response_data, dict) and 'results' in response_data:
                        page_invoices = response_data['results']
                    elif isinstance(response_data, list):
                        page_invoices = response_data
                    else:
                        break
                    
                    if not page_invoices:
                        break
                    
                    all_invoices_data.extend(page_invoices)
                    total_downloaded += len(page_invoices)
                    
                    self._logger.info(f"✅ Página {page}: {len(page_invoices)} facturas (Total: {total_downloaded})")
                    
                    if len(page_invoices) < page_size:
                        break
                    
                    page += 1
                    
                    # Rate limiting
                    import time
                    time.sleep(0.1)
                    
                except requests.exceptions.RequestException as e:
                    self._logger.error(f"❌ Error conexión página {page}: {e}")
                    break
            
            self._logger.info(f"✅ {total_downloaded} facturas descargadas")
            
            if total_downloaded == 0:
                return pd.DataFrame(), pd.DataFrame()
            
            # Procesar datos
            return self._process_siigo_invoices(all_invoices_data)
            
        except Exception as e:
            self._logger.error(f"❌ Error descargando facturas: {e}")
            return None, None
    
    def _process_siigo_invoices(self, invoices_data: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Procesar respuesta JSON de Siigo API y crear DataFrames."""
        
        if not isinstance(invoices_data, list) or len(invoices_data) == 0:
            return pd.DataFrame(), pd.DataFrame()
        
        encabezados = []
        detalle_items = []
        
        for i, invoice in enumerate(invoices_data):
            try:
                if not isinstance(invoice, dict):
                    continue
                
                factura_id = invoice.get('id', f'UNKNOWN_{i}')
                fecha = invoice.get('date', '')
                
                # Datos del cliente
                customer = invoice.get('customer', {})
                if isinstance(customer, dict):
                    cliente_nombre = customer.get('name', customer.get('commercial_name', 'Cliente Sin Nombre'))
                    cliente_nit = customer.get('identification', customer.get('nit', ''))
                else:
                    cliente_nombre = 'Cliente Sin Nombre'
                    cliente_nit = ''
                
                # Totales
                total = float(invoice.get('total', 0))
                impuestos = 0
                
                # Sumar impuestos
                taxes = invoice.get('taxes', [])
                if isinstance(taxes, list):
                    for tax in taxes:
                        if isinstance(tax, dict):
                            impuestos += float(tax.get('value', 0))
                
                estado = invoice.get('status', 'unknown')
                due_date = invoice.get('due_date', invoice.get('dueDate', ''))
                
                # Payment status
                payment_status = 'pendiente'
                if estado in ['closed', 'paid']:
                    payment_status = 'pagada'
                elif estado in ['cancelled', 'void']:
                    payment_status = 'anulada'
                elif due_date:
                    try:
                        due_date_obj = datetime.fromisoformat(due_date.replace('Z', ''))
                        if due_date_obj < datetime.now():
                            payment_status = 'vencida'
                    except:
                        pass
                
                # Seller ID
                seller_id = ''
                if 'vendedor_id' in invoice:
                    seller_id = invoice.get('vendedor_id', '')
                elif 'seller_id' in invoice:
                    seller_id = invoice.get('seller_id', '')
                else:
                    seller = invoice.get('seller', {})
                    if isinstance(seller, dict):
                        seller_id = seller.get('id', seller.get('identification', ''))
                    elif isinstance(seller, str):
                        seller_id = seller
                
                # Agregar encabezado
                encabezados.append({
                    'factura_id': factura_id,
                    'fecha': fecha,
                    'due_date': due_date,
                    'cliente_nombre': cliente_nombre,
                    'cliente_nit': cliente_nit,
                    'total': total,
                    'impuestos': impuestos,
                    'estado': estado,
                    'payment_status': payment_status,
                    'seller_id': seller_id
                })
                
                # Procesar items
                items = invoice.get('items', [])
                if isinstance(items, list):
                    for j, item in enumerate(items):
                        if not isinstance(item, dict):
                            continue
                        
                        producto_codigo = item.get('code', f'PROD_{j}')
                        producto_nombre = item.get('description', item.get('name', 'Producto Sin Nombre'))
                        cantidad = float(item.get('quantity', 0))
                        precio_unitario = float(item.get('price', 0))
                        subtotal = cantidad * precio_unitario
                        
                        # Impuestos del item
                        item_impuestos = 0
                        item_taxes = item.get('taxes', [])
                        if isinstance(item_taxes, list):
                            for tax in item_taxes:
                                if isinstance(tax, dict):
                                    item_impuestos += float(tax.get('value', 0))
                        
                        detalle_items.append({
                            'factura_id': factura_id,
                            'producto_codigo': producto_codigo,
                            'producto_nombre': producto_nombre,
                            'cantidad': cantidad,
                            'precio_unitario': precio_unitario,
                            'subtotal': subtotal,
                            'impuestos': item_impuestos
                        })
                
            except Exception as e:
                self._logger.warning(f"⚠️ Error procesando factura {i}: {e}")
                continue
        
        # Crear DataFrames
        encabezados_df = pd.DataFrame(encabezados)
        detalle_df = pd.DataFrame(detalle_items)
        
        self._logger.info(f"📊 Procesados {len(encabezados)} encabezados y {len(detalle_items)} items")
        
        return encabezados_df, detalle_df
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """Obtener factura específica por ID."""
        # Implementación simplificada para FREE
        filters = InvoiceFilter()
        invoices = self.get_invoices(filters)
        
        for invoice in invoices:
            if invoice.id == invoice_id:
                return invoice
        
        return None