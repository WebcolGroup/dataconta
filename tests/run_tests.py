"""
Test Suite Runner para DataConta
Script para ejecutar todos los tests unitarios del proyecto
"""

import unittest
import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Ejecuta todos los tests unitarios del proyecto."""
    
    print("=" * 70)
    print("🧪 DATACONTA - SUITE DE TESTS UNITARIOS")
    print("=" * 70)
    print()
    
    # Configurar el test loader
    loader = unittest.TestLoader()
    
    # Descubrir todos los tests en el directorio tests/
    test_directory = os.path.join(os.path.dirname(__file__))
    
    try:
        # Cargar todos los tests
        suite = loader.discover(
            start_dir=test_directory,
            pattern='test_*.py',
            top_level_dir=str(project_root)
        )
        
        # Configurar el runner con verbosidad
        runner = unittest.TextTestRunner(
            verbosity=2,
            buffer=True,
            failfast=False,
            stream=sys.stdout
        )
        
        print(f"📁 Directorio de tests: {test_directory}")
        print(f"🔍 Buscando archivos: test_*.py")
        print(f"📊 Tests encontrados: {suite.countTestCases()}")
        print()
        
        # Ejecutar todos los tests
        result = runner.run(suite)
        
        # Resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE EJECUCIÓN")
        print("=" * 70)
        
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        success_count = total_tests - failures - errors
        
        print(f"✅ Tests exitosos: {success_count}")
        print(f"❌ Tests fallidos: {failures}")
        print(f"🚨 Errores: {errors}")
        print(f"📈 Total ejecutados: {total_tests}")
        
        if result.wasSuccessful():
            print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
            success_percentage = 100.0
        else:
            success_percentage = (success_count / total_tests * 100) if total_tests > 0 else 0
            print(f"\n⚠️  TESTS COMPLETADOS CON ERRORES")
        
        print(f"📊 Porcentaje de éxito: {success_percentage:.1f}%")
        
        # Detalles de fallos si los hay
        if failures:
            print("\n" + "❌ DETALLES DE FALLOS:")
            print("-" * 50)
            for i, (test, traceback) in enumerate(result.failures, 1):
                print(f"{i}. {test}")
                print(f"   {traceback.splitlines()[-1]}")
        
        if errors:
            print("\n" + "🚨 DETALLES DE ERRORES:")
            print("-" * 50)
            for i, (test, traceback) in enumerate(result.errors, 1):
                print(f"{i}. {test}")
                print(f"   {traceback.splitlines()[-1]}")
        
        print("\n" + "=" * 70)
        
        # Código de salida
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"🚨 Error ejecutando tests: {e}")
        return 1


def run_specific_layer_tests(layer_name):
    """Ejecuta tests específicos de una capa (domain, application, infrastructure)."""
    
    print(f"🧪 Ejecutando tests de la capa: {layer_name.upper()}")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    test_directory = os.path.join(os.path.dirname(__file__), 'unit', layer_name)
    
    if not os.path.exists(test_directory):
        print(f"❌ No se encontró directorio: {test_directory}")
        return 1
    
    try:
        suite = loader.discover(
            start_dir=test_directory,
            pattern='test_*.py',
            top_level_dir=str(project_root)
        )
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"🚨 Error: {e}")
        return 1


def show_test_structure():
    """Muestra la estructura de tests del proyecto."""
    
    print("📁 ESTRUCTURA DE TESTS")
    print("=" * 50)
    
    test_dir = Path(__file__).parent
    
    def print_tree(directory, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
            
        items = sorted([
            item for item in directory.iterdir() 
            if item.name.startswith('test_') or item.is_dir()
        ])
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            
            if item.is_file() and item.suffix == '.py':
                print(f"{prefix}{current_prefix}🧪 {item.name}")
            elif item.is_dir() and item.name != '__pycache__':
                print(f"{prefix}{current_prefix}📁 {item.name}/")
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix, max_depth, current_depth + 1)
    
    print_tree(test_dir)
    print()


if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'structure':
            show_test_structure()
            sys.exit(0)
            
        elif command in ['domain', 'application', 'infrastructure']:
            exit_code = run_specific_layer_tests(command)
            sys.exit(exit_code)
            
        elif command == 'help':
            print("📖 USO DEL TEST RUNNER")
            print("=" * 40)
            print("python run_tests.py                  - Ejecutar todos los tests")
            print("python run_tests.py domain          - Tests de la capa domain")
            print("python run_tests.py application     - Tests de la capa application")
            print("python run_tests.py infrastructure  - Tests de la capa infrastructure")
            print("python run_tests.py structure       - Mostrar estructura de tests")
            print("python run_tests.py help            - Mostrar esta ayuda")
            sys.exit(0)
            
        else:
            print(f"❌ Comando desconocido: {command}")
            print("Usa 'python run_tests.py help' para ver opciones disponibles.")
            sys.exit(1)
    
    # Sin argumentos, ejecutar todos los tests
    exit_code = run_all_tests()
    sys.exit(exit_code)