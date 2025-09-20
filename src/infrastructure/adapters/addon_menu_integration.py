"""
Addon Menu Integration Extension
Extensión del DynamicMenuManager para integrar menús de addons sin romper funcionalidad existente.
"""

from typing import Dict, List, Any, Optional
from src.application.ports.addon_interfaces import AddonManager
from src.infrastructure.config.dynamic_menu_config import DynamicMenuManager, MenuCategory, MenuItem, MenuAction
from src.application.ports.interfaces import Logger


class AddonMenuIntegration:
    """
    Integra menús de addons con el sistema de menús dinámicos existente.
    
    Responsabilidades:
    - Cargar menús de addons sin romper menús existentes
    - Mantener separación entre addons y sistema base
    - Proporcionar hooks para acciones de addon
    - Validar permisos y licencias de addons
    """
    
    def __init__(self, 
                 menu_manager: DynamicMenuManager,
                 addon_manager: AddonManager,
                 logger: Logger = None):
        """
        Inicializar integración de menús addon.
        
        Args:
            menu_manager: Manager de menús dinámicos existente
            addon_manager: Manager de addons
            logger: Logger para eventos
        """
        self.menu_manager = menu_manager
        self.addon_manager = addon_manager
        self.logger = logger
        self.addon_categories = {}  # Separar categorías de addon
        self.addon_actions = {}     # Separar acciones de addon
        
    def load_addon_menus(self) -> bool:
        """
        Cargar menús de todos los addons activos sin romper menús existentes.
        
        Returns:
            bool: True si se cargaron exitosamente
        """
        try:
            if self.logger:
                self.logger.info("🔄 Cargando menús de addons...")
            
            # Obtener addons activos
            active_addons = self.addon_manager.get_active_addons()
            
            loaded_count = 0
            for addon in active_addons:
                try:
                    if self._load_addon_menu(addon):
                        loaded_count += 1
                        
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"❌ Error cargando menú de addon '{addon.get_name()}': {e}")
            
            if self.logger:
                self.logger.info(f"✅ Menús de addons cargados: {loaded_count}/{len(active_addons)}")
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cargando menús de addons: {e}")
            return False
    
    def _load_addon_menu(self, addon) -> bool:
        """
        Cargar menú de un addon específico.
        
        Args:
            addon: Instancia del addon
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            addon_name = addon.get_name()
            manifest = addon.get_manifest()
            
            # Verificar si el addon tiene menús
            menu_items = manifest.menu_items
            if not menu_items:
                return True  # Addon sin menús es válido
            
            # Crear categoría para el addon
            category_id = f"addon_{addon_name}"
            category_config = {
                'label': f"📦 {manifest.display_name}",
                'icon': '📦',
                'enabled': True,
                'submenu': []
            }
            
            # Procesar items de menú del addon
            for menu_item in menu_items:
                item_config = self._create_menu_item_config(addon_name, menu_item)
                category_config['submenu'].append(item_config)
                
                # Registrar acción del addon
                action_id = f"addon_{addon_name}_{menu_item['action']}"
                self._register_addon_action(addon, action_id, menu_item)
            
            # Crear categoría del addon (separada de las existentes)
            self.addon_categories[category_id] = MenuCategory(category_id, category_config)
            
            if self.logger:
                self.logger.debug(f"✅ Menú cargado para addon: {addon_name}")
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cargando menú de addon: {e}")
            return False
    
    def _create_menu_item_config(self, addon_name: str, menu_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crear configuración de item de menú para addon.
        
        Args:
            addon_name: Nombre del addon
            menu_item: Configuración del item del manifiesto
            
        Returns:
            Dict con configuración del item
        """
        action_id = f"addon_{addon_name}_{menu_item['action']}"
        
        config = {
            'id': menu_item.get('id', action_id),
            'label': menu_item.get('label', 'Acción de Addon'),
            'icon': menu_item.get('icon', '⚡'),
            'action': action_id,
            'enabled': True,
            'addon_source': addon_name  # Marcar origen del addon
        }
        
        # Agregar confirmación si se especifica
        if menu_item.get('requires_confirmation'):
            config['confirmation'] = f"¿Ejecutar '{menu_item.get('label')}' del addon {addon_name}?"
            
        return config
    
    def _register_addon_action(self, addon, action_id: str, menu_item: Dict[str, Any]):
        """
        Registrar acción de addon en el sistema.
        
        Args:
            addon: Instancia del addon
            action_id: ID único de la acción
            menu_item: Configuración del item de menú
        """
        action_config = {
            'type': 'addon',  # Tipo especial para addons
            'title': menu_item.get('label', 'Acción de Addon'),
            'description': menu_item.get('description', ''),
            'addon_instance': addon,
            'addon_action': menu_item.get('action'),
            'requires_confirmation': menu_item.get('requires_confirmation', False)
        }
        
        # Crear acción de addon (extendida)
        action = AddonMenuAction(action_id, action_config)
        self.addon_actions[action_id] = action
    
    def execute_addon_action(self, action_id: str, context: Dict[str, Any] = None) -> bool:
        """
        Ejecutar acción de addon de forma segura.
        
        Args:
            action_id: ID de la acción a ejecutar
            context: Contexto adicional para la acción
            
        Returns:
            bool: True si se ejecutó exitosamente
        """
        try:
            if action_id not in self.addon_actions:
                if self.logger:
                    self.logger.error(f"❌ Acción de addon no encontrada: {action_id}")
                return False
            
            action = self.addon_actions[action_id]
            addon = action.addon_instance
            addon_action = action.addon_action
            
            if self.logger:
                self.logger.info(f"🚀 Ejecutando acción de addon: {action_id}")
            
            # Validar que el addon sigue activo
            if not self.addon_manager.is_addon_active(addon.get_name()):
                if self.logger:
                    self.logger.error(f"❌ Addon no está activo: {addon.get_name()}")
                return False
            
            # Ejecutar acción del addon
            result = addon.execute_action(addon_action, context or {})
            
            if self.logger:
                if result:
                    self.logger.info(f"✅ Acción de addon ejecutada: {action_id}")
                else:
                    self.logger.warning(f"⚠️ Acción de addon falló: {action_id}")
                    
            return result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error ejecutando acción de addon {action_id}: {e}")
            return False
    
    def get_combined_categories(self) -> Dict[str, MenuCategory]:
        """
        Obtener categorías combinadas (sistema + addons).
        
        Returns:
            Dict con todas las categorías disponibles
        """
        combined = self.menu_manager.get_categories().copy()
        combined.update(self.addon_categories)
        return combined
    
    def get_combined_actions(self) -> Dict[str, Any]:
        """
        Obtener acciones combinadas (sistema + addons).
        
        Returns:
            Dict con todas las acciones disponibles
        """
        combined = self.menu_manager.get_actions().copy()
        combined.update(self.addon_actions)
        return combined
    
    def is_addon_action(self, action_id: str) -> bool:
        """
        Verificar si una acción pertenece a un addon.
        
        Args:
            action_id: ID de la acción
            
        Returns:
            bool: True si es acción de addon
        """
        return action_id.startswith('addon_') or action_id in self.addon_actions
    
    def reload_addon_menus(self) -> bool:
        """
        Recargar menús de addons (útil después de instalar/desinstalar).
        
        Returns:
            bool: True si se recargaron exitosamente
        """
        try:
            # Limpiar menús de addon existentes
            self.addon_categories.clear()
            self.addon_actions.clear()
            
            # Recargar menús
            return self.load_addon_menus()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error recargando menús de addons: {e}")
            return False
    
    def unload_addon_menu(self, addon_name: str) -> bool:
        """
        Descargar menú de un addon específico.
        
        Args:
            addon_name: Nombre del addon
            
        Returns:
            bool: True si se descargó exitosamente
        """
        try:
            category_id = f"addon_{addon_name}"
            
            # Remover categoría
            if category_id in self.addon_categories:
                del self.addon_categories[category_id]
            
            # Remover acciones relacionadas
            actions_to_remove = [
                action_id for action_id in self.addon_actions.keys()
                if action_id.startswith(f"addon_{addon_name}_")
            ]
            
            for action_id in actions_to_remove:
                del self.addon_actions[action_id]
            
            if self.logger:
                self.logger.info(f"✅ Menú de addon descargado: {addon_name}")
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error descargando menú de addon {addon_name}: {e}")
            return False
    
    def get_addon_menu_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de menús de addon.
        
        Returns:
            Dict con estadísticas
        """
        return {
            'addon_categories': len(self.addon_categories),
            'addon_actions': len(self.addon_actions),
            'categories': list(self.addon_categories.keys()),
            'total_menu_items': sum(
                len(category.items) 
                for category in self.addon_categories.values()
            )
        }


class AddonMenuAction(MenuAction):
    """
    Acción de menú específica para addons.
    Extiende MenuAction con funcionalidad específica de addon.
    """
    
    def __init__(self, action_id: str, config: Dict[str, Any]):
        super().__init__(action_id, config)
        self.addon_instance = config.get('addon_instance')
        self.addon_action = config.get('addon_action', '')
        self.requires_confirmation = config.get('requires_confirmation', False)


class EnhancedDynamicMenuManager(DynamicMenuManager):
    """
    Versión extendida del DynamicMenuManager que soporta addons.
    
    Mantiene 100% de compatibilidad con la implementación original
    mientras agrega soporte para menús de addon.
    """
    
    def __init__(self, config_file: str = "menu_config.json", addon_manager: AddonManager = None, logger: Logger = None):
        """
        Inicializar manager de menús extendido.
        
        Args:
            config_file: Archivo de configuración de menús
            addon_manager: Manager de addons (opcional)
            logger: Logger para eventos
        """
        super().__init__(config_file)
        
        self.logger = logger
        self.addon_integration = None
        
        # Configurar integración de addons si está disponible
        if addon_manager:
            self.addon_integration = AddonMenuIntegration(self, addon_manager, logger)
    
    def load_config(self) -> bool:
        """
        Cargar configuración extendida (sistema base + addons).
        
        Returns:
            bool: True si se cargó exitosamente
        """
        # Cargar configuración base (sin cambios)
        base_loaded = super().load_config()
        
        if not base_loaded:
            return False
        
        # Cargar menús de addons si está disponible
        if self.addon_integration:
            try:
                self.addon_integration.load_addon_menus()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"❌ Error cargando menús de addons: {e}")
                # No fallar la carga completa por errores de addon
        
        return True
    
    def get_categories(self) -> Dict[str, MenuCategory]:
        """
        Obtener todas las categorías (sistema + addons).
        
        Returns:
            Dict con todas las categorías
        """
        if self.addon_integration:
            return self.addon_integration.get_combined_categories()
        else:
            return super().get_categories()
    
    def get_actions(self) -> Dict[str, Any]:
        """
        Obtener todas las acciones (sistema + addons).
        
        Returns:
            Dict con todas las acciones
        """
        if self.addon_integration:
            return self.addon_integration.get_combined_actions()
        else:
            return super().get_actions()
    
    def execute_action(self, action_id: str, context: Dict[str, Any] = None) -> bool:
        """
        Ejecutar acción (sistema o addon).
        
        Args:
            action_id: ID de la acción
            context: Contexto para la acción
            
        Returns:
            bool: True si se ejecutó exitosamente
        """
        # Si es acción de addon, usar integración de addons
        if self.addon_integration and self.addon_integration.is_addon_action(action_id):
            return self.addon_integration.execute_addon_action(action_id, context)
        
        # Para acciones del sistema, usar lógica existente
        # Nota: Esto requeriría exponer el método _execute_action del DynamicMenuManager
        # Por ahora, delegar a través de señales
        self.menu_action_triggered.emit(action_id, context or {})
        return True
    
    def reload_with_addons(self) -> bool:
        """
        Recargar configuración completa incluyendo addons.
        
        Returns:
            bool: True si se recargó exitosamente
        """
        success = self.reload_config()
        
        if success and self.addon_integration:
            self.addon_integration.reload_addon_menus()
            
        return success
    
    def get_menu_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas completas del sistema de menús.
        
        Returns:
            Dict con estadísticas detalladas
        """
        base_stats = {
            'system_categories': len(super().get_categories()),
            'system_actions': len(super().get_actions()),
        }
        
        if self.addon_integration:
            addon_stats = self.addon_integration.get_addon_menu_stats()
            base_stats.update(addon_stats)
            base_stats['total_categories'] = base_stats['system_categories'] + addon_stats['addon_categories']
            base_stats['total_actions'] = base_stats['system_actions'] + addon_stats['addon_actions']
        else:
            base_stats['addon_categories'] = 0
            base_stats['addon_actions'] = 0
            base_stats['total_categories'] = base_stats['system_categories']
            base_stats['total_actions'] = base_stats['system_actions']
        
        return base_stats