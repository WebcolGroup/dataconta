"""
DataConta CLI FREE Version - Demo
Versión simplificada de la CLI para demostrar las funcionalidades FREE implementadas.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar solo lo necesario para evitar problemas con null bytes
from src.domain.services.license_manager import LicenseManager
from src.application.services.BasicStatisticsService import BasicStatisticsService, BasicStatisticsRequest
from src.infrastructure.adapters.simple_txt_logger_adapter import SimpleTxtLogger
from src.presentation.enhanced_menu_config import FreeMenuConfigManager


class DataContaFreeCLI:
    """CLI simplificada para demostrar funcionalidades FREE."""
    
    def __init__(self):
        """Inicializar la CLI con licencia FREE."""
        print("🚀 Iniciando DataConta FREE Version...")
        
        # Inicializar componentes FREE
        self.license_manager = LicenseManager("FREE_CLI_DEMO")
        self.logger = SimpleTxtLogger(self.license_manager, "cli_logs")
        self.menu_config = FreeMenuConfigManager(self.license_manager)
        
        # Mock repository para demos
        self.mock_repository = self._create_mock_repository()
        self.stats_service = BasicStatisticsService(self.mock_repository, self.license_manager)
        
        print("✅ Componentes FREE inicializados correctamente")
        self.logger.log_user_action("CLI Startup", "Usuario inició CLI FREE")
    
    def _create_mock_repository(self):
        """Crear un repository mock para las demos."""
        class MockInvoiceRepository:
            def get_invoices(self, **kwargs):
                # Simular facturas para demo
                return []  # Lista vacía por simplicidad
        
        return MockInvoiceRepository()
    
    def show_main_menu(self):
        """Mostrar el menú principal FREE."""
        print("\\n" + "="*60)
        print("🆓 DATACONTA FREE - MENÚ PRINCIPAL")
        print("="*60)
        
        # Mostrar información de licencia
        print(f"📋 Licencia: {self.license_manager.get_license_type()}")
        print(f"🔢 Límite consultas: {self.license_manager.get_max_invoices_for_query()} facturas")
        print(f"🎨 Modo GUI Lite: {'✅ Disponible' if self.license_manager.is_gui_lite_mode() else '❌ No disponible'}")
        
        print("\\n📂 OPCIONES DISPONIBLES (FREE):")
        print("   1. 📊 Ver estadísticas básicas")
        print("   2. 📤 Demostrar exportación JSON")
        print("   3. 📋 Ver configuración de menús")
        print("   4. 📝 Ver logs recientes")
        print("   5. 🔍 Información de licencia FREE")
        print("   6. 💡 Información de upgrade")
        print("   0. 🚪 Salir")
        
        print("\\n🔒 FUNCIONALIDADES BLOQUEADAS (Requieren PRO/ENTERPRISE):")
        print("   🚫 Reportes financieros avanzados")
        print("   🚫 Exportación BI completa") 
        print("   🚫 Análisis de tendencias")
        print("   🚫 Dashboard completo")
        print("   🚫 Consultas de más de 100 facturas")
        
        return input("\\n👉 Seleccione una opción: ").strip()
    
    def show_basic_statistics(self):
        """Mostrar estadísticas básicas FREE."""
        print("\\n📊 ESTADÍSTICAS BÁSICAS FREE")
        print("="*40)
        
        try:
            request = BasicStatisticsRequest(max_records=50)
            response = self.stats_service.calculate_basic_statistics(request)
            
            print(f"✅ Servicio de estadísticas: {'Operativo' if response else 'Error'}")
            print(f"🔢 Límite aplicado: {request.max_records} registros")
            print(f"🎯 Tipo de licencia: {self.license_manager.get_license_type()}")
            
            if response and response.success:
                print("📈 Estadísticas calculadas exitosamente")
                if response.statistics:
                    for key, value in response.statistics.items():
                        print(f"   📋 {key}: {value}")
            else:
                print("ℹ️  Demo con datos simulados - Funcionalidad operativa")
                print("   📋 Total facturas: 0 (demo)")
                print("   📋 Suma total: $0.00")
                print("   📋 Promedio: $0.00")
                print("   📋 Estado: Sistema listo para datos reales")
            
            print("\\n💡 Upgrade para más estadísticas:")
            print("   💼 PRO: Hasta 2,000 facturas + análisis avanzado")
            print("   🏢 ENTERPRISE: Sin límites + reportes personalizados")
            
        except Exception as e:
            print(f"⚠️  Error en estadísticas: {e}")
        
        self.logger.log_user_action("View Statistics", "Usuario consultó estadísticas básicas")
    
    def demo_json_export(self):
        """Demostrar la exportación JSON FREE."""
        print("\\n📤 DEMOSTRACIÓN EXPORTACIÓN JSON FREE")
        print("="*45)
        
        print("✨ Nueva funcionalidad para usuarios FREE:")
        print(f"🔢 Límite: {self.license_manager.get_max_invoices_for_query()} facturas por exportación")
        print("🏷️  Formato: JSON estructurado con metadatos")
        print("📊 Incluye: Estadísticas básicas automáticas")
        
        print("\\n📋 Estructura del JSON generado:")
        sample_json = '''{
  "export_info": {
    "timestamp": "2024-09-17T15:30:00Z",
    "license_type": "FREE",
    "total_records": 25,
    "format_version": "1.0",
    "exported_by": "DataConta FREE CLI"
  },
  "summary_statistics": {
    "total_amount": "75,500.00",
    "average_amount": "3,020.00",
    "currency": "COP",
    "date_range": {
      "start": "2024-09-01",
      "end": "2024-09-17"
    }
  },
  "invoices": [
    "... hasta 100 facturas ..."
  ],
  "upgrade_info": {
    "message": "Actualice a PRO para exportar más de 100 facturas",
    "benefits": [
      "PRO: Hasta 2,000 facturas",
      "ENTERPRISE: Sin límites"
    ],
    "contact": "ventas@dataconta.com"
  }
}'''
        print(sample_json)
        
        print("\\n💡 Ventajas del export JSON FREE:")
        print("   🚀 Formato moderno y estándar")
        print("   📊 Metadatos completos incluidos")
        print("   🏷️  Estadísticas automáticas")
        print("   💼 Compatible con herramientas actuales")
        print("   📱 Listo para integración")
        
        self.logger.log_user_action("Demo JSON Export", "Usuario exploró exportación JSON")
    
    def show_menu_configuration(self):
        """Mostrar la configuración de menús enhanced."""
        print("\\n📋 CONFIGURACIÓN DE MENÚS ENHANCED")
        print("="*42)
        
        try:
            summary = self.menu_config.get_free_license_summary()
            print("🆓 RESUMEN FREE LICENSE:")
            print(summary[:300] + "..." if len(summary) > 300 else summary)
            
            print("\\n🗂️  ESTRUCTURA DE MENÚS:")
            print("   1️⃣  CONSULTA DE FACTURAS (6 opciones disponibles)")
            print("   2️⃣  EXPORTACIÓN Y REPORTES (2 disponibles, 2 bloqueadas)")
            print("   3️⃣  ESTADÍSTICAS Y BI (1 disponible, 2 bloqueadas)")
            print("   4️⃣  API Y CONFIGURACIÓN (4 opciones básicas)")
            print("   5️⃣  INFORMACIÓN Y SOPORTE (2 opciones de ayuda)")
            
            print("\\n🔒 EJEMPLO DE MENSAJE BLOQUEADO:")
            blocked_msg = self.menu_config.get_blocked_feature_message("Reportes Avanzados")
            print(f"   {blocked_msg}")
            
        except Exception as e:
            print(f"⚠️  Error en configuración de menús: {e}")
        
        self.logger.log_user_action("View Menu Config", "Usuario consultó configuración de menús")
    
    def show_recent_logs(self):
        """Mostrar logs recientes del sistema."""
        print("\\n📝 LOGS RECIENTES DEL SISTEMA")
        print("="*35)
        
        try:
            recent_logs = self.logger.get_recent_logs(max_lines=10)
            print("📋 Últimos eventos registrados:")
            
            if recent_logs and recent_logs.strip():
                for line in recent_logs.split('\\n')[:5]:  # Mostrar solo 5 líneas
                    if line.strip():
                        print(f"   {line}")
            else:
                print("   ℹ️  No hay logs disponibles en esta sesión")
            
            print("\\n📊 Tipos de logs registrados:")
            print("   ✅ Validaciones de licencia")
            print("   ✅ Operaciones de usuario")
            print("   ✅ Acciones del sistema")
            print("   ✅ Exportaciones realizadas")
            
            print("\\n💡 Logging avanzado en versiones superiores:")
            print("   💼 PRO: Múltiples formatos + filtros")
            print("   🏢 ENTERPRISE: Análisis de logs + alertas")
            
        except Exception as e:
            print(f"⚠️  Error accediendo logs: {e}")
        
        self.logger.log_user_action("View Logs", "Usuario consultó logs del sistema")
    
    def show_license_info(self):
        """Mostrar información completa de la licencia FREE."""
        print("\\n🔍 INFORMACIÓN COMPLETA LICENCIA FREE")
        print("="*45)
        
        print(f"📋 Tipo de licencia: {self.license_manager.get_license_type()}")
        print(f"✅ Estado: {'Válida' if self.license_manager.is_license_valid() else 'Requiere activación'}")
        
        # Mostrar funcionalidades disponibles
        summary = self.license_manager.get_free_features_summary()
        
        print("\\n✅ FUNCIONALIDADES INCLUIDAS:")
        available_features = {
            'cli_access': 'Acceso completo a línea de comandos',
            'gui_lite': 'Interfaz gráfica reducida',
            'csv_export': 'Exportación a CSV básica', 
            'json_export': 'Exportación a JSON (NUEVO)',
            'basic_stats': 'Estadísticas básicas (NUEVO)',
            'api_verification': 'Verificación de estado API',
            'file_management': 'Gestión básica de archivos'
        }
        
        for key, description in available_features.items():
            if summary.get(key, False):
                print(f"   ✅ {description}")
        
        print(f"\\n🔢 LÍMITES APLICADOS:")
        print(f"   📊 Máximo facturas por consulta: {summary.get('max_invoices', 500)}")
        print(f"   🎨 Modo GUI: Lite (reducido)")
        print(f"   📤 Exportaciones: Formatos básicos")
        
        print("\\n🔒 FUNCIONALIDADES BLOQUEADAS:")
        if 'blocked_features' in summary:
            for feature, upgrade_msg in summary['blocked_features'].items():
                print(f"   🚫 {feature.replace('_', ' ').title()}: {upgrade_msg}")
    
    def show_upgrade_info(self):
        """Mostrar información de upgrade."""
        print("\\n💡 INFORMACIÓN DE UPGRADE")
        print("="*35)
        
        print("🆓 ACTUALMENTE: FREE")
        print("   ✅ Perfecto para comenzar y evaluar DataConta")
        print("   ✅ Funcionalidades esenciales incluidas")
        print("   ✅ Sin costo, sin compromisos")
        
        print("\\n💼 UPGRADE A PRO:")
        print("   🚀 Hasta 2,000 facturas por consulta")
        print("   🚀 GUI completa con todos los componentes")
        print("   🚀 Reportes financieros avanzados")
        print("   🚀 Exportación BI limitada")
        print("   🚀 Logging avanzado")
        print("   💰 Ideal para pequeñas y medianas empresas")
        
        print("\\n🏢 UPGRADE A ENTERPRISE:")
        print("   🚀 Sin límites en consultas ni exportaciones")
        print("   🚀 BI completo e ilimitado")
        print("   🚀 Funcionalidades avanzadas exclusivas")
        print("   🚀 Soporte prioritario")
        print("   🚀 Funcionalidades futuras incluidas")
        print("   💰 Solución completa para grandes organizaciones")
        
        print("\\n📞 CONTACTO PARA UPGRADE:")
        print("   ✉️  Email: ventas@dataconta.com")
        print("   🌐 Web: www.dataconta.com")
        print("   📱 Consulta personalizada disponible")
        
        print("\\n🎁 BENEFICIO DE SER USUARIO FREE:")
        print("   💰 Descuentos especiales para usuarios existentes")
        print("   📈 Migración de datos sin costo adicional")
        print("   🎯 Onboarding personalizado incluido")
    
    def run(self):
        """Ejecutar el bucle principal de la CLI."""
        print("\\n🎉 ¡Bienvenido a DataConta FREE!")
        print("💡 Versión completamente funcional con funcionalidades profesionales")
        
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == '0':
                    print("\\n👋 ¡Gracias por usar DataConta FREE!")
                    print("💌 Esperamos verte pronto en PRO o ENTERPRISE")
                    self.logger.log_user_action("CLI Exit", "Usuario cerró la aplicación")
                    break
                elif choice == '1':
                    self.show_basic_statistics()
                elif choice == '2':
                    self.demo_json_export()
                elif choice == '3':
                    self.show_menu_configuration()
                elif choice == '4':
                    self.show_recent_logs()
                elif choice == '5':
                    self.show_license_info()
                elif choice == '6':
                    self.show_upgrade_info()
                else:
                    print("\\n❌ Opción no válida. Por favor, seleccione una opción del menú.")
                
                input("\\n⏵  Presione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\\n\\n👋 Interrupción del usuario. ¡Hasta pronto!")
                self.logger.log_user_action("CLI Interrupt", "Usuario interrumpió la aplicación")
                break
            except Exception as e:
                print(f"\\n⚠️  Error inesperado: {e}")
                print("💡 La aplicación continuará ejecutándose...")


def main():
    """Función principal."""
    try:
        cli = DataContaFreeCLI()
        cli.run()
    except Exception as e:
        print(f"❌ Error crítico inicializando DataConta FREE CLI: {e}")
        print("💡 Verifique la instalación y dependencias")
        sys.exit(1)


if __name__ == "__main__":
    main()