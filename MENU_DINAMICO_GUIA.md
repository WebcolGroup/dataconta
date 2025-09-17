# DATACONTA - Sistema de Menús Dinámico
# Guía de Configuración JSON

## 📋 Cómo usar el sistema de menús dinámico

El sistema de menús de DATACONTA ahora es completamente configurable mediante el archivo `menu_config.json`. Puedes agregar, quitar o modificar elementos fácilmente.

## 🔧 Estructura del archivo menu_config.json

### 1. Categorías de Menú Principal
```json
"horizontal_menu": {
  "categoria_id": {
    "label": "Texto del botón",
    "icon": "🔧",
    "enabled": true,
    "submenu": [...]
  }
}
```

### 2. Elementos de Submenú
```json
"submenu": [
  {
    "id": "identificador_unico",
    "label": "Texto del elemento",
    "icon": "📋",
    "action": "accion_a_ejecutar",
    "confirmation": "Mensaje de confirmación (opcional)",
    "enabled": true
  }
]
```

### 3. Acciones de Menú
```json
"menu_actions": {
  "accion_id": {
    "type": "dialog|system",
    "title": "Título del diálogo",
    "content": "Contenido del mensaje",
    "description": "Descripción de la acción"
  }
}
```

## 📚 Ejemplos de uso

### Agregar nueva categoría "Configuración"
```json
"configuracion": {
  "label": "Configuración",
  "icon": "⚙️",
  "enabled": true,
  "submenu": [
    {
      "id": "preferencias",
      "label": "Preferencias",
      "icon": "🎛️",
      "action": "show_preferences",
      "enabled": true
    }
  ]
}
```

### Agregar nueva acción
```json
"show_preferences": {
  "type": "dialog",
  "title": "Preferencias del Sistema",
  "content": "Aquí puedes configurar las preferencias de la aplicación...",
  "description": "Mostrar preferencias del usuario"
}
```

### Deshabilitar un elemento
```json
{
  "id": "elemento_id",
  "label": "Elemento Deshabilitado",
  "icon": "❌",
  "action": "accion",
  "enabled": false
}
```

## 🎯 Casos de uso común

### 1. Agregar nuevo menú "Reportes"
Edita `menu_config.json` y agrega:
```json
"reportes": {
  "label": "Reportes",
  "icon": "📊",
  "enabled": true,
  "submenu": [
    {
      "id": "generar_reporte",
      "label": "Generar Reporte",
      "icon": "📈",
      "action": "generate_report",
      "enabled": true
    },
    {
      "id": "ver_historico",
      "label": "Ver Histórico",
      "icon": "📋",
      "action": "show_history",
      "enabled": true
    }
  ]
}
```

### 2. Quitar una categoría
Simplemente elimina la sección completa de `horizontal_menu`.

### 3. Modificar texto o iconos
Cambia los valores de `label` e `icon` en el JSON.

## 🔄 Recarga en tiempo real

El sistema permite recargar la configuración sin reiniciar la aplicación (funcionalidad avanzada):

```python
# Desde el código
main_window.reload_dynamic_menu()

# Agregar categoría en tiempo de ejecución
main_window.add_menu_category_runtime("nueva_categoria", config)

# Remover categoría
main_window.remove_menu_category_runtime("categoria_a_remover")
```

## 💡 Tips y mejores prácticas

1. **Iconos**: Usa emojis para mejor visualización
2. **IDs únicos**: Cada elemento debe tener un ID único
3. **Confirmaciones**: Usa `confirmation` para acciones críticas
4. **Habilitación**: Usa `enabled: false` para deshabilitar temporalmente
5. **Tipos de acción**:
   - `"system"`: Acciones del sistema (ej: salir)
   - `"dialog"`: Mostrar información en diálogo

## 🚀 Extensibilidad

El sistema está diseñado para ser extensible. Puedes:
- Agregar nuevos tipos de acciones
- Implementar acciones personalizadas
- Conectar con otros sistemas mediante señales
- Crear menús contextuales adicionales

## ⚠️ Consideraciones

- Siempre haz backup del archivo `menu_config.json`
- Valida la sintaxis JSON antes de guardar
- Los cambios requieren reiniciar la aplicación actualmente
- Mantén consistencia en iconos y nomenclatura