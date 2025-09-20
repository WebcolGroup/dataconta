"""
Main Window Lite - PySide6 UI for FREE License
Ventana principal reducida para licencia gratuita con funcionalidades limitadas.
Mantiene la arquitectura hexagonal con restricciones de licencia aplicadas.
"""

import sys
from typing import Dict, List, Callable, Optional, Any

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QGridLayout, QPushButton, QLabel, QTextEdit, QScrollArea,
        QFrame, QGroupBox, QStatusBar, QProgressBar, QMessageBox, 
        QInputDialog, QComboBox, QFileDialog, QTableWidget, QTableWidgetItem,
        QHeaderView, QSizePolicy, QSpacerItem
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
    QFrame = QGroupBox = QStatusBar = QProgressBar = QMessageBox = MockQtClass
    QInputDialog = QComboBox = QFileDialog = QTableWidget = QTableWidgetItem = MockQtClass
    QHeaderView = QSizePolicy = QSpacerItem = MockQtClass
    Qt = Signal = QTimer = QThread = QSize = MockQtClass
    QFont = QPalette = QColor = QIcon = QAction = MockQtClass

from src.domain.interfaces.ui_interfaces import (
    UIMenuController, UIUserInteraction, UIFileOperations, UIDataPresentation,
    UIMenuOption, UINotification, UINotificationType, UIProgressInfo
)
from src.domain.services.license_manager import LicenseManager


