# 📥 Instalación - DataConta

Guía completa de instalación de DataConta en diferentes sistemas operativos.

## 📋 Prerrequisitos

### 🐍 **Python**
- **Versión requerida**: Python 3.7+ (Recomendado: 3.11+)
- **Verificar instalación**: 
  ```bash
  python --version
  # o
  python3 --version
  ```

### 📦 **Gestor de Paquetes**
- **pip** debe estar instalado y actualizado
- **Verificar**: 
  ```bash
  pip --version
  ```
- **Actualizar pip**: 
  ```bash
  python -m pip install --upgrade pip
  ```

### 🌐 **Conectividad**
- Acceso a internet para descargar dependencias
- Acceso a **API de Siigo** (credenciales válidas)
- Puertos de red disponibles para requests HTTPS

### 💻 **Requisitos del Sistema**

#### **Windows**
- Windows 10 o superior
- PowerShell 5.1+ o Command Prompt
- 4GB RAM mínimo (8GB recomendado)

#### **macOS**
- macOS 10.14 Mojave o superior
- Terminal o iTerm2
- 4GB RAM mínimo (8GB recomendado)

#### **Linux**
- Ubuntu 18.04+, CentOS 7+, o distribución equivalente
- Bash shell
- 2GB RAM mínimo (4GB recomendado)

## 🚀 Instalación Paso a Paso

### 📥 **Paso 1: Obtener el Código**

#### **Desde GitHub**
```bash
git clone <url-repositorio>
cd dataconta
```

#### **Descarga Directa**
1. Descargar ZIP desde GitHub
2. Extraer archivo
3. Abrir terminal en la carpeta extraída

### 🐍 **Paso 2: Configurar Entorno Virtual (Recomendado)**

#### **Windows**
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
.venv\Scripts\activate

# Verificar activación
where python
```

#### **macOS/Linux**
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate

# Verificar activación
which python
```

### 📦 **Paso 3: Instalar Dependencias**

#### **Instalación Básica**
```bash
pip install -r requirements.txt
```

#### **Instalación para Desarrollo**
```bash
pip install -r requirements-dev.txt
```

#### **Instalación Manual (si falla requirements.txt)**
```bash
# Dependencias core
pip install requests>=2.31.0
pip install python-dotenv>=1.0.0
pip install pandas>=2.0.0

# Interfaz gráfica
pip install PySide6>=6.7.0

# Exportación Excel
pip install openpyxl>=3.1.0
```

### ⚙️ **Paso 4: Configurar Variables de Entorno**

#### **Crear archivo .env**
```bash
# Copiar plantilla
cp .env.template .env

# Windows
copy .env.template .env
```

#### **Configurar credenciales**
Editar `.env` con sus datos:
```env
# === API DE SIIGO ===
SIIGO_API_URL=https://api.siigo.com
SIIGO_USERNAME=su_usuario@empresa.com
SIIGO_ACCESS_KEY=su_clave_de_acceso

# === SISTEMA DE LICENCIAS ===
LICENSE_TYPE=FREE              # FREE, PROFESSIONAL, ENTERPRISE
LICENSE_KEY=                   # Opcional para FREE

# === CONFIGURACIÓN DE LA APLICACIÓN ===
APP_NAME=DataConta
APP_VERSION=3.0.0
ENVIRONMENT=production

# === LOGGING ===
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### 🧪 **Paso 5: Verificar Instalación**

#### **Test Básico**
```bash
python -c "
import sys
print(f'✅ Python: {sys.version}')

try:
    import requests, dotenv, pandas
    print('✅ Dependencias core: OK')
except ImportError as e:
    print(f'❌ Error core: {e}')

try:
    import PySide6
    print('✅ PySide6 (GUI): OK')
except ImportError:
    print('⚠️  PySide6 no disponible (solo CLI)')
"
```

#### **Test de Conectividad**
```bash
python -c "
from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('SIIGO_USERNAME')
access_key = os.getenv('SIIGO_ACCESS_KEY')

if username and access_key:
    adapter = SiigoAPIAdapter(username, access_key)
    if adapter.test_connection():
        print('✅ Conexión API Siigo: OK')
    else:
        print('❌ Error conexión API Siigo')
else:
    print('⚠️  Credenciales no configuradas')
