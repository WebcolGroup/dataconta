# 📜 Development Rules – No romper nunca

Estas reglas son obligatorias para **todo nuevo desarrollo, método, clase o funcionalidad**.  
Copilot y los desarrolladores deben seguirlas siempre.  

---

## 1. Principios generales
- ✅ Seguir **Clean Code**:
  - Nombres claros, expresivos y consistentes.
  - Métodos cortos y con una sola responsabilidad.
  - Evitar duplicación de código (DRY).
  - Comentarios solo cuando el código no sea autoexplicativo.
- ✅ Aplicar **principios SOLID**.
- ✅ Respetar **Arquitectura Hexagonal (Ports & Adapters)**:
  - Core de dominio independiente de frameworks y bases de datos.
  - Adaptadores externos en capas separadas.
  - Inyección de dependencias, nunca acoplamientos directos.

---

## 2. Estructura de proyecto
- **DTOs** → Solo transportar datos, sin lógica.  
- **Models (Domain Entities)** → Representan reglas del negocio.  
- **Interfaces (Ports)** → Definen contratos entre capas.  
- **Controllers (Adapters)** → Solo reciben/validan y delegan.  
- **Services / Use Cases** → Cada caso de uso encapsulado en su propia clase.  
- **Repositories** → Implementan interfaces de acceso a datos.  
- **Widgets (UI)** → Reutilizables, desacoplados, sin lógica de negocio.  

---

## 3. Buenas prácticas adicionales
- **Testing**:
  - Cobertura mínima del 80% en el core.
  - Usar mocks/stubs para dependencias externas.
- **Documentación**:
  - Documentar DTOs, Interfaces y Casos de Uso.
- **Seguridad**:
  - Nunca exponer credenciales en el código.
  - Validar siempre la entrada del usuario.
- **Logs & Errores**:
  - Excepciones personalizadas.
  - Logs claros, nunca exponer datos sensibles.
- **Estilo de código**:
  - Seguir linters y formateadores automáticos.
  - Convenciones oficiales del lenguaje.

---

## 4. Reglas específicas para Copilot
- Usar **estas reglas como referencia obligatoria**.
- No generar métodos con más de **30 líneas**.
- Cada clase debe estar en su **capa correcta**.
- No repetir código existente (sugerir refactorización).
- Proponer patrones de diseño si aplica (Factory, Strategy, Adapter, etc.).

---