class MainWindowLite(QMainWindow, UIMenuController, UIUserInteraction, UIFileOperations, UIDataPresentation):
    """
    Ventana principal lite para licencia FREE de DATACONTA.
    Implementa funcionalidades reducidas con restricciones de licencia aplicadas.
    """
    
    # Señales para comunicación asíncrona
    operation_started = Signal(str)
    operation_completed = Signal(str, bool, str)
    progress_updated = Signal(int, str)
    
    def __init__(self, license_manager: LicenseManager):
        """Inicializar la ventana principal lite"""
        super().__init__()
        
        self._license_manager = license_manager
        
        # Estado de la aplicación
        self._menu_options: Dict[str, UIMenuOption] = {}
        self._current_operation: Optional[str] = None
        self._progress_bar: Optional[QProgressBar] = None
        self._statistics_data: Dict[str, Any] = {}
        
        # Configurar ventana
        self._setup_window()
        self._create_ui_components()
        self._setup_layout()
        self._setup_status_bar()
        self._connect_signals()
        
        # Aplicar estilos lite
        self._apply_lite_styles()
        
        # Mostrar información de licencia
        self._show_free_license_info()
    
    def _setup_window(self):
        """Configurar propiedades básicas de la ventana lite"""
        self.setWindowTitle("🚀 DATACONTA FREE - Versión Gratuita")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        
        # Centrar ventana
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    
    def _create_ui_components(self):
        """Crear todos los componentes de la UI lite"""
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Header con información de licencia FREE
        self.header_frame = self._create_lite_header()
        
        # Área de contenido principal sin scroll para simplicidad
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Contenedores para secciones del menú lite
        self.menu_sections: Dict[str, QGroupBox] = {}
        
        # Panel de estadísticas básicas
        self.stats_panel = self._create_statistics_panel()
        
        # Panel de upgrade promocional
        self.upgrade_panel = self._create_upgrade_panel()
        
    def _create_lite_header(self) -> QFrame:
        """Crear el header de la aplicación lite"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setFrameStyle(QFrame.StyledPanel)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 8, 15, 8)
        
        # Logo y título
        title_label = QLabel("🚀 DATACONTA FREE")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 0px;")
        
        subtitle_label = QLabel("Versión Gratuita - Funcionalidades Limitadas")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #f39c12; margin: 0px; font-weight: bold;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(2)
        
        # Estado de conexión
        self.connection_status = QLabel("🌐 Conectado")
        self.connection_status.setFont(QFont("Arial", 9))
        self.connection_status.setStyleSheet("color: #27ae60; padding: 3px;")
        
        # Estado de licencia FREE
        self.license_status = QLabel("🆓 GRATIS")
        self.license_status.setFont(QFont("Arial", 9, QFont.Bold))
        self.license_status.setStyleSheet("color: #e74c3c; padding: 3px; border: 1px solid #e74c3c; border-radius: 3px;")
        
        # Botón de upgrade
        self.upgrade_button = QPushButton("⬆️ ACTUALIZAR A PRO")
        self.upgrade_button.setFont(QFont("Arial", 9, QFont.Bold))
        self.upgrade_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.upgrade_button.clicked.connect(self._show_upgrade_info)
        
        status_layout = QVBoxLayout()
        status_layout.addWidget(self.connection_status)
        status_layout.addWidget(self.license_status)
        status_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addWidget(self.upgrade_button)
        layout.addLayout(status_layout)
        
        return header
    
    def _create_statistics_panel(self) -> QFrame:
        """Crear panel de estadísticas básicas para FREE"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumHeight(150)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Título del panel
        stats_title = QLabel("📊 Estadísticas Básicas (Limitadas)")
        stats_title.setFont(QFont("Arial", 12, QFont.Bold))
        stats_title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        # Grid de estadísticas
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        # Etiquetas de estadísticas básicas
        self.stats_labels = {}
        stats_info = [
            ("total_invoices", "📄 Total Facturas:", "0"),
            ("total_amount", "💰 Monto Total:", "$0.00"),
            ("unique_customers", "👥 Clientes Únicos:", "0"),
            ("avg_invoice", "📊 Promedio/Factura:", "$0.00")
        ]
        
        for i, (key, label, default) in enumerate(stats_info):
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Arial", 9))
            label_widget.setStyleSheet("color: #7f8c8d;")
            
            value_widget = QLabel(default)
            value_widget.setFont(QFont("Arial", 9, QFont.Bold))
            value_widget.setStyleSheet("color: #2c3e50;")
            
            self.stats_labels[key] = value_widget
            
            row = i // 2
            col = (i % 2) * 2
            stats_grid.addWidget(label_widget, row, col)
            stats_grid.addWidget(value_widget, row, col + 1)
        
        layout.addWidget(stats_title)
        layout.addLayout(stats_grid)
        
        return panel
    
    def _create_upgrade_panel(self) -> QFrame:
        """Crear panel promocional de upgrade"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumHeight(100)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f39c12, stop:1 #e67e22);
                border: 2px solid #d35400;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Mensaje promocional
        promo_text = QLabel("🚀 ¡Desbloquea todas las funcionalidades!\n💼 Actualiza a PROFESIONAL o ENTERPRISE")
        promo_text.setFont(QFont("Arial", 11, QFont.Bold))
        promo_text.setStyleSheet("color: white; line-height: 1.4;")
        promo_text.setWordWrap(True)
        
        # Botón de upgrade grande
        upgrade_big_button = QPushButton("⬆️ VER PLANES")
        upgrade_big_button.setFont(QFont("Arial", 12, QFont.Bold))
        upgrade_big_button.setMinimumHeight(40)
        upgrade_big_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        upgrade_big_button.clicked.connect(self._show_upgrade_plans)
        
        layout.addWidget(promo_text)
        layout.addStretch()
        layout.addWidget(upgrade_big_button)
        
        return panel
    
    def _setup_layout(self):
        """Configurar el layout principal lite"""
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        main_layout.addWidget(self.header_frame)
        
        # Panel de upgrade promocional
        main_layout.addWidget(self.upgrade_panel)
        
        # Contenido principal
        main_layout.addWidget(self.content_widget, 1)
        
        # Panel de estadísticas
        main_layout.addWidget(self.stats_panel)
    
    def _setup_status_bar(self):
        """Configurar la barra de estado lite"""
        self.status_bar = self.statusBar()
        
        # Mensaje de estado
        self.status_bar.showMessage("✅ DATACONTA FREE iniciado - Funcionalidades limitadas")
        
        # Progress bar simple
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMaximumWidth(150)
        self.status_bar.addPermanentWidget(self._progress_bar)
        
        # Información de operación
        self.operation_label = QLabel("")
        self.status_bar.addPermanentWidget(self.operation_label)
    
    def _connect_signals(self):
        """Conectar señales internas"""
        self.operation_started.connect(self._on_operation_started)
        self.operation_completed.connect(self._on_operation_completed)
        self.progress_updated.connect(self._on_progress_updated)
    
    def _apply_lite_styles(self):
        """Aplicar estilos CSS a la ventana lite"""
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
                font-size: 12px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px 0 6px;
                background-color: #ffffff;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10px;
                min-height: 16px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            
            QPushButton[blocked="true"] {
                background-color: #e74c3c;
                color: white;
                text-decoration: line-through;
            }
            
            QPushButton[blocked="true"]:hover {
                background-color: #c0392b;
            }
            
            QStatusBar {
                background-color: #ecf0f1;
                border-top: 1px solid #bdc3c7;
                color: #2c3e50;
                font-size: 9px;
            }
        """)
    
    def _show_free_license_info(self):
        """Mostrar información inicial de licencia FREE"""
        if self._license_manager:
            info_text = self._license_manager.get_free_features_summary()
            QTimer.singleShot(1000, lambda: self._show_welcome_message(info_text))
    
    def _show_welcome_message(self, features_info: str):
        """Mostrar mensaje de bienvenida para licencia FREE"""
        welcome_msg = f"""
¡Bienvenido a DATACONTA FREE! 🎉

{features_info}

💡 Funcionalidades disponibles en esta versión gratuita:
• Consulta de facturas (hasta 100 registros)
• Exportación a JSON estructurado
• Estadísticas básicas
• Interfaz gráfica simplificada

🚀 Para acceder a todas las funcionalidades, considera actualizar a una licencia PRO o ENTERPRISE.
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("DATACONTA FREE - Bienvenido")
        msg_box.setText("¡Bienvenido a DATACONTA FREE!")
        msg_box.setDetailedText(welcome_msg.strip())
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()
    
    def _show_upgrade_info(self):
        """Mostrar información de upgrade básica"""
        upgrade_msg = """
