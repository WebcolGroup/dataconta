"""
CLI User Interface adapter - Implementation of UserInterface port.
"""

from typing import List, Optional
from datetime import datetime

from src.application.ports.interfaces import UserInterface, Logger
from src.domain.entities.invoice import Invoice, InvoiceFilter


class CLIUserInterfaceAdapter(UserInterface):
    """CLI adapter for user interface operations."""
    
    def __init__(self, logger: Logger):
        self._logger = logger
    
    def show_menu(self) -> str:
        """Display menu and return user selection."""
        try:
            self._display_menu()
            choice = input("\nSeleccione una opción: ").strip()
            return choice
        except KeyboardInterrupt:
            return '0'  # Exit
        except Exception as e:
            self._logger.error(f"Error in menu display: {e}")
            return '0'
    
    def get_invoice_filters(self) -> InvoiceFilter:
        """Get invoice filters from user input."""
        try:
            print("\n📋 Configurar filtros para la consulta de facturas:")
            print("-" * 50)
            
            # Get optional parameters from user
            document_id = self._get_optional_input("ID del documento (opcional): ")
            created_start = self._get_optional_input("Fecha inicio (YYYY-MM-DD, opcional): ")
            created_end = self._get_optional_input("Fecha fin (YYYY-MM-DD, opcional): ")
            
            # Validate dates if provided
            start_date = None
            end_date = None
            
            if created_start:
                try:
                    start_date = datetime.fromisoformat(created_start)
                except ValueError:
                    print("⚠️ Formato de fecha inicio inválido, se ignorará")
                    created_start = None
            
            if created_end:
                try:
                    end_date = datetime.fromisoformat(created_end)
                except ValueError:
                    print("⚠️ Formato de fecha fin inválido, se ignorará")
                    created_end = None
            
            return InvoiceFilter(
                document_id=document_id,
                created_start=start_date,
                created_end=end_date,
                page_size=100
            )
            
        except Exception as e:
            self._logger.error(f"Error getting invoice filters: {e}")
            return InvoiceFilter()  # Return default filter
    
    def display_invoices(self, invoices: List[Invoice]) -> None:
        """Display invoices to user."""
        try:
            if not invoices:
                print("📭 No se encontraron facturas")
                return
            
            print(f"\n📋 Facturas encontradas: {len(invoices)}")
            print("=" * 80)
            
            for i, invoice in enumerate(invoices[:10], 1):  # Show max 10 invoices
                customer_name = "N/A"
                if invoice.customer and invoice.customer.name:
                    customer_name = " ".join(invoice.customer.name)
                elif invoice.customer and invoice.customer.commercial_name:
                    customer_name = invoice.customer.commercial_name
                
                total = invoice.calculate_total() if invoice.items else (invoice.total or 0)
                
                print(f"{i:2d}. 📄 Factura #{invoice.number}")
                print(f"    🆔 ID: {invoice.id}")
                print(f"    👤 Cliente: {customer_name}")
                print(f"    📅 Fecha: {invoice.date.strftime('%Y-%m-%d') if invoice.date else 'N/A'}")
                print(f"    💰 Total: ${total:,.2f}")
                print(f"    📦 Items: {len(invoice.items) if invoice.items else 0}")
                print("-" * 40)
            
            if len(invoices) > 10:
                print(f"... y {len(invoices) - 10} facturas más")
                print("💾 Consulte el archivo de salida para ver todas las facturas")
            
        except Exception as e:
            self._logger.error(f"Error displaying invoices: {e}")
            print(f"❌ Error al mostrar facturas: {e}")
    
    def display_message(self, message: str, level: str = 'info') -> None:
        """Display a message to the user."""
        try:
            icons = {
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌'
            }
            
            icon = icons.get(level, 'ℹ️')
            print(f"{icon} {message}")
            
        except Exception as e:
            self._logger.error(f"Error displaying message: {e}")
            print(f"Error: {message}")
    
    def display_files(self, files: List[str]) -> None:
        """Display list of files to user."""
        try:
            print("\n📁 Archivos en la carpeta 'outputs/':")
            print("-" * 40)
            
            if not files:
                print("📭 No hay archivos en la carpeta 'outputs/'")
                return
            
            for i, filename in enumerate(files, 1):
                # Try to determine file type
                file_type = "📄"
                if filename.endswith('.json'):
                    file_type = "📋"
                elif filename.endswith('.txt'):
                    file_type = "📝"
                
                print(f"{i:2d}. {file_type} {filename}")
            
        except Exception as e:
            self._logger.error(f"Error displaying files: {e}")
            print(f"❌ Error al mostrar archivos: {e}")
    
    def _display_menu(self) -> None:
        """Display the main menu options."""
        print("\n" + "="*50)
        print("🏢 DATACONTA - SIIGO API")
        print("="*50)
        print("1. 📋 Consultar Facturas de Venta")
        print("2. 🔍 Verificar Estado de la API")
        print("3. 📁 Ver Archivos de Salida")
        print("4. 📤 Exportar Facturas a CSV")
        print("5. 🏢 Exportar a Business Intelligence")
        print("0. 🚪 Salir")
        print("="*50)
    
    def _get_optional_input(self, prompt: str) -> Optional[str]:
        """Get optional input from user."""
        try:
            value = input(prompt).strip()
            return value if value else None
        except KeyboardInterrupt:
            return None
        except Exception as e:
            self._logger.error(f"Error getting input: {e}")
            return None
    
    def get_csv_export_parameters(self) -> Optional[dict]:
        """
        Get parameters for CSV export from API data.
        
        Returns:
            Dictionary with export parameters or None if cancelled
        """
        try:
            print("\n📤 Exportar Facturas a CSV")
            print("-" * 30)
            
            # Get date range
            print("📅 Rango de fechas (opcional):")
            start_date = self._get_optional_input("Fecha de inicio (YYYY-MM-DD) [Enter para omitir]: ")
            end_date = self._get_optional_input("Fecha de fin (YYYY-MM-DD) [Enter para omitir]: ")
            
            # Get max records
            max_records_input = self._get_optional_input("Máximo número de registros [Enter para 100]: ")
            try:
                max_records = int(max_records_input) if max_records_input else 100
            except ValueError:
                max_records = 100
            
            # Get custom filename
            custom_filename = self._get_optional_input("Nombre del archivo CSV [Enter para automático]: ")
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "max_records": max_records,
                "custom_filename": custom_filename
            }
            
        except KeyboardInterrupt:
            return None
        except Exception as e:
            self._logger.error(f"Error getting export parameters: {e}")
            return None
    
    def get_bi_export_parameters(self) -> Optional[dict]:
        """
        Get parameters for Business Intelligence export.
        
        Returns:
            Dictionary with BI export parameters or None if cancelled
        """
        try:
            print("\n🏢 Exportar a Business Intelligence")
            print("-" * 40)
            print("📊 Generar modelo estrella para Power BI")
            print("Se crearán múltiples CSVs normalizados en outputs/bi/")
            print()
            
            # Get date range
            print("📅 Rango de fechas (opcional):")
            start_date = self._get_optional_input("Fecha de inicio (YYYY-MM-DD) [Enter para omitir]: ")
            end_date = self._get_optional_input("Fecha de fin (YYYY-MM-DD) [Enter para omitir]: ")
            
            # Get max records
            max_records_input = self._get_optional_input("Máximo número de facturas [Enter para 100]: ")
            try:
                max_records = int(max_records_input) if max_records_input else 100
            except ValueError:
                max_records = 100
            
            # Schema validation option
            validate_input = self._get_optional_input("Validar esquema generado? (s/N) [Enter para No]: ")
            validate_schema = validate_input and validate_input.lower().startswith('s')
            
            print(f"\n📋 Resumen de exportación BI:")
            print(f"   📅 Fechas: {start_date or 'Sin límite'} - {end_date or 'Sin límite'}")
            print(f"   📊 Máximo registros: {max_records}")
            print(f"   ✅ Validar esquema: {'Sí' if validate_schema else 'No'}")
            
            confirm = input("\n¿Proceder con la exportación? (S/n): ").strip()
            if confirm and confirm.lower().startswith('n'):
                return None
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "max_records": max_records,
                "validate_schema": validate_schema
            }
            
        except KeyboardInterrupt:
            return None
        except Exception as e:
            self._logger.error(f"Error getting BI export parameters: {e}")
            return None
    
    def display_api_status(self, status_info: dict) -> None:
        """Display API status information."""
        try:
            print("\n🔍 Estado de la API:")
            print("-" * 30)
            
            # License status
            license_valid = status_info.get('license_valid', False)
            license_icon = "✅" if license_valid else "❌"
            print(f"{license_icon} Licencia: {'Válida' if license_valid else 'Inválida'}")
            
            # API status
            api_available = status_info.get('api_available', False)
            api_icon = "✅" if api_available else "❌"
            print(f"{api_icon} API: {'Disponible' if api_available else 'No disponible'}")
            
            # Message
            message = status_info.get('message', '')
            if message:
                print(f"💬 {message}")
            
        except Exception as e:
            self._logger.error(f"Error displaying API status: {e}")
            print(f"❌ Error al mostrar estado: {e}")
    
    def display_file_info(self, file_info_list: List[dict]) -> None:
        """Display detailed file information."""
        try:
            if not file_info_list:
                print("📭 No hay archivos en la carpeta de salida")
                return
            
            print(f"\n📊 Información detallada de archivos ({len(file_info_list)} archivos):")
            print("-" * 60)
            
            for i, info in enumerate(file_info_list, 1):
                name = info.get('name', 'Unknown')
                size = info.get('size', 0)
                modified = info.get('modified', 'Unknown')
                
                # Format file size
                if size < 1024:
                    size_str = f"{size} bytes"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                
                print(f"{i:2d}. 📄 {name}")
                print(f"     📏 Tamaño: {size_str}")
                print(f"     📅 Modificado: {modified}")
                print()
            
        except Exception as e:
            self._logger.error(f"Error displaying file info: {e}")
            print(f"❌ Error al mostrar información de archivos: {e}")
    
    def wait_for_user(self, message: str = "Presione Enter para continuar...") -> None:
        """Wait for user input before continuing."""
        try:
            input(f"\n{message}")
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._logger.error(f"Error waiting for user: {e}")
    
    def display_exit_message(self) -> None:
        """Display exit message."""
        print("\n👋 ¡Gracias por usar DataConta!")
        print("🔚 Saliendo de la aplicación...")