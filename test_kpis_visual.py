"""
Script de prueba visual específico para KPIs básicos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    from PySide6.QtCore import QTimer
    from src.presentation.widgets.kpi_widget import KPIWidget
    
    print("✅ Creando aplicación de prueba para KPIs...")
    
    app = QApplication([])
    
    # Crear ventana principal
    window = QMainWindow()
    window.setWindowTitle("Prueba KPIs Básicos - DataConta")
    window.setGeometry(100, 100, 800, 600)
    
    # Widget central
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Crear KPIWidget
    kpi_widget = KPIWidget()
    layout.addWidget(kpi_widget)
    
    window.setCentralWidget(central_widget)
    
    # Función para actualizar KPIs después de un momento
    def actualizar_kpis():
        print("🔍 Actualizando KPIs con datos reales...")
        kpi_widget.update_kpis()
        print("✅ KPIs actualizados en la interfaz visual")
    
    # Timer para actualizar después de 1 segundo
    timer = QTimer()
    timer.singleShot(1000, actualizar_kpis)
    
    print("✅ Ventana de prueba creada. Mostrando interfaz...")
    window.show()
    
    # Ejecutar por 5 segundos para poder ver el resultado
    timer_exit = QTimer()
    timer_exit.singleShot(5000, app.quit)
    
    app.exec()
    print("✅ Prueba visual completada")
    
except Exception as e:
    print(f"❌ Error en prueba visual de KPIs: {e}")
    import traceback
    traceback.print_exc()