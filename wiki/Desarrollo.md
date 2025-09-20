# 🔧 Desarrollo - DataConta

Guía completa para desarrolladores que desean contribuir o extender DataConta.

## 🏗️ Configuración del Entorno de Desarrollo

### 📋 **Prerrequisitos para Desarrollo**
- Python 3.11+ (recomendado para desarrollo)
- Git 2.30+
- IDE recomendado: VS Code con extensiones Python
- Conocimiento de Arquitectura Hexagonal y principios SOLID

### 🛠️ **Setup Inicial**
```bash
# 1. Fork y clonar
git clone https://github.com/tu-username/dataconta.git
cd dataconta

# 2. Crear entorno de desarrollo
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 3. Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
```

### 📦 **Dependencias de Desarrollo**
```txt
# requirements-dev.txt
pytest>=7.4.0              # Testing framework
pytest-cov>=4.1.0          # Coverage reports
black>=23.0.0               # Code formatting
flake8>=6.0.0               # Linting
mypy>=1.5.0                 # Type checking
pre-commit>=3.3.0           # Git hooks
bandit>=1.7.0               # Security linting
isort>=5.12.0               # Import sorting
```

### 🔧 **Configuración de Herramientas**

#### **Pre-commit Hooks**
```bash
# Instalar hooks
pre-commit install

# Configuración (.pre-commit-config.yaml)
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

#### **VS Code Settings**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"]
}
```

## 📐 Principios y Convenciones

### 🎯 **Principios de Desarrollo**
1. **Clean Code**: Código limpio y autodocumentado
2. **SOLID**: Principios de diseño orientado a objetos
3. **DRY**: Don't Repeat Yourself
4. **YAGNI**: You Aren't Gonna Need It
5. **Boy Scout Rule**: Deja el código mejor de como lo encontraste

### 📝 **Convenciones de Código**

#### **Naming Conventions**
```python
# Variables y funciones: snake_case
invoice_total = calculate_invoice_total()

# Clases: PascalCase
class InvoiceService:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_INVOICES_PER_QUERY = 1000

# Archivos y módulos: snake_case
# siigo_api_adapter.py
```

#### **Type Hints Obligatorios**
```python
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

def process_invoices(
    invoices: List[Invoice],
    date_filter: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Procesa facturas con filtro opcional de fecha.
    
    Args:
        invoices: Lista de facturas a procesar
        date_filter: Fecha límite para filtrado (opcional)
    
    Returns:
        Diccionario con estadísticas procesadas
    
    Raises:
        ValidationError: Si las facturas no son válidas
    """
    pass
```

#### **Docstrings Google Style**
```python
class InvoiceRepository:
    """Repositorio para gestión de facturas.
    
    Este repositorio maneja la persistencia y recuperación de facturas
    siguiendo el patrón Repository del Domain-Driven Design.
    
    Attributes:
        connection: Conexión a la base de datos
        cache: Cache para consultas frecuentes
    
    Example:
        >>> repo = InvoiceRepository()
        >>> invoices = repo.find_by_date_range(start_date, end_date)
    """
    
    def find_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """Busca factura por ID.
        
        Args:
            invoice_id: Identificador único de la factura
            
        Returns:
            Factura encontrada o None si no existe
            
        Raises:
            DatabaseError: Si hay error de conectividad
        """
        pass
```

### 🏗️ **Arquitectura - Dónde Agregar Código**

#### **Nueva Entidad de Dominio**
```python
# src/domain/entities/nueva_entidad.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class NuevaEntidad:
    """Entidad de dominio para X."""
    id: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def validate(self) -> bool:
        """Validación de lógica de negocio."""
        return len(self.name) > 0
```

#### **Nuevo Caso de Uso**
```python
# src/application/use_cases/nuevo_use_case.py
from abc import ABC, abstractmethod
from src.domain.entities.nueva_entidad import NuevaEntidad

class NuevoUseCaseInterface(ABC):
    """Interfaz para el caso de uso."""
    
    @abstractmethod
    def execute(self, params: dict) -> NuevaEntidad:
        pass

class NuevoUseCase(NuevoUseCaseInterface):
    """Implementación del caso de uso."""
    
    def __init__(self, repository: NuevaEntidadRepository):
        self._repository = repository
    
    def execute(self, params: dict) -> NuevaEntidad:
        # Lógica del caso de uso
        pass
```

#### **Nuevo Adaptador**
```python
# src/infrastructure/adapters/nuevo_adapter.py
from src.application.ports.interfaces import NuevoRepositoryInterface
from src.domain.entities.nueva_entidad import NuevaEntidad

class NuevoAdapter(NuevoRepositoryInterface):
    """Adaptador para servicio externo."""
    
    def __init__(self, config: dict):
        self._config = config
    
    def fetch_data(self) -> List[NuevaEntidad]:
        # Implementación específica del adaptador
        pass
```