🚀 ACTUALIZAR A PROFESIONAL O ENTERPRISE

Desbloquea todas las funcionalidades:

📊 PROFESIONAL:
• Hasta 1,000 facturas por consulta
• Exportación CSV completa
• Informes avanzados
• Herramientas de análisis

🏢 ENTERPRISE:
• Consultas ilimitadas
• Exportación BI completa
• Integración con Ollama AI
• Análisis empresarial completo
• Soporte prioritario

💰 Contacta con nuestro equipo de ventas para más información.
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Actualizar Licencia")
        msg_box.setText("Planes de Licencia Disponibles")
        msg_box.setDetailedText(upgrade_msg.strip())
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()
    
    def _show_upgrade_plans(self):
        """Mostrar planes de upgrade detallados"""
        plans_msg = """
📋 COMPARATIVA DE PLANES

🆓 GRATUITO (Actual):
• Hasta 100 facturas por consulta
• Exportación JSON básica
• Estadísticas limitadas
• GUI simplificada

💼 PROFESIONAL ($29/mes):
• Hasta 1,000 facturas por consulta
• Exportación CSV completa
• Informes detallados
• GUI completa
• Herramientas de análisis

🏢 ENTERPRISE ($99/mes):
• Consultas ilimitadas
• Exportación BI completa
• Integración AI con Ollama
• Análisis empresarial avanzado
• Soporte 24/7
• Funcionalidades personalizadas

📞 Contacto: ventas@dataconta.com
🌐 Web: www.dataconta.com/planes
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Planes y Precios")
        msg_box.setText("Elige el plan que mejor se adapte a tu negocio")
        msg_box.setDetailedText(plans_msg.strip())
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()
    
    # Implementación de UIMenuController con restricciones FREE
    def setup_menu_options(self, menu_sections: Dict[str, List[UIMenuOption]]) -> None:
        """Configurar las opciones de menú lite con restricciones FREE"""
        
        # Limpiar layout existente
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        self.menu_sections.clear()
        self._menu_options.clear()
        
        # Filtrar y crear secciones de menú para FREE
        free_sections = self._filter_free_sections(menu_sections)
        
        for section_id, options in free_sections.items():
            section_group = self._create_lite_menu_section(section_id, options)
            self.menu_sections[section_id] = section_group
            self.content_layout.addWidget(section_group)
            
            # Guardar opciones para referencia
            for option in options:
                self._menu_options[option.id] = option
        
        self.content_layout.addStretch()
    
    def _filter_free_sections(self, menu_sections: Dict[str, List[UIMenuOption]]) -> Dict[str, List[UIMenuOption]]:
        """Filtrar secciones de menú para licencia FREE"""
        free_sections = {}
        
        # Solo mostrar secciones básicas para FREE
        allowed_sections = ["tools", "basic_reports"]  # Solo herramientas básicas
        
        for section_id, options in menu_sections.items():
            if section_id in allowed_sections or any("JSON" in opt.title or "Consulta" in opt.title for opt in options):
                # Filtrar opciones específicas para FREE
                free_options = []
                for option in options:
                    # Permitir solo operaciones básicas
                    if any(keyword in option.title.lower() for keyword in ["consulta", "json", "básico", "simple"]):
                        free_options.append(option)
                    else:
                        # Mostrar opciones bloqueadas para promocionar upgrade
                        blocked_option = UIMenuOption(
                            id=f"{option.id}_blocked",
                            title=f"🔒 {option.title}",
                            description=f"{option.description} (Requiere licencia PRO/ENTERPRISE)",
                            emoji="🔒",
                            enabled=False,
                            action=lambda opt=option: self._show_blocked_feature_message(opt.title)
                        )
                        free_options.append(blocked_option)
                
                if free_options:
                    free_sections[section_id] = free_options
        
        # Asegurar que siempre hay al menos opciones básicas
        if not free_sections:
            free_sections["free_tools"] = [
                UIMenuOption(
                    id="export_json_free",
                    title="📄 Exportar JSON",
                    description="Exportar facturas a formato JSON (hasta 100 registros)",
                    emoji="📄",
                    enabled=True,
                    action=lambda: self._execute_json_export()
                )
            ]
        
        return free_sections
    
    def _create_lite_menu_section(self, section_id: str, options: List[UIMenuOption]) -> QGroupBox:
        """Crear una sección de menú lite con botones más compactos"""
        
        # Determinar título de la sección
        section_titles = {
            "tools": "🛠️ Herramientas Básicas",
            "basic_reports": "📊 Informes Básicos",
            "free_tools": "🆓 Herramientas Gratuitas"
        }
        
        title = section_titles.get(section_id, section_id.replace("_", " ").title())
        group_box = QGroupBox(title)
        
        # Layout simplificado en una columna
        layout = QVBoxLayout(group_box)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 10)
        
        # Crear botones más compactos
        for option in options:
            button = self._create_lite_menu_button(option)
            layout.addWidget(button)
        
        return group_box
    
    def _create_lite_menu_button(self, option: UIMenuOption) -> QPushButton:
        """Crear un botón lite para una opción de menú"""
        button = QPushButton()
        
        # Texto con emoji y título
        button_text = f"{option.emoji} {option.title}"
        button.setText(button_text)
        
        # Configurar propiedades
        button.setEnabled(option.enabled)
        button.setMinimumHeight(40)  # Más compacto que la versión completa
        button.setToolTip(option.description)
        
        # Marcar si está bloqueado
        if not option.enabled and "🔒" in option.emoji:
            button.setProperty("blocked", True)
        
        # Conectar acción
        if option.action:
            button.clicked.connect(lambda checked, opt=option: self._execute_menu_action(opt))
        
        return button
    
    def _show_blocked_feature_message(self, feature_name: str):
        """Mostrar mensaje de funcionalidad bloqueada"""
        if self._license_manager:
            message = self._license_manager.get_blocked_feature_message(feature_name)
        else:
            message = f"La funcionalidad '{feature_name}' requiere una licencia PRO o ENTERPRISE."
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Funcionalidad Bloqueada")
        msg_box.setText(f"🔒 {feature_name}")
        msg_box.setInformativeText(message)
        msg_box.setDetailedText("""
