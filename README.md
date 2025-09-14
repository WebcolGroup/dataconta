# DataConta - Integración Avanzada con API de Siigo

**DataConta** es una aplicación profesional de línea de comandos (CLI) desarrollada en Python para integrar con la API de Siigo, implementando **Arquitectura Hexagonal** completa con capacidades avanzadas de exportación y Business Intelligence.

## 🎯 Características Principales

### ✨ **Funcionalidades Actuales (Septiembre 2025)**
- 📋 **Consulta de Facturas**: Obtención de facturas de venta con filtros avanzados
- 📤 **Exportación CSV**: Exportación directa de facturas a formato CSV normalizado
- 🏢 **Business Intelligence**: Generación de modelo estrella para Power BI
- 🔍 **Verificación API**: Monitoreo del estado y conectividad de la API
- 📁 **Gestión de Archivos**: Visualización y administración de archivos generados
- 🔐 **Validación de Licencias**: Sistema robusto de autenticación y autorización
- 📊 **Logging Avanzado**: Sistema completo de registro de actividades

### 🏗️ **Arquitectura Hexagonal Implementada**

DataConta utiliza una **Arquitectura Hexagonal** (Clean Architecture) completa:

```
📂 src/
├── 🎯 domain/                    # Dominio - Lógica de Negocio Pura
│   ├── entities/                # Entidades: Invoice, Cliente, Vendedor, etc.
│   └── services/                # Servicios de dominio
├── 🔄 application/              # Aplicación - Casos de Uso
│   ├── ports/interfaces.py     # Puertos (abstracciones)
│   ├── services/                # Servicios de aplicación
│   │   ├── InvoiceExportService.py
│   │   └── BIExportService.py
│   └── use_cases/               # Casos de uso
│       └── invoice_use_cases.py
├── 🔌 infrastructure/           # Infraestructura - Adaptadores
│   ├── adapters/               # Adaptadores para servicios externos
│   │   ├── siigo_api_adapter.py
│   │   ├── license_validator_adapter.py
│   │   ├── file_storage_adapter.py
│   │   └── csv_file_adapter.py
│   ├── config/                 # Configuración
│   └── utils/                  # Utilidades
├── 🖥️ presentation/            # Presentación - Interfaz CLI
│   └── cli_interface.py
└── 📋 tests/                   # Tests unitarios
```

## 🚀 Módulos Implementados

### 1. **📋 Módulo de Consulta de Facturas**
- Filtros por fecha de creación (rango)
- Filtros por ID de documento específico
- Paginación automática para grandes volúmenes
- Guardado automático en formato JSON con timestamp

### 2. **📤 Módulo de Exportación CSV**
- Transformación de facturas a formato CSV estructurado
- Normalización de datos con combinación producto-pago
- Campos calculados automáticamente (subtotales, impuestos)
- Validación de estructura de datos
- Configuración de registros máximos

### 3. **🏢 Módulo Business Intelligence (BI)**
**Nuevo - Implementado Septiembre 2025**

Genera un **modelo estrella completo** optimizado para Power BI:

#### **📊 Tablas Generadas:**
- **fact_invoices.csv**: Tabla de hechos principal
  - Métricas: cantidades, precios, descuentos, totales
  - Claves foráneas a todas las dimensiones
  - 202 registros procesados (ejemplo actual)

- **dim_clients.csv**: Dimensión de clientes
  - Información completa del cliente
  - Tipo de cliente (Persona Natural/Jurídica)
  - Régimen fiscal extraído inteligentemente

- **dim_sellers.csv**: Dimensión de vendedores
  - Datos completos de vendedores
  - Identificación y información de contacto

- **dim_products.csv**: Dimensión de productos
  - Catálogo completo de productos
  - Códigos, descripciones y categorías

- **dim_payments.csv**: Dimensión de métodos de pago
  - Métodos de pago normalizados
  - Referencias y valores

- **dim_dates.csv**: Dimensión temporal
  - Fechas formateadas para análisis temporal
  - Compatible con filtros de Power BI

