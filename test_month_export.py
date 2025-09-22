#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar la función de exportación del mes actual.
"""

from datetime import datetime
import calendar

def test_month_calculation():
    """Probar el cálculo de fechas del mes actual."""
    now = datetime.now()
    year = now.year
    month = now.month
    
    # Primer día del mes
    first_day = datetime(year, month, 1)
    fecha_inicio = first_day.strftime("%Y-%m-%d")
    
    # Último día del mes
    last_day_of_month = calendar.monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_of_month)
    fecha_fin = last_day.strftime("%Y-%m-%d")
    
    month_name = now.strftime("%B_%Y").lower()
    
    print(f"✅ Prueba de cálculo de fechas del mes actual:")
    print(f"📅 Mes: {now.strftime('%B %Y')}")
    print(f"🗓️ Fecha inicio: {fecha_inicio}")
    print(f"🗓️ Fecha fin: {fecha_fin}")
    print(f"📁 Nombre archivo: facturas_mes_actual_{month_name}_<timestamp>.xlsx")

if __name__ == "__main__":
    test_month_calculation()