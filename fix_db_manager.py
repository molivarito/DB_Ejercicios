"""
Script para diagnosticar y arreglar el problema con DatabaseManager
"""

import os
import requests
from pathlib import Path
import shutil

def check_current_file():
    """Verifica el archivo actual"""
    print("📄 VERIFICANDO ARCHIVO ACTUAL...")
    print("-" * 60)
    
    db_path = Path("database/db_manager.py")
    
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"✅ Archivo existe: {size} bytes")
        
        # Leer primeras líneas
        with open(db_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            
        print("\nPrimeras 10 líneas:")
        for i, line in enumerate(lines, 1):
            print(f"{i:2}: {line.rstrip()}")
            
        # Buscar métodos
        with open(db_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "def obtener_estadisticas" in content:
            print("\n✅ Método obtener_estadisticas ENCONTRADO")
        else:
            print("\n❌ Método obtener_estadisticas NO encontrado")
            
        return content
    else:
        print("❌ Archivo no existe")
        return None

def download_correct_version():
    """Descarga la versión correcta de GitHub"""
    print("\n📥 DESCARGANDO VERSIÓN CORRECTA DE GITHUB...")
    print("-" * 60)
    
    url = "https://raw.githubusercontent.com/molivarito/DB_Ejercicios/main/database/db_manager.py"
    
    try:
        # Hacer backup del actual
        db_path = Path("database/db_manager.py")
        if db_path.exists():
            backup_path = Path("database/db_manager_backup.py")
            shutil.copy(db_path, backup_path)
            print(f"✅ Backup creado: {backup_path}")
        
        # Descargar con requests
        print(f"Descargando de: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            content = response.text
            
            # Verificar que tiene los métodos correctos
            if "def obtener_estadisticas" in content:
                print("✅ Contenido verificado - contiene métodos correctos")
                
                # Guardar archivo
                with open(db_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ Archivo guardado: {len(content)} bytes")
                
                # Verificar métodos en el contenido descargado
                methods_to_find = [
                    'obtener_estadisticas',
                    'obtener_ejercicios',
                    'agregar_ejercicio',
                    'obtener_unidades_tematicas'
                ]
                
                print("\n📋 Métodos encontrados en versión descargada:")
                for method in methods_to_find:
                    if f"def {method}" in content:
                        print(f"  ✅ {method}")
                    else:
                        print(f"  ❌ {method}")
                
                return True
            else:
                print("❌ El contenido descargado no tiene los métodos esperados")
                print("Primeras 500 caracteres:")
                print(content[:500])
                return False
        else:
            print(f"❌ Error descargando: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_import():
    """Verifica que se pueda importar correctamente"""
    print("\n🔍 VERIFICANDO IMPORTACIÓN...")
    print("-" * 60)
    
    try:
        # Limpiar cache de importación
        import sys
        if 'database.db_manager' in sys.modules:
            del sys.modules['database.db_manager']
        if 'database' in sys.modules:
            del sys.modules['database']
            
        # Importar de nuevo
        from database.db_manager import DatabaseManager
        
        print("✅ Importación exitosa")
        
        # Verificar métodos
        db = DatabaseManager()
        
        methods = ['obtener_estadisticas', 'obtener_ejercicios']
        for method in methods:
            if hasattr(db, method):
                print(f"✅ Método {method} disponible")
            else:
                print(f"❌ Método {method} NO disponible")
                
        return True
        
    except Exception as e:
        print(f"❌ Error importando: {e}")
        return False

def main():
    print("🔧 DIAGNÓSTICO Y REPARACIÓN DE DATABASE MANAGER")
    print("=" * 60)
    
    # Paso 1: Verificar archivo actual
    current_content = check_current_file()
    
    # Paso 2: Descargar versión correcta
    success = download_correct_version()
    
    if success:
        # Paso 3: Verificar importación
        import_ok = verify_import()
        
        if import_ok:
            print("\n✅ ¡DatabaseManager reparado exitosamente!")
            print("🚀 Ahora ejecuta: python test_integration_v3.py")
        else:
            print("\n❌ Problemas con la importación")
            print("Intenta reiniciar el terminal Python")
    else:
        print("\n❌ No se pudo descargar la versión correcta")
        print("Alternativa manual:")
        print("1. Ve a: https://github.com/molivarito/DB_Ejercicios/blob/main/database/db_manager.py")
        print("2. Copia todo el contenido")
        print("3. Pégalo en database/db_manager.py")

if __name__ == "__main__":
    main()