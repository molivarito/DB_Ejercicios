#!/usr/bin/env python3
"""
Test simplificado para el parser LaTeX - específico para formato de Patricio
"""

import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.latex_parser import LaTeXExerciseParser

def test_patricio_format():
    """Prueba específica con el formato de Patricio"""
    print("🧪 Probando parser con formato de Patricio...")
    print("=" * 50)
    
    # Contenido de ejemplo basado en el archivo real
    patricio_sample = """
    \\subsection*{Números complejos}

    \\begin{enumerate}

        \\item Se tiene el número complejo $2z = 1 +i\\sqrt{3}$ y $2w = \\sqrt{2}-i\\sqrt{2}$ ahora calcule usando la forma polar:
        \\begin{enumerate}
            \\item $z\\cdot w$
            \\item $z/w$
        \\end{enumerate}
        \\ifanswers
        {\\color{red} \\textbf{Solución:} \\textit{Resuelta en ayudantía}}
        \\fi
        
        \\item Demuestre que para todo $z \\in \\mathbb{C}$ se cumple que:
        \\ifanswers
        {\\color{red}\\textbf{Solución:} 
        Tomamos un complejo cualquiera $z = \\sigma + j \\omega$
        }
        \\fi

    \\end{enumerate}

    \\subsection*{Señales y Sistemas}

    \\begin{enumerate}

        \\item Considere las señales de entrada y determine la salida del sistema.
        
        \\ifanswers
        {\\color{red} \\textbf{Solución:}
        Las señales se pueden descomponer como exponenciales complejas...
        }
        \\fi

        \\item Determine si el sistema es causal y estable.

        \\ifanswers
        {\\color{red} \\textbf{Solución:}
        El sistema es causal porque... y estable porque...
        }
        \\fi

    \\end{enumerate}

    \\subsection*{Sistemas Lineales y Convolución}

    \\begin{enumerate}

        \\item Calcule la convolución de las siguientes señales:
        $$h(t) = e^{-2t}u(t)$$
        $$x(t) = \\delta(t-1)$$

        \\ifanswers
        {\\color{red} \\textbf{Solución:}
        La convolución resulta en $y(t) = e^{-2(t-1)}u(t-1)$
        }
        \\fi

    \\end{enumerate}
    """
    
    # Crear parser
    parser = LaTeXExerciseParser()
    
    # Parsear contenido
    try:
        exercises = parser.parse_content(patricio_sample, "guia_patricio_test.tex")
        
        print(f"✅ Ejercicios encontrados: {len(exercises)}")
        print()
        
        # Mostrar cada ejercicio
        for i, exercise in enumerate(exercises, 1):
            print(f"📝 Ejercicio {i}:")
            print(f"   📍 Título: {exercise.get('titulo', 'Sin título')}")
            print(f"   🎯 Unidad: {exercise.get('unidad_tematica', 'No especificada')}")
            print(f"   📊 Dificultad: {exercise.get('nivel_dificultad', 'No especificada')}")
            print(f"   💻 Modalidad: {exercise.get('modalidad', 'No especificada')}")
            print(f"   ⏱️  Tiempo: {exercise.get('tiempo_estimado', 'No especificado')} min")
            print(f"   🔧 Patrón: {exercise.get('pattern_used', 'No especificado')}")
            
            # Mostrar enunciado (primeros 150 caracteres)
            enunciado = exercise.get('enunciado', 'Sin enunciado')
            print(f"   📄 Enunciado: {enunciado[:150]}{'...' if len(enunciado) > 150 else ''}")
            
            # Verificar si tiene solución
            solucion = exercise.get('solucion_completa', '')
            if solucion:
                print(f"   ✅ Solución: {solucion[:100]}{'...' if len(solucion) > 100 else ''}")
            else:
                print(f"   ❌ Sin solución detectada")
            
            # Palabras clave
            keywords = exercise.get('palabras_clave', [])
            if keywords:
                print(f"   🏷️  Keywords: {', '.join(keywords)}")
            
            print("-" * 50)
        
        # Estadísticas rápidas
        if exercises:
            print("📊 Estadísticas:")
            
            # Por unidad
            unidades = {}
            for ex in exercises:
                unidad = ex.get('unidad_tematica', 'Sin clasificar')
                unidades[unidad] = unidades.get(unidad, 0) + 1
            
            print("   Por unidad temática:")
            for unidad, count in unidades.items():
                print(f"     • {unidad}: {count}")
            
            # Por dificultad  
            dificultades = {}
            for ex in exercises:
                dif = ex.get('nivel_dificultad', 'Sin clasificar')
                dificultades[dif] = dificultades.get(dif, 0) + 1
            
            print("   Por dificultad:")
            for dif, count in dificultades.items():
                print(f"     • {dif}: {count}")
            
            # Promedio de tiempo
            tiempos = [ex.get('tiempo_estimado', 0) for ex in exercises if ex.get('tiempo_estimado')]
            if tiempos:
                promedio = sum(tiempos) / len(tiempos)
                print(f"   Tiempo promedio: {promedio:.1f} minutos")
    
    except Exception as e:
        print(f"❌ Error durante el parseo: {str(e)}")
        import traceback
        traceback.print_exc()

