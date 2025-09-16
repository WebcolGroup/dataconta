#!/usr/bin/env python3
"""
Test script to verify the new menu structure
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dataconta_advanced import DataContaAdvancedApp

def test_menu_structure():
    """Test the menu structure without full initialization"""
    print("🧪 PROBANDO ESTRUCTURA DE MENÚS - DATACONTA")
    print("=" * 60)
    
    try:
        # Create app instance
        print("🔧 Inicializando infraestructura...")
        app = DataContaAdvancedApp()
        
        print("✅ Inicialización exitosa")
        print("\n📋 ESTRUCTURA DE MENÚS VERIFICADA:")
        print("-" * 40)
        
        # Show main menu structure
        sessions = app._menu_system.sessions
        for session_key, session in sessions.items():
            print(f"\n{session.emoji} {session.title}")
            print(f"   📝 {session.description}")
            print(f"   🎫 Licencia requerida: {session.license_required.value}")
            for i, option in enumerate(session.options, 1):
                print(f"   {i}. {option.emoji} {option.name}")
                print(f"      📄 {option.description}")
        
        print("\n🎉 ESTRUCTURA DE MENÚS COMPLETADA EXITOSAMENTE")
        
        # Test financial reports menu specifically
        print("\n" + "="*60)
        print("🧪 PROBANDO SUBMENÚ DE INFORMES FINANCIEROS")
        print("="*60)
        
        app._handle_financial_reports_menu()
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

if __name__ == "__main__":
    success = test_menu_structure()
    sys.exit(0 if success else 1)