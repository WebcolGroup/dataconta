# 🎛️ Guía de Uso - DataConta

Tutorial completo para usar todas las funcionalidades de DataConta, desde las básicas hasta las más avanzadas.

## 🚀 Primeros Pasos

### **1. Verificar Instalación**
```bash
# Verificar que DataConta está funcionando
python dataconta.py --version

# Verificar conexión API Siigo
python main_hexagonal.py
# Seleccionar: "2. 🔍 Verificar Estado de la API"
```

### **2. Configurar Credenciales**
Asegúrate de tener configurado tu archivo `.env` con las credenciales de Siigo:

```env
SIIGO_API_URL=https://api.siigo.com
SIIGO_USERNAME=tu_usuario@empresa.com
SIIGO_ACCESS_KEY=tu_clave_de_acceso
LICENSE_TYPE=FREE
```

## 💻 Usando las Interfaces

### 🖥️ **Interfaz Gráfica (GUI) - PROFESSIONAL+**

#### **Iniciar la GUI**
```bash
python dataconta.py
```

#### **Navegación Principal**
La GUI se organiza en menús horizontales dinámicos:

- **🏠 Inicio**: Dashboard principal con KPIs
- **📊 Reportes**: Generación de informes financieros
- **🔧 Herramientas**: Utilidades y configuración
- **❓ Ayuda**: Documentación y soporte

#### **Dashboard Principal**
- **KPIs en Tiempo Real**: Métricas actualizadas automáticamente
- **Botones de Acción Rápida**: Acceso directo a funciones comunes
- **Indicador de Licencia**: Estado y límites visibles en todo momento

#### **Generar Informes**
1. **Click en menú "📊 Reportes"**
2. **Seleccionar tipo de informe**:
   - Estado de Resultados
   - Estado de Situación Financiera
   - Exportación BI
3. **Configurar parámetros** (fechas, filtros)
4. **Generar y descargar**

### ⌨️ **Interfaz CLI (Todas las Licencias)**

#### **Iniciar CLI**
```bash
python main_hexagonal.py
```

#### **Menú Principal**
```
🏢 DATACONTA - SIIGO API
==================================================
📄 Licencia Activa: PROFESSIONAL (2000 facturas máximo)
==================================================

1. 📋 Consultar Facturas de Venta ✅
2. 🔍 Verificar Estado de la API ✅
3. 📁 Ver Archivos de Salida ✅
4. 📤 Exportar Facturas a CSV ✅
5. 🏢 Exportar a Business Intelligence ✅ (PROFESSIONAL+)
6. 📊 Estado de Resultados ✅ (PROFESSIONAL+)
7. ⚖️ Estado de Situación Financiera ✅ (PROFESSIONAL+)
8. 🎫 Información de Licencia ✅
0. 🚪 Salir
```

## 📋 Funcionalidades Principales

### **1. Consultar Facturas de Venta**

#### **GUI**
1. Ir a menú **"🔧 Herramientas"** → **"Consulta de Facturas"**
2. Configurar filtros opcionales
3. Ejecutar consulta
4. Ver resultados en tabla

#### **CLI**
1. Seleccionar opción **"1. 📋 Consultar Facturas de Venta"**
2. Configurar filtros:
   - Fecha inicio/fin
   - ID específico de documento
   - Estado de factura
3. Procesar y ver resultados

**Límites por Licencia:**
- **FREE**: 500 facturas máximo
- **PROFESSIONAL**: 2,000 facturas máximo
- **ENTERPRISE**: Sin límites

### **2. Exportación de Datos**

#### **CSV Simple**
- **Disponible**: Todas las licencias
- **Formato**: Tabular normalizado
- **Uso**: Análisis básico en Excel

```bash
# CLI - Opción 4
4. 📤 Exportar Facturas a CSV

# Archivos generados:
outputs/facturas_export_YYYYMMDD_HHMMSS.csv
```

#### **Business Intelligence Export**
- **Disponible**: PROFESSIONAL+ (con límites)
- **Formato**: Modelo estrella (6 tablas CSV)
- **Uso**: Power BI, Tableau, análisis avanzado

```bash
# CLI - Opción 5
5. 🏢 Exportar a Business Intelligence

# Archivos generados:
outputs/bi/fact_invoices.csv       # Tabla de hechos
outputs/bi/dim_clients.csv         # Dimensión clientes
outputs/bi/dim_sellers.csv         # Dimensión vendedores
outputs/bi/dim_products.csv        # Dimensión productos
outputs/bi/dim_payments.csv        # Dimensión pagos
outputs/bi/dim_dates.csv           # Dimensión temporal
```

