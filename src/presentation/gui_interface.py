"""
GUI User Interface for DATACONTA application using PySide6.
"""

from typing import List, Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QDateEdit,
    QProgressBar, QMessageBox, QGroupBox, QFormLayout, QTabWidget,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPalette

from src.application.ports.interfaces import UserInterface, Logger
from src.domain.entities.invoice import Invoice, InvoiceFilter


class DataContaMainWindow(QMainWindow):
    """Main window for DATACONTA GUI application."""
    
    def __init__(self, logger: Logger):
        super().__init__()
        self._logger = logger
        self.setWindowTitle("DATACONTA - Sistema Avanzado de Gestión")
        self.setMinimumSize(1000, 700)
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
        header_frame.setStyleSheet("QFrame { background-color: #2c3e50; color: white; padding: 10px; }")
        
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("🏢 DATACONTA - SISTEMA AVANZADO DE MENÚS")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Interfaz Gráfica PySide6 | Arquitectura Hexagonal | Principios SOLID")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #ecf0f1; font-size: 10pt;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def _setup_license_status(self, layout):
        """Setup license status section."""
        self.license_frame = QFrame()
        self.license_frame.setFrameStyle(QFrame.Box)
        self.license_frame.setStyleSheet("QFrame { background-color: #27ae60; color: white; padding: 8px; }")
        
        license_layout = QHBoxLayout(self.license_frame)
        
        self.license_label = QLabel("📄 Licencia actual: 💼 Profesional")
        self.license_label.setStyleSheet("color: white; font-weight: bold;")
        license_layout.addWidget(self.license_label)
        
        layout.addWidget(self.license_frame)
    
    def _setup_main_menu(self, layout):
        """Setup the main menu sections."""
        # Create scroll area for menu
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        # Menu sections
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
        
        # Buttons
        self.financial_reports_btn = QPushButton("💰 Informes Financieros")
        self.financial_reports_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e67e22; color: white; 
                padding: 8px; margin: 2px; 
                font-weight: bold; border: none; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        reports_layout.addWidget(self.financial_reports_btn)
        
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


class GUIUserInterfaceAdapter(UserInterface):
    """GUI adapter for user interface operations."""
    
    def __init__(self, logger: Logger):
        self._logger = logger
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