## 🧪 Testing

### 📋 **Estrategia de Testing**

#### **Pirámide de Tests**
```
    🔺 E2E Tests (5%)
   🔺🔺 Integration Tests (15%)
  🔺🔺🔺 Unit Tests (80%)
```

#### **Estructura de Tests**
```
tests/
├── unit/                    # Tests unitarios
│   ├── domain/             # Tests de entidades y servicios de dominio
│   ├── application/        # Tests de casos de uso
│   └── infrastructure/     # Tests de adaptadores
├── integration/            # Tests de integración
│   ├── test_siigo_api.py  # Integración con API
│   └── test_database.py   # Integración con DB
└── e2e/                    # Tests end-to-end
    └── test_complete_flow.py
```

### ✅ **Escribir Tests Unitarios**

#### **Test de Entidad de Dominio**
```python
# tests/unit/domain/test_invoice.py
import pytest
from decimal import Decimal
from src.domain.entities.invoice import Invoice

class TestInvoice:
    def test_create_valid_invoice(self):
        """Test creación de factura válida."""
        invoice = Invoice(
            id="INV-001",
            total=Decimal("1000.00"),
            customer_id="CUST-001"
        )
        
        assert invoice.id == "INV-001"
        assert invoice.total == Decimal("1000.00")
        assert invoice.is_valid()
    
    def test_invoice_validation_fails_negative_total(self):
        """Test validación falla con total negativo."""
        with pytest.raises(ValidationError):
            Invoice(
                id="INV-002",
                total=Decimal("-100.00"),
                customer_id="CUST-001"
            )
    
    @pytest.mark.parametrize("total,expected", [
        (Decimal("0.00"), False),
        (Decimal("0.01"), True),
        (Decimal("1000.00"), True)
    ])
    def test_invoice_validation_edge_cases(self, total, expected):
        """Test casos límite de validación."""
        invoice = Invoice(id="INV-003", total=total, customer_id="CUST-001")
        assert invoice.is_valid() == expected
```

#### **Test de Caso de Uso**
```python
# tests/unit/application/test_invoice_service.py
import pytest
from unittest.mock import Mock, patch
from src.application.services.invoice_service import InvoiceService

class TestInvoiceService:
    def setup_method(self):
        """Setup para cada test."""
        self.mock_repository = Mock()
        self.service = InvoiceService(self.mock_repository)
    
    def test_get_invoices_by_date_range_success(self):
        """Test obtención exitosa de facturas por rango de fechas."""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        expected_invoices = [Mock(), Mock()]
        self.mock_repository.find_by_date_range.return_value = expected_invoices
        
        # Act
        result = self.service.get_invoices_by_date_range(start_date, end_date)
        
        # Assert
        assert len(result) == 2
        self.mock_repository.find_by_date_range.assert_called_once_with(
            start_date, end_date
        )
```

#### **Test de Adaptador**
```python
# tests/unit/infrastructure/test_siigo_adapter.py
import pytest
from unittest.mock import Mock, patch
import requests
from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter

class TestSiigoAPIAdapter:
    def setup_method(self):
        """Setup para cada test."""
        self.adapter = SiigoAPIAdapter("user", "key")
    
    @patch('requests.post')
    def test_authenticate_success(self, mock_post):
        """Test autenticación exitosa."""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "token123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Act
        token = self.adapter.authenticate()
        
        # Assert
        assert token == "token123"
        mock_post.assert_called_once()
```

### 🏃‍♂️ **Ejecutar Tests**

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/unit/domain/

# Con cobertura
pytest --cov=src --cov-report=html

# Solo tests que fallan
pytest --lf

# Modo verbose
pytest -v

# Ejecutar tests en paralelo
pytest -n auto
```

### 📊 **Coverage Reports**
```bash
# Generar reporte HTML
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Reporte en consola
pytest --cov=src --cov-report=term-missing

