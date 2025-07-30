#!/usr/bin/env python3
"""
Script de Testing MEJORADO para LaTeX Parser V4.0
Permite debuggear el parser sin Streamlit con análisis detallado

Uso:
python test_parser_improved.py main.tex
python test_parser_improved.py sample
python test_parser_improved.py debug_specific
"""

import sys
import os
import traceback
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent))

def test_parser_with_file(file_path: str):
    """Test del parser con archivo LaTeX real"""
    
    print("🧪 INICIANDO TEST COMPLETO DEL PARSER V4.0")
    print("=" * 60)
    
    # 1. Verificar archivo existe
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    print(f"📄 Archivo: {file_path}")
    print(f"📏 Tamaño: {os.path.getsize(file_path)} bytes")
    
    # 2. Leer archivo
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Archivo leído correctamente ({len(content)} caracteres)")
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    # 3. Análisis preliminar del contenido
    print("\n📊 ANÁLISIS PRELIMINAR DEL CONTENIDO:")
    print("-" * 50)
    
    # Contar subsecciones
    import re
    subsections = re.findall(r'\\subsection\*\{([^}]+)\}', content)
    print(f"📂 Subsecciones encontradas: {len(subsections)}")
    for i, title in enumerate(subsections, 1):
        print(f"   {i}. {title}")
    
    # Contar bloques enumerate
    enumerate_blocks = re.findall(r'\\begin\{enumerate\}.*?\\end\{enumerate\}', content, re.DOTALL)
    print(f"📋 Bloques enumerate: {len(enumerate_blocks)}")
    
    # Contar items totales
    all_items = re.findall(r'\\item\s+', content)
    print(f"📝 Total \\item encontrados: {len(all_items)}")
    
    # Contar soluciones
    solutions = re.findall(r'\\ifanswers.*?\\fi', content, re.DOTALL)
    print(f"💡 Bloques de solución \\ifanswers: {len(solutions)}")
    
    # 4. Importar y testear parser
    try:
        from utils.latex_parser import LaTeXParser
        print("\n✅ Parser V4.0 importado correctamente")
    except Exception as e:
        print(f"\n❌ Error importando parser: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False
    
    # 5. Crear instancia y ejecutar parsing
    try:
        parser = LaTeXParser()
        print("✅ Instancia del parser creada")
        
        print("\n🚀 EJECUTANDO PARSING PRINCIPAL:")
        print("-" * 50)
        
        exercises = parser.parse_file(content)
        
        print(f"\n🎉 ¡PARSING COMPLETADO EXITOSAMENTE!")
        print(f"📊 RESULTADO: {len(exercises)} ejercicios encontrados")
        
        return analyze_parsing_results(exercises)
        
    except Exception as e:
        print(f"\n❌ ERROR EN PARSING PRINCIPAL: {e}")
        print("\n🐛 TRACEBACK COMPLETO:")
        traceback.print_exc()
        
        # Ejecutar debug detallado para encontrar el problema
        print("\n🔍 INICIANDO DEBUG DETALLADO...")
        debug_parser_step_by_step(parser, content)
        
        return False

def analyze_parsing_results(exercises):
    """Analiza en detalle los resultados del parsing"""
    
    print("\n📋 ANÁLISIS DETALLADO DE RESULTADOS:")
    print("=" * 60)
    
    if not exercises:
        print("❌ No se encontraron ejercicios")
        return False
    
    # Estadísticas generales
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total ejercicios: {len(exercises)}")
    
    # Análisis por unidad temática
    units = {}
    for ex in exercises:
        unit = ex.unidad_tematica
        units[unit] = units.get(unit, 0) + 1
    
    print(f"\n🎯 DISTRIBUCIÓN POR UNIDAD TEMÁTICA:")
    for unit, count in sorted(units.items()):
        print(f"   {unit}: {count} ejercicios")
    
    # Análisis por dificultad
    difficulties = {}
    for ex in exercises:
        diff = ex.nivel_dificultad
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print(f"\n🎚️ DISTRIBUCIÓN POR DIFICULTAD:")
    for diff, count in sorted(difficulties.items()):
        print(f"   {diff}: {count} ejercicios")
    
    # Análisis por tipo
    types = {}
    for ex in exercises:
        tipo = ex.tipo_ejercicio
        types[tipo] = types.get(tipo, 0) + 1
    
    print(f"\n🔧 DISTRIBUCIÓN POR TIPO:")
    for tipo, count in sorted(types.items()):
        print(f"   {tipo}: {count} ejercicios")
    
    # Análisis de soluciones
    con_solucion = sum(1 for ex in exercises if ex.solucion_completa)
    sin_solucion = len(exercises) - con_solucion
    
    print(f"\n💡 ANÁLISIS DE SOLUCIONES:")
    print(f"   Con solución: {con_solucion} ({con_solucion/len(exercises)*100:.1f}%)")
    print(f"   Sin solución: {sin_solucion} ({sin_solucion/len(exercises)*100:.1f}%)")
    
    # Mostrar primeros ejercicios en detalle
    print(f"\n📝 PRIMEROS 5 EJERCICIOS EN DETALLE:")
    print("-" * 60)
    
    for i, exercise in enumerate(exercises[:5], 1):
        print(f"\n🏷️ EJERCICIO {i}:")
        print(f"   📋 Título: {exercise.titulo}")
        print(f"   🎯 Unidad: {exercise.unidad_tematica}")
        print(f"   🎚️ Dificultad: {exercise.nivel_dificultad}")
        print(f"   🔧 Tipo: {exercise.tipo_ejercicio}")
        print(f"   ⏱️ Tiempo: {exercise.tiempo_estimado} min")
        print(f"   💻 Modalidad: {exercise.modalidad}")
        print(f"   🏷️ Keywords: {', '.join(exercise.palabras_clave) if exercise.palabras_clave else 'N/A'}")
        print(f"   💡 Solución: {'SÍ' if exercise.solucion_completa else 'NO'}")
        print(f"   📏 Enunciado: {len(exercise.enunciado)} chars")
        print(f"   📄 Preview: {exercise.enunciado[:100]}...")
        if exercise.solucion_completa:
            print(f"   🔍 Solución: {exercise.solucion_completa[:80]}...")
    
    # Verificación de calidad
    print(f"\n🔍 VERIFICACIÓN DE CALIDAD:")
    print("-" * 40)
    
    # Verificar títulos únicos
    titles = [ex.titulo for ex in exercises]
    unique_titles = set(titles)
    if len(titles) == len(unique_titles):
        print("✅ Todos los títulos son únicos")
    else:
        print(f"⚠️ Hay títulos duplicados: {len(titles) - len(unique_titles)} duplicados")
    
    # Verificar enunciados no vacíos
    empty_statements = sum(1 for ex in exercises if not ex.enunciado.strip())
    if empty_statements == 0:
        print("✅ Todos los ejercicios tienen enunciado")
    else:
        print(f"❌ {empty_statements} ejercicios tienen enunciado vacío")
    
    # Verificar longitud mínima de enunciados
    short_statements = sum(1 for ex in exercises if len(ex.enunciado.split()) < 5)
    if short_statements == 0:
        print("✅ Todos los enunciados tienen longitud adecuada")
    else:
        print(f"⚠️ {short_statements} ejercicios tienen enunciados muy cortos")
    
    print(f"\n🏆 EVALUACIÓN GENERAL:")
    if len(exercises) >= 20 and empty_statements == 0:
        print("🎉 ¡EXCELENTE! El parser está funcionando correctamente")
        return True
    elif len(exercises) >= 10:
        print("✅ BUENO - El parser funciona pero podría mejorar")
        return True
    else:
        print("⚠️ REGULAR - El parser necesita ajustes")
        return False

def debug_parser_step_by_step(parser, content):
    """Debug paso a paso del parser"""
    
    print("\n🔍 DEBUG PASO A PASO:")
    print("=" * 50)
    
    try:
        # Step 1: Preprocess
        print("1️⃣ Testing preprocess...")
        cleaned = parser._preprocess_content(content)
        print(f"   ✅ Preprocess OK ({len(cleaned)} chars)")
        
        # Step 2: Find subsections
        print("\n2️⃣ Testing subsection detection...")
        import re
        subsection_pattern = r'\\subsection\*\{([^}]+)\}(.*?)(?=\\subsection\*|\\section|\\end\{document\}|\Z)'
        subsections = re.findall(subsection_pattern, cleaned, re.DOTALL | re.IGNORECASE)
        print(f"   ✅ Subsecciones encontradas: {len(subsections)}")
        
        if subsections:
            # Test first subsection in detail
            title, content_sec = subsections[0]
            print(f"   📂 Primera subsección: '{title}'")
            print(f"   📏 Contenido: {len(content_sec)} caracteres")
            
            # Test enumerate detection
            print("\n3️⃣ Testing enumerate detection...")
            enum_pattern = r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}'
            enum_matches = re.findall(enum_pattern, content_sec, re.DOTALL)
            print(f"   ✅ Bloques enumerate: {len(enum_matches)}")
            
            if enum_matches:
                first_enum = enum_matches[0]
                print(f"   📋 Primer enumerate: {len(first_enum)} chars")
                
                # Test nested block detection
                print("\n4️⃣ Testing nested block detection...")
                nested_ranges = parser._find_nested_blocks_ranges(first_enum)
                print(f"   ✅ Bloques anidados detectados: {len(nested_ranges)}")
                
                # Test main level item detection
                print("\n5️⃣ Testing main level item detection...")
                items = parser._split_by_main_level_items_only(first_enum)
                print(f"   ✅ Items del nivel principal: {len(items)}")
                
                # Show first item in detail
                if items:
                    print(f"\n   📝 PRIMER ITEM DETECTADO:")
                    print(f"   {'-' * 40}")
                    print(f"   {items[0][:200]}...")
                    print(f"   {'-' * 40}")
                    
                    # Test solution extraction
                    print("\n6️⃣ Testing solution extraction...")
                    enunciado, solucion = parser._extract_statement_and_solution_v4_fixed(items[0])
                    print(f"   ✅ Enunciado: {len(enunciado)} chars")
                    print(f"   ✅ Solución: {'SÍ' if solucion else 'NO'}")
                    
                    if solucion:
                        print(f"   🔍 Preview solución: {solucion[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Error en debug: {e}")
        traceback.print_exc()

