# 🚨 Troubleshooting - DataConta

Guía completa para solucionar problemas comunes en DataConta. Soluciones organizadas por categorías y síntomas.

## 🔍 Diagnóstico Rápido

### **✅ Verificación de Sistema**
```bash
# 1. Verificar Python
python --version
# Debe mostrar: Python 3.7+ 

# 2. Verificar dependencias críticas
python -c "
try:
    import requests, dotenv, pandas, PySide6
    print('✅ Todas las dependencias OK')
except ImportError as e:
    print(f'❌ Dependencia faltante: {e}')
"

# 3. Verificar estructura de archivos
ls -la src/ outputs/ .env
```

### **🌐 Test de Conectividad**
```bash
# Ping a Siigo API
ping api.siigo.com

# Test HTTP
curl -I https://api.siigo.com
# Debe retornar: HTTP/2 200
```

## 🐛 Problemas de Instalación

### **❌ Error: Python no encontrado**
```
'python' no se reconoce como comando
```

**💡 Soluciones:**

**Windows:**
```bash
# Descargar e instalar Python desde python.org
# ✅ Marcar "Add Python to PATH" durante instalación
# Reiniciar terminal
python --version
```

**macOS:**
```bash
# Con Homebrew
brew install python3

# Usar python3 explícitamente
python3 --version
alias python=python3
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### **❌ Error: pip no encontrado**
```
'pip' no se reconoce como comando
```

**💡 Soluciones:**
```bash
# Reinstalar pip
python -m ensurepip --upgrade

# Usar módulo pip directamente
python -m pip --version

# Linux: instalar pip
sudo apt install python3-pip
```

### **❌ Error: PySide6 no se instala**
```
ERROR: Failed building wheel for PySide6
```

**💡 Soluciones por prioridad:**
```bash
# 1. Actualizar herramientas base
python -m pip install --upgrade pip setuptools wheel

# 2. Instalar versión específica
pip install PySide6==6.7.0

# 3. Usar binarios precompilados
pip install --only-binary=all PySide6

# 4. Limpiar cache y reinstalar
pip cache purge
pip install --no-cache-dir PySide6

# 5. Alternativa con conda
conda install -c conda-forge pyside6
```

### **❌ Error: Dependencias conflictivas**
```
ERROR: pip's dependency resolver does not currently consider all the ways that packages can depend on each other
```

**💡 Solución:**
```bash
# Crear entorno virtual limpio
python -m venv .venv-clean
source .venv-clean/bin/activate  # Linux/macOS
.venv-clean\Scripts\activate     # Windows

# Instalar paso a paso
pip install --upgrade pip
pip install -r requirements.txt
```

## 🖥️ Problemas de Interfaz Gráfica

### **❌ GUI no se abre**
```
ModuleNotFoundError: No module named 'PySide6'
```

**💡 Solución Inmediata:**
```bash
# Usar CLI como alternativa
python main_hexagonal.py

# Instalar PySide6 en paralelo
pip install PySide6>=6.7.0
```

### **❌ Ventana aparece en blanco**
```
GUI se abre pero sin contenido visible
```

**💡 Soluciones:**
```bash
# 1. Verificar logs
tail -f app.log

# 2. Modo debug
python dataconta.py --debug

# 3. Reiniciar configuración GUI
rm -f .gui_config.json
python dataconta.py

# 4. Verificar temas
pip install --upgrade qt-material
```

### **❌ Error: Menu config not found**
```
ERROR: Could not load menu configuration
```

**💡 Solución:**
```bash
# Crear configuración por defecto
cp menu_config_extended.json menu_config.json

# Verificar formato JSON
python -m json.tool menu_config.json

# Resetear a configuración base
git checkout menu_config.json
```

### **❌ Fonts/iconos no se ven correctamente**

**💡 Soluciones:**
```bash
# Windows: Instalar fuentes emoji
# Descargar e instalar: Segoe UI Emoji, Twemoji

# Linux: Instalar fuentes
sudo apt install fonts-noto-color-emoji

# macOS: Actualizar sistema
sudo softwareupdate -i -a
```

## 🌐 Problemas de API/Conectividad

### **❌ Error: Authentication failed**
```
ERROR: Authentication failed with Siigo API
```

**💡 Diagnóstico paso a paso:**

1. **Verificar credenciales:**
```bash
grep SIIGO .env
# Debe mostrar:
# SIIGO_USERNAME=tu_usuario@empresa.com
# SIIGO_ACCESS_KEY=tu_clave
```

2. **Test de conectividad:**
```bash
# Ping básico
ping api.siigo.com

# Test HTTPS
curl -v https://api.siigo.com
```

3. **Verificar formato de credenciales:**
```bash
# Credenciales no deben tener espacios ni comillas extra
# ❌ Incorrecto: SIIGO_USERNAME="usuario@email.com"  
# ✅ Correcto: SIIGO_USERNAME=usuario@email.com
```

4. **Test de autenticación manual:**
```bash
python -c "
from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter
import os
from dotenv import load_dotenv

