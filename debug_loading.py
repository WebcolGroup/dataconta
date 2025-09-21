#!/usr/bin/env python3
"""
Script de debug para verificar que LoadingMixin esté funcionando correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.presentation.gui_interface import DataContaMainWindow
from src.presentation.widgets.loading_widget import LoadingMixin

def main():
    print("🔍 Debug: Verificando implementación de LoadingMixin")
    print(f"📊 DataContaMainWindow MRO: {DataContaMainWindow.__mro__}")
    
    # Verificar que LoadingMixin está en la jerarquía
    if LoadingMixin in DataContaMainWindow.__mro__:
        print("✅ LoadingMixin está correctamente en la jerarquía de DataContaMainWindow")
    else:
        print("❌ LoadingMixin NO está en la jerarquía de DataContaMainWindow")
    
    # Verificar métodos disponibles
    methods = ['show_loading', 'hide_loading', 'update_loading_message', 'init_loading']
    for method in methods:
        if hasattr(DataContaMainWindow, method):
            print(f"✅ {method} está disponible")
        else:
            print(f"❌ {method} NO está disponible")

if __name__ == "__main__":
    main()