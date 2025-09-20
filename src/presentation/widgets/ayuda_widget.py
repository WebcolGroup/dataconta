"""
Widget especializado para el tab de ayuda y soporte.
"""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QPushButton, QScrollArea, QFrame, QMessageBox, QDialog,
    QTextEdit, QDialogButtonBox, QLineEdit, QFormLayout
)
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtGui import QFont


class SiigoConfigDialog(QDialog):
    """
    Diálogo especializado para configurar credenciales de Siigo API.
    Permite editar el archivo .env con las credenciales necesarias.
    """
    
    def __init__(self, parent=None):
        """Inicializar el configurador de credenciales Siigo."""
        super().__init__(parent)
        self.setWindowTitle("🔐 Configuración de Credenciales Siigo API")
        self.setMinimumSize(600, 500)
        self.resize(700, 550)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self._setup_ui()
        self._load_current_config()
    
    def _setup_ui(self):
        """Configurar la interfaz del diálogo de configuración."""
        layout = QVBoxLayout(self)
        
        # Título y descripción
        title_label = QLabel("🔐 Configuración de Credenciales Siigo API")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1976d2;
                padding: 10px;
                background-color: #f5f5f5;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(
            "🔧 Configure las credenciales necesarias para conectar DataConta con la API de Siigo. "
            "Estas credenciales se guardarán de forma segura en el archivo de configuración local."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 10px;
                margin-bottom: 15px;
                background-color: #fff3e0;
                border-radius: 5px;
                border-left: 4px solid #ff9800;
            }
        """)
        layout.addWidget(desc_label)
        
        # Formulario de configuración
        form_group = QGroupBox("📝 Credenciales de Conexión")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """)
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 25, 20, 20)
        
        # Estilo para campos de entrada
        input_style = """
            QLineEdit {
                padding: 10px 12px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 11pt;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #1976d2;
                background-color: #f8f9fa;
            }
        """
        
        # Campo URL API
        self.api_url_input = QLineEdit()
        self.api_url_input.setStyleSheet(input_style)
        self.api_url_input.setPlaceholderText("https://api.siigo.com")
        form_layout.addRow("🌐 URL de la API:", self.api_url_input)
        
        # Campo Usuario
        self.user_input = QLineEdit()
        self.user_input.setStyleSheet(input_style)
        self.user_input.setPlaceholderText("usuario@ejemplo.com")
        form_layout.addRow("👤 Usuario/Email:", self.user_input)
        
        # Campo Access Key
        self.access_key_input = QLineEdit()
        self.access_key_input.setStyleSheet(input_style)
        self.access_key_input.setPlaceholderText("Su clave de acceso API")
        self.access_key_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("🔑 Access Key:", self.access_key_input)
        
        # Campo Partner ID
        self.partner_id_input = QLineEdit()
        self.partner_id_input.setStyleSheet(input_style)
        self.partner_id_input.setPlaceholderText("SandboxSiigoAPI")
        form_layout.addRow("🏢 Partner ID:", self.partner_id_input)
        
        layout.addWidget(form_group)
        
        # Botón para mostrar/ocultar Access Key
        show_key_btn = QPushButton("👁️ Mostrar/Ocultar Access Key")
        show_key_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #495057;
                border: 1px solid #dee2e6;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        show_key_btn.clicked.connect(self._toggle_access_key_visibility)
        layout.addWidget(show_key_btn)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        # Botón probar conexión
        test_btn = QPushButton("🔗 Probar Conexión")
        test_btn.setToolTip("Verificar que las credenciales funcionen")
        test_btn.clicked.connect(self._test_connection)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        button_layout.addWidget(test_btn)
        
        # Botón guardar
        save_btn = QPushButton("💾 Guardar Configuración")
        save_btn.clicked.connect(self._save_config)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        # Botón cancelar
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Información adicional
        info_label = QLabel(
            "💡 Nota: Las credenciales se almacenan localmente en el archivo .env. "
            "Nunca comparta sus credenciales de acceso con terceros."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 10px;
                padding: 10px;
                background-color: #e8f5e8;
                border-radius: 4px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(info_label)
    
    def _load_current_config(self):
        """Cargar configuración actual desde el archivo .env."""
        try:
            env_path = ".env"
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Parsear valores existentes
                for line in content.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'SIIGO_API_URL':
                            self.api_url_input.setText(value)
                        elif key == 'SIIGO_USER':
                            self.user_input.setText(value)
                        elif key == 'SIIGO_ACCESS_KEY':
                            self.access_key_input.setText(value)
                        elif key == 'PARTNER_ID':
                            self.partner_id_input.setText(value)
            else:
                # Valores por defecto si no existe .env
                self.api_url_input.setText("https://api.siigo.com")
                self.partner_id_input.setText("SandboxSiigoAPI")
                
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            # Valores por defecto en caso de error
            self.api_url_input.setText("https://api.siigo.com")
            self.partner_id_input.setText("SandboxSiigoAPI")
    
    def _toggle_access_key_visibility(self):
        """Alternar visibilidad del Access Key."""
        if self.access_key_input.echoMode() == QLineEdit.Password:
            self.access_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.access_key_input.setEchoMode(QLineEdit.Password)
    
    def _test_connection(self):
        """Probar la conexión con las credenciales ingresadas."""
        # Validar que todos los campos estén completos
        if not all([
            self.api_url_input.text().strip(),
            self.user_input.text().strip(),
            self.access_key_input.text().strip(),
            self.partner_id_input.text().strip()
        ]):
            QMessageBox.warning(
                self,
                "⚠️ Campos Incompletos",
                "Por favor, complete todos los campos antes de probar la conexión."
            )
            return
        
        # Mostrar mensaje de prueba (aquí se implementaría la conexión real)
        QMessageBox.information(
            self,
            "🔗 Prueba de Conexión",
            "🔄 Probando conexión con Siigo API...\n\n"
            "🚀 Esta funcionalidad se implementará para hacer una llamada de prueba "
            "a la API de Siigo con las credenciales proporcionadas.\n\n"
            "📊 Por ahora, proceda a guardar la configuración si las credenciales son correctas."
        )
    
    def _save_config(self):
        """Guardar configuración en el archivo .env."""
        try:
            # Validar campos obligatorios
            if not all([
                self.api_url_input.text().strip(),
                self.user_input.text().strip(),
                self.access_key_input.text().strip(),
                self.partner_id_input.text().strip()
            ]):
                QMessageBox.warning(
                    self,
                    "⚠️ Campos Incompletos",
                    "Por favor, complete todos los campos antes de guardar."
                )
                return
            
            # Contenido del archivo .env
            env_content = f"""# Siigo API Configuration
# Configuración con credenciales actualizadas desde DataConta

# Siigo API Configuration (Credenciales configuradas)
SIIGO_API_URL={self.api_url_input.text().strip()}
SIIGO_USER={self.user_input.text().strip()}
SIIGO_ACCESS_KEY={self.access_key_input.text().strip()}
PARTNER_ID={self.partner_id_input.text().strip()}

# License Configuration (Actualizado para nuevo sistema)
LICENSE=pro
LICENSE_URL=https://demo-license-server.local/validate

# Nueva clave de licencia con formato actualizado
# Ejemplo de licencia Professional para testing
LICENSE_KEY=PROF-2024-TEST-DEMO-001A

# Output Configuration
OUTPUT_DIR=./outputs

# Optional: Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=app.log
"""
            
            # Escribir archivo .env
            with open(".env", 'w', encoding='utf-8') as file:
                file.write(env_content)
            
            # Confirmar éxito
            QMessageBox.information(
                self,
                "✅ Configuración Guardada",
                "🎉 Las credenciales de Siigo API se han guardado correctamente.\n\n"
                "📝 Archivo .env actualizado con:\n"
                f"• URL API: {self.api_url_input.text().strip()}\n"
                f"• Usuario: {self.user_input.text().strip()}\n"
                f"• Partner ID: {self.partner_id_input.text().strip()}\n\n"
                "🔄 Reinicie la aplicación para que los cambios surtan efecto."
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Error",
                f"No se pudo guardar la configuración:\n{str(e)}\n\n"
                "Verifique que tenga permisos de escritura en el directorio."
            )
    
    @staticmethod
    def needs_configuration() -> bool:
        """
        Verificar si se necesita configuración de Siigo API.
        
        Returns:
            bool: True si no existe .env o está vacío/incompleto
        """
        try:
            env_path = ".env"
            if not os.path.exists(env_path):
                return True
            
            # Verificar si tiene las claves necesarias
            with open(env_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            if not content:
                return True
            
            # Verificar claves obligatorias
            required_keys = ['SIIGO_API_URL', 'SIIGO_USER', 'SIIGO_ACCESS_KEY', 'PARTNER_ID']
            config_keys = []
            
            for line in content.split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key = line.split('=', 1)[0].strip()
                    config_keys.append(key)
            
            # Si falta alguna clave obligatoria
            return not all(key in config_keys for key in required_keys)
            
        except Exception:
            # En caso de error, asumir que se necesita configuración
            return True
    
    @staticmethod
    def auto_open_if_needed(parent=None) -> bool:
        """
        Abrir automáticamente el configurador si es necesario.
        
        Args:
            parent: Widget padre para el diálogo
            
        Returns:
            bool: True si se abrió y configuró exitosamente
        """
        if SiigoConfigDialog.needs_configuration():
            try:
                dialog = SiigoConfigDialog(parent)
                dialog.setWindowTitle("🔐 Configuración Inicial - Siigo API")
                
                # Mostrar mensaje explicativo
                QMessageBox.information(
                    parent if parent else None,
                    "⚙️ Configuración Requerida",
                    "🔧 <b>Configuración Inicial de DataConta</b><br><br>"
                    "📋 Para conectar con Siigo API, necesita configurar "
                    "las credenciales de acceso.<br><br>"
                    "🔐 A continuación se abrirá el configurador donde podrá "
                    "ingresar sus credenciales de forma segura.<br><br>"
                    "💡 <i>Puede omitir esta configuración y hacerla más tarde "
                    "desde el menú de Ayuda.</i>"
                )
                
                result = dialog.exec()
                return result == QDialog.Accepted
                
            except Exception:
                return False
        
        return True  # Ya está configurado


class LogViewerDialog(QDialog):
    """
    Diálogo especializado para mostrar logs de actividad del sistema.
    Migrado desde el LogWidget de la parte inferior de la aplicación.
    """
    
    def __init__(self, parent=None):
        """Inicializar el visor de logs en modal."""
        super().__init__(parent)
        self.setWindowTitle("📊 Logs del Sistema - DataConta")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self._setup_ui()
        self._load_logs()
    
    def _setup_ui(self):
        """Configurar la interfaz del diálogo de logs."""
        layout = QVBoxLayout(self)
        
        # Título y descripción
        title_label = QLabel("📊 Log de Actividades del Sistema")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1976d2;
                padding: 10px;
                background-color: #f5f5f5;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(
            "🔍 Visualización en tiempo real de las actividades del sistema, conexiones API, "
            "operaciones de usuario y eventos importantes de DataConta."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(desc_label)
        
        # Área de texto para logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit { 
                background-color: #2c3e50; 
                color: #ecf0f1; 
                font-family: 'Courier New', monospace; 
                font-size: 9pt; 
                border: 2px solid #1976d2;
                border-radius: 5px;
                padding: 10px;
                selection-background-color: #3498db;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Información de archivos de log
        self.files_info = QLabel()
        self.files_info.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 10px;
                padding: 5px;
                background-color: #f9f9f9;
                border-radius: 3px;
                margin-top: 5px;
            }
        """)
        layout.addWidget(self.files_info)
        
        # Botones
        button_layout = QHBoxLayout()
        
        # Botón actualizar
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setToolTip("Recargar logs más recientes")
        refresh_btn.clicked.connect(self._load_logs)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        button_layout.addWidget(refresh_btn)
        
        # Botón limpiar
        clear_btn = QPushButton("🗑️ Limpiar Vista")
        clear_btn.setToolTip("Limpiar contenido de la vista actual")
        clear_btn.clicked.connect(self.log_text.clear)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d84315;
            }
        """)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        # Botón cerrar
        close_btn = QPushButton("✖️ Cerrar")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _load_logs(self):
        """Cargar contenido de logs desde archivos y actividad actual."""
        try:
            # Limpiar contenido actual
            self.log_text.clear()
            
            # Buscar y cargar archivos de log
            log_files = self._get_log_files()
            total_lines = 0
            
            # Mostrar logs más recientes primero
            self.log_text.append("=" * 80)
            self.log_text.append("📊 LOGS DEL SISTEMA DATACONTA - ACTIVIDAD RECIENTE")
            self.log_text.append("=" * 80)
            self.log_text.append("")
            
            # Cargar desde app.log (log principal)
            if os.path.exists('app.log'):
                self.log_text.append("📝 === LOG PRINCIPAL (app.log) ===")
                lines_added = self._load_log_file('app.log', max_lines=100)
                total_lines += lines_added
                self.log_text.append("")
            
            # Cargar logs de GUI más recientes
            gui_logs = [f for f in log_files if 'gui_logs' in f]
            if gui_logs:
                # Tomar el más reciente
                recent_gui = sorted(gui_logs, key=os.path.getmtime)[-1]
                self.log_text.append(f"📱 === LOG GUI RECIENTE ({os.path.basename(recent_gui)}) ===")
                lines_added = self._load_log_file(recent_gui, max_lines=50)
                total_lines += lines_added
                self.log_text.append("")
            
            # Información de archivos encontrados
            files_count = len(log_files)
            self.files_info.setText(
                f"📁 {files_count} archivos de log encontrados • "
                f"📋 {total_lines} líneas cargadas • "
                f"🔄 Última actualización: {self._get_current_timestamp()}"
            )
            
            # Auto-scroll al final
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            
        except Exception as e:
            self.log_text.append(f"❌ Error cargando logs: {str(e)}")
    
    def _load_log_file(self, file_path: str, max_lines: int = 100) -> int:
        """Cargar contenido de un archivo de log específico."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                
            # Tomar las últimas N líneas
            recent_lines = lines[-max_lines:] if len(lines) > max_lines else lines
            
            for line in recent_lines:
                self.log_text.append(line.rstrip())
            
            return len(recent_lines)
            
        except Exception as e:
            self.log_text.append(f"❌ Error leyendo {file_path}: {str(e)}")
            return 0
    
    def _get_log_files(self) -> list:
        """Obtener lista de archivos de log disponibles."""
        log_files = []
        log_dirs = ['logs/', 'cli_logs/', 'gui_logs/', 'test_logs/', 'pro_gui_logs/']
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                files = [f for f in os.listdir(log_dir) if f.endswith('.txt')]
                log_files.extend([os.path.join(log_dir, f) for f in files])
        
        if os.path.exists('app.log'):
            log_files.append('app.log')
        
        return log_files
    
    def _get_current_timestamp(self) -> str:
        """Obtener timestamp actual formateado."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


