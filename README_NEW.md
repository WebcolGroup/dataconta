# 🚀 DATACONTA - Sistema Avanzado de Gestión Empresarial

**DATACONTA** es un sistema avanzado de gestión empresarial que integra con la API de Siigo para proporcionar funcionalidades completas de Business Intelligence, exportación de datos y análisis financiero.

## ✨ Características Principales

### 🎨 **Interfaz Dual**
- **🖥️ Interfaz Gráfica Moderna**: GUI moderna con PySide6
- **💻 Interfaz de Consola**: CLI tradicional para uso en servidor

### 📊 **Business Intelligence**
- Exportación de datos dimensionales (clientes, productos, vendedores, fechas)
- Generación de tablas de hechos para análisis
- Reportes financieros detallados

### 📈 **Gestión de Facturas**
- Exportación masiva a JSON y CSV
- Integración completa con API de Siigo
- Análisis de datos transaccionales

### 🛠️ **Herramientas Avanzadas**
- Validación de licencias
- Análisis de arquitectura del proyecto
- Logging detallado de operaciones

## 🏗️ Arquitectura

### **Arquitectura Hexagonal** 
```
📁 Domain Layer (Reglas de Negocio)
├── 🔌 Interfaces UI
├── 📦 DTOs
└── 🏢 Entidades de Negocio

📁 Application Layer (Casos de Uso)
├── ⚙️ Servicios de Aplicación
└── 🎯 Casos de Uso

📁 Infrastructure Layer (Detalles Técnicos)
├── 🌐 Adaptadores de API
├── 💾 Adaptadores de Almacenamiento
└── 📄 Adaptadores de Archivos

📁 UI Layer (Presentación)
├── 🎨 Componentes PySide6
└── 🔗 Adaptadores UI
```

### **Principios SOLID** ✅
- **S**ingle Responsibility: Cada clase tiene una responsabilidad específica
- **O**pen/Closed: Extensible sin modificar código existente
- **L**iskov Substitution: Implementaciones intercambiables
- **I**nterface Segregation: Interfaces específicas y cohesivas
- **D**ependency Inversion: Dependencias invertidas correctamente

## 🚀 Instalación y Configuración

### Requisitos
```bash
Python 3.8+
PySide6 (para interfaz gráfica)
requests
python-dotenv
```

### 1. Clonar repositorio
```bash
git clone <repository-url>
cd dataconta
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# API Configuration
SIIGO_USERNAME=tu_usuario
SIIGO_ACCESS_KEY=tu_access_key
SIIGO_BASE_URL=https://api.siigo.com
SIIGO_PARTNER_ID=tu_partner_id

# Application Configuration  
DEBUG=True
LOG_LEVEL=INFO
```

## ▶️ Uso de la Aplicación

### 🎨 **Interfaz Gráfica (Recomendada)**
```bash
python main_gui.py
```

**Características de la GUI:**
- ✅ Interfaz moderna e intuitiva
- ✅ Botones organizados por categorías
- ✅ Panel de información en tiempo real
- ✅ Barras de progreso para operaciones largas
- ✅ Sistema de notificaciones integrado
- ✅ Logs de operaciones visibles

### 💻 **Interfaz de Consola**
```bash
python main_hexagonal.py
```

**Para sistemas sin interfaz gráfica o uso en servidor.**

## 📋 Funcionalidades Disponibles

### 📊 **Business Intelligence**
- **Exportar Datos BI**: Genera archivos CSV dimensionales
- **Reporte Financiero**: Análisis financiero con recomendaciones

### 📈 **Informes y Exportación**
- **Exportar Facturas JSON**: Descarga en formato JSON
- **Exportar Facturas CSV**: Genera archivos CSV para análisis

### 🛠️ **Herramientas**
- **Validar Licencia**: Verificación de estado de licencia
- **Análisis de Estructura**: Validación de arquitectura del proyecto

## 📁 Estructura del Proyecto

