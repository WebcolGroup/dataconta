"""
Free GUI Infrastructure Adapter - Infrastructure Layer
Adapter para la GUI FREE que maneja la conexión con API Siigo específicamente 
para la funcionalidad limitada de la versión gratuita.
"""

import os
import requests
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Callable
from dotenv import load_dotenv
from functools import wraps

from src.application.ports.interfaces import InvoiceRepository, APIClient, Logger
from src.domain.entities.invoice import Invoice, InvoiceFilter, Customer, InvoiceItem, APICredentials


class FreeGUISiigoAdapter(InvoiceRepository, APIClient):
    """Adapter específico para GUI FREE - conexión con API Siigo limitada."""
    
    def __init__(self, logger: Logger):
        self._logger = logger
        self._access_token: Optional[str] = None
        self._is_authenticated = False
        self._safety_callback: Optional[Callable] = None  # Callback para confirmar operaciones peligrosas
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
                    access_key=access_key,  # Usar el parámetro correcto
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
                'access_key': credentials.access_key  # Usar access_key correcto
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
            
            # Convertir campos del filtro estándar a formato FREE GUI
            fecha_inicio = None
            fecha_fin = None
            
            if filters.created_start:
                fecha_inicio = filters.created_start.strftime('%Y-%m-%d') if hasattr(filters.created_start, 'strftime') else str(filters.created_start)
            
            if filters.created_end:
                fecha_fin = filters.created_end.strftime('%Y-%m-%d') if hasattr(filters.created_end, 'strftime') else str(filters.created_end)
            
            encabezados_df, detalle_df = self.download_invoices_dataframes(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                cliente_id=filters.customer_id,  # Usar nuevo campo customer_id
                nit=filters.document_id,  # Mantener document_id como NIT por compatibilidad
                estado=filters.status  # Usar nuevo campo status
            )
            
            if encabezados_df is None or len(encabezados_df) == 0:
                return []
            
            # Convertir DataFrames a objetos Invoice
            invoices = []
            for _, row in encabezados_df.iterrows():
                # Crear customer usando los campos correctos de la entidad
                customer = Customer(
                    identification=str(row.get('cliente_nit', '')),
                    name=[str(row.get('cliente_nombre', 'Sin Nombre'))],  # Lista de nombres
                    commercial_name=str(row.get('cliente_nombre', 'Sin Nombre'))
                )
                
                # Obtener items de esta factura desde detalle_df
                items = []
                if detalle_df is not None and len(detalle_df) > 0:
                    factura_items = detalle_df[detalle_df['factura_id'] == row['factura_id']]
                    for _, item_row in factura_items.iterrows():
                        # Usar Decimal para mantener consistencia de tipos
                        from decimal import Decimal
                        item = InvoiceItem(
                            code=str(item_row.get('producto_codigo', '')),
                            description=str(item_row.get('producto_nombre', '')),
                            quantity=Decimal(str(item_row.get('cantidad', 0))),
                            price=Decimal(str(item_row.get('precio_unitario', 0))),
                            taxes=[]  # Simplificado para FREE
                        )
                        items.append(item)
                
                # Crear invoice con los campos correctos de la entidad
                from datetime import datetime as dt
                
                # Parsear fecha
                invoice_date = dt.now()  # Default
                try:
                    date_str = str(row.get('fecha', ''))
                    if date_str:
                        invoice_date = dt.strptime(date_str.split('T')[0], '%Y-%m-%d')
                except:
                    pass
                
                invoice = Invoice(
                    id=str(row['factura_id']),
                    document_id=str(row.get('numero', row['factura_id'])),
                    number=int(row.get('numero', 0)) if row.get('numero', '').isdigit() else 0,
                    name=f"Factura {row.get('numero', row['factura_id'])}",
                    date=invoice_date,
                    customer=customer,
                    items=items,
                    payments=[]  # Vacío por ahora en versión FREE
                )
                
                # Agregar total como Decimal para mantener consistencia de tipos
                try:
                    from decimal import Decimal
                    total_value = row.get('total', 0)
                    invoice.total = Decimal(str(total_value)) if total_value else Decimal('0.00')
                except:
                    invoice.total = Decimal('0.00')
                
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
    
    def get_customers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtener lista de clientes desde API de Siigo para poblar dropdown.
        
        Args:
            limit: Máximo número de clientes a obtener (por limitaciones FREE)
            
        Returns:
            Lista de diccionarios con id, name e identification de clientes
        """
        try:
            if not self.is_connected():
                if not self.authenticate():
                    self._logger.error("❌ No se pudo autenticar con Siigo")
                    return []
            
            api_url = os.getenv('SIIGO_API_URL', 'https://api.siigo.com')
            partner_id = os.getenv('PARTNER_ID', 'SandboxSiigoAPI')
            
            headers = {
                'Authorization': f'Bearer {self._access_token}',
                'Partner-Id': partner_id,
                'Content-Type': 'application/json'
            }
            
            # Parámetros para obtener clientes
            params = {
                'page': 1,
                'page_size': min(limit, 100)  # API Siigo máximo 100 por página
            }
            
            url = f"{api_url}/v1/customers"
            self._logger.info(f"📡 GET {url} - Obteniendo clientes...")
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Formatear datos para el dropdown
                customers = []
                for customer in results:
                    customer_dict = {
                        'id': str(customer.get('id', '')),
                        'name': customer.get('name', ['Sin Nombre'])[0] if isinstance(customer.get('name'), list) else str(customer.get('name', 'Sin Nombre')),
                        'identification': str(customer.get('identification', ''))
                    }
                    customers.append(customer_dict)
                
                self._logger.info(f"✅ Obtenidos {len(customers)} clientes desde Siigo")
                return customers
                
            else:
                self._logger.error(f"❌ Error obteniendo clientes: {response.status_code}")
                return []
                
        except Exception as e:
            self._logger.error(f"❌ Error en get_customers: {e}")
            return []
    
    def get_invoice_statuses(self) -> List[Dict[str, str]]:
        """
        Obtener estados disponibles para facturas según API Siigo.
        
        Returns:
            Lista de diccionarios con value y label para dropdown de estados
        """
        try:
            # Estados basados en la documentación de Siigo API
            statuses = [
                {'value': '', 'label': 'Todos los Estados'},
                {'value': 'open', 'label': '🔓 Abierta'},
                {'value': 'closed', 'label': '🔒 Cerrada'},
                {'value': 'cancelled', 'label': '❌ Anulada'}
            ]
            
            self._logger.info(f"📋 Estados de factura disponibles: {len(statuses)-1}")
            return statuses
            
        except Exception as e:
            self._logger.error(f"❌ Error obteniendo estados: {e}")
            return [{'value': '', 'label': 'Todos los Estados'}]
    
    # ==================== Sistema de Seguridad API ====================
    
    def set_safety_callback(self, callback: Callable) -> None:
        """
        Establecer callback para confirmar operaciones peligrosas.
        
        Args:
            callback: Función que recibe (method, url, data) y retorna bool
        """
        self._safety_callback = callback
        self._logger.info("🛡️ Sistema de seguridad API activado")
    
    def _is_dangerous_operation(self, method: str) -> bool:
        """
        Determinar si una operación HTTP es peligrosa y requiere confirmación.
        
        Args:
            method: Método HTTP (GET, POST, PUT, PATCH, DELETE)
            
        Returns:
            bool: True si la operación es peligrosa
        """
        dangerous_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        return method.upper() in dangerous_methods
    
    def _require_user_confirmation(self, method: str, url: str, data: Dict[str, Any] = None) -> bool:
        """
        Solicitar confirmación del usuario para operaciones peligrosas.
        
        Args:
            method: Método HTTP
            url: URL del endpoint
            data: Datos a enviar
            
        Returns:
            bool: True si el usuario confirma, False si cancela
        """
        try:
            if not self._safety_callback:
                self._logger.warning("⚠️ Sistema de seguridad no configurado, bloqueando operación peligrosa")
                return False
            
            # Log de la operación peligrosa detectada
            self._logger.warning(f"🚨 Operación peligrosa detectada: {method} {url}")
            
            # Llamar al callback de confirmación
            user_approved = self._safety_callback(method, url, data or {})
            
            if user_approved:
                self._logger.info(f"✅ Usuario aprobó operación: {method} {url}")
                return True
            else:
                self._logger.info(f"❌ Usuario rechazó operación: {method} {url}")
                return False
                
        except Exception as e:
            self._logger.error(f"❌ Error en confirmación de seguridad: {e}")
            return False
    
    def _safe_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Realizar request HTTP con verificación de seguridad.
        
        Args:
            method: Método HTTP
            url: URL del endpoint
            **kwargs: Argumentos para requests
            
        Returns:
            requests.Response: Respuesta HTTP
            
        Raises:
            PermissionError: Si la operación es rechazada por el usuario
            Exception: Otros errores de la request
        """
        # Verificar si es una operación peligrosa
        if self._is_dangerous_operation(method):
            # Extraer datos del payload
            payload = kwargs.get('json', kwargs.get('data', {}))
            
            # Solicitar confirmación del usuario
            if not self._require_user_confirmation(method, url, payload):
                raise PermissionError(f"Operación {method} {url} rechazada por el usuario")
            
            # Log de operación autorizada
            self._logger.info(f"🔓 Ejecutando operación autorizada: {method} {url}")
        
        # Ejecutar la request
        method_map = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'PATCH': requests.patch,
            'DELETE': requests.delete
        }
        
        request_func = method_map.get(method.upper())
        if not request_func:
            raise ValueError(f"Método HTTP no soportado: {method}")
        
        return request_func(url, **kwargs)
    
    # ==================== Métodos de API Seguros ====================
    
    def safe_create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crear factura con confirmación de seguridad.
        
        Args:
            invoice_data: Datos de la factura a crear
            
        Returns:
            Dict con la respuesta de la API
        """
        try:
            if not self._is_authenticated:
                raise Exception("No autenticado con Siigo API")
            
            url = f"{os.getenv('SIIGO_API_URL')}/v1/invoices"
            headers = self._get_headers()
            
            response = self._safe_request('POST', url, json=invoice_data, headers=headers, timeout=30)
            
            if response.status_code == 201:
                self._logger.info(f"✅ Factura creada exitosamente")
                return response.json()
            else:
                raise Exception(f"Error creando factura: {response.status_code} - {response.text}")
                
        except PermissionError as e:
            self._logger.warning(f"🚫 Creación de factura bloqueada: {e}")
            raise
        except Exception as e:
            self._logger.error(f"❌ Error creando factura: {e}")
            raise
    
    def safe_update_invoice(self, invoice_id: str, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualizar factura con confirmación de seguridad.
        
        Args:
            invoice_id: ID de la factura a actualizar
            invoice_data: Nuevos datos de la factura
            
        Returns:
            Dict con la respuesta de la API
        """
        try:
            if not self._is_authenticated:
                raise Exception("No autenticado con Siigo API")
            
            url = f"{os.getenv('SIIGO_API_URL')}/v1/invoices/{invoice_id}"
            headers = self._get_headers()
            
            response = self._safe_request('PUT', url, json=invoice_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self._logger.info(f"✅ Factura {invoice_id} actualizada exitosamente")
                return response.json()
            else:
                raise Exception(f"Error actualizando factura: {response.status_code} - {response.text}")
                
        except PermissionError as e:
            self._logger.warning(f"🚫 Actualización de factura bloqueada: {e}")
            raise
        except Exception as e:
            self._logger.error(f"❌ Error actualizando factura: {e}")
            raise
    
    def safe_delete_invoice(self, invoice_id: str) -> bool:
        """
        Eliminar factura con confirmación de seguridad.
        
        Args:
            invoice_id: ID de la factura a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if not self._is_authenticated:
                raise Exception("No autenticado con Siigo API")
            
            url = f"{os.getenv('SIIGO_API_URL')}/v1/invoices/{invoice_id}"
            headers = self._get_headers()
            
            response = self._safe_request('DELETE', url, headers=headers, timeout=30)
            
            if response.status_code == 204:
                self._logger.info(f"✅ Factura {invoice_id} eliminada exitosamente")
                return True
            else:
                raise Exception(f"Error eliminando factura: {response.status_code} - {response.text}")
                
        except PermissionError as e:
            self._logger.warning(f"🚫 Eliminación de factura bloqueada: {e}")
            raise
        except Exception as e:
            self._logger.error(f"❌ Error eliminando factura: {e}")
            raise