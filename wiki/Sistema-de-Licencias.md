# 🎫 Sistema de Licencias - DataConta

DataConta incluye un **sistema completo de licencias de 3 niveles** adaptado a diferentes necesidades empresariales con control automático de acceso y funcionalidades.

## 🏆 Comparación de Licencias

| Funcionalidad | 🆓 FREE | 💼 PROFESSIONAL | 🏢 ENTERPRISE |
|---------------|---------|------------------|---------------|
| **Interfaz CLI** | ✅ Completa | ✅ Completa | ✅ Completa |
| **Interfaz GUI** | ❌ No | ✅ Completa | ✅ Completa |
| **Facturas por consulta** | 500 | 2,000 | ♾️ Ilimitadas |
| **Exportación CSV** | ✅ Básica | ✅ Avanzada | ✅ Completa |
| **Business Intelligence** | ❌ No | ✅ Limitado (1K registros) | ✅ Completo |
| **Informes Financieros** | ❌ No | ✅ Básicos | ✅ Avanzados |
| **Dashboard Visual** | ❌ No | ✅ Completo | ✅ Completo + |
| **Sistema de Addons** | ❌ No | ✅ Limitado | ✅ Completo |
| **Soporte** | Comunidad | Email | Prioritario |
| **Precio** | Gratuito | $49/mes | $199/mes |

## 🆓 FREE - Versión Gratuita

### ✅ **Incluye:**
- **Interfaz CLI completa** para automatización
- **Hasta 500 facturas** por consulta
- **Exportación básica CSV** con datos reales
- **Verificación de API Siigo** y conectividad
- **Gestión básica de archivos** generados
- **Logging completo** de operaciones

### ❌ **No Incluye:**
- Interfaz gráfica (GUI)
- Business Intelligence Export
- Informes financieros automatizados
- Dashboard visual con KPIs
- Sistema de addons

### 🎯 **Ideal Para:**
- Desarrolladores individuales
- Pruebas y validación de concepto
- Scripts de automatización básicos
- Integración con sistemas externos via CLI

## 💼 PROFESSIONAL - Licencia Profesional

### ✅ **Todo lo de FREE +**
- **Interfaz GUI completa** con PySide6
- **Hasta 2,000 facturas** por consulta
- **Business Intelligence limitado** (1,000 registros)
- **Informes financieros básicos** (Estado de Resultados, Balance)
- **Dashboard integrado** con KPIs en tiempo real
- **Sistema de menús dinámico** configurable
- **Sistema de addons limitado**

### 🏢 **Funcionalidades Empresariales:**
- **Menús contextuales** profesionales con iconos
- **Validación visual** de licencia en tiempo real
- **Navegación intuitiva** con restricciones automáticas
- **Recarga dinámica** de configuraciones
- **Logging avanzado** con métricas de rendimiento

### 🎯 **Ideal Para:**
- Pequeñas y medianas empresas
- Consultores financieros independientes
- Equipos de contabilidad con necesidades gráficas
- Análisis financiero profesional

## 🏢 ENTERPRISE - Licencia Empresarial

### ✅ **Todo lo de PROFESSIONAL +**
- **Facturas ilimitadas** sin restricciones de cantidad
- **BI Export completo** sin límites de registros
- **Informes financieros avanzados** con personalización
- **Sistema de addons completo** para extensibilidad
- **Soporte prioritario** con SLA garantizado
- **API REST integrada** para integraciones (próximamente)
- **Soporte multi-usuario** (próximamente)

### 🚀 **Características Avanzadas:**
- **Sincronización en tiempo real** con múltiples fuentes
- **Configuraciones empresariales** centralizadas
- **Monitoreo y alertas** automáticas
- **Integración con sistemas ERP** existentes
- **Dashboards personalizables** por usuario/rol
- **Auditoria completa** de operaciones

### 🎯 **Ideal Para:**
- Grandes empresas con múltiples sucursales
- Firmas de consultoría con múltiples clientes
- Organizaciones con necesidades de integración complejas
- Equipos que requieren extensibilidad avanzada

## ⚙️ Configuración de Licencias

### 📋 **Variables de Entorno**

```env
# En archivo .env

# === CONFIGURACIÓN DE LICENCIA ===
LICENSE_TYPE=PROFESSIONAL      # FREE, PROFESSIONAL, ENTERPRISE
LICENSE_KEY=PROF-2024-TEST-DEMO-001A

# === VALIDACIÓN ONLINE (Opcional) ===
LICENSE_URL=https://api.dataconta.com/validate
LICENSE_CACHE_HOURS=24

# === CONFIGURACIÓN OFFLINE ===
LICENSE_OFFLINE_MODE=false     # true para modo sin internet
```

### 🔧 **Configuración Avanzada**

```env
# === LÍMITES PERSONALIZADOS (Solo ENTERPRISE) ===
MAX_INVOICES_CUSTOM=50000
BI_EXPORT_LIMIT_CUSTOM=100000
PARALLEL_REQUESTS_CUSTOM=20

# === FUNCIONALIDADES ESPECÍFICAS ===
ENABLE_GUI=true               # false para CLI-only
ENABLE_ADDONS=true            # false para deshabilitar addons
ENABLE_REAL_TIME_SYNC=false   # true solo en ENTERPRISE
```

## 🔍 Verificación de Licencia

### ⌨️ **Desde CLI**
```bash
python main_hexagonal.py
# Seleccionar: "8. 🎫 Información de Licencia"
```

