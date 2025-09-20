"""
API Safety Modal - Modal especializado para confirmar operaciones peligrosas en API Siigo
Parte del sistema de seguridad para evitar modificaciones no autorizadas

Responsabilidad única: Confirmar operaciones POST/PUT/DELETE antes de ejecutarlas
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QTextEdit, QCheckBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPalette
import json


class OperationType(Enum):
    """Tipos de operaciones que requieren confirmación."""
    POST = "POST"
    PUT = "PUT" 
    PATCH = "PATCH"
    DELETE = "DELETE"


class APISafetyModal(QDialog):
    """
    Modal de seguridad para confirmar operaciones peligrosas en API Siigo.
    
    Principios SOLID aplicados:
    - SRP: Solo maneja confirmación de operaciones API peligrosas
    - OCP: Extensible para nuevos tipos de operaciones
    - LSP: Substituble como cualquier QDialog
    - ISP: Interfaz específica para confirmación de seguridad
    - DIP: No depende de implementaciones concretas de API
    """
    
    # Señales para comunicación
    operation_approved = Signal(dict)  # Emitir cuando se aprueba la operación
    operation_rejected = Signal(dict)  # Emitir cuando se rechaza la operación
    
    def __init__(self, operation_type: OperationType, endpoint: str, 
                 payload: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        
        self.operation_type = operation_type
        self.endpoint = endpoint
        self.payload = payload or {}
        self.user_approved = False
        
        self.init_ui()
        self.setup_modal_properties()
    
    def setup_modal_properties(self):
        """Configurar propiedades del modal."""
        self.setModal(True)
        self.setWindowTitle("🛡️ Confirmación de Operación API - DataConta")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        # Centrar en la pantalla
        self.move_to_center()
    
    def move_to_center(self):
        """Centrar el modal en la pantalla."""
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def init_ui(self):
        """Inicializar interfaz del modal."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header de alerta
        header = self._create_alert_header()
        layout.addWidget(header)
        
        # Información de la operación
        operation_info = self._create_operation_info()
        layout.addWidget(operation_info)
        
        # Detalles del payload (si existe)
        if self.payload:
            payload_section = self._create_payload_section()
            layout.addWidget(payload_section)
        
        # Advertencias de seguridad
        warnings_section = self._create_warnings_section()
        layout.addWidget(warnings_section)
        
        # Checkbox de confirmación
        confirmation_checkbox = self._create_confirmation_checkbox()
        layout.addWidget(confirmation_checkbox)
        
        # Botones de acción
        buttons_section = self._create_buttons_section()
        layout.addWidget(buttons_section)
    
    def _create_alert_header(self) -> QWidget:
        """Crear header de alerta principal."""
        header_widget = QWidget()
        layout = QVBoxLayout(header_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icono y título según tipo de operación
        icon_text, color, title = self._get_operation_styling()
        
        # Título principal
        title_label = QLabel(f"{icon_text} {title}")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {color};
                margin-bottom: 10px;
                padding: 15px;
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid {color};
                border-radius: 10px;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtítulo explicativo
        subtitle_label = QLabel("Esta operación modificará datos en Siigo API")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                margin-bottom: 10px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        return header_widget
    
    def _create_operation_info(self) -> QWidget:
        """Crear sección de información de la operación."""
        group = QGroupBox("📋 Detalles de la Operación")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #1976d2;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Método HTTP
        method_label = QLabel(f"🔧 Método: {self.operation_type.value}")
        method_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
        layout.addWidget(method_label)
        
        # Endpoint
        endpoint_label = QLabel(f"🎯 Endpoint: {self.endpoint}")
        endpoint_label.setStyleSheet("font-size: 14px; margin: 5px; word-wrap: break-word;")
        endpoint_label.setWordWrap(True)
        layout.addWidget(endpoint_label)
        
        # Timestamp
        from datetime import datetime
        timestamp_label = QLabel(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        timestamp_label.setStyleSheet("font-size: 12px; color: #666; margin: 5px;")
        layout.addWidget(timestamp_label)
        
        return group
    
    def _create_payload_section(self) -> QWidget:
        """Crear sección de payload/datos."""
        group = QGroupBox("📦 Datos a Enviar")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #1976d2;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Texto con formato JSON del payload
        payload_text = QTextEdit()
        payload_text.setReadOnly(True)
        payload_text.setMaximumHeight(150)
        payload_text.setPlainText(json.dumps(self.payload, indent=2, ensure_ascii=False))
        payload_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        layout.addWidget(payload_text)
        
        return group
    
    def _create_warnings_section(self) -> QWidget:
        """Crear sección de advertencias de seguridad."""
        group = QGroupBox("⚠️ Advertencias de Seguridad")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #d32f2f;
                border: 2px solid #d32f2f;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        warnings = self._get_operation_warnings()
        
        for warning in warnings:
            warning_label = QLabel(f"⚠️ {warning}")
            warning_label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #d32f2f;
                    background-color: rgba(211, 47, 47, 0.1);
                    padding: 8px;
                    border-radius: 4px;
                    margin: 3px;
                }
            """)
            warning_label.setWordWrap(True)
            layout.addWidget(warning_label)
        
        return group
    
    def _create_confirmation_checkbox(self) -> QWidget:
        """Crear checkbox de confirmación obligatorio."""
        checkbox_widget = QWidget()
        layout = QVBoxLayout(checkbox_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        self.confirmation_checkbox = QCheckBox(
            "✅ Entiendo las implicaciones y autorizo esta operación"
        )
        self.confirmation_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
                color: #1976d2;
                padding: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.confirmation_checkbox.stateChanged.connect(self._on_confirmation_changed)
        layout.addWidget(self.confirmation_checkbox)
        
        return checkbox_widget
    
    def _create_buttons_section(self) -> QWidget:
        """Crear botones de acción."""
        buttons_widget = QWidget()
        layout = QHBoxLayout(buttons_widget)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        # Botón Cancelar
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 25px;
                border: none;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        cancel_button.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(cancel_button)
        
        # Botón Aprobar
        self.approve_button = QPushButton("✅ Aprobar y Ejecutar")
        self.approve_button.setEnabled(False)  # Deshabilitado hasta que se marque el checkbox
        self.approve_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 25px;
                border: none;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover:enabled {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.approve_button.clicked.connect(self._on_approve_clicked)
        layout.addWidget(self.approve_button)
        
        return buttons_widget
    
    def _get_operation_styling(self) -> tuple:
        """Obtener estilos según el tipo de operación."""
        styling_map = {
            OperationType.POST: ("📝", "#2196f3", "Crear Nuevo Registro"),
            OperationType.PUT: ("✏️", "#ff9800", "Actualizar Registro Completo"), 
            OperationType.PATCH: ("🔧", "#ff9800", "Actualizar Registro Parcial"),
            OperationType.DELETE: ("🗑️", "#f44336", "ELIMINAR Registro")
        }
        return styling_map.get(self.operation_type, ("⚠️", "#757575", "Operación Desconocida"))
    
    def _get_operation_warnings(self) -> list:
        """Obtener advertencias específicas por tipo de operación."""
        warnings_map = {
            OperationType.POST: [
                "Se creará un nuevo registro en Siigo",
                "Esta acción puede afectar reportes y balances",
                "Verifique que los datos sean correctos antes de continuar",
                "La operación puede ser irreversible según la configuración de Siigo"
            ],
            OperationType.PUT: [
                "Se reemplazará completamente el registro existente",
                "Todos los campos del registro serán sobrescritos", 
                "Esta acción puede afectar reportes históricos",
                "Asegúrese de tener respaldo de los datos actuales"
            ],
            OperationType.PATCH: [
                "Se modificarán campos específicos del registro",
                "Los cambios pueden afectar cálculos automáticos",
                "Esta acción puede impactar reportes dependientes", 
                "Verifique que las modificaciones sean correctas"
            ],
            OperationType.DELETE: [
                "⚠️ PELIGRO: Se eliminará permanentemente el registro",
                "⚠️ Esta acción NO puede ser deshecha",
                "⚠️ Puede afectar la integridad referencial de otros registros",
                "⚠️ Respalde los datos antes de proceder"
            ]
        }
        return warnings_map.get(self.operation_type, ["Operación no reconocida"])
    
    def _on_confirmation_changed(self, state):
        """Manejar cambio en checkbox de confirmación."""
        self.approve_button.setEnabled(state == Qt.Checked)
    
    def _on_cancel_clicked(self):
        """Manejar click en botón cancelar."""
        self.user_approved = False
        operation_data = {
            'type': self.operation_type.value,
            'endpoint': self.endpoint,
            'payload': self.payload,
            'approved': False,
            'timestamp': self._get_timestamp()
        }
        self.operation_rejected.emit(operation_data)
        self.reject()
    
    def _on_approve_clicked(self):
        """Manejar click en botón aprobar."""
        self.user_approved = True
        operation_data = {
            'type': self.operation_type.value,
            'endpoint': self.endpoint, 
            'payload': self.payload,
            'approved': True,
            'timestamp': self._get_timestamp()
        }
        self.operation_approved.emit(operation_data)
        self.accept()
    
    def _get_timestamp(self) -> str:
        """Obtener timestamp actual."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_user_approval(self) -> bool:
        """Obtener resultado de la aprobación del usuario."""
        return self.user_approved
    
    @staticmethod
    def confirm_operation(operation_type: OperationType, endpoint: str, 
                         payload: Dict[str, Any] = None, parent=None) -> bool:
        """
        Método estático para mostrar modal de confirmación.
        
        Returns:
            bool: True si el usuario aprueba, False si cancela
        """
        modal = APISafetyModal(operation_type, endpoint, payload, parent)
        result = modal.exec()
        return result == QDialog.Accepted and modal.get_user_approval()