# Changelog

Todas las versiones importantes de este proyecto serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Añadido
- Sistema completo de pruebas unitarias e integración
- Workflow de CI/CD con GitHub Actions
- Configuración de calidad de código (black, flake8, mypy, pylint)
- Sistema de loading mejorado con overlay visual
- Soporte para múltiples formatos de exportación

### Cambiado
- Arquitectura refactorizada siguiendo principios hexagonales
- Interfaz de usuario con PySide6 modernizada
- Sistema de configuración centralizado

### Arreglado
- Problemas de concurrencia en cálculos de KPI
- Manejo de errores mejorado en exportaciones
- Optimización de rendimiento en datasets grandes

## [v1.0.0-free] - 2025-09-20

### Añadido
- **Versión FREE inicial** con funcionalidades básicas
- **Cálculo de KPIs financieros** desde API de Siigo
  - Ventas totales y número de facturas
  - Ticket promedio y participación de impuestos
  - Top 5 clientes y productos
  - Evolución de ventas y estados de facturas
- **Sistema de exportación** a CSV y Excel
  - Filtros por fecha y estado
  - Transformación de datos para análisis
  - Validación de integridad de datos
- **Interfaz gráfica moderna** con PySide6
  - Dashboard interactivo de KPIs
  - Widgets especializados por funcionalidad
  - Sistema de menús dinámico
  - Loading overlay para procesos largos
- **Arquitectura hexagonal** con separación de capas
  - Domain layer con entidades y reglas de negocio
  - Application layer con casos de uso
  - Infrastructure layer con adaptadores
  - Presentation layer con controladores UI
- **Sistema de logging** estructurado
  - Logs por niveles (INFO, WARNING, ERROR)
  - Rotación automática de archivos de log
  - Integración con interfaz gráfica
- **Gestión de configuración** centralizada
  - Archivo de configuración JSON
  - Variables de entorno
  - Configuración de API externa
- **Sistema de addons** extensible
  - Manifest para definición de addons
  - Carga dinámica de extensiones
  - Integración con menú principal

### Limitaciones de la versión FREE
- **Límite de facturas**: Procesa hasta 10,000 facturas por consulta
- **Retención de datos**: KPIs guardados por 30 días
- **Formatos de exportación**: Solo CSV y Excel básico
- **Usuarios concurrentes**: Máximo 1 usuario
- **Soporte técnico**: Comunidad únicamente
- **Integraciones**: Solo API de Siigo

### Requisitos técnicos
- Python 3.9+
- PySide6 6.9.2+
- Pandas 2.3.2+
- Conexión a internet para API de Siigo
- Windows 10/11, macOS 10.15+, Ubuntu 20.04+

### Instalación
```bash
# Clonar repositorio
git clone https://github.com/WebcolGroup/dataconta.git
cd dataconta

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python dataconta.py
```

### Configuración inicial
1. Obtener credenciales de API de Siigo
2. Configurar variables de entorno en `.env`
3. Ejecutar primer cálculo de KPIs
4. Configurar exportaciones según necesidades

---

## Tipos de cambios
- `Añadido` para nuevas funcionalidades
- `Cambiado` para cambios en funcionalidades existentes
- `Obsoleto` para funcionalidades que serán removidas
- `Removido` para funcionalidades removidas
- `Arreglado` para corrección de bugs
- `Seguridad` para vulnerabilidades
