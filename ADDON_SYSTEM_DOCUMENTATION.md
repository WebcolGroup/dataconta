# 🔌 Sistema de Addons para DataConta

## 📋 Introducción

El **Sistema de Addons de DataConta** permite a la comunidad crear extensiones que amplían la funcionalidad de la aplicación sin modificar el código base. Siguiendo los principios de **Arquitectura Hexagonal** y **SOLID**, el sistema proporciona una base sólida y segura para el desarrollo de addons.

## 🏗️ Arquitectura

### **Principios de Diseño:**
- ✅ **Arquitectura Hexagonal**: Separación clara entre dominio, aplicación e infraestructura
- ✅ **Principios SOLID**: Interfaces bien definidas, responsabilidad única
- ✅ **No-Breaking Changes**: Cero impacto en funcionalidad existente
- ✅ **Security-First**: Validaciones, permisos y sandbox
- ✅ **Hot-Loading**: Carga/descarga dinámica de addons

### **Componentes Principales:**

#### **1. Core Interfaces (`src/application/ports/addon_interfaces.py`)**
```python
# Interfaces fundamentales
- AddonBase: Clase base para todos los addons
- AddonManager: Gestión del ciclo de vida de addons  
- AddonRepository: Almacenamiento y carga de addons
- AddonContext: Contexto de dependencias inyectadas
- AddonManifest: Estructura de metadatos del addon
```

#### **2. Infrastructure Adapters (`src/infrastructure/adapters/`)**
```python
# Implementaciones concretas
- FileSystemAddonRepository: Repositorio basado en archivos
- DynamicAddonLoader: Carga dinámica de módulos Python
- AddonManagerImpl: Manager principal con ciclo de vida completo
- AddonManifestValidator: Validador con 60+ reglas de seguridad
```

#### **3. Menu Integration (`addon_menu_integration.py`)**
```python  
# Integración con menús dinámicos
- AddonMenuIntegration: Integra menús de addons
- EnhancedDynamicMenuManager: Manager extendido compatible
- AddonMenuAction: Acciones específicas de addon
```

#### **4. Factory Pattern (`addon_factory.py`)**
```python
# Inyección de dependencias
- AddonFactory: Factory para crear sistema completo
- Dependency injection para Logger, MenuManager, etc.
```

## 📦 Estructura de un Addon

### **Archivo Manifest (`manifest.json`)**
```json
{
  "name": "mi_addon",
  "display_name": "Mi Addon Increíble", 
  "version": "1.0.0",
  "addon_type": "utility|integration|report|analysis",
  "description": "Descripción del addon",
  "author": "Desarrollador",
  "license": "MIT",
  "entry_point": "mi_addon.MiAddonClass",
  "requires_license": "FREE|PROFESSIONAL|ENTERPRISE",
  
  "dependencies": ["requests>=2.25.0", "pandas>=1.3.0"],
  
  "permissions": [
    "file_read", "file_write", "api_access", 
    "network_access", "email_send"
  ],
  
  "menu_items": [
    {
      "id": "mi_accion",
      "label": "Mi Acción", 
      "icon": "🚀",
      "action": "execute_my_action",
      "requires_confirmation": true
    }
  ],
  
  "security": {
    "sandbox": true,
    "network_access": true,
    "file_access": "read_only"
  }
}
```

### **Implementación del Addon**
```python
from src.application.ports.addon_interfaces import AddonBase, AddonContext

class MiAddon(AddonBase):
    def initialize(self, context: AddonContext) -> bool:
        self.context = context
        self.logger = context.logger
        return True
    
    def execute_action(self, action: str, params: dict) -> bool:
        if action == "execute_my_action":
            return self._mi_logica_personalizada(params)
        return False
    
    def get_name(self) -> str:
        return "mi_addon"
```

## 🛠️ Guía de Desarrollo

### **1. Crear Nuevo Addon**

