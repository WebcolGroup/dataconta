"""
CLI User Interface adapter - Implementation of UserInterface port.
"""

from typing import List, Optional
from datetime import datetime

from src.application.ports.interfaces import UserInterface, Logger
from src.domain.entities.invoice import Invoice, InvoiceFilter
from src.domain.services.license_manager import LicenseManager


class CLIUserInterfaceAdapter(UserInterface):
    """CLI adapter for user interface operations."""
    
    def __init__(self, logger: Logger, license_manager: Optional[LicenseManager] = None):
        self._logger = logger
        self._license_manager = license_manager
    
    def set_license_manager(self, license_manager: LicenseManager) -> None:
        """Set the license manager for feature access control."""
        self._license_manager = license_manager
    
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
        """Display the main menu options based on license permissions."""
        license_display = "Sin licencia"
        license_icon = "❌"
        
        if self._license_manager and self._license_manager.is_license_valid():
            license_display = self._license_manager.get_license_display_name()
            license_icon = "✅"
        
        print("\n" + "="*60)
        print("🏢 DATACONTA - SIIGO API")
        print("="*60)
        print(f"{license_icon} Licencia: {license_display}")
        print("-" * 60)
        print("1. 📋 Consultar Facturas de Venta")
        print("2. 🔍 Verificar Estado de la API")
        print("3. 📁 Ver Archivos de Salida")
        print("4. 📤 Exportar Facturas a CSV")
        
        # Show BI export only if license allows it
        if self._license_manager and self._license_manager.can_export_bi():
            bi_limit = self._license_manager.get_max_invoices_for_bi()
            if bi_limit is None:
                bi_note = "Ilimitado"
            else:
                bi_note = f"hasta {bi_limit:,} facturas"
            print(f"5. 🏢 Exportar a Business Intelligence ({bi_note})")
        else:
            print("5. 🏢 Exportar a Business Intelligence (❌ Requiere Professional+)")
        
        # Show GUI launch only if license allows it
        if self._license_manager and self._license_manager.can_access_gui():
            print("6. 🖥️ Abrir Interfaz Gráfica")
        else:
            print("6. 🖥️ Abrir Interfaz Gráfica (❌ Requiere Professional+)")
        
        # Show financial reports if available
        if self._license_manager and self._license_manager.can_generate_financial_reports():
            print("7. 📊 Generar Informes Financieros")
        else:
            print("7. 📊 Generar Informes Financieros (❌ Requiere Professional+)")
        
        # Always show license info and upgrade options
        print("8. ℹ️ Información de Licencia")
        print("9. ⬆️ Actualizar Licencia")
        print("0. 🚪 Salir")
        print("="*60)
        
        # Show upgrade message if applicable
        if self._license_manager and self._license_manager.is_license_valid():
            license_type = self._license_manager.get_license_type()
            if license_type.name in ["FREE", "PROFESSIONAL"]:
                print("💡 Consejo:", self._license_manager.get_upgrade_message().split('\n')[0])
                print("-" * 60)
    
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
            
            # Show license limits if available
            if self._license_manager and self._license_manager.is_license_valid():
                max_query_invoices = self._license_manager.get_max_invoices_for_query()
                print(f"📝 Licencia {self._license_manager.get_license_display_name()}: Máximo {max_query_invoices:,} facturas por consulta")
            
            # Get date range
            print("📅 Rango de fechas (opcional):")
            start_date = self._get_optional_input("Fecha de inicio (YYYY-MM-DD) [Enter para omitir]: ")
            end_date = self._get_optional_input("Fecha de fin (YYYY-MM-DD) [Enter para omitir]: ")
            
            # Get max records with license validation
            max_records_input = self._get_optional_input("Máximo número de registros [Enter para 100]: ")
            try:
                max_records = int(max_records_input) if max_records_input else 100
            except ValueError:
                max_records = 100
            
            # Validate against license limits
            if self._license_manager and self._license_manager.is_license_valid():
                max_allowed = self._license_manager.get_max_invoices_for_query()
                if max_records > max_allowed:
                    print(f"⚠️ Ajustando a límite de licencia: {max_allowed:,} registros")
                    max_records = max_allowed
            
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
            # Check license permissions first
            if not self._license_manager or not self._license_manager.can_export_bi():
                print("\n❌ Exportación BI no disponible")
                if self._license_manager:
                    print(f"Su licencia {self._license_manager.get_license_display_name()} no incluye esta funcionalidad")
                    print(self._license_manager.get_upgrade_message())
                else:
                    print("No hay licencia válida configurada")
                return None
            
            print("\n🏢 Exportar a Business Intelligence")
            print("-" * 40)
            print("📊 Generar modelo estrella para Power BI")
            print("Se crearán múltiples CSVs normalizados en outputs/bi/")
            
            # Show license limits
            max_bi_invoices = self._license_manager.get_max_invoices_for_bi()
            if max_bi_invoices is None:
                print(f"✅ Licencia {self._license_manager.get_license_display_name()}: Exportación BI ilimitada")
            else:
                print(f"⚠️ Licencia {self._license_manager.get_license_display_name()}: Máximo {max_bi_invoices:,} facturas para BI")
            print()
            
            # Get date range
            print("📅 Rango de fechas (opcional):")
            start_date = self._get_optional_input("Fecha de inicio (YYYY-MM-DD) [Enter para omitir]: ")
            end_date = self._get_optional_input("Fecha de fin (YYYY-MM-DD) [Enter para omitir]: ")
            
            # Get max records with license validation
            max_records_input = self._get_optional_input("Máximo número de facturas [Enter para 100]: ")
            try:
                max_records = int(max_records_input) if max_records_input else 100
            except ValueError:
                max_records = 100
            
            # Validate against license limits
            if max_bi_invoices is not None and max_records > max_bi_invoices:
                print(f"⚠️ Ajustando a límite de licencia: {max_bi_invoices:,} facturas")
                max_records = max_bi_invoices
            
            # Schema validation option
            validate_input = self._get_optional_input("Validar esquema generado? (s/N) [Enter para No]: ")
            validate_schema = validate_input and validate_input.lower().startswith('s')
            
            print(f"\n📋 Resumen de exportación BI:")
            print(f"   📅 Fechas: {start_date or 'Sin límite'} - {end_date or 'Sin límite'}")
            print(f"   📊 Máximo registros: {max_records:,}")
            print(f"   ✅ Validar esquema: {'Sí' if validate_schema else 'No'}")
            print(f"   📝 Licencia: {self._license_manager.get_license_display_name()}")
            
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
            license_type = status_info.get('license_type', 'Unknown')
            license_icon = "✅" if license_valid else "❌"
            print(f"{license_icon} Licencia: {license_type} {'(Válida)' if license_valid else '(Inválida)'}")
            
            # API status
            api_available = status_info.get('api_available', False)
            api_icon = "✅" if api_available else "❌"
            print(f"{api_icon} API: {'Disponible' if api_available else 'No disponible'}")
            
            # License summary if available
            license_summary = status_info.get('license_summary', {})
            if license_summary:
                print(f"\n📋 Resumen de licencia:")
                print(f"   🖥️ Acceso GUI: {'Sí' if license_summary.get('gui_access', False) else 'No'}")
                print(f"   📊 Informes financieros: {'Sí' if license_summary.get('financial_reports', False) else 'No'}")
                print(f"   🏢 Exportación BI: {'Sí' if license_summary.get('bi_export', False) else 'No'}")
                
                max_query = license_summary.get('max_invoices_query', 0)
                max_bi = license_summary.get('max_invoices_bi')
                
                print(f"   📋 Límite consultas: {max_query:,} facturas")
                if max_bi is None:
                    print(f"   🏢 Límite BI: Ilimitado")
                else:
                    print(f"   🏢 Límite BI: {max_bi:,} facturas")
            
            # Message
            message = status_info.get('message', '')
            if message:
                print(f"\n💬 {message}")
            
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
    
    # ========================================================================================
    # LICENSE MANAGEMENT METHODS
    # ========================================================================================
    
    def display_license_info(self) -> None:
        """Display detailed license information."""
        try:
            print("\n📋 Información de Licencia")
            print("=" * 50)
            
            if not self._license_manager:
                print("❌ No hay gestor de licencias configurado")
                return
            
            if not self._license_manager.is_license_valid():
                print("❌ No hay licencia válida configurada")
                print("\n🔧 Para configurar su licencia:")
                print("1. Edite el archivo .env")
                print("2. Agregue su LICENSE_KEY=su_clave_de_licencia")
                print("3. Reinicie la aplicación")
                return
            
            license_summary = self._license_manager.get_license_summary()
            license_type = self._license_manager.get_license_type()
            
            print(f"✅ Licencia activa: {license_summary['type']}")
            print(f"📅 Estado: {license_summary['status']}")
            
            if license_summary.get('expires_at'):
                print(f"⏰ Expira: {license_summary['expires_at']}")
            else:
                print("⏰ Expira: Sin vencimiento")
            
            print(f"\n🎯 Funcionalidades disponibles:")
            print(f"   🖥️ Interfaz Gráfica: {'✅ Sí' if license_summary['gui_access'] else '❌ No'}")
            print(f"   📊 Informes Financieros: {'✅ Sí' if license_summary['financial_reports'] else '❌ No'}")
            print(f"   🏢 Exportación BI: {'✅ Sí' if license_summary['bi_export'] else '❌ No'}")
            print(f"   🔬 Funciones Avanzadas: {'✅ Sí' if license_summary['advanced_features'] else '❌ No'}")
            
            print(f"\n📈 Límites de uso:")
            max_query = license_summary['max_invoices_query']
            max_bi = license_summary['max_invoices_bi']
            
            print(f"   📋 Consultas: {max_query:,} facturas máximo")
            if max_bi is None:
                print(f"   🏢 Exportación BI: Ilimitada")
            elif max_bi == 0:
                print(f"   🏢 Exportación BI: No disponible")
            else:
                print(f"   🏢 Exportación BI: {max_bi:,} facturas máximo")
            
            print(f"\n🔧 Configuración técnica:")
            print(f"   📡 Validación online: {'Sí' if license_summary['online_validation'] else 'No'}")
            print(f"   📝 Logging avanzado: {'Sí' if license_summary['advanced_logging'] else 'No'}")
            
            # Show features list
            features = license_summary.get('features', [])
            if features:
                print(f"\n🎨 Características incluidas:")
                for feature in features:
                    print(f"   ✓ {feature}")
            
            # Show upgrade message if applicable
            if license_type.name in ["FREE", "PROFESSIONAL"]:
                print(f"\n💡 {self._license_manager.get_upgrade_message()}")
            
        except Exception as e:
            self._logger.error(f"Error displaying license info: {e}")
            print(f"❌ Error al mostrar información de licencia: {e}")
    
    def display_upgrade_options(self) -> None:
        """Display license upgrade options and comparison table."""
        try:
            print("\n⬆️ Opciones de Actualización de Licencia")
            print("=" * 70)
            
            print("📊 Comparación de planes:")
            print("-" * 70)
            print(f"{'Característica':<25} {'GRATUITO':<15} {'PROFESIONAL':<15} {'ENTERPRISE':<15}")
            print("-" * 70)
            print(f"{'Interfaz CLI':<25} {'✅ Sí':<15} {'✅ Sí':<15} {'✅ Sí':<15}")
            print(f"{'Interfaz Gráfica':<25} {'❌ No':<15} {'✅ Sí':<15} {'✅ Sí':<15}")
            print(f"{'Consultas máximas':<25} {'500':<15} {'2,000':<15} {'Ilimitadas':<15}")
            print(f"{'Exportación CSV':<25} {'✅ Sí':<15} {'✅ Sí':<15} {'✅ Sí':<15}")
            print(f"{'Exportación BI':<25} {'❌ No':<15} {'✅ Limitada':<15} {'✅ Ilimitada':<15}")
            print(f"{'Informes Financieros':<25} {'❌ No':<15} {'✅ Sí':<15} {'✅ Sí':<15}")
            print(f"{'Multiusuario':<25} {'❌ No':<15} {'❌ No':<15} {'✅ Sí':<15}")
            print(f"{'API REST':<25} {'❌ No':<15} {'❌ No':<15} {'✅ Sí':<15}")
            print(f"{'IA Predictiva':<25} {'❌ No':<15} {'❌ No':<15} {'✅ Sí':<15}")
            print("-" * 70)
            
            if self._license_manager and self._license_manager.is_license_valid():
                current_type = self._license_manager.get_license_type()
                print(f"📍 Su licencia actual: {current_type.display_name}")
                print(f"\n💡 {self._license_manager.get_upgrade_message()}")
            else:
                print("📍 Actualmente sin licencia válida")
                print("\n💡 Comience con una licencia GRATUITA contactando al soporte")
            
            print(f"\n📞 Para actualizar su licencia:")
            print("   📧 Email: soporte@dataconta.com")
            print("   🌐 Web: https://dataconta.com/upgrade")
            print("   📱 WhatsApp: +57 300 123 4567")
            
        except Exception as e:
            self._logger.error(f"Error displaying upgrade options: {e}")
            print(f"❌ Error al mostrar opciones de actualización: {e}")
    
    def handle_feature_restriction(self, feature_name: str, required_license: str = "Professional") -> bool:
        """
        Handle access to restricted features and display appropriate messages.
        
        Args:
            feature_name: Name of the feature being accessed
            required_license: Minimum license level required
            
        Returns:
            True if access is allowed, False otherwise
        """
        try:
            if not self._license_manager:
                print(f"\n❌ Funcionalidad '{feature_name}' no disponible")
                print("No hay gestor de licencias configurado")
                return False
            
            if not self._license_manager.is_license_valid():
                print(f"\n❌ Funcionalidad '{feature_name}' no disponible")
                print("No hay licencia válida configurada")
                print("\n🔧 Configure su licencia en el archivo .env")
                return False
            
            # Check specific feature access
            current_license = self._license_manager.get_license_display_name()
            
            if feature_name.lower() == "gui" and not self._license_manager.can_access_gui():
                print(f"\n❌ Interfaz gráfica no disponible")
                print(f"Su licencia {current_license} no incluye acceso a la GUI")
                print(f"Se requiere licencia {required_license} o superior")
                print(f"\n{self._license_manager.get_upgrade_message()}")
                return False
            
            if feature_name.lower() == "bi" and not self._license_manager.can_export_bi():
                print(f"\n❌ Exportación BI no disponible")
                print(f"Su licencia {current_license} no incluye exportación BI")
                print(f"Se requiere licencia {required_license} o superior")
                print(f"\n{self._license_manager.get_upgrade_message()}")
                return False
            
            if feature_name.lower() == "financial_reports" and not self._license_manager.can_generate_financial_reports():
                print(f"\n❌ Informes financieros no disponibles")
                print(f"Su licencia {current_license} no incluye informes financieros")
                print(f"Se requiere licencia {required_license} o superior")
                print(f"\n{self._license_manager.get_upgrade_message()}")
                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error handling feature restriction: {e}")
            print(f"❌ Error al validar acceso a funcionalidad: {e}")
            return False