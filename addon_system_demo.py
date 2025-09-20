"""
Demo de integración completa del Sistema de Addons con DataConta
Demuestra cómo integrar el sistema de addons sin romper funcionalidad existente.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Asegurar que el proyecto esté en el path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.application.ports.interfaces import Logger, LogLevel
from src.infrastructure.factories.addon_factory import AddonFactory
from src.infrastructure.adapters.addon_menu_integration import EnhancedDynamicMenuManager
from src.infrastructure.adapters.addon_manifest_validator import validate_addon_manifest


class ConsoleLogger(Logger):
    """Logger simple para consola para la demo."""
    
    def __init__(self, level: LogLevel = LogLevel.INFO):
        self.level = level
    
    def info(self, message: str):
        if self.level.value <= LogLevel.INFO.value:
            print(f"ℹ️  {message}")
    
    def error(self, message: str):
        if self.level.value <= LogLevel.ERROR.value:
            print(f"❌ {message}")
    
    def warning(self, message: str):
        if self.level.value <= LogLevel.WARNING.value:
            print(f"⚠️  {message}")
    
    def debug(self, message: str):
        if self.level.value <= LogLevel.DEBUG.value:
            print(f"🐛 {message}")


class AddonSystemDemo:
    """
    Demo completa del sistema de addons integrado con DataConta.
    
    Muestra:
    - Inicialización del sistema
    - Validación de addons
    - Carga de addons
    - Integración con menús
    - Ejecución de acciones
    - Estadísticas y monitoreo
    """
    
    def __init__(self, addons_path: str = "addons"):
        """
        Inicializar demo del sistema de addons.
        
        Args:
            addons_path: Ruta donde están los addons
        """
        self.addons_path = addons_path
        self.logger = ConsoleLogger(LogLevel.INFO)
        self.addon_system = None
        self.menu_manager = None
        
    def run_complete_demo(self):
        """Ejecutar demo completa del sistema de addons."""
        print("🚀 DATACONTA - SISTEMA DE ADDONS DEMO")
        print("="*50)
        
        try:
            # 1. Inicializar sistema
            print("\n🔧 1. INICIALIZANDO SISTEMA DE ADDONS...")
            if not self._initialize_addon_system():
                print("❌ Error inicializando sistema")
                return False
            
            # 2. Validar addons
            print("\n🔍 2. VALIDANDO ADDONS...")
            self._validate_addons()
            
            # 3. Cargar addons
            print("\n📦 3. CARGANDO ADDONS...")
            loaded_count = self._load_addons()
            
            # 4. Integrar menús
            print("\n🎛️ 4. INTEGRANDO CON SISTEMA DE MENÚS...")
            if not self._setup_menu_integration():
                print("❌ Error configurando menús")
                return False
            
            # 5. Mostrar estadísticas
            print("\n📊 5. ESTADÍSTICAS DEL SISTEMA...")
            self._show_system_stats()
            
            # 6. Demo de acciones
            print("\n🎯 6. DEMO DE EJECUCIÓN DE ACCIONES...")
            self._demo_addon_actions()
            
            print("\n✅ DEMO COMPLETADA EXITOSAMENTE")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR EN DEMO: {e}")
            return False
    
    def _initialize_addon_system(self) -> bool:
        """Inicializar el sistema de addons."""
        try:
            self.addon_system = AddonFactory.create_complete_addon_system(
                repository_path=self.addons_path,
                logger=self.logger
            )
            
            print(f"✅ Sistema de addons creado - Path: {self.addons_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando sistema de addons: {e}")
            return False
    
    def _validate_addons(self):
        """Validar todos los addons encontrados."""
        addons_dir = Path(self.addons_path)
        
        if not addons_dir.exists():
            print(f"⚠️  Directorio de addons no existe: {addons_dir}")
            return
        
        valid_count = 0
        invalid_count = 0
        
        for addon_dir in addons_dir.iterdir():
            if addon_dir.is_dir():
                manifest_file = addon_dir / "manifest.json"
                
                if manifest_file.exists():
                    print(f"🔍 Validando addon: {addon_dir.name}")
                    
                    is_valid, errors = validate_addon_manifest(
                        str(manifest_file),
                        str(addon_dir),
                        logger=self.logger
                    )
                    
                    if is_valid:
                        print(f"   ✅ {addon_dir.name} - Válido")
                        valid_count += 1
                    else:
                        print(f"   ❌ {addon_dir.name} - Errores encontrados:")
                        for error in errors[:3]:  # Mostrar solo primeros 3 errores
                            print(f"      • {error}")
                        if len(errors) > 3:
                            print(f"      ... y {len(errors) - 3} errores más")
                        invalid_count += 1
                else:
                    print(f"   ⚠️  {addon_dir.name} - Sin manifest.json")
        
        print(f"\n📋 Resumen de validación:")
        print(f"   ✅ Válidos: {valid_count}")
        print(f"   ❌ Inválidos: {invalid_count}")
    
    def _load_addons(self) -> int:
        """Cargar todos los addons válidos."""
        try:
            loaded_addons = self.addon_system.load_all_addons()
            active_addons = self.addon_system.get_active_addons()
            
            print(f"📦 Addons procesados: {loaded_addons}")
            print(f"✅ Addons activos: {len(active_addons)}")
            
            for addon in active_addons:
                print(f"   • {addon.get_name()} v{addon.get_version()} - {addon.get_description()}")
                
            return len(active_addons)
            
        except Exception as e:
            print(f"❌ Error cargando addons: {e}")
            return 0
    
    def _setup_menu_integration(self) -> bool:
        """Configurar integración con sistema de menús."""
        try:
            self.menu_manager = EnhancedDynamicMenuManager(
                config_file="menu_config.json",
                addon_manager=self.addon_system,
                logger=self.logger
            )
            
            # Cargar configuración (incluye addons automáticamente)
            success = self.menu_manager.load_config()
            
            if success:
                print("✅ Menús integrados exitosamente")
                
                # Mostrar categorías disponibles
                categories = self.menu_manager.get_categories()
                addon_categories = [cat for cat in categories.keys() if cat.startswith('addon_')]
                
                print(f"🎛️  Categorías de menú total: {len(categories)}")
                print(f"📦 Categorías de addons: {len(addon_categories)}")
                
                for cat_id in addon_categories:
                    category = categories[cat_id]
                    print(f"   • {category.label} ({len(category.items)} items)")
                    
            return success
            
        except Exception as e:
            print(f"❌ Error configurando menús: {e}")
            return False
    
    def _show_system_stats(self):
        """Mostrar estadísticas completas del sistema."""
        try:
            # Estadísticas del addon system
            active_addons = self.addon_system.get_active_addons()
            
            print("📊 ESTADÍSTICAS DEL SISTEMA DE ADDONS:")
            print(f"   📦 Addons activos: {len(active_addons)}")
            
            for addon in active_addons:
                status = addon.get_status()
                print(f"      • {status['name']} v{status['version']} - Estado: {status['status']}")
            
            # Estadísticas de menús si están disponibles
            if self.menu_manager and hasattr(self.menu_manager, 'get_menu_statistics'):
                menu_stats = self.menu_manager.get_menu_statistics()
                print(f"\n🎛️  ESTADÍSTICAS DE MENÚS:")
                print(f"   📋 Total categorías: {menu_stats.get('total_categories', 0)}")
                print(f"   ⚡ Total acciones: {menu_stats.get('total_actions', 0)}")
                print(f"   🔧 Categorías sistema: {menu_stats.get('system_categories', 0)}")
                print(f"   📦 Categorías addons: {menu_stats.get('addon_categories', 0)}")
                
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
    
    def _demo_addon_actions(self):
        """Demostrar ejecución de acciones de addon."""
        try:
            active_addons = self.addon_system.get_active_addons()
            
            if not active_addons:
                print("⚠️  No hay addons activos para demo")
                return
            
            print("🎯 DEMO DE EJECUCIÓN DE ACCIONES:")
            
            # Buscar addon email_reports como ejemplo
            email_addon = None
            for addon in active_addons:
                if addon.get_name() == "email_reports":
                    email_addon = addon
                    break
            
            if email_addon:
                print(f"\n📧 Demostrando addon: {email_addon.get_name()}")
                
                # Demo de configuración
                print("   🔧 Ejecutando configuración de email...")
                success = email_addon.execute_action("configure_email_settings", {})
                print(f"   {'✅' if success else '❌'} Configuración: {'Exitosa' if success else 'Falló'}")
                
                # Demo de reporte diario
                print("   📧 Ejecutando reporte diario...")
                success = email_addon.execute_action("send_daily_report", {})
                print(f"   {'✅' if success else '❌'} Reporte diario: {'Enviado' if success else 'Falló'}")
                
                # Mostrar estado del addon
                status = email_addon.get_status()
                print(f"   📊 Estado del addon: {status}")
                
            else:
                print("ℹ️  Addon email_reports no encontrado - ejecutando demo genérica")
                
                # Demo con primer addon disponible
                first_addon = active_addons[0]
                print(f"🔧 Demostrando addon: {first_addon.get_name()}")
                
                status = first_addon.get_status()
                print(f"   📊 Estado: {status}")
                
                # Intentar ejecutar primera acción disponible del manifest
                manifest = first_addon.get_manifest()
                if hasattr(manifest, 'menu_items') and manifest.menu_items:
                    first_action = manifest.menu_items[0].get('action')
                    if first_action:
                        print(f"   🚀 Ejecutando acción: {first_action}")
                        success = first_addon.execute_action(first_action, {})
                        print(f"   {'✅' if success else '❌'} Resultado: {'Exitoso' if success else 'Falló'}")
                
        except Exception as e:
            print(f"❌ Error en demo de acciones: {e}")
    
    def interactive_demo(self):
        """Demo interactiva que permite al usuario explorar."""
        print("\n🎮 MODO INTERACTIVO - EXPLORADOR DE ADDONS")
        print("="*50)
        
        if not self.addon_system:
            print("❌ Sistema no inicializado. Ejecuta run_complete_demo() primero.")
            return
        
        active_addons = self.addon_system.get_active_addons()
        
        if not active_addons:
            print("⚠️  No hay addons activos para explorar")
            return
        
        while True:
            print(f"\n📦 ADDONS DISPONIBLES ({len(active_addons)}):")
            for i, addon in enumerate(active_addons, 1):
                print(f"   {i}. {addon.get_name()} v{addon.get_version()}")
                print(f"      {addon.get_description()}")
            
            print("\n🎛️  OPCIONES:")
            print("   0. Salir")
            print("   1-N. Explorar addon")
            print("   s. Mostrar estadísticas")
            print("   v. Validar addons")
            
            try:
                choice = input("\n➤ Selección: ").strip().lower()
                
                if choice == '0' or choice == 'salir' or choice == 'exit':
                    print("👋 ¡Hasta luego!")
                    break
                elif choice == 's':
                    self._show_system_stats()
                elif choice == 'v':
                    self._validate_addons()
                else:
                    try:
                        addon_index = int(choice) - 1
                        if 0 <= addon_index < len(active_addons):
                            self._explore_addon(active_addons[addon_index])
                        else:
                            print("❌ Selección inválida")
                    except ValueError:
                        print("❌ Entrada inválida")
                        
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
    
    def _explore_addon(self, addon):
        """Explorar un addon específico interactivamente."""
        print(f"\n🔍 EXPLORANDO ADDON: {addon.get_name()}")
        print("-" * 40)
        
        # Información básica
        print(f"📋 Información básica:")
        print(f"   • Nombre: {addon.get_name()}")
        print(f"   • Versión: {addon.get_version()}")
        print(f"   • Descripción: {addon.get_description()}")
        
        # Estado
        status = addon.get_status()
        print(f"\n📊 Estado actual:")
        for key, value in status.items():
            print(f"   • {key}: {value}")
        
        # Manifest info
        manifest = addon.get_manifest()
        if hasattr(manifest, 'menu_items') and manifest.menu_items:
            print(f"\n🎛️  Acciones disponibles ({len(manifest.menu_items)}):")
            for i, item in enumerate(manifest.menu_items, 1):
                print(f"   {i}. {item.get('label', 'Sin etiqueta')} ({item.get('action', 'sin_accion')})")
            
            # Permitir ejecutar acción
            try:
                action_choice = input("\n➤ Ejecutar acción (número o Enter para continuar): ").strip()
                if action_choice and action_choice.isdigit():
                    action_index = int(action_choice) - 1
                    if 0 <= action_index < len(manifest.menu_items):
                        action_name = manifest.menu_items[action_index].get('action')
                        print(f"🚀 Ejecutando: {action_name}")
                        success = addon.execute_action(action_name, {})
                        print(f"{'✅' if success else '❌'} Resultado: {'Exitoso' if success else 'Falló'}")
                        
            except (ValueError, KeyboardInterrupt):
                pass
        
        input("\n⏎ Presiona Enter para continuar...")


def main():
    """Función principal para ejecutar la demo."""
    print("🚀 DATACONTA ADDON SYSTEM - DEMO COMPLETA")
    print("=========================================")
    
    demo = AddonSystemDemo()
    
    # Ejecutar demo completa
    success = demo.run_complete_demo()
    
    if success:
        # Preguntar si quiere modo interactivo
        try:
            interactive = input("\n🎮 ¿Ejecutar modo interactivo? (s/n): ").strip().lower()
            if interactive in ['s', 'si', 'y', 'yes']:
                demo.interactive_demo()
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
    
    print("\n🎉 DEMO FINALIZADA")


if __name__ == "__main__":
    main()