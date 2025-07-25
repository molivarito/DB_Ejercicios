"""
Debug del problema de importación de ejercicios
"""

from pathlib import Path
import sqlite3

def check_import_function():
    """Verifica cómo está implementada la función de importación"""
    print("🔍 VERIFICANDO FUNCIÓN DE IMPORTACIÓN EN APP.PY")
    print("=" * 60)
    
    app_path = Path("app.py")
    
    if not app_path.exists():
        print("❌ No se encuentra app.py")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la función show_import_latex
    if 'show_import_latex' in content:
        print("✅ Función show_import_latex encontrada")
        
        # Buscar cómo se importan los ejercicios
        lines = content.split('\n')
        in_import_function = False
        relevant_lines = []
        
        for i, line in enumerate(lines):
            if 'def show_import_latex' in line:
                in_import_function = True
                print(f"\nFunción encontrada en línea {i+1}")
            
            if in_import_function:
                # Buscar líneas clave
                if any(keyword in line for keyword in ['batch_import', 'agregar_ejercicio', 'import_exercises', 'db_manager']):
                    relevant_lines.append((i+1, line.strip()))
                
                # Si encontramos otra función, paramos
                if 'def ' in line and 'show_import_latex' not in line and i > 0:
                    break
        
        if relevant_lines:
            print("\n📝 Líneas relevantes encontradas:")
            for line_num, line in relevant_lines:
                print(f"  Línea {line_num}: {line}")
        else:
            print("\n⚠️ No se encontraron llamadas a importación en la función")
    else:
        print("❌ No se encuentra función show_import_latex")

def check_database_content():
    """Verifica el contenido actual de la base de datos"""
    print("\n🗄️ VERIFICANDO CONTENIDO DE LA BASE DE DATOS")
    print("-" * 60)
    
    db_path = Path("database/ejercicios.db")
    
    if not db_path.exists():
        print("❌ No existe el archivo de base de datos")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Contar ejercicios
        cursor.execute("SELECT COUNT(*) FROM ejercicios")
        count = cursor.fetchone()[0]
        print(f"📊 Total ejercicios en BD: {count}")
        
        if count > 0:
            # Mostrar algunos ejercicios
            cursor.execute("SELECT id, titulo, unidad_tematica FROM ejercicios LIMIT 5")
            ejercicios = cursor.fetchall()
            print("\n📋 Primeros ejercicios:")
            for ej in ejercicios:
                print(f"  ID {ej[0]}: {ej[1]} ({ej[2]})")
        
        # Verificar estructura de la tabla
        cursor.execute("PRAGMA table_info(ejercicios)")
        columns = cursor.fetchall()
        print(f"\n📊 Columnas en la tabla: {len(columns)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accediendo BD: {e}")

def create_import_patch():
    """Crea un parche para la función de importación"""
    print("\n🔧 CREANDO PARCHE PARA IMPORTACIÓN")
    print("-" * 60)
    
    patch_content = '''"""
Parche para corregir la importación de ejercicios
Agregar este código al final de la función show_import_latex en app.py
"""

# CÓDIGO PARA AGREGAR DESPUÉS DE exercises = parser.parse_exercises(content)

if exercises:
    # Importar ejercicios usando el DatabaseManager
    try:
        db_manager = DatabaseManager()
        
        # Preparar ejercicios para importación
        ejercicios_preparados = []
        for ex in exercises:
            # Asegurar que tienen los campos mínimos
            ejercicio = {
                'titulo': ex.get('titulo', 'Sin título'),
                'enunciado': ex.get('enunciado', ''),
                'unidad_tematica': ex.get('unidad_tematica', 'General'),
                'nivel_dificultad': ex.get('nivel_dificultad', 'Intermedio'),
                'modalidad': ex.get('modalidad', 'Teórico'),
                'tiempo_estimado': ex.get('tiempo_estimado', 20),
                'solucion_completa': ex.get('solucion_completa', ''),
                'fuente': uploaded_file.name if uploaded_file else 'Importación manual'
            }
            
            # Agregar campos opcionales si existen
            for campo in ['datos_entrada', 'codigo_python', 'respuesta_final', 'prerrequisitos']:
                if campo in ex:
                    ejercicio[campo] = ex[campo]
            
            ejercicios_preparados.append(ejercicio)
        
        # Importar batch
        resultado = db_manager.batch_import_exercises(
            ejercicios_preparados,
            archivo_origen=uploaded_file.name if uploaded_file else 'Manual'
        )
        
        if resultado['imported'] > 0:
            st.success(f"✅ {resultado['imported']} ejercicios importados exitosamente")
            st.balloons()
        
        if resultado['errors']:
            st.error(f"❌ {len(resultado['errors'])} errores durante la importación")
            for error in resultado['errors'][:5]:  # Mostrar primeros 5 errores
                st.error(f"  • {error}")
                
    except Exception as e:
        st.error(f"❌ Error importando ejercicios: {str(e)}")
        st.exception(e)
'''
    
    # Guardar parche
    patch_path = Path("import_patch.py")
    with open(patch_path, 'w', encoding='utf-8') as f:
        f.write(patch_content)
    
    print(f"✅ Parche guardado en: {patch_path}")
    print("\n📋 INSTRUCCIONES:")
    print("1. Abre app.py")
    print("2. Busca la función show_import_latex()")
    print("3. Encuentra donde dice 'exercises = parser.parse_exercises(content)'")
    print("4. Después de esa línea, agrega el código del parche")
    print("5. O simplemente asegúrate de que esté llamando a db_manager.batch_import_exercises()")

def test_direct_import():
    """Prueba importación directa para verificar que funciona"""
    print("\n🧪 PROBANDO IMPORTACIÓN DIRECTA")
    print("-" * 60)
    
    try:
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        
        # Ejercicio de prueba
        ejercicio_test = {
            'titulo': 'Ejercicio de Prueba Directa',
            'enunciado': 'Este es un ejercicio de prueba para verificar la importación',
            'unidad_tematica': 'Pruebas',
            'nivel_dificultad': 'Básico',
            'modalidad': 'Teórico',
            'tiempo_estimado': 5
        }
        
        # Intentar agregar
        id_nuevo = db.agregar_ejercicio(ejercicio_test)
        print(f"✅ Ejercicio agregado con ID: {id_nuevo}")
        
        # Verificar
        ejercicios = db.obtener_ejercicios()
        print(f"✅ Total ejercicios después de agregar: {len(ejercicios)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importación directa: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Verificar función de importación
    check_import_function()
    
    # Verificar contenido de BD
    check_database_content()
    
    # Probar importación directa
    if test_direct_import():
        print("\n✅ La importación directa funciona")
        print("❌ El problema está en app.py")
        
        # Crear parche
        create_import_patch()
    else:
        print("\n❌ Hay un problema con el DatabaseManager")

if __name__ == "__main__":
    main()