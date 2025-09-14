# 🔐 Configuración de Licencia de Prueba

## ✅ Licencia Configurada

Tu archivo `.env` ya está configurado con una licencia de prueba válida:

```env
LICENSE_KEY=DEMO-TEST-2024-LOCAL
LICENSE_URL=https://demo-license-server.local/validate
```

## 🛠️ Cómo Funciona la Validación

### Modo Online
- La aplicación intenta validar la licencia contra el servidor remoto
- Si no hay conexión o el servidor no está disponible, automáticamente cambia al modo offline

### Modo Offline (Activo para pruebas)
- La clave `DEMO-TEST-2024-LOCAL` está hardcodeada como válida para desarrollo local
- No requiere conexión a internet
- Perfecta para pruebas y desarrollo

## 🚀 Ejecutar la Aplicación

```bash
python main.py
```

## 🧪 Probar Solo la Validación de Licencia

```bash
python test_license.py
```

## 📋 Estado Actual

✅ **Licencia configurada**: `DEMO-TEST-2024-LOCAL`  
✅ **Validación offline**: Habilitada  
✅ **Lista para desarrollo**: Sí  

---

**Nota**: Para producción, reemplaza estos valores con tu licencia real y servidor de validación.