#!/usr/bin/env python3
"""
Script de prueba para el parser LaTeX
Permite probar el importador sin usar Streamlit
"""

import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.latex_parser import LaTeXExerciseParser

def test_with_sample_content():
    """Prueba el parser con contenido de ejemplo"""
    
    # Contenido LaTeX de ejemplo
    sample_latex = """
    \\documentclass{article}
    \\usepackage[utf8]{inputenc}
    
    \\begin{document}
    
    \\section{Ejercicios de Sistemas Continuos}
    
    \\begin{ejercicio}
    % Dificultad: Intermedio
    % Unidad: Sistemas Continuos
    % Tiempo: 25
    
    Calcule la convolución $y(t) = x(t) * h(t)$ donde:
    \\begin{itemize}
        \\item $x(t) = \\text{rect}(t/2)$
        \\item $h(t) = \\delta(t-1) + \\delta(t+1)$
    \\end{itemize}
    
    \\begin{solucion}
    La convolución se calcula como:
    $y(t) = \\text{rect}((t-1)/2) + \\text{rect}((t+1)/2)$
    \\end{solucion}
    \\end{ejercicio}
    
    \\begin{ejercicio}
    % Dificultad: Avanzado
    % Unidad: Transformada de Fourier
    
    Determine la transformada de Fourier de la señal $x(t) = e^{-at}u(t)$ donde $a > 0$.
    
    \\textbf{Sugerencia:} Use la definición de la transformada de Fourier.
    \\end{ejercicio}
    
    \\section{Ejercicios Adicionales}
    
    \\item Calcule la respuesta al impulso del sistema descrito por la ecuación diferencial:
    $\\frac{dy(t)}{dt} + 2y(t) = x(t)$
    
    \\end{document}
    """
    
    print("🧪 Probando parser LaTeX...")
    print("=" * 50)
    
    # Crear parser
    parser = LaTeXExerciseParser()
    
    # Parsear contenido
    exercises = parser.parse_content(sample_latex, "test_content.tex")
    
    print(f"✅ Ejercicios encontrados: {len(exercises)}")
    print()
    
    # Mostrar resultados
    for i, exercise in enumerate(exercises, 1):
        print(f"📝 Ejercicio {i}:")
        print(f"   Título: {exercise.get('titulo', 'Sin título')}")
        print(f"   Dificultad: {exercise.get('nivel_dificultad', 'No especificada')}")
        print(f"   Unidad: {exercise.get('unidad_tematica', 'No especificada')}")
        print(f"   Tiempo: {exercise.get('tiempo_estimado', 'No especificado')} min")
        print(f"   Patrón usado: {exercise.get('pattern_used', 'No especificado')}")
        print(f"   Enunciado: {exercise.get('enunciado', 'Sin enunciado')[:100]}...")
        
        if exercise.get('solucion_completa'):
            print(f"   ✅ Solución encontrada: {exercise['solucion_completa'][:50]}...")
        
        print()

def test_with_different_patterns():
    """Prueba diferentes patrones de ejercicios"""
    
    patterns_to_test = [
        # Patrón 1: environment ejercicio
        {
            'name': 'Environment ejercicio',
            'content': """
            \\begin{ejercicio}
            Calcule la integral de la función f(x) = x^2.
            \\end{ejercicio}
            """
        },
        
        # Patrón 2: items numerados
        {
            'name': 'Items numerados',
            'content': """
            \\begin{enumerate}
            \\item Demuestre que la función es par.
            \\item Calcule la transformada de Laplace.
            \\item Determine la estabilidad del sistema.
            \\end{enumerate}
            """
        },
        
        # Patrón 3: secciones
        {
            'name': 'Secciones',
            'content': """
            \\section{Problema 1}
            Analice la respuesta en frecuencia del filtro pasa-bajos.
            
            \\section{Problema 2}  
            Calcule la DFT de la secuencia x[n] = {1, 2, 3, 4}.
            """
        },
        
        # Patrón 4: contenido sin estructura clara
        {
            'name': 'Sin estructura',
            'content': """
            Ejercicio sobre convolución:
            
            Calcule y(t) = x(t) * h(t) donde x(t) es una señal rectangular
            y h(t) es un impulso desplazado.
            
            Otro problema:
            
            Determine la transformada Z de la secuencia x[n] = a^n u[n].
            """
        }
    ]
    
    parser = LaTeXExerciseParser()
    
    print("🔍 Probando diferentes patrones...")
    print("=" * 50)
    
    for pattern_test in patterns_to_test:
        print(f"\n📋 Probando: {pattern_test['name']}")
        print("-" * 30)
        
        exercises = parser.parse_content(pattern_test['content'], f"test_{pattern_test['name']}")
        
        print(f"Ejercicios encontrados: {len(exercises)}")
        
        for i, ex in enumerate(exercises, 1):
            print(f"  {i}. {ex.get('titulo', 'Sin título')} "
                  f"(patrón: {ex.get('pattern_used', 'unknown')})")
            print(f"     Contenido: {ex.get('enunciado', '')[:80]}...")

def test_metadata_extraction():
    """Prueba específica para extracción de metadatos"""
    
    metadata_samples = [
        """
        \\begin{ejercicio}
        % Dificultad: Básico
        % Unidad: Sistemas Continuos
        % Tiempo: 15
        Ejercicio simple de convolución.
        \\end{ejercicio}
        """,
        
        """
        \\begin{problem}
        % Nivel: Avanzado
        % Tema: Transformada de Fourier
        Problema complejo de análisis espectral.
        \\end{problem}
        """,
        
        """
        % Dificultad: Intermedio
        Calcule la respuesta en frecuencia del sistema.
        """
    ]
    
    parser = LaTeXExerciseParser()
    
    print("🏷️  Probando extracción de metadatos...")
    print("=" * 50)
    
    for i, sample in enumerate(metadata_samples, 1):
        print(f"\n🧪 Muestra {i}:")
        exercises = parser.parse_content(sample, f"metadata_test_{i}")
        
        if exercises:
            ex = exercises[0]
            print(f"   Dificultad detectada: {ex.get('nivel_dificultad', 'No detectada')}")
            print(f"   Unidad detectada: {ex.get('unidad_tematica', 'No detectada')}")
            print(f"   Tiempo detectado: {ex.get('tiempo_estimado', 'No detectado')}")
        else:
            print("   ❌ No se detectaron ejercicios")

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas del parser LaTeX")
    print("=" * 60)
    
    # Test 1: Contenido de ejemplo completo
    test_with_sample_content()
    
    input("\nPresiona Enter para continuar con las pruebas de patrones...")
    
    # Test 2: Diferentes patrones
    test_with_different_patterns()
    
    input("\nPresiona Enter para continuar con las pruebas de metadatos...")
    
    # Test 3: Extracción de metadatos
    test_metadata_extraction()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas!")
    print("\n💡 Para usar en Streamlit:")
    print("   streamlit run app.py")
    print("   Ir a 'Importar LaTeX' y probar con tus archivos")

if __name__ == "__main__":
    main()