#### **Paso 1: Estructura de Carpetas**
```
addons/
└── mi_addon/
    ├── manifest.json       # Configuración del addon
    ├── mi_addon.py        # Implementación principal  
    ├── README.md          # Documentación
    └── requirements.txt   # Dependencias (opcional)
```

#### **Paso 2: Implementar AddonBase**
```python
from src.application.ports.addon_interfaces import AddonBase, AddonContext, AddonManifest
from typing import Dict, Any
import json
from pathlib import Path

class MiAddon(AddonBase):
    def __init__(self):
        super().__init__()
        self.manifest = None
        
    def initialize(self, context: AddonContext) -> bool:
        try:
            self.context = context
            self.logger = context.logger
            
            # Cargar manifest
            manifest_path = Path(__file__).parent / "manifest.json"
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            self.manifest = AddonManifest(**manifest_data)
            
            # Tu lógica de inicialización aquí
            
            return True
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Error inicializando addon: {e}")
            return False
    
    def execute_action(self, action_name: str, parameters: Dict[str, Any] = None) -> bool:
        # Mapear acciones a métodos
        action_map = {
            'mi_accion_1': self._accion_1,
            'mi_accion_2': self._accion_2
        }
        
        if action_name in action_map:
            return action_map[action_name](parameters or {})
        return False
    
    def _accion_1(self, params: Dict[str, Any]) -> bool:
        # Implementar lógica específica
        if self.logger:
            self.logger.info("Ejecutando acción 1")
        return True
```

#### **Paso 3: Validar Addon**
```python
# Test básico
from src.infrastructure.adapters.addon_manifest_validator import validate_addon_manifest

is_valid, errors = validate_addon_manifest(
    "addons/mi_addon/manifest.json",
    "addons/mi_addon/"
)

if is_valid:
    print("✅ Addon válido")
else:
    print("❌ Errores encontrados:")
    for error in errors:
        print(f"  - {error}")
```

### **2. Tipos de Addons Recomendados**

#### **🔧 Utility Addons**
- Herramientas auxiliares
- Calculadoras especializadas
- Conversores de datos
- Validadores personalizados

#### **🔗 Integration Addons**  
- Conectores con APIs externas
- Sincronización con otros sistemas
- Webhooks y notificaciones
- Importadores/exportadores

#### **📊 Report Addons**
- Reportes personalizados
- Dashboards específicos
- Análisis avanzados
- Visualizaciones custom

#### **🤖 Analysis Addons**
- Machine Learning
- Análisis predictivo
- Detección de anomalías
- Clasificación automática

## 🔐 Sistema de Seguridad

### **Validaciones del Manifest**
- ✅ **Schema JSON**: 60+ reglas de validación
- ✅ **Semantic Validation**: Nombres, versiones, dependencias
- ✅ **Security Validation**: Permisos, URLs, dependencias sospechosas
- ✅ **Integrity Validation**: Checksums, estructura de archivos

### **Sistema de Permisos**
```json
{
  "permissions": [
    "file_read",        // Leer archivos del sistema
    "file_write",       // Escribir archivos 
    "api_access",       // Acceso a APIs internas
    "network_access",   // Conexiones de red
    "system_info",      // Información del sistema
    "ui_modify",        // Modificar interfaz
    "menu_add",         // Agregar menús
    "data_export",      // Exportar datos
    "data_import",      // Importar datos
    "email_send",       // Enviar emails
    "notification_send" // Enviar notificaciones
  ]
}
```

### **Sandbox Security**
```json
{
  "security": {
    "sandbox": true,                    // Habilitar sandbox
    "network_access": false,            // Restringir red
    "file_access": "read_only",         // Solo lectura
    "checksum": "sha256_hash_here"      // Verificación integridad
  }
}
```

## 🚀 Integración con DataConta

### **1. Cargar Sistema de Addons**
```python
from src.infrastructure.factories.addon_factory import AddonFactory
from src.application.ports.interfaces import Logger

# Crear sistema de addons
logger = ConsoleLogger()  # O tu implementación de Logger
addon_system = AddonFactory.create_complete_addon_system(
    repository_path="addons/",
    logger=logger
)

# Cargar addons
addon_system.load_all_addons()

# Obtener addons activos
active_addons = addon_system.get_active_addons()
print(f"Addons cargados: {len(active_addons)}")
```

