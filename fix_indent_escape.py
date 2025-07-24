"""
Arreglar problema de indentación en _escape_latex
"""

from pathlib import Path
import shutil

def fix_indentation():
    """Arregla el problema de indentación"""
    print("🔧 ARREGLANDO INDENTACIÓN EN PDF GENERATOR")
    print("=" * 60)
    
    pdf_path = Path("generators/pdf_generator.py")
    
    # Leer el archivo
    with open(pdf_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar la línea problemática
    for i, line in enumerate(lines):
        if 'def _escape_latex' in line:
            print(f"Función encontrada en línea {i+1}")
            
            # Verificar siguiente línea
            if i+1 < len(lines):
                next_line = lines[i+1]
                if next_line.strip().startswith('"""'):
                    # Verificar indentación
                    if not next_line.startswith('        '):
                        print(f"❌ Problema de indentación en línea {i+2}")
                        print(f"   Actual: '{next_line.rstrip()}'")
                        
                        # Corregir todas las líneas de la función
                        j = i + 1
                        while j < len(lines):
                            if lines[j].strip() == '':
                                j += 1
                                continue
                            
                            # Si encontramos otra función, terminamos
                            if lines[j].strip().startswith('def ') and j > i:
                                break
                            
                            # Si la línea tiene contenido y no empieza con 'def'
                            if lines[j].strip():
                                # Asegurar que tiene 8 espacios (2 niveles de indentación)
                                stripped = lines[j].lstrip()
                                if not lines[j].startswith('    def '):
                                    lines[j] = '        ' + stripped
                            
                            j += 1
                        
                        print("✅ Indentación corregida")
            break
    
    # Guardar
    backup_path = Path("generators/pdf_generator_indent_backup.py")
    shutil.copy(pdf_path, backup_path)
    print(f"✅ Backup: {backup_path}")
    
    with open(pdf_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Archivo guardado")

def verify_syntax():
    """Verifica la sintaxis del archivo corregido"""
    print("\n🐍 VERIFICANDO SINTAXIS")
    print("-" * 60)
    
    pdf_path = Path("generators/pdf_generator.py")
    
    try:
        with open(pdf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, str(pdf_path), 'exec')
        print("✅ Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en línea {e.lineno}:")
        print(f"   {e.text}")
        print(f"   {' ' * (e.offset - 1)}^")
        return False
    except IndentationError as e:
        print(f"❌ Error de indentación en línea {e.lineno}:")
        print(f"   {e.text}")
        return False

def show_escape_function():
    """Muestra la función _escape_latex actual"""
    print("\n📝 FUNCIÓN _escape_latex ACTUAL:")
    print("-" * 60)
    
    pdf_path = Path("generators/pdf_generator.py")
    
    with open(pdf_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_function = False
    for i, line in enumerate(lines):
        if 'def _escape_latex' in line:
            in_function = True
            
        if in_function:
            print(f"{i+1:4}: {line.rstrip()}")
            
            # Si encontramos el return, mostramos unas líneas más y paramos
            if 'return text' in line and i > 410:  # Asegurar que es el return correcto
                for j in range(i+1, min(i+3, len(lines))):
                    print(f"{j+1:4}: {lines[j].rstrip()}")
                break

def restore_backup():
    """Restaura desde el backup si es necesario"""
    print("\n🔄 OPCIÓN DE RESTAURAR BACKUP")
    print("-" * 60)
    
    backups = list(Path("generators").glob("pdf_generator*backup*.py"))
    
    if backups:
        print("Backups disponibles:")
        for i, backup in enumerate(backups):
            print(f"{i+1}. {backup.name}")
        
        print("\nPara restaurar, ejecuta:")
        print(f"cp {backups[0]} generators/pdf_generator.py")

def main():
    # Intentar arreglar
    fix_indentation()
    
    # Verificar
    if verify_syntax():
        show_escape_function()
        print("\n✅ Archivo corregido")
        print("🚀 Ejecuta: python test_integration_v3.py")
    else:
        print("\n❌ Aún hay problemas")
        restore_backup()
        
        # Ofrecer alternativa
        print("\nALTERNATIVA: Usa la versión original del PDF Generator")
        print("que viene con el proyecto (sin V3.0) temporalmente:")
        print("1. cp generators/pdf_generator_backup.py generators/pdf_generator.py")
        print("2. O descarga la versión original de GitHub")

if __name__ == "__main__":
    main()