"""
GUI User Interface for DATACONTA application using PySide6.
"""

from typing import List, Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QDateEdit,
    QProgressBar, QMessageBox, QGroupBox, QFormLayout, QTabWidget,
    QScrollArea, QFrame, QMenuBar, QMenu, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPalette

from src.application.ports.interfaces import UserInterface, Logger
from src.domain.entities.invoice import Invoice, InvoiceFilter
from src.infrastructure.config.dynamic_menu_config import DynamicMenuManager


class DataContaMainWindow(QMainWindow):
    """Main window for DATACONTA GUI application."""
    
    def __init__(self, logger: Logger, license_manager=None):
        super().__init__()
        self._logger = logger
        self._license_manager = license_manager
        self.setWindowTitle("DATACONTA - Sistema Avanzado de Gestión")
        self.setMinimumSize(1000, 700)
        
        # Inicializar gestor de menús dinámico
        self.menu_manager = DynamicMenuManager("menu_config.json")
        self.menu_manager.set_parent_window(self)
        self.menu_manager.load_config()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header Section
        self._setup_header(layout)
        
        # License Status
        self._setup_license_status(layout)
        
        # Main Menu Sections
        self._setup_main_menu(layout)
        
        # Output Section
        self._setup_output_section(layout)
        
        # Status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def _setup_header(self, layout):
        """Setup the header section."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Box)
        
        # Cambiar color de header según licencia
        if self._is_free_license():
            header_frame.setStyleSheet("QFrame { background-color: #27ae60; color: white; padding: 10px; }")
            title_text = "🆓 DATACONTA FREE - VERSIÓN GRATUITA"
            subtitle_text = "Funcionalidades básicas | Límite: 500 facturas por consulta"
        else:
            header_frame.setStyleSheet("QFrame { background-color: #2c3e50; color: white; padding: 10px; }")
            title_text = "🏢 DATACONTA - SISTEMA AVANZADO DE MENÚS"
            subtitle_text = "Interfaz Gráfica PySide6 | Arquitectura Hexagonal | Principios SOLID"
        
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel(title_text)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #ecf0f1; font-size: 10pt;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def _setup_license_status(self, layout):
        """Setup license status section with dynamic menu."""
        self.license_frame = QFrame()
        self.license_frame.setFrameStyle(QFrame.Box)
        self.license_frame.setStyleSheet("QFrame { background-color: #27ae60; color: white; padding: 8px; }")
        
        license_layout = QVBoxLayout(self.license_frame)
        
        # Crear menú horizontal dinámico
        menu_layout = QHBoxLayout()
        
        # Crear botones de menú dinámicamente
        menu_buttons = self.menu_manager.create_menu_buttons()
        for button in menu_buttons:
            menu_layout.addWidget(button)
        
        menu_layout.addStretch()  # Para empujar el resto hacia la derecha
        
        # Status de licencia
        license_status_layout = QHBoxLayout()
        self.license_label = QLabel("📄 Licencia actual: 💼 Profesional")
        self.license_label.setStyleSheet("color: white; font-weight: bold;")
        license_status_layout.addWidget(self.license_label)
        
        # Agregar ambos layouts al frame principal
        license_layout.addLayout(menu_layout)
        license_layout.addLayout(license_status_layout)
        
        layout.addWidget(self.license_frame)
    
    def reload_dynamic_menu(self):
        """Recargar configuración de menú dinámico."""
        if hasattr(self, 'menu_manager'):
            self.menu_manager.reload_config()
            # Recrear la sección de licencia/menú
            # Nota: Para una recarga completa, sería necesario recrear toda la interfaz
            self._logger.info("Configuración de menú recargada")
    
    def add_menu_category_runtime(self, category_id: str, config: dict):
        """Agregar categoría de menú en tiempo de ejecución."""
        if hasattr(self, 'menu_manager'):
            success = self.menu_manager.add_menu_category(category_id, config)
            if success:
                self._logger.info(f"Categoría {category_id} agregada exitosamente")
                return True
            else:
                self._logger.error(f"Error agregando categoría {category_id}")
                return False
        return False
    
    def remove_menu_category_runtime(self, category_id: str):
        """Remover categoría de menú en tiempo de ejecución."""
        if hasattr(self, 'menu_manager'):
            success = self.menu_manager.remove_menu_category(category_id)
            if success:
                self._logger.info(f"Categoría {category_id} removida exitosamente")
                return True
            else:
                self._logger.error(f"Error removiendo categoría {category_id}")
                return False
        return False
    
    def _setup_main_menu(self, layout):
        """Setup the main menu sections."""
        # Create scroll area for menu
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        if self._is_free_license():
            # FREE version - GUI Lite
            self._setup_free_statistics_section(scroll_layout, 0, 0)
            self._setup_free_query_section(scroll_layout, 0, 1)
            self._setup_free_export_section(scroll_layout, 1, 0)
            self._setup_blocked_features_section(scroll_layout, 1, 1)
        else:
            # Full version
            self._setup_business_intelligence_section(scroll_layout, 0, 0)
            self._setup_reports_section(scroll_layout, 0, 1)
            self._setup_tools_section(scroll_layout, 1, 0)
            self._setup_ollama_section(scroll_layout, 1, 1)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
    def _setup_business_intelligence_section(self, layout, row, col):
        """Setup Business Intelligence section."""
        bi_group = QGroupBox("📊 Business Intelligence")
        bi_group.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
        bi_layout = QVBoxLayout(bi_group)
        
        # Description
        desc_label = QLabel("📝 Herramientas de análisis de datos y consultas")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        bi_layout.addWidget(desc_label)
        
        # Buttons
        self.get_invoices_btn = QPushButton("📋 Consultar Facturas de Venta")
        self.get_invoices_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; color: white; 
                padding: 10px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        bi_layout.addWidget(self.get_invoices_btn)
        
        self.export_bi_btn = QPushButton("🏢 Exportar a Business Intelligence")
        self.export_bi_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; color: white; 
                padding: 10px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        bi_layout.addWidget(self.export_bi_btn)
        
        layout.addWidget(bi_group, row, col)
    
    def _setup_reports_section(self, layout, row, col):
        """Setup Reports section."""
        reports_group = QGroupBox("📈 Generación de Informes")
        reports_group.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
        reports_layout = QVBoxLayout(reports_group)
        
        # Description
        desc_label = QLabel("📝 Sistema completo de informes empresariales")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        reports_layout.addWidget(desc_label)
        
        # Financial Reports Buttons
        self.financial_reports_btn = QPushButton("💰 Estado de Resultados")
        self.financial_reports_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e67e22; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        reports_layout.addWidget(self.financial_reports_btn)
        
        self.balance_general_btn = QPushButton("🏦 Estado de Situación Financiera")
        self.balance_general_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e67e22; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        reports_layout.addWidget(self.balance_general_btn)
        
        self.operational_reports_btn = QPushButton("🏭 Informes Operativos")
        self.operational_reports_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e67e22; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        reports_layout.addWidget(self.operational_reports_btn)
        
        self.compliance_reports_btn = QPushButton("🔍 Informes de Cumplimiento")
        self.compliance_reports_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e67e22; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        reports_layout.addWidget(self.compliance_reports_btn)
        
        self.management_reports_btn = QPushButton("👔 Informes Gerenciales")
        self.management_reports_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e67e22; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        reports_layout.addWidget(self.management_reports_btn)
        
        self.view_files_btn = QPushButton("📁 Ver Archivos de Salida")
        self.view_files_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e67e22; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        reports_layout.addWidget(self.view_files_btn)
        
        self.export_csv_btn = QPushButton("📤 Exportar Facturas a CSV")
        self.export_csv_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e67e22; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        reports_layout.addWidget(self.export_csv_btn)
        
        layout.addWidget(reports_group, row, col)
    
    def _setup_tools_section(self, layout, row, col):
        """Setup Tools section."""
        tools_group = QGroupBox("🛠️ Herramientas")
        tools_group.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
        tools_layout = QVBoxLayout(tools_group)
        
        # Description
        desc_label = QLabel("📝 Utilidades y herramientas de sistema")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        tools_layout.addWidget(desc_label)
        
        # Buttons
        self.check_api_btn = QPushButton("🔍 Verificar Estado de la API")
        self.check_api_btn.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; color: white; 
                padding: 10px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #229954; }
        """)
        tools_layout.addWidget(self.check_api_btn)
        
        self.config_btn = QPushButton("⚙️ Configuración del Sistema")
        self.config_btn.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; color: white; 
                padding: 10px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #229954; }
        """)
        tools_layout.addWidget(self.config_btn)
        
        layout.addWidget(tools_group, row, col)
    
    def _setup_ollama_section(self, layout, row, col):
        """Setup Ollama section."""
        ollama_group = QGroupBox("🤖 Integración con Ollama")
        ollama_group.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
        ollama_layout = QVBoxLayout(ollama_group)
        
        # Description
        desc_label = QLabel("📝 Integración con modelos de IA local")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        ollama_layout.addWidget(desc_label)
        
        # Buttons
        self.send_ollama_btn = QPushButton("📤 Enviar Datos a Ollama")
        self.send_ollama_btn.setStyleSheet("""
            QPushButton { 
                background-color: #8e44ad; color: white; 
                padding: 10px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #7d3c98; }
        """)
        ollama_layout.addWidget(self.send_ollama_btn)
        
        self.query_ollama_btn = QPushButton("💬 Consultar Respuesta de Ollama")
        self.query_ollama_btn.setStyleSheet("""
            QPushButton { 
                background-color: #8e44ad; color: white; 
                padding: 10px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #7d3c98; }
        """)
        ollama_layout.addWidget(self.query_ollama_btn)
        
        layout.addWidget(ollama_group, row, col)
    
    def _setup_output_section(self, layout):
        """Setup output section."""
        output_group = QGroupBox("📋 Registro de Actividades")
        output_group.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)
        self.output_text.setStyleSheet("""
            QTextEdit { 
                background-color: #ecf0f1; 
                border: 1px solid #bdc3c7; 
                font-family: 'Courier New', monospace; 
                font-size: 9pt; 
            }
        """)
        output_layout.addWidget(self.output_text)
        
        # Exit button
        self.exit_btn = QPushButton("🚪 Salir")
        self.exit_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e74c3c; color: white; 
                padding: 10px; margin: 5px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        output_layout.addWidget(self.exit_btn)
        
        layout.addWidget(output_group)
    
    def update_license_status(self, license_type: str):
        """Update license status display."""
        license_icons = {
            "FREE": "🆓",
            "PROFESSIONAL": "💼",
            "PRO": "💼", 
            "ENTERPRISE": "🏢"
        }
        
        icon = license_icons.get(license_type.upper(), "📄")
        self.license_label.setText(f"📄 Licencia actual: {icon} {license_type}")
    
    def log_message(self, message: str):
        """Add a message to the output text area."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.output_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def show_progress(self, show: bool = True):
        """Show or hide the progress bar."""
        self.progress_bar.setVisible(show)
    
    def show_error(self, title: str, message: str):
        """Show an error dialog."""
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str):
        """Show an info dialog."""
        QMessageBox.information(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """Show a warning dialog."""
        QMessageBox.warning(self, title, message)
    
    # ========================================================================================
    # FREE LICENSE HELPER METHODS
    # ========================================================================================
    
    def _is_free_license(self) -> bool:
        """Check if current license is FREE."""
        if self._license_manager:
            return self._license_manager.get_license_type() == "FREE"
        return True  # Default to FREE if no license manager
    
    def _show_blocked_feature_dialog(self, feature_name: str):
        """Show dialog for blocked feature."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Función Bloqueada")
        msg.setText(f"🔒 {feature_name}")
        msg.setInformativeText("Esta funcionalidad está disponible solo en Profesional o Enterprise.")
        
        upgrade_btn = msg.addButton("💼 Actualizar a PRO", QMessageBox.AcceptRole)
        cancel_btn = msg.addButton("Cancelar", QMessageBox.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == upgrade_btn:
            self._show_upgrade_info()
    
    def _show_upgrade_info(self):
        """Show upgrade information dialog."""
        info_msg = QMessageBox(self)
        info_msg.setIcon(QMessageBox.Information)
        info_msg.setWindowTitle("Información de Upgrade")
        info_msg.setText("💼 DATACONTA PROFESIONAL")
        info_msg.setInformativeText(
            "✨ Funcionalidades PRO:\n"
            "• Informes financieros avanzados\n"
            "• Exportación BI completa\n"
            "• Análisis de tendencias\n"
            "• Dashboard completo\n"
            "• Sin límite de facturas\n\n"
            "📧 Contacte a soporte para más información."
        )
        info_msg.exec()
    
    # ========================================================================================
    # FREE VERSION GUI SECTIONS
    # ========================================================================================
    
    def _setup_free_statistics_section(self, layout, row, col):
        """Setup statistics section for FREE version."""
        stats_group = QGroupBox("📊 Estadísticas Básicas (FREE)")
        stats_group.setStyleSheet("QGroupBox { font-weight: bold; color: #27ae60; }")
        stats_layout = QVBoxLayout(stats_group)
        
        # Description
        desc_label = QLabel("📝 Métricas básicas de su negocio")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        stats_layout.addWidget(desc_label)
        
        # Statistics display area
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(120)
        self.stats_display.setStyleSheet("""
            QTextEdit { 
                background-color: #f8f9fa; 
                border: 1px solid #27ae60; 
                font-family: 'Arial', sans-serif; 
                font-size: 9pt;
                padding: 8px;
            }
        """)
        self.stats_display.setText("📈 Haga clic en 'Actualizar' para ver sus estadísticas")
        stats_layout.addWidget(self.stats_display)
        
        # Update button
        self.update_stats_btn = QPushButton("🔄 Actualizar Estadísticas")
        self.update_stats_btn.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #229954; }
        """)
        stats_layout.addWidget(self.update_stats_btn)
        
        layout.addWidget(stats_group, row, col)
    
    def _setup_free_query_section(self, layout, row, col):
        """Setup query section for FREE version."""
        query_group = QGroupBox("📋 Consulta de Facturas (FREE)")
        query_group.setStyleSheet("QGroupBox { font-weight: bold; color: #27ae60; }")
        query_layout = QVBoxLayout(query_group)
        
        # Description with limit
        desc_label = QLabel("📝 Consultar facturas (Límite: 500 facturas)")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        query_layout.addWidget(desc_label)
        
        # Query button
        self.query_invoices_btn = QPushButton("📋 Consultar Facturas")
        self.query_invoices_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; color: white; 
                padding: 10px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        query_layout.addWidget(self.query_invoices_btn)
        
        # API status button
        self.check_api_btn = QPushButton("🔍 Verificar Estado de la API")
        self.check_api_btn.setStyleSheet("""
            QPushButton { 
                background-color: #17a2b8; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #138496; }
        """)
        query_layout.addWidget(self.check_api_btn)
        
        layout.addWidget(query_group, row, col)
    
    def _setup_free_export_section(self, layout, row, col):
        """Setup export section for FREE version."""
        export_group = QGroupBox("📤 Exportación Simple (FREE)")
        export_group.setStyleSheet("QGroupBox { font-weight: bold; color: #27ae60; }")
        export_layout = QVBoxLayout(export_group)
        
        # Description
        desc_label = QLabel("📝 Exportación básica de datos")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        export_layout.addWidget(desc_label)
        
        # JSON export button
        self.export_json_btn = QPushButton("📄 Exportar a JSON")
        self.export_json_btn.setStyleSheet("""
            QPushButton { 
                background-color: #fd7e14; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #e8650e; }
        """)
        export_layout.addWidget(self.export_json_btn)
        
        # CSV export button
        self.export_csv_simple_btn = QPushButton("📊 Exportar CSV Simple")
        self.export_csv_simple_btn.setStyleSheet("""
            QPushButton { 
                background-color: #20c997; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #1aa085; }
        """)
        export_layout.addWidget(self.export_csv_simple_btn)
        
        # View files button
        self.view_files_btn = QPushButton("📁 Ver Archivos")
        self.view_files_btn.setStyleSheet("""
            QPushButton { 
                background-color: #6f42c1; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #5a359a; }
        """)
        export_layout.addWidget(self.view_files_btn)
        
        layout.addWidget(export_group, row, col)
    
    def _setup_blocked_features_section(self, layout, row, col):
        """Setup blocked features section for FREE version."""
        blocked_group = QGroupBox("🔒 Funciones Avanzadas (PRO/ENTERPRISE)")
        blocked_group.setStyleSheet("QGroupBox { font-weight: bold; color: #dc3545; }")
        blocked_layout = QVBoxLayout(blocked_group)
        
        # Description
        desc_label = QLabel("📝 Funcionalidades disponibles en versiones de pago")
        desc_label.setStyleSheet("color: #6c757d; font-size: 9pt;")
        blocked_layout.addWidget(desc_label)
        
        # Blocked buttons
        blocked_buttons = [
            ("🔒 Informes Financieros", "Informes Financieros Avanzados"),
            ("🔒 Business Intelligence", "Exportación BI Completa"),
            ("🔒 Dashboard Completo", "Dashboard Ejecutivo"),
            ("🔒 Análisis Predictivo", "Análisis con IA"),
        ]
        
        for btn_text, feature_name in blocked_buttons:
            blocked_btn = QPushButton(btn_text)
            blocked_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #6c757d; color: white; 
                    padding: 8px; margin: 2px; 
                    font-weight: bold; border: none; border-radius: 4px; 
                }
                QPushButton:hover { background-color: #5a6268; }
            """)
            # Connect to blocked feature handler
            blocked_btn.clicked.connect(lambda checked, name=feature_name: self._show_blocked_feature_dialog(name))
            blocked_layout.addWidget(blocked_btn)
        
        # Upgrade button
        upgrade_btn = QPushButton("💼 ¡Actualizar a PRO!")
        upgrade_btn.setStyleSheet("""
            QPushButton { 
                background-color: #28a745; color: white; 
                padding: 10px; margin: 5px; 
                font-weight: bold; border: none; border-radius: 4px; 
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        upgrade_btn.clicked.connect(self._show_upgrade_info)
        blocked_layout.addWidget(upgrade_btn)
        
        layout.addWidget(blocked_group, row, col)
    
    def update_free_statistics(self, stats_data: dict):
        """Update statistics display for FREE version."""
        if not stats_data:
            self.stats_display.setText("❌ No se pudieron obtener estadísticas")
            return
        
        stats_text = f"""📊 ESTADÍSTICAS BÁSICAS - DATACONTA FREE
        
🔢 Total de facturas consultadas: {stats_data.get('total_invoices', 0):,}
💰 Total vendido acumulado: ${stats_data.get('total_amount', 0):,.2f}
👥 Número de clientes distintos: {stats_data.get('unique_customers', 0):,}
📅 Facturas del mes actual: {stats_data.get('current_month_invoices', 0):,}
📈 Promedio por factura: ${stats_data.get('average_invoice_amount', 0):,.2f}

🆓 Licencia: FREE | 📊 Límite: 500 facturas por consulta
💡 Actualice a PRO para funcionalidades avanzadas
        """
        
        self.stats_display.setText(stats_text.strip())


class GUIUserInterfaceAdapter(UserInterface):
    """GUI adapter for user interface operations."""
    
    def __init__(self, logger: Logger, license_manager=None):
        self._logger = logger
        self._license_manager = license_manager
        self._main_window = None
    
    def set_main_window(self, main_window: DataContaMainWindow):
        """Set the main window reference."""
        self._main_window = main_window
    
    def show_menu(self) -> str:
        """Display GUI menu - not applicable for GUI."""
        return "gui_mode"
    
    def get_filter_parameters(self) -> Optional[InvoiceFilter]:
        """Get filter parameters from GUI - stub implementation."""
        return InvoiceFilter()
    
    def get_invoice_filters(self) -> InvoiceFilter:
        """Get invoice filters from user input."""
        return InvoiceFilter()
    
    def display_invoices(self, invoices: List[Invoice]) -> None:
        """Display invoices to user."""
        if self._main_window:
            self._main_window.log_message(f"Mostrando {len(invoices)} facturas")
            for invoice in invoices[:5]:  # Show first 5 invoices
                self._main_window.log_message(f"  - Factura {invoice.number}: {invoice.total}")
            if len(invoices) > 5:
                self._main_window.log_message(f"  ... y {len(invoices) - 5} facturas más")
    
    def display_message(self, message: str, level: str = 'info') -> None:
        """Display a message to the user."""
        if self._main_window:
            if level.lower() == 'error':
                self._main_window.log_message(f"ERROR: {message}")
            elif level.lower() == 'warning':
                self._main_window.log_message(f"ADVERTENCIA: {message}")
            else:
                self._main_window.log_message(f"INFO: {message}")
    
    def display_files(self, files: List[str]) -> None:
        """Display list of files to user."""
        if self._main_window:
            self._main_window.log_message("Archivos disponibles:")
            for file in files:
                self._main_window.log_message(f"  - {file}")
    
    def show_invoice_count(self, count: int, message: str = "") -> None:
        """Show invoice count in GUI."""
        if self._main_window:
            self._main_window.log_message(f"Total de facturas: {count}")
            if message:
                self._main_window.log_message(message)
    
    def show_invoices_summary(self, invoices: List[Invoice]) -> None:
        """Show invoices summary in GUI."""
        if self._main_window:
            self._main_window.log_message(f"Resumen de {len(invoices)} facturas obtenidas")
    
    def show_export_progress(self, current: int, total: int, message: str = "") -> None:
        """Show export progress in GUI."""
        if self._main_window:
            self._main_window.progress_bar.setMaximum(total)
            self._main_window.progress_bar.setValue(current)
            self._main_window.log_message(f"Progreso: {current}/{total} - {message}")
    
    def show_export_complete(self, filename: str, count: int) -> None:
        """Show export completion message in GUI."""
        if self._main_window:
            self._main_window.show_progress(False)
            self._main_window.log_message(f"Exportación completada: {filename} ({count} registros)")
            self._main_window.show_info("Exportación Completada", f"Archivo creado: {filename}\nRegistros: {count}")
    
    def show_error(self, message: str) -> None:
        """Show error message in GUI."""
        if self._main_window:
            self._main_window.log_message(f"ERROR: {message}")
            self._main_window.show_error("Error", message)
        self._logger.error(message)
    
    def show_success(self, message: str) -> None:
        """Show success message in GUI."""
        if self._main_window:
            self._main_window.log_message(f"ÉXITO: {message}")
            self._main_window.show_info("Éxito", message)
        self._logger.info(message)
    
    def show_info(self, message: str) -> None:
        """Show info message in GUI."""
        if self._main_window:
            self._main_window.log_message(f"INFO: {message}")
        self._logger.info(message)
    
    def confirm_action(self, message: str) -> bool:
        """Ask for user confirmation in GUI."""
        if self._main_window:
            reply = QMessageBox.question(
                self._main_window, 
                "Confirmación", 
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return False
    
    def get_invoice_limit(self) -> Optional[int]:
        """Get invoice limit from GUI - stub implementation."""
        return 100  # Default limit for GUI mode
    
    def show_bi_export_progress(self, step: str, current: int, total: int) -> None:
        """Show BI export progress in GUI."""
        if self._main_window:
            self._main_window.progress_bar.setMaximum(total)
            self._main_window.progress_bar.setValue(current)
            self._main_window.log_message(f"BI Export - {step}: {current}/{total}")
    
    def show_bi_export_complete(self, files_created: dict, statistics: dict) -> None:
        """Show BI export completion in GUI."""
        if self._main_window:
            self._main_window.show_progress(False)
            message = "Exportación BI completada:\n"
            for file, success in files_created.items():
                status = "✓" if success else "✗"
                message += f"{status} {file}\n"
            
            self._main_window.log_message("Exportación BI completada")
            self._main_window.show_info("Exportación BI Completada", message)