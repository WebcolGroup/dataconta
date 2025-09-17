"""
Dynamic Menu Configuration System for DATACONTA GUI
Permite cargar y gestionar menús desde configuración JSON
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from PySide6.QtWidgets import QMenu, QPushButton, QMessageBox, QApplication
from PySide6.QtCore import QObject, Signal


class MenuAction:
    """Representa una acción de menú con sus propiedades."""
    
    def __init__(self, action_id: str, config: Dict[str, Any]):
        self.id = action_id
        self.type = config.get('type', 'dialog')
        self.title = config.get('title', '')
        self.content = config.get('content', '')
        self.description = config.get('description', '')


class MenuItem:
    """Representa un elemento de menú con sus propiedades."""
    
    def __init__(self, item_config: Dict[str, Any]):
        self.id = item_config.get('id', '')
        self.label = item_config.get('label', '')
        self.icon = item_config.get('icon', '')
        self.action = item_config.get('action', '')
        self.enabled = item_config.get('enabled', True)
        self.confirmation = item_config.get('confirmation', None)


class MenuCategory:
    """Representa una categoría de menú principal."""
    
    def __init__(self, category_id: str, config: Dict[str, Any]):
        self.id = category_id
        self.label = config.get('label', '')
        self.icon = config.get('icon', '')
        self.enabled = config.get('enabled', True)
        self.items = []
        
        # Procesar submenús
        submenu_config = config.get('submenu', [])
        for item_config in submenu_config:
            self.items.append(MenuItem(item_config))


class DynamicMenuManager(QObject):
    """
    Gestor de menús dinámicos basado en configuración JSON.
    Permite cargar, crear y gestionar menús de forma flexible.
    """
    
    # Señales para comunicación con la interfaz
    menu_action_triggered = Signal(str, dict)
    
    def __init__(self, config_file: str = "menu_config.json"):
        super().__init__()
        self.config_file = config_file
        self.config = {}
        self.actions = {}
        self.categories = {}
        self.parent_window = None
        
    def set_parent_window(self, window):
        """Establecer ventana padre para diálogos."""
        self.parent_window = window
        
    def load_config(self) -> bool:
        """
        Cargar configuración de menús desde archivo JSON.
        
        Returns:
            bool: True si la carga fue exitosa, False en caso contrario
        """
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                self._create_default_config()
                
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
                
            self._process_config()
            return True
            
        except Exception as e:
            print(f"Error cargando configuración de menú: {e}")
            return False
    
    def _create_default_config(self):
        """Crear configuración por defecto si no existe."""
        default_config = {
            "horizontal_menu": {
                "inicio": {
                    "label": "Inicio",
                    "icon": "🏠",
                    "enabled": True,
                    "submenu": [
                        {
                            "id": "salir",
                            "label": "Salir",
                            "icon": "🚪",
                            "action": "exit_application",
                            "confirmation": "¿Está seguro que desea salir?",
                            "enabled": True
                        }
                    ]
                }
            },
            "menu_actions": {
                "exit_application": {
                    "type": "system",
                    "description": "Cerrar aplicación"
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(default_config, file, indent=2, ensure_ascii=False)
    
    def _process_config(self):
        """Procesar configuración cargada."""
        # Procesar acciones
        actions_config = self.config.get('menu_actions', {})
        for action_id, action_config in actions_config.items():
            self.actions[action_id] = MenuAction(action_id, action_config)
        
        # Procesar categorías de menú
        menu_config = self.config.get('horizontal_menu', {})
        for category_id, category_config in menu_config.items():
            self.categories[category_id] = MenuCategory(category_id, category_config)
    
    def create_menu_buttons(self) -> List[QPushButton]:
        """
        Crear botones de menú basados en la configuración.
        
        Returns:
            List[QPushButton]: Lista de botones creados
        """
        buttons = []
        
        for category in self.categories.values():
            if not category.enabled:
                continue
                
            button = QPushButton(f"{category.icon} {category.label}")
            button.setStyleSheet(self._get_button_style())
            
            # Crear una función de callback que pase tanto la categoría como el botón
            def create_callback(cat, btn):
                return lambda: self._show_category_menu(cat, btn)
            
            callback = create_callback(category, button)
            button.clicked.connect(callback)
            
            # Almacenar referencia a la categoría en el botón para debug
            button.category = category
            buttons.append(button)
            
        return buttons
    
    def _get_button_style(self) -> str:
        """Obtener estilo CSS para botones de menú."""
        return """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 5px 10px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
        """
    
    def _show_category_menu(self, category: MenuCategory, button: QPushButton):
        """Mostrar menú contextual para una categoría."""
        if not button:
            return
            
        menu = QMenu(self.parent_window)
        menu.setStyleSheet(self._get_menu_style())
        
        # Agregar items del submenú
        items_added = 0
        for item in category.items:
            if not item.enabled:
                continue
                
            action = menu.addAction(f"{item.icon} {item.label}")
            
            # Crear callback específico para cada item
            def create_action_callback(it):
                return lambda: self._execute_action(it)
            
            action.triggered.connect(create_action_callback(item))
            items_added += 1
        
        # Si no hay items habilitados, no mostrar menú
        if items_added == 0:
            return
            
        # Mostrar menú en la posición correcta
        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.exec(pos)
    
    def _get_menu_style(self) -> str:
        """Obtener estilo CSS para menús contextuales."""
        return """
            QMenu {
                background-color: #27ae60;
                color: white;
                border: 1px solid #2c3e50;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 8px 15px;
                border: none;
            }
            QMenu::item:selected {
                background-color: #2c3e50;
                border-radius: 3px;
            }
        """
    
    def _execute_action(self, item: MenuItem):
        """Ejecutar acción de menú."""
        if item.action not in self.actions:
            print(f"Acción no encontrada: {item.action}")
            return
        
        action = self.actions[item.action]
        
        # Mostrar confirmación si es necesaria
        if item.confirmation:
            reply = QMessageBox.question(
                self.parent_window,
                "Confirmación",
                item.confirmation,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Ejecutar acción según su tipo
        if action.type == 'system':
            self._execute_system_action(action, item)
        elif action.type == 'dialog':
            self._execute_dialog_action(action, item)
        else:
            # Emitir señal para acciones personalizadas
            self.menu_action_triggered.emit(item.action, {
                'item': item,
                'action': action
            })
    
    def _execute_system_action(self, action: MenuAction, item: MenuItem):
        """Ejecutar acciones del sistema."""
        if action.id == 'exit_application':
            QApplication.quit()
    
    def _execute_dialog_action(self, action: MenuAction, item: MenuItem):
        """Ejecutar acciones de diálogo."""
        if self.parent_window:
            QMessageBox.information(
                self.parent_window,
                action.title,
                action.content
            )
    
    def add_menu_category(self, category_id: str, config: Dict[str, Any]) -> bool:
        """
        Agregar nueva categoría de menú dinámicamente.
        
        Args:
            category_id: ID único de la categoría
            config: Configuración de la categoría
            
        Returns:
            bool: True si se agregó exitosamente
        """
        try:
            self.categories[category_id] = MenuCategory(category_id, config)
            self._save_config()
            return True
        except Exception as e:
            print(f"Error agregando categoría {category_id}: {e}")
            return False
    
    def remove_menu_category(self, category_id: str) -> bool:
        """
        Remover categoría de menú.
        
        Args:
            category_id: ID de la categoría a remover
            
        Returns:
            bool: True si se removió exitosamente
        """
        try:
            if category_id in self.categories:
                del self.categories[category_id]
                self._save_config()
                return True
            return False
        except Exception as e:
            print(f"Error removiendo categoría {category_id}: {e}")
            return False
    
    def _save_config(self):
        """Guardar configuración actual al archivo JSON."""
        try:
            # Reconstruir estructura de configuración
            config_to_save = {
                'horizontal_menu': {},
                'menu_actions': {}
            }
            
            # Guardar categorías
            for cat_id, category in self.categories.items():
                config_to_save['horizontal_menu'][cat_id] = {
                    'label': category.label,
                    'icon': category.icon,
                    'enabled': category.enabled,
                    'submenu': []
                }
                
                for item in category.items:
                    item_config = {
                        'id': item.id,
                        'label': item.label,
                        'icon': item.icon,
                        'action': item.action,
                        'enabled': item.enabled
                    }
                    if item.confirmation:
                        item_config['confirmation'] = item.confirmation
                    
                    config_to_save['horizontal_menu'][cat_id]['submenu'].append(item_config)
            
            # Guardar acciones
            for action_id, action in self.actions.items():
                config_to_save['menu_actions'][action_id] = {
                    'type': action.type,
                    'description': action.description
                }
                if action.title:
                    config_to_save['menu_actions'][action_id]['title'] = action.title
                if action.content:
                    config_to_save['menu_actions'][action_id]['content'] = action.content
            
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(config_to_save, file, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def reload_config(self) -> bool:
        """Recargar configuración desde archivo."""
        return self.load_config()
    
    def get_categories(self) -> Dict[str, MenuCategory]:
        """Obtener todas las categorías de menú."""
        return self.categories.copy()
    
    def get_actions(self) -> Dict[str, MenuAction]:
        """Obtener todas las acciones disponibles."""
        return self.actions.copy()