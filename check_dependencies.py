"""
Verificador de dependencias para el PDF Generator
Verifica que todas las librerías necesarias estén instaladas
"""

import sys
import subprocess
from pathlib import Path

def check_python_packages():
    """Verifica paquetes Python necesarios"""
    print("🐍 VERIFICANDO PAQUETES PYTHON")
    print("-" * 40)
    
    required_packages = [
        ('pylatex', 'PyLaTeX'),
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('sqlite3', 'SQLite3 (built-in)'),
        ('pathlib', 'PathLib (built-in)'),
        ('datetime', 'DateTime (built-in)'),
        ('typing', 'Typing (built-in)')
    ]
    
    missing_packages = []
    
    for package, name in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'pathlib':
                from pathlib import Path
            elif package == 'datetime':
                from datetime import datetime
            elif package == 'typing':
                from typing import List, Dict, Optional
            else:
                __import__(package)
            
            print(f"✅ {name}")
            
        except ImportError:
            print(f"❌ {name} - FALTANTE")
            missing_packages.append(package)
    
    return missing_packages

def check_latex_packages():
    """Verifica paquetes LaTeX necesarios"""
    print("\n📄 VERIFICANDO PAQUETES LATEX")
    print("-" * 40)
    
    # Lista de paquetes LaTeX necesarios (de pdf_generator.py)
    latex_packages = [
        'babel',
        'inputenc', 
        'fontenc',
        'amsmath',
        'amsfonts', 
        'amssymb',
        'graphicx',
        'float',
        'enumitem',
        'fancyhdr',
        'titlesec',
        'xcolor',
        'hyperref',
        'geometry'
    ]
    
    print("📋 Paquetes LaTeX requeridos:")
    for pkg in latex_packages:
        print(f"   • {pkg}")
    
    print("\n💡 Para verificar paquetes LaTeX instalados:")
    print("   tlmgr list --installed | grep -E '(babel|amsmath|geometry)'")
    
    return latex_packages

def check_file_structure():
    """Verifica estructura de archivos del proyecto"""
    print("\n📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    print("-" * 40)
    
    required_files = [
        'generators/pdf_generator.py',
        'database/db_manager.py',
        'app.py',
        'utils/latex_parser.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - FALTANTE")
            missing_files.append(file_path)
    
    return missing_files

def check_output_directory():
    """Verifica/crea directorio de salida"""
    print("\n📂 VERIFICANDO DIRECTORIO DE SALIDA")
    print("-" * 40)
    
    output_dirs = ['output', 'test_output']
    
    for dir_name in output_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ existe")
        else:
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ {dir_name}/ creado")
            except Exception as e:
                print(f"❌ Error creando {dir_name}/: {e}")
                return False
    
    return True

def generate_install_commands(missing_packages):
    """Genera comandos para instalar paquetes faltantes"""
    if not missing_packages:
        return
    
    print("\n💊 COMANDOS PARA INSTALAR PAQUETES FALTANTES")
    print("-" * 50)
    
    # Para conda (preferido según environment.yml)
    conda_packages = []
    pip_packages = []
    
    for pkg in missing_packages:
        if pkg in ['pylatex', 'streamlit', 'pandas']:
            conda_packages.append(pkg)
        else:
            pip_packages.append(pkg)
    
    if conda_packages:
        print("📦 Con conda (recomendado):")
        print(f"   conda install {' '.join(conda_packages)}")
    
    if pip_packages:
        print("🐍 Con pip:")
        print(f"   pip install {' '.join(pip_packages)}")
    
    print("\n🔧 Para LaTeX (si falta):")
    print("   • macOS: brew install --cask mactex")
    print("   • Ubuntu: sudo apt-get install texlive-full")
    print("   • Windows: Instalar MiKTeX o TeX Live")

def main():
    """Verificación completa de dependencias"""
    print("🔍 VERIFICADOR DE DEPENDENCIAS - DB_Ejercicios")
    print("=" * 60)
    
    all_good = True
    
    # 1. Verificar paquetes Python
    missing_python = check_python_packages()
    if missing_python:
        all_good = False
    
    # 2. Verificar estructura de archivos
    missing_files = check_file_structure()
    if missing_files:
        all_good = False
    
    # 3. Verificar directorio de salida
    if not check_output_directory():
        all_good = False
    
    # 4. Verificar paquetes LaTeX (informativo)
    check_latex_packages()
    
    # 5. Generar comandos de instalación si es necesario
    if missing_python:
        generate_install_commands(missing_python)
    
    # 6. Resumen final
    print("\n" + "=" * 60)
    if all_good and not missing_python:
        print("🎉 TODAS LAS DEPENDENCIAS ESTÁN LISTAS")
        print("✅ Puedes ejecutar el test del PDF generator")
        print("\n🚀 Ejecuta: python test_pdf_standalone.py")
    else:
        print("⚠️  HAY DEPENDENCIAS FALTANTES")
        print("❌ Instala los paquetes faltantes antes de continuar")
        
        if missing_files:
            print(f"\n📁 Archivos faltantes: {missing_files}")
            print("   Asegúrate de estar en el directorio correcto del proyecto")
    
    print("=" * 60)
    return all_good and not missing_python

if __name__ == "__main__":
    main()