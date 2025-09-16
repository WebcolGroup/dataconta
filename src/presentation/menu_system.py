"""
Advanced Menu System for DATACONTA
Modular, scalable menu system with license validation and session-based organization.
"""

import os
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv


class LicenseType(Enum):
    """Supported license types"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class MenuOption:
    """Represents a single menu option"""
    name: str
    emoji: str
    action: Callable
    description: Optional[str] = None


@dataclass
class MenuSession:
    """Represents a menu session with multiple options"""
    title: str
    emoji: str
    license_required: LicenseType
    options: List[MenuOption]
    description: Optional[str] = None


class LicenseValidator:
    """Handles license validation and management"""
    
    def __init__(self):
        load_dotenv()
        self._current_license = self._load_license()
    
    def _load_license(self) -> LicenseType:
        """Load license from environment variable"""
        license_str = os.getenv('LICENSE', 'free').lower()
        try:
            return LicenseType(license_str)
        except ValueError:
            print(f"⚠️ Licencia desconocida '{license_str}', usando licencia gratuita")
            return LicenseType.FREE
    
    def get_current_license(self) -> LicenseType:
        """Get current license type"""
        return self._current_license
    
    def has_access_to(self, required_license: LicenseType) -> bool:
        """Check if current license has access to required feature"""
        license_hierarchy = {
            LicenseType.FREE: 1,
            LicenseType.PRO: 2,
            LicenseType.ENTERPRISE: 3
        }
        
        current_level = license_hierarchy.get(self._current_license, 1)
        required_level = license_hierarchy.get(required_license, 1)
        
        return current_level >= required_level
    
    def get_license_display_name(self) -> str:
        """Get formatted license name for display"""
        license_names = {
            LicenseType.FREE: "🆓 Gratuita",
            LicenseType.PRO: "💼 Profesional",
            LicenseType.ENTERPRISE: "🏢 Empresarial"
        }
        return license_names.get(self._current_license, "🔍 Desconocida")


class MenuSystem:
    """Advanced menu system with session management"""
    
    def __init__(self):
        self.license_validator = LicenseValidator()
        self.sessions: Dict[str, MenuSession] = {}
        self.current_session: Optional[str] = None
        self._setup_menu_structure()
    
    def _setup_menu_structure(self):
        """Initialize the menu structure configuration"""
        # This will be populated by register_session calls
        pass
    
    def register_session(self, session_id: str, session: MenuSession):
        """Register a new menu session"""
        self.sessions[session_id] = session
    
    def get_available_sessions(self) -> Dict[str, MenuSession]:
        """Get sessions available for current license"""
        available = {}
        for session_id, session in self.sessions.items():
            if self.license_validator.has_access_to(session.license_required):
                available[session_id] = session
        return available
    
    def display_main_menu(self):
        """Display the main menu with available sessions"""
        print("\n" + "="*60)
        print("🏢 DATACONTA - SISTEMA AVANZADO DE MENÚS")
        print("="*60)
        
        # Show license info
        license_display = self.license_validator.get_license_display_name()
        print(f"📄 Licencia actual: {license_display}")
        print("-"*60)
        
        available_sessions = self.get_available_sessions()
        
        if not available_sessions:
            print("❌ No hay sesiones disponibles para su licencia actual")
            return False
        
        # Display available sessions
        session_keys = list(available_sessions.keys())
        for i, (session_id, session) in enumerate(available_sessions.items(), 1):
            print(f"{i}. {session.emoji} {session.title}")
            if session.description:
                print(f"   📝 {session.description}")
        
        print("-"*60)
        print("0. 🚪 Salir")
        print("="*60)
        
        return session_keys
    
    def display_session_menu(self, session_id: str):
        """Display a specific session menu"""
        if session_id not in self.sessions:
            print(f"❌ Sesión '{session_id}' no encontrada")
            return False
        
        session = self.sessions[session_id]
        
        # Check license access
        if not self.license_validator.has_access_to(session.license_required):
            print(f"🔒 Acceso denegado a '{session.title}'")
            print(f"   Licencia requerida: {session.license_required.value}")
            return False
        
        print("\n" + "="*60)
        print(f"{session.emoji} {session.title.upper()}")
        print("="*60)
        
        if session.description:
            print(f"📝 {session.description}")
            print("-"*60)
        
        # Display session options
        for i, option in enumerate(session.options, 1):
            print(f"{i}. {option.emoji} {option.name}")
            if option.description:
                print(f"   📝 {option.description}")
        
        print("-"*60)
        print("9. 🔙 Volver al menú principal")
        print("0. 🚪 Salir")
        print("="*60)
        
        return True
    
    def execute_option(self, session_id: str, option_index: int) -> bool:
        """Execute a specific menu option"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        if option_index < 1 or option_index > len(session.options):
            print("⚠️ Opción inválida")
            return False
        
        option = session.options[option_index - 1]
        
        try:
            print(f"\n🚀 Ejecutando: {option.name}")
            print("-"*40)
            
            # Execute the action
            result = option.action()
            
            print("-"*40)
            input("📌 Presione Enter para continuar...")
            return True
            
        except Exception as e:
            print(f"❌ Error al ejecutar '{option.name}': {str(e)}")
            input("📌 Presione Enter para continuar...")
            return False
    
    def run(self):
        """Main menu loop"""
        print("🎯 Iniciando sistema de menús DATACONTA...")
        
        while True:
            try:
                # Display main menu
                session_keys = self.display_main_menu()
                
                if not session_keys:
                    break
                
                # Get user choice for main menu
                choice = input("\nSeleccione una opción: ").strip()
                
                if choice == "0":
                    print("👋 ¡Gracias por usar DATACONTA!")
                    break
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(session_keys):
                        selected_session_id = session_keys[choice_num - 1]
                        self._run_session_menu(selected_session_id)
                    else:
                        print("⚠️ Opción inválida. Por favor, seleccione una opción válida.")
                        input("📌 Presione Enter para continuar...")
                
                except ValueError:
                    print("⚠️ Por favor, ingrese un número válido.")
                    input("📌 Presione Enter para continuar...")
            
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {str(e)}")
                input("📌 Presione Enter para continuar...")
    
    def _run_session_menu(self, session_id: str):
        """Run a specific session menu loop"""
        while True:
            # Display session menu
            if not self.display_session_menu(session_id):
                break
            
            # Get user choice for session menu
            choice = input("\nSeleccione una opción: ").strip()
            
            if choice == "0":
                print("👋 ¡Gracias por usar DATACONTA!")
                return "exit"
            elif choice == "9":
                break  # Return to main menu
            
            try:
                choice_num = int(choice)
                if not self.execute_option(session_id, choice_num):
                    input("📌 Presione Enter para continuar...")
            
            except ValueError:
                print("⚠️ Por favor, ingrese un número válido.")
                input("📌 Presione Enter para continuar...")


def create_default_menu_system() -> MenuSystem:
    """Factory function to create a default menu system with predefined sessions"""
    menu_system = MenuSystem()
    
    # We'll define the actual menu options in a separate configuration
    return menu_system


if __name__ == "__main__":
    # Test the menu system
    menu = create_default_menu_system()
    menu.run()