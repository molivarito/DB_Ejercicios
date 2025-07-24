"""
Diagnóstico detallado del DatabaseManager
"""

import os
import sys
from pathlib import Path

def check_database_structure():
    """Verifica la estructura del directorio database"""
    print("📁 VERIFICANDO ESTRUCTURA DE DATABASE...")
    print("-" * 50)
    
    # Verificar directorio database
    if not Path("database").exists():
        print("❌ Directorio 'database/' no existe")
        print("   Ejecuta: mkdir database")
        return False
    else:
        print("✅ Directorio 'database/' existe")
    
    # Verificar archivo db_manager.py
    db_manager_path = Path("database/db_manager.py")
    if not db_manager_path.exists():
        print("❌ Archivo 'database/db_manager.py' no existe")
        print("   Necesitas crear este archivo")
        return False
    else:
        size = db_manager_path.stat().st_size
        print(f"✅ Archivo 'database/db_manager.py' existe ({size} bytes)")
    
    # Verificar __init__.py
    init_path = Path("database/__init__.py")
    if not init_path.exists():
        print("⚠️  Archivo 'database/__init__.py' no existe")
        print("   Creándolo automáticamente...")
        try:
            init_path.touch()
            print("✅ Archivo __init__.py creado")
        except Exception as e:
            print(f"❌ Error creando __init__.py: {e}")
    else:
        print("✅ Archivo 'database/__init__.py' existe")
    
    return True

