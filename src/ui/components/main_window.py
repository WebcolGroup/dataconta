"""
Main Window - PySide6 UI
Ventana principal que implementa el sistema de menús con interfaz gráfica.
Mantiene la separación de responsabilidades y bajo acoplamiento con la lógica de negocio.
"""

import sys
from typing import Dict, List, Callable, Optional, Any

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QGridLayout, QPushButton, QLabel, QTextEdit, QScrollArea,
        QFrame, QGroupBox, QStatusBar, QMenuBar, QToolBar, QSplitter,
        QProgressBar, QMessageBox, QInputDialog, QComboBox, QFileDialog
    )
    from PySide6.QtCore import Qt, Signal, QTimer, QThread, QSize
    from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QAction
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Fallback para cuando PySide6 no esté instalado durante desarrollo
    PYSIDE6_AVAILABLE = False
    
    # Clases mock para que el código compile
    class MockQtClass:
        def __init__(self, *args, **kwargs):
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    QApplication = QMainWindow = QWidget = QVBoxLayout = QHBoxLayout = MockQtClass
    QGridLayout = QPushButton = QLabel = QTextEdit = QScrollArea = MockQtClass
    QFrame = QGroupBox = QStatusBar = QMenuBar = QToolBar = QSplitter = MockQtClass
    QProgressBar = QMessageBox = QInputDialog = QComboBox = QFileDialog = MockQtClass
    Qt = Signal = QTimer = QThread = QSize = MockQtClass
    QFont = QPalette = QColor = QIcon = QAction = MockQtClass

from src.domain.interfaces.ui_interfaces import (
    UIMenuController, UIUserInteraction, UIFileOperations, UIDataPresentation,
    UIMenuOption, UINotification, UINotificationType, UIProgressInfo
)


