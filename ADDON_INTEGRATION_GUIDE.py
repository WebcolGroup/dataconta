"""
Ejemplo de integración del Sistema de Addons con dataconta.py
Modificación mínima y no-invasiva que mantiene toda la funcionalidad existente.
"""

# ==================== PASO 1: AGREGAR IMPORTS AL INICIO ====================
# Agregar estos imports después de las líneas existentes ~29-42

# Imports del sistema de addons (agregar después de LoggerAdapter)
from src.infrastructure.factories.addon_factory import AddonFactory
from src.infrastructure.adapters.addon_menu_integration import EnhancedDynamicMenuManager

# ==================== PASO 2: MODIFICAR create_dataconta_app() ====================
# Reemplazar la función existente (líneas ~475-520) con esta versión extendida:

def create_dataconta_app() -> DataContaMainWindow:
    """
    Factory function para crear la aplicación con arquitectura hexagonal NO monolítica.
    
    NUEVO: Ahora incluye sistema de addons integrado de forma transparente.
    
    Implementa inyección de dependencias completa siguiendo principios SOLID.
    
    Returns:
        DataContaMainWindow: Instancia NO monolítica de la aplicación con addons
    """
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear adaptador de logger (Infrastructure Layer)
    logger = LoggerAdapter(name="dataconta_non_monolithic")
    logger.info("🏗️ Iniciando DataConta")
    
    # ==================== NUEVO: SISTEMA DE ADDONS ====================
    # Inicializar sistema de addons (completamente opcional y no-invasivo)
    addon_system = None
    enhanced_menu_manager = None
    
    try:
        logger.info("🔌 Inicializando sistema de addons...")
        
        # Crear sistema de addons usando factory pattern
        addon_system = AddonFactory.create_complete_addon_system(
            repository_path="addons/",
            logger=logger
        )
        
        # Cargar addons disponibles
        loaded_addons = addon_system.load_all_addons()
        active_addons = addon_system.get_active_addons()
        
        if active_addons:
            logger.info(f"✅ Sistema de addons inicializado: {len(active_addons)} addons activos")
            for addon in active_addons:
                logger.info(f"  📦 {addon.get_name()} v{addon.get_version()}")
        else:
            logger.info("ℹ️  Sistema de addons listo (no hay addons instalados)")
            
    except Exception as e:
        logger.warning(f"⚠️  Sistema de addons no disponible: {e}")
        # Continúa normalmente sin addons - NO es un error crítico
        addon_system = None
    
    # ==================== LÓGICA EXISTENTE (SIN CAMBIOS) ====================
    # Crear adaptadores de infraestructura
    siigo_adapter = FreeGUISiigoAdapter(logger=logger)
    file_storage = FileStorageAdapter(output_directory="./outputs", logger=logger)
    
    # Crear servicios de aplicación
    kpi_service = KPIService(
        invoice_repository=siigo_adapter,
        file_storage=file_storage,
        logger=logger
    )
    
    export_service = ExportService(
        invoice_repository=siigo_adapter,
        file_storage=file_storage,
        logger=logger
    )
    
    # Crear controlador (Application Layer)
    controller = FreeGUIController(
        kpi_service=kpi_service,
        export_service=export_service,
        invoice_repository=siigo_adapter,
        logger=logger,
        file_storage=file_storage
    )
    
    # ==================== NUEVO: CONTROLADOR MEJORADO CON ADDONS ====================
    # Agregar referencia del sistema de addons al controlador (opcional)
    if addon_system and hasattr(controller, 'set_addon_system'):
        controller.set_addon_system(addon_system)
        logger.info("🔗 Sistema de addons vinculado al controlador")
    
    # Crear GUI NO monolítica (Presentation Layer)
    main_window = DataContaMainWindow(controller)
    
    # ==================== NUEVO: INTEGRAR ADDONS CON UI ====================
    # Vincular sistema de addons con la interfaz (si está disponible)
    if addon_system and hasattr(main_window, 'set_addon_system'):
        main_window.set_addon_system(addon_system)
        logger.info("🎛️  Sistema de addons integrado con interfaz")
    
    logger.info("✅ DataConta NO Monolítico creado exitosamente")
    
    # ==================== NUEVO: LOG DE ESTADÍSTICAS ====================
    if addon_system:
        stats = {
            'total_addons': len(addon_system.get_active_addons()),
            'addon_names': [addon.get_name() for addon in addon_system.get_active_addons()]
        }
        logger.info(f"📊 Estadísticas de addons: {stats}")
    
    return main_window

