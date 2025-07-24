"""
Script de diagnóstico para verificar la configuración actual
"""

import os
import sys
from pathlib import Path

def check_pdf_generator_version():
    """Verifica qué versión del PDF Generator está instalada"""
    print("🔍 VERIFICANDO PDF GENERATOR...")
    print("-" * 50)
    
    pdf_gen_path = Path("generators/pdf_generator.py")
    
    if not pdf_gen_path.exists():
        print("❌ No se encuentra generators/pdf_generator.py")
        return False
    
    # Leer contenido
    with open(pdf_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si es V3.0 (usa templates reales) o versión antigua (usa PyLaTeX)
    if "RealTemplatePDFGenerator" in content:
        print("✅ PDF Generator V3.0 detectado (usa templates LaTeX reales)")
        return True
    elif "from pylatex import" in content:
        print("⚠️  PDF Generator antiguo detectado (usa PyLaTeX)")
        print("📝 Necesitas actualizar a V3.0 que usa templates reales")
        return False
    else:
        print("❓ Versión desconocida de PDF Generator")
        return False

def check_templates():
    """Verifica que existan los templates"""
    print("\n📄 VERIFICANDO TEMPLATES...")
    print("-" * 50)
    
    templates_dir = Path("templates")
    required_templates = [
        "guia_template.tex",
        "prueba_template.tex", 
        "tarea_template.tex"
    ]
    
    if not templates_dir.exists():
        print("❌ Directorio templates/ no existe")
        return False
    
    all_good = True
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            size = template_path.stat().st_size / 1024
            print(f"✅ {template} ({size:.1f} KB)")
        else:
            print(f"❌ {template} - FALTANTE")
            all_good = False
    
    return all_good

def check_database_methods():
    """Verifica métodos de DatabaseManager"""
    print("\n🗄️ VERIFICANDO DATABASE MANAGER...")
    print("-" * 50)
    
    try:
        # Importar sin ejecutar init
        import importlib.util
        spec = importlib.util.spec_from_file_location("db_manager", "database/db_manager.py")
        db_module = importlib.util.module_from_spec(spec)
        
        # Verificar que existe la clase
        if hasattr(db_module, 'DatabaseManager'):
            print("✅ Clase DatabaseManager encontrada")
            
            # Verificar métodos sin instanciar
            with open("database/db_manager.py", 'r', encoding='utf-8') as f:
                content = f.read()
                
            methods_to_check = [
                'obtener_estadisticas',
                'obtener_ejercicios',
                'agregar_ejercicio',
                'obtener_unidades_tematicas'
            ]
            
            for method in methods_to_check:
                if f"def {method}" in content:
                    print(f"✅ Método {method} encontrado")
                else:
                    print(f"❌ Método {method} NO encontrado")
                    
            return True
        else:
            print("❌ Clase DatabaseManager no encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando DatabaseManager: {e}")
        return False

def suggest_fix():
    """Sugiere cómo arreglar los problemas"""
    print("\n🔧 ACCIONES RECOMENDADAS:")
    print("=" * 50)
    
    # Verificar si tenemos el PDF Generator V3.0 correcto
    pdf_gen_path = Path("generators/pdf_generator.py")
    if pdf_gen_path.exists():
        with open(pdf_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "from pylatex import" in content:
            print("\n1. ACTUALIZAR PDF GENERATOR:")
            print("   El archivo actual usa PyLaTeX (versión antigua)")
            print("   Necesitas reemplazarlo con el PDF Generator V3.0 que adjuntaste")
            print("   que usa los templates LaTeX reales")
            print("\n   Comando:")
            print("   cp pdf_generator_v3.py generators/pdf_generator.py")
    
    print("\n2. VERIFICAR ESTRUCTURA DE ARCHIVOS:")
    print("   DB_Ejercicios/")
    print("   ├── generators/")
    print("   │   └── pdf_generator.py (V3.0 con RealTemplatePDFGenerator)")
    print("   ├── templates/")
    print("   │   ├── guia_template.tex")
    print("   │   ├── prueba_template.tex")
    print("   │   └── tarea_template.tex")
    print("   └── database/")
    print("       └── db_manager.py")
    
    print("\n3. CORREGIR ERROR DE ESCAPE:")
    print("   El error 'bad escape \\c' puede venir de la función _escape_latex()")
    print("   Ya está corregido en el PDF Generator V3.0 adjunto")

def main():
    """Ejecuta todos los chequeos"""
    print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN - DB_Ejercicios")
    print("=" * 50)
    print(f"📁 Directorio actual: {Path.cwd()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Ejecutar verificaciones
    pdf_ok = check_pdf_generator_version()
    templates_ok = check_templates()
    db_ok = check_database_methods()
    
    # Resumen
    print("\n📊 RESUMEN:")
    print("=" * 50)
    print(f"PDF Generator V3.0: {'✅ OK' if pdf_ok else '❌ ACTUALIZAR'}")
    print(f"Templates LaTeX:    {'✅ OK' if templates_ok else '❌ REVISAR'}")
    print(f"Database Manager:   {'✅ OK' if db_ok else '❌ REVISAR'}")
    
    if not (pdf_ok and templates_ok and db_ok):
        suggest_fix()
    else:
        print("\n✅ ¡Todo parece estar correctamente configurado!")
        print("🚀 Puedes ejecutar test_integration_v3.py")

if __name__ == "__main__":
    main()