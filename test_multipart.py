#!/usr/bin/env python3
"""
Test específico para ejercicios con múltiples partes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from latex_parser import LaTeXExerciseParser

def test_multipart_exercise():
    """Test con ejercicio que tiene múltiples partes"""
    print("🧪 Probando ejercicio con múltiples partes...")
    print("=" * 50)
    
    # Ejemplo basado en tu documento - ejercicio con subpartes
    multipart_content = """
    \\subsection*{Números complejos}

    \\begin{enumerate}

        \\item Se tiene el número complejo $2z = 1 +i\\sqrt{3}$ y $2w = \\sqrt{2}-i\\sqrt{2}$ ahora calcule usando la forma polar:
        \\begin{enumerate}
            \\item $z\\cdot w$
            \\item $z/w$
            \\item $zz^{*},\\frac{1}{2} (z + z^{*}), \\frac{1}{2i} (z - z^{*})$
            \\item Magnitud y fase de $(z\\cdot w)^{*}$
        \\end{enumerate}
        \\ifanswers
        {\\color{red} \\textbf{Solución:} \\textit{Resuelta en ayudantía}}
        \\fi
        
        \\item Demuestre que para todo $z \\in \\mathbb{C}$  se cumple que:
        \\begin{itemize}
            \\item $\\Re{\\{z\\}} = \\frac{z + z^*}{2}$
            \\item $j\\Im{\\{z\\}}  = \\frac{z-z^*}{2}$
        \\end{itemize}

        \\ifanswers
        {\\color{red}\\textbf{Solución:} 
        Tomamos un complejo cualquiera $z = \\sigma + j \\omega$
        $$z + z^* = \\sigma + j\\omega + \\sigma -j\\omega = 2\\sigma $$
        }
        \\fi

        \\item Considere la señal $x(t) = \\sqrt{2}(1+j)e^{j\\pi/4}e^{(-1+j 2\\pi)t} $. Determine:
        \\begin{enumerate}
            \\item $\\Re\\{x(t)\\}$
            \\item $\\Im\\{x(t)\\}$ 
            \\item $x(t+2)+x^{*}(t+2)$
        \\end{enumerate}

        \\ifanswers
        {\\color{red}\\textbf{Solución:}
        Primero, puede ser conveniente desarrollar $x(t)$ en su forma polar...
        }
        \\fi

    \\end{enumerate}
    """
    
    # Crear parser
    parser = LaTeXExerciseParser()
    
    try:
        exercises = parser.parse_content(multipart_content, "test_multipart.tex")
        
        print(f"✅ Ejercicios encontrados: {len(exercises)}")
        print()
        
        expected_count = 3  # Deberíamos tener 3 ejercicios, no más
        
        if len(exercises) == expected_count:
            print("🎯 ¡Perfecto! Se detectaron exactamente 3 ejercicios como esperado")
        else:
            print(f"⚠️  Se esperaban {expected_count} ejercicios, pero se encontraron {len(exercises)}")
        
        print()
        
        # Analizar cada ejercicio
        for i, exercise in enumerate(exercises, 1):
            print(f"📝 EJERCICIO {i}:")
            print(f"   📍 Título: {exercise.get('titulo', 'Sin título')}")
            
            # Mostrar enunciado y verificar si contiene subpartes
            enunciado = exercise.get('enunciado', '')
            print(f"   📄 Enunciado (primeros 150 chars): {enunciado[:150]}...")
            
            # Verificar si contiene estructura de subpreguntas
            has_subenumerate = '\\begin{enumerate}' in enunciado or '\\begin{itemize}' in enunciado
            subitem_count = enunciado.count('\\item')
            
            if has_subenumerate:
                print(f"   ✅ Contiene subpreguntas: {subitem_count} subitems detectados")
            else:
                print(f"   ℹ️  Sin subpreguntas detectadas")
            
            # Verificar solución
            solucion = exercise.get('solucion_completa', '')
            if solucion:
                print(f"   ✅ Solución: {solucion[:100]}...")
            else:
                print(f"   ❌ Sin solución")
            
            print(f"   🎯 Unidad: {exercise.get('unidad_tematica', 'No clasificada')}")
            print("-" * 50)
        
        # Análisis de calidad
        print("📊 ANÁLISIS DE CALIDAD:")
        
        # ¿Preservó las subpreguntas?
        subpreguntas_preservadas = sum(1 for ex in exercises 
                                     if ('\\begin{enumerate}' in ex.get('enunciado', '') or 
                                         '\\begin{itemize}' in ex.get('enunciado', '')))
        
        print(f"   • Ejercicios con subpreguntas preservadas: {subpreguntas_preservadas}")
        
        # ¿Tienen soluciones?
        con_solucion = sum(1 for ex in exercises if ex.get('solucion_completa'))
        print(f"   • Ejercicios con solución: {con_solucion}/{len(exercises)}")
        
        # ¿Clasificación correcta?
        bien_clasificados = sum(1 for ex in exercises 
                              if ex.get('unidad_tematica') != 'Por determinar')
        print(f"   • Ejercicios bien clasificados: {bien_clasificados}/{len(exercises)}")
        
        if len(exercises) == 3 and con_solucion == 3 and subpreguntas_preservadas >= 2:
            print("\n🎉 ¡ÉXITO! El parser maneja correctamente ejercicios con subpartes")
        else:
            print("\n🔧 Necesita ajustes en el parser")
        
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()

def test_mixed_exercises():
    """Test con mezcla de ejercicios simples y con subpartes"""
    print("\n🧪 Probando mezcla de ejercicios simples y complejos...")
    print("=" * 50)
    
    mixed_content = """
    \\subsection*{Señales y Sistemas}

    \\begin{enumerate}

        \\item Determine si el sistema es lineal y causal.

        \\ifanswers
        {\\color{red} \\textbf{Solución:} El sistema es lineal porque... y causal porque...}
        \\fi
        
        \\item Sea la señal $x(t) = \\cos{(\\omega_x(t+\\tau_x)+\\theta_x)}$:
        \\begin{enumerate}
            \\item Determine la frecuencia en Hz y el período de $x(t)$
            \\item Evalúe casos específicos con diferentes parámetros
        \\end{enumerate}
        \\ifanswers
        {\\color{red} \\textbf{Solución:} La frecuencia se calcula como...}
        \\fi

        \\item Calcule la convolución de $h(t) = e^{-2t}u(t)$ y $x(t) = \\delta(t-1)$.

        \\ifanswers
        {\\color{red} \\textbf{Solución:} La convolución resulta en...}
        \\fi

    \\end{enumerate}
    """
    
    parser = LaTeXExerciseParser()
    exercises = parser.parse_content(mixed_content, "test_mixed.tex")
    
    print(f"✅ Ejercicios encontrados: {len(exercises)}")
    
    # Clasificar por tipo
    simples = [ex for ex in exercises if '\\begin{enumerate}' not in ex.get('enunciado', '')]
    complejos = [ex for ex in exercises if '\\begin{enumerate}' in ex.get('enunciado', '')]
    
    print(f"   • Ejercicios simples: {len(simples)}")
    print(f"   • Ejercicios con subpartes: {len(complejos)}")
    
    if len(exercises) == 3:
        print("🎯 ¡Correcto! Se mantiene la estructura esperada")
    else:
        print("⚠️  La cantidad no coincide con lo esperado")

def main():
    """Función principal"""
    print("🚀 Test de Ejercicios con Múltiples Partes")
    print("🎓 Verificando que no se dividan incorrectamente")
    print("=" * 60)
    
    test_multipart_exercise()
    test_mixed_exercises()
    
    print("\n" + "=" * 60)
    print("✅ Tests completados!")
    print("\n💡 Si todo funciona bien:")
    print("   1. streamlit run app_simple.py")
    print("   2. Sube tu archivo completo")
    print("   3. Verifica que ejercicios con subpartes no se dividan")

if __name__ == "__main__":
    main()