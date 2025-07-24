"""
Arreglar el problema de escape en las funciones de reemplazo
"""

import re
from pathlib import Path
import shutil

def fix_replace_functions():
    """Arregla las funciones de reemplazo que causan el error"""
    print("🔧 ARREGLANDO FUNCIONES DE REEMPLAZO")
    print("=" * 60)
    
    pdf_path = Path("generators/pdf_generator.py")
    
    # Hacer backup
    backup_path = Path("generators/pdf_generator_escape_backup.py")
    shutil.copy(pdf_path, backup_path)
    print(f"✅ Backup: {backup_path}")
    
    # Leer archivo
    with open(pdf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # El problema es que los strings de reemplazo contienen \c que se interpreta como escape
    # Necesitamos usar raw strings o escapar correctamente
    
    # Buscar y reemplazar las funciones problemáticas
    replacements = [
        # _replace_guia_config
        (
            r'new_config = f"""\\configurarguia\{\{',
            r'new_config = r"""\configurarguia{'
        ),
        # _replace_prueba_config
        (
            r'new_config = f"""\\configurarprueba\{\{',
            r'new_config = r"""\configurarprueba{'
        ),
        # _replace_tarea_config
        (
            r'new_config = f"""\\configurartarea\{\{',
            r'new_config = r"""\configurartarea{'
        ),
        # También necesitamos cambiar los patrones a raw strings
        (
            r"config_pattern = r'\\\\configurarguia",
            r"config_pattern = r'\\configurarguia"
        ),
        (
            r"config_pattern = r'\\\\configurarprueba",
            r"config_pattern = r'\\configurarprueba"
        ),
        (
            r"config_pattern = r'\\\\configurartarea",
            r"config_pattern = r'\\configurartarea"
        ),
    ]
    
    # Aplicar reemplazos
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Reemplazado: {old[:30]}...")
    
    # Guardar
    with open(pdf_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo actualizado")

def test_fixed_regex():
    """Prueba que los regex arreglados funcionen"""
    print("\n🧪 PROBANDO REGEX ARREGLADOS")
    print("-" * 60)
    
    # Probar los patrones
    test_patterns = [
        (r'\\configurarguia\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}', 'guia'),
        (r'\\configurarprueba\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}', 'prueba'),
        (r'\\configurartarea\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}', 'tarea')
    ]
    
    test_content = r"\configurarguia{Test}{Test}{Test}{Test}{Test}{Test}"
    
    for pattern, name in test_patterns:
        try:
            # El problema es usar f-string con \c
            # Solución: usar raw string
            new_config = r"\configurar" + name + "{Nueva}{Config}{Test}{Test}{Test}{Test}"
            
            if name == 'guia':
                result = re.sub(pattern, new_config, test_content, flags=re.DOTALL)
                print(f"✅ Patrón {name} funciona")
        except re.error as e:
            print(f"❌ Patrón {name} error: {e}")

def fix_with_simple_approach():
    """Arreglo más simple y directo"""
    print("\n🔨 APLICANDO ARREGLO SIMPLE")
    print("-" * 60)
    
    pdf_path = Path("generators/pdf_generator.py")
    
    with open(pdf_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar y arreglar líneas específicas
    for i, line in enumerate(lines):
        # Arreglar new_config lines
        if 'new_config = f"""\\configurar' in line:
            # Cambiar f-string a raw string
            lines[i] = line.replace('f"""\\configurar', 'r"""\configurar')
            print(f"✅ Arreglada línea {i+1}")
        
        # También arreglar las llaves dobles {{ }} que no son necesarias en raw strings
        if i > 0 and 'r"""\configurar' in lines[i-1]:
            # En las siguientes líneas, cambiar {{ }} por { }
            if '{{' in line:
                lines[i] = line.replace('{{', '{').replace('}}', '}')
    
    # Guardar
    with open(pdf_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Arreglo simple aplicado")

def verify_syntax():
    """Verifica que el archivo tenga sintaxis correcta"""
    print("\n🐍 VERIFICANDO SINTAXIS")
    print("-" * 60)
    
    pdf_path = Path("generators/pdf_generator.py")
    
    try:
        with open(pdf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, str(pdf_path), 'exec')
        print("✅ Sintaxis correcta")
        
        # Verificar que ya no hay f-strings con \c
        if 'f"""\\configurar' in content:
            print("⚠️  Aún hay f-strings con \\configurar")
        else:
            print("✅ No hay f-strings problemáticos")
            
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        return False

def main():
    # Intentar arreglo simple primero
    fix_with_simple_approach()
    
    # Verificar
    if verify_syntax():
        test_fixed_regex()
        print("\n✅ Problema arreglado")
        print("🚀 Ejecuta: python test_integration_v3.py")
    else:
        print("\n❌ Aún hay problemas")
        print("Intenta el arreglo completo:")
        fix_replace_functions()

if __name__ == "__main__":
    main()