def test_database_import():
    """Intenta importar DatabaseManager de diferentes formas"""
    print("\n🔧 PROBANDO IMPORTACIÓN...")
    print("-" * 50)
    
    # Método 1: Import directo
    try:
        from database.db_manager import DatabaseManager
        print("✅ Método 1: from database.db_manager import DatabaseManager - FUNCIONA")
        
        # Verificar métodos
        methods = ['obtener_estadisticas', 'obtener_ejercicios', 'agregar_ejercicio']
        for method in methods:
            if hasattr(DatabaseManager, method):
                print(f"  ✅ Método {method} encontrado")
            else:
                print(f"  ❌ Método {method} NO encontrado")
                
        return True
        
    except ImportError as e:
        print(f"❌ Método 1 falló: {e}")
    
    # Método 2: Import con sys.path
    try:
        sys.path.insert(0, str(Path.cwd()))
        from database.db_manager import DatabaseManager
        print("✅ Método 2: con sys.path - FUNCIONA")
        return True
    except ImportError as e:
        print(f"❌ Método 2 falló: {e}")
    
    # Método 3: Verificar contenido del archivo
    print("\n📄 VERIFICANDO CONTENIDO DEL ARCHIVO...")
    try:
        with open("database/db_manager.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "class DatabaseManager" in content:
            print("✅ Clase DatabaseManager encontrada en el archivo")
            
            # Buscar métodos específicos
            if "def obtener_estadisticas" in content:
                print("✅ Método obtener_estadisticas encontrado")
            else:
                print("❌ Método obtener_estadisticas NO encontrado")
                
            if "def obtener_ejercicios" in content:
                print("✅ Método obtener_ejercicios encontrado")
            else:
                print("❌ Método obtener_ejercicios NO encontrado")
                
            # Mostrar primeras líneas
            print("\n📝 Primeras 10 líneas del archivo:")
            lines = content.split('\n')[:10]
            for i, line in enumerate(lines, 1):
                print(f"{i:3}: {line}")
                
        else:
            print("❌ Clase DatabaseManager NO encontrada en el archivo")
            
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
    
    return False

def test_database_connection():
    """Intenta crear una instancia de DatabaseManager"""
    print("\n🗄️ PROBANDO CONEXIÓN A BASE DE DATOS...")
    print("-" * 50)
    
    try:
        # Agregar el directorio actual al path
        sys.path.insert(0, str(Path.cwd()))
        
        # Intentar importar
        from database.db_manager import DatabaseManager
        
        # Crear instancia
        print("📊 Creando instancia de DatabaseManager...")
        db = DatabaseManager()
        print("✅ DatabaseManager instanciado correctamente")
        
        # Probar métodos
        print("\n🔍 Probando métodos...")
        
        try:
            stats = db.obtener_estadisticas()
            print(f"✅ obtener_estadisticas() funciona")
            print(f"   Total ejercicios: {stats.get('total_ejercicios', 0)}")
        except Exception as e:
            print(f"❌ Error en obtener_estadisticas(): {e}")
        
        try:
            ejercicios = db.obtener_ejercicios()
            print(f"✅ obtener_ejercicios() funciona")
            print(f"   Ejercicios encontrados: {len(ejercicios)}")
        except Exception as e:
            print(f"❌ Error en obtener_ejercicios(): {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_sqlite_database():
    """Verifica si existe el archivo de base de datos SQLite"""
    print("\n💾 VERIFICANDO ARCHIVO SQLITE...")
    print("-" * 50)
    
    db_file = Path("database/ejercicios.db")
    
    if db_file.exists():
        size = db_file.stat().st_size / 1024  # KB
        print(f"✅ Archivo ejercicios.db existe ({size:.1f} KB)")
        
        # Verificar si tiene contenido
        if size < 10:  # Menos de 10KB probablemente está vacía
            print("⚠️  La base de datos parece estar vacía")
        else:
            print("✅ La base de datos tiene contenido")
            
        return True
    else:
        print("❌ Archivo ejercicios.db NO existe")
        print("   Se creará automáticamente al ejecutar DatabaseManager")
        return False

def suggest_fixes():
    """Sugiere soluciones basadas en los problemas encontrados"""
    print("\n🛠️ SOLUCIONES SUGERIDAS:")
    print("=" * 50)
    
    # Verificar si falta __init__.py
    if not Path("database/__init__.py").exists():
        print("\n1. Crear archivo database/__init__.py:")
        print("   touch database/__init__.py")
    
    # Verificar si el archivo db_manager.py está vacío o corrupto
    db_path = Path("database/db_manager.py")
    if db_path.exists():
        size = db_path.stat().st_size
        if size < 100:  # Archivo muy pequeño
            print("\n2. El archivo db_manager.py parece estar vacío o incompleto")
            print("   Descarga el archivo correcto de:")
            print("   https://raw.githubusercontent.com/molivarito/DB_Ejercicios/main/database/db_manager.py")
    
    print("\n3. Si persisten los problemas, verifica:")
    print("   - Que estés en el directorio correcto (DB_Ejercicios)")
    print("   - Que el entorno conda esté activado: conda activate ejercicios-sys")
    print("   - Permisos de lectura/escritura en los archivos")

def main():
    print("🔍 DIAGNÓSTICO DETALLADO DE DATABASE MANAGER")
    print("=" * 50)
    print(f"📁 Directorio actual: {Path.cwd()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📦 Python Path: {sys.path[0]}")
    
    # Ejecutar verificaciones
    structure_ok = check_database_structure()
    
    if structure_ok:
        import_ok = test_database_import()
        db_ok = test_database_connection()
        sqlite_ok = check_sqlite_database()
    else:
        import_ok = False
        db_ok = False
        sqlite_ok = False
    
    # Resumen
    print("\n📊 RESUMEN DETALLADO:")
    print("=" * 50)
    print(f"Estructura directorios: {'✅ OK' if structure_ok else '❌ FALTA'}")
    print(f"Importación módulo:     {'✅ OK' if import_ok else '❌ FALLA'}")
    print(f"Conexión BD:            {'✅ OK' if db_ok else '❌ FALLA'}")
    print(f"Archivo SQLite:         {'✅ OK' if sqlite_ok else '⚠️  NO EXISTE'}")
    
    if not (structure_ok and import_ok):
        suggest_fixes()
    else:
        print("\n✅ DatabaseManager parece estar correctamente configurado")

if __name__ == "__main__":
    main()