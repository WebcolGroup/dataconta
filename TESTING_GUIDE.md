# 🧪 Testing Guide - DataConta FREE

Esta guía explica cómo ejecutar y desarrollar pruebas para DataConta FREE.

## 📋 Configuración de Pruebas

### Estructura de Pruebas

```
tests/
├── __init__.py
├── conftest.py                 # Configuración global y fixtures
├── pytest.ini                 # Configuración de pytest
├── unit/                       # Pruebas unitarias
│   ├── test_kpi_service.py    # Pruebas de cálculo de KPIs
│   ├── test_export_service.py # Pruebas de exportación
│   └── test_free_limits.py    # Pruebas de límites FREE
└── integration/                # Pruebas de integración
    └── test_system_integration.py
```

### Dependencias de Pruebas

```bash
# Instalar dependencias de testing
pip install pytest pytest-cov pytest-mock pytest-xdist

# Para análisis de código
pip install black flake8 mypy isort pylint

# Para seguridad
pip install bandit safety
```

## 🚀 Ejecutar Pruebas

### Comandos Básicos

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=src --cov-report=html

# Ejecutar solo pruebas unitarias
pytest tests/unit/

# Ejecutar solo pruebas de integración
pytest tests/integration/

# Ejecutar pruebas específicas por marcadores
pytest -m unit          # Solo pruebas unitarias
pytest -m kpi           # Solo pruebas de KPI
pytest -m export        # Solo pruebas de exportación
pytest -m free_limit    # Solo pruebas de límites FREE
pytest -m "not slow"    # Excluir pruebas lentas
```

### Ejecución Paralela

```bash
# Ejecutar pruebas en paralelo (más rápido)
pytest -n auto

# Ejecutar en 4 procesos
pytest -n 4
```

### Modo Verbose

```bash
# Ver detalles de cada prueba
pytest -v

# Ver output completo (incluyendo prints)
pytest -s
```

## 📊 Cobertura de Código

### Generar Reportes de Cobertura

```bash
# Reporte en terminal
pytest --cov=src --cov-report=term-missing

# Reporte HTML (navegable)
pytest --cov=src --cov-report=html
# Abrir htmlcov/index.html en el navegador

# Reporte XML (para CI/CD)
pytest --cov=src --cov-report=xml