"
```

## 🚦 Primer Uso

### 🖥️ **Interfaz Gráfica (PROFESSIONAL+)**
```bash
python dataconta.py
```
- La ventana se abrirá maximizada automáticamente
- Status de licencia visible en la barra superior
- Menús dinámicos según tipo de licencia

### ⌨️ **Interfaz CLI (Todas las licencias)**
```bash
python main_hexagonal.py
```
- Menú interactivo con opciones según licencia
- Validación automática de permisos
- Funciones adaptadas a límites de licencia

### 🔍 **Verificar Estado**
1. **Verificar API Siigo** (opción 2 en CLI)
2. **Consultar algunas facturas** (opción 1 en CLI)
3. **Ver información de licencia** (opción 8 en CLI)

## ❗ Solución de Problemas Comunes

### 🐍 **Error: Python no encontrado**
```
'python' no se reconoce como comando
```
**Solución Windows:**
1. Instalar Python desde [python.org](https://python.org)
2. ✅ Marcar "Add Python to PATH" durante instalación
3. Reiniciar terminal

**Solución macOS:**
```bash
# Instalar con Homebrew
brew install python3

# O usar python3 en lugar de python
python3 --version
```

### 📦 **Error: pip no encontrado**
```
'pip' no se reconoce como comando
```
**Solución:**
```bash
# Reinstalar pip
python -m ensurepip --upgrade

# O usar módulo pip
python -m pip --version
```

### 🖥️ **Error: PySide6 no se instala**
```
ERROR: Failed building wheel for PySide6
```
**Soluciones:**
```bash
# Opción 1: Actualizar pip y setuptools
python -m pip install --upgrade pip setuptools wheel

# Opción 2: Versión específica
pip install PySide6==6.7.0

# Opción 3: Pre-compiled wheel
pip install --only-binary=all PySide6

# Opción 4: Usar conda (si disponible)
conda install -c conda-forge pyside6
```

### 🌐 **Error: No se conecta a API Siigo**
```
ERROR: Authentication failed with Siigo API
```
**Verificaciones:**
1. **Credenciales correctas** en `.env`
2. **Conectividad internet**: `ping api.siigo.com`
3. **Firewall/Proxy**: Permitir conexiones HTTPS
4. **Revisar logs**: `cat app.log | tail -20`

### 🔐 **Error: Variables de entorno no se cargan**
```
SIIGO_USERNAME not found
```
**Solución:**
1. Verificar que `.env` existe en la raíz del proyecto
2. Sin espacios alrededor del `=`: `VARIABLE=valor`
3. Sin comillas dobles innecesarias
4. Archivo con encoding UTF-8

### 💾 **Error: Permisos de archivos**
```
PermissionError: Cannot write to outputs/
```
**Solución:**
```bash
# Linux/macOS
chmod -R 755 outputs/

# Windows (como administrador)
icacls outputs /grant Everyone:F
```

## 🔧 Instalación Avanzada

### 🐳 **Con Docker (Próximamente)**
```bash
# Construir imagen
docker build -t dataconta .

# Ejecutar contenedor
docker run -it dataconta
```

### 🏢 **Instalación Empresarial**

#### **Para Múltiples Usuarios**
```bash
# Instalación sistema
pip install -r requirements.txt --system

# Configuración compartida
sudo mkdir /etc/dataconta
sudo cp .env.template /etc/dataconta/
```

#### **Como Servicio (Linux)**
```bash
# Crear usuario servicio
sudo useradd -r -s /bin/false dataconta

# Configurar systemd
sudo cp dataconta.service /etc/systemd/system/
sudo systemctl enable dataconta
sudo systemctl start dataconta
```

## 📊 Verificación de Rendimiento

### 🚀 **Benchmark Post-Instalación**
```bash
python -c "
import time
from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter

# Test de rendimiento
start = time.time()
# Simular carga típica
end = time.time()

print(f'⚡ Tiempo de carga: {end-start:.2f}s')
print('✅ Instalación optimizada' if end-start < 5 else '⚠️  Revisar rendimiento')
"
```

### 📈 **Monitoreo de Recursos**
```bash
# Durante ejecución
python -c "
import psutil
import os

process = psutil.Process(os.getpid())
print(f'💾 RAM: {process.memory_info().rss / 1024 / 1024:.1f} MB')
print(f'💻 CPU: {process.cpu_percent()}%')
"
```

---

¡Instalación completada! Continúa con la [🎛️ Guía de Uso](Guia-de-Uso) para comenzar a usar DataConta.