**Salida ejemplo:**
```
📄 INFORMACIÓN DE LICENCIA
════════════════════════════════════════════════
🎫 Tipo de Licencia: PROFESSIONAL
🔑 Clave: PROF-2024-TEST-DEMO-001A
📊 Límite de Facturas: 2,000
🏢️ Acceso GUI: ✅ Habilitado
📈 Informes Financieros: ✅ Habilitado  
🔍 Business Intelligence: ✅ Limitado (1,000 registros)
🔌 Sistema de Addons: ✅ Limitado
⏰ Válida hasta: 2025-12-31
════════════════════════════════════════════════
```

### 🖥️ **Desde GUI**
- **Indicador visual** en la barra superior verde
- **Status en tiempo real** del estado de licencia
- **Alertas automáticas** al acercarse a límites

### 🐍 **Programáticamente**
```python
from src.application.services.license_manager import LicenseManager

# Verificar licencia actual
license_manager = LicenseManager()
info = license_manager.get_license_info()

print(f"Tipo: {info.license_type}")
print(f"Válida: {info.is_valid}")
print(f"Límite facturas: {info.invoice_limit}")
```

## 🎯 Control de Acceso Automático

### 🔒 **Restricciones por Licencia**

#### **FREE:**
```python
# Automáticamente aplicado
if license.is_free():
    max_invoices = 500
    gui_enabled = False
    bi_export_enabled = False
    financial_reports_enabled = False
```

#### **PROFESSIONAL:**
```python
if license.is_professional():
    max_invoices = 2000
    gui_enabled = True
    bi_export_enabled = True
    bi_export_limit = 1000
    financial_reports_enabled = True
```

#### **ENTERPRISE:**
```python
if license.is_enterprise():
    max_invoices = None  # Sin límites
    gui_enabled = True
    bi_export_enabled = True
    bi_export_limit = None  # Sin límites
    financial_reports_enabled = True
    advanced_features_enabled = True
```

### ⚠️ **Manejo de Límites**
```python
# Ejemplo de validación automática
def export_invoices(self, count: int):
    if count > self.license_manager.get_invoice_limit():
        raise LicenseError(
            f"Límite excedido. Licencia {self.license_type} "
            f"permite máximo {self.get_invoice_limit()} facturas"
        )
    
    # Proceder con exportación
    return self.do_export(count)
```

## 🛒 Adquisición y Upgrades

### 💳 **Cómo Obtener Licencias**

#### **FREE → PROFESSIONAL**
1. Contactar: sales@dataconta.com
2. Recibir `LICENSE_KEY` personalizada
3. Actualizar `.env` con nueva configuración
4. Reiniciar aplicación

#### **PROFESSIONAL → ENTERPRISE**
1. Solicitar upgrade vía email
2. Configuración empresarial personalizada
3. Migración asistida de datos existentes
4. Training para usuarios avanzados

### 🔄 **Proceso de Upgrade**
```bash
# 1. Actualizar configuración
nano .env
# LICENSE_TYPE=ENTERPRISE
# LICENSE_KEY=ENT-2024-COMPANY-XXX

# 2. Verificar upgrade
python -c "
from src.application.services.license_manager import LicenseManager
lm = LicenseManager()
print(f'Nueva licencia: {lm.get_license_info().license_type}')
"

# 3. Reiniciar aplicación
python dataconta.py
```

### ⏰ **Renovaciones**
- **FREE**: Sin vencimiento
- **PROFESSIONAL**: Renovación anual automática
- **ENTERPRISE**: Contratos personalizados (1-3 años)

## 🚨 Troubleshooting de Licencias

### ❌ **Error: License validation failed**
```
ERROR: Unable to validate license
```

**Soluciones:**
1. **Verificar conectividad**: `ping api.dataconta.com`
2. **Modo offline**: `LICENSE_OFFLINE_MODE=true`
3. **Cache corrupto**: Eliminar `.license_cache`
4. **Contactar soporte**: support@dataconta.com

### ⚠️ **Warning: License expiring soon**
```
WARNING: License expires in 7 days
```

**Acciones:**
1. **Renovación automática** habilitada (PROFESSIONAL+)
2. **Contactar ventas** para extensión manual
3. **Backup de datos** antes del vencimiento

### 🔒 **Error: Feature not available in current license**
```
ERROR: GUI requires PROFESSIONAL+ license
```

**Solución:**
- **Upgrade de licencia** o **usar CLI** disponible en FREE

### 📊 **Límites alcanzados**
```
WARNING: Approaching invoice limit (1800/2000)
```

**Opciones:**
1. **Upgrade a ENTERPRISE** para límites ilimitados
2. **Optimizar consultas** para usar menos facturas
3. **Procesar en lotes** múltiples consultas pequeñas

## 🎁 Modo Demo y Trial

### 🧪 **Modo Demo**
```env
# Configuración de demo (30 días)
LICENSE_TYPE=PROFESSIONAL
LICENSE_KEY=DEMO-TRIAL-30DAYS
LICENSE_DEMO_MODE=true
```

### ⏰ **Trial ENTERPRISE (7 días)**
- **Funcionalidades completas** por tiempo limitado
- **Sin límites** durante el período de prueba
- **Migración automática** a FREE al vencer (con aviso)

### 📧 **Solicitar Trial**
Email: trials@dataconta.com con:
- Nombre de empresa
- Casos de uso esperados
- Volumen estimado de datos

---

El sistema de licencias de DataConta está diseñado para crecer con sus necesidades empresariales, ofreciendo una experiencia fluida desde desarrollo individual hasta implementaciones empresariales a gran escala.