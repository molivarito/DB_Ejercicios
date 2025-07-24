"""
Script para verificar qué métodos tiene DatabaseManager localmente
"""

import inspect
from pathlib import Path

def check_local_db_manager():
    """Verifica los métodos disponibles en DatabaseManager local"""
    print("🔍 ANALIZANDO DATABASE MANAGER LOCAL...")
    print("=" * 60)
    
    try:
        # Importar DatabaseManager
        from database.db_manager import DatabaseManager
        
        print("✅ DatabaseManager importado correctamente\n")
        
        # Obtener todos los métodos de la clase
        print("📋 MÉTODOS DISPONIBLES EN DatabaseManager:")
        print("-" * 60)
        
        methods = []
        for name, method in inspect.getmembers(DatabaseManager, predicate=inspect.isfunction):
            if not name.startswith('_'):  # Ignorar métodos privados
                methods.append(name)
                # Obtener la firma del método
                sig = inspect.signature(method)
                print(f"  • {name}{sig}")
        
        print(f"\n📊 Total métodos públicos: {len(methods)}")
        
        # Verificar métodos esperados
        print("\n🎯 VERIFICACIÓN DE MÉTODOS ESPERADOS:")
        print("-" * 60)
        
        expected_methods = [
            'obtener_estadisticas',
            'obtener_ejercicios', 
            'agregar_ejercicio',
            'actualizar_ejercicio',
            'obtener_ejercicio_por_id',
            'obtener_unidades_tematicas',
            'registrar_uso'
        ]
        
        for method in expected_methods:
            if method in methods:
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} - NO ENCONTRADO")
        
        # Si faltan métodos, buscar nombres similares
        missing = [m for m in expected_methods if m not in methods]
        if missing:
            print("\n🔎 BUSCANDO MÉTODOS SIMILARES:")
            print("-" * 60)
            
            # Mapeo de posibles nombres alternativos
            alternatives = {
                'obtener_estadisticas': ['get_stats', 'estadisticas', 'stats', 'get_statistics'],
                'obtener_ejercicios': ['get_exercises', 'ejercicios', 'get_ejercicios', 'buscar_ejercicios'],
                'agregar_ejercicio': ['add_exercise', 'crear_ejercicio', 'nuevo_ejercicio', 'insertar_ejercicio']
            }
            
            for expected in missing:
                print(f"\n  Buscando alternativas para '{expected}':")
                found_alternative = False
                
                # Buscar por nombres alternativos
                if expected in alternatives:
                    for alt in alternatives[expected]:
                        if alt in methods:
                            print(f"    ✅ Encontrado como: {alt}")
                            found_alternative = True
                            break
                
                # Buscar por coincidencia parcial
                if not found_alternative:
                    similar = [m for m in methods if expected.split('_')[0] in m or m in expected]
                    if similar:
                        print(f"    🔍 Métodos similares: {', '.join(similar)}")
                    else:
                        print(f"    ❌ No se encontraron métodos similares")
        
        # Mostrar primeras líneas del archivo para verificar
        print("\n📄 PRIMERAS 30 LÍNEAS DE db_manager.py:")
        print("-" * 60)
        
        db_path = Path("database/db_manager.py")
        with open(db_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:30]
            for i, line in enumerate(lines, 1):
                print(f"{i:3}: {line.rstrip()}")
        
        return methods
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def suggest_solution(methods):
    """Sugiere una solución basada en los métodos encontrados"""
    print("\n💡 SOLUCIÓN SUGERIDA:")
    print("=" * 60)
    
    # Verificar si tiene los métodos esperados
    expected = ['obtener_estadisticas', 'obtener_ejercicios']
    missing = [m for m in expected if m not in methods]
    
    if missing:
        print("\nParece que tu versión local de db_manager.py es diferente a la esperada.")
        print("Tienes dos opciones:\n")
        
        print("OPCIÓN 1: Actualizar con la versión de GitHub")
        print("-" * 40)
        print("curl -o database/db_manager.py https://raw.githubusercontent.com/molivarito/DB_Ejercicios/main/database/db_manager.py")
        
        print("\nOPCIÓN 2: Crear un adaptador")
        print("-" * 40)
        print("Si tu versión local funciona pero tiene nombres diferentes,")
        print("podemos crear un adaptador. Primero necesito saber qué métodos tienes.")
        
        # Si encontramos métodos alternativos, sugerir un wrapper
        if any(m for m in methods if 'ejercicio' in m.lower() or 'exercise' in m.lower()):
            print("\n📝 Parece que tienes métodos relacionados con ejercicios.")
            print("Podemos crear un wrapper para adaptar los nombres.")
    else:
        print("\n✅ Tu DatabaseManager tiene todos los métodos necesarios!")
        print("El problema puede estar en otro lugar.")

def main():
    methods = check_local_db_manager()
    
    if methods:
        suggest_solution(methods)
    else:
        print("\n❌ No se pudieron obtener los métodos de DatabaseManager")

if __name__ == "__main__":
    main()
    