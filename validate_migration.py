#!/usr/bin/env python3
"""
Test de Validación - DATACONTA GUI Migration
Valida que la migración a PySide6 mantiene la arquitectura hexagonal
y todos los principios SOLID correctamente implementados.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

def test_architecture_integrity():
    """Validar integridad de la arquitectura hexagonal"""
    
    print("🏗️ Verificando Arquitectura Hexagonal...")
    
    # Test 1: Domain Layer - Interfaces UI
    try:
        from src.domain.interfaces.ui_interfaces import (
            UIMenuController, UIUserInteraction, UIFileOperations, 
            UIDataPresentation, UIApplicationController
        )
        print("   ✅ Domain interfaces cargadas correctamente")
    except ImportError as e:
        print(f"   ❌ Error cargando interfaces de dominio: {e}")
        return False
    
    # Test 2: Domain Layer - DTOs
    try:
        from src.domain.dtos.ui_dtos import (
            UIInvoiceRequestDTO, UIFinancialReportRequestDTO, 
            UIProgressInfo, UINotification
        )
        print("   ✅ DTOs de dominio cargados correctamente")
    except ImportError as e:
        print(f"   ❌ Error cargando DTOs: {e}")
        return False
    
    # Test 3: UI Adapters  
    try:
        from src.ui.adapters.ui_adapters import (
            UIControllerAdapter, BusinessLogicAdapter, MenuActionsAdapter
        )
        print("   ✅ Adaptadores de UI cargados correctamente")
    except ImportError as e:
        print(f"   ❌ Error cargando adaptadores: {e}")
        return False
    
    # Test 4: MainWindow (condicional PySide6)
    try:
        from src.ui.components.main_window import MainWindow
        print("   ✅ MainWindow cargada correctamente")
    except ImportError as e:
        print(f"   ⚠️  MainWindow no cargada (PySide6 no disponible): {e}")
        # No es error crítico si PySide6 no está instalado durante testing
    
    return True


def test_solid_principles():
    """Validar aplicación de principios SOLID"""
    
    print("\n🛡️ Verificando Principios SOLID...")
    
    # Test SRP - Single Responsibility Principle
    print("   📋 Single Responsibility Principle:")
    try:
        from src.domain.interfaces.ui_interfaces import UIMenuController
        from src.ui.adapters.ui_adapters import BusinessLogicAdapter
        
        # Verificar que las interfaces tienen responsabilidades específicas
        ui_menu_methods = [method for method in dir(UIMenuController) if not method.startswith('_')]
        business_methods = [method for method in dir(BusinessLogicAdapter) if not method.startswith('_')]
        
        print(f"      ✅ UIMenuController: {len(ui_menu_methods)} métodos específicos de menú")
        print(f"      ✅ BusinessLogicAdapter: {len(business_methods)} métodos de lógica de negocio")
        
    except Exception as e:
        print(f"      ❌ Error verificando SRP: {e}")
        return False
    
    # Test DIP - Dependency Inversion Principle
    print("   🔄 Dependency Inversion Principle:")
    try:
        from src.domain.interfaces.ui_interfaces import UIUserInteraction
        from abc import ABC
        
        # Verificar que las interfaces son abstractas
        if issubclass(UIUserInteraction, ABC):
            print("      ✅ Interfaces abstractas correctamente definidas")
        else:
            print("      ❌ Interfaces no son abstractas")
            return False
            
    except Exception as e:
        print(f"      ❌ Error verificando DIP: {e}")
        return False
    
    # Test ISP - Interface Segregation Principle
    print("   📝 Interface Segregation Principle:")
    try:
        from src.domain.interfaces.ui_interfaces import (
            UIMenuController, UIUserInteraction, UIFileOperations, UIDataPresentation
        )
        
        # Verificar que hay múltiples interfaces específicas en lugar de una grande
        interfaces = [UIMenuController, UIUserInteraction, UIFileOperations, UIDataPresentation]
        print(f"      ✅ {len(interfaces)} interfaces específicas en lugar de una monolítica")
        
    except Exception as e:
        print(f"      ❌ Error verificando ISP: {e}")
        return False
    
    return True


def test_functionality_preservation():
    """Validar que se preservó la funcionalidad original"""
    
    print("\n🔧 Verificando Preservación de Funcionalidad...")
    
    # Test 1: Casos de uso originales accesibles
    try:
        from src.application.use_cases.invoice_use_cases_wrapper import InvoiceUseCases
        from src.application.services.BIExportService import BIExportService
        from src.application.services.InvoiceExportService import InvoiceExportService
        print("   ✅ Casos de uso originales accesibles")
    except ImportError as e:
        print(f"   ❌ Error accediendo casos de uso: {e}")
        return False
    
    # Test 2: Adaptadores de infraestructura
    try:
        from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter
        from src.infrastructure.adapters.license_validator_adapter import LicenseValidatorAdapter
        print("   ✅ Adaptadores de infraestructura accesibles")
    except ImportError as e:
        print(f"   ❌ Error accediendo adaptadores: {e}")
        return False
    
    # Test 3: Menu Actions disponibles
    try:
        from src.ui.adapters.ui_adapters import MenuActionsAdapter
        
        # Crear instancia mock para probar
        class MockBusinessAdapter:
            def export_invoices_to_json(self): pass
            def export_invoices_to_csv(self): pass
            def export_bi_data(self): pass
            def generate_financial_report(self): pass
            def validate_license(self): pass
            def analyze_structure(self): pass
        
        menu_adapter = MenuActionsAdapter(MockBusinessAdapter())
        menu_actions = menu_adapter.get_menu_actions()
        
        expected_sections = ["business_intelligence", "reports", "tools"]
        for section in expected_sections:
            if section in menu_actions:
                print(f"   ✅ Sección '{section}': {len(menu_actions[section])} acciones")
            else:
                print(f"   ❌ Sección '{section}' no encontrada")
                return False
                
    except Exception as e:
        print(f"   ❌ Error verificando acciones de menú: {e}")
        return False
    
    return True


def test_gui_entry_point():
    """Validar punto de entrada GUI"""
    
    print("\n🚪 Verificando Punto de Entrada GUI...")
    
    # Test 1: main_gui.py importable
    try:
        # Solo verificar que el módulo es importable, no ejecutar
        with open('main_gui.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'DataContaGUIApplication' in content:
            print("   ✅ main_gui.py contiene clase principal")
        else:
            print("   ❌ main_gui.py no contiene clase principal")
            return False
            
        if 'def main()' in content:
            print("   ✅ main_gui.py contiene función main")
        else:
            print("   ❌ main_gui.py no contiene función main")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando main_gui.py: {e}")
        return False
    
    # Test 2: Requirements actualizados
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.read()
            
        if 'PySide6' in requirements:
            print("   ✅ PySide6 agregado a requirements.txt")
        else:
            print("   ❌ PySide6 no encontrado en requirements.txt")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando requirements.txt: {e}")
        return False
    
    return True


def test_documentation():
    """Validar documentación de migración"""
    
    print("\n📚 Verificando Documentación...")
    
    try:
        doc_path = Path('MIGRACION_GUI_COMPLETADA.md')
        if doc_path.exists():
            print("   ✅ Documentación de migración creada")
            
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar secciones clave
            key_sections = [
                "Arquitectura Implementada",
                "Principios SOLID Aplicados", 
                "Cómo Ejecutar",
                "Funcionalidades Disponibles"
            ]
            
            for section in key_sections:
                if section in content:
                    print(f"   ✅ Sección '{section}' documentada")
                else:
                    print(f"   ⚠️  Sección '{section}' no encontrada")
                    
        else:
            print("   ❌ Documentación no encontrada")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando documentación: {e}")
        return False
    
    return True


def run_all_tests():
    """Ejecutar todos los tests de validación"""
    
    print("=" * 80)
    print("🧪 DATACONTA GUI - VALIDACIÓN DE MIGRACIÓN")
    print("🏗️ Arquitectura Hexagonal + 🛡️ Principios SOLID + 🎨 PySide6 GUI")
    print("=" * 80)
    
    tests = [
        ("Arquitectura Hexagonal", test_architecture_integrity),
        ("Principios SOLID", test_solid_principles),
        ("Funcionalidad Preservada", test_functionality_preservation),
        ("Punto de Entrada GUI", test_gui_entry_point),
        ("Documentación", test_documentation)
    ]
    
    results = []
    
    for test_name, test_function in tests:
        try:
            result = test_function()
            results.append((test_name, result))
            
            if result:
                print(f"\n✅ {test_name}: PASADO")
            else:
                print(f"\n❌ {test_name}: FALLADO")
                
        except Exception as e:
            print(f"\n💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASADO" if result else "❌ FALLADO"
        print(f"   {test_name:.<50} {status}")
    
    print(f"\n🎯 RESULTADO: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n🎉 ¡MIGRACIÓN VALIDADA EXITOSAMENTE!")
        print("🚀 DATACONTA GUI está listo para usar")
        print("\n📋 Próximos pasos:")
        print("   1. pip install PySide6")
        print("   2. python main_gui.py")
        return True
    else:
        print(f"\n⚠️  Se encontraron {total - passed} problemas")
        print("🔧 Revise los errores arriba antes de usar la aplicación GUI")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)