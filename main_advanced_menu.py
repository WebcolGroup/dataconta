#!/usr/bin/env python3
"""
DATACONTA - Advanced Menu System Integration
Main entry point using the new modular menu system.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.presentation.menu_system import MenuSystem, LicenseType
from src.presentation.menu_config import create_dataconta_menu_system, setup_dataconta_menus

# Import existing infrastructure
from src.infrastructure.config.environment_config import EnvironmentConfigurationProvider
from src.infrastructure.adapters.logger_adapter import LoggerAdapter
from src.infrastructure.adapters.license_validator_adapter import LicenseValidatorAdapter
from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter

# Import specific use cases
from src.application.use_cases.invoice_use_cases import (
    GetInvoicesUseCase, 
    CheckAPIStatusUseCase, 
    ViewStoredFilesUseCase,
    ExportInvoiceToCSVUseCase,
    ExportToBIUseCase
)


class DatacontaMenuIntegrator:
    """Integrates existing DATACONTA functionality with the new menu system"""
    
    def __init__(self):
        self.config = None
        self.logger = None
        self.license_validator = None
        self.api_client = None
        self.invoice_use_cases = None
        self._initialize_infrastructure()
    
    def _initialize_infrastructure(self):
        """Initialize all infrastructure components"""
        try:
            # Setup logging first
            self.logger = LoggerAdapter("DatacontaMenuSystem")
            self.logger.info("Starting infrastructure initialization")
            
            # Load environment configuration
            self.config = EnvironmentConfigurationProvider(self.logger)
            
            # Initialize license validator
            license_url = self.config.get_license_url()
            self.license_validator = LicenseValidatorAdapter(license_url, self.logger)
            
            # Get API credentials
            credentials = self.config.get_api_credentials()
            
            # Initialize API client
            self.api_client = SiigoAPIAdapter(
                base_url=credentials.api_url,
                username=credentials.username,
                access_key=credentials.access_key
            )
            
            # Test API connection
            self.logger.info("Attempting authentication with Siigo API")
            if self.api_client.authenticate():
                self.logger.info("Authentication successful")
            else:
                self.logger.error("Authentication failed")
                return False
            
            self.logger.info("Starting DataConta - Advanced Menu System")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing infrastructure: {str(e)}")
            return False
    
    def consultar_facturas(self):
        """Consultar facturas de venta - integrado con funcionalidad existente"""
        try:
            print("📋 Consultando facturas de venta...")
            
            # Use API client directly
            invoices = self.api_client.get_invoices(limit=100)
            
            if not invoices:
                print("ℹ️ No se encontraron facturas")
                return True
            
            print(f"✅ Se encontraron {len(invoices)} facturas:")
            for i, invoice in enumerate(invoices[:10], 1):  # Show first 10
                number = invoice.get('number', invoice.get('id', 'N/A'))
                date = invoice.get('date', invoice.get('created_at', 'N/A'))
                total = invoice.get('total', invoice.get('amount', 0))
                print(f"  {i}. {number} - {date} - ${total:,.2f}")
            
            if len(invoices) > 10:
                print(f"  ... y {len(invoices) - 10} facturas más")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error consulting invoices: {str(e)}")
            print(f"❌ Error consultando facturas: {str(e)}")
            return False
    
    def exportar_bi(self):
        """Exportar datos para Business Intelligence - integrado"""
        try:
            print("🏢 Iniciando exportación para Business Intelligence...")
            
            # This would need proper implementation
            print("🔧 Funcionalidad de BI en desarrollo...")
            print("ℹ️ Use el sistema actual (main_hexagonal.py) para exportación BI completa")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting BI: {str(e)}")
            print(f"❌ Error exportando BI: {str(e)}")
            return False
    
    def verificar_api(self):
        """Verificar estado de la API - integrado"""
        try:
            print("🔍 Verificando estado de la API...")
            
            # Test API connection
            if self.api_client.test_connection():
                print("✅ API de Siigo: Conectada correctamente")
                credentials = self.config.get_api_credentials()
                print(f"🌐 URL Base: {credentials.api_url}")
                print(f"👤 Usuario: {credentials.username}")
                
                # Test specific endpoints
                print("📡 Probando endpoints específicos...")
                
                # Test invoices endpoint
                try:
                    test_invoices = self.api_client.get_invoices(limit=1)
                    if test_invoices:
                        print("✅ Endpoint de facturas: Funcionando")
                    else:
                        print("⚠️ Endpoint de facturas: Sin datos o error")
                except Exception as e:
                    print(f"❌ Endpoint de facturas: Error - {str(e)}")
                
                return True
            else:
                print("❌ API de Siigo: No conectada")
                print("🔧 Verifique sus credenciales en el archivo .env")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying API: {str(e)}")
            print(f"❌ Error verificando API: {str(e)}")
            return False
    
    def ver_archivos(self):
        """Ver archivos de salida - integrado"""
        try:
            print("📁 Explorando archivos de salida...")
            
            outputs_path = Path("outputs")
            if not outputs_path.exists():
                print("ℹ️ No existe el directorio de salida")
                return True
            
            # List files in outputs directory
            files_found = []
            
            # Check main outputs directory
            for file in outputs_path.glob("*.json"):
                files_found.append(("JSON", file.name, file.stat().st_size))
            
            for file in outputs_path.glob("*.csv"):
                files_found.append(("CSV", file.name, file.stat().st_size))
            
            # Check BI subdirectory
            bi_path = outputs_path / "bi"
            if bi_path.exists():
                for file in bi_path.glob("*.csv"):
                    files_found.append(("BI-CSV", f"bi/{file.name}", file.stat().st_size))
            
            if not files_found:
                print("ℹ️ No se encontraron archivos de salida")
            else:
                print(f"✅ Se encontraron {len(files_found)} archivos:")
                for file_type, file_name, file_size in files_found:
                    size_mb = file_size / 1024 / 1024
                    print(f"  📄 [{file_type}] {file_name} ({size_mb:.2f} MB)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error listing files: {str(e)}")
            print(f"❌ Error listando archivos: {str(e)}")
            return False
    
    def exportar_csv(self):
        """Exportar facturas a CSV - integrado"""
        try:
            print("📤 Exportando facturas a CSV...")
            
            # This would need proper implementation
            print("🔧 Funcionalidad de exportación CSV en desarrollo...")
            print("ℹ️ Use el sistema actual (main_hexagonal.py) para exportación CSV completa")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting CSV: {str(e)}")
            print(f"❌ Error exportando CSV: {str(e)}")
            return False
    
    def create_integrated_menu_system(self) -> MenuSystem:
        """Create menu system with integrated functionality"""
        menu_system = MenuSystem()
        
        # Override menu functions with integrated versions
        from src.presentation import menu_config
        
        # Replace placeholder functions with integrated ones
        menu_config.consultar_facturas = self.consultar_facturas
        menu_config.exportar_bi = self.exportar_bi
        menu_config.verificar_api = self.verificar_api
        menu_config.ver_archivos = self.ver_archivos
        menu_config.exportar_csv = self.exportar_csv
        
        # Setup menus with integrated functions
        setup_dataconta_menus(menu_system)
        
        return menu_system


def main():
    """Main entry point"""
    print("🚀 Inicializando DATACONTA - Sistema Avanzado de Menús...")
    
    # Initialize integrator
    integrator = DatacontaMenuIntegrator()
    
    # Create integrated menu system
    menu_system = integrator.create_integrated_menu_system()
    
    # Show initialization success
    license_display = menu_system.license_validator.get_license_display_name()
    print(f"✅ Inicialización exitosa - Licencia: {license_display}")
    
    # Run menu system
    menu_system.run()
    
    print("🔚 Finalizando aplicación...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 ¡Aplicación terminada por el usuario!")
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        sys.exit(1)