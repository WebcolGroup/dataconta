#!/usr/bin/env python3
"""
DATACONTA - Simple Menu System Demo
Demonstrates the new menu system with basic functionality.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.presentation.menu_system import MenuSystem, LicenseType
from src.presentation.menu_config import create_dataconta_menu_system


def demo_consultar_facturas():
    """Demo function for consulting invoices"""
    print("📋 Consultando facturas de venta...")
    print("✅ Simulando consulta de facturas...")
    print("  1. Factura-001 - 2025-09-15 - $2,436,000.75")
    print("  2. Factura-002 - 2025-09-14 - $1,850,500.25") 
    print("  3. Factura-003 - 2025-09-13 - $3,200,750.50")
    print("📊 Total: 3 facturas encontradas")
    return True


def demo_exportar_bi():
    """Demo function for BI export"""
    print("🏢 Iniciando exportación para Business Intelligence...")
    print("🔄 Procesando facturas...")
    print("📊 Generando modelo estrella...")
    print("✅ Exportación BI exitosa!")
    print("📁 Archivos creados:")
    print("  ✓ fact_invoices.csv")
    print("  ✓ dim_clients.csv")
    print("  ✓ dim_products.csv")
    print("📂 Ubicación: outputs/bi/")
    return True


def demo_verificar_api():
    """Demo function for API verification"""
    print("🔍 Verificando estado de la API...")
    print("✅ API de Siigo: Conectada correctamente")
    print("🌐 URL Base: https://api.siigo.com/v1/")
    print("👤 Usuario: demo@dataconta.com")
    print("📡 Probando endpoints específicos...")
    print("✅ Endpoint de facturas: Funcionando")
    print("✅ Endpoint de clientes: Funcionando")
    return True


def demo_ver_archivos():
    """Demo function for viewing output files"""
    print("📁 Explorando archivos de salida...")
    print("✅ Se encontraron 6 archivos:")
    print("  📄 [JSON] invoices_100_items_20250915.json (2.45 MB)")
    print("  📄 [CSV] invoices_export_50_items_20250915.csv (1.23 MB)")
    print("  📄 [BI-CSV] bi/fact_invoices.csv (0.89 MB)")
    print("  📄 [BI-CSV] bi/dim_clients.csv (0.05 MB)")
    print("  📄 [BI-CSV] bi/dim_products.csv (0.12 MB)")
    print("  📄 [BI-CSV] bi/dim_dates.csv (0.02 MB)")
    return True


def demo_exportar_csv():
    """Demo function for CSV export"""
    print("📤 Exportando facturas a CSV...")
    print("🔄 Procesando 100 facturas...")
    print("💾 Aplicando formato con comas decimales...")
    print("✅ Exportación CSV exitosa!")
    print("📊 Facturas exportadas: 100")
    print("📁 Archivo creado: outputs/invoices_export_100_items_20250915.csv")
    return True


def demo_exportar_pdf():
    """Demo function for PDF export"""
    print("📄 Exportando informe a PDF...")
    print("🎨 Generando diseño profesional...")
    print("📊 Incluyendo gráficos y tablas...")
    print("✅ Informe PDF generado exitosamente!")
    print("📁 Archivo creado: outputs/informe_facturas_20250915.pdf")
    return True


def demo_configuracion():
    """Demo function for system configuration"""
    print("⚙️ Configuración del sistema...")
    print("📋 Configuración actual:")
    print("  🔑 Licencia: Gratuita")
    print("  🌐 API URL: https://api.siigo.com/v1/")
    print("  👤 Usuario: demo@dataconta.com")
    print("  📂 Directorio de salida: ./outputs/")
    print("  🔍 Formato decimal: Coma (,)")
    print("  📊 Límite por defecto: 100 registros")
    return True


def demo_enviar_ollama():
    """Demo function for Ollama integration"""
    print("🤖 Enviando datos a Ollama...")
    print("📤 Preparando datos de facturas...")
    print("🧠 Conectando con modelo de IA local...")
    print("✅ Datos enviados exitosamente!")
    print("💬 Ollama está procesando la información...")
    print("⏳ Tiempo estimado: 30 segundos")
    return True


def demo_consultar_ollama():
    """Demo function for Ollama query"""
    print("💬 Consultando respuesta de Ollama...")
    print("🤖 Respuesta de IA:")
    print("┌─────────────────────────────────────────────┐")
    print("│ ANÁLISIS INTELIGENTE DE FACTURAS            │")
    print("├─────────────────────────────────────────────┤")
    print("│ • Tendencia: Incremento del 15% en ventas   │")
    print("│ • Cliente principal: Empresa XYZ Corp       │")
    print("│ • Producto top: Servicios profesionales     │")
    print("│ • Recomendación: Enfocar en Q4 2025        │")
    print("└─────────────────────────────────────────────┘")
    return True


def setup_demo_menu_system() -> MenuSystem:
    """Create demo menu system with mock functions"""
    menu_system = create_dataconta_menu_system()
    
    # Replace the placeholder functions with demo functions
    from src.presentation import menu_config
    
    menu_config.consultar_facturas = demo_consultar_facturas
    menu_config.exportar_bi = demo_exportar_bi
    menu_config.verificar_api = demo_verificar_api
    menu_config.ver_archivos = demo_ver_archivos
    menu_config.exportar_csv = demo_exportar_csv
    menu_config.exportar_pdf = demo_exportar_pdf
    menu_config.configuracion = demo_configuracion
    menu_config.enviar_ollama = demo_enviar_ollama
    menu_config.consultar_ollama = demo_consultar_ollama
    
    # Recreate menu system with updated functions
    demo_menu = MenuSystem()
    menu_config.setup_dataconta_menus(demo_menu)
    
    return demo_menu


def main():
    """Main entry point for demo"""
    print("🚀 DATACONTA - SISTEMA AVANZADO DE MENÚS (DEMO)")
    print("="*60)
    print("📌 Esta es una demostración del nuevo sistema de menús")
    print("🔧 Las funciones mostradas son simulaciones para pruebas")
    print("="*60)
    
    # Create demo menu system
    menu_system = setup_demo_menu_system()
    
    # Show license info
    license_display = menu_system.license_validator.get_license_display_name()
    print(f"✅ Sistema inicializado - Licencia: {license_display}")
    
    # Run menu system
    menu_system.run()
    
    print("🔚 Finalizando demostración...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 ¡Demostración terminada por el usuario!")
    except Exception as e:
        print(f"❌ Error en demostración: {str(e)}")
        sys.exit(1)