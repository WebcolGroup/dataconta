#!/usr/bin/env python3
"""
Test simple para verificar el funcionamiento del LoadingMixin
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow
from src.presentation.widgets.loading_widget import LoadingMixin

class TestWindow(QMainWindow, LoadingMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Loading")
        self.setGeometry(100, 100, 400, 300)
        
        # Inicializar loading
        self.init_loading()
        
        # Mostrar loading después de 1 segundo
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, self.test_loading)
        
    def test_loading(self):
        print("🔍 Testing loading...")
        self.show_loading("Probando loader...")
        
        # Ocultar después de 3 segundos
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, self.hide_loading)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    print("✅ Ventana de test mostrada")
    print("🔄 Esperando 1 segundo para mostrar loading...")
    
    app.exec()