def test_with_real_file():
    """Test con archivo real si está disponible"""
    print("\\n🧪 Buscando archivo LaTeX real...")
    
    # Buscar archivos .tex en el directorio actual
    tex_files = []
    for file in os.listdir('.'):
        if file.endswith('.tex'):
            tex_files.append(file)
    
    if tex_files:
        print(f"📁 Archivos .tex encontrados: {', '.join(tex_files)}")
        
        # Usar el primer archivo encontrado
        filename = tex_files[0]
        print(f"📖 Probando con: {filename}")
        
        try:
            parser = LaTeXExerciseParser()
            exercises = parser.parse_file(filename)
            
            print(f"✅ Resultado: {len(exercises)} ejercicios extraídos de {filename}")
            
            # Mostrar solo los primeros 3 para no saturar
            for i, ex in enumerate(exercises[:3], 1):
                print(f"  {i}. {ex.get('titulo', 'Sin título')} [{ex.get('unidad_tematica', 'Sin unidad')}]")
            
            if len(exercises) > 3:
                print(f"  ... y {len(exercises) - 3} ejercicios más")
                
        except Exception as e:
            print(f"❌ Error leyendo {filename}: {str(e)}")
    else:
        print("❌ No se encontraron archivos .tex en el directorio actual")

def test_with_document_content():
    """Test usando el contenido real del documento de Patricio"""
    print("\n🧪 Probando con fragmento del documento real...")
    print("=" * 50)
    
    # Fragmento real del documento que subiste
    real_content = """
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
        
        Tomamos un complejo cualquiera $z = \\sigma + j \\omega$\\\\
        $z + z^* = \\sigma + j\\omega + \\sigma -j\\omega = 2\\sigma $
        $\\frac{z + z^*}{2} = \\sigma$
        Similarmente:
        $z-z^* = \\sigma +j\\omega - \\sigma + j\\omega = 2j\\omega$
        $\\frac{z - z^*}{2} = j \\omega$}
        \\fi

    \\end{enumerate}

    \\subsection*{Señales y Sistemas}

    \\begin{enumerate}

        \\item Considere las señales de entrada
        \\begin{align*}
            x(t) &= \\cos\\left(\\frac{2\\pi t}{3}\\right) + 2 \\sin\\left(\\frac{16 \\pi t}{3}\\right) \\\\
            y(t) &= \\sin(\\pi t)
        \\end{align*}
            El sistema se modela por la relación $z(t)=x(t)y(t)$, donde $z(t)$ es la señal salida.
      

        \\ifanswers
        {\\color{red}  \\textbf{Solución:}

        Las señales $x(t)$ e $y(t)$ se pueden descomponer como una suma de exponenciales complejas, lo que lleva a
        \\begin{align*}
            x(t) &= \\frac{1}{2} e^{j(2\\pi t/3)} + \\frac{1}{2} e^{-2\\pi t/3}+\\frac{e^{16\\pi t/3}}{j}-\\frac{e^{-16\\pi t /3}}{j}
        \\end{align*}}
        \\fi

    \\end{enumerate}
    """
    
    # Crear parser
    parser = LaTeXExerciseParser()
    
    try:
        exercises = parser.parse_content(real_content, "documento_real.tex")
        
        print(f"✅ Ejercicios encontrados: {len(exercises)}")
        print()
        
        # Mostrar cada ejercicio con más detalle
        for i, exercise in enumerate(exercises, 1):
            print(f"📝 EJERCICIO {i}:")
            print(f"   📍 Título: {exercise.get('titulo', 'Sin título')}")
            print(f"   🎯 Unidad: {exercise.get('unidad_tematica', 'No clasificada')}")
            print(f"   📊 Dificultad: {exercise.get('nivel_dificultad', 'No especificada')}")
            print(f"   💻 Modalidad: {exercise.get('modalidad', 'No especificada')}")
            print(f"   ⏱️  Tiempo: {exercise.get('tiempo_estimado', 0)} min")
            print(f"   🔧 Patrón: {exercise.get('pattern_used', 'No especificado')}")
            
            # Enunciado limpio
            enunciado = exercise.get('enunciado', 'Sin enunciado')
            print(f"   📄 ENUNCIADO:")
            print(f"      {enunciado[:200]}{'...' if len(enunciado) > 200 else ''}")
            
            # Solución 
            solucion = exercise.get('solucion_completa', '')
            if solucion and solucion.strip():
                print(f"   ✅ SOLUCIÓN DETECTADA:")
                print(f"      {solucion[:150]}{'...' if len(solucion) > 150 else ''}")
            else:
                print(f"   ❌ SIN SOLUCIÓN DETECTADA")
                # Debug: mostrar contenido raw para ver qué pasa
                raw = exercise.get('raw_content', '')
                if '\\ifanswers' in raw:
                    print(f"   🔍 DEBUG: Se detectó \\ifanswers en el contenido raw")
                    # Mostrar la parte de ifanswers
                    import re
                    ifanswers_match = re.search(r'\\ifanswers.*?\\fi', raw, re.DOTALL)
                    if ifanswers_match:
                        print(f"      Contenido ifanswers: {ifanswers_match.group(0)[:100]}...")
            
            # Palabras clave
            keywords = exercise.get('palabras_clave', [])
            if keywords:
                print(f"   🏷️  Keywords: {', '.join(keywords)}")
            
            print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error durante el parseo: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    print("🚀 Test Mejorado del Parser LaTeX")
    print("🎓 Especializado para formato de Patricio de la Cuadra - PUC")  
    print("=" * 60)
    
    # Test principal con contenido de ejemplo
    test_patricio_format()
    
    # Test con contenido real del documento
    test_with_document_content()
    
    # Test con archivo real si existe
    test_with_real_file()
    
    print("\n" + "=" * 60)
    print("✅ Tests completados!")
    print("\n💡 Análisis:")
    print("   - Si ve 'SIN SOLUCIÓN DETECTADA', necesitamos ajustar los patrones regex")
    print("   - Si las unidades son 'Por determinar', mejoraremos el mapeo")
    print("   - Si todo se ve bien, procedemos con Streamlit")
    print("\n🔧 Para usar:")
    print("   streamlit run app.py → 'Importar LaTeX' → subir archivo completo")

if __name__ == "__main__":
    main()