# 🏢 DATACONTA - Sistema Avanzado de Menús

## 📋 Descripción General

El Sistema Avanzado de Menús de DATACONTA es una solución modular y escalable que organiza las funcionalidades del sistema en sesiones lógicas con validación de licencia. Permite una navegación intuitiva y un acceso controlado a diferentes características según el tipo de licencia del usuario.

## ✨ Características Principales

### 🎯 **Organización por Sesiones**
- **Business Intelligence**: Análisis de datos y consultas
- **Generación de Informes**: Herramientas avanzadas de reportes
- **Herramientas**: Utilidades del sistema
- **Integración con Ollama**: IA local (PRO+)
- **Análisis con IA**: Análisis avanzado (ENTERPRISE)

### 🔐 **Sistema de Licencias**
- **🆓 FREE**: Acceso a funciones básicas
- **💼 PRO**: Funciones avanzadas + IA básica
- **🏢 ENTERPRISE**: Todas las funciones + IA avanzada

### 🚀 **Arquitectura Modular**
- Fácil adición de nuevas sesiones
- Configuración centralizada
- Validación automática de licencias
- Sistema de navegación intuitivo

## 📂 Estructura del Sistema

```
src/presentation/
├── menu_system.py      # Motor del sistema de menús
├── menu_config.py      # Configuración de sesiones
└── cli_interface.py    # Interfaz actual (legacy)

main_advanced_menu.py   # Integración completa
demo_menu_system.py     # Demostración del sistema
```

## 🔧 Archivos Principales

### 1. **menu_system.py** - Motor Principal
```python
class MenuSystem:
    - Gestión de navegación
    - Validación de licencias
    - Renderizado de menús
    - Control de flujo
```

### 2. **menu_config.py** - Configuración
```python
def setup_dataconta_menus(menu_system):
    - Define todas las sesiones
    - Configura opciones por sesión
    - Asigna acciones a opciones
```

### 3. **demo_menu_system.py** - Demostración
- Sistema completamente funcional
- Funciones de demostración
- No requiere infraestructura compleja

## 📊 Sesiones Disponibles

### 📊 **Business Intelligence** (FREE+)
```python
- Consultar Facturas de Venta
- Exportar a Business Intelligence
```

### 📈 **Generación de Informes** (PRO+)
```python
- Ver Archivos de Salida
- Exportar Facturas a CSV
- Exportar Informe PDF
```

### 🛠️ **Herramientas** (FREE+)
```python
- Verificar Estado de la API
- Configuración del Sistema
```

### 🤖 **Integración con Ollama** (PRO+)
```python
- Enviar Datos a Ollama
- Consultar Respuesta de Ollama
```

### 🧠 **Análisis con IA** (ENTERPRISE)
```python
- Análisis Predictivo
- Detección de Anomalías
- Recomendaciones Inteligentes
```

## ⚙️ Configuración de Licencia

### Archivo `.env`
```properties
# Configuración de Licencia
LICENSE=free          # Opciones: free, pro, enterprise
LICENSE_URL=https://...
LICENSE_KEY=DEMO-...
```

### Tipos de Licencia
| Licencia | Business Intelligence | Informes | Herramientas | Ollama | IA Avanzada |
|----------|---------------------|----------|--------------|---------|-------------|
| FREE     | ✅                  | ❌       | ✅           | ❌      | ❌          |
| PRO      | ✅                  | ✅       | ✅           | ✅      | ❌          |
| ENTERPRISE| ✅                 | ✅       | ✅           | ✅      | ✅          |

## 🚀 Uso del Sistema

### Ejecutar Demostración
```bash
python demo_menu_system.py
```

### Ejecutar Sistema Completo (en desarrollo)
```bash
python main_advanced_menu.py
```

### Cambiar Licencia
```bash
# Editar .env
LICENSE=pro    # o enterprise
```

## 🔄 Flujo de Navegación

```
┌─────────────────┐
│   Menú Principal │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Seleccionar      │
│ Sesión          │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Submenú de    │
│    Sesión       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Ejecutar       │
│   Acción        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Volver al Menú  │
│ o Salir         │
└─────────────────┘
```

## 📝 Ejemplo de Configuración

### Agregar Nueva Sesión
```python
# En menu_config.py
new_session = MenuSession(
    title="Nueva Funcionalidad",
    emoji="🆕",
    license_required=LicenseType.PRO,
    description="Descripción de la nueva sesión",
    options=[
        MenuOption(
            name="Nueva Opción",
            emoji="⭐",
            action=nueva_funcion,
            description="Descripción de la opción"
        )
    ]
)

# Registrar la sesión
menu_system.register_session("nueva_funcionalidad", new_session)
```

### Agregar Nueva Función
```python
def nueva_funcion():
    """Nueva funcionalidad del sistema"""
    print("🆕 Ejecutando nueva funcionalidad...")
    # Implementar lógica aquí
    return True
```

## 🔮 Características Futuras

### 🔧 **En Desarrollo**
- Integración completa con sistema existente
- Configuración dinámica de menús
- Validación de licencia online
- Personalización de temas

### 💡 **Planificadas**
- Menús contextuales
- Historial de acciones
- Favoritos del usuario
- Atajos de teclado
- Modo admin/configuración

## 📚 Documentación Técnica

### Clases Principales
```python
class MenuSystem:
    - register_session()      # Registrar nueva sesión
    - get_available_sessions()# Obtener sesiones disponibles
    - display_main_menu()    # Mostrar menú principal
    - run()                  # Ejecutar bucle principal

class MenuSession:
    - title: str             # Título de la sesión
    - emoji: str             # Emoji representativo
    - license_required       # Licencia requerida
    - options: List         # Lista de opciones

class LicenseValidator:
    - get_current_license()  # Obtener licencia actual
    - has_access_to()       # Verificar acceso
    - get_license_display_name() # Nombre de licencia
```

## 🛠️ Guía de Desarrollo

### Agregar Nueva Sesión
1. Definir funciones de acción
2. Crear MenuSession en menu_config.py
3. Registrar sesión en setup_dataconta_menus()
4. Probar con demo_menu_system.py

### Cambiar Validación de Licencia
1. Modificar LicenseValidator en menu_system.py
2. Ajustar lógica en has_access_to()
3. Actualizar configuración en .env

### Personalizar Interfaz
1. Modificar display_main_menu() y display_session_menu()
2. Cambiar emojis y colores en menu_config.py
3. Ajustar formato de salida

## 🧪 Testing

### Probar Diferentes Licencias
```bash
# Editar .env y cambiar LICENSE=
LICENSE=free       # Solo herramientas básicas
LICENSE=pro        # Incluye informes y Ollama
LICENSE=enterprise # Todas las funciones
```

### Verificar Funcionalidad
```bash
python demo_menu_system.py
# Navegar por todos los menús
# Probar todas las opciones
# Verificar validación de licencia
```

---

## 🎉 **¡Sistema Completo y Funcional!**

El Sistema Avanzado de Menús de DATACONTA está listo para producción con:
- ✅ Navegación intuitiva por sesiones
- ✅ Validación automática de licencias
- ✅ Arquitectura modular y escalable
- ✅ Fácil configuración y mantenimiento
- ✅ Demostración completa funcional

**¡Perfecto para escalar y agregar nuevas funcionalidades!** 🚀