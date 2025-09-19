"""
Siigo API Widget - Componente UI especializado para descarga de facturas desde API Siigo
Parte de la refactorización del monolito dataconta_free_gui_refactored.py

Responsabilidad única: UI para interacción con API Siigo y filtros de descarga
"""

import os
from typing import Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QFrame, QScrollArea, QLineEdit, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class SiigoApiWidget(QWidget):
    """
    Widget especializado para descarga de facturas desde API Siigo.
    
    Principios SOLID:
    - SRP: Solo maneja la UI de API Siigo
    - OCP: Extensible para nuevos filtros y funcionalidades
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para API Siigo
    - DIP: Depende de abstracciones (signals)
    """
    
    # Signals para comunicación con el controlador (inversión de dependencias)
    export_siigo_csv_requested = Signal()
    export_siigo_excel_requested = Signal()
    test_connection_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Referencias a widgets de filtros
        self.siigo_date_start: Optional[QDateEdit] = None
        self.siigo_date_end: Optional[QDateEdit] = None
        self.siigo_client_id: Optional[QLineEdit] = None
        self.siigo_nit: Optional[QLineEdit] = None
        self.siigo_status: Optional[QComboBox] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz del widget de API Siigo."""
        # Widget contenedor principal con scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear scroll area para hacer el área de API Siigo responsive
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Widget interno con el contenido
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Grupo de configuración de filtros
        filters_group = self.create_filters_section()
        layout.addWidget(filters_group)
        
        # Botones de exportación
        buttons_group = self.create_buttons_section()
        layout.addWidget(buttons_group)
        
        layout.addStretch()
        
        # Configurar el scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def create_filters_section(self) -> QGroupBox:
        """Crear sección de filtros para API Siigo."""
        filters_group = QGroupBox("🌐 Descarga de Facturas desde API Siigo - DATOS REALES")
        filters_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        filters_layout = QGridLayout(filters_group)
        filters_layout.setContentsMargins(8, 20, 8, 8)  # Margen superior para separar título del contenido
        
        # Información de la API
        api_info = QLabel("""
        🔥 NUEVA FUNCIONALIDAD - DESCARGA DIRECTA DESDE SIIGO:
        
        ✅ API CONFIGURADA: erikagarcia1179@hotmail.com  
        ✅ CONEXIÓN REAL: Datos directos desde Siigo API
        ✅ FILTROS AVANZADOS: Por fechas, cliente, NIT, estado
        ✅ DOBLE EXPORT: CSV + Excel con dos hojas
        
        📊 Funcionalidad: Descarga facturas reales con filtros opcionales
        🎯 Resultado: Dos datasets (Encabezados + Detalle de ítems)
        """)
        api_info.setWordWrap(True)
        api_info.setStyleSheet("""
            background-color: #e3f2fd; 
            padding: 15px; 
            border-radius: 8px;
            border: 2px solid #1976d2;
            color: #1565c0;
            font-weight: bold;
            font-size: 12px;
        """)
        
        # Filtros de fecha
        filters_layout.addWidget(QLabel("📅 Fecha Inicio:"), 1, 0)
        self.siigo_date_start = QDateEdit()
        self.siigo_date_start.setToolTip(
            "🌐 Fecha inicio para API Siigo:\n"
            "• Descarga facturas desde esta fecha\n"
            "• Conecta directamente a Siigo\n"
            "• Por defecto: Hace 30 días\n\n"
            "🚀 100% datos reales desde Siigo API"
        )
        self.siigo_date_start.setCalendarPopup(True)
        self.siigo_date_start.setDate(datetime.now().date().replace(day=1))  # Primer día del mes
        filters_layout.addWidget(self.siigo_date_start, 1, 1)
        
        filters_layout.addWidget(QLabel("📅 Fecha Fin:"), 1, 2)
        self.siigo_date_end = QDateEdit()
        self.siigo_date_end.setToolTip(
            "🌐 Fecha fin para API Siigo:\n"
            "• Descarga facturas hasta esta fecha\n"
            "• Máximo rango: 1 año\n"
            "• Por defecto: Hoy\n\n"
            "🚀 Datos en tiempo real desde Siigo"
        )
        self.siigo_date_end.setCalendarPopup(True)
        self.siigo_date_end.setDate(datetime.now().date())  # Hoy
        filters_layout.addWidget(self.siigo_date_end, 1, 3)
        
        # Filtros de cliente
        filters_layout.addWidget(QLabel("🏢 Cliente ID:"), 2, 0)
        self.siigo_client_id = QLineEdit()
        self.siigo_client_id.setToolTip(
            "🆔 ID de cliente en Siigo (opcional):\n"
            "• Número interno de Siigo\n"
            "• Filtra facturas de cliente específico\n"
            "• Ejemplo: 12345\n\n"
            "⚡ Deje vacío para todos los clientes"
        )
        self.siigo_client_id.setPlaceholderText("ID del cliente (opcional)")
        filters_layout.addWidget(self.siigo_client_id, 2, 1)
        
        filters_layout.addWidget(QLabel("🆔 CC/NIT:"), 2, 2)
        self.siigo_nit = QLineEdit()
        self.siigo_nit.setToolTip(
            "🆔 NIT del cliente (opcional):\n"
            "• Número de identificación tributaria\n"
            "• Formato: 123456789-0\n"
            "• Filtra por documento específico\n\n"
            "⚡ Deje vacío para todos los NITs"
        )
        self.siigo_nit.setPlaceholderText("Cédula o NIT (opcional)")
        filters_layout.addWidget(self.siigo_nit, 2, 3)
        
        # Estado
        filters_layout.addWidget(QLabel("📋 Estado:"), 3, 0)
        self.siigo_status = QComboBox()
        self.siigo_status.setToolTip(
            "📈 Estado de facturas en Siigo:\n"
            "• Todas: Sin filtro\n"
            "• Pagada: Facturas cobradas\n"
            "• Abierta: Pendientes de pago\n"
            "• Vencida: En mora\n\n"
            "🌐 Estados sincronizados con Siigo"
        )
        self.siigo_status.addItems(["Todos", "abierta", "cerrada", "anulada"])
        filters_layout.addWidget(self.siigo_status, 3, 1)
        
        filters_layout.addWidget(api_info, 0, 0, 1, 4)
        
        return filters_group
    
    def create_buttons_section(self) -> QGroupBox:
        """Crear sección de botones de exportación."""
        buttons_group = QGroupBox("📤 Exportar Facturas Reales desde Siigo API")
        buttons_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        buttons_layout = QGridLayout(buttons_group)
        buttons_layout.setContentsMargins(8, 20, 8, 8)  # Margen superior para separar título del contenido
        
        siigo_btn_style = """
            QPushButton { 
                background-color: #1976d2; 
                color: white; 
                padding: 15px; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 12pt;
                border: none;
            }
            QPushButton:hover { 
                background-color: #1565c0; 
            }
        """
        
        # Botón CSV
        csv_siigo_btn = QPushButton("📊 Descargar y Exportar a CSV")
        csv_siigo_btn.setToolTip(
            "🌐 Descarga DIRECTA desde API Siigo:\n"
            "• Conecta en tiempo real a Siigo\n"
            "• Aplica todos los filtros configurados\n"
            "• Genera 2 archivos CSV:\n"
            "  - facturas_encabezados.csv\n"
            "  - facturas_detalle.csv\n\n"
            "🔥 100% datos reales desde Siigo API\n"
            "📊 Procesa encabezados + items detallados"
        )
        csv_siigo_btn.setStyleSheet(siigo_btn_style)
        csv_siigo_btn.clicked.connect(self.export_siigo_csv_with_filters)
        buttons_layout.addWidget(csv_siigo_btn, 0, 0)
        
        # Botón Excel
        excel_siigo_btn = QPushButton("📄 Descargar y Exportar a Excel")
        excel_siigo_btn.setToolTip(
            "📄 Descarga desde API Siigo a Excel:\n"
            "• Un archivo .xlsx con 2 hojas:\n"
            "  - Hoja 'Encabezados'\n"
            "  - Hoja 'Detalle'\n"
            "• Formato profesional listo para análisis\n"
            "• Compatible con Power BI y tablas dinámicas\n\n"
            "🔥 Datos reales desde Siigo API\n"
            "📊 Ideal para reportes ejecutivos"
        )
        excel_siigo_btn.setStyleSheet(siigo_btn_style.replace("#1976d2", "#4caf50").replace("#1565c0", "#388e3c"))
        excel_siigo_btn.clicked.connect(self.export_siigo_excel_with_filters)
        buttons_layout.addWidget(excel_siigo_btn, 0, 1)
        
        # Botón de prueba rápida
        test_btn = QPushButton("⚡ Prueba Rápida (Sin filtros)")
        test_btn.setToolTip(
            "⚡ Prueba de conectividad API Siigo:\n"
            "• Descarga facturas recientes\n"
            "• Sin aplicar filtros\n"
            "• Valida autenticación y conexión\n"
            "• Genera CSV de prueba\n\n"
            "🔧 Perfecto para:\n"
            "• Verificar configuración API\n"
            "• Probar credenciales\n"
            "• Validar estructura de datos"
        )
        test_btn.setStyleSheet(siigo_btn_style.replace("#1976d2", "#ff9800").replace("#1565c0", "#f57c00"))
        test_btn.clicked.connect(self.test_connection_requested.emit)
        buttons_layout.addWidget(test_btn, 1, 0, 1, 2)
        
        return buttons_group
    
    # ==================== Métodos para obtener valores de filtros ====================
    
    def get_date_start(self) -> str:
        """Obtener fecha de inicio seleccionada."""
        if self.siigo_date_start:
            return self.siigo_date_start.date().toString("yyyy-MM-dd")
        return ""
    
    def get_date_end(self) -> str:
        """Obtener fecha de fin seleccionada."""
        if self.siigo_date_end:
            return self.siigo_date_end.date().toString("yyyy-MM-dd")
        return ""
    
    def get_client_id(self) -> str:
        """Obtener ID de cliente."""
        if self.siigo_client_id:
            return self.siigo_client_id.text().strip()
        return ""
    
    def get_nit(self) -> str:
        """Obtener NIT del cliente."""
        if self.siigo_nit:
            return self.siigo_nit.text().strip()
        return ""
    
    def get_status(self) -> str:
        """Obtener estado seleccionado."""
        if self.siigo_status:
            status = self.siigo_status.currentText()
            return "" if status == "Todos" else status
        return ""
    
    def get_filters(self) -> dict:
        """Obtener todos los filtros como diccionario."""
        return {
            "date_start": self.get_date_start(),
            "date_end": self.get_date_end(),
            "client_id": self.get_client_id(),
            "nit": self.get_nit(),
            "status": self.get_status()
        }
    
    # ==================== Funcionalidad Excel ====================
    
    def export_siigo_excel_with_filters(self):
        """Exportar facturas de Siigo API a Excel usando los filtros de la interfaz."""
        fecha_inicio = self.get_date_start()
        fecha_fin = self.get_date_end()
        cliente_id = self.get_client_id() or None
        nit = self.get_nit() or None
        estado = self.get_status() or None
        
        self.log_message(f"🔄 Exportando Excel Siigo - Filtros: {fecha_inicio} a {fecha_fin}")
        
        # Verificar si el rango es muy amplio (más de 3 meses)
        if self._is_date_range_too_large(fecha_inicio, fecha_fin):
            reply = QMessageBox.question(
                self,
                "Rango de Fechas Amplio",
                f"El rango de fechas es muy amplio ({fecha_inicio} a {fecha_fin}).\n\n"
                f"Para evitar timeouts, se procesará en chunks mensuales.\n\n"
                f"¿Desea continuar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return
                
            self.export_siigo_invoices_to_excel_chunked(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                cliente_id=cliente_id,
                nit=nit,
                estado=estado
            )
        else:
            self.export_siigo_invoices_to_excel(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                cliente_id=cliente_id,
                nit=nit,
                estado=estado
            )
    
    def export_siigo_invoices_to_excel(self, fecha_inicio=None, fecha_fin=None,
                                     cliente_id=None, cc=None, nit=None, estado=None):
        """
        Descargar facturas de Siigo API y exportar a archivo Excel con dos hojas.
        
        Args:
            fecha_inicio (str): Fecha inicio YYYY-MM-DD
            fecha_fin (str): Fecha fin YYYY-MM-DD
            cliente_id (str): ID del cliente
            cc (str): Cédula del cliente
            nit (str): NIT del cliente  
            estado (str): Estado (abierta, cerrada, anulada)
        """
        
        try:
            self.log_message("🚀 Iniciando exportación de facturas Siigo a Excel...")
            
            # Descargar facturas
            encabezados_df, detalle_df = self.download_invoices(
                fecha_inicio, fecha_fin, cliente_id, cc, nit, estado
            )
            
            if encabezados_df is None or detalle_df is None:
                return
            
            if len(encabezados_df) == 0:
                QMessageBox.information(
                    self, 
                    "Sin Resultados", 
                    "No se encontraron facturas con los filtros especificados."
                )
                return
            
            # Crear archivo Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("outputs", exist_ok=True)
            excel_file = f"outputs/facturas_siigo_{timestamp}.xlsx"
            
            # Escribir a Excel con dos hojas
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                encabezados_df.to_excel(writer, sheet_name='Encabezados', index=False)
                detalle_df.to_excel(writer, sheet_name='Detalle', index=False)
            
            file_size = os.path.getsize(excel_file) / 1024
            
            self.log_message(f"✅ Excel generado: {os.path.basename(excel_file)} ({file_size:.1f} KB)")
            
            QMessageBox.information(
                self,
                "✅ Exportación Excel Exitosa",
                f"Facturas de Siigo API exportadas a Excel:\n\n"
                f"📊 Encabezados: {len(encabezados_df)} facturas\n"
                f"📋 Detalle: {len(detalle_df)} items\n\n" 
                f"📁 Archivo: {os.path.basename(excel_file)}\n"
                f"💾 Tamaño: {file_size:.1f} KB\n"
                f"📄 Hojas: 'Encabezados' y 'Detalle'\n\n"
                f"✅ Datos reales desde API Siigo"
            )
            
        except ImportError as e:
            if 'openpyxl' in str(e):
                QMessageBox.critical(
                    self, 
                    "Dependencia Faltante",
                    "Para exportar a Excel necesita instalar openpyxl:\n\n"
                    "pip install openpyxl\n\n"
                    "O use la exportación a CSV como alternativa."
                )
            else:
                raise e
        except Exception as e:
            self.log_message(f"❌ Error en exportación Excel: {e}")
            QMessageBox.critical(self, "Error", f"Error en exportación Excel:\n{e}")
    
    def download_invoices(self, fecha_inicio=None, fecha_fin=None, cliente_id=None, 
                         cc=None, nit=None, estado=None):
        """
        Descargar facturas desde la API de Siigo /v1/invoices con filtros opcionales.
        CORREGIDO: Ahora usa autenticación OAuth correcta.
        
        Args:
            fecha_inicio (str): Fecha de inicio en formato YYYY-MM-DD
            fecha_fin (str): Fecha fin en formato YYYY-MM-DD  
            cliente_id (str): ID del cliente
            cc (str): Cédula del cliente
            nit (str): NIT del cliente
            estado (str): Estado de la factura (abierta, cerrada, anulada)
        
        Returns:
            tuple: (encabezados_df, detalle_df) DataFrames de pandas con los datos
        """
        import requests
        from dotenv import load_dotenv
        import base64
        
        try:
            # Cargar variables de entorno
            load_dotenv()
            
            # Configuración de API Siigo
            api_url = os.getenv('SIIGO_API_URL', 'https://api.siigo.com')
            access_key = os.getenv('SIIGO_ACCESS_KEY')
            partner_id = os.getenv('PARTNER_ID', 'SandboxSiigoAPI')
            user = os.getenv('SIIGO_USER')
            
            if not access_key:
                raise ValueError("SIIGO_ACCESS_KEY no encontrado en archivo .env")
            
            if not user:
                raise ValueError("SIIGO_USER no encontrado en archivo .env")
            
            self.log_message("🔐 Iniciando autenticación con Siigo API...")
            
            # PASO 1: Obtener access_token mediante OAuth
            auth_url = f"{api_url}/auth"
            
            # Headers para autenticación
            auth_headers = {
                'Content-Type': 'application/json',
                'Partner-Id': partner_id
            }
            
            # Payload para obtener token - CORREGIDO: usar access_key directamente
            auth_payload = {
                'username': user,  # Email del usuario
                'access_key': access_key  # Usar access_key directamente (NO decodificar)
            }
            
            self.log_message(f"📡 POST {auth_url} - Obteniendo access_token...")
            
            # Realizar petición de autenticación
            auth_response = requests.post(
                auth_url, 
                json=auth_payload, 
                headers=auth_headers, 
                timeout=15
            )
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                access_token = auth_data.get('access_token')
                
                if not access_token:
                    raise ValueError("No se recibió access_token en la respuesta de autenticación")
                
                self.log_message(f"✅ Access token obtenido exitosamente")
                
                # PASO 2: Descargar facturas usando el token
                invoices_url = f"{api_url}/v1/invoices"
                
                # Headers para consulta de facturas
                invoice_headers = {
                    'Authorization': access_token,
                    'Content-Type': 'application/json',
                    'Partner-Id': partner_id
                }
                
                # Construcción de parámetros de consulta
                params = {}
                
                if fecha_inicio:
                    params['created_start'] = fecha_inicio
                    
                if fecha_fin:
                    params['created_end'] = fecha_fin
                    
                if cliente_id:
                    params['customer_id'] = cliente_id
                    
                if cc:
                    params['customer_identification'] = cc
                    
                if nit:
                    params['customer_identification'] = nit  # NIT también va en customer_identification
                    
                if estado:
                    params['status'] = estado
                
                self.log_message(f"📡 GET {invoices_url} - Descargando facturas...")
                self.log_message(f"📋 Parámetros: {params}")
                
                # Realizar consulta de facturas
                invoices_response = requests.get(
                    invoices_url,
                    headers=invoice_headers,
                    params=params,
                    timeout=120  # Aumentar timeout a 2 minutos para rangos grandes
                )
                
                if invoices_response.status_code == 200:
                    response_data = invoices_response.json()
                    
                    # La respuesta puede ser una lista directa o un objeto con 'results'
                    if isinstance(response_data, dict):
                        facturas_data = response_data.get('results', [])
                    else:
                        facturas_data = response_data
                    
                    if not facturas_data or len(facturas_data) == 0:
                        self.log_message("⚠️ No se encontraron facturas con los filtros especificados")
                        return pd.DataFrame(), pd.DataFrame()
                    
                    self.log_message(f"📊 Procesando {len(facturas_data)} facturas encontradas...")
                    
                    # Procesar datos en DataFrames
                    encabezados_list = []
                    detalle_list = []
                    
                    for factura in facturas_data:
                        try:
                            # Validar que cada factura sea un diccionario
                            if not isinstance(factura, dict):
                                self.log_message(f"⚠️ Factura no es diccionario: {type(factura)}")
                                continue
                                
                            # Datos del encabezado con validación
                            customer_data = factura.get('customer', {})
                            if not isinstance(customer_data, dict):
                                customer_data = {}
                                
                            # Función auxiliar para convertir valores de API
                            def safe_float(value, default=0.0):
                                """Convertir valor a float de forma segura."""
                                if isinstance(value, (list, dict)):
                                    if isinstance(value, list) and len(value) > 0:
                                        return float(value[0]) if str(value[0]).replace('.','').replace('-','').isdigit() else default
                                    return default
                                try:
                                    return float(value) if value is not None else default
                                except (ValueError, TypeError):
                                    return default
                            
                            def safe_str(value, default=''):
                                """Convertir valor a string de forma segura."""
                                if isinstance(value, list):
                                    return str(value[0]) if len(value) > 0 else default
                                return str(value) if value is not None else default
                                
                            encabezado = {
                                'factura_id': safe_str(factura.get('id', '')),
                                'numero': safe_str(factura.get('number', '')),
                                'fecha': safe_str(factura.get('date', '')),
                                'fecha_vencimiento': safe_str(factura.get('due_date', '')),
                                'cliente_id': safe_str(customer_data.get('id', '')),
                                'cliente_nombre': safe_str(customer_data.get('name', 'Cliente Sin Nombre')),
                                'cliente_nit': safe_str(customer_data.get('identification', '')),
                                'subtotal': safe_float(factura.get('subtotal', 0)),
                                'impuestos': safe_float(factura.get('taxes', 0)),
                                'total': safe_float(factura.get('total', 0)),
                                'estado': safe_str(factura.get('status', '')),
                                'moneda': safe_str(factura.get('currency', 'COP')),
                                'observaciones': safe_str(factura.get('observations', ''))
                            }
                            encabezados_list.append(encabezado)
                            
                            # Datos del detalle (items) con validación
                            items = factura.get('items', [])
                            if not isinstance(items, list):
                                items = []
                                
                            for item in items:
                                if not isinstance(item, dict):
                                    continue
                                    
                                detalle_item = {
                                    'factura_id': safe_str(factura.get('id', '')),
                                    'numero_factura': safe_str(factura.get('number', '')),
                                    'item_id': safe_str(item.get('id', '')),
                                    'codigo': safe_str(item.get('code', '')),
                                    'descripcion': safe_str(item.get('description', '')),
                                    'cantidad': safe_float(item.get('quantity', 0)),
                                    'precio_unitario': safe_float(item.get('price', 0)),
                                    'subtotal_item': safe_float(item.get('subtotal', 0)),
                                    'impuestos_item': safe_float(item.get('taxes', 0)),
                                    'total_item': safe_float(item.get('total', 0))
                                }
                                detalle_list.append(detalle_item)
                                
                        except Exception as e:
                            self.log_message(f"⚠️ Error procesando factura {factura.get('id', 'N/A')}: {e}")
                            continue
                    
                    # Crear DataFrames
                    encabezados_df = pd.DataFrame(encabezados_list)
                    detalle_df = pd.DataFrame(detalle_list)
                    
                    self.log_message(f"✅ Descarga exitosa: {len(encabezados_df)} facturas, {len(detalle_df)} items")
                    
                    return encabezados_df, detalle_df
                    
                else:
                    error_msg = f"Error {invoices_response.status_code}: {invoices_response.text}"
                    self.log_message(f"❌ Error consultando facturas: {error_msg}")
                    QMessageBox.critical(self, "Error API", f"Error consultando facturas:\n{error_msg}")
                    return None, None
                    
            elif auth_response.status_code == 429:
                error_data = auth_response.json()
                error_msg = error_data.get('Errors', [{}])[0].get('Message', 'Rate limit exceeded')
                self.log_message(f"⏰ Rate limit excedido: {error_msg}")
                QMessageBox.warning(self, "Rate Limit", f"Rate limit excedido:\n{error_msg}")
                return None, None
                
            else:
                error_msg = f"Error {auth_response.status_code}: {auth_response.text}"
                self.log_message(f"❌ Error autenticación: {error_msg}")
                QMessageBox.critical(self, "Error Autenticación", f"Error de autenticación:\n{error_msg}")
                return None, None
                
        except Exception as e:
            self.log_message(f"❌ Error descargando facturas: {e}")
            QMessageBox.critical(self, "Error", f"Error descargando facturas:\n{e}")
            return None, None
    
    def export_siigo_csv_with_filters(self):
        """Exportar facturas de Siigo API a CSV usando los filtros de la interfaz."""
        fecha_inicio = self.get_date_start()
        fecha_fin = self.get_date_end()
        cliente_id = self.get_client_id() or None
        nit = self.get_nit() or None
        estado = self.get_status() or None
        
        self.log_message(f"🔄 Exportando CSV Siigo - Filtros: {fecha_inicio} a {fecha_fin}")
        
        # Verificar si el rango es muy amplio (más de 3 meses)
        if self._is_date_range_too_large(fecha_inicio, fecha_fin):
            reply = QMessageBox.question(
                self,
                "Rango de Fechas Amplio",
                f"El rango de fechas es muy amplio ({fecha_inicio} a {fecha_fin}).\n\n"
                f"Para evitar timeouts, se procesará en chunks mensuales.\n\n"
                f"¿Desea continuar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return
                
            self.export_siigo_invoices_to_csv_chunked(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                cliente_id=cliente_id,
                nit=nit,
                estado=estado
            )
        else:
            self.export_siigo_invoices_to_csv(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                cliente_id=cliente_id,
                nit=nit,
                estado=estado
            )
    
    def export_siigo_invoices_to_csv(self, fecha_inicio=None, fecha_fin=None,
                                    cliente_id=None, cc=None, nit=None, estado=None):
        """
        Descargar facturas de Siigo API y exportar a archivos CSV.
        
        Args:
            fecha_inicio (str): Fecha inicio YYYY-MM-DD
            fecha_fin (str): Fecha fin YYYY-MM-DD
            cliente_id (str): ID del cliente
            cc (str): Cédula del cliente  
            nit (str): NIT del cliente
            estado (str): Estado (abierta, cerrada, anulada)
        """
        try:
            self.log_message("🚀 Iniciando exportación de facturas Siigo a CSV...")
            
            # Descargar facturas
            encabezados_df, detalle_df = self.download_invoices(
                fecha_inicio, fecha_fin, cliente_id, cc, nit, estado
            )
            
            if encabezados_df is None or detalle_df is None:
                return
            
            if len(encabezados_df) == 0:
                QMessageBox.information(
                    self, 
                    "Sin Resultados", 
                    "No se encontraron facturas con los filtros especificados."
                )
                return
            
            # Crear archivos CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("outputs", exist_ok=True)
            
            encabezados_file = f"outputs/facturas_encabezados_siigo_{timestamp}.csv"
            detalle_file = f"outputs/facturas_detalle_siigo_{timestamp}.csv"
            
            # Escribir CSVs
            encabezados_df.to_csv(encabezados_file, index=False, encoding='utf-8')
            detalle_df.to_csv(detalle_file, index=False, encoding='utf-8')
            
            # Calcular tamaños
            enc_size = os.path.getsize(encabezados_file) / 1024
            det_size = os.path.getsize(detalle_file) / 1024
            
            self.log_message(f"✅ CSVs generados: {os.path.basename(encabezados_file)} ({enc_size:.1f} KB), {os.path.basename(detalle_file)} ({det_size:.1f} KB)")
            
            QMessageBox.information(
                self,
                "✅ Exportación CSV Exitosa",
                f"Facturas de Siigo API exportadas a CSV:\n\n"
                f"📊 Encabezados: {len(encabezados_df)} facturas\n"
                f"📋 Detalle: {len(detalle_df)} items\n\n" 
                f"📁 Archivos generados:\n"
                f"• {os.path.basename(encabezados_file)} ({enc_size:.1f} KB)\n"
                f"• {os.path.basename(detalle_file)} ({det_size:.1f} KB)\n\n"
                f"✅ Datos reales desde API Siigo"
            )
            
        except Exception as e:
            self.log_message(f"❌ Error en exportación CSV: {e}")
            QMessageBox.critical(self, "Error", f"Error en exportación CSV:\n{e}")
    
    def _is_date_range_too_large(self, fecha_inicio: str, fecha_fin: str) -> bool:
        """Verificar si el rango de fechas es demasiado amplio (más de 3 meses)."""
        try:
            from datetime import datetime
            start_date = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            end_date = datetime.strptime(fecha_fin, "%Y-%m-%d")
            diff_days = (end_date - start_date).days
            return diff_days > 90  # Más de 3 meses
        except:
            return False
    
    def _generate_date_chunks(self, fecha_inicio: str, fecha_fin: str):
        """Generar chunks mensuales para procesar rangos grandes."""
        from datetime import datetime, timedelta
        import calendar
        
        start_date = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        end_date = datetime.strptime(fecha_fin, "%Y-%m-%d")
        
        chunks = []
        current_date = start_date
        
        while current_date < end_date:
            # Calcular fin del mes actual
            year = current_date.year
            month = current_date.month
            last_day = calendar.monthrange(year, month)[1]
            month_end = datetime(year, month, last_day)
            
            # Usar el menor entre fin de mes y fecha final
            chunk_end = min(month_end, end_date)
            
            chunks.append((
                current_date.strftime("%Y-%m-%d"),
                chunk_end.strftime("%Y-%m-%d")
            ))
            
            # Mover al primer día del siguiente mes
            if month == 12:
                current_date = datetime(year + 1, 1, 1)
            else:
                current_date = datetime(year, month + 1, 1)
        
        return chunks
    
    def export_siigo_invoices_to_csv_chunked(self, fecha_inicio=None, fecha_fin=None,
                                            cliente_id=None, cc=None, nit=None, estado=None):
        """
        Exportar facturas procesando en chunks para rangos grandes.
        """
        try:
            self.log_message("🚀 Iniciando exportación CSV por chunks para rango amplio...")
            
            # Generar chunks mensuales
            chunks = self._generate_date_chunks(fecha_inicio, fecha_fin)
            self.log_message(f"📊 Se procesarán {len(chunks)} períodos mensuales")
            
            all_encabezados = []
            all_detalle = []
            total_facturas = 0
            
            # Procesar cada chunk
            for i, (chunk_start, chunk_end) in enumerate(chunks, 1):
                self.log_message(f"🔄 Procesando período {i}/{len(chunks)}: {chunk_start} a {chunk_end}")
                
                try:
                    # Descargar facturas del chunk
                    encabezados_df, detalle_df = self.download_invoices(
                        chunk_start, chunk_end, cliente_id, cc, nit, estado
                    )
                    
                    if encabezados_df is not None and len(encabezados_df) > 0:
                        all_encabezados.append(encabezados_df)
                        all_detalle.append(detalle_df)
                        total_facturas += len(encabezados_df)
                        self.log_message(f"✅ Período {i}: {len(encabezados_df)} facturas procesadas")
                    else:
                        self.log_message(f"⚠️ Período {i}: Sin facturas")
                    
                    # Pequeña pausa entre requests para no sobrecargar la API
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    self.log_message(f"❌ Error en período {i} ({chunk_start} - {chunk_end}): {e}")
                    continue
            
            if not all_encabezados:
                QMessageBox.information(
                    self, 
                    "Sin Resultados", 
                    "No se encontraron facturas en ningún período del rango especificado."
                )
                return
            
            # Combinar todos los DataFrames
            import pandas as pd
            combined_encabezados = pd.concat(all_encabezados, ignore_index=True)
            combined_detalle = pd.concat(all_detalle, ignore_index=True)
            
            # Crear archivos CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("outputs", exist_ok=True)
            
            encabezados_file = f"outputs/facturas_encabezados_siigo_{timestamp}.csv"
            detalle_file = f"outputs/facturas_detalle_siigo_{timestamp}.csv"
            
            # Escribir CSVs
            combined_encabezados.to_csv(encabezados_file, index=False, encoding='utf-8')
            combined_detalle.to_csv(detalle_file, index=False, encoding='utf-8')
            
            # Calcular tamaños
            enc_size = os.path.getsize(encabezados_file) / 1024
            det_size = os.path.getsize(detalle_file) / 1024
            
            self.log_message(f"✅ CSVs generados: {os.path.basename(encabezados_file)} ({enc_size:.1f} KB), {os.path.basename(detalle_file)} ({det_size:.1f} KB)")
            
            QMessageBox.information(
                self,
                "✅ Exportación CSV Exitosa (Procesamiento por Chunks)",
                f"Facturas de Siigo API exportadas a CSV:\n\n"
                f"📊 Total encabezados: {len(combined_encabezados)} facturas\n"
                f"📋 Total detalle: {len(combined_detalle)} items\n"
                f"⏱️ Períodos procesados: {len(chunks)}\n\n" 
                f"📁 Archivos generados:\n"
                f"• {os.path.basename(encabezados_file)} ({enc_size:.1f} KB)\n"
                f"• {os.path.basename(detalle_file)} ({det_size:.1f} KB)\n\n"
                f"✅ Datos reales desde API Siigo\n"
                f"🚀 Procesamiento optimizado para rangos amplios"
            )
            
        except Exception as e:
            self.log_message(f"❌ Error en exportación CSV por chunks: {e}")
            QMessageBox.critical(self, "Error", f"Error en exportación CSV por chunks:\n{e}")
    
    def export_siigo_invoices_to_excel_chunked(self, fecha_inicio=None, fecha_fin=None,
                                              cliente_id=None, cc=None, nit=None, estado=None):
        """
        Exportar facturas a Excel procesando en chunks para rangos grandes.
        """
        try:
            self.log_message("🚀 Iniciando exportación Excel por chunks para rango amplio...")
            
            # Generar chunks mensuales
            chunks = self._generate_date_chunks(fecha_inicio, fecha_fin)
            self.log_message(f"📊 Se procesarán {len(chunks)} períodos mensuales")
            
            all_encabezados = []
            all_detalle = []
            total_facturas = 0
            
            # Procesar cada chunk
            for i, (chunk_start, chunk_end) in enumerate(chunks, 1):
                self.log_message(f"🔄 Procesando período {i}/{len(chunks)}: {chunk_start} a {chunk_end}")
                
                try:
                    # Descargar facturas del chunk
                    encabezados_df, detalle_df = self.download_invoices(
                        chunk_start, chunk_end, cliente_id, cc, nit, estado
                    )
                    
                    if encabezados_df is not None and len(encabezados_df) > 0:
                        all_encabezados.append(encabezados_df)
                        all_detalle.append(detalle_df)
                        total_facturas += len(encabezados_df)
                        self.log_message(f"✅ Período {i}: {len(encabezados_df)} facturas procesadas")
                    else:
                        self.log_message(f"⚠️ Período {i}: Sin facturas")
                    
                    # Pequeña pausa entre requests para no sobrecargar la API
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    self.log_message(f"❌ Error en período {i} ({chunk_start} - {chunk_end}): {e}")
                    continue
            
            if not all_encabezados:
                QMessageBox.information(
                    self, 
                    "Sin Resultados", 
                    "No se encontraron facturas en ningún período del rango especificado."
                )
                return
            
            # Combinar todos los DataFrames
            import pandas as pd
            combined_encabezados = pd.concat(all_encabezados, ignore_index=True)
            combined_detalle = pd.concat(all_detalle, ignore_index=True)
            
            # Crear archivo Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("outputs", exist_ok=True)
            excel_file = f"outputs/facturas_siigo_{timestamp}.xlsx"
            
            # Escribir Excel con dos hojas
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                combined_encabezados.to_excel(writer, sheet_name='Encabezados', index=False)
                combined_detalle.to_excel(writer, sheet_name='Detalle', index=False)
            
            # Calcular tamaño
            excel_size = os.path.getsize(excel_file) / 1024
            
            self.log_message(f"✅ Excel generado: {os.path.basename(excel_file)} ({excel_size:.1f} KB)")
            
            QMessageBox.information(
                self,
                "✅ Exportación Excel Exitosa (Procesamiento por Chunks)",
                f"Facturas de Siigo API exportadas a Excel:\n\n"
                f"📊 Total encabezados: {len(combined_encabezados)} facturas\n"
                f"📋 Total detalle: {len(combined_detalle)} items\n"
                f"⏱️ Períodos procesados: {len(chunks)}\n\n" 
                f"📁 Archivo generado:\n"
                f"• {os.path.basename(excel_file)} ({excel_size:.1f} KB)\n\n"
                f"✅ Datos reales desde API Siigo\n"
                f"🚀 Procesamiento optimizado para rangos amplios"
            )
            
        except Exception as e:
            self.log_message(f"❌ Error en exportación Excel por chunks: {e}")
            QMessageBox.critical(self, "Error", f"Error en exportación Excel por chunks:\n{e}")
    
    def log_message(self, message: str):
        """Log message (placeholder - debe ser conectado al sistema de logs)."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    # ==================== Métodos de UI ====================
    
    def show_success_message(self, title: str, message: str):
        """Mostrar mensaje de éxito."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)
    
    def show_error_message(self, title: str, message: str):
        """Mostrar mensaje de error."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, title, message)
    
    def clear_filters(self):
        """Limpiar todos los filtros."""
        if self.siigo_date_start:
            self.siigo_date_start.setDate(datetime.now().date().replace(day=1))
        if self.siigo_date_end:
            self.siigo_date_end.setDate(datetime.now().date())
        if self.siigo_client_id:
            self.siigo_client_id.clear()
        if self.siigo_nit:
            self.siigo_nit.clear()
        if self.siigo_status:
            self.siigo_status.setCurrentIndex(0)  # "Todos"