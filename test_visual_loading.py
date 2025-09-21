#!/usr/bin/env python3
"""
Test visual del sistema de loading
Verifica que el loader sea visible durante un proceso simulado
"""

import sys
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, QThread, Signal
from src.presentation.widgets.loading_widget import LoadingMixin

class WorkerThread(QThread):
    """Thread para simular trabajo en segundo plano"""
    finished = Signal()
    
    def run(self):
        # Simular trabajo pesado
        time.sleep(3)
        self.finished.emit()

class TestMainWindow(QMainWindow, LoadingMixin):
    """Ventana de prueba con sistema de loading"""
    
    def __init__(self):
        super().__init__()
        self.init_loading()
        self.setWindowTitle("Test Visual Loading")
        self.setGeometry(200, 200, 600, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Botón de prueba
        self.test_button = QPushButton("🧪 Iniciar Proceso de Prueba")
        self.test_button.clicked.connect(self.start_test_process)
        layout.addWidget(self.test_button)
        
        # Worker thread
        self.worker = None
    
    def start_test_process(self):
        """Inicia un proceso de prueba con loading"""
        print("🧪 Iniciando proceso de prueba...")
        
        # Mostrar loader
        self.show_loading("🧪 Procesando datos de prueba...")
        self.test_button.setEnabled(False)
        
        # Crear y configurar worker thread
        self.worker = WorkerThread()
        self.worker.finished.connect(self.on_process_finished)
        self.worker.start()
    
    def on_process_finished(self):
        """Callback cuando el proceso termina"""
        print("✅ Proceso de prueba completado")
        
        # Ocultar loader
        self.hide_loading()
        self.test_button.setEnabled(True)
        
        # Limpiar worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Crear y mostrar ventana
    window = TestMainWindow()
    window.show()
    
    print("🧪 Test Visual Loading iniciado")
    print("📝 Instrucciones:")
    print("   1. Haz clic en el botón 'Iniciar Proceso de Prueba'")
    print("   2. Deberías ver un loader semi-transparente con spinner")
    print("   3. El loader desaparecerá después de 3 segundos")
    print("   4. Cierra la ventana para terminar el test")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()