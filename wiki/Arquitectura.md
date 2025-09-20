# 🏗️ Arquitectura - DataConta

DataConta implementa **Arquitectura Hexagonal** (Clean Architecture) con separación completa de responsabilidades siguiendo principios **SOLID**.

## 📐 Principios Arquitectónicos

### 🎯 **Arquitectura Hexagonal (Ports & Adapters)**

```
        📱 Presentación (GUI/CLI)
              ⬇️ ⬆️
        🔌 Puertos (Interfaces)
              ⬇️ ⬆️
    🎯 Dominio (Lógica de Negocio)
              ⬇️ ⬆️
        🔌 Puertos (Interfaces)
              ⬇️ ⬆️
    🔧 Infraestructura (APIs, DB)
```

### 🔧 **Principios SOLID Aplicados**

- ✅ **S**ingle Responsibility: Cada clase una responsabilidad específica
- ✅ **O**pen/Closed: Extensible sin modificar código existente  
- ✅ **L**iskov Substitution: Implementaciones intercambiables
- ✅ **I**nterface Segregation: Interfaces específicas y cohesivas
- ✅ **D**ependency Inversion: Inyección de dependencias

## 📂 Estructura del Proyecto

```
📂 src/
├── 🎯 domain/                    # Dominio - Lógica de Negocio Pura
│   ├── entities/                # Entidades: Invoice, Cliente, FinancialReports
│   │   ├── invoice.py          # Entidades de facturación
│   │   └── financial_reports.py # Entidades de informes financieros
│   └── services/               # Servicios de dominio
│       └── financial_reports_service.py
│
├── 🔄 application/              # Aplicación - Casos de Uso
│   ├── ports/interfaces.py     # Puertos (abstracciones)
│   ├── services/                # Servicios de aplicación
│   │   ├── InvoiceExportService.py
│   │   └── BIExportService.py
│   ├── use_cases/               # Casos de uso
│   │   ├── invoice_use_cases.py
│   │   └── financial_reports_use_cases.py
│   └── dtos/                    # Data Transfer Objects
│       └── financial_reports_dtos.py
│
├── 🔌 infrastructure/           # Infraestructura - Adaptadores
│   ├── adapters/               # Adaptadores para servicios externos
│   │   ├── siigo_api_adapter.py
│   │   ├── license_validator_adapter.py
│   │   ├── file_storage_adapter.py
│   │   ├── csv_file_adapter.py
│   │   └── financial_reports_repository.py
│   ├── config/                 # Configuración
│   │   ├── environment_config.py
│   │   └── dynamic_menu_config.py
│   └── factories/              # Factories para inyección de dependencias
│       └── financial_reports_factory.py
│
├── 🖥️ presentation/            # Presentación - Interfaces
│   ├── cli_interface.py        # Interfaz CLI
│   ├── gui_interface.py        # Interfaz GUI (PySide6)
│   └── financial_reports_integration.py
│
└── 📋 tests/                   # Tests unitarios
    └── test_bi_export.py
```

## 🔌 Patrones de Diseño Implementados

### 🏭 **Factory Pattern**
```python
class FinancialReportsFactory:
    """Factory para crear servicios de informes financieros."""
    
    @staticmethod
    def create_service() -> FinancialReportsService:
        repository = FinancialReportsRepository()
        return FinancialReportsService(repository)
```

### 🔌 **Adapter Pattern**
```python
class SiigoAPIAdapter:
    """Adaptador para integración con API de Siigo."""
    
    def get_invoices(self, filters: InvoiceFilters) -> List[Invoice]:
        # Adaptación de API externa a modelo interno
        pass
```

### 📊 **Repository Pattern**
```python
class InvoiceRepository(ABC):
    """Repositorio abstracto para facturas."""
    
    @abstractmethod
    def find_by_date_range(self, start: date, end: date) -> List[Invoice]:
        pass
```

