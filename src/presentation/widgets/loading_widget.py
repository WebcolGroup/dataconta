from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen
import math


class ModernSpinner(QWidget):
    """Spinner circular minimalista para indicar carga."""

    def __init__(self, parent=None, size=40, line_count=12, line_width=3, color="#1976d2"):
        super().__init__(parent)
        self.size = size
        self.line_count = line_count
        self.line_width = line_width
        self.color = QColor(color)
        self.angle = 0
        self.setFixedSize(size, size)

        # Timer para rotación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)

    def start(self):
        self.timer.start(60)  # más suave
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)

        for i in range(self.line_count):
            alpha = int(255 * (i + 1) / self.line_count)
            pen = QPen(self.color, self.line_width)
            pen.setCapStyle(Qt.RoundCap)  # Usar setCapStyle en lugar del parámetro cap
            pen.setColor(QColor(self.color.red(), self.color.green(), self.color.blue(), alpha))
            painter.setPen(pen)
            painter.drawLine(0, -self.size // 2 + 5, 0, -self.size // 2 + 15)
            painter.rotate(360 / self.line_count)

        painter.rotate(self.angle)


class LoadingOverlay(QWidget):
    """Overlay moderno con spinner y mensaje."""

    def __init__(self, parent=None, message="Cargando..."):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 180);
            }
            QLabel {
                color: #444;
                font-size: 14px;
                font-weight: 600;
            }
        """)
        self.setGeometry(0, 0, parent.width(), parent.height() if parent else 400)

        # Layout centrado
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Spinner
        self.spinner = ModernSpinner(self, size=40, color="#1976d2")
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        # Mensaje
        self.label = QLabel(message, self)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # Animación fade
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.hide()

    def show_loading(self, message="Cargando..."):
        self.label.setText(message)
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        self.spinner.start()
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        # fade in
        self.fade_anim.stop()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

    def hide_loading(self):
        # fade out
        self.fade_anim.stop()
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self._final_hide)
        self.fade_anim.start()

    def _final_hide(self):
        self.spinner.stop()
        self.hide()

    def resizeEvent(self, event):
        """Mantener el overlay centrado al redimensionar."""
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        super().resizeEvent(event)


class LoadingMixin:
    """Mixin para agregar funcionalidad de loading a cualquier widget."""
    
    def init_loading(self):
        """Inicializar el sistema de loading."""
        if not hasattr(self, '_loading_overlay'):
            self._loading_overlay = LoadingOverlay(self, "Cargando...")
            print("🔍 LoadingMixin.init_loading: Loading overlay inicializado")
    
    def show_loading(self, message="Cargando..."):
        """Mostrar el loading overlay con un mensaje."""
        print(f"🔍 LoadingMixin.show_loading called: '{message}'")
        
        # Asegurar que loading está inicializado
        if not hasattr(self, '_loading_overlay'):
            self.init_loading()
        
        # Debug de geometría
        if hasattr(self, 'geometry'):
            print(f"🔍 Parent widget geometry: {self.width()}x{self.height()}")
            print(f"🔍 Loading widget geometry: {self._loading_overlay.geometry()}")
        
        # Mostrar loading
        self._loading_overlay.show_loading(message)
        print("✅ LoadingMixin.show_loading completed")
    
    def hide_loading(self):
        """Ocultar el loading overlay."""
        print("🔍 LoadingMixin.hide_loading called")
        
        if hasattr(self, '_loading_overlay'):
            self._loading_overlay.hide_loading()
            print("✅ LoadingMixin.hide_loading completed")
        else:
            print("⚠️ LoadingMixin.hide_loading: No loading overlay found")
    
    def update_loading_message(self, message):
        """Actualizar el mensaje del loading."""
        if hasattr(self, '_loading_overlay') and self._loading_overlay.isVisible():
            self._loading_overlay.label.setText(message)
