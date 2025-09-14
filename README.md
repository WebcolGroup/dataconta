# DataConta - Integración con API Siigo

**DataConta** es una aplicación de línea de comandos (CLI) desarrollada en Python para integrar con la API de Siigo, implementando **Arquitectura Hexagonal** y siguiendo principios SOLID y mejores prácticas de código limpio.

## 🏗️ Arquitectura Hexagonal

DataConta está diseñada con **Arquitectura Hexagonal** (Ports & Adapters) que proporciona:

- **🎯 Domain Layer**: Lógica de negocio pura (Entidades: Invoice, Customer, etc.)
- **🔄 Application Layer**: Casos de uso y puertos/interfaces
- **🔌 Infrastructure Layer**: Adaptadores para servicios externos (Siigo API, File Storage, etc.)
- **🖥️ Presentation Layer**: Interfaz CLI para usuario
- **⚙️ Configuration**: Gestión de variables de entorno y configuración

## 🚀 Características

- ✅ **Arquitectura Hexagonal** completa con separación de capas
- 🔑 Validación de licencias online/offline
- 📋 Consulta de facturas de venta con filtros avanzados
- 🔍 Verificación del estado de la API
- 💾 Guardado automático de respuestas en JSON con timestamps
- 📝 Sistema de logging completo con diferentes niveles
- 🔐 Integración segura con credenciales de Siigo
- 🛠️ Manejo robusto de errores
- 🔐 Autenticación segura con tokens
- 📁 Gestión de archivos de salida

## 📋 Prerrequisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd proyectia
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar las variables de entorno**
   ```bash
   # Copiar el archivo de plantilla
   copy .env.template .env
   
   # Editar .env con tus credenciales reales
   ```

## ⚙️ Configuración

Edita el archivo `.env` con tus credenciales:

```env
# Configuración de la API de Siigo
SIIGO_API_URL=https://api.siigo.com
SIIGO_USERNAME=tu_usuario_siigo
SIIGO_ACCESS_KEY=tu_clave_de_acceso_siigo

# Configuración de validación de licencia
LICENSE_URL=https://tu-servidor-de-licencias.com/validate
LICENSE_KEY=XXXX-XXXX-XXXX-XXXX

# Opcional: Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## 🏃‍♂️ Uso

### Ejecutar DataConta

```bash
python main_hexagonal.py
```

### Menú principal

DataConta presenta un menú interactivo con las siguientes opciones:

```
🏢 SIIGO API - MENÚ PRINCIPAL
==================================================
1. 📋 Consultar Facturas de Venta
2. 🔍 Verificar Estado de la API
3. 📁 Ver Archivos de Salida
0. 🚪 Salir
==================================================
```

### Funcionalidades

#### 1. Consultar Facturas de Venta
- Obtiene facturas de venta desde la API de Siigo
- Permite filtrar por ID de documento y rangos de fechas
- Guarda automáticamente los resultados en `outputs/`

#### 2. Verificar Estado de la API
- Verifica la conectividad con la API de Siigo
- Muestra el estado de autenticación

#### 3. Ver Archivos de Salida
- Lista todos los archivos guardados en la carpeta `outputs/`
- Muestra información sobre tamaño y tipo de archivo

## 📁 Estructura de Archivos

```
proyectia/
├── .github/
│   └── copilot-instructions.md
├── outputs/                    # Respuestas de la API (generado automáticamente)
├── main.py                     # Punto de entrada
├── cli_menu.py                 # Interfaz CLI
├── siigo_client.py            # Cliente de la API de Siigo
├── license_validator.py       # Validador de licencias
├── requirements.txt           # Dependencias de Python
├── .env.template             # Plantilla de configuración
├── .env                      # Configuración (crear desde template)
├── app.log                   # Archivo de logs (generado automáticamente)
└── README.md                 # Este archivo
```

## 🔒 Validación de Licencias

DataConta incluye un sistema de validación de licencias que:

- Valida la licencia contra un servidor remoto
- Incluye modo offline para casos de conectividad limitada
- Maneja errores de red de manera robusta
- Proporciona información detallada sobre el estado de la licencia

## 📊 Logging

DataConta genera logs detallados que incluyen:

- **INFO**: Operaciones normales y flujo de DataConta
- **WARNING**: Situaciones que requieren atención pero no impiden la operación
- **ERROR**: Errores que pueden afectar la funcionalidad

Los logs se escriben tanto en la consola como en el archivo `app.log`.

## 🛠️ Desarrollo

### Principios SOLID Aplicados

- **S** - Single Responsibility: Cada clase tiene una responsabilidad específica
- **O** - Open/Closed: Extensible sin modificar el código existente
- **L** - Liskov Substitution: Las implementaciones pueden intercambiarse
- **I** - Interface Segregation: Interfaces específicas y cohesivas
- **D** - Dependency Inversion: Dependencias se inyectan, no se crean internamente

### Mejores Prácticas Implementadas

- ✅ Type hints en todo el código
- ✅ Docstrings para todas las funciones y clases
- ✅ Manejo robusto de excepciones
- ✅ Logging estructurado y consistente
- ✅ Separación de responsabilidades
- ✅ Configuración mediante variables de entorno
- ✅ Validación de datos de entrada
- ✅ Código limpio y legible

### Testing (Opcional)

Para ejecutar tests (si están disponibles):

```bash
pytest
```

### Formateo de código

```bash
# Formatear código
black .

# Verificar estilo
flake8 .

# Verificación de tipos
mypy .
```

## 🚨 Solución de Problemas

### Error de autenticación
- Verifica que `SIIGO_USERNAME` y `SIIGO_ACCESS_KEY` sean correctos
- Confirma que la URL de la API sea válida

### Error de validación de licencia
- Verifica que `LICENSE_URL` y `LICENSE_KEY` sean correctos
- Confirma conectividad a internet
- En caso de problemas, la aplicación intentará validación offline

### Problemas de conectividad
- Verifica tu conexión a internet
- Confirma que no hay firewalls bloqueando las conexiones
- Revisa los logs en `app.log` para más detalles

## 📝 API de Siigo

Esta aplicación utiliza los siguientes endpoints de la API de Siigo:

- `POST /auth` - Autenticación
- `GET /v1/invoices` - Consulta de facturas
- `GET /v1/users/current` - Verificación de estado

Para más información sobre la API de Siigo, consulta la [documentación oficial](https://api.siigo.com/docs).

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## ✨ Versión

**Versión Actual**: 1.0.0

### Historial de Cambios

- **v1.0.0**: Versión inicial con funcionalidades básicas de consulta de facturas y validación de licencias

---

**Desarrollado con ❤️ siguiendo principios SOLID y mejores prácticas de Python**