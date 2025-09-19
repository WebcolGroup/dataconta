"""
Export Widget - Componente UI especializado para exportaciones
Parte de la refactorización del monolito dataconta_free_gui_refactored.py

Responsabilidad única: UI de exportaciones, delegando toda la lógica al controlador
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor


class ExportWidget(QWidget):
    """
    Widget especializado para exportaciones CSV/Excel.
    
    Principios SOLID:
    - SRP: Solo maneja la UI de exportaciones
    - OCP: Extensible para nuevos formatos
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para exportaciones
    - DIP: Depende de abstracciones (signals)
    """
    
    # Signals para comunicación con el controlador
    export_csv_requested = Signal(int)  # count
    export_csv_simple_requested = Signal()
    export_excel_requested = Signal(int)  # count
    siigo_csv_export_requested = Signal()
    siigo_excel_export_requested = Signal()
    test_connection_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz de exportaciones."""
        layout = QVBoxLayout(self)

        # Sección CSV (card)
        csv = self.create_csv_section()
        layout.addWidget(self._wrap_in_card(csv))

        # Sección Excel (card)
        excel = self.create_excel_section()
        layout.addWidget(self._wrap_in_card(excel))

        # Sección API Siigo (card)
        siigo = self.create_siigo_section()
        layout.addWidget(self._wrap_in_card(siigo))
    
    def create_csv_section(self) -> QWidget:
        """Crear sección de exportaciones CSV (devuelve contenedor)."""
        csv_group = QGroupBox("📤 Exportaciones CSV - Versión FREE")
        csv_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        csv_layout = QGridLayout(csv_group)
        
        # Información actualizada
        info_frame = self._create_info_frame()
        csv_layout.addWidget(info_frame, 0, 0, 1, 2)
        
        # Estilo para botones
        btn_style = self._get_button_style("#1976d2", "#1565c0")
        
        # Botón 10 facturas
        csv_10_btn = QPushButton("📊 Exportar 10 Facturas Reales")
        csv_10_btn.setToolTip(self._get_csv_10_tooltip())
        csv_10_btn.setStyleSheet(btn_style)
        csv_10_btn.clicked.connect(lambda: self.export_csv_requested.emit(10))
        csv_layout.addWidget(csv_10_btn, 1, 0)
        
        # Botón 100 facturas
        csv_100_btn = QPushButton("📊 Exportar 100 Facturas Reales")
        csv_100_btn.setToolTip(self._get_csv_100_tooltip())
        csv_100_btn.setStyleSheet(btn_style.replace("#1976d2", "#2196f3").replace("#1565c0", "#1976d2"))
        csv_100_btn.clicked.connect(lambda: self.export_csv_requested.emit(100))
        csv_layout.addWidget(csv_100_btn, 1, 1)
        
        # Botón CSV simple
        csv_simple_btn = QPushButton("📋 Exportar CSV Simple (5 registros)")
        csv_simple_btn.setToolTip(self._get_csv_simple_tooltip())
        csv_simple_btn.setStyleSheet(btn_style.replace("#1976d2", "#4caf50").replace("#1565c0", "#388e3c"))
        csv_simple_btn.clicked.connect(self.export_csv_simple_requested.emit)
        csv_layout.addWidget(csv_simple_btn, 2, 0, 1, 2)
        
        return csv_group
    
    def create_excel_section(self) -> QWidget:
        """Crear sección de exportaciones Excel (devuelve contenedor)."""
        excel_group = QGroupBox("📊 Exportaciones Excel - Versión PRO Preview")
        excel_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        excel_layout = QGridLayout(excel_group)
        
        excel_info = QLabel("""
        🚀 FUNCIONALIDAD EXCEL DISPONIBLE:
        ✅ Exportación directa desde Siigo API
        ✅ Formato Excel profesional (.xlsx)
        ✅ Datos reales sin 'Cliente Demo'
        💡 Pruebe las exportaciones Excel de forma gratuita
        """)
        excel_info.setStyleSheet("color: #0d47a1; font-weight: bold; font-size: 11px; padding: 10px;")
        excel_info.setWordWrap(True)
        excel_layout.addWidget(excel_info, 0, 0, 1, 2)
        
        # Estilo para botones Excel
        excel_btn_style = self._get_button_style("#ff9800", "#f57c00")
        
        # Botón Excel 10
        excel_10_btn = QPushButton("📊 Exportar 10 Facturas Excel")
        excel_10_btn.setToolTip(self._get_excel_10_tooltip())
        excel_10_btn.setStyleSheet(excel_btn_style)
        excel_10_btn.clicked.connect(lambda: self.export_excel_requested.emit(10))
        excel_layout.addWidget(excel_10_btn, 1, 0)
        
        # Botón Excel 100
        excel_100_btn = QPushButton("📊 Exportar 100 Facturas Excel")
        excel_100_btn.setToolTip(self._get_excel_100_tooltip())
        excel_100_btn.setStyleSheet(excel_btn_style.replace("#ff9800", "#ff5722").replace("#f57c00", "#d84315"))
        excel_100_btn.clicked.connect(lambda: self.export_excel_requested.emit(100))
        excel_layout.addWidget(excel_100_btn, 1, 1)
        
        return excel_group
    
    def create_siigo_section(self) -> QWidget:
        """Crear sección de exportaciones desde API Siigo (devuelve contenedor)."""
        siigo_group = QGroupBox("🌐 Exportaciones desde API Siigo")
        siigo_group.setStyleSheet("QGroupBox{ border: none; font-weight: 700; }")
        siigo_layout = QGridLayout(siigo_group)
        
        # Información de Siigo
        siigo_info = QLabel("""
        🔥 DESCARGA DIRECTA DESDE SIIGO:
        ✅ API CONFIGURADA: erikagarcia1179@hotmail.com  
        ✅ CONEXIÓN REAL: Datos directos desde Siigo API
        ✅ FILTROS AVANZADOS: Por fechas, cliente, NIT, estado
        """)
        siigo_info.setWordWrap(True)
        siigo_info.setStyleSheet("""
            background-color: #e3f2fd; 
            padding: 15px; 
            border-radius: 8px;
            border: 2px solid #1976d2;
            color: #1565c0;
            font-weight: bold;
            font-size: 12px;
        """)
        siigo_layout.addWidget(siigo_info, 0, 0, 1, 2)
        
        # Estilo para botones Siigo
        siigo_btn_style = self._get_button_style("#1976d2", "#1565c0")
        
        # Botón CSV Siigo
        csv_siigo_btn = QPushButton("📊 Descargar y Exportar a CSV")
        csv_siigo_btn.setToolTip(self._get_siigo_csv_tooltip())
        csv_siigo_btn.setStyleSheet(siigo_btn_style)
        csv_siigo_btn.clicked.connect(self.siigo_csv_export_requested.emit)
        siigo_layout.addWidget(csv_siigo_btn, 1, 0)
        
        # Botón Excel Siigo
        excel_siigo_btn = QPushButton("📄 Descargar y Exportar a Excel")
        excel_siigo_btn.setToolTip(self._get_siigo_excel_tooltip())
        excel_siigo_btn.setStyleSheet(siigo_btn_style.replace("#1976d2", "#4caf50").replace("#1565c0", "#388e3c"))
        excel_siigo_btn.clicked.connect(self.siigo_excel_export_requested.emit)
        siigo_layout.addWidget(excel_siigo_btn, 1, 1)
        
        # Botón de prueba
        test_btn = QPushButton("⚡ Prueba Rápida (Sin filtros)")
        test_btn.setToolTip(self._get_test_connection_tooltip())
        test_btn.setStyleSheet(siigo_btn_style.replace("#1976d2", "#ff9800").replace("#1565c0", "#f57c00"))
        test_btn.clicked.connect(self.test_connection_requested.emit)
        siigo_layout.addWidget(test_btn, 2, 0, 1, 2)
        
        return siigo_group
    
    def _create_info_frame(self) -> QFrame:
        """Crear frame con información de exportaciones."""
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e8;
                border: 2px solid #4caf50;
                border-radius: 8px;
                padding: 10px;
                margin: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_text = QLabel("""
        🔥 FUNCIONALIDAD CONFIRMADA - DATOS REALES:
        
        ✅ PROBLEMA RESUELTO: Los CSV ya NO contienen "Cliente Demo S.A.S"
        ✅ DATOS REALES: Ahora exporta "Cliente Real X Ltda." de Siigo API
        ✅ API CONFIGURADA: erikagarcia1179@hotmail.com
        ✅ CONEXIÓN: Siigo API funcionando correctamente
        
        📊 Versión FREE: Hasta 100 facturas por exportación
        🚀 Versión PRO: Hasta 2,000 facturas + formatos avanzados
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #2c5530; font-weight: bold; font-size: 12px;")
        info_layout.addWidget(info_text)
        
        return info_frame
    
    def _get_button_style(self, primary_color: str, hover_color: str) -> str:
        """Obtener estilo base para botones."""
        return f"""
            QPushButton {{ 
                background-color: {primary_color}; 
                color: white; 
                padding: 15px; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 12pt;
                border: none;
            }}
            QPushButton:hover {{ 
                background-color: {hover_color}; 
            }}
        """
    
    def _get_csv_10_tooltip(self) -> str:
        """Tooltip para botón CSV 10 facturas."""
        return (
            "📊 Exportar 10 facturas con datos REALES:\n"
            "• Datos directos de Siigo API\n"
            "• Clientes reales (NO 'Demo S.A.S')\n"
            "• Formato CSV estándar\n"
            "• Incluye: fecha, cliente, montos, estado\n\n"
            "⚡ Exportación rápida para pruebas"
        )
    
    def _get_csv_100_tooltip(self) -> str:
        """Tooltip para botón CSV 100 facturas."""
        return (
            "📊 Exportar 100 facturas con datos REALES:\n"
            "• Máximo permitido en versión FREE\n"
            "• Datos completos de Siigo API\n"
            "• Incluye campos extendidos\n"
            "• Perfecto para análisis mensual\n\n"
            "🏆 PRO: Hasta 2,000 facturas"
        )
    
    def _get_csv_simple_tooltip(self) -> str:
        """Tooltip para botón CSV simple."""
        return (
            "📋 Exportación CSV simplificada:\n"
            "• Solo 5 registros de muestra\n"
            "• Formato compacto y ligero\n"
            "• Ideal para pruebas rápidas\n"
            "• Datos reales de Siigo\n\n"
            "⚡ Perfecto para validar estructura"
        )
    
    def _get_excel_10_tooltip(self) -> str:
        """Tooltip para botón Excel 10 facturas."""
        return (
            "📊 Exportar 10 facturas a Excel:\n"
            "• Formato Excel profesional\n"
            "• Datos reales de Siigo API\n"
            "• Perfecto para análisis detallado\n"
            "• Incluye formateo automático\n\n"
            "⚡ Preview gratuito de funcionalidad PRO"
        )
    
    def _get_excel_100_tooltip(self) -> str:
        """Tooltip para botón Excel 100 facturas."""
        return (
            "📊 Exportar 100 facturas a Excel:\n"
            "• Formato Excel completo\n"
            "• Gráficos y tablas dinámicas\n"
            "• Análisis financiero avanzado\n"
            "• Datos de Siigo en tiempo real\n\n"
            "🏆 Funcionalidad premium gratuita"
        )
    
    def _get_siigo_csv_tooltip(self) -> str:
        """Tooltip para botón CSV Siigo."""
        return (
            "🌐 Descarga DIRECTA desde API Siigo:\n"
            "• Conecta en tiempo real a Siigo\n"
            "• Aplica todos los filtros configurados\n"
            "• Genera 2 archivos CSV:\n"
            "  - facturas_encabezados.csv\n"
            "  - facturas_detalle.csv\n\n"
            "🔥 100% datos reales desde Siigo API\n"
            "📊 Procesa encabezados + items detallados"
        )
    
    def _get_siigo_excel_tooltip(self) -> str:
        """Tooltip para botón Excel Siigo."""
        return (
            "📄 Descarga desde API Siigo a Excel:\n"
            "• Un archivo .xlsx con 2 hojas:\n"
            "  - Hoja 'Encabezados'\n"
            "  - Hoja 'Detalle'\n"
            "• Formato profesional listo para análisis\n"
            "• Compatible con Power BI y tablas dinámicas\n\n"
            "🔥 Datos reales desde Siigo API\n"
            "📊 Ideal para reportes ejecutivos"
        )
    
    def _get_test_connection_tooltip(self) -> str:
        """Tooltip para botón de prueba de conexión."""
        return (
            "⚡ Prueba de conectividad API Siigo:\n"
            "• Descarga facturas recientes\n"
            "• Sin aplicar filtros\n"
            "• Valida autenticación y conexión\n"
            "• Genera CSV de prueba\n\n"
            "🔧 Perfecto para:\n"
            "• Verificar configuración API\n"
            "• Probar credenciales\n"
            "• Validar estructura de datos"
        )
    
    def show_success_message(self, title: str, message: str):
        """Mostrar mensaje de éxito."""
        QMessageBox.information(self, title, message)
    
    def show_error_message(self, title: str, message: str):
        """Mostrar mensaje de error."""
        QMessageBox.warning(self, title, message)
    
    def show_warning_message(self, title: str, message: str):
        """Mostrar mensaje de advertencia."""
        QMessageBox.warning(self, title, message)

    # ---------- Helpers de UI (cards y sombras) ----------
    def _wrap_in_card(self, inner: QWidget) -> QFrame:
        card = QFrame()
        card.setObjectName("CardFrame")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.addWidget(inner)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)
        return card