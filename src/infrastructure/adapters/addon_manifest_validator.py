"""
Addon Manifest Validator
Validador de manifiestos de addons usando JSON Schema y validaciones adicionales de seguridad.
"""

import json
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from src.application.ports.interfaces import Logger


class AddonManifestValidator:
    """
    Validador de manifiestos de addons.
    
    Proporciona validación exhaustiva de manifiestos incluyendo:
    - Validación de esquema JSON
    - Validaciones de seguridad
    - Validaciones semánticas
    - Verificación de integridad
    """
    
    def __init__(self, schema_path: str = None, logger: Logger = None):
        """
        Inicializar validador.
        
        Args:
            schema_path: Path al archivo de schema JSON
            logger: Logger para logging
        """
        self.logger = logger
        self.schema = None
        
        # Cargar schema JSON
        if schema_path:
            self.load_schema(schema_path)
        else:
            # Usar schema por defecto
            default_schema_path = Path(__file__).parent.parent.parent.parent / "addons" / "addon_manifest.schema.json"
            if default_schema_path.exists():
                self.load_schema(str(default_schema_path))
    
    def load_schema(self, schema_path: str) -> bool:
        """
        Cargar schema JSON desde archivo.
        
        Args:
            schema_path: Path al archivo de schema
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
                
            if self.logger:
                self.logger.info(f"✅ Schema de addon cargado: {schema_path}")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cargando schema {schema_path}: {e}")
            return False
    
    def validate_manifest(self, manifest_data: Dict[str, Any], addon_path: str = None) -> Tuple[bool, List[str]]:
        """
        Validar manifiesto de addon completo.
        
        Args:
            manifest_data: Datos del manifiesto a validar
            addon_path: Path del addon (para validaciones adicionales)
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_de_errores)
        """
        errors = []
        
        # 1. Validación de schema JSON
        schema_errors = self._validate_json_schema(manifest_data)
        errors.extend(schema_errors)
        
        # 2. Validaciones semánticas
        semantic_errors = self._validate_semantics(manifest_data)
        errors.extend(semantic_errors)
        
        # 3. Validaciones de seguridad
        security_errors = self._validate_security(manifest_data, addon_path)
        errors.extend(security_errors)
        
        # 4. Validaciones de integridad (si addon_path está disponible)
        if addon_path:
            integrity_errors = self._validate_integrity(manifest_data, addon_path)
            errors.extend(integrity_errors)
        
        is_valid = len(errors) == 0
        
        if self.logger:
            if is_valid:
                self.logger.info(f"✅ Manifiesto válido: {manifest_data.get('name', 'unknown')}")
            else:
                self.logger.error(f"❌ Manifiesto inválido: {len(errors)} errores encontrados")
                
        return is_valid, errors
    
    def _validate_json_schema(self, manifest_data: Dict[str, Any]) -> List[str]:
        """Validar contra schema JSON."""
        errors = []
        
        if not JSONSCHEMA_AVAILABLE:
            errors.append("jsonschema no está instalado - validación de schema omitida")
            return errors
            
        if not self.schema:
            errors.append("Schema JSON no está cargado")
            return errors
            
        try:
            jsonschema.validate(manifest_data, self.schema)
            
        except jsonschema.ValidationError as e:
            errors.append(f"Error de schema: {e.message} en {e.json_path}")
            
        except jsonschema.SchemaError as e:
            errors.append(f"Error en schema JSON: {e.message}")
            
        except Exception as e:
            errors.append(f"Error validando schema: {str(e)}")
            
        return errors
    
    def _validate_semantics(self, manifest_data: Dict[str, Any]) -> List[str]:
        """Validar semántica del manifiesto."""
        errors = []
        
        # Validar nombre del addon
        name = manifest_data.get('name', '')
        if not self._is_valid_addon_name(name):
            errors.append(f"Nombre de addon inválido: '{name}' - debe ser snake_case, 3-50 chars")
            
        # Validar entry point
        entry_point = manifest_data.get('entry_point', '')
        if not self._is_valid_entry_point(entry_point):
            errors.append(f"Entry point inválido: '{entry_point}' - debe ser 'module.ClassName'")
            
        # Validar versión
        version = manifest_data.get('version', '')
        if not self._is_valid_semver(version):
            errors.append(f"Versión inválida: '{version}' - debe seguir semántica (x.y.z)")
            
        # Validar dependencias
        dependencies = manifest_data.get('dependencies', [])
        dep_errors = self._validate_dependencies(dependencies)
        errors.extend(dep_errors)
        
        # Validar items de menú
        menu_items = manifest_data.get('menu_items', [])
        menu_errors = self._validate_menu_items(menu_items)
        errors.extend(menu_errors)
        
        # Validar permisos
        permissions = manifest_data.get('permissions', [])
        perm_errors = self._validate_permissions(permissions)
        errors.extend(perm_errors)
        
        return errors
    
    def _validate_security(self, manifest_data: Dict[str, Any], addon_path: str = None) -> List[str]:
        """Validar aspectos de seguridad."""
        errors = []
        
        # Verificar permisos peligrosos
        permissions = manifest_data.get('permissions', [])
        dangerous_perms = self._check_dangerous_permissions(permissions)
        if dangerous_perms:
            errors.append(f"Permisos peligrosos detectados: {dangerous_perms}")
        
        # Verificar dependencias sospechosas
        dependencies = manifest_data.get('dependencies', [])
        suspicious_deps = self._check_suspicious_dependencies(dependencies)
        if suspicious_deps:
            errors.append(f"Dependencias sospechosas: {suspicious_deps}")
        
        # Verificar URLs sospechosas
        urls = [
            manifest_data.get('homepage'),
            manifest_data.get('repository')
        ]
        suspicious_urls = self._check_suspicious_urls([url for url in urls if url])
        if suspicious_urls:
            errors.append(f"URLs sospechosas: {suspicious_urls}")
            
        # Validar sandbox settings
        security_config = manifest_data.get('security', {})
        if not security_config.get('sandbox', True):
            errors.append("Addon solicita deshabilitar sandbox - requiere revisión manual")
            
        return errors
    
    def _validate_integrity(self, manifest_data: Dict[str, Any], addon_path: str) -> List[str]:
        """Validar integridad del addon."""
        errors = []
        addon_dir = Path(addon_path)
        
        # Verificar que existe el archivo principal
        entry_point = manifest_data.get('entry_point', '')
        if '.' in entry_point:
            module_name = entry_point.split('.')[0]
            main_file = addon_dir / f"{module_name}.py"
            
            if not main_file.exists():
                errors.append(f"Archivo principal no encontrado: {main_file}")
            elif not self._is_valid_python_file(main_file):
                errors.append(f"Archivo principal no es Python válido: {main_file}")
        
        # Verificar checksum si está especificado
        security_config = manifest_data.get('security', {})
        expected_checksum = security_config.get('checksum')
        
        if expected_checksum:
            actual_checksum = self._calculate_addon_checksum(addon_dir)
            if actual_checksum != expected_checksum:
                errors.append(f"Checksum no coincide: esperado {expected_checksum}, actual {actual_checksum}")
        
        # Verificar estructura de archivos
        structure_errors = self._validate_file_structure(addon_dir, manifest_data)
        errors.extend(structure_errors)
        
        return errors
    
    def _is_valid_addon_name(self, name: str) -> bool:
        """Verificar si el nombre del addon es válido."""
        if not name or not isinstance(name, str):
            return False
        return bool(re.match(r'^[a-z][a-z0-9_]{2,49}$', name))
    
    def _is_valid_entry_point(self, entry_point: str) -> bool:
        """Verificar si el entry point es válido."""
        if not entry_point or not isinstance(entry_point, str):
            return False
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*$', entry_point))
    
    def _is_valid_semver(self, version: str) -> bool:
        """Verificar si la versión es semántica válida."""
        if not version or not isinstance(version, str):
            return False
        return bool(re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$', version))
    
    def _validate_dependencies(self, dependencies: List[str]) -> List[str]:
        """Validar lista de dependencias."""
        errors = []
        
        if not isinstance(dependencies, list):
            return ["dependencies debe ser una lista"]
            
        for dep in dependencies:
            if not isinstance(dep, str):
                errors.append(f"Dependencia inválida: {dep} - debe ser string")
                continue
                
            # Validar formato de dependencia
            if not re.match(r'^[a-zA-Z0-9_-]+(>=|<=|==|~=|!=)?[0-9.]*$', dep):
                errors.append(f"Formato de dependencia inválido: {dep}")
                
        return errors
    
    def _validate_menu_items(self, menu_items: List[Dict]) -> List[str]:
        """Validar items de menú."""
        errors = []
        
        if not isinstance(menu_items, list):
            return ["menu_items debe ser una lista"]
            
        used_ids = set()
        
        for i, item in enumerate(menu_items):
            if not isinstance(item, dict):
                errors.append(f"Menu item {i} debe ser un objeto")
                continue
                
            # Verificar campos requeridos
            required_fields = ['id', 'label', 'action']
            for field in required_fields:
                if field not in item:
                    errors.append(f"Menu item {i} falta campo requerido: {field}")
                    
            # Verificar ID único
            item_id = item.get('id')
            if item_id in used_ids:
                errors.append(f"Menu item ID duplicado: {item_id}")
            used_ids.add(item_id)
                
        return errors
    
    def _validate_permissions(self, permissions: List[str]) -> List[str]:
        """Validar permisos."""
        errors = []
        
        if not isinstance(permissions, list):
            return ["permissions debe ser una lista"]
            
        valid_permissions = {
            'file_read', 'file_write', 'api_access', 'network_access',
            'system_info', 'ui_modify', 'menu_add', 'data_export',
            'data_import', 'email_send', 'notification_send'
        }
        
        for perm in permissions:
            if not isinstance(perm, str):
                errors.append(f"Permiso inválido: {perm} - debe ser string")
                continue
                
            if perm not in valid_permissions:
                errors.append(f"Permiso desconocido: {perm}")
                
        return errors
    
    def _check_dangerous_permissions(self, permissions: List[str]) -> List[str]:
        """Detectar permisos peligrosos."""
        dangerous = {'file_write', 'system_info', 'network_access'}
        return [perm for perm in permissions if perm in dangerous]
    
    def _check_suspicious_dependencies(self, dependencies: List[str]) -> List[str]:
        """Detectar dependencias sospechosas."""
        # Lista de paquetes que podrían ser problemáticos
        suspicious = {
            'subprocess32', 'os', 'sys', 'eval', 'exec',
            'requests', 'urllib', 'socket', 'threading'
        }
        
        suspicious_found = []
        for dep in dependencies:
            dep_name = dep.split('>=')[0].split('<=')[0].split('==')[0].split('~=')[0].split('!=')[0]
            if dep_name.lower() in suspicious:
                suspicious_found.append(dep)
                
        return suspicious_found
    
    def _check_suspicious_urls(self, urls: List[str]) -> List[str]:
        """Detectar URLs sospechosas."""
        suspicious = []
        suspicious_patterns = [
            r'\.tk$', r'\.ml$', r'\.ga$', r'\.cf$',  # TLD sospechosos
            r'bit\.ly', r'tinyurl\.com',  # URL shorteners
            r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',  # IPs directas
        ]
        
        for url in urls:
            for pattern in suspicious_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    suspicious.append(url)
                    break
                    
        return suspicious
    
    def _is_valid_python_file(self, file_path: Path) -> bool:
        """Verificar si es un archivo Python válido."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificación básica de sintaxis Python
            compile(content, str(file_path), 'exec')
            return True
            
        except Exception:
            return False
    
    def _calculate_addon_checksum(self, addon_dir: Path) -> str:
        """Calcular checksum SHA256 del addon."""
        try:
            hasher = hashlib.sha256()
            
            # Incluir todos los archivos .py en el checksum
            python_files = sorted(addon_dir.glob('*.py'))
            
            for py_file in python_files:
                with open(py_file, 'rb') as f:
                    hasher.update(f.read())
                    
            return hasher.hexdigest()
            
        except Exception:
            return ""
    
    def _validate_file_structure(self, addon_dir: Path, manifest_data: Dict[str, Any]) -> List[str]:
        """Validar estructura de archivos del addon."""
        errors = []
        
        # Archivos requeridos
        required_files = ['manifest.json']
        
        # Agregar archivo principal basado en entry_point
        entry_point = manifest_data.get('entry_point', '')
        if '.' in entry_point:
            module_name = entry_point.split('.')[0]
            required_files.append(f"{module_name}.py")
        
        # Verificar archivos requeridos
        for req_file in required_files:
            file_path = addon_dir / req_file
            if not file_path.exists():
                errors.append(f"Archivo requerido faltante: {req_file}")
        
        # Verificar archivos prohibidos
        prohibited_patterns = [
            '*.exe', '*.bat', '*.cmd', '*.sh', '*.dll', '*.so',
            '__pycache__', '*.pyc', '.git', '.svn'
        ]
        
        for pattern in prohibited_patterns:
            matches = list(addon_dir.glob(pattern))
            if matches:
                errors.append(f"Archivos prohibidos encontrados: {[f.name for f in matches]}")
        
        return errors
    
    def create_validation_report(self, manifest_data: Dict[str, Any], addon_path: str = None) -> Dict[str, Any]:
        """
        Crear reporte detallado de validación.
        
        Args:
            manifest_data: Datos del manifiesto
            addon_path: Path del addon
            
        Returns:
            Dict con reporte detallado
        """
        is_valid, errors = self.validate_manifest(manifest_data, addon_path)
        
        report = {
            'addon_name': manifest_data.get('name', 'unknown'),
            'addon_version': manifest_data.get('version', '0.0.0'),
            'is_valid': is_valid,
            'error_count': len(errors),
            'errors': errors,
            'checks_performed': [
                'json_schema_validation',
                'semantic_validation', 
                'security_validation'
            ],
            'validation_timestamp': self._get_timestamp()
        }
        
        if addon_path:
            report['checks_performed'].append('integrity_validation')
            report['addon_path'] = addon_path
            
        # Agregar información adicional si es válido
        if is_valid:
            report['addon_info'] = {
                'type': manifest_data.get('addon_type'),
                'author': manifest_data.get('author'),
                'license': manifest_data.get('license', 'MIT'),
                'requires_license': manifest_data.get('requires_license', 'FREE'),
                'permissions': manifest_data.get('permissions', []),
                'menu_items_count': len(manifest_data.get('menu_items', [])),
                'dependencies_count': len(manifest_data.get('dependencies', []))
            }
            
        return report
    
    def _get_timestamp(self) -> str:
        """Obtener timestamp actual."""
        from datetime import datetime
        return datetime.now().isoformat()


def validate_addon_manifest(
    manifest_file_path: str,
    addon_path: str = None,
    schema_path: str = None,
    logger: Logger = None
) -> Tuple[bool, List[str]]:
    """
    Función helper para validar un manifiesto de addon.
    
    Args:
        manifest_file_path: Path al archivo manifest.json
        addon_path: Path del addon (opcional)
        schema_path: Path al schema JSON (opcional)
        logger: Logger (opcional)
        
    Returns:
        Tuple[bool, List[str]]: (es_valido, lista_de_errores)
    """
    try:
        # Cargar manifiesto
        with open(manifest_file_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        # Crear validador
        validator = AddonManifestValidator(schema_path, logger)
        
        # Validar
        return validator.validate_manifest(manifest_data, addon_path)
        
    except Exception as e:
        error_msg = f"Error validando manifiesto {manifest_file_path}: {e}"
        if logger:
            logger.error(error_msg)
        return False, [error_msg]