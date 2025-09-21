"""
Loading widget with spinner animation for background operations.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QThread, Signal
from PySide6.QtGui import QMovie, QPixmap, QPainter, QPen
import math


class SpinnerWidget(QWidget):
    """Custom spinning widget for loading indication."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.angle = 0
        
        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
    def start_spinning(self):
        """Start the spinning animation."""
        self.timer.start(50)  # Update every 50ms for smooth animation
        
    def stop_spinning(self):
        """Stop the spinning animation."""
        self.timer.stop()
        
    def rotate(self):
        """Rotate the spinner."""
        self.angle = (self.angle + 10) % 360
        self.update()
        
    def paintEvent(self, event):
        """Paint the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up the painter
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        
        # Draw the spinner
        pen = QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        
        for i in range(8):
            # Calculate opacity based on position
            opacity = 1.0 - (i * 0.1)
            pen.setColor(f"rgba(0, 122, 255, {int(opacity * 255)})")
            painter.setPen(pen)
            
            # Draw line
            painter.drawLine(0, -15, 0, -10)
            painter.rotate(45)


class LoadingWidget(QWidget):
    """
    Loading widget with spinner and customizable message.
    Shows a semi-transparent overlay with spinner and status text.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoadingWidget")
        self.setupUI()
        self.hide()  # Hidden by default
        
    def setupUI(self):
        """Set up the loading widget UI."""
        # Set object name for styling
        self.setObjectName("LoadingWidget")
        
        # Make widget fully cover parent and block events
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget#LoadingWidget {
                background-color: rgba(255, 255, 255, 40);
                border: none;
            }
            QLabel#LoadingMessage {
                color: #333333;
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(255, 255, 255, 220);
                padding: 8px 15px;
                border-radius: 8px;
                border: 1px solid #cccccc;
            }
            QFrame#LoadingFrame {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 15px;
                border: 2px solid #4A90E2;
                padding: 20px;
                min-width: 250px;
                max-width: 400px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Loading frame
        self.loading_frame = QFrame()
        self.loading_frame.setObjectName("LoadingFrame")
        self.loading_frame.setObjectName("LoadingFrame")
        self.loading_frame.setFixedSize(250, 120)
        
        # Frame layout
        frame_layout = QVBoxLayout(self.loading_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        frame_layout.setAlignment(Qt.AlignCenter)
        
        # Spinner widget
        self.spinner = SpinnerWidget()
        spinner_layout = QHBoxLayout()
        spinner_layout.addStretch()
        spinner_layout.addWidget(self.spinner)
        spinner_layout.addStretch()
        frame_layout.addLayout(spinner_layout)
        
        # Loading message
        self.message_label = QLabel("Procesando...")
        self.message_label.setObjectName("LoadingMessage")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: #333; font-size: 12px; font-weight: bold;")
        frame_layout.addWidget(self.message_label)
        
        main_layout.addWidget(self.loading_frame)
        
    def show_loading(self, message="Procesando..."):
        """Show the loading widget with optional custom message."""
        print(f"🔍 LoadingWidget.show_loading called: '{message}'")
        self.message_label.setText(message)
        self.spinner.start_spinning()
        
        # Ensure widget is properly positioned and visible
        self.setWindowFlags(Qt.Widget)  # Ensure it's a normal widget
        self.show()
        self.raise_()  # Bring to front
        self.activateWindow()  # Activate the widget
        
        print(f"🔍 LoadingWidget visible: {self.isVisible()}")
        print(f"🔍 LoadingWidget geometry: {self.geometry()}")
        print(f"🔍 LoadingWidget parent: {self.parent()}")
        print("✅ LoadingWidget.show_loading completed")
        
    def hide_loading(self):
        """Hide the loading widget."""
        self.spinner.stop_spinning()
        self.hide()
        
    def update_message(self, message):
        """Update the loading message."""
        self.message_label.setText(message)
        
    def resizeEvent(self, event):
        """Handle resize event to keep loading centered."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_frame'):
            # Center the loading frame
            self.setGeometry(0, 0, self.parent().width() if self.parent() else 800, 
                           self.parent().height() if self.parent() else 600)


class LoadingMixin:
    """
    Mixin to add loading functionality to any widget.
    """
    
    def init_loading(self):
        """Initialize the loading widget."""
        if not hasattr(self, '_loading_widget'):
            self._loading_widget = LoadingWidget(self)
            
    def show_loading(self, message="Procesando..."):
        """Show loading overlay."""
        print(f"🔍 LoadingMixin.show_loading called: '{message}'")
        self.init_loading()
        
        # Force update geometry and ensure proper positioning
        self.update()  # Force widget update
        self._loading_widget.setGeometry(0, 0, self.width(), self.height())
        self._loading_widget.setParent(self)  # Ensure proper parent
        
        print(f"🔍 Parent widget geometry: {self.width()}x{self.height()}")
        print(f"🔍 Loading widget geometry: {self._loading_widget.geometry()}")
        
        self._loading_widget.show_loading(message)
        
        # Force repaint to ensure visibility
        self._loading_widget.update()
        self._loading_widget.repaint()
        
        print("✅ LoadingMixin.show_loading completed")
        
    def hide_loading(self):
        """Hide loading overlay."""
        if hasattr(self, '_loading_widget'):
            self._loading_widget.hide_loading()
            
    def update_loading_message(self, message):
        """Update the loading message."""
        if hasattr(self, '_loading_widget'):
            self._loading_widget.update_message(message)
            
    def resizeEvent(self, event):
        """Handle resize to keep loading centered."""
        super().resizeEvent(event)
        if hasattr(self, '_loading_widget'):
            self._loading_widget.setGeometry(0, 0, self.width(), self.height())