load_dotenv()
adapter = SiigoAPIAdapter(
    os.getenv('SIIGO_USERNAME'), 
    os.getenv('SIIGO_ACCESS_KEY')
)
print('✅ Auth OK' if adapter.test_connection() else '❌ Auth FAILED')
"
```

### **❌ Error: Connection timeout**
```
requests.exceptions.ConnectTimeout: HTTPSConnectionPool
```

**💡 Soluciones:**
```bash
# 1. Verificar firewall/proxy
# Permitir conexiones HTTPS a api.siigo.com

# 2. Aumentar timeout en .env
REQUEST_TIMEOUT_SECONDS=60

# 3. Test de proxy
python -c "
import requests
proxies = {'https': 'http://proxy:port'}  # Si usas proxy
response = requests.get('https://api.siigo.com', proxies=proxies)
print(f'Status: {response.status_code}')
"
```

### **❌ Error: SSL Certificate verification failed**
```
requests.exceptions.SSLError: HTTPSConnectionPool
```

**💡 Soluciones:**
```bash
# 1. Actualizar certificados (Linux)
sudo apt update && sudo apt install ca-certificates

# 2. Actualizar requests
pip install --upgrade requests certifi

# 3. Verificar fecha/hora del sistema
date

# 4. Test sin verificación SSL (solo debug)
python -c "
import requests
import urllib3
urllib3.disable_warnings()
response = requests.get('https://api.siigo.com', verify=False)
print(f'Status: {response.status_code}')
"
```

## 📊 Problemas de Licencias

### **❌ License validation failed**
```
ERROR: Unable to validate license
```

**💡 Soluciones:**

1. **Verificar configuración:**
```bash
grep LICENSE .env
# Debe mostrar:
# LICENSE_TYPE=PROFESSIONAL
# LICENSE_KEY=PROF-2024-XXX
```

2. **Modo offline:**
```bash
# En .env agregar:
LICENSE_OFFLINE_MODE=true
```

3. **Limpiar cache de licencia:**
```bash
rm -f .license_cache
python main_hexagonal.py
```

### **❌ Feature not available in current license**
```
ERROR: GUI requires PROFESSIONAL+ license
```

**💡 Soluciones:**
```bash
# 1. Verificar licencia actual
python main_hexagonal.py
# Opción 8: Información de Licencia

# 2. Usar funcionalidades disponibles
# FREE: CLI únicamente
# PROFESSIONAL+: GUI completa

# 3. Upgrade de licencia
# Contactar: sales@dataconta.com
```

### **❌ Límites de licencia alcanzados**
```
WARNING: Invoice limit exceeded (2000/2000)
```

**💡 Soluciones:**
```bash
# 1. Optimizar consultas
# Usar filtros por fecha más específicos

# 2. Procesar en lotes
# Dividir consultas grandes en varias pequeñas

# 3. Upgrade a ENTERPRISE
# Sin límites en facturas
```

## 🗄️ Problemas de Archivos/Datos

### **❌ PermissionError: Cannot write to outputs/**
```
PermissionError: [Errno 13] Permission denied: 'outputs/'
```

**💡 Soluciones:**
```bash
# Linux/macOS
chmod -R 755 outputs/
sudo chown -R $USER outputs/

# Windows (como administrador)
icacls outputs /grant Everyone:(F)

# Crear directorio si no existe
mkdir -p outputs/{bi,financial_reports,kpis}
```

### **❌ No se pueden cargar KPIs existentes**
```
WARNING: Could not load existing KPIs
```

**💡 Soluciones:**
```bash
# 1. Verificar archivos KPIs
ls -la outputs/kpis/

# 2. Validar formato JSON
python -m json.tool outputs/kpis/kpis_*.json

# 3. Regenerar KPIs
python main_hexagonal.py
# Opción 1: Consultar facturas (genera KPIs nuevos)

