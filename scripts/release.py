#!/usr/bin/env python3
"""
Script para automatizar el proceso de release de DataConta FREE
Maneja versionado, tags de Git y generación de artifacts.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path


def get_current_version():
    """Obtiene la versión actual desde VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"


def update_version_file(new_version):
    """Actualiza el archivo VERSION con la nueva versión."""
    version_file = Path(__file__).parent.parent / "VERSION"
    version_file.write_text(f"{new_version}\n")
    print(f"✅ Versión actualizada a {new_version}")


def update_changelog(version, release_notes):
    """Actualiza el CHANGELOG.md con las notas de la nueva versión."""
    changelog_file = Path(__file__).parent.parent / "CHANGELOG.md"
    
    if not changelog_file.exists():
        print("⚠️  CHANGELOG.md no encontrado")
        return
    
    # Leer contenido actual
    content = changelog_file.read_text(encoding='utf-8')
    
    # Crear entrada de nueva versión
    today = datetime.now().strftime('%Y-%m-%d')
    new_entry = f"\n## [{version}] - {today}\n\n{release_notes}\n"
    
    # Insertar después de [Unreleased]
    unreleased_pos = content.find('## [Unreleased]')
    if unreleased_pos != -1:
        # Encontrar el final de la sección Unreleased
        next_version_pos = content.find('## [', unreleased_pos + 1)
        if next_version_pos != -1:
            # Insertar antes de la siguiente versión
            new_content = content[:next_version_pos] + new_entry + content[next_version_pos:]
        else:
            # Agregar al final
            new_content = content + new_entry
    else:
        # Si no hay sección Unreleased, agregar al inicio
        new_content = new_entry + content
    
    changelog_file.write_text(new_content, encoding='utf-8')
    print(f"✅ CHANGELOG.md actualizado con versión {version}")


def create_git_tag(version, message):
    """Crea un tag de Git para la nueva versión."""
    try:
        # Verificar que estamos en un repositorio Git
        subprocess.run(["git", "status"], check=True, capture_output=True)
        
        # Crear tag anotado
        subprocess.run(["git", "tag", "-a", f"v{version}", "-m", message], check=True)
        print(f"✅ Tag v{version} creado")
        
        # Preguntar si hacer push del tag
        push_tag = input("❓ ¿Hacer push del tag a origin? (y/N): ").lower().strip()
        if push_tag in ['y', 'yes', 's', 'si']:
            subprocess.run(["git", "push", "origin", f"v{version}"], check=True)
            print(f"✅ Tag v{version} enviado a origin")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en Git: {e}")
        return False
    
    return True


def build_release_artifacts():
    """Construye los artifacts de release."""
    print("📺 Construyendo artifacts de release...")
    
    project_root = Path(__file__).parent.parent
    
    try:
        # Limpiar builds anteriores
        dist_dir = project_root / "dist"
        build_dir = project_root / "build"
        
        if dist_dir.exists():
            import shutil
            shutil.rmtree(dist_dir)
        
        if build_dir.exists():
            import shutil
            shutil.rmtree(build_dir)
        
        # Construir con PyInstaller
        os.chdir(project_root)
        result = subprocess.run([
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name", "dataconta-free",
            "--add-data", "src;src",
            "--add-data", "addons;addons",
            "--add-data", "menu_config.json;.",
            "dataconta.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable construido exitosamente")
            return True
        else:
            print(f"❌ Error en construcción: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error construyendo artifacts: {e}")
        return False


def validate_version_format(version):
    """Valida que el formato de versión sea correcto."""
    import re
    
    # Patrón para semantic versioning con sufijo opcional
    pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
    
    if not re.match(pattern, version):
        print(f"❌ Formato de versión inválido: {version}")
        print("Formato esperado: X.Y.Z o X.Y.Z-suffix (ej: 1.0.0 o 1.0.0-beta)")
        return False
    
    return True


def main():
    """Función principal del script de release."""
    parser = argparse.ArgumentParser(description='Script de release para DataConta FREE')
    parser.add_argument('version', help='Nueva versión (ej: 1.0.1, 1.1.0-beta)')
    parser.add_argument('--notes', help='Notas de release', default="")
    parser.add_argument('--no-build', action='store_true', help='No construir artifacts')
    parser.add_argument('--no-tag', action='store_true', help='No crear tag de Git')
    
    args = parser.parse_args()
    
    # Validar formato de versión
    if not validate_version_format(args.version):
        sys.exit(1)
    
    current_version = get_current_version()
    new_version = args.version
    
    print(f"🚀 Iniciando release: {current_version} → {new_version}")
    
    # Confirmar
    confirm = input(f"❓ ¿Confirmar release v{new_version}? (y/N): ").lower().strip()
    if confirm not in ['y', 'yes', 's', 'si']:
        print("❌ Release cancelado")
        sys.exit(0)
    
    # Actualizar archivos
    update_version_file(new_version)
    
    if args.notes:
        update_changelog(new_version, args.notes)
    
    # Construir artifacts
    if not args.no_build:
        if not build_release_artifacts():
            print("❌ Fallo en construcción de artifacts")
            sys.exit(1)
    
    # Crear tag de Git
    if not args.no_tag:
        tag_message = f"Release v{new_version}\n\n{args.notes if args.notes else 'Nueva versión'}"
        if not create_git_tag(new_version, tag_message):
            print("❌ Fallo en creación de tag")
            sys.exit(1)
    
    print(f"✅ Release v{new_version} completado exitosamente!")
    print("\n📝 Pasos siguientes:")
    print("1. Revisar y hacer commit de cambios en VERSION y CHANGELOG")
    print("2. Hacer push de commits y tags")
    print("3. Crear release en GitHub con artifacts")
    print("4. Actualizar documentación")


if __name__ == '__main__':
    main()
