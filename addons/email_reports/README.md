# Email Reports Addon

Addon de ejemplo para **DataConta** que demuestra el sistema de addons enviando reportes financieros por correo electrónico.

## 📋 Descripción

Este addon proporciona funcionalidades para enviar reportes automáticos de DataConta por email, incluyendo:

- ✅ Reportes diarios de ventas
- ✅ Reportes mensuales completos  
- ✅ Configuración flexible de email
- ✅ Integración con datos de Siigo
- ✅ Interfaz gráfica integrada

## 🚀 Características

### **Funcionalidades Principales:**
- **Reporte Diario**: Envío automático de métricas diarias
- **Reporte Mensual**: Resumen completo con top clientes
- **Configuración Email**: Setup fácil de SMTP y destinatarios
- **HTML Templates**: Reportes profesionales con formato HTML
- **Modo Demo**: Funciona sin configuración real de email

### **Integración con DataConta:**
- Sigue arquitectura hexagonal
- Cumple con principios SOLID
- Integración con sistema de menús dinámicos
- Validación de licencias (PROFESSIONAL+)
- Logging completo

## 📦 Instalación

1. **Copiar addon** en la carpeta `addons/email_reports/`
2. **Validar manifest.json** con el esquema definido
3. **Recargar sistema** de addons en DataConta
4. **Configurar email** usando la opción del menú

## ⚙️ Configuración

### **Configuración de Email:**
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "tu-email@empresa.com",
  "sender_password": "tu-password",
  "recipient_emails": [
    "gerencia@empresa.com",
    "contabilidad@empresa.com"
  ]
}
```

### **Permisos Requeridos:**
- `email_send`: Para envío de correos
- `file_read`: Para leer datos de reportes
- `data_export`: Para exportar información

## 🎛️ Uso

### **Desde el Menú GUI:**
1. Abrir DataConta GUI
2. Buscar categoría **"📦 Email Reports"**
3. Seleccionar acción deseada:
   - 📧 **Enviar Reporte Diario**
   - 📊 **Enviar Reporte Mensual**  
   - ⚙️ **Configurar Email**

### **Acciones Disponibles:**
- `send_daily_report`: Envía reporte diario
- `send_monthly_report`: Envía reporte mensual
- `configure_email_settings`: Configura ajustes de email

## 📊 Ejemplo de Reportes

### **Reporte Diario:**
```
📊 Reporte Diario DataConta
Fecha: 2025-09-17

💰 Total Ventas: $15,420.50
📄 Número de Facturas: 23
🏆 Cliente Principal: Empresa ABC S.A.S
    Valor: $5,420.00
```

### **Reporte Mensual:**
```
📈 Reporte Mensual DataConta  
Período: Septiembre 2025

💰 Total Ventas del Mes: $456,789.25
📄 Total Facturas: 342
📊 Promedio Diario: $15,226.31

🏆 Top 3 Clientes del Mes:
1. Cliente A S.A.S: $89,456.20
2. Cliente B Ltda: $67,834.15  
3. Cliente C S.A.S: $45,678.30
```

## 🔧 Desarrollo

### **Estructura de Archivos:**
```
email_reports/
├── manifest.json              # Configuración del addon
├── email_reports_addon.py     # Implementación principal
├── email_config.json          # Configuración de email (generado)
└── README.md                  # Esta documentación
```

### **Arquitectura:**
- **AddonBase**: Clase base implementada
- **EmailConfig**: Configuración con dataclass  
- **SOLID Principles**: Responsabilidad única, interfaces
- **Error Handling**: Manejo robusto de errores
- **Logging**: Integración con sistema de logs

### **Testing:**
```bash
# Test básico del addon
cd addons/email_reports/
python email_reports_addon.py
```

## 🛡️ Seguridad

### **Validaciones:**
- ✅ Sandbox habilitado
- ✅ Permisos específicos requeridos
- ✅ Validación de manifest.json
- ✅ Checksum de integridad (opcional)

### **Consideraciones:**
- Passwords en config (usar encriptación en producción)
- Validación de destinatarios de email
- Rate limiting para envío de emails
- Logs de auditoría

## 📄 Licencia

**MIT License** - Ver archivo de licencia para detalles.

## 🤝 Contribuciones

Este es un addon de **ejemplo** para demostrar el sistema de addons de DataConta.

### **Para Contribuir:**
1. Fork del repositorio
2. Crear branch para feature
3. Seguir estándares de código de DataConta
4. Testing completo
5. Pull request con descripción clara

## 📞 Soporte

- **Logs**: Revisar logs de DataConta para debugging
- **Configuración**: Verificar `email_config.json` 
- **Permisos**: Validar que el addon tenga permisos necesarios
- **Licencia**: Requiere licencia PROFESSIONAL o superior

## 🎯 Roadmap

### **Versión 1.1:**
- [ ] Templates de reporte personalizables
- [ ] Programación automática de envíos
- [ ] Archivos adjuntos (CSV, PDF)
- [ ] Múltiples idiomas

### **Versión 1.2:**
- [ ] Integración con calendarios
- [ ] Notificaciones push
- [ ] Dashboard de estadísticas de envío
- [ ] API REST para integración externa

---

**🚀 Email Reports Addon v1.0.0** - *Creando el futuro de los reportes automatizados*