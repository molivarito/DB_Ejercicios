"""
Diagnóstico rápido del problema de importación
"""

import sys
import os
from pathlib import Path

def diagnose_import_issue():
    print("🔍 DIAGNÓSTICO DE IMPORTACIÓN")
    print("=" * 60)
    
    # 1. Verificar que el archivo existe
    db_file = Path("database/db_manager.py")
    print(f"📄 Archivo db_manager.py existe: {db_file.exists()}")
    
    if db_file.exists():
        print(f"   Tamaño: {db_file.stat().st_size} bytes")
    
    # 2. Verificar __init__.py
    init_file = Path("database/__init__.py")
    print(f"📄 Archivo __init__.py existe: {init_file.exists()}")
    
    # 3. Verificar contenido del archivo
    if db_file.exists():
        print("\n📝 Verificando contenido...")
        with open(db_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la clase
        if "class DatabaseManager" in content:
            print("✅ Clase DatabaseManager encontrada")
            
            # Verificar si hay errores de sintaxis obvios
            lines = content.split('\n')
            for i, line in enumerate(lines[:50], 1):
                if "class DatabaseManager" in line:
                    print(f"   Línea {i}: {line}")
                    # Verificar las siguientes líneas
                    for j in range(i, min(i+5, len(lines))):
                        print(f"   Línea {j}: {lines[j-1]}")
                    break
        else:
            print("❌ Clase DatabaseManager NO encontrada")
    
    # 4. Intentar importar paso a paso
    print("\n🔧 Probando importación paso a paso...")
    
    # Limpiar cache
    if 'database' in sys.modules:
        del sys.modules['database']
    if 'database.db_manager' in sys.modules:
        del sys.modules['database.db_manager']
    
    try:
        print("1. Importando módulo database...")
        import database
        print("   ✅ OK")
        
        print("2. Importando database.db_manager...")
        import database.db_manager
        print("   ✅ OK")
        
        print("3. Importando DatabaseManager desde database.db_manager...")
        from database.db_manager import DatabaseManager
        print("   ✅ OK")
        
        print("4. Creando instancia...")
        db = DatabaseManager()
        print("   ✅ OK")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   Archivo: {e.filename}")
        print(f"   Línea: {e.lineno}")
        print(f"   Texto: {e.text}")
        return False
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_syntax():
    """Verifica la sintaxis del archivo"""
    print("\n🐍 VERIFICANDO SINTAXIS PYTHON...")
    print("-" * 60)
    
    db_file = Path("database/db_manager.py")
    
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Intentar compilar
        compile(content, str(db_file), 'exec')
        print("✅ Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en línea {e.lineno}:")
        print(f"   {e.text}")
        print(f"   {' ' * (e.offset - 1)}^")
        print(f"   {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ Error verificando sintaxis: {e}")
        return False

def create_minimal_db_manager():
    """Crea una versión mínima para testing"""
    print("\n🔧 CREANDO VERSIÓN MÍNIMA DE DB_MANAGER...")
    print("-" * 60)
    
    minimal_content = '''"""
DatabaseManager mínimo para testing
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "database/ejercicios.db"):
        self.db_path = db_path
        self.conn = None
        
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas básicas"""
        return {
            'total_ejercicios': 324,
            'por_unidad': {'Sistemas Continuos': 50, 'Transformada de Fourier': 45},
            'por_dificultad': {'Básico': 100, 'Intermedio': 150, 'Avanzado': 74},
            'por_modalidad': {'Teórico': 200, 'Computacional': 124}
        }
    
    def obtener_ejercicios(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """Retorna lista de ejercicios"""
        # Datos de prueba
        return [
            {
                'id': 1,
                'titulo': 'Convolución básica',
                'enunciado': 'Calcule la convolución y(t) = x(t) * h(t)',
                'unidad_tematica': 'Sistemas Continuos',
                'nivel_dificultad': 'Básico',
                'modalidad': 'Teórico',
                'tiempo_estimado': 15,
                'puntos': 6,
                'solucion_completa': 'Solución de ejemplo'
            }
        ]
    
    def obtener_unidades_tematicas(self) -> List[str]:
        """Retorna lista de unidades"""
        return [
            "Introducción",
            "Sistemas Continuos", 
            "Transformada de Fourier",
            "Transformada de Laplace",
            "Sistemas Discretos",
            "Transformada de Fourier Discreta",
            "Transformada Z"
        ]
'''
    
    # Guardar versión mínima temporalmente
    backup_path = Path("database/db_manager_full.py")
    current_path = Path("database/db_manager.py")
    
    # Hacer backup
    if current_path.exists():
        import shutil
        shutil.copy(current_path, backup_path)
        print(f"✅ Backup guardado en: {backup_path}")
    
    # Escribir versión mínima
    with open(current_path, 'w', encoding='utf-8') as f:
        f.write(minimal_content)
    
    print("✅ Versión mínima creada")
    print("🔄 Prueba ejecutar el test ahora")

def main():
    # Diagnóstico
    success = diagnose_import_issue()
    
    if not success:
        # Verificar sintaxis
        syntax_ok = check_syntax()
        
        if not syntax_ok:
            print("\n💡 SOLUCIÓN SUGERIDA:")
            print("El archivo tiene errores de sintaxis.")
            print("Opciones:")
            print("1. Usar versión mínima temporal: python quick_db_fix.py --minimal")
            print("2. Restaurar desde backup: cp database/db_manager_backup.py database/db_manager.py")
            print("3. Descargar versión correcta manualmente")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--minimal":
        create_minimal_db_manager()
    else:
        main()