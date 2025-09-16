#!/usr/bin/env python3
"""
DATACONTA - Sistema Avanzado de Menús con Funcionalidad Completa
Sistema de menús modular con integración completa de la API de Siigo
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.presentation.menu_system import MenuSystem, MenuSession, MenuOption, LicenseType, LicenseValidator
from src.infrastructure.adapters.logger_adapter import LoggerAdapter
from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter
from src.infrastructure.adapters.license_validator_adapter import LicenseValidatorAdapter
from src.infrastructure.adapters.file_storage_adapter import FileStorageAdapter
from src.infrastructure.adapters.csv_file_adapter import CSVFileAdapter
from src.infrastructure.config.environment_config import EnvironmentConfigurationProvider
from src.presentation.cli_interface import CLIUserInterfaceAdapter

from src.application.services.InvoiceExportService import InvoiceExportService
from src.application.services.BIExportService import BIExportService
from src.application.use_cases.invoice_use_cases import (
    GetInvoicesUseCase,
    CheckAPIStatusUseCase,
    ViewStoredFilesUseCase,
    ExportInvoiceToCSVUseCase,
    ExportInvoicesFromAPIToCSVUseCase,
    ExportToBIUseCase,
    GetInvoicesRequest,
    ExportInvoiceToCSVRequest,
    ExportInvoicesFromAPIToCSVRequest,
    ExportToBIRequest
)


class DataContaAdvancedApp:
    """Application principal con sistema de menús avanzado y funcionalidad completa"""
    
    def __init__(self):
        """Initialize application"""
        self._logger = LoggerAdapter(__name__)
        self._setup_infrastructure()
        self._setup_use_cases()
        self._setup_menu_system()
    
    def _setup_infrastructure(self):
        """Set up infrastructure components"""
        try:
            # Core infrastructure
            self._config = EnvironmentConfigurationProvider(self._logger)
            
            # Validate configuration
            is_valid, missing_vars = self._config.validate_configuration()
            if not is_valid:
                self._logger.error(f"Configuration validation failed. Missing: {missing_vars}")
                raise Exception("Configuration validation failed")
            
            # External adapters
            self._siigo_adapter = SiigoAPIAdapter(self._logger)
            self._license_validator = LicenseValidatorAdapter(
                self._config.get_license_url(),
                self._logger
            )
            self._file_storage = FileStorageAdapter(
                self._config.get_output_directory(),
                self._logger
            )
            self._csv_exporter = CSVFileAdapter(self._logger)
            self._ui = CLIUserInterfaceAdapter(self._logger)
            
            # Application services
            self._invoice_export_service = InvoiceExportService(self._logger)
            self._bi_export_service = BIExportService(self._logger)
            
            # Authenticate with Siigo API
            credentials = self._config.get_api_credentials()
            if not self._siigo_adapter.authenticate(credentials):
                self._logger.error("Failed to authenticate with Siigo API")
                raise Exception("API authentication failed")
            
            self._logger.info("Infrastructure setup completed successfully")
            
        except Exception as e:
            self._logger.error(f"Infrastructure setup failed: {e}")
            raise
    
    def _setup_use_cases(self):
        """Set up use cases"""
        self._get_invoices_use_case = GetInvoicesUseCase(
            self._siigo_adapter,
            self._license_validator,
            self._file_storage,
            self._logger
        )
        
        self._check_api_status_use_case = CheckAPIStatusUseCase(
            self._siigo_adapter,
            self._license_validator,
            self._logger
        )
        
        self._view_files_use_case = ViewStoredFilesUseCase(
            self._file_storage,
            self._logger
        )
        
        self._export_csv_use_case = ExportInvoiceToCSVUseCase(
            self._invoice_export_service,
            self._csv_exporter,
            self._license_validator,
            self._logger
        )
        
        self._export_api_to_csv_use_case = ExportInvoicesFromAPIToCSVUseCase(
            self._siigo_adapter,
            self._invoice_export_service,
            self._csv_exporter,
            self._license_validator,
            self._logger
        )
        
        self._export_to_bi_use_case = ExportToBIUseCase(
            self._siigo_adapter,
            self._bi_export_service,
            self._license_validator,
            self._logger
        )
    
    def _setup_menu_system(self):
        """Set up the advanced menu system"""
        # Create menu system
        self._menu_system = MenuSystem()
        
        # Create license validator for menu system
        menu_license_validator = LicenseValidator()
        menu_license_validator.license_validator_adapter = self._license_validator
        menu_license_validator.license_key = self._config.get_license_key()
        
        self._menu_system.license_validator = menu_license_validator
        
        # Configure menu sessions
        self._configure_business_intelligence_session()
        self._configure_reports_session()
        self._configure_tools_session()
        self._configure_ollama_session()
        self._configure_ai_analytics_session()
    
    def _configure_business_intelligence_session(self):
        """Configure Business Intelligence session"""
        bi_session = MenuSession(
            title="Business Intelligence",
            emoji="📊",
            license_required=LicenseType.FREE,
            description="Herramientas de análisis de datos y consultas",
            options=[
                MenuOption(
                    name="Consultar Facturas de Venta",
                    emoji="📋",
                    action=self._handle_get_invoices,
                    description="Consultar y visualizar facturas de venta"
                ),
                MenuOption(
                    name="Exportar a Business Intelligence",
                    emoji="🏢",
                    action=self._handle_export_bi,
                    description="Generar modelo estrella para Power BI"
                )
            ]
        )
        self._menu_system.register_session("business_intelligence", bi_session)
    
    def _configure_reports_session(self):
        """Configure Reports session"""
        reports_session = MenuSession(
            title="Generación de Informes",
            emoji="📈",
            license_required=LicenseType.PRO,
            description="Sistema completo de informes empresariales",
            options=[
                MenuOption(
                    name="📊 Informes Financieros",
                    emoji="💰",
                    action=self._handle_financial_reports_menu,
                    description="Estado de Resultados, Balance General, Flujo de Caja"
                ),
                MenuOption(
                    name="⚙️ Informes Operativos",
                    emoji="🏭",
                    action=self._handle_operational_reports_menu,
                    description="Reportes de operaciones y procesos del negocio"
                ),
                MenuOption(
                    name="📋 Informes de Cumplimiento y Auditoría",
                    emoji="�",
                    action=self._handle_compliance_reports_menu,
                    description="Reportes regulatorios y de auditoría"
                ),
                MenuOption(
                    name="👔 Informes Gerenciales",
                    emoji="📊",
                    action=self._handle_management_reports_menu,
                    description="Dashboards ejecutivos y reportes estratégicos"
                ),
                MenuOption(
                    name="📁 Ver Archivos de Salida",
                    emoji="�",
                    action=self._handle_view_files,
                    description="Explorar archivos generados por el sistema"
                ),
                MenuOption(
                    name="📤 Exportar Facturas a CSV",
                    emoji="�",
                    action=self._handle_export_csv,
                    description="Exportar facturas directamente desde la API a CSV"
                )
            ]
        )
        self._menu_system.register_session("reports", reports_session)
    
    def _configure_tools_session(self):
        """Configure Tools session"""
        tools_session = MenuSession(
            title="Herramientas",
            emoji="🛠️",
            license_required=LicenseType.FREE,
            description="Utilidades y herramientas de sistema",
            options=[
                MenuOption(
                    name="Verificar Estado de la API",
                    emoji="🔍",
                    action=self._handle_check_api_status,
                    description="Verificar conectividad y estado de Siigo API"
                ),
                MenuOption(
                    name="Configuración del Sistema",
                    emoji="⚙️",
                    action=self._handle_show_configuration,
                    description="Ver y gestionar configuración del sistema"
                )
            ]
        )
        self._menu_system.register_session("tools", tools_session)
    
    def _configure_ollama_session(self):
        """Configure Ollama session"""
        ollama_session = MenuSession(
            title="Integración con Ollama",
            emoji="🤖",
            license_required=LicenseType.PRO,
            description="Integración con modelos de IA local",
            options=[
                MenuOption(
                    name="Enviar Datos a Ollama",
                    emoji="📤",
                    action=self._handle_send_to_ollama,
                    description="Enviar datos de facturas para análisis con IA"
                ),
                MenuOption(
                    name="Consultar Respuesta de Ollama",
                    emoji="💬",
                    action=self._handle_query_ollama,
                    description="Ver respuestas y análisis de Ollama"
                )
            ]
        )
        self._menu_system.register_session("ollama", ollama_session)
    
    def _configure_ai_analytics_session(self):
        """Configure AI Analytics session (Enterprise)"""
        ai_analytics_session = MenuSession(
            title="Análisis con IA",
            emoji="🧠",
            license_required=LicenseType.ENTERPRISE,
            description="Análisis avanzado con inteligencia artificial",
            options=[
                MenuOption(
                    name="Análisis Predictivo",
                    emoji="🔮",
                    action=self._handle_predictive_analysis,
                    description="Predicciones basadas en datos históricos"
                ),
                MenuOption(
                    name="Detección de Anomalías",
                    emoji="🎯",
                    action=self._handle_anomaly_detection,
                    description="Identificar patrones inusuales en facturas"
                ),
                MenuOption(
                    name="Recomendaciones Inteligentes",
                    emoji="💡",
                    action=self._handle_smart_recommendations,
                    description="Sugerencias automatizadas para optimización"
                )
            ]
        )
        self._menu_system.register_session("ai_analytics", ai_analytics_session)
    
    # Handler methods - Real implementations
    
    def _handle_get_invoices(self):
        """Handle get invoices operation"""
        try:
            print("📋 Consultando facturas de venta...")
            print("📅 Usando filtros predeterminados (últimas 50 facturas)")
            
            request = GetInvoicesRequest(
                document_id=None,
                created_start=None,
                created_end=None
            )
            
            response = self._get_invoices_use_case.execute(
                request,
                self._config.get_license_key()
            )
            
            if response.success:
                print(f"✅ {response.message}")
                
                if response.invoices:
                    print(f"📊 Total de facturas encontradas: {len(response.invoices)}")
                    print("\n📋 Primeras 10 facturas:")
                    
                    for i, invoice in enumerate(response.invoices[:10], 1):
                        number = invoice.get('number', invoice.get('id', 'N/A'))
                        date = invoice.get('date', 'N/A')
                        total = invoice.get('total', 0)
                        print(f"  {i}. {number} - {date} - ${total:,.2f}")
                    
                    if len(response.invoices) > 10:
                        print(f"  ... y {len(response.invoices) - 10} facturas más")
                    
                    print("\n💾 Los datos se han guardado en la carpeta 'outputs/'")
                else:
                    print("ℹ️ No se encontraron facturas con los filtros aplicados")
            else:
                print(f"❌ {response.message}")
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error in get invoices handler: {e}")
            print(f"❌ Error al consultar facturas: {e}")
            return False
    
    def _handle_export_bi(self):
        """Handle export to Business Intelligence"""
        try:
            print("🏢 Exportar a Business Intelligence")
            print("-" * 40)
            print("📊 Generar modelo estrella para Power BI")
            print("Se crearán múltiples CSVs normalizados en outputs/bi/")
            
            print("\n📅 Usando parámetros predeterminados:")
            print("   📅 Fechas: Sin límite")
            print("   📊 Máximo registros: 10")
            print("   ✅ Validar esquema: No")
            
            request = ExportToBIRequest(
                start_date=None,
                end_date=None,
                max_records=10,  # Reduced even more for testing
                validate_schema=False
            )
            
            print("\nℹ️ 🔄 Procesando facturas y generando modelo estrella...")
            
            license_key = self._config.get_license_key()
            result = self._export_to_bi_use_case.execute(request, license_key)
            
            if result.success:
                stats = result.statistics
                files = result.files_created
                
                success_files = [filename for filename, success in files.items() if success]
                
                print("✅ Exportación BI exitosa!")
                print(f"📊 Facturas procesadas: {stats.get('facts_count', 0)}")
                print(f"👥 Clientes únicos: {stats.get('clients_count', 0)}")
                print(f"🏪 Vendedores únicos: {stats.get('sellers_count', 0)}")
                print(f"📦 Productos únicos: {stats.get('products_count', 0)}")
                print(f"💳 Métodos de pago únicos: {stats.get('payments_count', 0)}")
                print(f"📅 Fechas únicas: {stats.get('dates_count', 0)}")
                print("\n📁 Archivos creados:")
                
                for filename in success_files:
                    print(f"   ✓ {filename}")
                
                print(f"\n📂 Ubicación: {stats.get('output_directory', 'outputs/bi/')}")
                print(f"💬 {result.message}")
                
            else:
                print(f"❌ Error en exportación BI: {result.message}")
                
                if result.files_created:
                    failed_files = [f for f, s in result.files_created.items() if not s]
                    if failed_files:
                        print(f"❌ Archivos que fallaron: {', '.join(failed_files)}")
            
            return result.success
            
        except Exception as e:
            self._logger.error(f"Error in export BI handler: {e}")
            print(f"❌ Error al exportar BI: {e}")
            return False
    
    def _handle_check_api_status(self):
        """Handle check API status"""
        try:
            print("🔍 Verificando estado de la API...")
            
            status = self._check_api_status_use_case.execute(
                self._config.get_license_key()
            )
            
            if status.get('success', False):
                print("✅ Estado de la API: Operativa")
                print(f"🌐 URL: {status.get('api_url', 'N/A')}")
                print(f"👤 Usuario: {status.get('username', 'N/A')}")
                print(f"⏰ Tiempo de respuesta: {status.get('response_time_ms', 0)}ms")
                
                if 'endpoints_status' in status:
                    print("\n📡 Estado de endpoints:")
                    for endpoint, endpoint_status in status['endpoints_status'].items():
                        status_icon = "✅" if endpoint_status else "❌"
                        print(f"   {status_icon} {endpoint}")
            else:
                print("❌ Estado de la API: Error")
                print(f"💬 Mensaje: {status.get('message', 'Error desconocido')}")
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error in check API status handler: {e}")
            print(f"❌ Error al verificar el estado de la API: {e}")
            return False
    
    def _handle_view_files(self):
        """Handle view files"""
        try:
            print("📁 Ver Archivos de Salida")
            print("-" * 40)
            
            result = self._view_files_use_case.execute()
            
            if result['success']:
                files = result['files']
                if files:
                    print(f"📊 Total de archivos encontrados: {len(files)}")
                    print("\n📋 Lista de archivos:")
                    
                    for file_info in files:
                        file_type = file_info.get('type', 'UNKNOWN').upper()
                        file_name = file_info.get('name', 'N/A')
                        file_size = file_info.get('size', 0)
                        
                        size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
                        
                        print(f"  📄 [{file_type}] {file_name} ({size_mb:.2f} MB)")
                    
                    print(f"\n💬 {result['message']}")
                else:
                    print("ℹ️ No se encontraron archivos de salida")
            else:
                print(f"❌ {result['message']}")
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error in view files handler: {e}")
            print(f"❌ Error al ver los archivos: {e}")
            return False
    
    def _handle_export_csv(self):
        """Handle export CSV"""
        try:
            print("📤 Exportar Facturas a CSV")
            print("-" * 40)
            print("📊 Exportar facturas desde API a formato CSV")
            
            print("\n📋 Usando parámetros predeterminados:")
            print("   📅 Fechas: Sin límite")
            print("   📊 Máximo registros: 25")
            
            request = ExportInvoicesFromAPIToCSVRequest(
                start_date=None,
                end_date=None,
                max_records=25,  # Reduced for better performance
                output_filename=None
            )
            
            print("\nℹ️ 🔄 Obteniendo facturas desde API y exportando a CSV...")
            
            license_key = self._config.get_license_key()
            result = self._export_api_to_csv_use_case.execute(request, license_key)
            
            if result.success:
                outputs_path = self._csv_exporter.get_outputs_directory()
                print("✅ Exportación exitosa!")
                print(f"📁 Archivo: {result.file_path}")
                print(f"📊 Filas exportadas: {result.rows_exported}")
                print(f"📂 Ubicación: {outputs_path}")
                print(f"💬 {result.message}")
            else:
                print(f"❌ Error en exportación: {result.message}")
            
            return result.success
            
        except Exception as e:
            self._logger.error(f"Error in export CSV handler: {e}")
            print(f"❌ Error al exportar CSV: {e}")
            return False
    
    # Report menu handlers - New structured approach
    
    def _handle_financial_reports_menu(self):
        """Handle Financial Reports submenu"""
        try:
            while True:
                print("\n" + "="*60)
                print("💰 INFORMES FINANCIEROS")
                print("="*60)
                print("📝 Reportes contables y análisis financiero")
                print("-"*60)
                print("1. 📊 Estado de Resultados (P&L)")
                print("   📝 Informe de ingresos, gastos y utilidades")
                print("2. ⚖️ Balance General")
                print("   📝 Activos, pasivos y patrimonio")
                print("3. 💸 Flujo de Caja")
                print("   📝 Análisis de entradas y salidas de efectivo")
                print("4. 🏦 Cuentas por Cobrar y Pagar")
                print("   📝 Estado de deudas y acreencias")
                print("-"*60)
                print("9. 🔙 Volver al menú anterior")
                print("0. 🚪 Salir")
                print("="*60)
                
                try:
                    option = input("\nSeleccione una opción: ").strip()
                    
                    if option == "0":
                        return False
                    elif option == "9":
                        return True
                    elif option == "1":
                        self._handle_profit_loss_report()
                    elif option == "2":
                        self._handle_balance_sheet_report()
                    elif option == "3":
                        self._handle_cash_flow_report()
                    elif option == "4":
                        self._handle_accounts_report()
                    else:
                        print("❌ Opción no válida. Intente nuevamente.")
                    
                    if option in ["1", "2", "3", "4"]:
                        input("\n� Presione Enter para continuar...")
                    
                except KeyboardInterrupt:
                    return False
                    
        except Exception as e:
            self._logger.error(f"Error in financial reports menu: {e}")
            print(f"❌ Error en el menú de informes financieros: {e}")
            return False
    
    def _handle_operational_reports_menu(self):
        """Handle Operational Reports submenu"""
        try:
            while True:
                print("\n" + "="*60)
                print("🏭 INFORMES OPERATIVOS")
                print("="*60)
                print("📝 Reportes de operaciones y procesos del negocio")
                print("-"*60)
                print("1. 📦 Informe de Ventas")
                print("   📝 Análisis detallado de ventas y productos")
                print("2. 👥 Informe de Clientes")
                print("   📝 Comportamiento y segmentación de clientes")
                print("3. 🏪 Informe de Vendedores")
                print("   📝 Desempeño del equipo de ventas")
                print("4. 📈 Análisis de Tendencias")
                print("   📝 Patrones y tendencias del negocio")
                print("-"*60)
                print("9. 🔙 Volver al menú anterior")
                print("0. � Salir")
                print("="*60)
                
                try:
                    option = input("\nSeleccione una opción: ").strip()
                    
                    if option == "0":
                        return False
                    elif option == "9":
                        return True
                    elif option == "1":
                        self._handle_sales_report()
                    elif option == "2":
                        self._handle_customers_report()
                    elif option == "3":
                        self._handle_sellers_report()
                    elif option == "4":
                        self._handle_trends_report()
                    else:
                        print("❌ Opción no válida. Intente nuevamente.")
                    
                    if option in ["1", "2", "3", "4"]:
                        input("\n📌 Presione Enter para continuar...")
                    
                except KeyboardInterrupt:
                    return False
                    
        except Exception as e:
            self._logger.error(f"Error in operational reports menu: {e}")
            print(f"❌ Error en el menú de informes operativos: {e}")
            return False
    
    def _handle_compliance_reports_menu(self):
        """Handle Compliance Reports submenu"""
        try:
            while True:
                print("\n" + "="*60)
                print("🔍 INFORMES DE CUMPLIMIENTO Y AUDITORÍA")
                print("="*60)
                print("📝 Reportes regulatorios y de auditoría")
                print("-"*60)
                print("1. 📋 Reporte DIAN")
                print("   📝 Informes para la Dirección de Impuestos")
                print("2. 🧾 Libro de Ventas")
                print("   📝 Registro oficial de ventas")
                print("3. 🔐 Auditoría de Facturas")
                print("   📝 Revisión y validación de documentos")
                print("4. 📊 Informe de Impuestos")
                print("   📝 Cálculos y declaraciones tributarias")
                print("-"*60)
                print("9. 🔙 Volver al menú anterior")
                print("0. 🚪 Salir")
                print("="*60)
                
                try:
                    option = input("\nSeleccione una opción: ").strip()
                    
                    if option == "0":
                        return False
                    elif option == "9":
                        return True
                    elif option == "1":
                        self._handle_dian_report()
                    elif option == "2":
                        self._handle_sales_book_report()
                    elif option == "3":
                        self._handle_audit_report()
                    elif option == "4":
                        self._handle_tax_report()
                    else:
                        print("❌ Opción no válida. Intente nuevamente.")
                    
                    if option in ["1", "2", "3", "4"]:
                        input("\n📌 Presione Enter para continuar...")
                    
                except KeyboardInterrupt:
                    return False
                    
        except Exception as e:
            self._logger.error(f"Error in compliance reports menu: {e}")
            print(f"❌ Error en el menú de cumplimiento: {e}")
            return False
    
    def _handle_management_reports_menu(self):
        """Handle Management Reports submenu"""
        try:
            while True:
                print("\n" + "="*60)
                print("� INFORMES GERENCIALES")
                print("="*60)
                print("📝 Dashboards ejecutivos y reportes estratégicos")
                print("-"*60)
                print("1. 📊 Dashboard Ejecutivo")
                print("   📝 KPIs y métricas clave del negocio")
                print("2. 💹 Análisis de Rentabilidad")
                print("   📝 Márgenes y rentabilidad por producto/cliente")
                print("3. 🎯 Indicadores de Desempeño")
                print("   📝 KPIs operativos y financieros")
                print("4. 📈 Proyecciones y Presupuestos")
                print("   📝 Análisis predictivo y planeación")
                print("-"*60)
                print("9. 🔙 Volver al menú anterior")
                print("0. 🚪 Salir")
                print("="*60)
                
                try:
                    option = input("\nSeleccione una opción: ").strip()
                    
                    if option == "0":
                        return False
                    elif option == "9":
                        return True
                    elif option == "1":
                        self._handle_executive_dashboard()
                    elif option == "2":
                        self._handle_profitability_analysis()
                    elif option == "3":
                        self._handle_kpi_report()
                    elif option == "4":
                        self._handle_projections_report()
                    else:
                        print("❌ Opción no válida. Intente nuevamente.")
                    
                    if option in ["1", "2", "3", "4"]:
                        input("\n📌 Presione Enter para continuar...")
                    
                except KeyboardInterrupt:
                    return False
                    
        except Exception as e:
            self._logger.error(f"Error in management reports menu: {e}")
            print(f"❌ Error en el menú de informes gerenciales: {e}")
            return False
    
    # Financial Reports Implementation
    
    def _handle_profit_loss_report(self):
        """Handle Profit & Loss Statement"""
        print("📊 Estado de Resultados (P&L)")
        print("-" * 40)
        print("💰 Generando informe de ingresos, gastos y utilidades...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Mes actual")
        print("💡 Características planificadas:")
        print("  • Ingresos por ventas")
        print("  • Costos y gastos operativos")
        print("  • Utilidad bruta y neta")
        print("  • Comparativo vs período anterior")
        return True
    
    def _handle_balance_sheet_report(self):
        """Handle Balance Sheet"""
        print("⚖️ Balance General")
        print("-" * 40)
        print("🏛️ Generando estado de situación financiera...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Fecha de corte: Hoy")
        print("💡 Características planificadas:")
        print("  • Activos corrientes y no corrientes")
        print("  • Pasivos y obligaciones")
        print("  • Patrimonio y capital")
        print("  • Ecuación contable balanceada")
        return True
    
    def _handle_cash_flow_report(self):
        """Handle Cash Flow Statement"""
        print("💸 Flujo de Caja")
        print("-" * 40)
        print("💰 Analizando entradas y salidas de efectivo...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Últimos 3 meses")
        print("💡 Características planificadas:")
        print("  • Flujo operativo")
        print("  • Flujo de inversión")
        print("  • Flujo de financiación")
        print("  • Proyección de liquidez")
        return True
    
    def _handle_accounts_report(self):
        """Handle Accounts Receivable/Payable"""
        print("🏦 Cuentas por Cobrar y Pagar")
        print("-" * 40)
        print("💳 Analizando estado de deudas y acreencias...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Corte: Fecha actual")
        print("💡 Características planificadas:")
        print("  • Antigüedad de saldos")
        print("  • Clientes morosos")
        print("  • Obligaciones por pagar")
        print("  • Indicadores de cartera")
        return True
    
    # Operational Reports Implementation
    
    def _handle_sales_report(self):
        """Handle Sales Report"""
        print("📦 Informe de Ventas")
        print("-" * 40)
        print("📊 Analizando desempeño de ventas...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Último mes")
        print("💡 Características planificadas:")
        print("  • Ventas por producto")
        print("  • Análisis de márgenes")
        print("  • Productos más vendidos")
        print("  • Tendencias de ventas")
        return True
    
    def _handle_customers_report(self):
        """Handle Customers Report"""
        print("👥 Informe de Clientes")
        print("-" * 40)
        print("👤 Analizando comportamiento de clientes...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Últimos 6 meses")
        print("💡 Características planificadas:")
        print("  • Segmentación de clientes")
        print("  • Frecuencia de compras")
        print("  • Valor promedio de compra")
        print("  • Clientes más rentables")
        return True
    
    def _handle_sellers_report(self):
        """Handle Sellers Performance Report"""
        print("🏪 Informe de Vendedores")
        print("-" * 40)
        print("� Evaluando desempeño del equipo de ventas...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Trimestre actual")
        print("💡 Características planificadas:")
        print("  • Ventas por vendedor")
        print("  • Cumplimiento de metas")
        print("  • Comisiones generadas")
        print("  • Ranking de desempeño")
        return True
    
    def _handle_trends_report(self):
        """Handle Trends Analysis Report"""
        print("📈 Análisis de Tendencias")
        print("-" * 40)
        print("📊 Identificando patrones del negocio...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Último año")
        print("💡 Características planificadas:")
        print("  • Estacionalidad de ventas")
        print("  • Crecimiento mensual")
        print("  • Tendencias por categoría")
        print("  • Predicciones futuras")
        return True
    
    # Compliance Reports Implementation
    
    def _handle_dian_report(self):
        """Handle DIAN Report"""
        print("📋 Reporte DIAN")
        print("-" * 40)
        print("🏛️ Generando informes para la DIAN...")
        print("� Funcionalidad en desarrollo...")
        print("📅 Período: Mes fiscal actual")
        print("💡 Características planificadas:")
        print("  • Formato 1001 - Ventas")
        print("  • Retenciones aplicadas")
        print("  • IVA causado y descontable")
        print("  • Archivos XML para envío")
        return True
    
    def _handle_sales_book_report(self):
        """Handle Sales Book Report"""
        print("🧾 Libro de Ventas")
        print("-" * 40)
        print("📚 Generando libro oficial de ventas...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Mes seleccionado")
        print("� Características planificadas:")
        print("  • Registro cronológico")
        print("  • Numeración consecutiva")
        print("  • Totales por día/mes")
        print("  • Formato legal requerido")
        return True
    
    def _handle_audit_report(self):
        """Handle Audit Report"""
        print("🔐 Auditoría de Facturas")
        print("-" * 40)
        print("🔍 Verificando integridad de documentos...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Rango seleccionado")
        print("💡 Características planificadas:")
        print("  • Validación de secuencias")
        print("  • Facturas anuladas")
        print("  • Inconsistencias detectadas")
        print("  • Reporte de anomalías")
        return True
    
    def _handle_tax_report(self):
        """Handle Tax Report"""
        print("📊 Informe de Impuestos")
        print("-" * 40)
        print("💰 Calculando obligaciones tributarias...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Bimestre actual")
        print("💡 Características planificadas:")
        print("  • IVA por pagar")
        print("  • Retenciones practicadas")
        print("  • Base gravable")
        print("  • Formularios de declaración")
        return True
    
    # Management Reports Implementation
    
    def _handle_executive_dashboard(self):
        """Handle Executive Dashboard"""
        print("📊 Dashboard Ejecutivo")
        print("-" * 40)
        print("📈 Generando vista ejecutiva del negocio...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Tiempo real y tendencias")
        print("💡 Características planificadas:")
        print("  • KPIs principales")
        print("  • Gráficos de tendencias")
        print("  • Alertas importantes")
        print("  • Resumen ejecutivo")
        return True
    
    def _handle_profitability_analysis(self):
        """Handle Profitability Analysis"""
        print("💹 Análisis de Rentabilidad")
        print("-" * 40)
        print("💰 Evaluando rentabilidad por segmentos...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Últimos 12 meses")
        print("💡 Características planificadas:")
        print("  • Margen por producto")
        print("  • Rentabilidad por cliente")
        print("  • Análisis ABC")
        print("  • Oportunidades de mejora")
        return True
    
    def _handle_kpi_report(self):
        """Handle KPI Report"""
        print("🎯 Indicadores de Desempeño")
        print("-" * 40)
        print("📊 Midiendo indicadores clave...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Período: Trimestre actual")
        print("💡 Características planificadas:")
        print("  • ROI y ROE")
        print("  • Rotación de inventario")
        print("  • Días de cartera")
        print("  • Indicadores operativos")
        return True
    
    def _handle_projections_report(self):
        """Handle Projections and Budget Report"""
        print("📈 Proyecciones y Presupuestos")
        print("-" * 40)
        print("🔮 Generando análisis predictivo...")
        print("🔧 Funcionalidad en desarrollo...")
        print("📅 Horizonte: Próximos 6 meses")
        print("💡 Características planificadas:")
        print("  • Proyección de ventas")
        print("  • Presupuesto vs real")
        print("  • Análisis de variaciones")
        print("  • Escenarios futuros")
        return True
    
    # Ollama handlers (future functionality)
    def _handle_send_to_ollama(self):
        """Handle send to Ollama"""
        print("🤖 Enviar Datos a Ollama")
        print("-" * 40)
        print("🔧 Funcionalidad en desarrollo...")
        print("ℹ️ La integración con Ollama estará disponible próximamente")
        print("💡 Características planificadas:")
        print("  • Análisis automático de facturas")
        print("  • Detección de patrones y tendencias")
        print("  • Recomendaciones inteligentes")
        return True
    
    def _handle_query_ollama(self):
        """Handle query Ollama"""
        print("💬 Consultar Respuesta de Ollama")
        print("-" * 40)
        print("🔧 Funcionalidad en desarrollo...")
        print("ℹ️ La consulta a Ollama estará disponible próximamente")
        print("💡 Podrás obtener:")
        print("  • Análisis de tendencias de ventas")
        print("  • Insights sobre clientes")
        print("  • Recomendaciones de optimización")
        return True
    
    # Enterprise AI handlers (future functionality)
    def _handle_predictive_analysis(self):
        """Handle predictive analysis"""
        print("🔮 Análisis Predictivo")
        print("-" * 40)
        print("🔧 Funcionalidad Enterprise en desarrollo...")
        print("ℹ️ Características planificadas:")
        print("  • Pronóstico de ventas")
        print("  • Tendencias de mercado")
        print("  • Análisis de temporalidad")
        return True
    
    def _handle_anomaly_detection(self):
        """Handle anomaly detection"""
        print("🎯 Detección de Anomalías")
        print("-" * 40)
        print("🔧 Funcionalidad Enterprise en desarrollo...")
        print("ℹ️ Características planificadas:")
        print("  • Facturas duplicadas")
        print("  • Patrones de precios inusuales")
        print("  • Comportamiento atípico de clientes")
        return True
    
    def _handle_smart_recommendations(self):
        """Handle smart recommendations"""
        print("💡 Recomendaciones Inteligentes")
        print("-" * 40)
        print("🔧 Funcionalidad Enterprise en desarrollo...")
        print("ℹ️ Características planificadas:")
        print("  • Optimización de precios")
        print("  • Mejores clientes potenciales")
        print("  • Estrategias de ventas personalizadas")
        return True
    
    def _handle_show_configuration(self):
        """Handle show configuration"""
        try:
            print("⚙️ Configuración del Sistema")
            print("-" * 40)
            
            credentials = self._config.get_api_credentials()
            output_dir = self._config.get_output_directory()
            license_key = self._config.get_license_key()
            
            print("📋 Configuración actual:")
            print(f"  🌐 API URL: {credentials.api_url}")
            print(f"  👤 Usuario: {credentials.username}")
            print(f"  🔑 Clave de acceso: {credentials.access_key[:10]}...")
            print(f"  📂 Directorio de salida: {output_dir}")
            print(f"  🎫 Clave de licencia: {license_key[:15]}..." if license_key else "  🎫 Sin licencia configurada")
            print(f"  📊 Formato decimal: Coma (,) - Optimizado para Power BI")
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error in show configuration handler: {e}")
            print(f"❌ Error al mostrar configuración: {e}")
            return False
    
    def run(self):
        """Run the application"""
        try:
            print("🚀 DATACONTA - SISTEMA AVANZADO DE MENÚS")
            print("=" * 60)
            print("✨ Sistema modular con funcionalidad completa integrada")
            print("🔗 Conectado a API de Siigo con todas las características")
            print("=" * 60)
            
            # Show license information
            license_display = self._menu_system.license_validator.get_license_display_name()
            print(f"✅ Inicialización exitosa - Licencia: {license_display}")
            print("🌐 Conexión con API de Siigo: ✅ Establecida")
            print()
            
            # Run menu system
            self._menu_system.run()
            
            print("🔚 Finalizando aplicación...")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Aplicación terminada por el usuario!")
        except Exception as e:
            self._logger.error(f"Error running application: {e}")
            print(f"❌ Error durante la ejecución: {e}")
            raise


def main():
    """Main entry point"""
    try:
        app = DataContaAdvancedApp()
        app.run()
        return 0
        
    except Exception as e:
        print(f"❌ Error crítico durante la inicialización: {str(e)}")
        print("💡 Verifique:")
        print("  • Configuración del archivo .env")
        print("  • Conectividad a internet")
        print("  • Credenciales de API de Siigo")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 ¡Aplicación terminada por el usuario!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        sys.exit(1)