#### **🧠 Características Inteligentes del BI:**
- **Extracción Automática de Reglas de Negocio**: Identifica tipo de cliente y régimen fiscal desde observaciones
- **Deduplicación Inteligente**: Elimina duplicados manteniendo integridad referencial
- **Generación de Claves Únicas**: Claves consistentes para todas las dimensiones
- **Validación de Esquema**: Verificación automática de la estructura generada
- **Estadísticas de Procesamiento**: Métricas detalladas de la exportación

### 4. **🔐 Módulo de Seguridad y Validación**
- Validación de licencias online/offline
- Autenticación segura con tokens JWT
- Manejo robusto de credenciales
- Configuración por variables de entorno

### 5. **📊 Módulo de Logging y Monitoreo**
- Niveles de log configurables (INFO, WARNING, ERROR)
- Registro tanto en consola como en archivo
- Tracking detallado de operaciones
- Métricas de rendimiento

## 💻 Menú Interactivo Actual

```
🏢 DATACONTA - SIIGO API
==================================================
1. 📋 Consultar Facturas de Venta
2. 🔍 Verificar Estado de la API  
3. 📁 Ver Archivos de Salida
4. 📤 Exportar Facturas a CSV
5. 🏢 Exportar a Business Intelligence  ⭐ NUEVO
0. 🚪 Salir
==================================================
```

## 📊 Capacidades de Exportación Actuales

### **Exportación Simple CSV**
- Facturas normalizadas en formato tabular
- Combinaciones producto-pago por fila
- Campos calculados automáticamente
- Configuración de límites de registros

### **Exportación Business Intelligence** ⭐
- **Modelo estrella completo** para análisis avanzado
- **6 archivos CSV** interconectados
- Optimizado para **Power BI**, **Tableau**, **Excel**
- **Métricas de procesamiento** en tiempo real
- **Validación automática** del esquema generado

### **Formatos de Salida Disponibles**
```
📂 outputs/
├── 📄 invoices_*.json              # Respuestas brutas de API
├── 📊 invoices_export_*.csv        # Exportación simple CSV
└── 📁 bi/                          # Modelo estrella BI
    ├── fact_invoices.csv          # Tabla de hechos principal
    ├── dim_clients.csv            # Dimensión clientes
    ├── dim_sellers.csv            # Dimensión vendedores  
    ├── dim_products.csv           # Dimensión productos
    ├── dim_payments.csv           # Dimensión métodos pago
    └── dim_dates.csv              # Dimensión temporal
```

## 🔧 Instalación y Configuración

### **Prerrequisitos**
- Python 3.7+ (Testado en Python 3.13.4)
- pip (gestor de paquetes)
- Acceso a API de Siigo

### **Instalación Rápida**
```bash
# 1. Clonar repositorio
git clone <url-repositorio>
cd dataconta

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.template .env
# Editar .env con sus credenciales
```

### **Configuración .env**
```env
# API de Siigo
SIIGO_API_URL=https://api.siigo.com
SIIGO_USERNAME=su_usuario_siigo
SIIGO_ACCESS_KEY=su_clave_acceso

# Validación de Licencia  
LICENSE_URL=https://servidor-licencias.com/validate
LICENSE_KEY=XXXX-XXXX-XXXX-XXXX

# Logging (Opcional)
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## 🏃‍♂️ Uso de la Aplicación

### **Ejecutar DataConta**
```bash
python main_hexagonal.py
```

### **Flujo de Trabajo Típico**

1. **🔍 Verificar Estado API** (Opción 2)
   - Confirma conectividad con Siigo
   - Valida credenciales y licencia

2. **📋 Consultar Facturas** (Opción 1)
   - Aplica filtros según necesidad
   - Visualiza resultados en consola
   - Datos guardados automáticamente

3. **🏢 Exportar a BI** (Opción 5) ⭐
   - Configura parámetros de exportación
   - Procesa facturas a modelo estrella
   - Genera 6 archivos CSV listos para análisis

4. **📁 Ver Archivos** (Opción 3)
   - Lista todos los archivos generados
   - Muestra tamaños y fechas de modificación

## 📈 Estadísticas de Rendimiento Actual

**Ejemplo de Procesamiento BI (Septiembre 2025)**:
- ✅ **202 facturas** procesadas exitosamente
- 📊 **6 tablas** del modelo estrella generadas
- 👥 **1 cliente único** identificado
- 🏪 **1 vendedor único** procesado
- 📦 **60+ productos únicos** catalogados
- 💳 **1 método de pago** normalizado
- 📅 **Múltiples fechas** en dimensión temporal

## 🛠️ Desarrollo y Arquitectura

### **Principios SOLID Aplicados**
- ✅ **S**ingle Responsibility: Cada clase una responsabilidad
- ✅ **O**pen/Closed: Extensible sin modificar código existente
- ✅ **L**iskov Substitution: Implementaciones intercambiables
- ✅ **I**nterface Segregation: Interfaces específicas y cohesivas
- ✅ **D**ependency Inversion: Inyección de dependencias

### **Mejores Prácticas Implementadas**
- ✅ **Type Hints** completos en todo el código
- ✅ **Docstrings** para funciones y clases
- ✅ **Manejo robusto de excepciones**
- ✅ **Logging estructurado** y consistente
- ✅ **Separación clara de responsabilidades**
- ✅ **Configuración por variables de entorno**
- ✅ **Validación exhaustiva de datos**
- ✅ **Código limpio y mantenible**

### **Testing**
```bash
# Ejecutar tests unitarios
pytest tests/

