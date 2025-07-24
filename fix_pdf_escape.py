"""
Arreglar el problema de escape en PDF Generator
"""

import re
from pathlib import Path

def check_current_escape():
    """Verifica la función _escape_latex actual"""
    print("🔍 VERIFICANDO FUNCIÓN _escape_latex")
    print("=" * 60)
    
    pdf_gen_path = Path("generators/pdf_generator.py")
    
    with open(pdf_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la función
    lines = content.split('\n')
    escape_start = -1
    escape_end = -1
    
    for i, line in enumerate(lines):
        if 'def _escape_latex' in line:
            escape_start = i
            print(f"Función encontrada en línea {i+1}")
            
            # Buscar el final de la función
            indent = len(line) - len(line.lstrip())
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' ' * (indent + 1)):
                    escape_end = j
                    break
            
            break
    
    if escape_start >= 0:
        print("\n📝 Función actual:")
        for i in range(escape_start, min(escape_end, escape_start + 20)):
            print(f"{i+1:4}: {lines[i]}")
    
    # Buscar uso problemático de raw strings
    problematic_patterns = [
        r'\\c',
        'r"\\c"',
        "r'\\c'",
        'replacements = {',
    ]
    
    print("\n🔎 Buscando patrones problemáticos...")
    for pattern in problematic_patterns:
        if pattern in content:
            print(f"⚠️  Encontrado: {pattern}")

def fix_escape_function():
    """Corrige la función _escape_latex"""
    print("\n🔧 CORRIGIENDO FUNCIÓN _escape_latex")
    print("-" * 60)
    
    pdf_gen_path = Path("generators/pdf_generator.py")
    
    # Leer archivo
    with open(pdf_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Función corregida
    correct_escape = '''    def _escape_latex(self, text: str) -> str:
        """Escapa caracteres especiales de LaTeX (versión conservadora)"""
        if not text:
            return ""
        
        # Solo escapar caracteres que sabemos que causan problemas
        # Ser conservador para no romper LaTeX math existente
        replacements = {
            '&': '\\\\&',
            '%': '\\\\%',
            '#': '\\\\#',
            '_': '\\\\_',
            '~': '\\\\textasciitilde{}',
            '^': '\\\\textasciicircum{}'
        }
        
        for char, escaped in replacements.items():
            # Solo reemplazar si no está ya escapado
            text = re.sub(f'(?<!\\\\\\\\){re.escape(char)}', escaped, text)
        
        return text'''
    
    # Buscar y reemplazar la función
    import re
    
    # Patrón para encontrar la función completa
    pattern = r'def _escape_latex\(self.*?\n(?:.*?\n)*?        return text'
    
    # Verificar si encontramos la función
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    if matches:
        print(f"✅ Función encontrada ({len(matches)} ocurrencia(s))")
        
        # Reemplazar todas las ocurrencias
        for match in reversed(matches):  # Reverso para no afectar índices
            start, end = match.span()
            content = content[:start] + correct_escape + content[end:]
        
        # Hacer backup
        import shutil
        backup_path = Path("generators/pdf_generator_backup.py")
        shutil.copy(pdf_gen_path, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        
        # Guardar archivo corregido
        with open(pdf_gen_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Función _escape_latex corregida")
        
    else:
        print("❌ No se encontró la función _escape_latex")
        print("Intentando método alternativo...")
        
        # Método alternativo: buscar línea por línea
        lines = content.split('\n')
        new_lines = []
        in_escape_function = False
        skip_until_return = False
        
        for i, line in enumerate(lines):
            if 'def _escape_latex' in line:
                in_escape_function = True
                skip_until_return = True
                # Agregar la función corregida
                new_lines.extend(correct_escape.split('\n'))
                continue
            
            if skip_until_return:
                if 'return' in line and in_escape_function:
                    skip_until_return = False
                    in_escape_function = False
                continue
            
            new_lines.append(line)
        
        # Guardar
        with open(pdf_gen_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Función corregida con método alternativo")

def test_escape():
    """Prueba la función de escape"""
    print("\n🧪 PROBANDO FUNCIÓN CORREGIDA")
    print("-" * 60)
    
    # Recargar módulo
    import sys
    if 'generators.pdf_generator' in sys.modules:
        del sys.modules['generators.pdf_generator']
    
    try:
        from generators.pdf_generator import RealTemplatePDFGenerator
        
        generator = RealTemplatePDFGenerator()
        
        # Casos de prueba
        test_cases = [
            "Texto normal",
            "Texto con & ampersand",
            "Porcentaje 50%",
            "Número #1",
            "sub_índice",
            "Tilde ~",
            "Potencia x^2",
            "Ya escapado \\& no debe cambiar",
            "Fórmula $x^2 + y^2 = z^2$"
        ]
        
        print("Casos de prueba:")
        for test in test_cases:
            try:
                result = generator._escape_latex(test)
                print(f"✅ '{test}' → '{result}'")
            except Exception as e:
                print(f"❌ '{test}' → Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    # Verificar problema actual
    check_current_escape()
    
    # Corregir
    fix_escape_function()
    
    # Probar
    success = test_escape()
    
    if success:
        print("\n✅ Función _escape_latex corregida exitosamente")
        print("🚀 Ejecuta ahora: python test_integration_v3.py")
    else:
        print("\n❌ Aún hay problemas")
        print("Revisa el archivo generators/pdf_generator.py manualmente")

if __name__ == "__main__":
    main()