### **3. Informes Financieros Automatizados**

#### **Estado de Resultados**
- **Disponible**: PROFESSIONAL+
- **Contenido**: Ingresos, gastos, utilidad neta
- **Formato**: CSV contable estándar

#### **Estado de Situación Financiera**
- **Disponible**: PROFESSIONAL+
- **Contenido**: Activos, pasivos, patrimonio
- **Validación**: Verificación automática de ecuación contable

```bash
# CLI
6. 📊 Estado de Resultados
7. ⚖️ Estado de Situación Financiera

# Archivos generados:
outputs/financial_reports/estado_resultados_PERIODO_FECHA.csv
outputs/financial_reports/balance_general_FECHA.csv
```

## 🎛️ Configuración Avanzada

### **Personalizar Menús GUI**

Editar `menu_config.json`:
```json
{
  "horizontal_menu": {
    "mi_menu_personalizado": {
      "label": "Mi Menú",
      "icon": "🆕",
      "enabled": true,
      "license_required": "PROFESSIONAL",
      "submenu": [
        {
          "label": "Mi Función",
          "action": "mi_accion_personalizada"
        }
      ]
    }
  }
}
```

### **Configurar Límites de Rendimiento**

En archivo `.env`:
```env
# Configuración de rendimiento
MAX_INVOICES_PER_QUERY=1000
CACHE_EXPIRATION_HOURS=24
REQUEST_TIMEOUT_SECONDS=30
PARALLEL_REQUESTS=5
```

### **Logging Detallado**

```env
LOG_LEVEL=DEBUG
LOG_FILE=app.log
LOG_MAX_SIZE_MB=100
```

Ver logs en tiempo real:
```bash
tail -f app.log
```

## 📊 Casos de Uso Prácticos

### **Caso 1: Análisis Mensual de Ventas**

```bash
# 1. Obtener facturas del mes actual
python main_hexagonal.py
# Opción 1: Consultar facturas
# Filtrar por fecha: 2024-12-01 a 2024-12-31

# 2. Exportar a CSV para análisis
# Opción 4: Exportar CSV

# 3. Generar estado de resultados
# Opción 6: Estado de Resultados

# Resultado: 3 archivos listos para contabilidad
```

### **Caso 2: Dashboard Ejecutivo**

```bash
# GUI Mode
python dataconta.py

# 1. Ver KPIs actualizados en dashboard
# 2. Click "Actualizar con Datos Reales"
# 3. Analizar TOP clientes
# 4. Exportar datos para presentación
```

### **Caso 3: Integración con Power BI**

```bash
# 1. Exportar modelo BI
python main_hexagonal.py
# Opción 5: Exportar a Business Intelligence

# 2. En Power BI:
# - Importar archivos CSV desde outputs/bi/
# - Las relaciones se crean automáticamente
# - Crear dashboard con métricas
```

## 🔧 Mantenimiento y Optimización

### **Limpieza de Archivos**
```bash
# Limpiar archivos antiguos (>30 días)
find outputs/ -name "*.csv" -mtime +30 -delete

# Windows PowerShell
Get-ChildItem outputs\ -Recurse -Filter "*.csv" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

### **Backup de Configuración**
```bash
# Backup de archivos importantes
cp .env .env.backup
cp menu_config.json menu_config.backup.json
tar -czf dataconta_backup.tar.gz .env menu_config.json outputs/
```

### **Actualización de Dependencias**
```bash
# Verificar actualizaciones disponibles
pip list --outdated

# Actualizar todas las dependencias
pip install -r requirements.txt --upgrade
```

## 🚨 Troubleshooting Rápido

### **La aplicación no inicia**
```bash
# 1. Verificar Python y dependencias
python --version
pip install -r requirements.txt

# 2. Verificar configuración
cat .env | grep SIIGO

# 3. Probar conexión
python -c "import requests; print('OK' if requests.get('https://api.siigo.com').status_code == 200 else 'ERROR')"
```

### **GUI no funciona**
```bash
# Instalar/actualizar PySide6
pip install --upgrade PySide6

# Usar CLI como alternativa
python main_hexagonal.py
```

### **Error de autenticación**
1. Verificar credenciales en `.env`
2. Confirmar conectividad: `ping api.siigo.com`
3. Revisar logs: `tail app.log`

---

¡Con esta guía ya puedes usar todas las funcionalidades de DataConta! Para dudas específicas, consulta el [Troubleshooting](Troubleshooting) o crea un [Issue en GitHub](https://github.com/WebcolGroup/dataconta/issues).