def test_with_specific_sample():
    """Test con contenido específico del formato Patricio"""
    
    print("🧪 TESTING CON MUESTRA ESPECÍFICA DEL FORMATO PATRICIO")
    print("=" * 60)
    
    # Contenido real del archivo main.tex
    sample_content = r"""
\subsection*{Números complejos}

\begin{enumerate}

    \item Se tiene el número complejo $2z = 1 +i\sqrt{3}$ y $2w = \sqrt{2}-i\sqrt{2}$ ahora calcule usando la forma polar:
    \begin{enumerate}
        \item $z\cdot w$
        \item $z/w$
        \item $zz^{*},\frac{1}{2} (z + z^{*}), \frac{1}{2i} (z - z^{*})$
        \item Magnitud y fase de $(z\cdot w)^{*}$
    \end{enumerate}
    \ifanswers
    {\color{red} \textbf{Solución:} \textit{Resuelta en ayudantía}}
    \fi
    
    \item Demuestre que para todo $z \in \mathbb{C}$  se cumple que:
    \begin{itemize}
        \item $\Re{\{z\}} = \frac{z + z^*}{2}$
        \item $j\Im{\{z\}}  = \frac{z-z^*}{2}$
    \end{itemize}

    \ifanswers
    {\color{red}\textbf{Solución:} 
    
    Tomamos un complejo cualquiera $z = \sigma + j \omega$\\
    $$z + z^* = \sigma + j\omega + \sigma -j\omega = 2\sigma $$
    $$\frac{z + z^*}{2} = \sigma$$
    Similarmente:
    $$z-z^* = \sigma +j\omega - \sigma + j\omega = 2j\omega$$
    $$\frac{z - z^*}{2} = j \omega$$}
    \fi

    \item Demuestre que 
    \begin{align*}
        1-e^{j\alpha} = 2\sin \left(\frac{\alpha}{2}\right)e^{j(\alpha-\pi)/2}
    \end{align*}
    
    \ifanswers
    {\color{red} \textbf{Solución:}

    Aplicando la identidad de Euler a la parte derecha de la igualdad se obtiene:
    \begin{align*}
        1-e^{j\alpha} &= 2\sin\left(\frac{\alpha}{2}\right)(\cos\left(\frac{\alpha}{2}-\frac{\pi}{2}\right)+j\sin\left(\frac{\alpha}{2}-\frac{\pi}{2}\right))
    \end{align*}
    }
    \fi

\end{enumerate}
    """
    
    try:
        from utils.latex_parser import LaTeXParser
        parser = LaTeXParser()
        
        print("📋 Contenido de muestra específica del formato Patricio")
        print("📊 Se esperan 3 ejercicios del tema 'Números complejos'")
        print("   - Ejercicio 1: Con sub-partes (enumerate) - Sin solución real")
        print("   - Ejercicio 2: Con sub-partes (itemize) - Con solución completa")
        print("   - Ejercicio 3: Demostración matemática - Con solución completa")
        
        exercises = parser.parse_file(sample_content)
        
        print(f"\n🎯 RESULTADO: {len(exercises)} ejercicios encontrados")
        
        if len(exercises) == 3:
            print("✅ ¡PERFECTO! Se encontraron exactamente 3 ejercicios como esperado")
            
            for i, ex in enumerate(exercises, 1):
                print(f"\n📝 Ejercicio {i}:")
                print(f"   Título: {ex.titulo}")
                print(f"   Unidad: {ex.unidad_tematica}")
                print(f"   Dificultad: {ex.nivel_dificultad}")
                print(f"   Solución: {'SÍ' if ex.solucion_completa else 'NO'}")
                print(f"   Enunciado (preview): {ex.enunciado[:80]}...")
            
            return True
        else:
            print(f"⚠️ Se esperaban 3 ejercicios, pero se encontraron {len(exercises)}")
            return False
        
    except Exception as e:
        print(f"❌ Error en test de muestra: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    
    print("🧪 LATEX PARSER V4.0 - TESTER MEJORADO")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("📋 USO:")
        print("  python test_parser_improved.py <archivo.tex>")
        print("  python test_parser_improved.py sample")
        print("  python test_parser_improved.py debug_specific")
        print("\n🔧 EJEMPLOS:")
        print("  python test_parser_improved.py main.tex")
        print("  python test_parser_improved.py sample")
        print("  python test_parser_improved.py debug_specific")
        return
    
    arg = sys.argv[1].lower()
    
    if arg == "sample":
        success = test_with_specific_sample()
    elif arg == "debug_specific":
        success = test_with_specific_sample()
        if success:
            print("\n🔍 Test específico exitoso, ahora puedes probar con tu archivo real:")
            print("python test_parser_improved.py main.tex")
    else:
        # Test con archivo real
        success = test_parser_with_file(sys.argv[1])
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡TEST COMPLETADO EXITOSAMENTE!")
        print("✅ El parser V4.0 está funcionando correctamente")
        print("🚀 Puedes proceder a usarlo en tu aplicación Streamlit")
    else:
        print("❌ TEST FALLÓ - Revisar errores arriba")
        print("🔧 Considera usar 'debug_specific' para identificar problemas")
    print("=" * 60)

if __name__ == "__main__":
    main()