# Test específico del módulo BI
pytest tests/test_bi_export.py
```

## 📊 Integración con Herramientas BI

### **Power BI** (Recomendado)
1. Importar archivos CSV desde `outputs/bi/`
2. Establecer relaciones automáticamente por claves foráneas
3. Crear visualizaciones sobre el modelo estrella

### **Excel/Tableau**
1. Cargar archivos CSV individuales
2. Establecer relaciones manualmente si es necesario
3. Aprovechar la estructura normalizada para análisis

## 🚨 Solución de Problemas

### **Error de Autenticación**
```
❌ Error: Authentication failed
```
- Verificar `SIIGO_USERNAME` y `SIIGO_ACCESS_KEY`
- Confirmar conectividad con API de Siigo

### **Error de Validación de Licencia**
```  
❌ Error: License validation failed
```
- Verificar `LICENSE_URL` y `LICENSE_KEY`
- Confirmar conectividad a internet

### **Problemas en Exportación BI**
```
❌ Error: BI export failed
```
- Revisar logs en `app.log` para detalles
- Verificar permisos de escritura en carpeta `outputs/`
- Confirmar que hay facturas disponibles para procesar

## 📄 API de Siigo Utilizada

**Endpoints Principales**:
- `POST /auth` - Autenticación
- `GET /v1/invoices` - Consulta de facturas  
- `GET /v1/users/current` - Verificación de estado

**Documentación**: [API Siigo Official](https://api.siigo.com/docs)

## 📝 Registro de Cambios

### **v2.0.0 - Septiembre 2025** ⭐
- ✅ **NUEVO**: Módulo completo de Business Intelligence
- ✅ **NUEVO**: Generación de modelo estrella para Power BI
- ✅ **NUEVO**: 6 tablas CSV interconectadas (fact + dimensions)
- ✅ **NUEVO**: Extracción inteligente de reglas de negocio
- ✅ **NUEVO**: Validación automática de esquemas
- ✅ **NUEVO**: Estadísticas detalladas de procesamiento
- ✅ **MEJORA**: Interfaz CLI actualizada con opción BI
- ✅ **MEJORA**: Tests unitarios para módulo BI

### **v1.0.0 - Versiones Anteriores**
- ✅ Funcionalidades básicas de consulta
- ✅ Exportación simple CSV  
- ✅ Validación de licencias
- ✅ Arquitectura hexagonal base

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama feature: `git checkout -b feature/Nueva-Funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/Nueva-Funcionalidad`  
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver `LICENSE` para más detalles.

---

**📧 Contacto**: Desarrollado con ❤️ siguiendo principios SOLID y arquitectura limpia

**📍 Estado Actual**: ✅ **Completamente funcional** con capacidades avanzadas de BI

**🔄 Última Actualización**: Septiembre 14, 2025