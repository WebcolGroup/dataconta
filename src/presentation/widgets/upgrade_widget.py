"""
Upgrade Widget - Widget especializado para contenido de Funciones PRO
Parte de la refactorización siguiendo principios SOLID y clean code

Responsabilidad única: UI para mostrar información sobre funciones PRO y upgrades
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont


class UpgradeWidget(QWidget):
    """
    Widget especializado para mostrar información sobre funciones PRO.
    
    Principios SOLID aplicados:
    - SRP: Solo maneja la UI de información de upgrade PRO
    - OCP: Extensible para nuevas funciones PRO
    - LSP: Substituble como cualquier QWidget
    - ISP: Interfaz específica para información de upgrade
    - DIP: No depende de implementaciones concretas
    """
    
    # Señales para comunicación con otros componentes
    upgrade_requested = Signal()
    contact_support_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pro_features = self._load_pro_features()
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz del widget de upgrade."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header principal
        header = self._create_header()
        layout.addWidget(header)
        
        # Sección de beneficios PRO
        benefits_section = self._create_benefits_section()
        layout.addWidget(benefits_section)
        
        # Sección de características PRO
        features_section = self._create_features_section()
        layout.addWidget(features_section)
        
        # Sección de llamada a la acción
        cta_section = self._create_cta_section()
        layout.addWidget(cta_section)
        
        # Spacer para empujar contenido hacia arriba
        layout.addStretch()
    
    def _create_header(self) -> QWidget:
        """Crear header principal del widget."""
        header_widget = QWidget()
        layout = QVBoxLayout(header_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Título principal
        title_label = QLabel("🏆 Funciones PRO")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #1976d2;
                margin-bottom: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Desbloquea todo el potencial de DataConta")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                margin-bottom: 20px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        return header_widget
    
    def _create_benefits_section(self) -> QWidget:
        """Crear sección de beneficios principales."""
        group = QGroupBox("✨ Beneficios Exclusivos")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #1976d2;
                border-radius: 10px;
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
        layout.setSpacing(15)
        
        benefits = [
            "🚀 Análisis financiero avanzado con IA",
            "📊 Reportes personalizados ilimitados",
            "🔄 Sincronización automática con múltiples APIs",
            "💾 Exportación a formatos premium (Excel, PDF, PowerBI)",
            "⚡ Procesamiento masivo de datos sin límites",
            "🔒 Seguridad empresarial y respaldos automáticos",
            "📞 Soporte prioritario 24/7",
            "🎯 Integración con sistemas ERP empresariales"
        ]
        
        for benefit in benefits:
            benefit_label = QLabel(benefit)
            benefit_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #333;
                    padding: 5px;
                    background-color: rgba(25, 118, 210, 0.05);
                    border-radius: 5px;
                }
            """)
            layout.addWidget(benefit_label)
        
        return group
    
    def _create_features_section(self) -> QWidget:
        """Crear sección de características específicas."""
        group = QGroupBox("🛠️ Funcionalidades Avanzadas")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #1976d2;
                border-radius: 10px;
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
        layout.setSpacing(10)
        
        # Crear grid de características
        features_widget = self._create_features_grid()
        layout.addWidget(features_widget)
        
        return group
    
    def _create_features_grid(self) -> QWidget:
        """Crear grid con características PRO."""
        features_widget = QWidget()
        layout = QVBoxLayout(features_widget)
        
        for feature_category, features in self._pro_features.items():
            category_frame = self._create_feature_category(feature_category, features)
            layout.addWidget(category_frame)
        
        return features_widget
    
    def _create_feature_category(self, category: str, features: List[str]) -> QWidget:
        """Crear una categoría de características."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 118, 210, 0.08);
                border: 1px solid rgba(25, 118, 210, 0.3);
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Título de categoría
        category_label = QLabel(category)
        category_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1976d2;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(category_label)
        
        # Lista de características
        for feature in features:
            feature_label = QLabel(f"• {feature}")
            feature_label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #333;
                    margin-left: 15px;
                    margin-bottom: 5px;
                }
            """)
            feature_label.setWordWrap(True)
            layout.addWidget(feature_label)
        
        return frame
    
    def _create_cta_section(self) -> QWidget:
        """Crear sección de llamada a la acción."""
        cta_widget = QWidget()
        layout = QVBoxLayout(cta_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Mensaje de llamada a la acción
        cta_label = QLabel("¿Listo para llevar tu gestión contable al siguiente nivel?")
        cta_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                text-align: center;
                margin: 20px 0;
            }
        """)
        cta_label.setAlignment(Qt.AlignCenter)
        cta_label.setWordWrap(True)
        layout.addWidget(cta_label)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        upgrade_button = self._create_upgrade_button()
        contact_button = self._create_contact_button()
        
        buttons_layout.addWidget(upgrade_button)
        buttons_layout.addWidget(contact_button)
        
        layout.addLayout(buttons_layout)
        
        return cta_widget
    
    def _create_upgrade_button(self) -> QPushButton:
        """Crear botón principal de upgrade."""
        button = QPushButton("🚀 ¡Actualizar a PRO!")
        button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #1565c0;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        button.clicked.connect(self._on_upgrade_clicked)
        return button
    
    def _create_contact_button(self) -> QPushButton:
        """Crear botón de contacto/soporte."""
        button = QPushButton("📞 Contactar Soporte")
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1976d2;
                font-size: 14px;
                font-weight: bold;
                padding: 15px 30px;
                border: 2px solid #1976d2;
                border-radius: 25px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: rgba(25, 118, 210, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(25, 118, 210, 0.2);
            }
        """)
        button.clicked.connect(self._on_contact_clicked)
        return button
    
    def _load_pro_features(self) -> Dict[str, List[str]]:
        """Cargar configuración de características PRO."""
        return {
            "📊 Análisis Avanzado": [
                "Dashboard ejecutivo con KPIs personalizados",
                "Análisis predictivo de flujo de caja",
                "Detección automática de anomalías financieras",
                "Comparativas multiperíodo avanzadas"
            ],
            "🔗 Integraciones Premium": [
                "Conexión directa con bancos (Open Banking)",
                "Sincronización con ERPs empresariales",
                "Integración con plataformas de e-commerce",
                "APIs personalizadas para terceros"
            ],
            "📈 Reportes Ejecutivos": [
                "Reportes personalizados con branding",
                "Automatización de envío de reportes",
                "Plantillas de informes gerenciales",
                "Exportación a PowerBI y Tableau"
            ],
            "🛡️ Seguridad Empresarial": [
                "Autenticación de doble factor",
                "Auditoría completa de accesos",
                "Respaldos automáticos en la nube",
                "Cumplimiento normativo IFRS"
            ]
        }
    
    def _on_upgrade_clicked(self):
        """Manejar click en botón de upgrade."""
        # Emitir señal para que el controlador maneje la lógica
        self.upgrade_requested.emit()
    
    def _on_contact_clicked(self):
        """Manejar click en botón de contacto."""
        # Emitir señal para que el controlador maneje la lógica
        self.contact_support_requested.emit()
    
    def get_current_plan(self) -> str:
        """Obtener plan actual del usuario."""
        # TODO: Implementar lógica para obtener plan actual
        return "FREE"
    
    def update_features(self, new_features: Dict[str, List[str]]):
        """Actualizar características PRO dinámicamente."""
        self._pro_features = new_features
        # TODO: Refrescar UI con nuevas características