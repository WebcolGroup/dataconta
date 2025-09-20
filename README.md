# 📊 DataConta - Sistema de Gestión Financiera

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-orange.svg)](../../wiki/Arquitectura)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**DataConta** es un sistema profesional de gestión financiera desarrollado en Python que implementa **Arquitectura Hexagonal** completa. Ofrece integración directa con la **API de Siigo** para obtener datos reales de facturación, con capacidades avanzadas de análisis, exportación y generación de reportes financieros automatizados.

## 🚀 Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone <url-repositorio>
cd dataconta

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.template .env
# Editar .env con sus credenciales de Siigo
```

## 💻 Uso

### 🖥️ Interfaz Gráfica (PROFESSIONAL+)
```bash
python dataconta.py
```

### ⌨️ Interfaz CLI (Todas las licencias)
```bash
python main_hexagonal.py
```

## 🎫 Sistema de Licencias

DataConta incluye **3 niveles de licencia** adaptados a diferentes necesidades:

- **🆓 FREE**: CLI básica, hasta 500 facturas, exportación CSV
- **💼 PROFESSIONAL**: GUI completa, hasta 2,000 facturas, informes financieros, BI limitado
- **🏢 ENTERPRISE**: Sin límites, todas las funciones, soporte prioritario

> Ver [**📋 Configuración de Licencias**](../../wiki/Sistema-de-Licencias) para más detalles.

## ✨ Características Principales

- 🌐 **Integración API Siigo**: Conexión directa para datos reales
- 📊 **Dashboard KPIs**: Métricas empresariales en tiempo real
- 🏆 **Análisis Top Clientes**: Consolidación automática por NIT
- 📤 **Exportación Múltiple**: CSV, Excel, Business Intelligence
- 🔍 **Consulta de Facturas**: Filtros avanzados y búsqueda personalizada
- 📈 **Informes Financieros**: Estado de Resultados y Balance General automatizados
- 🖥️ **Interfaz Dual**: GUI moderna (PySide6) y CLI completa
- 🔌 **Sistema de Addons**: Extensibilidad para la comunidad

## 🏗️ Arquitectura

DataConta implementa **Arquitectura Hexagonal** (Clean Architecture) con principios **SOLID** para máxima mantenibilidad y extensibilidad.

```
src/
├── domain/          # Lógica de negocio pura
├── application/     # Casos de uso y servicios
├── infrastructure/  # Adaptadores externos (Siigo API, Base de datos, etc.)
└── presentation/    # Interfaces (CLI, GUI)
```

> Ver [**🏗️ Documentación de Arquitectura**](../../wiki/Arquitectura) para detalles completos.

## 📊 Ejemplo de Análisis

```
🏆 TOP 3 CLIENTES:
🥇 webcol                    | $37,128,000 (19.1%)
🥈 Cliente NIT: 66716838     | $19,316,080 (9.9%)
🥉 Cliente NIT: 21334607     | $18,802,000 (9.7%)

📈 ESTADÍSTICAS:
💰 Ventas totales: $194,559,393
📄 Total facturas: 61
📊 Top 3 representa: 38.7% del total
```

## 📖 Documentación Completa

- [📥 **Instalación Detallada**](../../wiki/Instalacion)
- [🎛️ **Guía de Uso**](../../wiki/Guia-de-Uso)
- [🔧 **Configuración**](../../wiki/Configuracion)
- [🏗️ **Arquitectura y Desarrollo**](../../wiki/Arquitectura)
- [🔌 **Sistema de Addons**](../../wiki/Sistema-de-Addons)
- [📊 **Business Intelligence**](../../wiki/Business-Intelligence)
- [📈 **Informes Financieros**](../../wiki/Informes-Financieros)
- [🔍 **API Reference**](../../wiki/API-Reference)
- [🚨 **Solución de Problemas**](../../wiki/Troubleshooting)

## 🤝 Contribución

1. **Fork** del repositorio
2. **Crear rama**: `git checkout -b feature/nueva-funcionalidad`
3. **Implementar** siguiendo [convenciones de código](../../wiki/Desarrollo#convenciones)
4. **Agregar tests** unitarios
5. **Pull Request** con descripción detallada

> Ver [**🔧 Guía de Desarrollo**](../../wiki/Desarrollo) para información completa.

## 📄 Licencia

Este proyecto está licenciado bajo **MIT License**. Ver [LICENSE](LICENSE) para detalles.

## 📞 Soporte

- 📖 **Documentación**: [GitHub Wiki](../../wiki)
- 🐛 **Reportar Issues**: [GitHub Issues](../../issues)
- 💬 **Discusiones**: [GitHub Discussions](../../discussions)
- 📧 **Contacto**: WebcolGroup

---

**🎯 DataConta** - Gestión financiera moderna con arquitectura limpia  
*Desarrollado con ❤️ siguiendo principios SOLID y mejores prácticas de software*

📊 Dashboard • 🔌 API Integration • 🏗️ Clean Architecture • 📈 Real-time KPIs