class AyudaWidget(QWidget):
    """
    Widget especializado para mostrar opciones de ayuda y soporte.
    Siguiendo principios de arquitectura hexagonal y SOLID.
    """
    
    # Señales para comunicación con otros componentes
    documentacion_requested = Signal()
    logs_requested = Signal()
    siigo_config_requested = Signal()
    upgrade_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializar widget de ayuda.
        
        Args:
            parent: Widget padre opcional
        """
        super().__init__(parent)
        self.setObjectName("AyudaWidget")
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Configurar la interfaz de usuario del widget de ayuda."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título principal
        titulo_group = self._create_titulo_section()
        main_layout.addWidget(titulo_group)
        
        # Sección de menús de ayuda
        menus_group = self._create_menus_section()
        main_layout.addWidget(menus_group)
        
        # Espaciador flexible
        main_layout.addStretch()
    
    def _create_titulo_section(self) -> QGroupBox:
        """Crear sección del título principal."""
        titulo_group = QGroupBox("❓ Centro de Ayuda DataConta")
        titulo_group.setStyleSheet("""
            QGroupBox { 
                border: none; 
                font-weight: 700; 
                font-size: 16px;
                color: #1976d2;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        titulo_layout = QVBoxLayout(titulo_group)
        titulo_layout.setContentsMargins(15, 25, 15, 15)
        
        descripcion = QLabel("""
        🎯 Encuentre toda la información y soporte que necesita:
        
        📚 Documentación completa y guías de uso
        ℹ️ Información sobre la aplicación y versión
        📊 Acceso a logs del sistema para diagnóstico
        🚀 Opciones para actualizar a versiones Pro/Enterprise
        """)
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("""
            background-color: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px;
            border: 1px solid #e9ecef;
            color: #495057;
            font-weight: normal;
            font-size: 12px;
            line-height: 1.5;
        """)
        titulo_layout.addWidget(descripcion)
        return titulo_group
    
    def _create_menus_section(self) -> QGroupBox:
        """Crear sección de menús de ayuda."""
        menus_group = QGroupBox("🔧 Opciones de Ayuda")
        menus_group.setStyleSheet("""
            QGroupBox { 
                border: none; 
                font-weight: 700; 
                font-size: 15px;
                color: #2c3e50;
                padding-top: 10px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        menus_layout = QVBoxLayout(menus_group)
        menus_layout.setSpacing(12)
        menus_layout.setContentsMargins(15, 25, 15, 15)
        
        # Estilo común para botones de ayuda
        button_style = self._get_button_style()
        
        # Crear botones de ayuda
        buttons_data = [
            {
                "text": "📚 Documentación",
                "tooltip": self._get_documentacion_tooltip(),
                "handler": self._handle_documentacion,
                "style": button_style
            },
            {
                "text": "ℹ️ Acerca de DataConta",
                "tooltip": self._get_acerca_de_tooltip(),
                "handler": self._handle_acerca_de,
                "style": button_style
            },
            {
                "text": "📊 Ver Logs del Sistema",
                "tooltip": self._get_logs_tooltip(),
                "handler": self._handle_logs,
                "style": button_style
            },
            {
                "text": "⚙️ Configurar Siigo API",
                "tooltip": self._get_siigo_config_tooltip(),
                "handler": self._handle_siigo_config,
                "style": self._get_siigo_config_button_style()
            },
            {
                "text": "🚀 Actualizar a Pro/Enterprise",
                "tooltip": self._get_upgrade_tooltip(),
                "handler": self._handle_upgrade,
                "style": self._get_upgrade_button_style()
            }
        ]
        
        for button_data in buttons_data:
            button = self._create_help_button(**button_data)
            menus_layout.addWidget(button)
        
        return menus_group
    
    def _create_help_button(self, text: str, tooltip: str, handler, style: str) -> QPushButton:
        """Crear un botón de ayuda con configuración específica."""
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.setStyleSheet(style)
        button.clicked.connect(handler)
        return button
    
    def _get_button_style(self) -> str:
        """Obtener estilo común para botones de ayuda."""
        return """
            QPushButton { 
                background-color: #ffffff;
                color: #495057;
                padding: 15px 20px; 
                border: 2px solid #dee2e6;
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 12pt;
                text-align: left;
                min-height: 40px;
            }
            QPushButton:hover { 
                background-color: #f8f9fa;
                border-color: #1976d2;
                color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #e3f2fd;
            }
        """
    
    def _get_upgrade_button_style(self) -> str:
        """Obtener estilo especial para botón de upgrade."""
        base_style = self._get_button_style()
        return base_style.replace("#ffffff", "#fff3e0") \
                         .replace("#dee2e6", "#ff9800") \
                         .replace("#1976d2", "#f57c00") \
                         .replace("#f8f9fa", "#ffe0b2")
    
    def _get_siigo_config_button_style(self) -> str:
        """Obtener estilo especial para botón de configuración Siigo."""
        base_style = self._get_button_style()
        return base_style.replace("#ffffff", "#f3e5f5") \
                         .replace("#dee2e6", "#9c27b0") \
                         .replace("#1976d2", "#7b1fa2") \
                         .replace("#f8f9fa", "#e1bee7")
    
    def _get_documentacion_tooltip(self) -> str:
        """Obtener tooltip para botón de documentación."""
        return (
            "📚 Acceder a la documentación completa:\n"
            "• Guía de usuario paso a paso\n"
            "• Manual de funcionalidades\n"
            "• Preguntas frecuentes (FAQ)\n"
            "• Tutoriales y ejemplos\n\n"
            "🔗 Abre la documentación en el navegador"
        )
    
    def _get_acerca_de_tooltip(self) -> str:
        """Obtener tooltip para botón acerca de."""
        return (
            "ℹ️ Información sobre la aplicación:\n"
            "• Versión actual del software\n"
            "• Información del desarrollador\n"
            "• Licencias y términos de uso\n"
            "• Créditos y reconocimientos\n\n"
            "📋 Muestra ventana con información detallada"
        )
    
    def _get_logs_tooltip(self) -> str:
        """Obtener tooltip para botón de logs."""
        return (
            "📊 Acceder a los logs del sistema:\n"
            "• Logs de ejecución actual\n"
            "• Historial de errores\n"
            "• Logs de conexiones API\n"
            "• Diagnóstico de problemas\n\n"
            "🔍 Útil para soporte técnico"
        )
    
    def _get_siigo_config_tooltip(self) -> str:
        """Obtener tooltip para botón de configuración Siigo."""
        return (
            "⚙️ Configurar credenciales de Siigo API:\n"
            "• URL del servidor API\n"
            "• Usuario y credenciales de acceso\n"
            "• Partner ID de integración\n"
            "• Validación de conectividad\n\n"
            "🔐 Gestiona tu conexión con Siigo de forma segura"
        )
    
    def _get_upgrade_tooltip(self) -> str:
        """Obtener tooltip para botón de upgrade."""
        return (
            "🚀 Opciones de actualización:\n"
            "• DataConta Pro: Funcionalidades avanzadas\n"
            "• DataConta Enterprise: Para empresas\n"
            "• Comparación de versiones\n"
            "• Precios y licenciamiento\n\n"
            "💎 Desbloquea todas las funcionalidades"
        )
    
    def _connect_signals(self) -> None:
        """Conectar señales internas."""
        # Las señales ya están conectadas en _create_help_button
        pass
    
    # ==================== Handlers para acciones de ayuda ====================
    
    def _handle_documentacion(self) -> None:
        """Manejar clic en Documentación."""
        QMessageBox.information(
            self,
            "📚 Documentación",
            "🔗 Abriendo documentación de DataConta...\n\n"
            "📖 La documentación incluye:\n"
            "• Manual de usuario completo\n"
            "• Guía de configuración API Siigo\n"
            "• Resolución de problemas comunes\n"
            "• Ejemplos de uso y mejores prácticas\n\n"
            "🌐 Se abrirá en su navegador web por defecto."
        )
        # Emitir señal para posible manejo externo
        self.documentacion_requested.emit()
    
    def _handle_acerca_de(self) -> None:
        """Manejar clic en Acerca de."""
        QMessageBox.about(
            self,
            "ℹ️ Acerca de DataConta",
            "🏢 <b>DataConta FREE</b><br>"
            "📊 Sistema de Gestión y Análisis de Facturas<br><br>"
            "<b>Versión:</b> 2.0.0 FREE<br>"
            "<b>Arquitectura:</b> No Monolítica (Hexagonal)<br>"
            "<b>API:</b> Siigo Integration<br>"
            "<b>Tecnología:</b> Python + PySide6<br><br>"
            "<b>Desarrollado por:</b><br>"
            "🏪 WebcolGroup<br>"
            "📧 Contacto: info@webcolgroup.com<br><br>"
            "<b>Licencia:</b> Uso comercial limitado<br>"
            "<b>Copyright:</b> © 2025 WebcolGroup<br><br>"
            "🚀 <i>Actualice a PRO para funcionalidades avanzadas</i>"
        )
    
    def _handle_logs(self) -> None:
        """Manejar clic en Logs - Abrir modal con visualización completa."""
        try:
            # Crear y mostrar el diálogo de logs
            log_dialog = LogViewerDialog(self)
            log_dialog.exec()
            
            # Emitir señal para posible manejo externo
            self.logs_requested.emit()
            
        except Exception as e:
            # Fallback al mensaje simple si hay error
            QMessageBox.critical(
                self,
                "❌ Error",
                f"No se pudo abrir el visor de logs:\n{str(e)}\n\n"
                "Por favor, verifique que los archivos de log estén accesibles."
            )
    
    def _handle_siigo_config(self) -> None:
        """Manejar clic en Configurar Siigo API - Abrir modal de configuración."""
        try:
            # Crear y mostrar el diálogo de configuración Siigo
            config_dialog = SiigoConfigDialog(self)
            result = config_dialog.exec()
            
            if result == QDialog.Accepted:
                # Configuración guardada exitosamente
                QMessageBox.information(
                    self,
                    "✅ Configuración Aplicada",
                    "🎉 La configuración de Siigo API ha sido aplicada correctamente.\n\n"
                    "🔄 Para que los cambios surtan efecto completamente, "
                    "es recomendable reiniciar la aplicación.\n\n"
                    "🚀 ¡DataConta está listo para conectar con Siigo!"
                )
            
            # Emitir señal para posible manejo externo
            self.siigo_config_requested.emit()
            
        except Exception as e:
            # Fallback al mensaje de error si hay problemas
            QMessageBox.critical(
                self,
                "❌ Error de Configuración",
                f"No se pudo abrir el configurador de Siigo API:\n{str(e)}\n\n"
                "Por favor, verifique los permisos del sistema y vuelva a intentar."
            )
    
    def _handle_upgrade(self) -> None:
        """Manejar clic en Actualizar a Pro/Enterprise."""
        reply = QMessageBox.question(
            self,
            "🚀 Actualizar DataConta",
            "💎 <b>Actualice a DataConta PRO/Enterprise</b><br><br>"
            "<b>🏆 DataConta PRO incluye:</b><br>"
            "• 📊 Reportes avanzados y dashboards<br>"
            "• 🤖 Automatización de procesos<br>"
            "• 📈 Análisis predictivo de ventas<br>"
            "• 🔄 Sincronización en tiempo real<br>"
            "• 🎯 Alertas personalizables<br><br>"
            "<b>🏢 DataConta Enterprise incluye:</b><br>"
            "• 👥 Gestión multi-usuario<br>"
            "• 🔐 Seguridad empresarial<br>"
            "• ☁️ Despliegue en la nube<br>"
            "• 🆘 Soporte técnico 24/7<br>"
            "• 🔧 Personalización avanzada<br><br>"
            "¿Desea obtener más información sobre las versiones PRO?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self._show_contact_info()
        
        # Emitir señal para posible manejo externo
        self.upgrade_requested.emit()
    
    def _show_contact_info(self) -> None:
        """Mostrar información de contacto comercial."""
        QMessageBox.information(
            self,
            "📞 Contacto Comercial",
            "🏪 <b>Contacte con WebcolGroup</b><br><br>"
            "📧 <b>Email:</b> ventas@webcolgroup.com<br>"
            "📱 <b>WhatsApp:</b> +57 300 123 4567<br>"
            "🌐 <b>Web:</b> www.webcolgroup.com<br><br>"
            "⏰ <b>Horario de atención:</b><br>"
            "Lunes a Viernes: 8:00 AM - 6:00 PM<br>"
            "Sábados: 9:00 AM - 1:00 PM<br><br>"
            "🎁 <b>Oferta especial:</b><br>"
            "¡Descuento del 30% por actualización desde FREE!<br><br>"
            "💼 Nuestro equipo comercial se pondrá en contacto."
        )
    
    def _scan_log_files(self) -> list:
        """Escanear y obtener lista de archivos de log."""
        log_files = []
        log_dirs = ['logs/', 'cli_logs/', 'gui_logs/', 'test_logs/', 'pro_gui_logs/']
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                files = [f for f in os.listdir(log_dir) if f.endswith('.txt')]
                log_files.extend([f"{log_dir}{f}" for f in files])
        
        if os.path.exists('app.log'):
            log_files.append('app.log')
            
        return log_files
    
    def _format_log_files_list(self, log_files: list) -> str:
        """Formatear lista de archivos de log para mostrar."""
        files_text = "\n".join([f"• {f}" for f in log_files[:10]])  # Mostrar max 10
        if len(log_files) > 10:
            files_text += f"\n... y {len(log_files) - 10} archivos más"
        return files_text
    
    # ==================== Métodos públicos para integración ====================
    
    def refresh_logs_info(self) -> None:
        """Actualizar información de logs (llamado externamente si es necesario)."""
        # Método para futuras expansiones si se necesita actualizar info dinámicamente
        pass
    
    def set_version_info(self, version: str, build: str = "") -> None:
        """Actualizar información de versión (para futuras expansiones)."""
        # Método para futuras expansiones si se necesita versión dinámica
        pass