### 🎯 **Strategy Pattern**
```python
class ExportStrategy(ABC):
    """Estrategia abstracta para exportación."""
    
    @abstractmethod
    def export(self, data: Any, path: str) -> bool:
        pass

class CSVExportStrategy(ExportStrategy):
    def export(self, data: Any, path: str) -> bool:
        # Implementación específica para CSV
        pass
```

## 🔄 Flujo de Datos

### 📊 **Consulta de Facturas**
```
1. 🖥️ GUI/CLI → 2. 🎯 Use Case → 3. 🔌 Repository → 4. 🌐 API Siigo
   ⬅️ Invoice[]  ⬅️ Invoice[]    ⬅️ Invoice[]     ⬅️ JSON Response
```

### 📈 **Generación de Informes**
```
1. 🖥️ Solicitud → 2. 🎯 Service → 3. 📊 Calculator → 4. 💾 Storage
   ⬅️ Report      ⬅️ Report      ⬅️ FinancialData ⬅️ Success
```

## 🧪 Testing Strategy

### 📋 **Tipos de Tests**
- **Unit Tests**: Lógica de dominio y servicios
- **Integration Tests**: Adaptadores e API
- **E2E Tests**: Flujo completo usuario

### 🎯 **Cobertura de Código**
- **Dominio**: 95%+ (lógica crítica)
- **Aplicación**: 90%+ (casos de uso)
- **Infraestructura**: 80%+ (adaptadores)

```bash
# Ejecutar tests
pytest tests/

# Cobertura
pytest --cov=src tests/
```

## ⚡ Características de Rendimiento

### 🚀 **Optimizaciones**
- **Cache inteligente**: Consultas repetitivas
- **Paginación automática**: Grandes volúmenes
- **Lazy loading**: Datos bajo demanda
- **Connection pooling**: API requests eficientes

### 📊 **Métricas Típicas**
- **Inicio**: < 3 segundos
- **Consulta API**: 100 facturas en < 5 segundos
- **Exportación BI**: 1,000 registros en < 30 segundos
- **Memoria**: < 150MB en uso típico

## 🔐 Seguridad

### 🛡️ **Medidas Implementadas**
- **Variables de entorno** para credenciales
- **HTTPS obligatorio** para API calls
- **Validación de entrada** en todos los endpoints
- **No logging** de datos sensibles
- **Sanitización** de outputs

### 🔑 **Autenticación**
```python
class SecureCredentialManager:
    """Gestor seguro de credenciales."""
    
    def get_api_credentials(self) -> Tuple[str, str]:
        username = os.getenv('SIIGO_USERNAME')
        access_key = os.getenv('SIIGO_ACCESS_KEY')
        
        if not username or not access_key:
            raise SecurityError("Credenciales no configuradas")
            
        return username, access_key
```

## 🔄 Extensibilidad

### 🔌 **Sistema de Addons**
DataConta incluye un sistema completo de addons que permite extensibilidad sin modificar el core:

```python
class AddonBase(ABC):
    """Clase base para todos los addons."""
    
    @abstractmethod
    def initialize(self, context: AddonContext) -> bool:
        pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        pass
```

### 📦 **Nuevas Funcionalidades**
- **Nuevos exportadores**: Implementar `ExportStrategy`
- **Nuevas APIs**: Crear adaptador siguiendo patrón establecido
- **Nuevos informes**: Extender `FinancialReportsService`
- **Nuevas interfaces**: Implementar en capa de presentación

## 📈 Escalabilidad

### 🏢 **Para Empresas Grandes**
- **Multi-tenant**: Soporte para múltiples empresas
- **Microservices**: Separación de servicios independientes
- **Load balancing**: Distribución de carga
- **Monitoring**: Métricas y observabilidad

### 📊 **Configuración de Alto Volumen**
```python
# En environment_config.py
class HighVolumeConfig:
    MAX_INVOICES_PER_QUERY = 5000
    PARALLEL_REQUESTS = 10
    CACHE_EXPIRATION_HOURS = 1
    BATCH_SIZE = 1000
```

---

Esta arquitectura garantiza que DataConta sea mantenible, extensible y escalable, siguiendo las mejores prácticas de desarrollo de software empresarial.