# ==================== PASO 3: EXTENDER DataContaMainWindow (OPCIONAL) ====================
# Agregar estos métodos a la clase DataContaMainWindow (después de __init__):

class DataContaMainWindowExtended(DataContaMainWindow):
    """
    Extensión opcional de DataContaMainWindow con soporte para addons.
    
    Mantiene 100% de compatibilidad con la implementación original.
    """
    
    def __init__(self, controller: FreeGUIController):
        # Inicialización normal
        super().__init__(controller)
        
        # Sistema de addons (opcional)
        self.addon_system = None
        self.enhanced_menu_manager = None
    
    def set_addon_system(self, addon_system):
        """
        Configurar sistema de addons para la ventana principal.
        
        Args:
            addon_system: Sistema de addons inicializado
        """
        try:
            self.addon_system = addon_system
            
            # Si hay tabs_widget, integrar menús de addon
            if self.tabs_widget and hasattr(self.tabs_widget, 'add_addon_integration'):
                self.tabs_widget.add_addon_integration(addon_system)
                self.controller._logger.info("🎛️  Menús de addons integrados con TabsWidget")
            
            # Conectar señales de addons si es necesario
            self._connect_addon_signals()
            
        except Exception as e:
            self.controller._logger.warning(f"⚠️  Error integrando sistema de addons: {e}")
    
    def _connect_addon_signals(self):
        """Conectar señales específicas de addons."""
        if not self.addon_system:
            return
            
        try:
            # Ejemplo: conectar ejecución de addons con logging
            active_addons = self.addon_system.get_active_addons()
            
            for addon in active_addons:
                # Log cuando se ejecute una acción de addon
                addon_name = addon.get_name()
                self.controller._logger.info(f"🔌 Addon {addon_name} listo para uso")
                
        except Exception as e:
            self.controller._logger.warning(f"⚠️  Error conectando señales de addon: {e}")
    
    def execute_addon_action(self, addon_name: str, action_name: str, parameters: dict = None):
        """
        Ejecutar acción de addon desde la interfaz.
        
        Args:
            addon_name: Nombre del addon
            action_name: Acción a ejecutar
            parameters: Parámetros para la acción
        """
        if not self.addon_system:
            self.controller._logger.warning("⚠️  Sistema de addons no disponible")
            return False
        
        try:
            addon = self.addon_system.get_addon(addon_name)
            if not addon:
                self.controller._logger.error(f"❌ Addon no encontrado: {addon_name}")
                return False
            
            # Ejecutar acción
            success = addon.execute_action(action_name, parameters or {})
            
            if success:
                self.controller._logger.info(f"✅ Acción de addon ejecutada: {addon_name}.{action_name}")
            else:
                self.controller._logger.warning(f"⚠️  Acción de addon falló: {addon_name}.{action_name}")
                
            return success
            
        except Exception as e:
            self.controller._logger.error(f"❌ Error ejecutando addon {addon_name}.{action_name}: {e}")
            return False

# ==================== PASO 4: ACTUALIZAR MAIN FUNCTION (OPCIONAL) ====================
# Modificar main() para usar la versión extendida y mostrar info de addons:

def main():
    """Función principal de la aplicación NO monolítica con soporte de addons."""
    app = QApplication(sys.argv)
    
    try:
        # Aplicar tema Material si está disponible
        if apply_stylesheet is not None:
            try:
                apply_stylesheet(app, theme="light_blue_500.xml")
            except Exception:
                pass
                
        print("🚀 Iniciando DataConta FREE - Versión NO Monolítica con Addons")
        print("=" * 70)
        print("📊 Componentes especializados:")
        print("  • DashboardWidget: UI de KPIs")
        print("  • ExportWidget: UI de exportaciones")  
        print("  • QueryWidget: UI de consultas")
        print("  • MainWindow: Solo coordinación")
        print("  🔌 • Sistema de Addons: Extensibilidad de comunidad")
        print("=" * 70)
        
        # Crear aplicación NO monolítica con addons
        main_window = create_dataconta_app()
        main_window.show()
        
        # Información adicional de addons si están disponibles
        if hasattr(main_window, 'addon_system') and main_window.addon_system:
            active_addons = main_window.addon_system.get_active_addons()
            if active_addons:
                print(f"🔌 Addons cargados ({len(active_addons)}):")
                for addon in active_addons:
                    print(f"  📦 {addon.get_name()} v{addon.get_version()} - {addon.get_description()}")
            else:
                print("ℹ️  Sistema de addons listo (no hay addons instalados)")
        
        print("✅ Aplicación NO Monolítica iniciada correctamente")
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return 1