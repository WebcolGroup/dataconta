#!/usr/bin/env python3
"""
Test script para probar la funcionalidad de limpieza de KPIs
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from src.application.services.kpi_service import KPIApplicationService
from src.infrastructure.adapters.file_storage_adapter import FileStorageAdapter
from src.infrastructure.adapters.logger_adapter import LoggerAdapter
from src.domain.services.kpi_service import KPICalculationServiceImpl, KPIAnalysisService

# Mock de repositorio de invoices (no necesario para esta prueba)
class MockInvoiceRepository:
    def download_invoices_dataframes(self, fecha_inicio, fecha_fin):
        import pandas as pd
        return pd.DataFrame(), pd.DataFrame()

# Mock de logger
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")

def test_kpi_cleanup():
    """Probar la limpieza automática de archivos KPIs antiguos."""
    print("🧪 Testing KPI cleanup functionality...")
    
    # Configurar servicios
    logger = MockLogger()
    file_storage = FileStorageAdapter("outputs", logger)
    invoice_repo = MockInvoiceRepository()
    kpi_calc_service = KPICalculationServiceImpl()
    kpi_analysis_service = KPIAnalysisService(kpi_calc_service)
    
    # Crear el servicio de aplicación
    kpi_service = KPIApplicationService(
        invoice_repository=invoice_repo,
        file_storage=file_storage,
        kpi_calculation_service=kpi_calc_service,
        kpi_analysis_service=kpi_analysis_service,
        logger=logger
    )
    
    print("📂 Estado inicial del directorio kpis:")
    kpis_dir = "outputs/kpis"
    if os.path.exists(kpis_dir):
        files_before = os.listdir(kpis_dir)
        print(f"   Archivos encontrados: {len(files_before)}")
        for file in files_before:
            print(f"   - {file}")
    else:
        print("   Directorio no existe")
    
    # Crear datos de prueba
    test_kpis_data = {
        "ventas_totales": 1000000,
        "numero_facturas": 100,
        "ticket_promedio": 10000,
        "cliente_top": {"nombre": "Cliente Test", "nit": "123456", "monto": 50000},
        "ventas_por_cliente": [],
        "estado_sistema": "PRUEBA ✅",
        "fecha_calculo": datetime.now().isoformat(),
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-12-31"
    }
    
    print("\n🔄 Guardando nuevos KPIs de prueba...")
    
    # Probar el guardado (esto debería limpiar archivos antiguos)
    try:
        fecha_inicio = datetime(2025, 1, 1)
        fecha_fin = datetime(2025, 12, 31)
        kpi_service._guardar_kpis(test_kpis_data, fecha_inicio, fecha_fin)
        print("✅ KPIs de prueba guardados exitosamente")
    except Exception as e:
        print(f"❌ Error guardando KPIs de prueba: {e}")
    
    print("\n📂 Estado final del directorio kpis:")
    if os.path.exists(kpis_dir):
        files_after = os.listdir(kpis_dir)
        print(f"   Archivos encontrados: {len(files_after)}")
        for file in files_after:
            print(f"   - {file}")
            
        # Verificar resultado
        if len(files_after) == 1:
            print("✅ ¡Limpieza exitosa! Solo queda 1 archivo KPI")
            # Verificar que es del nuevo formato
            if files_after[0].startswith("kpis_siigo_"):
                print("✅ ¡Formato de archivo correcto!")
            else:
                print("⚠️ Formato de archivo no esperado")
        else:
            print(f"⚠️ Limpieza incompleta. Se esperaba 1 archivo, se encontraron {len(files_after)}")
    else:
        print("   Directorio no existe")
    
    print("\n🧪 Probando carga de KPIs existentes...")
    existing_kpis = kpi_service.load_existing_kpis()
    if existing_kpis:
        print("✅ ¡Carga de KPIs existentes exitosa!")
        print(f"   Ventas totales: ${existing_kpis.get('ventas_totales', 0):,.2f}")
        print(f"   Estado sistema: {existing_kpis.get('estado_sistema', 'N/A')}")
    else:
        print("❌ Error cargando KPIs existentes")

if __name__ == "__main__":
    test_kpi_cleanup()