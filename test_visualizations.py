#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar la generación de visualizaciones.
"""

import os
from dataconta.reports.charts import generate_all_charts

def main():
    # Buscar el archivo KPI más reciente
    kpis_dir = "outputs/kpis"
    if not os.path.exists(kpis_dir):
        print(f"❌ No existe el directorio {kpis_dir}")
        return
    
    # Listar archivos JSON
    json_files = [f for f in os.listdir(kpis_dir) if f.endswith('.json')]
    if not json_files:
        print(f"❌ No se encontraron archivos JSON en {kpis_dir}")
        return
    
    # Usar el archivo más reciente
    latest_file = os.path.join(kpis_dir, sorted(json_files)[-1])
    print(f"📂 Usando archivo: {latest_file}")
    
    # Generar visualizaciones
    try:
        results = generate_all_charts(latest_file)
        print(f"\n✅ Proceso completado!")
        print(f"📊 Se generaron {len(results)} visualizaciones:")
        for chart_type, file_path in results.items():
            print(f"  • {chart_type}: {file_path}")
            
        if not results:
            print("⚠️ No se generaron visualizaciones")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    main()