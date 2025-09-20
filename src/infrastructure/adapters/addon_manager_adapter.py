"""
Addon Manager Implementation
Implementación concreta del gestor de addons siguiendo arquitectura hexagonal.
"""

import os
import sys
import json
import importlib
import importlib.util
from typing import Dict, List, Any, Optional
from pathlib import Path
from packaging import version

from src.application.ports.addon_interfaces import (
    AddonManager, AddonRepository, AddonLoader, AddonRegistry,
    AddonBase, AddonManifest, AddonContext, AddonStatus, AddonType
)
from src.application.ports.interfaces import Logger


class FileSystemAddonRepository(AddonRepository):
    """Implementación de repositorio de addons basado en sistema de archivos."""
    
    def __init__(self, addons_path: str = "addons", logger: Logger = None):
        """
        Inicializar repositorio.
        
        Args:
            addons_path: Path base donde buscar addons
            logger: Logger para logging
        """
        self.addons_path = Path(addons_path)
        self.logger = logger
        self.config_path = self.addons_path / "config"
        
        # Crear directorios si no existen
        self.addons_path.mkdir(exist_ok=True)
        self.config_path.mkdir(exist_ok=True)
    
    def find_all_addons(self) -> List[str]:
        """Encontrar todos los addons disponibles."""
        addon_dirs = []
        
        try:
            # Buscar en subdirectorios
            for item in self.addons_path.iterdir():
                if item.is_dir() and item.name not in ['config', '__pycache__', '.git']:
                    manifest_file = item / "manifest.json"
                    if manifest_file.exists():
                        addon_dirs.append(str(item))
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error buscando addons: {e}")
                
        return addon_dirs
    
    def load_addon_manifest(self, addon_path: str) -> Optional[AddonManifest]:
        """Cargar manifiesto de un addon."""
        try:
            manifest_file = Path(addon_path) / "manifest.json"
            
            if not manifest_file.exists():
                return None
                
            with open(manifest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir tipo de addon
            addon_type_str = data.get('addon_type', 'utility')
            try:
                addon_type = AddonType(addon_type_str)
            except ValueError:
                addon_type = AddonType.UTILITY
            
            manifest = AddonManifest(
                name=data.get('name', ''),
                version=data.get('version', '0.0.0'),
                description=data.get('description', ''),
                author=data.get('author', ''),
                addon_type=addon_type,
                entry_point=data.get('entry_point', ''),
                min_dataconta_version=data.get('min_dataconta_version', '3.0.0'),
                max_dataconta_version=data.get('max_dataconta_version'),
                dependencies=data.get('dependencies', []),
                requires_license=data.get('requires_license', 'FREE'),
                permissions=data.get('permissions', []),
                menu_items=data.get('menu_items', []),
                ui_components=data.get('ui_components', []),
                license=data.get('license', 'MIT'),
                keywords=data.get('keywords', []),
                homepage=data.get('homepage'),
                repository=data.get('repository')
            )
            
            return manifest
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error cargando manifiesto de {addon_path}: {e}")
            return None
    
    def validate_addon(self, addon_path: str) -> bool:
        """Validar estructura y contenido de un addon."""
        try:
            addon_dir = Path(addon_path)
            
            # Verificar estructura básica
            if not addon_dir.is_dir():
                return False
                
            # Verificar manifest.json
            manifest_file = addon_dir / "manifest.json"
            if not manifest_file.exists():
                return False
                
            # Cargar y validar manifiesto
            manifest = self.load_addon_manifest(addon_path)
            if not manifest:
                return False
                
            # Verificar que existe el archivo principal
            entry_point_parts = manifest.entry_point.split('.')
            if len(entry_point_parts) < 2:
                return False
                
            module_name = entry_point_parts[0]
            python_file = addon_dir / f"{module_name}.py"
            if not python_file.exists():
                return False
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validando addon {addon_path}: {e}")
            return False
    
    def get_addon_config(self, addon_name: str) -> Dict[str, Any]:
        """Obtener configuración de un addon."""
        try:
            config_file = self.config_path / f"{addon_name}.json"
            
            if not config_file.exists():
                return {}
                
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error cargando configuración de {addon_name}: {e}")
            return {}
    
    def save_addon_config(self, addon_name: str, config: Dict[str, Any]) -> bool:
        """Guardar configuración de un addon."""
        try:
            config_file = self.config_path / f"{addon_name}.json"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error guardando configuración de {addon_name}: {e}")
            return False


class DynamicAddonLoader(AddonLoader):
    """Implementación de cargador dinámico de addons."""
    
    def __init__(self, logger: Logger = None):
        """
        Inicializar cargador.
        
        Args:
            logger: Logger para logging
        """
        self.logger = logger
    
    def load_addon_class(self, addon_path: str, entry_point: str) -> Optional[type]:
        """Cargar clase de un addon dinámicamente."""
        try:
            addon_dir = Path(addon_path)
            addon_name = addon_dir.name
            
            # Dividir entry_point en módulo y clase
            parts = entry_point.split('.')
            if len(parts) != 2:
                if self.logger:
                    self.logger.error(f"Entry point inválido: {entry_point}")
                return None
                
            module_name, class_name = parts
            
            # Construir path completo del módulo
            module_file = addon_dir / f"{module_name}.py"
            if not module_file.exists():
                if self.logger:
                    self.logger.error(f"Archivo de módulo no encontrado: {module_file}")
                return None
            
            # Crear spec del módulo
            spec = importlib.util.spec_from_file_location(
                f"addon_{addon_name}_{module_name}",
                module_file
            )
            
            if spec is None or spec.loader is None:
                if self.logger:
                    self.logger.error(f"No se pudo crear spec para {module_file}")
                return None
            
            # Cargar el módulo
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            
            # Obtener la clase
            if not hasattr(module, class_name):
                if self.logger:
                    self.logger.error(f"Clase {class_name} no encontrada en {module_name}")
                return None
                
            addon_class = getattr(module, class_name)
            
            # Validar la clase
            if not self.validate_addon_class(addon_class):
                return None
                
            return addon_class
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error cargando clase de addon {addon_path}: {e}")
            return None
    
    def create_addon_instance(self, addon_class: type, context: AddonContext) -> Optional[AddonBase]:
        """Crear instancia de un addon."""
        try:
            return addon_class(context)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creando instancia de addon {addon_class.__name__}: {e}")
            return None
    
    def validate_addon_class(self, addon_class: type) -> bool:
        """Validar que una clase sea un addon válido."""
        try:
            # Verificar que herede de AddonBase
            if not issubclass(addon_class, AddonBase):
                if self.logger:
                    self.logger.error(f"Clase {addon_class.__name__} no hereda de AddonBase")
                return False
                
            # Verificar que implemente métodos requeridos
            required_methods = ['get_manifest', 'initialize', 'shutdown']
            for method_name in required_methods:
                if not hasattr(addon_class, method_name):
                    if self.logger:
                        self.logger.error(f"Clase {addon_class.__name__} no implementa {method_name}")
                    return False
                    
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validando clase de addon: {e}")
            return False


class InMemoryAddonRegistry(AddonRegistry):
    """Implementación de registro de addons en memoria."""
    
    def __init__(self, logger: Logger = None):
        """
        Inicializar registro.
        
        Args:
            logger: Logger para logging
        """
        self.addons: Dict[str, AddonBase] = {}
        self.logger = logger
    
    def register_addon(self, addon_name: str, addon_instance: AddonBase) -> bool:
        """Registrar una instancia de addon."""
        try:
            self.addons[addon_name] = addon_instance
            if self.logger:
                self.logger.info(f"Addon {addon_name} registrado exitosamente")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error registrando addon {addon_name}: {e}")
            return False
    
    def unregister_addon(self, addon_name: str) -> bool:
        """Desregistrar un addon."""
        try:
            if addon_name in self.addons:
                del self.addons[addon_name]
                if self.logger:
                    self.logger.info(f"Addon {addon_name} desregistrado exitosamente")
                return True
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error desregistrando addon {addon_name}: {e}")
            return False
    
    def get_addon(self, addon_name: str) -> Optional[AddonBase]:
        """Obtener instancia de addon registrado."""
        return self.addons.get(addon_name)
    
    def get_all_addons(self) -> Dict[str, AddonBase]:
        """Obtener todos los addons registrados."""
        return self.addons.copy()
    
    def get_addons_by_type(self, addon_type: AddonType) -> List[AddonBase]:
        """Obtener addons por tipo."""
        result = []
        for addon in self.addons.values():
            try:
                manifest = addon.get_manifest()
                if manifest and manifest.addon_type == addon_type:
                    result.append(addon)
            except Exception:
                continue
        return result
    
    def get_active_addons(self) -> List[AddonBase]:
        """Obtener addons activos."""
        return [addon for addon in self.addons.values() if addon.is_active()]
    
    def execute_addon_action(self, addon_name: str, action: str, **kwargs) -> Any:
        """Ejecutar acción de un addon."""
        try:
            addon = self.get_addon(addon_name)
            if not addon or not addon.is_active():
                return None
                
            # Obtener acciones registradas del addon
            actions = addon.register_menu_actions()
            if action not in actions:
                if self.logger:
                    self.logger.warning(f"Acción {action} no encontrada en addon {addon_name}")
                return None
                
            # Ejecutar la acción
            action_func = actions[action]
            return action_func(**kwargs)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error ejecutando acción {action} en addon {addon_name}: {e}")
            return None


class AddonManagerImpl(AddonManager):
    """Implementación principal del gestor de addons."""
    
    def __init__(
        self,
        repository: AddonRepository,
        loader: AddonLoader,
        registry: AddonRegistry,
        context: AddonContext,
        dataconta_version: str = "3.0.0",
        logger: Logger = None
    ):
        """
        Inicializar gestor de addons.
        
        Args:
            repository: Repositorio de addons
            loader: Cargador de addons
            registry: Registro de addons
            context: Contexto de la aplicación
            dataconta_version: Versión actual de DataConta
            logger: Logger para logging
        """
        self.repository = repository
        self.loader = loader
        self.registry = registry
        self.context = context
        self.dataconta_version = dataconta_version
        self.logger = logger
        
        # Cache de manifiestos
        self._manifests_cache: Dict[str, AddonManifest] = {}
    
    def scan_addons(self) -> int:
        """Escanear y encontrar addons disponibles."""
        try:
            addon_paths = self.repository.find_all_addons()
            valid_count = 0
            
            for addon_path in addon_paths:
                if self.repository.validate_addon(addon_path):
                    manifest = self.repository.load_addon_manifest(addon_path)
                    if manifest:
                        self._manifests_cache[manifest.name] = manifest
                        valid_count += 1
                        
            if self.logger:
                self.logger.info(f"Escaneados {valid_count} addons válidos de {len(addon_paths)} encontrados")
                
            return valid_count
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error escaneando addons: {e}")
            return 0
    
    def load_addon(self, addon_name: str) -> bool:
        """Cargar un addon específico."""
        try:
            # Verificar si ya está cargado
            if self.registry.get_addon(addon_name):
                if self.logger:
                    self.logger.warning(f"Addon {addon_name} ya está cargado")
                return True
                
            # Buscar manifiesto
            manifest = self._manifests_cache.get(addon_name)
            if not manifest:
                # Intentar reescanear
                self.scan_addons()
                manifest = self._manifests_cache.get(addon_name)
                
            if not manifest:
                if self.logger:
                    self.logger.error(f"Manifiesto no encontrado para addon {addon_name}")
                return False
                
            # Verificar compatibilidad
            if not self.is_addon_compatible(manifest):
                if self.logger:
                    self.logger.error(f"Addon {addon_name} no es compatible")
                return False
                
            # Encontrar path del addon
            addon_paths = self.repository.find_all_addons()
            addon_path = None
            
            for path in addon_paths:
                path_manifest = self.repository.load_addon_manifest(path)
                if path_manifest and path_manifest.name == addon_name:
                    addon_path = path
                    break
                    
            if not addon_path:
                if self.logger:
                    self.logger.error(f"Path no encontrado para addon {addon_name}")
                return False
                
            # Cargar clase del addon
            addon_class = self.loader.load_addon_class(addon_path, manifest.entry_point)
            if not addon_class:
                return False
                
            # Crear instancia
            addon_instance = self.loader.create_addon_instance(addon_class, self.context)
            if not addon_instance:
                return False
                
            # Registrar addon
            if not self.registry.register_addon(addon_name, addon_instance):
                return False
                
            if self.logger:
                self.logger.info(f"Addon {addon_name} cargado exitosamente")
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error cargando addon {addon_name}: {e}")
            return False
    
    def unload_addon(self, addon_name: str) -> bool:
        """Descargar un addon específico."""
        try:
            addon = self.registry.get_addon(addon_name)
            if not addon:
                return True  # Ya está descargado
                
            # Desactivar addon
            if addon.is_active():
                addon.deactivate()
                
            # Desregistrar
            return self.registry.unregister_addon(addon_name)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error descargando addon {addon_name}: {e}")
            return False
    
    def get_loaded_addons(self) -> List[str]:
        """Obtener lista de addons cargados."""
        return list(self.registry.get_all_addons().keys())
    
    def get_addon_info(self, addon_name: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un addon."""
        try:
            addon = self.registry.get_addon(addon_name)
            if not addon:
                # Buscar en cache de manifiestos
                manifest = self._manifests_cache.get(addon_name)
                if manifest:
                    return {
                        'name': manifest.name,
                        'version': manifest.version,
                        'description': manifest.description,
                        'author': manifest.author,
                        'type': manifest.addon_type.value,
                        'status': 'not_loaded',
                        'loaded': False
                    }
                return None
                
            manifest = addon.get_manifest()
            return {
                'name': manifest.name if manifest else addon_name,
                'version': manifest.version if manifest else '0.0.0',
                'description': manifest.description if manifest else '',
                'author': manifest.author if manifest else '',
                'type': manifest.addon_type.value if manifest else 'unknown',
                'status': addon.get_status().value,
                'loaded': True,
                'active': addon.is_active()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error obteniendo info de addon {addon_name}: {e}")
            return None
    
    def is_addon_compatible(self, manifest: AddonManifest) -> bool:
        """Verificar si un addon es compatible con la versión actual."""
        try:
            current_version = version.parse(self.dataconta_version)
            min_version = version.parse(manifest.min_dataconta_version)
            
            if current_version < min_version:
                return False
                
            if manifest.max_dataconta_version:
                max_version = version.parse(manifest.max_dataconta_version)
                if current_version > max_version:
                    return False
                    
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error verificando compatibilidad: {e}")
            return False
    
    def enable_addon(self, addon_name: str) -> bool:
        """Habilitar un addon."""
        try:
            # Cargar addon si no está cargado
            if not self.registry.get_addon(addon_name):
                if not self.load_addon(addon_name):
                    return False
                    
            # Activar addon
            addon = self.registry.get_addon(addon_name)
            if addon:
                return addon.activate()
                
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error habilitando addon {addon_name}: {e}")
            return False
    
    def disable_addon(self, addon_name: str) -> bool:
        """Deshabilitar un addon."""
        try:
            addon = self.registry.get_addon(addon_name)
            if addon:
                return addon.deactivate()
            return True  # Ya está deshabilitado
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error deshabilitando addon {addon_name}: {e}")
            return False