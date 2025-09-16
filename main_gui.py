#!/usr/bin/env python3
"""
DATACONTA - Punto de entrada GUI
Aplicación principal con interfaz gráfica PySide6.
Mantiene arquitectura hexagonal y principios SOLID.
"""

import sys
import os
import logging
from typing import Optional
from pathlib import Path

# Agregar el directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Importaciones condicionales para PySide6
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("⚠️  PySide6 no está instalado. Instale con: pip install PySide6")
    print("📋 Ejecutando en modo consola...")

# Financial Reports Integration
from src.infrastructure.factories.financial_reports_factory import FinancialReportsFactory
from src.presentation.financial_reports_integration import FinancialReportsIntegration


class DataContaGUIApplication:
    """
    Aplicación principal GUI para DATACONTA.
    Coordina la inicialización de todos los componentes manteniendo arquitectura hexagonal.
    """
    
    def __init__(self):
        """Inicializar la aplicación GUI"""
        self.app: Optional[QApplication] = None
        self.main_window = None
        self.ui_controller = None
        self.business_adapter = None
        self.menu_adapter = None
        
        # Configurar logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Verificar PySide6
        if not PYSIDE6_AVAILABLE:
            self.logger.error("PySide6 no disponible - no se puede iniciar GUI")
            raise ImportError("PySide6 es requerido para la interfaz gráfica")
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        import sys
        
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Configurar handlers con codificación UTF-8 para evitar problemas con emojis
        file_handler = logging.FileHandler('app.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Para consola, usar handler que maneje encoding mejor en Windows
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Configurar logger raíz
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler]
        )
    
    def initialize(self) -> bool:
        """Inicializar todos los componentes de la aplicación"""
        try:
            self.logger.info("*** Iniciando DATACONTA GUI...")
            
            # 1. Inicializar QApplication
            if not self._init_qt_application():
                return False
            
            # 2. Configurar entorno
            if not self._setup_environment():
                return False
            
            # 3. Inicializar componentes de infraestructura
            if not self._init_infrastructure_components():
                return False
            
            # 4. Inicializar componentes de aplicación
            if not self._init_application_components():
                return False
            
            # 5. Configurar UI
            if not self._setup_ui_components():
                return False
            
            # 6. Configurar menú y acciones
            if not self._setup_menu_system():
                return False
            
            self.logger.info("*** DATACONTA GUI inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"*** Error inicializando aplicación GUI: {e}")
            return False
    
    def _init_qt_application(self) -> bool:
        """Inicializar QApplication"""
        try:
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("DATACONTA")
            self.app.setApplicationVersion("2.0.0")
            self.app.setOrganizationName("DATACONTA Systems")
            
            # Configurar estilo de la aplicación
            self.app.setStyle("Fusion")
            
            # Configurar icono si existe
            icon_path = ROOT_DIR / "assets" / "dataconta_icon.png"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
            
            self.logger.info("Qt Application inicializada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando Qt Application: {e}")
            return False
    
    def _setup_environment(self) -> bool:
        """Configurar variables de entorno"""
        try:
            from dotenv import load_dotenv
            
            # Cargar configuración de entorno directamente
            load_dotenv()
            
            self.logger.info("Configuración de entorno cargada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configurando entorno: {e}")
            return False
    
    def _init_infrastructure_components(self) -> bool:
        """Inicializar componentes de infraestructura"""
        try:
            # Importar adapters de infraestructura
            from src.infrastructure.adapters.logger_adapter import LoggerAdapter
            from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter
            from src.infrastructure.adapters.license_validator_adapter import LicenseValidatorAdapter
            from src.infrastructure.adapters.file_storage_adapter import FileStorageAdapter
            from src.infrastructure.adapters.csv_file_adapter import CSVFileAdapter
            
            # Inicializar adapters
            self.logger_adapter = LoggerAdapter("DATACONTA_GUI")
            
            # Crear proveedor de configuración
            from src.infrastructure.config.environment_config import EnvironmentConfigurationProvider
            self._config = EnvironmentConfigurationProvider(self.logger_adapter)
            
            self.siigo_api = SiigoAPIAdapter(self.logger_adapter)
            
            # Autenticar automáticamente con Siigo API usando credenciales de configuración
            self.logger_adapter.info("Attempting authentication with Siigo API")
            credentials = self._config.get_api_credentials()
            if credentials and credentials.is_valid():
                auth_result = self.siigo_api.authenticate(credentials)
                if auth_result:
                    self.logger_adapter.info("Authentication successful")
                    self.logger_adapter.info("Successfully authenticated with Siigo API")
                else:
                    self.logger_adapter.warning("Authentication failed - continuing without API access")
            else:
                self.logger_adapter.warning("Invalid or missing API credentials - continuing without API access")
            
            self.license_validator = LicenseValidatorAdapter(
                license_url=self._config.get_license_url(),
                logger=self.logger_adapter
            )
            self.file_storage = FileStorageAdapter(
                output_directory=self._config.get_output_directory(),
                logger=self.logger_adapter
            )
            self.csv_adapter = CSVFileAdapter(self.logger_adapter)
            
            self.logger.info("Componentes de infraestructura inicializados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando infraestructura: {e}")
            return False
    
    def _init_application_components(self) -> bool:
        """Inicializar componentes de aplicación (casos de uso)"""
        try:
            # Importar casos de uso y servicios
            from src.application.use_cases.wrapper import InvoiceUseCases
            from src.application.services.InvoiceExportService import InvoiceExportService
            from src.application.services.BIExportService import BIExportService
            
            # Crear servicios primero
            self.invoice_export_service = InvoiceExportService(
                logger=self.logger_adapter
            )
            
            self.bi_export_service = BIExportService(
                logger=self.logger_adapter
            )
            
            # Crear casos de uso con inyección de dependencias
            self.invoice_use_cases = InvoiceUseCases(
                invoice_repository=self.siigo_api,
                license_validator=self.license_validator,
                file_storage=self.file_storage,
                logger=self.logger_adapter,
                user_interface=None,  # Se asignará después
                invoice_processor=self.invoice_export_service,
                csv_exporter=self.csv_adapter,
                bi_export_service=self.bi_export_service
            )
            
            # Crear sistema de informes financieros
            self.logger.info("Creando servicio de informes financieros")
            factory = FinancialReportsFactory(
                logger=self.logger_adapter,
                file_storage=self.file_storage,
                api_client=self.siigo_api,
                config_provider=self._config
            )
            financial_service = factory.create_financial_reports_service()
            
            self.financial_integration = FinancialReportsIntegration(
                financial_reports_service=financial_service,
                logger=self.logger_adapter
            )
            self.logger.info("Servicio de informes financieros creado exitosamente")
            
            self.logger.info("Componentes de aplicación inicializados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando componentes de aplicación: {e}")
            return False
    
    def _setup_ui_components(self) -> bool:
        """Configurar componentes de UI"""
        try:
            # Importar componentes de UI
            from src.presentation.gui_interface import DataContaMainWindow, GUIUserInterfaceAdapter
            
            # Crear interfaz de usuario GUI
            self.gui_interface = GUIUserInterfaceAdapter(self.logger_adapter)
            
            # Crear ventana principal
            self.main_window = DataContaMainWindow(self.logger_adapter)
            
            # Conectar la interfaz con la ventana
            self.gui_interface.set_main_window(self.main_window)
            
            # Asignar la interfaz de usuario a los casos de uso
            self.invoice_use_cases.get_invoices._user_interface = self.gui_interface
            
            # Actualizar estado de la licencia
            self._update_license_display()
            
            self.logger.info("Componentes de UI configurados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configurando UI: {e}")
            return False
    
    def _setup_menu_system(self) -> bool:
        """Configurar sistema de menús"""
        try:
            # Conectar botones de la interfaz con las funciones
            self._connect_ui_signals()
            
            self.logger.info("Sistema de menús configurado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configurando menús: {e}")
            return False
    
    def _connect_ui_signals(self):
        """Conectar señales de la interfaz con las acciones correspondientes."""
        if self.main_window:
            # Business Intelligence
            self.main_window.get_invoices_btn.clicked.connect(self._on_get_invoices)
            self.main_window.export_bi_btn.clicked.connect(self._on_export_bi)
            
            # Reports
            self.main_window.financial_reports_btn.clicked.connect(self._on_financial_reports)
            self.main_window.balance_general_btn.clicked.connect(self._on_balance_general)
            self.main_window.operational_reports_btn.clicked.connect(self._on_operational_reports)
            self.main_window.compliance_reports_btn.clicked.connect(self._on_compliance_reports)
            self.main_window.management_reports_btn.clicked.connect(self._on_management_reports)
            self.main_window.view_files_btn.clicked.connect(self._on_view_files)
            self.main_window.export_csv_btn.clicked.connect(self._on_export_csv)
            
            # Tools
            self.main_window.check_api_btn.clicked.connect(self._on_check_api)
            self.main_window.config_btn.clicked.connect(self._on_show_config)
            
            # Ollama
            self.main_window.send_ollama_btn.clicked.connect(self._on_send_ollama)
            self.main_window.query_ollama_btn.clicked.connect(self._on_query_ollama)
            
            # Exit
            self.main_window.exit_btn.clicked.connect(self._on_exit)
    
    def _on_get_invoices(self):
        """Manejar acción de obtener facturas."""
        try:
            self.main_window.log_message("📋 Consultando facturas de venta...")
            self.main_window.show_progress(True)
            
            # Crear petición con parámetros por defecto
            from src.application.use_cases.invoice_use_cases import GetInvoicesRequest
            request = GetInvoicesRequest(
                document_id=None,
                created_start=None,
                created_end=None
            )
            
            # Ejecutar caso de uso
            license_key = self._config.get_license_key()
            result = self.invoice_use_cases.get_invoices.execute(request, license_key)
            
            if result.success:
                self.main_window.log_message(f"✅ {result.message}")
                self.main_window.log_message(f"📊 Total de facturas obtenidas: {result.total_count}")
                
                # Mostrar las primeras facturas
                if result.invoices:
                    self.main_window.log_message("📄 Primeras facturas:")
                    for i, invoice in enumerate(result.invoices[:5], 1):
                        customer = "N/A"
                        if invoice.customer and invoice.customer.name:
                            customer = " ".join(invoice.customer.name)
                        
                        total = invoice.calculate_total() if invoice.items else (invoice.total or 0)
                        self.main_window.log_message(f"  {i}. #{invoice.number} - {customer} - ${total:,.2f}")
                    
                    if len(result.invoices) > 5:
                        self.main_window.log_message(f"  ... y {len(result.invoices) - 5} facturas más")
                
            else:
                self.main_window.log_message(f"❌ Error: {result.message}")
                self.main_window.show_error("Error", result.message)
            
            self.main_window.show_progress(False)
            
        except Exception as e:
            self.main_window.show_progress(False)
            self.logger.error(f"Error en consulta de facturas: {e}")
            self.main_window.log_message(f"❌ Error inesperado: {str(e)}")
            self.main_window.show_error("Error", f"Error obteniendo facturas: {e}")
    
    def _on_export_bi(self):
        """Manejar acción de exportar a BI."""
        try:
            self.main_window.log_message("🏢 Iniciando exportación a Business Intelligence...")
            self.main_window.show_progress(True)
            
            # Crear petición
            from src.application.use_cases.invoice_use_cases import ExportToBIRequest
            request = ExportToBIRequest(
                start_date=None,
                end_date=None,
                max_records=100,
                validate_schema=False
            )
            
            self.main_window.log_message("📊 Procesando facturas y generando modelo estrella...")
            
            # Ejecutar caso de uso
            license_key = self._config.get_license_key()
            result = self.invoice_use_cases.export_to_bi.execute(request, license_key)
            
            if result.success:
                stats = result.statistics
                files = result.files_created
                
                success_files = [filename for filename, success in files.items() if success]
                
                self.main_window.log_message("✅ Exportación BI exitosa!")
                self.main_window.log_message(f"📊 Facturas procesadas: {stats.get('facts_count', 0)}")
                self.main_window.log_message(f"👥 Clientes únicos: {stats.get('clients_count', 0)}")
                self.main_window.log_message(f"🏪 Vendedores únicos: {stats.get('sellers_count', 0)}")
                self.main_window.log_message(f"📦 Productos únicos: {stats.get('products_count', 0)}")
                
                self.main_window.log_message("📁 Archivos creados:")
                for filename in success_files:
                    self.main_window.log_message(f"   ✓ {filename}")
                
                self.main_window.show_info("Exportación Completada", f"Se crearon {len(success_files)} archivos BI exitosamente")
            else:
                self.main_window.log_message(f"❌ Error en exportación BI: {result.message}")
                self.main_window.show_error("Error BI", result.message)
            
            self.main_window.show_progress(False)
            
        except Exception as e:
            self.main_window.show_progress(False)
            self.logger.error(f"Error en exportación BI: {e}")
            self.main_window.log_message(f"❌ Error inesperado: {str(e)}")
            self.main_window.show_error("Error", f"Error exportando a BI: {e}")
    
    def _on_export_csv(self):
        """Manejar exportación a CSV."""
        try:
            self.main_window.log_message("📤 Iniciando exportación a CSV...")
            self.main_window.show_progress(True)
            
            # Crear petición
            from src.application.use_cases.invoice_use_cases import ExportInvoicesFromAPIToCSVRequest
            request = ExportInvoicesFromAPIToCSVRequest(
                start_date=None,
                end_date=None,
                max_records=100,
                custom_filename=None
            )
            
            # Ejecutar caso de uso
            license_key = self._config.get_license_key()
            result = self.invoice_use_cases.export_from_api_to_csv.execute(request, license_key)
            
            if result.success:
                self.main_window.log_message(f"✅ {result.message}")
                self.main_window.log_message(f"📊 Facturas exportadas: {result.exported_count}")
                self.main_window.log_message(f"📁 Archivo: {result.filename}")
                self.main_window.show_info("Exportación Completada", f"Archivo CSV creado: {result.filename}")
            else:
                self.main_window.log_message(f"❌ Error: {result.message}")
                self.main_window.show_error("Error CSV", result.message)
                
            self.main_window.show_progress(False)
            
        except Exception as e:
            self.main_window.show_progress(False)
            self.logger.error(f"Error en exportación CSV: {e}")
            self.main_window.log_message(f"❌ Error inesperado: {str(e)}")
            self.main_window.show_error("Error", f"Error exportando CSV: {e}")
    
    def _on_view_files(self):
        """Manejar visualización de archivos."""
        try:
            self.main_window.log_message("📁 Consultando archivos de salida...")
            
            # Usar el caso de uso correspondiente
            license_key = self._config.get_license_key()
            result = self.invoice_use_cases.view_files.execute(license_key)
            
            if result.success:
                if result.files:
                    self.main_window.log_message(f"📂 Encontrados {len(result.files)} archivos:")
                    for file in result.files:
                        self.main_window.log_message(f"   📄 {file}")
                else:
                    self.main_window.log_message("📭 No hay archivos en la carpeta de salida")
            else:
                self.main_window.log_message(f"❌ Error: {result.message}")
                
        except Exception as e:
            self.logger.error(f"Error visualizando archivos: {e}")
            self.main_window.log_message(f"❌ Error: {str(e)}")
    
    def _on_check_api(self):
        """Verificar estado de la API."""
        try:
            self.main_window.log_message("🔍 Verificando estado de la API...")
            
            # Usar el caso de uso correspondiente
            license_key = self._config.get_license_key()
            result = self.invoice_use_cases.check_api_status.execute(license_key)
            
            if result.success:
                self.main_window.log_message("✅ API de Siigo: Disponible")
                self.main_window.log_message("✅ Licencia: Válida")
                self.main_window.log_message(f"💬 {result.message}")
            else:
                self.main_window.log_message("❌ Problemas con la API o licencia")
                self.main_window.log_message(f"💬 {result.message}")
                
        except Exception as e:
            self.logger.error(f"Error verificando API: {e}")
            self.main_window.log_message(f"❌ Error verificando API: {str(e)}")
    
    def _on_show_config(self):
        """Mostrar configuración del sistema."""
        self.main_window.log_message("⚙️ Configuración del Sistema:")
        self.main_window.log_message(f"📁 Directorio de salida: {self._config.get_output_directory()}")
        self.main_window.log_message(f"🔗 URL de licencia: {self._config.get_license_url()}")
        self.main_window.log_message(f"🌐 Usuario API: {self._config.get_api_credentials().username}")
    
    def _on_financial_reports(self):
        """Generar Estado de Resultados con selección de períodos."""
        try:
            self.main_window.log_message("💰 Estado de Resultados - Selección de Períodos")
            
            if not hasattr(self, 'financial_integration') or not self.financial_integration:
                self.main_window.log_message("❌ Sistema de informes financieros no disponible")
                return
            
            # Obtener períodos sugeridos
            periodos = self.financial_integration._service.get_tipos_periodo_sugeridos()
            
            if not periodos:
                self.main_window.log_message("❌ No hay períodos disponibles")
                return
            
            # Mostrar diálogo de selección de período
            periodo_seleccionado = self._mostrar_dialogo_seleccion_periodo(periodos)
            
            if periodo_seleccionado:
                fecha_inicio = periodo_seleccionado['fecha_inicio']
                fecha_fin = periodo_seleccionado['fecha_fin']
                
                self.main_window.log_message(f"💰 Estado de Resultados - {periodo_seleccionado['nombre']}")
                self.main_window.log_message(f"� Período: {fecha_inicio} - {fecha_fin}")
                
                # Generar el informe
                result = self.financial_integration._service.generar_estado_resultados(
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    formato_salida='json',
                    incluir_kpis=True
                )
                
                if result.success and result.data and "estado_resultados" in result.data:
                    estado = result.data["estado_resultados"]
                    self.main_window.log_message("✅ Estado de Resultados generado exitosamente")
                    self.main_window.log_message(f"💰 Ventas Netas: ${estado['ventas_netas']:,.2f}")
                    self.main_window.log_message(f"💸 Costo de Ventas: ${estado['costo_ventas']:,.2f}")
                    self.main_window.log_message(f"💵 Utilidad Bruta: ${estado['utilidad_bruta']:,.2f}")
                    self.main_window.log_message(f"💎 Utilidad Neta: ${estado['utilidad_neta']:,.2f}")
                    self.main_window.log_message(f"📈 Margen Neto: {estado['margen_neto_porcentaje']:.2f}%")
                    if result.file_path:
                        self.main_window.log_message(f"📄 Guardado: {result.file_path}")
                else:
                    self.main_window.log_message("❌ Error al generar el informe")
            else:
                self.main_window.log_message("❌ Selección de período cancelada")
                    
        except Exception as e:
            self.logger.error(f"Error en Estado de Resultados: {e}")
            self.main_window.log_message(f"❌ Error: {str(e)}")

    def _mostrar_dialogo_seleccion_periodo(self, periodos):
        """Mostrar diálogo para seleccionar período de tiempo."""
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                       QPushButton, QListWidget, QListWidgetItem, 
                                       QLabel)
        from PySide6.QtCore import Qt
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Seleccionar Período - Estado de Resultados")
        dialog.setMinimumSize(500, 400)
        dialog.setModal(True)
        
        # Layout principal
        layout = QVBoxLayout(dialog)
        
        # Título
        titulo = QLabel("Seleccione el período para el Estado de Resultados:")
        titulo.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Lista de períodos
        lista_periodos = QListWidget()
        lista_periodos.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        
        # Agregar períodos a la lista
        for key, periodo in periodos.items():
            texto = f"{periodo['nombre']} ({periodo['fecha_inicio']} - {periodo['fecha_fin']})"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, periodo)
            lista_periodos.addItem(item)
        
        # Seleccionar el primer elemento por defecto
        if lista_periodos.count() > 0:
            lista_periodos.setCurrentRow(0)
        
        layout.addWidget(lista_periodos)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        
        btn_generar = QPushButton("Generar Informe")
        btn_generar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        botones_layout.addStretch()
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_generar)
        
        layout.addLayout(botones_layout)
        
        # Conectar señales
        btn_cancelar.clicked.connect(dialog.reject)
        btn_generar.clicked.connect(dialog.accept)
        lista_periodos.itemDoubleClicked.connect(dialog.accept)
        
        # Mostrar diálogo y obtener resultado
        if dialog.exec() == QDialog.Accepted:
            item_seleccionado = lista_periodos.currentItem()
            if item_seleccionado:
                return item_seleccionado.data(Qt.UserRole)
        
        return None

    def _on_balance_general(self):
        """Generar Balance General con selección de fechas de corte."""
        try:
            self.main_window.log_message("🏦 Balance General - Selección de Fechas de Corte")
            
            if not hasattr(self, 'financial_integration') or not self.financial_integration:
                self.main_window.log_message("❌ Sistema de informes financieros no disponible")
                return
            
            # Obtener fechas de corte sugeridas basadas en períodos
            periodos = self.financial_integration._service.get_tipos_periodo_sugeridos()
            
            # Convertir períodos a fechas de corte (usar fecha fin como fecha de corte)
            fechas_corte = {}
            for key, periodo in periodos.items():
                fechas_corte[key] = {
                    'nombre': f"Balance al {periodo['fecha_fin']}",
                    'fecha': periodo['fecha_fin']
                }
            
            if not fechas_corte:
                self.main_window.log_message("❌ No hay fechas de corte disponibles")
                return
            
            # Mostrar diálogo de selección de fecha de corte
            fecha_seleccionada = self._mostrar_dialogo_seleccion_fecha_corte(fechas_corte)
            
            if fecha_seleccionada:
                fecha_corte = fecha_seleccionada['fecha']
                
                self.main_window.log_message(f"🏦 Balance General - {fecha_seleccionada['nombre']}")
                self.main_window.log_message(f"📅 Fecha de Corte: {fecha_corte}")
                
                # Generar el informe
                result = self.financial_integration._service.generar_balance_general(
                    fecha_corte=fecha_corte,
                    formato_salida='json',
                    incluir_kpis=True,
                    incluir_detalle=False
                )
                
                if result.success and result.data and "balance_general" in result.data:
                    balance = result.data["balance_general"]
                    kpis = result.data.get("kpis", {})
                    
                    self.main_window.log_message("✅ Balance General generado exitosamente")
                    self.main_window.log_message(f"💰 Total Activos: ${balance['total_activos']:,.2f}")
                    self.main_window.log_message(f"💸 Total Pasivos: ${balance['total_pasivos']:,.2f}")
                    self.main_window.log_message(f"💵 Total Patrimonio: ${balance['total_patrimonio']:,.2f}")
                    self.main_window.log_message(f"🔍 Ratio Liquidez: {balance['ratio_liquidez']:.2f}")
                    self.main_window.log_message(f"📊 Ratio Endeudamiento: {balance['ratio_endeudamiento']:.2f}")
                    self.main_window.log_message(f"✅ Ecuación Contable: {'Válida' if balance['ecuacion_contable_valida'] else 'Inválida'}")
                    if result.file_path:
                        self.main_window.log_message(f"📄 Guardado: {result.file_path}")
                else:
                    self.main_window.log_message("❌ Error al generar el informe")
            else:
                self.main_window.log_message("❌ Selección de fecha cancelada")
                    
        except Exception as e:
            self.logger.error(f"Error en Balance General: {e}")
            self.main_window.log_message(f"❌ Error: {str(e)}")

    def _mostrar_dialogo_seleccion_fecha_corte(self, fechas_corte):
        """Mostrar diálogo para seleccionar fecha de corte para Balance General."""
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                       QPushButton, QListWidget, QListWidgetItem, 
                                       QLabel)
        from PySide6.QtCore import Qt
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Seleccionar Fecha de Corte - Balance General")
        dialog.setMinimumSize(500, 400)
        dialog.setModal(True)
        
        # Layout principal
        layout = QVBoxLayout(dialog)
        
        # Título
        titulo = QLabel("Seleccione la fecha de corte para el Balance General:")
        titulo.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Lista de fechas
        lista_fechas = QListWidget()
        lista_fechas.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        
        # Agregar fechas a la lista
        for key, fecha_info in fechas_corte.items():
            if isinstance(fecha_info, dict):
                texto = f"{fecha_info.get('nombre', key)} ({fecha_info.get('fecha', key)})"
                item = QListWidgetItem(texto)
                item.setData(Qt.UserRole, fecha_info)
            else:
                # Si es solo una fecha string
                texto = f"{key} ({fecha_info})"
                item = QListWidgetItem(texto)
                item.setData(Qt.UserRole, {'nombre': key, 'fecha': fecha_info})
            lista_fechas.addItem(item)
        
        # Seleccionar el primer elemento por defecto
        if lista_fechas.count() > 0:
            lista_fechas.setCurrentRow(0)
        
        layout.addWidget(lista_fechas)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        
        btn_generar = QPushButton("Generar Balance")
        btn_generar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        botones_layout.addStretch()
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_generar)
        
        layout.addLayout(botones_layout)
        
        # Conectar señales
        btn_cancelar.clicked.connect(dialog.reject)
        btn_generar.clicked.connect(dialog.accept)
        lista_fechas.itemDoubleClicked.connect(dialog.accept)
        
        # Mostrar diálogo y obtener resultado
        if dialog.exec() == QDialog.Accepted:
            item_seleccionado = lista_fechas.currentItem()
            if item_seleccionado:
                return item_seleccionado.data(Qt.UserRole)
        
        return None
    
    def _on_operational_reports(self):
        """Informes Operativos."""
        self.main_window.log_message("🏭 Informes Operativos")
        self.main_window.log_message("🔧 Funcionalidad en desarrollo...")
        self.main_window.log_message("💡 Características planificadas:")
        self.main_window.log_message("  • Informe de Ventas")
        self.main_window.log_message("  • Informe de Clientes")
        self.main_window.log_message("  • Desempeño de Vendedores")
        
    def _on_compliance_reports(self):
        """Informes de Cumplimiento."""
        self.main_window.log_message("🔍 Informes de Cumplimiento y Auditoría")
        self.main_window.log_message("🔧 Funcionalidad en desarrollo...")
        self.main_window.log_message("💡 Características planificadas:")
        self.main_window.log_message("  • Reporte DIAN")
        self.main_window.log_message("  • Libro de Ventas")
        self.main_window.log_message("  • Auditoría de Facturas")
        
    def _on_management_reports(self):
        """Informes Gerenciales."""
        self.main_window.log_message("👔 Informes Gerenciales")
        self.main_window.log_message("🔧 Funcionalidad en desarrollo...")
        self.main_window.log_message("💡 Características planificadas:")
        self.main_window.log_message("  • Dashboard Ejecutivo")
        self.main_window.log_message("  • Análisis de Rentabilidad")
        self.main_window.log_message("  • KPIs y Métricas")
        
    def _on_send_ollama(self):
        """Enviar datos a Ollama."""
        self.main_window.log_message("📤 Integración con Ollama")
        self.main_window.log_message("🔧 Funcionalidad en desarrollo...")
        self.main_window.log_message("💡 Características planificadas:")
        self.main_window.log_message("  • Envío de datos de facturas")
        self.main_window.log_message("  • Análisis con IA local")
        
    def _on_query_ollama(self):
        """Consultar respuesta de Ollama."""
        self.main_window.log_message("💬 Consulta a Ollama")
        self.main_window.log_message("🔧 Funcionalidad en desarrollo...")
        self.main_window.log_message("💡 Características planificadas:")
        self.main_window.log_message("  • Consultas de IA")
        self.main_window.log_message("  • Respuestas inteligentes")
        
    def _on_exit(self):
        """Salir de la aplicación."""
        self.main_window.log_message("👋 ¡Gracias por usar DATACONTA!")
        self.main_window.log_message("🔚 Finalizando aplicación...")
        self.shutdown()
    
    def _update_license_display(self):
        """Actualizar display de licencia."""
        try:
            # Verificar licencia
            license_key = self._config.get_license_key()
            if self.license_validator.validate_license(license_key):
                # Por defecto mostramos Profesional ya que es la licencia activa
                self.main_window.update_license_status("Profesional")
            else:
                self.main_window.update_license_status("FREE")
        except Exception as e:
            self.logger.error(f"Error actualizando licencia: {e}")
            self.main_window.update_license_status("FREE")
    
    def run(self) -> int:
        """Ejecutar la aplicación GUI"""
        try:
            if not self.app:
                self.logger.error("Aplicación no inicializada")
                return 1
            
            # Mostrar la ventana principal
            if self.main_window:
                self.main_window.show()
                self.main_window.log_message("DATACONTA GUI iniciado correctamente")
            
            # Ejecutar el bucle principal de la aplicación
            return self.app.exec()
            
        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación: {e}")
            return 1
    
    def shutdown(self):
        """Finalizar aplicación correctamente"""
        try:
            self.logger.info("*** Finalizando DATACONTA GUI...")
            
            if self.ui_controller:
                self.ui_controller.shutdown_application()
            
            if self.app:
                self.app.quit()
            
            self.logger.info("*** DATACONTA GUI finalizado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error finalizando aplicación: {e}")


