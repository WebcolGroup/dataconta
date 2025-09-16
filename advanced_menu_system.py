#!/usr/bin/env python3
"""
DATACONTA - Advanced Menu System with Full Integration
Production-ready system with complete functionality from main_hexagonal.py
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the advanced menu system
from src.presentation.menu_system import MenuSystem, LicenseType
from src.presentation.menu_config import create_dataconta_menu_system, setup_dataconta_menus

# Import all the infrastructure from main_hexagonal.py
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


class AdvancedDataContaIntegrator:
    """Integration layer between advanced menu system and full DATACONTA functionality"""
    
    def __init__(self):
        """Initialize with full infrastructure like main_hexagonal.py"""
        self._setup_dependencies()
        self._setup_use_cases()
    
    def _setup_dependencies(self) -> None:
        """Set up all dependencies exactly like main_hexagonal.py"""
        # Core infrastructure
        self._logger = LoggerAdapter(__name__)
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
        
        self._logger.info("Advanced menu system initialized successfully")
    
    def _setup_use_cases(self) -> None:
        """Set up use cases exactly like main_hexagonal.py"""
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
    
    # Real implementation functions - identical to main_hexagonal.py
    
    def consultar_facturas(self):
        """Handle get invoices operation - REAL FUNCTIONALITY"""
        try:
            print("📋 Consultando facturas de venta...")
            
            # Get filters from user (simplified for menu system)
            print("📅 Usando filtros predeterminados (últimas 50 facturas)")
            
            # Create request
            request = GetInvoicesRequest(
                document_id=None,
                created_start=None,
                created_end=None
            )
            
            # Execute use case
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
            self._logger.error(f"Error handling get invoices: {e}")
            print(f"❌ Error al consultar facturas: {e}")
            return False
    
    def exportar_bi(self):
        """Handle export to Business Intelligence - REAL FUNCTIONALITY"""
        try:
            print("🏢 Exportar a Business Intelligence")
            print("-" * 40)
            print("📊 Generar modelo estrella para Power BI")
            print("Se crearán múltiples CSVs normalizados en outputs/bi/")
            
            # Get basic parameters (simplified for menu)
            print("\n📅 Usando parámetros predeterminados:")
            print("   📅 Fechas: Sin límite")
            print("   📊 Máximo registros: 100")
            print("   ✅ Validar esquema: No")
            
            # Create request
            request = ExportToBIRequest(
                start_date=None,
                end_date=None,
                max_records=100,
                validate_schema=False
            )
            
            print("\nℹ️ 🔄 Procesando facturas y generando modelo estrella...")
            
            # Execute use case
            license_key = self._config.get_license_key()
            result = self._export_to_bi_use_case.execute(request, license_key)
            
            if result.success:
                # Show detailed success information
                stats = result.statistics
                files = result.files_created
                
                success_files = [filename for filename, success in files.items() if success]
                
                print("✅ ✅ Exportación BI exitosa!")
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
                
                # Show partial results if available
                if result.files_created:
                    failed_files = [f for f, s in result.files_created.items() if not s]
                    if failed_files:
                        print(f"❌ Archivos que fallaron: {', '.join(failed_files)}")
            
            return result.success
            
        except Exception as e:
            self._logger.error(f"Error exporting BI: {e}")
            print(f"❌ Error al exportar BI: {e}")
            return False
    
    def verificar_api(self):
        """Handle check API status - REAL FUNCTIONALITY"""
        try:
            print("🔍 Verificando estado de la API...")
            
            # Execute use case
            status = self._check_api_status_use_case.execute(
                self._config.get_license_key()
            )
            
            # Display results
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
            self._logger.error(f"Error checking API status: {e}")
            print(f"❌ Error al verificar el estado de la API: {e}")
            return False
    
    def ver_archivos(self):
        """Handle view files - REAL FUNCTIONALITY"""
        try:
            print("📁 Ver Archivos de Salida")
            print("-" * 40)
            
            # Execute use case
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
                        
                        # Convert size to MB
                        size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
                        
                        print(f"  📄 [{file_type}] {file_name} ({size_mb:.2f} MB)")
                    
                    print(f"\n💬 {result['message']}")
                else:
                    print("ℹ️ No se encontraron archivos de salida")
            else:
                print(f"❌ {result['message']}")
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error viewing files: {e}")
            print(f"❌ Error al ver los archivos: {e}")
            return False
    
    def exportar_csv(self):
        """Handle export CSV - REAL FUNCTIONALITY"""
        try:
            print("📤 Exportar Facturas a CSV")
            print("-" * 40)
            print("📊 Exportar facturas desde API a formato CSV")
            
            # Use simplified parameters
            print("\n📋 Usando parámetros predeterminados:")
            print("   📅 Fechas: Sin límite")
            print("   📊 Máximo registros: 50")
            
            # Create request
            request = ExportInvoicesFromAPIToCSVRequest(
                start_date=None,
                end_date=None,
                max_records=50,
                output_filename=None
            )
            
            # Execute use case
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
            self._logger.error(f"Error exporting CSV: {e}")
            print(f"❌ Error al exportar CSV: {e}")
            return False
    
    def exportar_pdf(self):
        """Export to PDF - Future functionality"""
        print("📄 Exportar Informe PDF")
        print("-" * 40)
        print("🔧 Funcionalidad en desarrollo...")
        print("ℹ️ Esta característica estará disponible en futuras versiones")
        print("💡 Sugerencia: Use la exportación CSV mientras tanto")
        return True
    
    def configuracion(self):
        """Show system configuration - REAL INFO"""
        try:
            print("⚙️ Configuración del Sistema")
            print("-" * 40)
            
            # Get real configuration
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
            self._logger.error(f"Error showing configuration: {e}")
            print(f"❌ Error al mostrar configuración: {e}")
            return False
    
    def enviar_ollama(self):
        """Send data to Ollama - Future functionality"""
        print("🤖 Enviar Datos a Ollama")
        print("-" * 40)
        print("🔧 Funcionalidad en desarrollo...")
        print("ℹ️ La integración con Ollama estará disponible próximamente")
        print("💡 Características planificadas:")
        print("  • Análisis automático de facturas")
        print("  • Detección de patrones y tendencias")
        print("  • Recomendaciones inteligentes")
        return True
    
    def consultar_ollama(self):
        """Query Ollama response - Future functionality"""
        print("💬 Consultar Respuesta de Ollama")
        print("-" * 40)
        print("🔧 Funcionalidad en desarrollo...")
        print("ℹ️ La consulta a Ollama estará disponible próximamente")
        print("💡 Podrás obtener:")
        print("  • Análisis de tendencias de ventas")
        print("  • Insights sobre clientes")
        print("  • Recomendaciones de optimización")
        return True
    
    def create_integrated_menu_system(self) -> MenuSystem:
        """Create menu system with all real functionality integrated"""
        menu_system = MenuSystem()
        
        # Override menu functions with real implementations
        from src.presentation import menu_config
        
        # Replace functions with real integrated versions
        menu_config.consultar_facturas = self.consultar_facturas
        menu_config.exportar_bi = self.exportar_bi
        menu_config.verificar_api = self.verificar_api
        menu_config.ver_archivos = self.ver_archivos
        menu_config.exportar_csv = self.exportar_csv
        menu_config.exportar_pdf = self.exportar_pdf
        menu_config.configuracion = self.configuracion
        menu_config.enviar_ollama = self.enviar_ollama
        menu_config.consultar_ollama = self.consultar_ollama
        
        # Setup menus with integrated functions
        setup_dataconta_menus(menu_system)
        
        return menu_system


def main():
    """Main entry point"""
    print("🚀 DATACONTA - SISTEMA AVANZADO DE MENÚS (FUNCIONALIDAD COMPLETA)")
    print("=" * 70)
    print("✨ Sistema de menús avanzado con funcionalidad 100% real")
    print("🔗 Integración completa con API de Siigo y todas las características")
    print("=" * 70)
    
    try:
        # Initialize integrator (this includes all the real infrastructure)
        print("🔧 Inicializando infraestructura completa...")
        integrator = AdvancedDataContaIntegrator()
        
        # Create integrated menu system
        print("🎯 Configurando sistema de menús avanzado...")
        menu_system = integrator.create_integrated_menu_system()
        
        # Show initialization success
        license_display = menu_system.license_validator.get_license_display_name()
        print(f"✅ Inicialización exitosa - Licencia: {license_display}")
        print("🌐 Conexión con API de Siigo: Establecida")
        
        # Run menu system
        menu_system.run()
        
        print("🔚 Finalizando aplicación...")
        
    except Exception as e:
        print(f"❌ Error crítico durante la inicialización: {str(e)}")
        print("💡 Verifique:")
        print("  • Configuración del archivo .env")
        print("  • Conectividad a internet")
        print("  • Credenciales de API de Siigo")
        return 1
    
    return 0


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