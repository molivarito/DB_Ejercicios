"""
Test standalone del PDF Generator
Verifica que el generador de PDFs funcione correctamente antes de integrarlo con la GUI
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.append(str(Path(__file__).parent))

from generators.pdf_generator import ExercisePDFGenerator, create_sample_exercises
from datetime import datetime

def test_pdf_generation():
    """Test completo del generador de PDFs"""
    print("🧪 INICIANDO TESTS DEL PDF GENERATOR")
    print("=" * 50)
    
    # 1. Crear generador
    print("\n1️⃣ Creando generador...")
    try:
        generator = ExercisePDFGenerator("test_output")
        print("✅ Generador creado exitosamente")
        print(f"   📁 Directorio de salida: {generator.output_dir}")
    except Exception as e:
        print(f"❌ Error creando generador: {e}")
        return False
    
    # 2. Preparar datos de prueba
    print("\n2️⃣ Preparando datos de prueba...")
    
    # Información de la prueba
    exam_info = {
        'nombre': 'TEST - Interrogación 1 - Señales y Sistemas',
        'profesor': 'Patricio de la Cuadra',
        'semestre': '2024-2',
        'fecha': datetime.now().strftime("%d de %B, %Y"),
        'tiempo_total': 90,
        'instrucciones': [
            "Esta es una prueba del sistema de generación de PDFs.",
            "Verifique que todos los elementos se muestren correctamente.",
            "Los ejercicios son de ejemplo para testing."
        ]
    }
    
    # Ejercicios de prueba (usando los del generator + algunos adicionales)
    exercises = create_sample_exercises()
    
    # Agregar un ejercicio adicional más específico del curso
    exercises.append({
        'titulo': 'Transformada de Laplace',
        'enunciado': 'Determine la transformada de Laplace de la señal x(t) = e^(-2t)u(t) donde u(t) es la función escalón unitario.',
        'datos_entrada': 'x(t) = e^(-2t)u(t), donde a = 2',
        'tiempo_estimado': 15,
        'nivel_dificultad': 'Básico',
        'modalidad': 'Teórico',
        'solucion_completa': 'Aplicando la definición: X(s) = ∫₀^∞ e^(-2t)e^(-st)dt = 1/(s+2) para Re{s} > -2',
        'respuesta_final': 'X(s) = 1/(s+2), Re{s} > -2'
    })
    
    print(f"✅ Datos preparados:")
    print(f"   📋 {len(exercises)} ejercicios de prueba")
    print(f"   📄 Información del examen: {exam_info['nombre']}")
    
    # 3. Test: Generar LaTeX source
    print("\n3️⃣ Generando código LaTeX...")
    try:
        latex_path = generator.generate_latex_source(exercises, exam_info, "test_exam_source")
        print(f"✅ Código LaTeX generado: {latex_path}")
        
        # Verificar que el archivo existe
        if os.path.exists(latex_path):
            file_size = os.path.getsize(latex_path)
            print(f"   📊 Tamaño del archivo: {file_size} bytes")
        else:
            print("⚠️  Archivo LaTeX no encontrado")
            
    except Exception as e:
        print(f"❌ Error generando LaTeX: {e}")
        return False
    
    # 4. Test: Generar PDF completo
    print("\n4️⃣ Generando PDF completo...")
    try:
        # PDF sin soluciones
        pdf_result = generator.generate_exam_pdf(
            exercises, 
            exam_info, 
            include_solutions=False,
            filename="test_exam_complete"
        )
        
        # El resultado puede ser una tupla (pdf_path, solutions_path) o solo pdf_path
        if isinstance(pdf_result, tuple):
            pdf_path, solutions_path = pdf_result
            print(f"✅ PDF principal generado: {pdf_path}")
            print(f"✅ PDF con soluciones generado: {solutions_path}")
            
            # Verificar archivos
            for path in [pdf_path, solutions_path]:
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"   📊 {os.path.basename(path)}: {size} bytes")
                else:
                    print(f"⚠️  Archivo no encontrado: {path}")
        else:
            pdf_path = pdf_result
            print(f"✅ PDF generado: {pdf_path}")
            
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"   📊 Tamaño: {size} bytes")
                
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        print(f"   💡 Posibles causas:")
        print(f"      - LaTeX no está instalado")
        print(f"      - Faltan paquetes LaTeX necesarios")
        print(f"      - Problemas con caracteres especiales")
        return False
    
    # 5. Test: Generar guía de ejercicios
    print("\n5️⃣ Generando guía de ejercicios...")
    try:
        sheet_info = {
            'nombre': 'TEST - Guía de Ejercicios - Señales y Sistemas',
            'profesor': 'Patricio de la Cuadra',
            'semestre': '2024-2'
        }
        
        guide_path = generator.generate_exercise_sheet(
            exercises, 
            sheet_info,
            filename="test_exercise_guide"
        )
        
        print(f"✅ Guía generada: {guide_path}")
        
        if os.path.exists(guide_path):
            size = os.path.getsize(guide_path)
            print(f"   📊 Tamaño: {size} bytes")
            
    except Exception as e:
        print(f"❌ Error generando guía: {e}")
        return False
    
    # 6. Resumen final
    print("\n" + "=" * 50)
    print("🎉 RESUMEN DE TESTS")
    print("=" * 50)
    
    # Listar archivos generados
    output_dir = Path("test_output")
    if output_dir.exists():
        files = list(output_dir.glob("test_*"))
        print(f"📁 Archivos generados en {output_dir}:")
        for file in files:
            size = file.stat().st_size
            print(f"   📄 {file.name} ({size} bytes)")
        
        if len(files) >= 3:  # LaTeX + PDF + Guide mínimo
            print("✅ Todos los tests PASARON")
            print("🚀 PDF Generator está FUNCIONANDO correctamente")
            return True
        else:
            print("⚠️  Algunos archivos no se generaron")
            return False
    else:
        print("❌ Directorio de salida no creado")
        return False

def check_latex_installation():
    """Verifica si LaTeX está instalado y disponible"""
    print("\n🔍 VERIFICANDO INSTALACIÓN DE LATEX")
    print("-" * 40)
    
    import subprocess
    
    latex_commands = ['pdflatex', 'xelatex', 'lualatex']
    
    for cmd in latex_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                print(f"✅ {cmd} está disponible")
                # Mostrar primera línea de la versión
                first_line = result.stdout.split('\n')[0]
                print(f"   📋 {first_line}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            print(f"❌ {cmd} no encontrado")
    
    print("\n💡 SOLUCIÓN:")
    print("   Para instalar LaTeX:")
    print("   • macOS: brew install --cask mactex")
    print("   • Ubuntu: sudo apt-get install texlive-full")
    print("   • Windows: Instalar MiKTeX o TeX Live")
    
    return False

def main():
    """Función principal"""
    print("🚀 TEST STANDALONE - PDF GENERATOR")
    print("Proyecto: DB_Ejercicios")
    print("Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Verificar LaTeX primero
    if not check_latex_installation():
        print("\n⚠️  LaTeX no está disponible.")
        print("   Los PDFs no se podrán generar, pero el código LaTeX sí.")
        print("   ¿Continuar solo con generación de código LaTeX? (y/n)")
        
        # Para automatizar el test, asumimos que sí
        print("   Continuando con test limitado...")
    
    # Ejecutar tests
    success = test_pdf_generation()
    
    if success:
        print("\n🎉 CONCLUSIÓN: PDF Generator está LISTO para integración con GUI")
        print("💡 Próximo paso: Integrar con app.py")
    else:
        print("\n❌ CONCLUSIÓN: Hay problemas que resolver antes de integrar")
        print("💡 Revisa los errores arriba y corrígelos primero")
    
    return success

if __name__ == "__main__":
    main()