# Fallar si coverage < 80%
pytest --cov=src --cov-fail-under=80
```

## 🔄 Git Workflow

### 🌿 **Branching Strategy**

#### **Ramas Principales**
- `main`: Código en producción
- `develop`: Rama de desarrollo principal
- `feature/*`: Nuevas funcionalidades
- `bugfix/*`: Correcciones de errores
- `hotfix/*`: Correcciones urgentes de producción

#### **Naming Conventions**
```bash
# Features
feature/ISSUE-123-add-invoice-export
feature/addon-system-implementation

# Bugfixes  
bugfix/ISSUE-456-fix-authentication-error
bugfix/memory-leak-in-export

# Hotfixes
hotfix/critical-security-patch
hotfix/production-crash-fix
```

### 📝 **Commit Messages**

#### **Formato Convencional**
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### **Tipos de Commits**
```bash
# Nuevas funcionalidades
feat(auth): add JWT authentication support

# Correcciones de errores
fix(export): resolve memory leak in large exports

# Documentación
docs(readme): update installation instructions

# Refactoring
refactor(services): extract common validation logic

# Tests
test(invoice): add edge case tests for validation

# Configuración/CI
chore(deps): update PySide6 to 6.7.0
```

#### **Ejemplos de Buenos Commits**
```bash
feat(gui): implement dynamic menu system

- Add menu configuration via JSON
- Support for license-based menu visibility
- Auto-reload configuration without restart
- Add menu validation and error handling

Closes #123

fix(api): handle connection timeout gracefully

- Add exponential backoff for failed requests
- Improve error messages for network issues
- Add unit tests for timeout scenarios

Fixes #456

refactor(architecture): extract addon system interfaces

- Move addon interfaces to application/ports
- Implement factory pattern for addon creation
- Add comprehensive validation for addon manifests
- Update documentation with architecture diagrams

BREAKING CHANGE: addon interface signatures changed
```

### 🔄 **Pull Request Process**

#### **Checklist del PR**
- [ ] **Tests**: Todos los tests pasan (`pytest`)
- [ ] **Coverage**: Coverage ≥ 80% en nuevos archivos
- [ ] **Linting**: Sin errores de flake8/black (`pre-commit run --all-files`)
- [ ] **Type Hints**: Todas las funciones públicas tipadas
- [ ] **Documentación**: Docstrings actualizadas
- [ ] **CHANGELOG**: Cambios documentados si aplica

#### **Template de PR**
```markdown
## 📋 Descripción
Descripción breve de los cambios realizados.

## 🎯 Tipo de Cambio
- [ ] 🆕 Nueva funcionalidad
- [ ] 🐛 Corrección de error
- [ ] 📚 Documentación
- [ ] ♻️ Refactoring
- [ ] ⚡ Mejora de rendimiento

## 🧪 Testing
- [ ] Tests unitarios agregados/actualizados
- [ ] Tests de integración verificados
- [ ] Tests manuales realizados

## 📝 Checklist
- [ ] Self-review completado
- [ ] Documentación actualizada
- [ ] No hay breaking changes (o están documentados)
- [ ] Screenshots agregados (si aplica)
```

## 🚀 Continuous Integration

### 🏗️ **GitHub Actions**

#### **Workflow Principal (.github/workflows/ci.yml)**
```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: flake8 src/ tests/
    
    - name: Type check with mypy
      run: mypy src/
    
    - name: Test with pytest
      run: pytest --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

### 📊 **Quality Gates**

#### **Requisitos para Merge**
- ✅ Todos los tests pasan en múltiples versiones de Python
- ✅ Coverage ≥ 80%
- ✅ No hay errores de linting
- ✅ Type checking pasa sin errores
- ✅ Al menos 1 aprobación de code review
- ✅ Todas las conversaciones resueltas

## 🔐 Seguridad

### 🛡️ **Security Checklist**

#### **Para Desarrollo**
- [ ] No commitear credenciales (usar `.env`)
- [ ] Validar todas las entradas de usuario
- [ ] Usar HTTPS para todas las API calls
- [ ] Logging sin datos sensibles
- [ ] Dependencias actualizadas (sin vulnerabilidades)

#### **Code Security**
```bash
# Verificar vulnerabilidades en dependencias
pip-audit

# Security linting
bandit -r src/

# Verificar secrets en commits
git secrets --scan
```

## 📚 Recursos para Desarrolladores

### 📖 **Documentación Técnica**
- [Arquitectura Hexagonal](Arquitectura.md)
- [API Reference](API-Reference.md)
- [Sistema de Addons](Sistema-de-Addons.md)

### 🛠️ **Herramientas Recomendadas**
- **IDE**: VS Code con Python extension pack
- **Database Browser**: DBeaver para análisis de datos
- **API Testing**: Postman o Insomnia
- **Diagramas**: Draw.io para arquitectura

### 🎓 **Recursos de Aprendizaje**
- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://realpython.com/solid-principles-python/)
- [Effective Python](https://effectivepython.com/)
- [Python Type Checking](https://mypy.readthedocs.io/)

---

¡Bienvenido al equipo de desarrollo de DataConta! 🎉