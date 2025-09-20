"""
Demo Handler Widget - Componente UI especializado para manejar demostraciones
Parte de la refactorización para desacoplar métodos de demo del archivo principal

Responsabilidad única: Manejar todas las demostraciones y mensajes de upgrade
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import QObject, Signal


class DemoHandlerWidget(QWidget):
    """
    Widget especializado para manejar demostraciones y upgrades.
    
    Principios SOLID:
    - SRP: Solo maneja demos y mensajes informativos
    - OCP: Extensible para nuevos tipos de demo
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para demos
    - DIP: Depende de abstracciones (signals)
    """
    
    # Signals para comunicación externa si es necesario
    demo_completed = Signal(str, str)  # tipo_demo, resultado
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz del demo handler (puede estar vacía)."""
        # Este widget es principalmente lógico, no requiere UI visual
        pass
    
    # ==================== Métodos de Demo Principales ====================
    
    def show_top_clients_demo(self):
        """Mostrar demo de TOP clientes."""
        title = "TOP Clientes"
        message = ("🏆 TOP 10 Clientes - Funcionalidad desde widget especializado\n\n"
                  "📊 DEMO - Análisis de Clientes Principales:\n"
                  "• Cliente A: $2,450,000 (23% del total)\n"
                  "• Cliente B: $1,890,000 (18% del total)\n"
                  "• Cliente C: $1,230,000 (12% del total)\n"
                  "• Cliente D: $987,000 (9% del total)\n"
                  "• Cliente E: $756,000 (7% del total)\n\n"
                  "💡 En DataConta PRO:\n"
                  "• Análisis detallado por segmento\n"
                  "• Predicciones de comportamiento\n"
                  "• Alertas de riesgo de churn\n"
                  "• Recomendaciones personalizadas")
        
        QMessageBox.information(self.parent(), title, message)
        self.demo_completed.emit("top_clients", "success")
    
    def show_pro_upgrade_demo(self):
        """Mostrar demo de información de upgrade."""
        title = "DataConta PRO"
        message = ("🚀 Upgrade desde componente especializado\n\n"
                  "✨ FUNCIONALIDADES PRO DISPONIBLES:\n"
                  "• Hasta 2,000 facturas procesables\n"
                  "• Dashboard BI interactivo\n"
                  "• Arquitectura modular\n"
                  "• Componentes reutilizables\n\n"
                  "📊 ANÁLISIS AVANZADOS:\n"
                  "• Predicciones con Machine Learning\n"
                  "• Detección automática de anomalías\n"
                  "• Reportes financieros ejecutivos\n"
                  "• Integración con sistemas ERP\n\n"
                  "💰 PLANES DISPONIBLES:\n"
                  "💼 PRO: $29/mes - Ideal para pequeñas empresas\n"
                  "🏢 ENTERPRISE: $99/mes - Para corporaciones\n\n"
                  "📞 Contacto: ventas@dataconta.com\n"
                  "🌐 Web: www.dataconta.com/upgrade")
        
        QMessageBox.information(self.parent(), title, message)
        self.demo_completed.emit("pro_upgrade", "success")
    
    def show_invoice_search_demo(self, filters: Dict[str, Any]) -> list:
        """Generar datos demo para búsqueda de facturas."""
        demo_invoices = [
            {
                "numero": "DEMO-001",
                "fecha": "2025-01-18",
                "cliente": "Cliente Demo 1",
                "monto": 1500000,
                "estado": "PAGADA"
            },
            {
                "numero": "DEMO-002", 
                "fecha": "2025-01-17",
                "cliente": "Cliente Demo 2",
                "monto": 2300000,
                "estado": "PENDIENTE"
            },
            {
                "numero": "DEMO-003",
                "fecha": "2025-01-16", 
                "cliente": "Cliente Demo 3",
                "monto": 890000,
                "estado": "VENCIDA"
            },
            {
                "numero": "DEMO-004",
                "fecha": "2025-01-15",
                "cliente": "Cliente Demo 4", 
                "monto": 3200000,
                "estado": "PAGADA"
            }
        ]
        
        # Aplicar filtros demo si están presentes
        filtered_invoices = self._apply_demo_filters(demo_invoices, filters)
        
        self.demo_completed.emit("invoice_search", f"found_{len(filtered_invoices)}_invoices")
        return filtered_invoices
    
    def show_siigo_connection_demo(self):
        """Mostrar demo de prueba de conexión Siigo."""
        title = "Prueba de Conexión"
        message = ("🌐 Conexión con API Siigo verificada correctamente\n\n"
                  "✅ ESTADO DE CONEXIÓN:\n"
                  "• Servidor: siigo.com ✓\n"
                  "• Autenticación: Válida ✓\n"
                  "• API Version: v1.3.2 ✓\n"
                  "• Rate Limit: 1000/hora ✓\n\n"
                  "📊 DATOS DISPONIBLES:\n"
                  "• Facturas: 1,247 registros\n"
                  "• Clientes: 342 registros\n"
                  "• Productos: 89 registros\n\n"
                  "🔥 FUNCIONALIDADES ACTIVAS:\n"
                  "• Descarga en tiempo real ✓\n"
                  "• Filtros avanzados ✓\n"
                  "• Exportación dual (CSV + Excel) ✓\n"
                  "• Sincronización automática ✓")
        
        QMessageBox.information(self.parent(), title, message)
        self.demo_completed.emit("siigo_connection", "success")
    
    def show_clear_filters_demo(self):
        """Mostrar demo de limpieza de filtros."""
        title = "Filtros"
        message = ("🧹 Filtros limpiados correctamente\n\n"
                  "✅ FILTROS REINICIADOS:\n"
                  "• Fechas: Restauradas al período actual\n"
                  "• Cliente: Todos seleccionados\n"
                  "• Estado: Sin filtro aplicado\n"
                  "• Monto: Rango completo\n\n"
                  "💡 CONSEJO PRO:\n"
                  "Use filtros específicos para obtener\n"
                  "resultados más precisos y relevantes.")
        
        QMessageBox.information(self.parent(), title, message)
        self.demo_completed.emit("clear_filters", "success")
    
    def show_export_success_demo(self, export_type: str):
        """Mostrar demo de éxito en exportación."""
        export_messages = {
            "csv": ("📊 Exportación CSV desde API Siigo completada\n\n"
                   "✅ ARCHIVOS GENERADOS:\n"
                   "• facturas_encabezados.csv (1,247 registros)\n"
                   "• facturas_detalle.csv (3,891 items)\n\n"
                   "📂 UBICACIÓN: ./outputs/\n"
                   "💾 TAMAÑO TOTAL: 2.3 MB\n"
                   "⏱️ TIEMPO: 3.2 segundos"),
            
            "excel": ("📄 Exportación Excel desde API Siigo completada\n\n"
                     "✅ ARCHIVO GENERADO:\n"
                     "• facturas_siigo.xlsx\n"
                     "• Hoja 'Encabezados' (1,247 registros)\n"
                     "• Hoja 'Detalle' (3,891 items)\n\n"
                     "📊 FORMATO: Professional Excel\n"
                     "📂 UBICACIÓN: ./outputs/\n"
                     "💾 TAMAÑO: 1.8 MB\n"
                     "⏱️ TIEMPO: 4.1 segundos"),
            
            "simple": ("💾 Exportación simple completada\n\n"
                      "✅ ARCHIVO GENERADO:\n"
                      "• facturas_simple.csv (100 registros)\n\n"
                      "📂 UBICACIÓN: ./outputs/\n"
                      "💾 TAMAÑO: 45 KB\n"
                      "⏱️ TIEMPO: 0.8 segundos")
        }
        
        message = export_messages.get(export_type, f"Exportación {export_type} completada correctamente")
        QMessageBox.information(self.parent(), "Éxito", message)
        self.demo_completed.emit(f"export_{export_type}", "success")
    
    def show_export_error_demo(self, error_message: str):
        """Mostrar demo de error en exportación."""
        title = "Error"
        full_message = (f"❌ ERROR EN EXPORTACIÓN:\n{error_message}\n\n"
                       "🔧 POSIBLES SOLUCIONES:\n"
                       "• Verificar conexión a internet\n"
                       "• Comprobar credenciales de API\n"
                       "• Revisar permisos de escritura\n"
                       "• Contactar soporte técnico\n\n"
                       "📞 Soporte: soporte@dataconta.com")
        
        QMessageBox.warning(self.parent(), title, full_message)
        self.demo_completed.emit("export_error", error_message)
    
    # ==================== Métodos de Utilidad ====================
    
    def _apply_demo_filters(self, invoices: list, filters: Dict[str, Any]) -> list:
        """Aplicar filtros demo a la lista de facturas."""
        if not filters:
            return invoices
        
        filtered = invoices.copy()
        
        # Filtro por estado (ejemplo)
        if filters.get('estado') and filters['estado'] != 'todos':
            filtered = [inv for inv in filtered if inv['estado'].lower() == filters['estado'].lower()]
        
        # Filtro por monto mínimo (ejemplo)
        if filters.get('monto_min'):
            try:
                min_amount = float(filters['monto_min'])
                filtered = [inv for inv in filtered if inv['monto'] >= min_amount]
            except (ValueError, TypeError):
                pass
        
        return filtered
    
    def get_demo_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas demo para el dashboard."""
        return {
            "num_facturas": 1247,
            "ventas_totales_mes": 15750000,
            "top_cliente": "Empresa ABC S.A.S",
            "ticket_promedio": 12630.50,
            "ventas_totales": 189300000,
            "facturas_pagadas": 1089,
            "facturas_pendientes": 158,
            "mejor_mes": "Marzo 2025"
        }
    
    def show_custom_demo(self, title: str, message: str, demo_type: str = "info"):
        """Mostrar demo personalizado."""
        if demo_type == "warning":
            QMessageBox.warning(self.parent(), title, message)
        elif demo_type == "error":
            QMessageBox.critical(self.parent(), title, message)
        else:
            QMessageBox.information(self.parent(), title, message)
        
        self.demo_completed.emit("custom_demo", demo_type)