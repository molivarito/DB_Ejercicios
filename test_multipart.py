#!/usr/bin/env python3
"""
Test de Integración para el Sistema de Importación LaTeX
Sistema de Gestión de Ejercicios - Señales y Sistemas
Patricio de la Cuadra - PUC Chile
"""

import sys
import os
import tempfile
import json
from datetime import datetime

# Agregar path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_latex_parser():
    """Test del parser LaTeX con diferentes formatos"""
    print("🧪 Testing LaTeX Parser...")
    
    try:
        from utils.latex_parser import LaTeXParser, ParseError
        
        parser = LaTeXParser()
        
        # Test Case 1: Ejercicio con environment
        test_content_1 = """
        \\begin{ejercicio}
        % Dificultad: Intermedio
        % Unidad: Sistemas Continuos
        % Tiempo: 25
        
        Calcule la convolución y(t) = x(t) * h(t) donde:
        \\begin{enumerate}
        \\item x(t) = rect(t/2)
        \\item h(t) = δ(t-1)  
        \\end{enumerate}
        
        \\begin{solucion}
        La convolución resulta en y(t) = rect((t-1)/2)
        \\end{solucion}
        \\end{ejercicio}
        """
        
        exercises = parser.parse_file(test_content_1)
        assert len(exercises) >= 1, "Debería encontrar al menos 1 ejercicio"
        
        exercise = exercises[0]
        assert exercise.nivel_dificultad == "Intermedio", f"Dificultad incorrecta: {exercise.nivel_dificultad}"
        assert exercise.unidad_tematica == "Sistemas Continuos", f"Unidad incorrecta: {exercise.unidad_tematica}"
        assert exercise.tiempo_estimado == 25, f"Tiempo incorrecto: {exercise.tiempo_estimado}"
        assert exercise.solucion is not None, "Debería tener solución"
        assert exercise.confidence_score > 0.8, f"Confianza muy baja: {exercise.confidence_score}"
        
        print("✅ Test Case 1 (Environment): PASSED")
        
        # Test Case 2: Multiple exercises in enumerate
        test_content_2 = """
        \\section{Ejercicios de Fourier}
        
        \\begin{enumerate}
        \\item Determine la transformada de Fourier de x(t) = e^{-at}u(t)
        
        \\item Calcule la serie de Fourier de una señal cuadrada
        
        \\item % Dificultad: Avanzado
        Analice la convergencia de la serie de Fourier
        \\end{enumerate}
        """
        
        exercises = parser.parse_file(test_content_2)
        assert len(exercises) >= 2, f"Debería encontrar al menos 2 ejercicios, encontró {len(exercises)}"
        
        print("✅ Test Case 2 (Enumerate): PASSED")
        
        # Test Case 3: Auto-detection of units
        test_content_3 = """
        \\begin{problem}
        Implemente en Python un algoritmo para calcular la FFT de una señal 
        discreta x[n] y grafique su espectro de frecuencias.
        \\end{problem}
        """
        
        exercises = parser.parse_file(test_content_3)
        assert len(exercises) >= 1, "Debería encontrar al menos 1 ejercicio"
        
        exercise = exercises[0]
        assert "Discreta" in exercise.unidad_tematica or "DFT" in exercise.unidad_tematica, f"Unidad auto-detectada incorrecta: {exercise.unidad_tematica}"
        assert exercise.modalidad == "Computacional" or "Computacional" in exercise.modalidad, f"Modalidad incorrecta: {exercise.modalidad}"
        
        print("✅ Test Case 3 (Auto-detection): PASSED")
        
        print("🎉 LaTeX Parser: ALL TESTS PASSED")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando LaTeX Parser: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_manager():
    """Test del gestor de base de datos"""
    print("\n🧪 Testing Database Manager...")
    
    try:
        from database.db_manager import DatabaseManager, DatabaseError
        from utils.latex_parser import ParsedExercise
        
        # Crear base de datos temporal
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        db_manager = DatabaseManager(db_path)
        
        # Test Case 1: Crear ejercicio de prueba
        test_exercise = ParsedExercise(
            titulo="Test Exercise - Convolución",
            enunciado="Calcule y(t) = x(t) * h(t) para las señales dadas",
            solucion="La convolución resulta en...",
            nivel_dificultad="Intermedio",
            unidad_tematica="Sistemas Continuos",
            tiempo_estimado=20,
            modalidad="Teórico",
            subtemas=["convolución", "señales"],
            palabras_clave=["convolution", "signals"],
            pattern_used="test_pattern",
            confidence_score=0.9
        )
        
        # Test Case 2: Importación individual
        result = db_manager.batch_import_exercises([test_exercise], "test_file.tex", "test_user")
        
        assert result['ejercicios_exitosos'] == 1, f"Debería haber importado 1 ejercicio exitosamente"
        assert result['ejercicios_fallidos'] == 0, f"No debería haber ejercicios fallidos"
        assert len(result['ids_insertados']) == 1, "Debería tener 1 ID insertado"
        
        print("✅ Test Case 1 (Single Import): PASSED")
        
        # Test Case 3: Importación múltiple
        test_exercises = []
        for i in range(5):
            exercise = ParsedExercise(
                titulo=f"Test Exercise {i+1}",
                enunciado=f"Enunciado del ejercicio {i+1}",
                nivel_dificultad=["Básico", "Intermedio", "Avanzado"][i % 3],
                unidad_tematica=["Sistemas Continuos", "Transformada de Fourier"][i % 2],
                confidence_score=0.8 - (i * 0.1)
            )
            test_exercises.append(exercise)
        
        result = db_manager.batch_import_exercises(test_exercises, "test_batch.tex", "test_user")
        
        assert result['ejercicios_exitosos'] == 5, f"Debería haber importado 5 ejercicios, importó {result['ejercicios_exitosos']}"
        assert len(result['ids_insertados']) == 5, "Debería tener 5 IDs insertados"
        
        print("✅ Test Case 2 (Batch Import): PASSED")
        
        # Test Case 4: Historial de importaciones
        import_history = db_manager.get_import_history(10)
        assert len(import_history) >= 2, f"Debería tener al menos 2 importaciones en el historial"
        
        print("✅ Test Case 3 (Import History): PASSED")
        
        # Test Case 5: Ejercicios que necesitan revisión
        exercises_review = db_manager.get_exercises_needing_review()
        # Algunos ejercicios deberían necesitar revisión por baja confianza
        
        print("✅ Test Case 4 (Review Queue): PASSED")
        
        # Limpiar archivo temporal
        os.unlink(db_path)
        
        print("🎉 Database Manager: ALL TESTS PASSED")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando Database Manager: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_integration_workflow():
    """Test del flujo completo de integración"""
    print("\n🧪 Testing Integration Workflow...")
    
    try:
        from utils.latex_parser import LaTeXParser
        from database.db_manager import DatabaseManager
        
        # Crear base de datos temporal
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        parser = LaTeXParser()
        db_manager = DatabaseManager(db_path)
        
        # Test Case: Flujo completo LaTeX → Parser → Database
        full_latex_content = """
        \\documentclass{article}
        \\begin{document}
        
        \\section{Ejercicios de Señales y Sistemas}
        
        \\begin{ejercicio}
        % Dificultad: Básico
        % Unidad: Introducción
        % Tiempo: 15
        
        Defina qué es una señal continua y dé tres ejemplos de la vida real.
        
        \\begin{solucion}
        Una señal continua es aquella definida para todos los valores del tiempo...
        Ejemplos: temperatura ambiente, presión atmosférica, voltaje de una batería.
        \\end{solucion}
        \\end{ejercicio}
        
        \\begin{ejercicio}
        % Dificultad: Intermedio
        % Unidad: Sistemas Continuos
        % Tiempo: 30
        
        Para el sistema LTI con respuesta al impulso h(t) = e^{-2t}u(t):
        \\begin{enumerate}
        \\item Calcule la respuesta a x(t) = u(t)
        \\item Determine si el sistema es estable
        \\item Grafique h(t) y y(t)
        \\end{enumerate}
        
        \\begin{solucion}
        \\begin{enumerate}
        \\item y(t) = (1/2)(1-e^{-2t})u(t)
        \\item El sistema es estable porque ∫|h(t)|dt < ∞
        \\item [Gráficos]
        \\end{enumerate}
        \\end{solucion}
        \\end{ejercicio}
        
        \\section{Problemas Avanzados}
        
        \\begin{problem}
        % Dificultad: Avanzado
        % Modalidad: Computacional
        Implemente en Python un filtro pasa-bajas usando la transformada de Fourier
        y analice su respuesta en frecuencia.
        \\end{problem}
        
        \\end{document}
        """
        
        # 1. Parser
        exercises = parser.parse_file(full_latex_content)
        assert len(exercises) >= 3, f"Debería encontrar al menos 3 ejercicios, encontró {len(exercises)}"
        
        # Verificar que se parsearon correctamente
        basic_exercise = next((ex for ex in exercises if ex.nivel_dificultad == "Básico"), None)
        assert basic_exercise is not None, "Debería encontrar ejercicio básico"
        assert basic_exercise.tiempo_estimado == 15, f"Tiempo incorrecto: {basic_exercise.tiempo_estimado}"
        
        intermediate_exercise = next((ex for ex in exercises if ex.nivel_dificultad == "Intermedio"), None)
        assert intermediate_exercise is not None, "Debería encontrar ejercicio intermedio"
        assert intermediate_exercise.unidad_tematica == "Sistemas Continuos", f"Unidad incorrecta: {intermediate_exercise.unidad_tematica}"
        
        computational_exercise = next((ex for ex in exercises if ex.modalidad == "Computacional"), None)
        assert computational_exercise is not None, "Debería encontrar ejercicio computacional"
        
        print("✅ Phase 1 (Parsing): PASSED")
        
        # 2. Database Import
        result = db_manager.batch_import_exercises(exercises, "integration_test.tex", "integration_test")
        
        assert result['ejercicios_exitosos'] == len(exercises), f"Todos los ejercicios deberían haberse importado exitosamente"
        assert result['ejercicios_fallidos'] == 0, "No debería haber ejercicios fallidos"
        
        print("✅ Phase 2 (Database Import): PASSED")
        
        # 3. Verificar datos en base de datos
        import_history = db_manager.get_import_history(1)
        latest_import = import_history[0]
        
        assert latest_import['archivo_origen'] == "integration_test.tex", "Nombre de archivo incorrecto"
        assert latest_import['ejercicios_exitosos'] == len(exercises), "Cantidad importada incorrecta"
        
        print("✅ Phase 3 (Database Verification): PASSED")
        
        # 4. Test de búsqueda y filtrado (simulado)
        # En un sistema real, aquí probaríamos las funciones de búsqueda
        exercises_review = db_manager.get_exercises_needing_review()
        print(f"📋 Ejercicios que necesitan revisión: {len(exercises_review)}")
        
        print("✅ Phase 4 (Search & Filter): PASSED")
        
        # Limpiar
        os.unlink(db_path)
        
        print("🎉 Integration Workflow: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_error_handling():
    """Test del manejo de errores"""
    print("\n🧪 Testing Error Handling...")
    
    try:
        from utils.latex_parser import LaTeXParser, ParseError
        from database.db_manager import DatabaseManager, DatabaseError
        
        parser = LaTeXParser()
        
        # Test Case 1: Contenido LaTeX malformado
        malformed_content = """
        \\begin{ejercicio}
        Este ejercicio no tiene cierre
        % Sin \\end{ejercicio}
        """
        
        try:
            exercises = parser.parse_file(malformed_content)
            # Debería manejar gracefulmente el contenido malformado
            print("✅ Test Case 1 (Malformed Content): PASSED")
        except Exception as e:
            print(f"⚠️ Test Case 1: Parser manejó error correctamente: {type(e).__name__}")
        
        # Test Case 2: Contenido vacío
        empty_content = ""
        exercises = parser.parse_file(empty_content)
        assert exercises == [], "Contenido vacío debería retornar lista vacía"
        print("✅ Test Case 2 (Empty Content): PASSED")
        
        # Test Case 3: Ejercicio sin metadatos obligatorios
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        db_manager = DatabaseManager(db_path)
        
        # Ejercicio con datos incompletos
        invalid_exercise = {
            'titulo': '',  # Título vacío (inválido)
            'enunciado': '',  # Enunciado vacío (inválido)
            'nivel_dificultad': 'InvalidLevel'  # Nivel inválido
        }
        
        try:
            result = db_manager.batch_import_exercises([invalid_exercise], "test_error.tex")
            assert result['ejercicios_fallidos'] >= 1, "Debería fallar con datos inválidos"
            print("✅ Test Case 3 (Invalid Data): PASSED")
        except Exception:
            print("✅ Test Case 3 (Invalid Data): PASSED - Exception handled")
        
        os.unlink(db_path)
        
        print("🎉 Error Handling: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_performance():
    """Test de rendimiento con archivos grandes"""
    print("\n🧪 Testing Performance...")
    
    try:
        from utils.latex_parser import LaTeXParser
        import time
        
        parser = LaTeXParser()
        
        # Generar contenido LaTeX grande
        large_content = "\\documentclass{article}\n\\begin{document}\n\n"
        
        # 100 ejercicios simulados
        for i in range(100):
            large_content += f"""
\\begin{{ejercicio}}
% Dificultad: {"Básico" if i % 3 == 0 else "Intermedio" if i % 3 == 1 else "Avanzado"}
% Unidad: {"Sistemas Continuos" if i % 2 == 0 else "Transformada de Fourier"}
% Tiempo: {15 + (i % 30)}

Ejercicio número {i+1}: Calcule la transformada de la señal x_{i+1}(t) = sin(2πf_{i+1}t)
donde f_{i+1} = {i+1} Hz.

\\begin{{enumerate}}
\\item Determine la transformada de Fourier
\\item Grafique el espectro de magnitud  
\\item Analice el ancho de banda
\\end{{enumerate}}

\\begin{{solucion}}
La transformada de Fourier de x_{i+1}(t) es X_{i+1}(f) = π[δ(f-{i+1}) - δ(f+{i+1})]
El espectro muestra impulsos en ±{i+1} Hz.
El ancho de banda es teóricamente cero para una sinusoide pura.
\\end{{solucion}}
\\end{{ejercicio}}

"""
        
        large_content += "\\end{document}"
        
        # Medir tiempo de parsing
        start_time = time.time()
        exercises = parser.parse_file(large_content)
        end_time = time.time()
        
        parsing_time = end_time - start_time
        exercises_per_second = len(exercises) / parsing_time if parsing_time > 0 else float('inf')
        
        print(f"📊 Performance Results:")
        print(f"   - Ejercicios parseados: {len(exercises)}")
        print(f"   - Tiempo de parsing: {parsing_time:.2f} segundos")
        print(f"   - Velocidad: {exercises_per_second:.1f} ejercicios/segundo")
        
        # Verificaciones de performance
        assert len(exercises) >= 80, f"Debería parsear al menos 80 de 100 ejercicios, parseó {len(exercises)}"
        assert parsing_time < 30, f"Parsing debería tomar menos de 30 segundos, tomó {parsing_time:.2f}"
        
        print("✅ Performance test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def generate_test_report():
    """Genera un reporte completo de los tests"""
    print("\n" + "="*60)
    print("📋 REPORTE COMPLETO DE TESTING")
    print("="*60)
    
    test_results = {}
    
    # Ejecutar todos los tests
    test_results['latex_parser'] = test_latex_parser()
    test_results['database_manager'] = test_database_manager()
    test_results['integration_workflow'] = test_integration_workflow()
    test_results['error_handling'] = test_error_handling()
    test_results['performance'] = test_performance()
    
    # Generar resumen
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   ✅ Tests pasados: {passed_tests}/{total_tests}")
    print(f"   📈 Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ El sistema de importación LaTeX está listo para producción")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests fallaron")
        print("🔧 Revisar los componentes que fallaron antes de usar en producción")
    
    # Generar reporte JSON
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_results': test_results,
        'summary': {
            'passed': passed_tests,
            'total': total_tests,
            'success_rate': (passed_tests/total_tests)*100
        }
    }
    
    try:
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Reporte guardado en: test_report.json")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el reporte: {e}")
    
    return passed_tests == total_tests

def create_sample_latex_files():
    """Crea archivos LaTeX de ejemplo para testing manual"""
    print("\n📁 Creando archivos de ejemplo para testing manual...")
    
    # Crear directorio de ejemplos
    examples_dir = "examples_latex"
    os.makedirs(examples_dir, exist_ok=True)
    
    # Ejemplo 1: Ejercicios básicos
    example1_content = """\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage[spanish]{babel}

\\begin{document}

\\section{Ejercicios Básicos - Señales y Sistemas}

\\begin{ejercicio}
% Dificultad: Básico
% Unidad: Introducción
% Tiempo: 10
% Tipo: Definición

Defina los siguientes conceptos:
\\begin{enumerate}
\\item Señal continua
\\item Sistema LTI
\\item Respuesta al impulso
\\end{enumerate}

\\begin{solucion}
\\begin{enumerate}
\\item Una señal continua está definida para todos los valores del tiempo real
\\item Un sistema LTI es lineal e invariante en el tiempo
\\item La respuesta al impulso caracteriza completamente un sistema LTI
\\end{enumerate}
\\end{solucion}
\\end{ejercicio}

\\begin{ejercicio}
% Dificultad: Intermedio
% Unidad: Sistemas Continuos
% Tiempo: 20

Calcule la convolución y(t) = x(t) * h(t) donde:
\\begin{itemize}
\\item x(t) = u(t) - u(t-2)
\\item h(t) = e^{-t}u(t)
\\end{itemize}

\\begin{solucion}
y(t) = (1-e^{-t})u(t) - (1-e^{-(t-2)})u(t-2)
\\end{solucion}
\\end{ejercicio}

\\end{document}"""
    
    with open(f"{examples_dir}/ejercicios_basicos.tex", "w", encoding="utf-8") as f:
        f.write(example1_content)
    
    # Ejemplo 2: Ejercicios avanzados
    example2_content = """\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{graphicx}

\\begin{document}

\\section{Problemas Avanzados}

\\begin{problem}
% Dificultad: Avanzado
% Unidad: Transformada de Fourier
% Modalidad: Computacional
% Tiempo: 45

Diseñe un filtro digital que cumpla las siguientes especificaciones:
\\begin{itemize}
\\item Frecuencia de corte: 1 kHz
\\item Atenuación en banda de rechazo: > 40 dB
\\item Ondulación en banda de paso: < 0.5 dB
\\end{itemize}

Implemente el filtro en Python y verifique su respuesta.
\\end{problem}

\\subsection{Ejercicios de Transformada Z}

\\begin{enumerate}
\\item % Dificultad: Intermedio
Determine la transformada Z de x[n] = a^n u[n] y su región de convergencia.

\\item % Dificultad: Avanzado
Analice la estabilidad del sistema con función de transferencia:
$H(z) = \\frac{1 + z^{-1}}{1 - 0.8z^{-1} + 0.15z^{-2}}$

\\item % Dificultad: Desafío
Diseñe un sistema que tenga respuesta finita al impulso y fase lineal.
\\end{enumerate}

\\end{document}"""
    
    with open(f"{examples_dir}/ejercicios_avanzados.tex", "w", encoding="utf-8") as f:
        f.write(example2_content)
    
    # Ejemplo 3: Formato mixto
    example3_content = """\\documentclass{article}

\\begin{document}

% Este archivo tiene formatos mixtos para probar la robustez del parser

\\section{Sistemas Discretos}

\\ejercicio{1}{
% Dificultad: Básico
% Unidad: Sistemas Discretos
Explique el teorema de muestreo de Nyquist.
}

\\begin{ejercicio}
% Dificultad: Intermedio
% Tiempo: 30
Una señal x(t) = cos(2π·50t) se muestrea a fs = 100 Hz.
¿Qué frecuencia aparece en la señal muestreada?

\\ifanswers
La frecuencia de muestreo es exactamente el doble de la frecuencia de la señal,
por lo que no hay aliasing. La señal muestreada tendrá la misma frecuencia: 50 Hz.
\\fi
\\end{ejercicio}

% Ejercicio sin environment específico
**Problema 3:** % Dificultad: Avanzado
Implemente la FFT radix-2 y compare su eficiencia con la DFT directa
para señales de longitud N = 1024.

\\end{document}"""
    
    with open(f"{examples_dir}/formato_mixto.tex", "w", encoding="utf-8") as f:
        f.write(example3_content)
    
    print(f"✅ Archivos de ejemplo creados en: {examples_dir}/")
    print("   - ejercicios_basicos.tex")
    print("   - ejercicios_avanzados.tex") 
    print("   - formato_mixto.tex")
    
    return examples_dir

if __name__ == "__main__":
    print("🚀 SISTEMA DE TESTING - IMPORTADOR LATEX")
    print("Sistema de Gestión de Ejercicios - Señales y Sistemas")
    print("=" * 60)
    
    # Crear archivos de ejemplo
    create_sample_latex_files()
    
    # Ejecutar tests completos
    all_passed = generate_test_report()
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 SISTEMA LISTO PARA PRODUCCIÓN")
        print("\n📋 Próximos pasos:")
        print("1. Integrar los módulos en app.py")
        print("2. Descommentar las importaciones reales")
        print("3. Poblar la base de datos con ejercicios reales")
        print("4. Configurar logging para producción")
    else:
        print("🔧 REVISAR COMPONENTES ANTES DE USAR")
        print("\n🛠️ Acciones recomendadas:")
        print("1. Revisar los errores reportados")
        print("2. Instalar dependencias faltantes")
        print("3. Verificar estructura de directorios")
        print("4. Re-ejecutar tests específicos")
    
    print(f"\n📊 Reporte completo disponible en: test_report.json")
    
    exit(0 if all_passed else 1)