### **2. Integrar con Menús**
```python
from src.infrastructure.adapters.addon_menu_integration import EnhancedDynamicMenuManager
from src.infrastructure.config.dynamic_menu_config import DynamicMenuManager

# Crear manager de menús extendido
menu_manager = EnhancedDynamicMenuManager(
    config_file="menu_config.json",
    addon_manager=addon_system,
    logger=logger
)

# Cargar configuración (incluye addons automáticamente)
menu_manager.load_config()

# Obtener botones de menú (sistema + addons)
buttons = menu_manager.create_menu_buttons()
```

### **3. Ejecutar Acciones de Addon**
```python  
# A través del menu manager
success = menu_manager.execute_action("addon_mi_addon_mi_accion", {"param1": "valor"})

# Directamente con addon manager
addon = addon_system.get_addon("mi_addon")
if addon:
    result = addon.execute_action("mi_accion", {"data": "test"})
```

## 📊 Monitoreo y Debugging

### **Logs del Sistema**
```python
# Configurar logging detallado
logger.info("🔄 Cargando addons...")
logger.debug("📦 Addon cargado: email_reports v1.0.0")
logger.warning("⚠️ Addon requiere permisos adicionales")
logger.error("❌ Error en addon: permiso denegado")
```

### **Estadísticas de Addons**
```python
# Obtener estadísticas completas
stats = menu_manager.get_menu_statistics()
print(f"""
📊 Estadísticas del Sistema:
   - Categorías del sistema: {stats['system_categories']}
   - Categorías de addons: {stats['addon_categories']}
   - Total acciones: {stats['total_actions']}
   - Addons activos: {len(addon_system.get_active_addons())}
""")
```

### **Validación en Tiempo Real**
```python
# Validar addon antes de carga
from src.infrastructure.adapters.addon_manifest_validator import AddonManifestValidator

validator = AddonManifestValidator(logger=logger)
is_valid, errors = validator.validate_manifest(manifest_data, addon_path)

if not is_valid:
    logger.error(f"Addon inválido: {errors}")
```

## 🧪 Testing

### **Test de Addon Individual**
```python
# test_mi_addon.py
import unittest
from addons.mi_addon.mi_addon import MiAddon
from src.application.ports.addon_interfaces import AddonContext

class TestMiAddon(unittest.TestCase):
    def setUp(self):
        self.addon = MiAddon()
        self.context = AddonContext(logger=MockLogger())
        
    def test_initialize(self):
        result = self.addon.initialize(self.context)
        self.assertTrue(result)
        
    def test_execute_action(self):
        self.addon.initialize(self.context)
        result = self.addon.execute_action("mi_accion", {})
        self.assertTrue(result)
```

### **Test de Integración**
```python  
# test_addon_system.py
def test_complete_addon_system():
    # Crear sistema
    addon_system = AddonFactory.create_complete_addon_system(
        repository_path="test_addons/",
        logger=MockLogger()
    )
    
    # Cargar addons
    loaded = addon_system.load_all_addons()
    assert loaded > 0
    
    # Ejecutar acción
    success = addon_system.execute_addon_action("test_addon", "test_action", {})
    assert success
```

## 📚 Ejemplos de Addons

### **1. Email Reports Addon** (Incluido)
- 📧 Envío de reportes por email
- 📊 Reportes diarios y mensuales
- ⚙️ Configuración flexible
- 📍 Ubicación: `addons/email_reports/`

### **2. Data Analyzer Addon** (Ejemplo)
```python
class DataAnalyzerAddon(AddonBase):
    def execute_action(self, action: str, params: dict) -> bool:
        if action == "analyze_sales_trends":
            return self._analyze_trends(params)
        elif action == "detect_anomalies":
            return self._detect_anomalies(params)
        return False
```

