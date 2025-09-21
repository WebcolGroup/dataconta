"""
DataConta FREE - Entrypoint Principal
Punto de entrada puro que solo inicializa la aplicación y delega el resto.

Responsabilidades:
- Inicializar la aplicación Qt
- Aplicar configuración de tema
- Crear la ventana principal usando el factory
- Manejar argumentos de línea de comandos básicos

NO ES RESPONSABLE DE:
- Lógica de negocio (delegada al dominio)
- Configuración compleja (delegada a factories)
- Manejo de datos (delegado a servicios)
"""

import sys
import os
from typing import Optional

# Qt Framework
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCommandLineParser, QCommandLineOption

# Aplicación de temas (opcional)
try:
    from qt_material import apply_stylesheet
except ImportError:
    apply_stylesheet = None

# Factory para crear la aplicación
from src.infrastructure.factories.application_factory import DataContaApplicationFactory


class DataContaEntrypoint:
    """
    Entrypoint puro para DataConta.
    Solo maneja inicialización de la aplicación y delegación.
    """
    
    def __init__(self):
        self.app: Optional[QApplication] = None
        self.main_window = None
    
    def run(self, args: list = None) -> int:
        """
        Ejecutar la aplicación DataConta.
        
        Args:
            args: Argumentos de línea de comandos
            
        Returns:
            Código de salida de la aplicación
        """
        try:
            # 1. Crear aplicación Qt
            self.app = QApplication(args or sys.argv)
            
            # 2. Procesar argumentos de línea de comandos
            cmd_args = self._parse_command_line()
            
            # 3. Configurar tema
            self._apply_theme(cmd_args.get('theme', 'light_blue'))
            
            # 4. Crear aplicación usando factory (Inyección de Dependencias)
            self.main_window = DataContaApplicationFactory.create_main_window()
            
            # 5. Configurar aplicación post-inicialización
            self._configure_application(cmd_args)
            
            # 6. Mostrar ventana principal
            self.main_window.show()
            
            # 7. Auto-configurar servicios si es necesario
            self._auto_configure_services()
            
            # 8. Ejecutar bucle principal de la aplicación
            return self.app.exec()
            
        except Exception as e:
            self._handle_startup_error(e)
            return 1
    
    def _parse_command_line(self) -> dict:
        """
        Procesar argumentos de línea de comandos.
        
        Returns:
            Diccionario con argumentos procesados
        """
        parser = QCommandLineParser()
        parser.setApplicationDescription("DataConta FREE - Análisis Financiero y Contable")
        parser.addHelpOption()
        parser.addVersionOption()
        
        # Opción de tema
        theme_option = QCommandLineOption(
            ["t", "theme"], 
            "Tema de la aplicación (light_blue, dark_blue, etc.)", 
            "theme", 
            "light_blue"
        )
        parser.addOption(theme_option)
        
        # Opción de debug
        debug_option = QCommandLineOption(
            ["d", "debug"], 
            "Activar modo debug"
        )
        parser.addOption(debug_option)
        
        parser.process(self.app)
        
        return {
            'theme': parser.value(theme_option),
            'debug': parser.isSet(debug_option)
        }
    
    def _apply_theme(self, theme_name: str) -> None:
        """
        Aplicar tema Material Design si está disponible.
        
        Args:
            theme_name: Nombre del tema a aplicar
        """
        if apply_stylesheet is not None and self.app is not None:
            try:
                apply_stylesheet(self.app, theme=f"{theme_name}.xml")
                print(f"✅ Tema aplicado: {theme_name}")
            except Exception as e:
                print(f"⚠️  No se pudo aplicar tema {theme_name}: {e}")
        else:
            print("ℹ️  qt-material no disponible, usando tema por defecto")
    
    def _configure_application(self, args: dict) -> None:
        """
        Configurar aplicación después de la inicialización.
        
        Args:
            args: Argumentos de línea de comandos
        """
        if self.app is None:
            return
            
        # Configurar información de la aplicación
        self.app.setApplicationName("DataConta FREE")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("DataConta")
        self.app.setOrganizationDomain("dataconta.com")
        
        # Configurar debug si está activado
        if args.get('debug', False):
            os.environ['DATACONTA_DEBUG'] = '1'
            print("🐛 Modo debug activado")
    
    def _auto_configure_services(self) -> None:
        """
        Auto-configurar servicios que lo requieran.
        Delegado a los adaptadores correspondientes.
        """
        try:
            # Verificar si se necesita configuración de Siigo
            from src.presentation.widgets.ayuda_widget import SiigoConfigDialog
            
            # Pequeña pausa para renderizar la ventana principal
            if self.app:
                self.app.processEvents()
            
            # Auto-abrir configurador si es necesario
            if SiigoConfigDialog.needs_configuration():
                print("⚙️  Configuración de Siigo API requerida")
                SiigoConfigDialog.auto_open_if_needed(self.main_window)
                
        except Exception as e:
            print(f"⚠️  Error en auto-configuración: {e}")
    
    def _handle_startup_error(self, error: Exception) -> None:
        """
        Manejar errores durante el inicio de la aplicación.
        
        Args:
            error: Error ocurrido durante el inicio
        """
        print(f"❌ Error iniciando DataConta: {error}")
        
        # Log adicional para debug
        import traceback
        traceback.print_exc()
        
        # Mostrar mensaje al usuario si es posible
        if self.app is not None:
            from PySide6.QtWidgets import QMessageBox
            try:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error de Inicio")
                msg.setText(f"No se pudo iniciar DataConta:\n{str(error)}")
                msg.exec()
            except:
                pass  # Silenciar errores secundarios


def main() -> int:
    """
    Función principal - Punto de entrada de la aplicación.
    
    Returns:
        Código de salida de la aplicación
    """
    print("🚀 Iniciando DataConta FREE")
    print("📐 Arquitectura Hexagonal - Versión Refactorizada")
    print("=" * 70)
    
    entrypoint = DataContaEntrypoint()
    exit_code = entrypoint.run()
    
    print("=" * 70)
    print("👋 DataConta FREE finalizado")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())