# Fallar si cobertura < 80%
pytest --cov=src --cov-fail-under=80
```

### Excluir Archivos de Cobertura

En `.coveragerc`:
```ini
[run]
omit = 
    */tests/*
    */venv/*
    */build/*
    setup.py
```

## 🏷️ Marcadores de Pruebas

### Marcadores Disponibles

- `@pytest.mark.unit` - Pruebas unitarias
- `@pytest.mark.integration` - Pruebas de integración
- `@pytest.mark.kpi` - Pruebas de KPIs
- `@pytest.mark.export` - Pruebas de exportación
- `@pytest.mark.free_limit` - Pruebas de límites FREE
- `@pytest.mark.slow` - Pruebas que tardan más tiempo

### Usar Marcadores

```python
@pytest.mark.unit
@pytest.mark.kpi
def test_calculate_kpis():
    # Test de KPI unitario
    pass

@pytest.mark.slow
def test_large_dataset():
    # Test que tarda mucho tiempo
    pass
```

## 🛠️ Fixtures Disponibles

### Fixtures de Datos

```python
def test_with_sample_data(sample_invoice_data):
    # sample_invoice_data contiene facturas de ejemplo
    assert len(sample_invoice_data) == 3

def test_with_temp_dir(temp_output_dir):
    # temp_output_dir es un directorio temporal
    file_path = os.path.join(temp_output_dir, "test.csv")
```

### Fixtures de Mocks

```python
def test_kpi_service(kpi_service):
    # kpi_service ya configurado con mocks
    result = kpi_service.calculate_real_kpis(2025)
    assert result is not None

def test_with_mocked_repo(mock_invoice_repository):
    # Repositorio mockeado listo para usar
    mock_invoice_repository.get_invoices.return_value = []
```

## 🧪 Escribir Nuevas Pruebas

### Estructura de Prueba Unitaria

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
@pytest.mark.kpi
class TestKPIService:
    """Pruebas unitarias para KPIService."""

    def test_calculate_kpis_success(self, kpi_service, sample_invoice_data):
        """Test exitoso de cálculo de KPIs."""
        # Arrange
        kpi_service._invoice_repository.get_invoices.return_value = sample_invoice_data
        
        # Act
        result = kpi_service.calculate_real_kpis(2025)
        
        # Assert
        assert isinstance(result, KPIData)
        assert result.ventas_totales > 0
        assert result.num_facturas > 0

    def test_calculate_kpis_empty_data(self, kpi_service):
        """Test con datos vacíos."""
        # Arrange
        kpi_service._invoice_repository.get_invoices.return_value = []
        
        # Act
        result = kpi_service.calculate_real_kpis(2025)
        
        # Assert
        assert result.ventas_totales == 0
        assert result.num_facturas == 0
```

### Estructura de Prueba de Integración

```python
@pytest.mark.integration
class TestSystemIntegration:
    """Pruebas de integración del sistema."""

    def test_full_kpi_flow(self, real_file_storage, real_logger):
        """Test del flujo completo de KPIs."""
        # Usar componentes reales cuando sea posible
        # Mock solo las dependencias externas (APIs, etc.)
        pass
```

## ⚡ Optimización de Pruebas

### Pruebas Rápidas vs Lentas

```python
# Prueba rápida (< 1 segundo)
@pytest.mark.unit
def test_quick_calculation():
    result = simple_function()
    assert result == expected

# Prueba lenta (> 5 segundos)
@pytest.mark.slow
def test_large_dataset_processing():
    # Procesar 10,000+ registros
    pass
```

### Parametrización

```python
@pytest.mark.parametrize("input_value,expected", [
    (100, 119),      # Con IVA 19%
    (1000, 1190),
    (0, 0),
])
def test_calculate_with_tax(input_value, expected):
    result = calculate_with_tax(input_value, 0.19)
    assert result == expected
```

## 🔍 Debugging de Pruebas

### Debugging Básico

```bash
# Parar en la primera falla
pytest -x

# Mostrar variables locales en fallos
pytest -l

# Modo debug interactivo
pytest --pdb

# Capturar solo fallos, no éxitos
pytest --tb=short
```

### Debugging con Print

```python
def test_debug_example():
    data = get_test_data()
    print(f"Debug: data = {data}")  # Se verá con pytest -s
    assert data is not None
```

## 📈 Métricas de Calidad

### Ejecutar Todas las Herramientas

```bash
# Formateo de código
black src/ tests/

# Ordenar imports
isort src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Análisis estático
pylint src/

# Seguridad
bandit -r src/
safety check
```

### Script de Calidad Completo

```bash
#!/bin/bash
# quality_check.sh

echo "🔍 Ejecutando verificaciones de calidad..."

echo "📋 Formateo con Black..."
black --check src/ tests/

echo "📦 Ordenando imports con isort..."
isort --check-only src/ tests/

echo "🔍 Linting con flake8..."
flake8 src/ tests/

echo "🧪 Ejecutando pruebas..."
pytest --cov=src --cov-fail-under=80

echo "✅ Verificaciones completadas!"
```

## 🚀 CI/CD Integration

### GitHub Actions

Las pruebas se ejecutan automáticamente en:
- Cada push a `main`, `develop`, `refactorizar`
- Cada pull request
- Cada release tag

### Local Pre-commit

```bash
# Instalar pre-commit hooks
pip install pre-commit
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

## 📝 Mejores Prácticas

1. **AAA Pattern**: Arrange, Act, Assert
2. **Una aserción por prueba**: Fácil de entender qué falló
3. **Nombres descriptivos**: `test_calculate_kpis_with_empty_data`
4. **Mocks para dependencias externas**: APIs, DB, archivos
5. **Fixtures para datos comunes**: Reutilizar configuraciones
6. **Marcar pruebas lentas**: Permitir ejecución rápida
7. **Probar casos límite**: Datos vacíos, nulos, extremos
8. **Cobertura > 80%**: Pero calidad > cantidad

## 🆘 Solución de Problemas

### Errores Comunes

**ImportError al ejecutar pruebas:**
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Fixtures no encontrados:**
```bash
# Verificar conftest.py en la ubicación correcta
ls tests/conftest.py
```

**Pruebas muy lentas:**
```bash
# Ejecutar solo pruebas rápidas
pytest -m "not slow"
```

**Cobertura baja:**
```bash
# Ver líneas no cubiertas
pytest --cov=src --cov-report=term-missing
```

---

¡Felices pruebas! 🎉