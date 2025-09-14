"""
Main entry point for DataConta - Siigo API Integration using Hexagonal Architecture.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

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


class DataContaApplication:
    """DataConta - Main application class using Hexagonal Architecture."""
    
    def __init__(self):
        """Initialize the application with all dependencies."""
        self._setup_dependencies()
        self._setup_use_cases()
    
    def _setup_dependencies(self) -> None:
        """Set up all dependencies (adapters)."""
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
    
    def _setup_use_cases(self) -> None:
        """Set up use cases with dependencies."""
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
    
    def run(self) -> int:
        """Run the main application."""
        try:
            self._logger.info("Starting DataConta - Siigo API Integration")
            
            # Validate license
            license_key = self._config.get_license_key()
            if not self._license_validator.is_license_valid(license_key):
                self._ui.display_message("License validation failed", "error")
                return 1
            
            self._logger.info("License validation successful")
            self._ui.display_message("¡Aplicación iniciada correctamente!", "success")
            
            # Main application loop
            while True:
                try:
                    choice = self._ui.show_menu()
                    
                    if choice == '1':
                        self._handle_get_invoices()
                    elif choice == '2':
                        self._handle_check_api_status()
                    elif choice == '3':
                        self._handle_view_files()
                    elif choice == '4':
                        self._handle_export_csv()
                    elif choice == '5':
                        self._handle_export_bi()
                    elif choice == '0':
                        break
                    else:
                        self._ui.display_message("Opción inválida. Por favor, seleccione una opción válida.", "warning")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self._logger.error(f"Error in main loop: {e}")
                    self._ui.display_message(f"Error inesperado: {e}", "error")
            
            self._ui.display_exit_message()
            self._logger.info("Application finished successfully")
            return 0
            
        except Exception as e:
            self._logger.error(f"Application error: {e}")
            self._ui.display_message(f"Error de aplicación: {e}", "error")
            return 1
    
    def _handle_get_invoices(self) -> None:
        """Handle get invoices operation."""
        try:
            self._ui.display_message("Consultando facturas de venta...", "info")
            
            # Get filters from user
            filters = self._ui.get_invoice_filters()
            
            # Create request
            request = GetInvoicesRequest(
                document_id=filters.document_id,
                created_start=filters.created_start.isoformat() if filters.created_start else None,
                created_end=filters.created_end.isoformat() if filters.created_end else None
            )
            
            # Execute use case
            response = self._get_invoices_use_case.execute(
                request,
                self._config.get_license_key()
            )
            
            if response.success:
                self._ui.display_message(response.message, "success")
                self._ui.display_invoices(response.invoices)
                if response.invoices:
                    self._ui.display_message("Los datos se han guardado en la carpeta 'outputs/'", "info")
            else:
                self._ui.display_message(response.message, "error")
            
        except Exception as e:
            self._logger.error(f"Error handling get invoices: {e}")
            self._ui.display_message(f"Error al consultar facturas: {e}", "error")
        finally:
            self._ui.wait_for_user()
    
    def _handle_check_api_status(self) -> None:
        """Handle check API status operation."""
        try:
            self._ui.display_message("Verificando estado de la API...", "info")
            
            # Execute use case
            status = self._check_api_status_use_case.execute(
                self._config.get_license_key()
            )
            
            # Display results
            self._ui.display_api_status(status)
            
        except Exception as e:
            self._logger.error(f"Error checking API status: {e}")
            self._ui.display_message(f"Error al verificar el estado de la API: {e}", "error")
        finally:
            self._ui.wait_for_user()
    
    def _handle_view_files(self) -> None:
        """Handle view files operation."""
        try:
            # Execute use case
            result = self._view_files_use_case.execute()
            
            if result['success']:
                self._ui.display_file_info(result['files'])
                self._ui.display_message(result['message'], "info")
            else:
                self._ui.display_message(result['message'], "error")
                
        except Exception as e:
            self._logger.error(f"Error viewing files: {e}")
            self._ui.display_message(f"Error al ver los archivos: {e}", "error")
        finally:
            self._ui.wait_for_user()
    
    def _handle_export_csv(self) -> None:
        """Handle export invoices to CSV operation from API."""
        try:
            # Get export parameters from user
            export_params = self._ui.get_csv_export_parameters()
            
            if not export_params:
                self._ui.display_message("Operación cancelada", "info")
                return
            
            # Create request
            request = ExportInvoicesFromAPIToCSVRequest(
                start_date=export_params.get("start_date"),
                end_date=export_params.get("end_date"),
                max_records=export_params.get("max_records", 100),
                output_filename=export_params.get("custom_filename")
            )
            
            # Execute use case
            self._ui.display_message("Obteniendo facturas desde API y exportando a CSV...", "info")
            
            license_key = self._config.get_license_key()
            result = self._export_api_to_csv_use_case.execute(request, license_key)
            
            if result.success:
                outputs_path = self._csv_exporter.get_outputs_directory()
                self._ui.display_message(
                    f"✅ Exportación exitosa!\n"
                    f"📁 Archivo: {result.file_path}\n"
                    f"📊 Filas exportadas: {result.rows_exported}\n"
                    f"📂 Ubicación: {outputs_path}\n"
                    f"💬 {result.message}",
                    "success"
                )
            else:
                self._ui.display_message(f"❌ Error en exportación: {result.message}", "error")
                
        except Exception as e:
            self._logger.error(f"Error exporting CSV: {e}")
            self._ui.display_message(f"Error al exportar CSV: {e}", "error")
        finally:
            self._ui.wait_for_user()
    
    def _handle_export_bi(self) -> None:
        """Handle export to Business Intelligence operation."""
        try:
            # Get BI export parameters from user
            bi_params = self._ui.get_bi_export_parameters()
            
            if not bi_params:
                self._ui.display_message("Operación cancelada", "info")
                return
            
            # Create request
            request = ExportToBIRequest(
                start_date=bi_params.get("start_date"),
                end_date=bi_params.get("end_date"),
                max_records=bi_params.get("max_records", 100),
                validate_schema=bi_params.get("validate_schema", True)
            )
            
            # Execute use case
            self._ui.display_message("🔄 Procesando facturas y generando modelo estrella...", "info")
            
            license_key = self._config.get_license_key()
            result = self._export_to_bi_use_case.execute(request, license_key)
            
            if result.success:
                # Show detailed success information
                stats = result.statistics
                files = result.files_created
                
                success_files = [filename for filename, success in files.items() if success]
                
                message_parts = [
                    "✅ Exportación BI exitosa!",
                    f"📊 Facturas procesadas: {stats.get('facts_count', 0)}",
                    f"👥 Clientes únicos: {stats.get('clients_count', 0)}",
                    f"🏪 Vendedores únicos: {stats.get('sellers_count', 0)}",
                    f"📦 Productos únicos: {stats.get('products_count', 0)}",
                    f"💳 Métodos de pago únicos: {stats.get('payments_count', 0)}",
                    f"📅 Fechas únicas: {stats.get('dates_count', 0)}",
                    "",
                    "📁 Archivos creados:",
                ]
                
                for filename in success_files:
                    message_parts.append(f"   ✓ {filename}")
                
                message_parts.extend([
                    "",
                    f"📂 Ubicación: {stats.get('output_directory', 'outputs/bi/')}",
                    f"💬 {result.message}"
                ])
                
                # Show validation results if available
                if result.validation_results:
                    validation = result.validation_results
                    if validation.get('valid', False):
                        message_parts.append("✅ Validación del esquema: EXITOSA")
                    else:
                        message_parts.append("⚠️ Validación del esquema: CON ADVERTENCIAS")
                        if validation.get('warnings'):
                            for warning in validation['warnings'][:3]:  # Show first 3 warnings
                                message_parts.append(f"   ⚠️ {warning}")
                
                self._ui.display_message("\n".join(message_parts), "success")
                
            else:
                self._ui.display_message(f"❌ Error en exportación BI: {result.message}", "error")
                
                # Show partial results if available
                if result.files_created:
                    failed_files = [f for f, s in result.files_created.items() if not s]
                    if failed_files:
                        self._ui.display_message(f"❌ Archivos que fallaron: {', '.join(failed_files)}", "warning")
                
        except Exception as e:
            self._logger.error(f"Error exporting BI: {e}")
            self._ui.display_message(f"Error al exportar BI: {e}", "error")
        finally:
            self._ui.wait_for_user()


def main() -> int:
    """Main entry point."""
    try:
        app = DataContaApplication()
        return app.run()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())