"""
Debug detallado del error 'bad escape \c'
"""

import traceback
import re
from pathlib import Path

def test_regex_patterns():
    """Prueba diferentes patrones regex que podrían causar el error"""
    print("🔍 PROBANDO PATRONES REGEX")
    print("=" * 60)
    
    # Patrones sospechosos
    test_patterns = [
        r'\\c',
        r'\c',
        r'(?<!\\)',
        r'(?<!\\\\)',
        r'\\configurarguia',
        r'\\configurarprueba',
        r'\\configurartarea'
    ]
    
    test_text = "Texto de prueba con configuración"
    
    for pattern in test_patterns:
        try:
            result = re.search(pattern, test_text)
            print(f"✅ Patrón '{pattern}' - OK")
        except re.error as e:
            print(f"❌ Patrón '{pattern}' - Error: {e}")

def find_problematic_code():
    """Busca código problemático en el PDF generator"""
    print("\n📄 ANALIZANDO PDF GENERATOR")
    print("-" * 60)
    
    pdf_path = Path("generators/pdf_generator.py")
    
    with open(pdf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar patrones problemáticos
    problematic_patterns = [
        (r'\\c(?![a-zA-Z])', 'Escape \\c suelto'),
        (r're\.sub.*\\c', 'regex con \\c'),
        (r're\.search.*\\c', 'regex search con \\c'),
        (r'config_pattern.*\\c', 'pattern de config'),
        (r'\\\\c(?![a-zA-Z])', 'Doble escape \\\\c'),
    ]
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        for pattern, desc in problematic_patterns:
            if re.search(pattern, line):
                print(f"⚠️  Línea {i+1} - {desc}:")
                print(f"    {line.strip()}")

def test_minimal_pdf_generation():
    """Prueba generación mínima de PDF"""
    print("\n🧪 TEST MÍNIMO DE GENERACIÓN")
    print("-" * 60)
    
    try:
        from generators.pdf_generator import ExercisePDFGenerator
        
        # Crear generador
        generator = ExercisePDFGenerator("test_output_debug", "templates")
        
        # Datos mínimos
        minimal_exercise = {
            'titulo': 'Test',
            'enunciado': 'Prueba simple sin caracteres especiales',
            'unidad_tematica': 'Test',
            'nivel_dificultad': 'Basico',  # Sin tilde
            'modalidad': 'Teorico',  # Sin tilde
            'tiempo_estimado': 10,
            'puntos': 5,
            'solucion_completa': 'Solucion simple'
        }
        
        minimal_info = {
            'nombre': 'Test Guia',
            'unidad': 'Test',
            'descripcion': 'Descripcion simple'
        }
        
        print("Intentando generar con datos mínimos...")
        
        # Intentar generar
        try:
            result = generator.generate_guia([minimal_exercise], minimal_info)
            print(f"✅ Generación exitosa: {result}")
        except Exception as e:
            print(f"❌ Error en generación: {e}")
            # Rastrear exactamente dónde ocurre
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ Error importando: {e}")

def check_template_patterns():
    """Verifica patrones en los templates"""
    print("\n📄 VERIFICANDO TEMPLATES")
    print("-" * 60)
    
    templates = ['guia_template.tex', 'prueba_template.tex', 'tarea_template.tex']
    
    for template_name in templates:
        template_path = Path('templates') / template_name
        
        if template_path.exists():
            print(f"\n📝 {template_name}:")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar comandos que empiecen con \c
            commands = re.findall(r'\\c[a-zA-Z]+', content)
            unique_commands = set(commands)
            
            if unique_commands:
                print(f"   Comandos encontrados: {', '.join(sorted(unique_commands))}")
            
            # Buscar patrones problemáticos
            if re.search(r'\\c(?![a-zA-Z])', content):
                print(f"   ⚠️ Encontrado \\c suelto")

def test_direct_replacement():
    """Prueba el reemplazo directo que está causando el problema"""
    print("\n🔧 PROBANDO REEMPLAZO DIRECTO")
    print("-" * 60)
    
    # Simular lo que hace _replace_guia_config
    config_pattern = r'\\configurarguia\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}'
    
    test_content = r"""
\configurarguia{
  Título
}{
  Unidad
}{
  Fecha
}{
  Profesor
}{
  Semestre
}{
  Descripción
}
"""
    
    new_config = r"""\configurarguia{
  Nueva config
}{
  Test
}{
  Test
}{
  Test
}{
  Test
}{
  Test
}"""
    
    try:
        result = re.sub(config_pattern, new_config, test_content, flags=re.DOTALL)
        print("✅ Reemplazo exitoso")
    except re.error as e:
        print(f"❌ Error en regex: {e}")
        print(f"   Patrón problemático: {config_pattern}")

def main():
    # Tests en orden
    test_regex_patterns()
    find_problematic_code()
    check_template_patterns()
    test_direct_replacement()
    test_minimal_pdf_generation()
    
    print("\n💡 CONCLUSIÓN:")
    print("El error 'bad escape \\c' probablemente viene de:")
    print("1. Un patrón regex mal formado")
    print("2. Un comando LaTeX que empieza con \\c")
    print("3. Un problema en la función de reemplazo de configuración")

if __name__ == "__main__":
    main()