Para acceder a esta funcionalidad, actualiza tu licencia:

💼 PROFESIONAL: Ideal para pequeñas empresas
🏢 ENTERPRISE: Completo para grandes organizaciones

Contacta: ventas@dataconta.com
        """)
        msg_box.setIcon(QMessageBox.Warning)
        
        # Agregar botón de upgrade
        upgrade_button = msg_box.addButton("⬆️ Ver Planes", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Ok)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == upgrade_button:
            self._show_upgrade_plans()
    
    def _execute_json_export(self):
        """Ejecutar exportación JSON para licencia FREE"""
        # Esta sería la integración con el caso de uso JSON
        self.show_notification(UINotification(
            title="Exportación JSON",
            message="Funcionalidad de exportación JSON disponible para licencia FREE (hasta 100 registros)",
            notification_type=UINotificationType.INFO
        ))
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Actualizar las estadísticas básicas en el panel"""
        self._statistics_data = stats
        
        # Formatear y mostrar estadísticas
        if "total_invoices" in stats:
            self.stats_labels["total_invoices"].setText(str(stats["total_invoices"]))
        
        if "total_amount" in stats:
            amount = stats["total_amount"]
            self.stats_labels["total_amount"].setText(f"${amount:,.2f}")
        
        if "unique_customers" in stats:
            self.stats_labels["unique_customers"].setText(str(stats["unique_customers"]))
        
        if "average_invoice_amount" in stats:
            avg = stats["average_invoice_amount"]
            self.stats_labels["avg_invoice"].setText(f"${avg:,.2f}")
    
    # Implementación básica de interfaces UI (métodos simplificados)
    
    def show_notification(self, notification: UINotification) -> None:
        """Mostrar una notificación al usuario (versión simplificada)"""
        
        icon_map = {
            UINotificationType.INFO: QMessageBox.Information,
            UINotificationType.SUCCESS: QMessageBox.Information,
            UINotificationType.WARNING: QMessageBox.Warning,
            UINotificationType.ERROR: QMessageBox.Critical,
            UINotificationType.QUESTION: QMessageBox.Question
        }
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"DATACONTA FREE - {notification.title}")
        msg_box.setText(notification.message)
        msg_box.setIcon(icon_map.get(notification.notification_type, QMessageBox.Information))
        
        if notification.details:
            msg_box.setDetailedText(notification.details)
        
        msg_box.exec()
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        """Pedir confirmación al usuario"""
        reply = QMessageBox.question(
            self, f"DATACONTA FREE - {title}", message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def get_user_input(self, title: str, message: str, default_value: str = "") -> Optional[str]:
        """Obtener input de texto del usuario"""
        text, ok = QInputDialog.getText(self, f"DATACONTA FREE - {title}", message, text=default_value)
        return text if ok else None
    
    def show_progress(self, progress_info: UIProgressInfo) -> None:
        """Mostrar progreso de una operación (versión simplificada)"""
        self._progress_bar.setVisible(True)
        self._progress_bar.setMaximum(progress_info.maximum if not progress_info.is_indeterminate else 0)
        self._progress_bar.setValue(progress_info.current)
        self.operation_label.setText(progress_info.message[:30])  # Truncar para UI compacta
        self.status_bar.showMessage(progress_info.title)
    
    def hide_progress(self) -> None:
        """Ocultar el indicador de progreso"""
        self._progress_bar.setVisible(False)
        self.operation_label.setText("")
        self.status_bar.showMessage("✅ DATACONTA FREE - Listo para usar")
    
    # Implementación simplificada de otros métodos
    def select_save_file(self, title: str, default_filename: str, file_filter: str) -> Optional[str]:
        """Permitir al usuario seleccionar dónde guardar un archivo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"DATACONTA FREE - {title}", default_filename, file_filter
        )
        return file_path if file_path else None
    
    def show_data_table(self, title: str, headers: List[str], data: List[List[Any]]) -> None:
        """Mostrar datos en formato tabla (versión simplificada para FREE)"""
        # Limitar datos a 50 filas para licencia FREE
        limited_data = data[:50] if len(data) > 50 else data
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"DATACONTA FREE - {title}")
        
        if len(data) > 50:
            msg_box.setText(f"Mostrando primeras 50 filas de {len(data)} disponibles")
            msg_box.setInformativeText("Actualiza a PRO/ENTERPRISE para ver todos los datos")
        else:
            msg_box.setText(f"Datos: {len(data)} filas")
        
        # Crear tabla simple
        content = "Headers: " + " | ".join(headers) + "\n\n"
        for i, row in enumerate(limited_data[:10]):  # Mostrar solo 10 filas en el texto
            content += f"Row {i+1}: " + " | ".join(map(str, row)) + "\n"
        
        if len(limited_data) > 10:
            content += f"\n... y {len(limited_data) - 10} filas más"
        
        msg_box.setDetailedText(content)
        msg_box.exec()
    
    # Métodos auxiliares
    def _execute_menu_action(self, option: UIMenuOption) -> None:
        """Ejecutar la acción de una opción de menú con validaciones FREE"""
        try:
            # Validar límites de licencia antes de ejecutar
            if self._license_manager and not self._license_manager.is_gui_lite_mode():
                self._show_blocked_feature_message(option.title)
                return
            
            self.operation_started.emit(option.title)
            
            # Ejecutar la acción
            if option.action:
                option.action()
            
            self.operation_completed.emit(option.title, True, "Operación completada")
            
        except Exception as e:
            self.operation_completed.emit(option.title, False, str(e))
            self.show_notification(UINotification(
                title="Error en Operación",
                message=f"Error ejecutando {option.title}: {str(e)}",
                notification_type=UINotificationType.ERROR
            ))
    
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
        
        # Auto-limpiar después de 3 segundos (más rápido que versión completa)
        QTimer.singleShot(3000, lambda: self.status_bar.showMessage("✅ DATACONTA FREE - Listo"))
    
    def _on_progress_updated(self, value: int, message: str) -> None:
        """Actualizar progreso"""
        if self._progress_bar.isVisible():
            self._progress_bar.setValue(value)
            self.operation_label.setText(message[:30])  # Truncar para UI compacta
    
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
    
    def show_main_window(self) -> None:
        """Mostrar la ventana principal lite"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def close_application(self) -> None:
        """Cerrar la aplicación"""
        reply = self.ask_confirmation(
            "Confirmar Salida",
            "¿Está seguro que desea cerrar DATACONTA FREE?"
        )
        
        if reply:
            QApplication.quit()
    
    def closeEvent(self, event):
        """Manejar evento de cierre de ventana"""
        self.close_application()
        event.ignore()  # Ignorar hasta que el usuario confirme
    
    # Métodos adicionales específicos para FREE
    def show_free_limitations(self):
        """Mostrar las limitaciones de la licencia FREE"""
        limitations = """
📋 LIMITACIONES DE DATACONTA FREE

🔢 Límites de Datos:
• Máximo 100 facturas por consulta
• Estadísticas básicas únicamente
• Exportación solo a JSON

🚫 Funcionalidades Bloqueadas:
• Exportación CSV avanzada
• Módulo BI completo
• Integración con Ollama AI
• Informes empresariales
• Análisis de tendencias

💡 Para eliminar estas limitaciones, actualiza a:
• PROFESIONAL: Funcionalidades avanzadas
• ENTERPRISE: Sin limitaciones + IA

🌐 Más información: www.dataconta.com/planes
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Limitaciones de Licencia FREE")
        msg_box.setText("Información sobre limitaciones")
        msg_box.setDetailedText(limitations.strip())
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()