# 4. Limpiar archivos corruptos
rm -f outputs/kpis/*.json
```

### **❌ Error en exportación BI**
```
ERROR: BI export failed with validation error
```

**💡 Diagnóstico:**
```bash
# 1. Verificar logs detallados
tail -100 app.log | grep -i "bi export"

# 2. Test de memoria disponible
python -c "
import psutil
mem = psutil.virtual_memory()
print(f'RAM disponible: {mem.available // (1024**3)} GB')
print('✅ Suficiente RAM' if mem.available > 1024**3 else '⚠️ RAM baja')
"

# 3. Reducir dataset
# Usar filtros por fecha más específicos
# Procesar menos facturas por vez
```

## ⚡ Problemas de Rendimiento

### **⚠️ La aplicación está muy lenta**

**💡 Optimizaciones:**

1. **Verificar recursos del sistema:**
```bash
# CPU y RAM
top -p $(pgrep -f dataconta)

# Windows
tasklist /fi "imagename eq python.exe"
```

2. **Optimizar configuración:**
```env
# En .env
MAX_INVOICES_PER_QUERY=500
PARALLEL_REQUESTS=3
CACHE_EXPIRATION_HOURS=1
```

3. **Limpiar archivos temporales:**
```bash
# Limpiar cache Python
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Limpiar archivos antiguos
find outputs/ -name "*.csv" -mtime +7 -delete
```

### **⚠️ Memory leak / Uso excesivo de RAM**

**💡 Soluciones:**
```bash
# 1. Reiniciar aplicación periódicamente
# 2. Procesar datos en lotes más pequeños
# 3. Limpiar variables grandes

python -c "
import gc
gc.collect()  # Forzar recolección de basura
"
```

## 🔧 Diagnóstico Avanzado

### **📋 Script de Diagnóstico Completo**

<function_calls>
<invoke name="create_file">
<parameter name="content">#!/usr/bin/env python3
"""
DataConta - Script de Diagnóstico Completo
Ejecutar cuando tengas problemas para obtener información detallada del sistema.
"""

import sys
import os
import platform
import subprocess
import importlib
from pathlib import Path

def run_diagnostics():
    print("🔍 DATACONTA - DIAGNÓSTICO DEL SISTEMA")
    print("=" * 50)
    
    # Sistema operativo
    print(f"🖥️ SO: {platform.system()} {platform.release()}")
    print(f"📊 Arquitectura: {platform.architecture()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Directorio de trabajo: {os.getcwd()}")
    print()
    
    # Dependencias críticas
    print("📦 VERIFICACIÓN DE DEPENDENCIAS:")
    critical_deps = [
        "requests", "dotenv", "pandas", "PySide6", 
        "openpyxl", "json", "datetime"
    ]
    
    for dep in critical_deps:
        try:
            mod = importlib.import_module(dep)
            version = getattr(mod, '__version__', 'N/A')
            print(f"✅ {dep}: {version}")
        except ImportError:
            print(f"❌ {dep}: NO INSTALADO")
    print()
    
    # Archivos críticos
    print("📁 VERIFICACIÓN DE ARCHIVOS:")
    critical_files = [
        ".env", "requirements.txt", "dataconta.py", 
        "main_hexagonal.py", "menu_config.json"
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file}: {size} bytes")
        else:
            print(f"❌ {file}: NO ENCONTRADO")
    print()
    
    # Directorios
    print("📂 VERIFICACIÓN DE DIRECTORIOS:")
    dirs = ["src", "outputs", "outputs/bi", "outputs/kpis"]
    for dir_path in dirs:
        if os.path.exists(dir_path):
            files = len(list(Path(dir_path).glob("*")))
            print(f"✅ {dir_path}: {files} archivos")
        else:
            print(f"❌ {dir_path}: NO EXISTE")
    print()
    
    # Variables de entorno
    print("🔧 VERIFICACIÓN DE CONFIGURACIÓN:")
    env_vars = [
        "SIIGO_API_URL", "SIIGO_USERNAME", "SIIGO_ACCESS_KEY",
        "LICENSE_TYPE", "LOG_LEVEL"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Ocultar credenciales sensibles
            if "ACCESS_KEY" in var or "USERNAME" in var:
                masked = value[:4] + "*" * (len(value) - 8) + value[-4:]
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: NO CONFIGURADO")
    print()
    
    # Test de conectividad
    print("🌐 TEST DE CONECTIVIDAD:")
    try:
        import requests
        response = requests.get("https://api.siigo.com", timeout=5)
        print(f"✅ API Siigo: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ API Siigo: {str(e)}")
    print()
    
    # Espacio en disco
    print("💾 INFORMACIÓN DEL SISTEMA:")
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        print(f"📊 Disco Total: {total // (1024**3)} GB")
        print(f"📊 Disco Usado: {used // (1024**3)} GB") 
        print(f"📊 Disco Libre: {free // (1024**3)} GB")
        
        if free < 1024**3:  # Menos de 1GB
            print("⚠️ ADVERTENCIA: Espacio en disco bajo")
    except:
        print("⚠️ No se pudo obtener información del disco")
    print()
    
    # Procesos Python activos
    print("🔄 PROCESOS PYTHON ACTIVOS:")
    try:
        import psutil
        python_procs = [p for p in psutil.process_iter() 
                       if 'python' in p.name().lower()]
        for proc in python_procs[:5]:  # Top 5
            try:
                print(f"📊 PID {proc.pid}: {proc.name()} - {proc.memory_info().rss // 1024**2} MB")
            except:
                continue
    except ImportError:
        print("⚠️ psutil no disponible")
    
    print("\n" + "=" * 50)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("📧 Si el problema persiste, envía esta información a soporte.")

if __name__ == "__main__":
    run_diagnostics()