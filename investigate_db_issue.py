"""
Investigar el problema con el archivo db_manager completo
"""

from pathlib import Path
import ast

def analyze_db_manager():
    """Analiza el archivo db_manager_full.py para encontrar el problema"""
    print("🔍 ANALIZANDO ARCHIVO DB_MANAGER COMPLETO")
    print("=" * 60)
    
    db_file = Path("database/db_manager_full.py")
    
    if not db_file.exists():
        print("❌ No se encuentra database/db_manager_full.py")
        return
    
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Archivo: {db_file}")
    print(f"📊 Tamaño: {len(content)} bytes")
    
    # 1. Buscar la definición de clase
    print("\n🔎 Buscando definición de clase...")
    lines = content.split('\n')
    
    class_found = False
    indent_issues = []
    
    for i, line in enumerate(lines, 1):
        # Buscar clase
        if 'class DatabaseManager' in line:
            class_found = True
            print(f"✅ Clase encontrada en línea {i}: {line.strip()}")
            
            # Verificar indentación
            if line.startswith(' ') or line.startswith('\t'):
                indent_issues.append(f"⚠️  Línea {i}: La clase tiene indentación (no debe tenerla)")
        
        # Buscar problemas de indentación en métodos
        if 'def ' in line and i < 100:  # Revisar primeros 100 líneas
            # Contar espacios al inicio
            spaces = len(line) - len(line.lstrip())
            if class_found and spaces != 4:
                if 'def __init__' in line:
                    print(f"   Línea {i}: método __init__ con {spaces} espacios")
                elif spaces == 0 and 'class' not in lines[i-2]:
                    indent_issues.append(f"⚠️  Línea {i}: método sin indentación: {line.strip()}")
    
    if not class_found:
        print("❌ Clase DatabaseManager NO encontrada")
    
    # 2. Verificar estructura con AST
    print("\n🐍 Analizando estructura con AST...")
    try:
        tree = ast.parse(content)
        
        # Buscar la clase
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        for cls in classes:
            if cls.name == 'DatabaseManager':
                print(f"✅ Clase DatabaseManager encontrada por AST")
                print(f"   Métodos encontrados:")
                
                methods = [node.name for node in cls.body if isinstance(node, ast.FunctionDef)]
                for method in methods[:10]:  # Mostrar primeros 10
                    print(f"   - {method}")
                
                if len(methods) > 10:
                    print(f"   ... y {len(methods) - 10} más")
                    
                # Verificar métodos clave
                required_methods = ['__init__', 'obtener_estadisticas', 'obtener_ejercicios']
                for req_method in required_methods:
                    if req_method in methods:
                        print(f"   ✅ {req_method} presente")
                    else:
                        print(f"   ❌ {req_method} NO encontrado")
                
                break
        else:
            print("❌ Clase DatabaseManager no encontrada por AST")
            
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   Línea {e.lineno}: {e.text}")
    except Exception as e:
        print(f"❌ Error analizando AST: {e}")
    
    # 3. Buscar problemas comunes
    print("\n🔍 Buscando problemas comunes...")
    
    # Caracteres invisibles
    if '\u200b' in content or '\u00a0' in content:
        print("⚠️  Caracteres invisibles detectados")
    
    # Tabulaciones vs espacios
    if '\t' in content and '    ' in content:
        print("⚠️  Mezcla de tabulaciones y espacios")
    
    # Problemas de encoding
    try:
        content.encode('ascii')
    except UnicodeEncodeError:
        print("⚠️  Caracteres no-ASCII en el archivo")
    
    if indent_issues:
        print("\n⚠️  Problemas de indentación encontrados:")
        for issue in indent_issues[:5]:
            print(f"   {issue}")
    
    # 4. Sugerir solución
    print("\n💡 SOLUCIÓN SUGERIDA:")
    if indent_issues or not class_found:
        print("El archivo parece tener problemas de estructura.")
        print("Recomendación: Usar el archivo create_correct_db_manager.py")
        print("que tiene el contenido correcto.")
    else:
        print("El archivo parece estar bien estructurado.")
        print("El problema puede ser de importación o cache.")

def compare_files():
    """Compara el archivo actual con el backup"""
    print("\n📊 COMPARANDO ARCHIVOS")
    print("-" * 60)
    
    current = Path("database/db_manager.py")
    backup = Path("database/db_manager_full.py")
    
    if current.exists():
        current_size = current.stat().st_size
        print(f"Archivo actual: {current_size} bytes")
    
    if backup.exists():
        backup_size = backup.stat().st_size
        print(f"Archivo backup: {backup_size} bytes")
        
        # Mostrar primeras líneas del backup
        print("\nPrimeras 20 líneas del backup:")
        with open(backup, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if i > 20:
                    break
                print(f"{i:3}: {line.rstrip()}")

def main():
    analyze_db_manager()
    compare_files()
    
    print("\n🔧 ACCIONES RECOMENDADAS:")
    print("1. Continuar con la versión mínima por ahora")
    print("2. Ejecutar: python test_integration_v3.py")
    print("3. Si necesitas la versión completa, ejecutar:")
    print("   python create_correct_db_manager.py")

if __name__ == "__main__":
    main()