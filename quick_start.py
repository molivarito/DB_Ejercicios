#!/usr/bin/env python3
"""
Script de inicio rápido para el Sistema de Gestión de Ejercicios
Señales y Sistemas - PUC Chile

Este script:
1. Verifica dependencias
2. Inicializa la base de datos
3. Carga datos de ejemplo
4. Lanza la aplicación
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Verifica que Python sea 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 o superior requerido")
        print(f"Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def check_latex():
    """Verifica que LaTeX esté instalado"""
    try:
        result = subprocess.run(['pdflatex', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ LaTeX encontrado")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  LaTeX no encontrado - La generación de PDFs no funcionará")
    print("   Instala LaTeX para usar todas las funcionalidades:")
    print("   - Windows: MiKTeX o TeX Live")
    print("   - macOS: MacTeX") 
    print("   - Linux: sudo apt-get install texlive-full")
    return False

def check_conda():
    """Verifica si conda está disponible"""
    try:
        result = subprocess.run(['conda', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Conda encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("ℹ️  Conda no encontrado - usando pip")
    return False

def setup_conda_environment():
    """Configura el entorno conda"""
    print("🐍 Configurando entorno conda...")
    
    env_file = Path("environment.yml")
    if not env_file.exists():
        print("❌ Archivo environment.yml no encontrado")
        return False
    
    try:
        # Crear entorno conda
        print("   Creando entorno 'ejercicios-sys'...")
        subprocess.run(['conda', 'env', 'create', '-f', 'environment.yml'], 
                      check=True)
        
        print("✅ Entorno conda creado correctamente")
        print("💡 Para activar el entorno ejecuta:")
        print("   conda activate ejercicios-sys")
        return True
        
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e):
            print("ℹ️  El entorno 'ejercicios-sys' ya existe")
            update_choice = input("¿Actualizar entorno existente? (y/N): ").lower()
            if update_choice in ['y', 'yes', 's', 'si']:
                try:
                    subprocess.run(['conda', 'env', 'update', '-f', 'environment.yml'], 
                                  check=True)
                    print("✅ Entorno actualizado")
                    return True
                except subprocess.CalledProcessError:
                    print("❌ Error actualizando entorno")
                    return False
            return True
        else:
            print(f"❌ Error creando entorno conda: {e}")
            return False

def install_dependencies():
    """Instala las dependencias según el gestor disponible"""
    print("📦 Configurando dependencias...")
    
    # Verificar si conda está disponible
    has_conda = check_conda()
    
    if has_conda:
        use_conda = input("¿Usar conda para gestionar dependencias? (Y/n): ").lower()
        if use_conda not in ['n', 'no']:
            return setup_conda_environment()
    
    # Fallback a pip
    print("📦 Instalando dependencias con pip...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ Archivo requirements.txt no encontrado")
        return False
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias")
        return False

def create_directories():
    """Crea los directorios necesarios"""
    directories = [
        'database',
        'output', 
        'templates',
        'static/images'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios creados")

def initialize_database():
    """Inicializa la base de datos con datos de ejemplo"""
    print("🗄️  Inicializando base de datos...")
    
    # Importar después de instalar dependencias
    try:
        # Simular la importación del database manager
        # En implementación real: from database.db_manager import DatabaseManager
        
        db_path = "database/ejercicios.db"
        
        # Crear base de datos simple para demo
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla básica
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ejercicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            unidad_tematica TEXT,
            nivel_dificultad TEXT,
            enunciado TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insertar ejercicios de ejemplo
        ejercicios_ejemplo = [
            ("Convolución de señales rectangulares", "Sistemas Continuos", "Básico", 
             "Calcule la convolución y(t) = x(t) * h(t) donde x(t) y h(t) son señales rectangulares."),
            ("FFT de señal con ruido", "Transformada de Fourier Discreta", "Intermedio",
             "Implemente en Python el cálculo de la FFT de una señal sinusoidal con ruido."),
            ("Análisis de estabilidad", "Transformada Z", "Avanzado",
             "Analice la estabilidad del sistema usando la transformada Z.")
        ]
        
        cursor.executemany("""
        INSERT INTO ejercicios (titulo, unidad_tematica, nivel_dificultad, enunciado)
        VALUES (?, ?, ?, ?)
        """, ejercicios_ejemplo)
        
        conn.commit()
        conn.close()
        
        print("✅ Base de datos inicializada con ejercicios de ejemplo")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

def create_sample_config():
    """Crea archivos de configuración de ejemplo"""
    config_content = """# Configuración del Sistema de Gestión de Ejercicios

# Información del curso
COURSE_NAME = "IEE2103 - Señales y Sistemas"
PROFESSOR_NAME = "Patricio de la Cuadra"
UNIVERSITY = "Pontificia Universidad Católica de Chile"
SEMESTER = "2024-2"

# Configuración de base de datos
DATABASE_PATH = "database/ejercicios.db"

# Configuración de exportación
OUTPUT_DIR = "output"
LATEX_TEMPLATE = "templates/prueba_template.tex"

# Configuración de aplicación
DEBUG = True
PORT = 8501
"""
    
    with open("config.py", "w") as f:
        f.write(config_content)
    
    print("✅ Archivo de configuración creado")

def launch_application():
    """Lanza la aplicación Streamlit"""
    print("🚀 Lanzando aplicación...")
    
    # Verificar si estamos en entorno conda
    if 'CONDA_DEFAULT_ENV' in os.environ:
        env_name = os.environ['CONDA_DEFAULT_ENV']
        if env_name != 'ejercicios-sys':
            print(f"⚠️  Advertencia: Entorno actual '{env_name}' no es 'ejercicios-sys'")
            print("   Para usar el entorno correcto:")
            print("   conda activate ejercicios-sys")
            print("   streamlit run app.py")
            return
        else:
            print(f"✅ Usando entorno conda: {env_name}")
    
    print("   La aplicación se abrirá en http://localhost:8501")
    print("   Presiona Ctrl+C para detener la aplicación")
    
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida")
    except FileNotFoundError:
        print("❌ Error: app.py no encontrado")
        print("   Asegúrate de estar en el directorio correcto")

def main():
    """Función principal del script de inicio"""
    print("=" * 60)
    print("🎓 Sistema de Gestión de Ejercicios - Señales y Sistemas")
    print("   Pontificia Universidad Católica de Chile")
    print("=" * 60)
    print()
    
    # Verificaciones del sistema
    if not check_python_version():
        return
    
    check_latex()
    print()
    
    # Configuración inicial
    print("🔧 Configuración inicial...")
    create_directories()
    create_sample_config()
    
    # Instalar dependencias
    install_choice = input("¿Instalar dependencias de Python? (y/N): ").lower()
    if install_choice in ['y', 'yes', 's', 'si']:
        if not install_dependencies():
            return
    
    # Inicializar base de datos
    db_choice = input("¿Inicializar base de datos con ejemplos? (Y/n): ").lower()
    if db_choice not in ['n', 'no']:
        if not initialize_database():
            return
    
    print()
    print("✅ ¡Configuración completada!")
    print()
    
    # Lanzar aplicación
    launch_choice = input("¿Lanzar aplicación ahora? (Y/n): ").lower()
    if launch_choice not in ['n', 'no']:
        launch_application()
    else:
        print("💡 Para lanzar la aplicación más tarde, ejecuta:")
        print("   streamlit run app.py")

if __name__ == "__main__":
    main()