def main() -> int:
    """Función principal de entrada"""
    
    # Verificar que PySide6 esté disponible
    if not PYSIDE6_AVAILABLE:
        print("\n" + "="*60)
        print("*** DATACONTA GUI - PySide6 No Disponible")
        print("="*60)
        print("\n*** Para instalar PySide6, ejecute:")
        print("   pip install PySide6")
        print("\n*** Alternativamente, use la versión de consola:")
        print("   python main_hexagonal.py")
        print("\n" + "="*60)
        return 1
    
    try:
        # Crear y ejecutar aplicación
        app = DataContaGUIApplication()
        
        if not app.initialize():
            print("*** Error inicializando aplicación GUI")
            return 1
        
        return app.run()
        
    except KeyboardInterrupt:
        print("\n*** Aplicación interrumpida por el usuario")
        return 0
    except Exception as e:
        print(f"*** Error crítico: {e}")
        return 1
    finally:
        # Cleanup
        if 'app' in locals():
            app.shutdown()


if __name__ == "__main__":
    # Banner de inicio
    print("\n" + "="*60)
    print("*** DATACONTA - Sistema Avanzado de Gestión")
    print("*** Interfaz Gráfica PySide6")
    print("*** Arquitectura Hexagonal | Principios SOLID")
    print("="*60 + "\n")
    
    exit_code = main()
    sys.exit(exit_code)