```
dataconta/
├── 🚀 main_gui.py                     # Punto de entrada GUI
├── 💻 main_hexagonal.py               # Punto de entrada consola
├── 🧪 validate_migration.py           # Script de validación
├── 📋 requirements.txt                # Dependencias
├── 📚 README.md                       # Documentación principal
├── 📖 MIGRACION_GUI_COMPLETADA.md     # Documentación de migración
├── 
├── 📁 src/
│   ├── 📁 domain/                     # Capa de Dominio
│   │   ├── 📁 interfaces/             # Interfaces abstractas
│   │   │   └── 🔌 ui_interfaces.py    # Contratos de UI
│   │   ├── 📁 dtos/                   # Objetos de transferencia
│   │   │   └── 📦 ui_dtos.py          # DTOs para UI
│   │   └── 📁 entities/               # Entidades de negocio
│   │
│   ├── 📁 application/                # Capa de Aplicación
│   │   ├── 📁 use_cases/              # Casos de uso
│   │   └── 📁 services/               # Servicios de aplicación
│   │
│   ├── 📁 infrastructure/             # Capa de Infraestructura
│   │   ├── 📁 adapters/               # Adaptadores externos
│   │   ├── 📁 config/                 # Configuración
│   │   └── 📁 utils/                  # Utilidades
│   │
│   ├── 📁 ui/                         # Capa de UI (Nueva)
│   │   ├── 📁 components/             # Componentes PySide6
│   │   │   └── 🎨 main_window.py      # Ventana principal
│   │   └── 📁 adapters/               # Adaptadores UI
│   │       └── 🔗 ui_adapters.py      # Conexión UI-Negocio
│   │
│   └── 📁 presentation/               # Interfaz de consola
│       └── 💻 cli_interface.py        # CLI original
│
├── 📁 outputs/                        # Archivos generados
│   └── 📁 bi/                         # Datos Business Intelligence
│
└── 📁 tests/                          # Tests del proyecto
```

## 🎯 Casos de Uso Principales

### 1. **Exportación Business Intelligence**
```python
# La aplicación genera automáticamente:
outputs/bi/dim_clients.csv      # Dimensión clientes
outputs/bi/dim_products.csv     # Dimensión productos  
outputs/bi/dim_sellers.csv      # Dimensión vendedores
outputs/bi/dim_dates.csv        # Dimensión fechas
outputs/bi/fact_invoices.csv    # Tabla de hechos facturas
```

### 2. **Análisis Financiero**
- Reportes mensuales, trimestrales y anuales
- Métricas de rendimiento
- Recomendaciones automatizadas

### 3. **Gestión de Datos**
- Exportación masiva de facturas
- Transformación de datos para análisis
- Integración con herramientas BI externas

## 🧪 Testing y Validación

### Ejecutar validación completa:
```bash
python validate_migration.py
```

**Valida:**
- ✅ Integridad de arquitectura hexagonal
- ✅ Aplicación correcta de principios SOLID  
- ✅ Preservación de funcionalidad original
- ✅ Configuración correcta de GUI
- ✅ Documentación completa

## 🔧 Desarrollo y Contribución

### Principios de Desarrollo
1. **Arquitectura Hexagonal**: Mantener separación de responsabilidades
2. **SOLID**: Aplicar principios en todos los componentes nuevos
3. **Bajo Acoplamiento**: Usar interfaces y inyección de dependencias
4. **Alta Cohesión**: Funcionalidades relacionadas en mismos módulos

### Agregar Nuevas Funcionalidades
1. Definir interfaces en `src/domain/interfaces/`
2. Crear DTOs en `src/domain/dtos/`  
3. Implementar casos de uso en `src/application/`
4. Crear adaptadores en `src/infrastructure/`
5. Agregar componentes UI en `src/ui/`

## 📞 Soporte y Contacto

Para soporte técnico o consultas sobre el proyecto, consulte:
- 📖 Documentación técnica en `/docs`
- 📋 Issues del proyecto
- 📚 Documentación de migración: `MIGRACION_GUI_COMPLETADA.md`

---

## 🏆 Estado del Proyecto

**✅ MIGRACIÓN GUI COMPLETADA**
- **Arquitectura**: Hexagonal ✓
- **Principios**: SOLID ✓  
- **UI Framework**: PySide6 ✓
- **Funcionalidad**: 100% Preservada ✓
- **Testing**: Validado ✓
- **Documentación**: Completa ✓

**🚀 DATACONTA está listo para el futuro con una interfaz moderna respaldada por una arquitectura sólida.**