class MainWindow(QMainWindow, UIMenuController, UIUserInteraction, UIFileOperations, UIDataPresentation):
    """
    Ventana principal de la aplicación DATACONTA.
    Implementa todas las interfaces de UI manteniendo bajo acoplamiento.
    """
    
    # Señales para comunicación asíncrona
    operation_started = Signal(str)
    operation_completed = Signal(str, bool, str)
    progress_updated = Signal(int, str)
    
    def __init__(self):
        """Inicializar la ventana principal"""
        super().__init__()
        
        # Estado de la aplicación
        self._menu_options: Dict[str, UIMenuOption] = {}
        self._current_operation: Optional[str] = None
        self._progress_bar: Optional[QProgressBar] = None
        
        # Configurar ventana
        self._setup_window()
        self._create_ui_components()
        self._setup_layout()
        self._setup_status_bar()
        self._connect_signals()
        
        # Aplicar estilos
        self._apply_styles()
    
    def _setup_window(self):
        """Configurar propiedades básicas de la ventana"""
        self.setWindowTitle("🚀 DATACONTA - Sistema Avanzado de Gestión")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Centrar ventana
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    
    def _create_ui_components(self):
        """Crear todos los componentes de la UI"""
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Header con información de la aplicación
        self.header_frame = self._create_header()
        
        # Área de contenido principal con scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        self.scroll_area.setWidget(self.content_widget)
        
        # Contenedores para secciones del menú
        self.menu_sections: Dict[str, QGroupBox] = {}
        
        # Panel de información lateral
        self.info_panel = self._create_info_panel()
        
    def _create_header(self) -> QFrame:
        """Crear el header de la aplicación"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setFrameStyle(QFrame.StyledPanel)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo y título
        title_label = QLabel("🚀 DATACONTA")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 0px;")
        
        subtitle_label = QLabel("Sistema Avanzado de Gestión Empresarial")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: #7f8c8d; margin: 0px;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(2)
        
        # Estado de conexión
        self.connection_status = QLabel("🌐 Conectado")
        self.connection_status.setFont(QFont("Arial", 10))
        self.connection_status.setStyleSheet("color: #27ae60; padding: 5px;")
        
        # Estado de licencia
        self.license_status = QLabel("💼 Profesional")
        self.license_status.setFont(QFont("Arial", 10))
        self.license_status.setStyleSheet("color: #3498db; padding: 5px;")
        
        status_layout = QVBoxLayout()
        status_layout.addWidget(self.connection_status)
        status_layout.addWidget(self.license_status)
        status_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addLayout(status_layout)
        
        return header
    
    def _create_info_panel(self) -> QFrame:
        """Crear panel de información lateral"""
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Título del panel
        info_title = QLabel("📊 Información del Sistema")
        info_title.setFont(QFont("Arial", 14, QFont.Bold))
        info_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Área de texto para mostrar información
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
                font-family: Consolas, Monaco, monospace;
                font-size: 10px;
            }
        """)
        
        # Log de operaciones recientes
        recent_title = QLabel("📋 Operaciones Recientes")
        recent_title.setFont(QFont("Arial", 12, QFont.Bold))
        recent_title.setStyleSheet("color: #2c3e50;")
        
        self.recent_operations = QTextEdit()
        self.recent_operations.setReadOnly(True)
        self.recent_operations.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
                font-family: Consolas, Monaco, monospace;
                font-size: 9px;
            }
        """)
        
        layout.addWidget(info_title)
        layout.addWidget(self.info_text)
        layout.addWidget(recent_title)
        layout.addWidget(self.recent_operations)
        layout.addStretch()
        
        return panel
    
    def _setup_layout(self):
        """Configurar el layout principal"""
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        main_layout.addWidget(self.header_frame)
        
        # Contenido principal con splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.scroll_area)
        splitter.addWidget(self.info_panel)
        splitter.setStretchFactor(0, 1)  # Área principal ocupa más espacio
        splitter.setStretchFactor(1, 0)  # Panel lateral tamaño fijo
        
        main_layout.addWidget(splitter, 1)
    
    def _setup_status_bar(self):
        """Configurar la barra de estado"""
        self.status_bar = self.statusBar()
        
        # Mensaje de estado
        self.status_bar.showMessage("✅ Sistema iniciado - Listo para usar")
        
        # Progress bar para operaciones
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self._progress_bar)
        
        # Información adicional
        self.operation_label = QLabel("")
        self.status_bar.addPermanentWidget(self.operation_label)
    
    def _connect_signals(self):
        """Conectar señales internas"""
        self.operation_started.connect(self._on_operation_started)
        self.operation_completed.connect(self._on_operation_completed)
        self.progress_updated.connect(self._on_progress_updated)
    
    def _apply_styles(self):
        """Aplicar estilos CSS a la ventana"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e1e5e9;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            
            QStatusBar {
                background-color: #ecf0f1;
                border-top: 1px solid #bdc3c7;
                color: #2c3e50;
            }
        """)
    
    # Implementación de UIMenuController
    def setup_menu_options(self, menu_sections: Dict[str, List[UIMenuOption]]) -> None:
        """Configurar las opciones de menú en la UI"""
        
        # Limpiar layout existente
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        self.menu_sections.clear()
        self._menu_options.clear()
        
        # Crear secciones de menú
        for section_id, options in menu_sections.items():
            section_group = self._create_menu_section(section_id, options)
            self.menu_sections[section_id] = section_group
            self.content_layout.addWidget(section_group)
            
            # Guardar opciones para referencia
            for option in options:
                self._menu_options[option.id] = option
        
        self.content_layout.addStretch()
    
    def _create_menu_section(self, section_id: str, options: List[UIMenuOption]) -> QGroupBox:
        """Crear una sección de menú con sus botones"""
        
        # Determinar título de la sección
        section_titles = {
            "business_intelligence": "📊 Business Intelligence",
            "reports": "📈 Generación de Informes", 
            "tools": "🛠️ Herramientas",
            "ollama": "🤖 Integración con Ollama",
            "ai_analytics": "🧠 AI Analytics"
        }
        
        title = section_titles.get(section_id, section_id.replace("_", " ").title())
        group_box = QGroupBox(title)
        
        # Layout de grid para los botones
        layout = QGridLayout(group_box)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 15)
        
        # Crear botones en grid (2 columnas)
        for i, option in enumerate(options):
            button = self._create_menu_button(option)
            row = i // 2
            col = i % 2
            layout.addWidget(button, row, col)
        
        return group_box
    
    def _create_menu_button(self, option: UIMenuOption) -> QPushButton:
        """Crear un botón para una opción de menú"""
        button = QPushButton()
        
        # Texto con emoji y título
        button_text = f"{option.emoji} {option.title}"
        button.setText(button_text)
        
        # Configurar propiedades
        button.setEnabled(option.enabled)
        button.setMinimumHeight(60)
        button.setToolTip(option.description)
        
        # Conectar acción
        if option.action:
            button.clicked.connect(lambda checked, opt=option: self._execute_menu_action(opt))
        
        # Estilo específico según el tipo de opción
        button_style = self._get_button_style(option)
        button.setStyleSheet(button_style)
        
        return button
    
    def _get_button_style(self, option: UIMenuOption) -> str:
        """Obtener estilo específico para un botón según su tipo"""
        base_style = """
            QPushButton {
                text-align: left;
                padding-left: 15px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 8px;
            }
        """
        
        # Colores según el tipo de funcionalidad
        if "Business Intelligence" in option.description or "BI" in option.description:
            color_style = """
                QPushButton { background-color: #9b59b6; }
                QPushButton:hover { background-color: #8e44ad; }
                QPushButton:pressed { background-color: #7d3c98; }
            """
        elif "Informe" in option.description or "Report" in option.description:
            color_style = """
                QPushButton { background-color: #e74c3c; }
                QPushButton:hover { background-color: #c0392b; }
                QPushButton:pressed { background-color: #a93226; }
            """
        elif "Herramienta" in option.description or "Tool" in option.description:
            color_style = """
                QPushButton { background-color: #f39c12; }
                QPushButton:hover { background-color: #e67e22; }
                QPushButton:pressed { background-color: #d68910; }
            """
        elif "Ollama" in option.description or "AI" in option.description:
            color_style = """
                QPushButton { background-color: #1abc9c; }
                QPushButton:hover { background-color: #16a085; }
                QPushButton:pressed { background-color: #138d75; }
            """
        else:
            color_style = """
                QPushButton { background-color: #3498db; }
                QPushButton:hover { background-color: #2980b9; }
                QPushButton:pressed { background-color: #21618c; }
            """
        
        return base_style + color_style
    
    def _execute_menu_action(self, option: UIMenuOption) -> None:
        """Ejecutar la acción de una opción de menú"""
        try:
            self.operation_started.emit(option.title)
            self._log_operation(f"Ejecutando: {option.title}")
            
            # Ejecutar la acción
            if option.action:
                option.action()
            
            self.operation_completed.emit(option.title, True, "Operación completada exitosamente")
            
        except Exception as e:
            self.operation_completed.emit(option.title, False, str(e))
            self.show_notification(UINotification(
                title="Error en Operación",
                message=f"Error ejecutando {option.title}: {str(e)}",
                notification_type=UINotificationType.ERROR
            ))
    
    def enable_option(self, option_id: str, enabled: bool = True) -> None:
        """Habilitar/deshabilitar una opción específica"""
        if option_id in self._menu_options:
            self._menu_options[option_id].enabled = enabled
            
            # Buscar y actualizar el botón correspondiente
            for section in self.menu_sections.values():
                for button in section.findChildren(QPushButton):
                    if option_id in button.text():
                        button.setEnabled(enabled)
                        break
    
    def update_license_status(self, license_type: str, is_valid: bool) -> None:
        """Actualizar el estado de la licencia en la UI"""
        if is_valid:
            self.license_status.setText(f"💼 {license_type}")
            self.license_status.setStyleSheet("color: #27ae60; padding: 5px;")
        else:
            self.license_status.setText("❌ Licencia Inválida")
            self.license_status.setStyleSheet("color: #e74c3c; padding: 5px;")
    
    def show_main_window(self) -> None:
        """Mostrar la ventana principal"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def close_application(self) -> None:
        """Cerrar la aplicación"""
        reply = self.ask_confirmation(
            "Confirmar Salida",
            "¿Está seguro que desea cerrar DATACONTA?"
        )
        
        if reply:
            QApplication.quit()
    
    # Implementación de UIUserInteraction
    def show_notification(self, notification: UINotification) -> None:
        """Mostrar una notificación al usuario"""
        
        # Mapear tipos de notificación
        icon_map = {
            UINotificationType.INFO: QMessageBox.Information,
            UINotificationType.SUCCESS: QMessageBox.Information,
            UINotificationType.WARNING: QMessageBox.Warning,
            UINotificationType.ERROR: QMessageBox.Critical,
            UINotificationType.QUESTION: QMessageBox.Question
        }
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(notification.title)
        msg_box.setText(notification.message)
        msg_box.setIcon(icon_map.get(notification.notification_type, QMessageBox.Information))
        
        if notification.details:
            msg_box.setDetailedText(notification.details)
        
        # Para notificaciones de éxito, usar color verde
        if notification.notification_type == UINotificationType.SUCCESS:
            msg_box.setStyleSheet("QMessageBox { background-color: #d4edda; }")
        
        msg_box.exec()
        
        # Log de la notificación
        self._log_operation(f"{notification.notification_type.value.upper()}: {notification.message}")
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        """Pedir confirmación al usuario"""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def get_user_input(self, title: str, message: str, default_value: str = "") -> Optional[str]:
        """Obtener input de texto del usuario"""
        text, ok = QInputDialog.getText(self, title, message, text=default_value)
        return text if ok else None
    
    def select_from_list(self, title: str, message: str, options: List[str]) -> Optional[str]:
        """Permitir al usuario seleccionar de una lista de opciones"""
        item, ok = QInputDialog.getItem(self, title, message, options, 0, False)
        return item if ok else None
    
    def show_progress(self, progress_info: UIProgressInfo) -> None:
        """Mostrar progreso de una operación"""
        self._progress_bar.setVisible(True)
        self._progress_bar.setMaximum(progress_info.maximum if not progress_info.is_indeterminate else 0)
        self._progress_bar.setValue(progress_info.current)
        self.operation_label.setText(progress_info.message)
        self.status_bar.showMessage(progress_info.title)
    
    def hide_progress(self) -> None:
        """Ocultar el indicador de progreso"""
        self._progress_bar.setVisible(False)
        self.operation_label.setText("")
        self.status_bar.showMessage("✅ Listo para usar")
    
    # Implementación de UIFileOperations
    def select_save_file(self, title: str, default_filename: str, file_filter: str) -> Optional[str]:
        """Permitir al usuario seleccionar dónde guardar un archivo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, title, default_filename, file_filter
        )
        return file_path if file_path else None
    
    def select_open_file(self, title: str, file_filter: str) -> Optional[str]:
        """Permitir al usuario seleccionar un archivo para abrir"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, title, "", file_filter
        )
        return file_path if file_path else None
    
    def select_directory(self, title: str, default_path: str = "") -> Optional[str]:
        """Permitir al usuario seleccionar un directorio"""
        directory = QFileDialog.getExistingDirectory(
            self, title, default_path
        )
        return directory if directory else None
    
    # Implementación de UIDataPresentation
    def show_data_table(self, title: str, headers: List[str], data: List[List[Any]]) -> None:
        """Mostrar datos en formato tabla"""
        # Esta implementación sería más compleja con QTableWidget
        # Por simplicidad, mostramos en un diálogo de texto
        content = f"Headers: {headers}\n\n"
        for row in data[:10]:  # Mostrar solo primeras 10 filas
            content += f"{row}\n"
        
        if len(data) > 10:
            content += f"\n... y {len(data) - 10} filas más"
        
        self.show_report_results(title, content)
    
    def show_report_results(self, title: str, content: str, format_type: str = "text") -> None:
        """Mostrar resultados de un reporte"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText("Reporte generado exitosamente")
        msg_box.setDetailedText(content)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    # Métodos auxiliares privados
    def _on_operation_started(self, operation_name: str) -> None:
        """Manejar inicio de operación"""
        self._current_operation = operation_name
        self.status_bar.showMessage(f"🔄 Ejecutando: {operation_name}")
    
    def _on_operation_completed(self, operation_name: str, success: bool, message: str) -> None:
        """Manejar finalización de operación"""
        self._current_operation = None
        
        if success:
            self.status_bar.showMessage(f"✅ {operation_name} completado")
        else:
            self.status_bar.showMessage(f"❌ Error en {operation_name}")
        
        self._log_operation(f"{operation_name}: {'ÉXITO' if success else 'ERROR'} - {message}")
        
        # Auto-limpiar después de 5 segundos
        QTimer.singleShot(5000, lambda: self.status_bar.showMessage("✅ Listo para usar"))
    
    def _on_progress_updated(self, value: int, message: str) -> None:
        """Actualizar progreso"""
        if self._progress_bar.isVisible():
            self._progress_bar.setValue(value)
            self.operation_label.setText(message)
    
    def _log_operation(self, message: str) -> None:
        """Registrar operación en el panel de información"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        current_text = self.recent_operations.toPlainText()
        lines = current_text.split('\n')
        
        # Mantener solo las últimas 20 líneas
        if len(lines) >= 20:
            lines = lines[-19:]
        
        lines.append(log_entry)
        self.recent_operations.setPlainText('\n'.join(lines))
        
        # Scroll hacia abajo
        scrollbar = self.recent_operations.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_system_info(self, info: str) -> None:
        """Actualizar información del sistema"""
        self.info_text.setPlainText(info)
    
    def update_connection_status(self, connected: bool) -> None:
        """Actualizar estado de conexión"""
        if connected:
            self.connection_status.setText("🌐 Conectado")
            self.connection_status.setStyleSheet("color: #27ae60; padding: 5px;")
        else:
            self.connection_status.setText("🔴 Desconectado")
            self.connection_status.setStyleSheet("color: #e74c3c; padding: 5px;")
    
    def closeEvent(self, event):
        """Manejar evento de cierre de ventana"""
        self.close_application()
        event.ignore()  # Ignorar hasta que el usuario confirme