"""
Script de prueba para diagnosticar problemas con KPIs básicos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import QApplication
    from src.presentation.widgets.kpi_widget import KPIWidget
    from src.presentation.widgets.dashboard_widget import DashboardWidget
    
    print("✅ Importaciones exitosas")
    
    app = QApplication([])
    
    # Probar KPIWidget directamente
    print("🔍 Creando KPIWidget...")
    kpi_widget = KPIWidget()
    print("✅ KPIWidget creado exitosamente")
    
    # Probar actualización de KPIs
    print("🔍 Probando actualización de KPIs...")
    kpi_widget.update_kpis()
    print("✅ Actualización de KPIs exitosa")
    
    # Probar DashboardWidget
    print("🔍 Creando DashboardWidget...")
    dashboard = DashboardWidget()
    print("✅ DashboardWidget creado exitosamente")
    
    # Verificar que el KPIWidget está integrado correctamente
    if hasattr(dashboard, 'kpi_widget') and dashboard.kpi_widget:
        print("✅ KPIWidget integrado correctamente en DashboardWidget")
        
        # Probar actualización a través del dashboard
        print("🔍 Probando actualización KPIs a través de DashboardWidget...")
        dashboard.update_kpis({"test": "data"}, False)
        print("✅ Actualización a través de DashboardWidget exitosa")
    else:
        print("❌ KPIWidget NO está integrado correctamente")
    
    print("✅ Todas las pruebas de KPIs básicos completadas exitosamente")
    
except Exception as e:
    print(f"❌ Error en pruebas de KPIs: {e}")
    import traceback
    traceback.print_exc()