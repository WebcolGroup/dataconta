#!/usr/bin/env python3
"""
Script de prueba específico para debuggear la funcionalidad de KPIs
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.application.services.kpi_service import KPIService
from src.application.services.export_service import ExportService
from src.infrastructure.adapters.free_gui_siigo_adapter import FreeGUISiigoAdapter
from src.infrastructure.adapters.console_logger import ConsoleLogger
from src.infrastructure.adapters.file_storage_adapter import FileStorageAdapter
from src.presentation.controllers.free_gui_controller import FreeGUIController

def test_kpi_button_functionality():
    """Probar la funcionalidad completa del botón de KPIs sin GUI."""
    
    print("=" * 80)
    print("🧪 PRUEBA FUNCIONALIDAD BOTÓN KPIs - DATACONTA HEXAGONAL")
    print("=" * 80)
    
    # 1. Inicializar dependencias
    print("1️⃣ Inicializando dependencias...")
    logger = ConsoleLogger()
    file_storage = FileStorageAdapter(output_directory="./outputs", logger=logger)
    siigo_adapter = FreeGUISiigoAdapter(logger=logger)
    
    # 2. Probar autenticación
    print("\n2️⃣ Probando autenticación...")
    auth_result = siigo_adapter.authenticate()
    print(f"   Resultado autenticación: {auth_result}")
    print(f"   Conexión activa: {siigo_adapter.is_connected()}")
    
    if not auth_result:
        print("❌ Error: No se pudo autenticar. Terminando prueba.")
        return False
    
    # 3. Inicializar servicios
    print("\n3️⃣ Inicializando servicios...")
    kpi_service = KPIService(
        invoice_repository=siigo_adapter,
        logger=logger,
        file_storage=file_storage
    )
    
    export_service = ExportService(
        invoice_repository=siigo_adapter,
        logger=logger,
        file_storage=file_storage
    )
    
    # 4. Inicializar controlador
    print("\n4️⃣ Inicializando controlador...")
    controller = FreeGUIController(
        kpi_service=kpi_service,
        export_service=export_service,
        invoice_repository=siigo_adapter,
        logger=logger,
        file_storage=file_storage
    )
    
    # 5. Simular click del botón KPIs
    print("\n5️⃣ Simulando click del botón KPIs...")
    print("   🔘 Invocando controller.refresh_kpis()...")
    
    try:
        controller.refresh_kpis()
        print("✅ refresh_kpis() ejecutado sin errores")
    except Exception as e:
        print(f"❌ Error en refresh_kpis(): {e}")
        return False
    
    # 6. Verificar archivos generados
    print("\n6️⃣ Verificando archivos generados...")
    kpis_dir = "outputs/kpis"
    if os.path.exists(kpis_dir):
        files = os.listdir(kpis_dir)
        print(f"   📁 Archivos en {kpis_dir}: {files}")
        if files:
            print("✅ Archivos JSON de KPIs generados correctamente")
        else:
            print("⚠️  Directorio existe pero está vacío")
    else:
        print("❌ Directorio outputs/kpis no existe")
    
    print("\n" + "=" * 80)
    print("🏁 PRUEBA FINALIZADA")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_kpi_button_functionality()
    if success:
        print("\n✅ Prueba completada exitosamente")
    else:
        print("\n❌ Prueba falló")
        sys.exit(1)