### **3. API Connector Addon** (Ejemplo)
```python
class ApiConnectorAddon(AddonBase):
    def execute_action(self, action: str, params: dict) -> bool:
        if action == "sync_with_external_api":
            return self._sync_data(params)
        elif action == "export_to_webhook":
            return self._export_webhook(params)
        return False
```

## 🔄 Ciclo de Vida de Addon

### **1. Desarrollo**
1. ✅ Crear estructura de carpetas
2. ✅ Implementar AddonBase
3. ✅ Crear manifest.json
4. ✅ Validar con schema JSON
5. ✅ Testing local

### **2. Instalación**
1. ✅ Copiar a carpeta `addons/`
2. ✅ Validación automática
3. ✅ Verificación de permisos
4. ✅ Carga en sistema

### **3. Ejecución**
1. ✅ Inicialización con contexto
2. ✅ Registro en menús
3. ✅ Ejecución de acciones
4. ✅ Logging y monitoreo

### **4. Mantenimiento**
1. ✅ Actualizaciones de versión
2. ✅ Re-validación de seguridad  
3. ✅ Migración de configuración
4. ✅ Cleanup de recursos

## 🚨 Troubleshooting

### **Problemas Comunes**

#### **❌ Addon no se carga**
```
Verificar:
- manifest.json es válido JSON
- entry_point apunta a clase correcta
- permissions están bien definidos
- dependencies están instaladas
```

#### **❌ Acción no se ejecuta**
```
Verificar:
- action_name coincide con manifest
- método execute_action implementado
- permisos suficientes
- logs para más detalles
```

#### **❌ Menu no aparece**
```
Verificar:  
- menu_items definidos en manifest
- addon está activo
- licencia requerida cumplida
- reload de configuración de menús
```

### **Debugging Tips**
```python
# Habilitar logging detallado
logger.set_level(LogLevel.DEBUG)

# Verificar estado del addon
status = addon.get_status()
logger.info(f"Estado del addon: {status}")

# Validar manifest manualmente
validator = AddonManifestValidator(logger=logger)
report = validator.create_validation_report(manifest_data, addon_path)
logger.info(f"Reporte de validación: {report}")
```

## 📈 Roadmap

### **Versión Actual (1.0)**
- ✅ Sistema base de addons
- ✅ Validación y seguridad
- ✅ Integración con menús  
- ✅ Addon de ejemplo (email_reports)
- ✅ Documentación completa

### **Versión 1.1 (Próximamente)**
- 🔄 Hot-reload de addons
- 🔄 Marketplace de addons
- 🔄 Sandbox más robusto
- 🔄 API REST para addons

### **Versión 1.2 (Futuro)**
- 🔄 Visual addon builder
- 🔄 Containerización de addons
- 🔄 Distributed addon system
- 🔄 AI-powered addon suggestions

## 🤝 Contribución

### **Cómo Contribuir**
1. 🍴 Fork del repositorio
2. 🌿 Crear branch para addon/feature  
3. 🔧 Seguir estándares de código DataConta
4. ✅ Testing completo con coverage > 80%
5. 📝 Documentación clara
6. 🚀 Pull request descriptivo

### **Estándares de Código**
- ✅ Type hints obligatorios
- ✅ Docstrings en todas las funciones
- ✅ PEP 8 compliance
- ✅ Error handling robusto  
- ✅ Logging apropiado
- ✅ Principios SOLID

## 📄 Licencia

**MIT License** - Sistema de addons desarrollado para DataConta con ❤️ por la comunidad.

---

## 🎯 ¿Listo para crear tu primer addon?

1. 📋 Lee esta documentación completa
2. 🔍 Analiza el addon de ejemplo `email_reports`
3. 🛠️ Sigue la guía de desarrollo paso a paso  
4. ✅ Valida tu addon con las herramientas incluidas
5. 🚀 ¡Comparte tu addon con la comunidad!

**¡El futuro de DataConta está en tus manos! 🚀**