"""
Forzar recarga del módulo DatabaseManager
"""

import sys
import os
from pathlib import Path

def check_file_content():
    """Verifica el contenido del archivo actual"""
    print("📄 VERIFICANDO CONTENIDO DEL ARCHIVO...")
    print("-" * 60)
    
    db_path = Path("database/db_manager.py")
    
    with open(db_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Tamaño del archivo: {len(content)} bytes")
    
    # Buscar métodos clave
    methods = [
        'obtener_estadisticas',
        'obtener_ejercicios',
        'agregar_ejercicio',
        'obtener_unidades_tematicas'
    ]
    
    print("\n🔍 Buscando métodos en el archivo:")
    for method in methods:
        if f"def {method}" in content:
            print(f"  ✅ {method} - ENCONTRADO en el archivo")
            # Mostrar la línea donde aparece
            for i, line in enumerate(content.split('\n'), 1):
                if f"def {method}" in line:
                    print(f"     Línea {i}: {line.strip()}")
                    break
        else:
            print(f"  ❌ {method} - NO encontrado")
    
    # Mostrar las primeras líneas para verificar
    print("\n📝 Primeras 20 líneas del archivo:")
    lines = content.split('\n')[:20]
    for i, line in enumerate(lines, 1):
        print(f"{i:3}: {line}")
    
    return content

def clear_python_cache():
    """Limpia el cache de Python para forzar recarga"""
    print("\n🧹 LIMPIANDO CACHE DE PYTHON...")
    print("-" * 60)
    
    # Eliminar módulos del cache
    modules_to_remove = [
        'database',
        'database.db_manager',
        'db_manager'
    ]
    
    for module in modules_to_remove:
        if module in sys.modules:
            del sys.modules[module]
            print(f"  ✅ Eliminado del cache: {module}")
    
    # Eliminar archivos .pyc
    pycache_dir = Path("database/__pycache__")
    if pycache_dir.exists():
        for pyc_file in pycache_dir.glob("*.pyc"):
            pyc_file.unlink()
            print(f"  ✅ Eliminado: {pyc_file.name}")
        
        # Intentar eliminar el directorio
        try:
            pycache_dir.rmdir()
            print("  ✅ Directorio __pycache__ eliminado")
        except:
            pass

def test_import_fresh():
    """Prueba importar con módulo fresco"""
    print("\n🔄 IMPORTANDO MÓDULO FRESCO...")
    print("-" * 60)
    
    try:
        # Asegurarse de que Python vea el directorio actual
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            print(f"✅ Agregado al path: {current_dir}")
        
        # Importar
        print("Importando DatabaseManager...")
        from database.db_manager import DatabaseManager
        
        print("✅ Importación exitosa")
        
        # Crear instancia
        db = DatabaseManager()
        print("✅ Instancia creada")
        
        # Verificar métodos
        print("\n📋 Verificando métodos en la instancia:")
        
        all_methods = [attr for attr in dir(db) if not attr.startswith('_')]
        print(f"\nMétodos disponibles ({len(all_methods)}):")
        for method in sorted(all_methods):
            print(f"  • {method}")
        
        # Verificar métodos específicos
        print("\n🎯 Métodos esperados:")
        expected = [
            'obtener_estadisticas',
            'obtener_ejercicios',
            'agregar_ejercicio',
            'obtener_unidades_tematicas'
        ]
        
        for method in expected:
            if hasattr(db, method):
                print(f"  ✅ {method}")
                # Intentar ejecutar
                try:
                    if method == 'obtener_estadisticas':
                        result = db.obtener_estadisticas()
                        print(f"     → Ejecutado: {result.get('total_ejercicios', 0)} ejercicios")
                except Exception as e:
                    print(f"     → Error ejecutando: {e}")
            else:
                print(f"  ❌ {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 FORZANDO RECARGA DE DATABASE MANAGER")
    print("=" * 60)
    
    # Paso 1: Verificar contenido del archivo
    content = check_file_content()
    
    if "def obtener_estadisticas" not in content:
        print("\n❌ El archivo NO contiene los métodos esperados")
        print("🔄 El archivo puede estar corrupto o ser la versión incorrecta")
        print("\nIntenta descargar manualmente:")
        print("1. Ve a: https://github.com/molivarito/DB_Ejercicios/blob/main/database/db_manager.py")
        print("2. Click en 'Raw'")
        print("3. Guarda el contenido como database/db_manager.py")
        return
    
    # Paso 2: Limpiar cache
    clear_python_cache()
    
    # Paso 3: Probar importación fresca
    success = test_import_fresh()
    
    if success:
        print("\n✅ ¡DatabaseManager cargado correctamente!")
        print("🚀 Ahora ejecuta: python test_integration_v3.py")
    else:
        print("\n❌ Aún hay problemas con la importación")
        print("Intenta:")
        print("1. Reiniciar el terminal")
        print("2. Salir y volver a entrar al entorno conda")
        print("3. conda deactivate && conda activate ejercicios-sys")

if __name__ == "__main__":
    main()