"""
Importar LaTeX - CON ESTADO PERSISTENTE
Sistema de Gestión de Ejercicios - Señales y Sistemas
VERSIÓN ARREGLADA: Usa st.session_state para mantener ejercicios
"""

import streamlit as st
import logging

# Configuración de la página
st.set_page_config(
    page_title="Importar LaTeX - Gestión Ejercicios SyS",
    page_icon="📥",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Página para importar ejercicios desde LaTeX - VERSIÓN ARREGLADA"""
    st.markdown('<h1 class="main-header">📥 Importar Ejercicios desde LaTeX</h1>', 
                unsafe_allow_html=True)
    
    st.info("""
    **¿Cómo funciona el importador?**
    
    1. **Detecta patrones automáticamente**: Busca estructuras como `\\begin{ejercicio}...\\end{ejercicio}`, numeración, etc.
    2. **Extrae metadatos**: Reconoce comentarios como `% Dificultad: Intermedio` o `% Unidad: Fourier`
    3. **Preview antes de importar**: Te permite revisar y editar antes de guardar en la base de datos
    4. **Mapeo inteligente**: Asigna automáticamente categorías basado en palabras clave
    """)
    
    st.subheader("🔄 Importador de Ejercicios LaTeX")
    
    # ========================================
    # 🔧 ESTADO PERSISTENTE - CLAVE DEL FIX
    # ========================================
    
    # Inicializar session_state
    if 'exercises_found' not in st.session_state:
        st.session_state.exercises_found = []
    if 'import_completed' not in st.session_state:
        st.session_state.import_completed = False
    
    # Método de entrada
    input_method = st.radio(
        "Método de entrada:",
        ["📁 Subir archivo LaTeX", "📝 Pegar código LaTeX"]
    )
    
    # ========================================
    # OPCIÓN 1: SUBIR ARCHIVO
    # ========================================
    if input_method == "📁 Subir archivo LaTeX":
        uploaded_file = st.file_uploader(
            "Selecciona archivo .tex",
            type=['tex', 'txt'],
            help="Sube tu archivo LaTeX con ejercicios"
        )
        
        if uploaded_file:
            content = str(uploaded_file.read(), "utf-8")
            
            with st.expander("👀 Vista previa del archivo"):
                st.code(content[:1000] + "..." if len(content) > 1000 else content, 
                        language="latex")
            
            if st.button("🔄 Extraer Ejercicios", key="extract_file"):
                with st.spinner("🔍 Analizando archivo LaTeX..."):
                    try:
                        # Importar el parser real
                        from utils.latex_parser import LaTeXParser
                        
                        # Crear instancia del parser
                        parser = LaTeXParser()
                        
                        # Parsear el contenido del archivo
                        parsed_exercises = parser.parse_file(content)
                        
                        # Convertir ParsedExercise a diccionarios y GUARDAR EN SESSION_STATE
                        exercises_found = []
                        for parsed_ex in parsed_exercises:
                            exercise_dict = {
                                'titulo': parsed_ex.titulo,
                                'enunciado': parsed_ex.enunciado,
                                'unidad_tematica': parsed_ex.unidad_tematica,
                                'nivel_dificultad': parsed_ex.nivel_dificultad,
                                'modalidad': parsed_ex.modalidad,
                                'tiempo_estimado': parsed_ex.tiempo_estimado,
                                'fuente': uploaded_file.name,
                                'pattern_used': parsed_ex.pattern_used
                            }
                            
                            # Agregar solucion_completa si existe
                            if hasattr(parsed_ex, 'solucion_completa') and parsed_ex.solucion_completa:
                                exercise_dict['solucion_completa'] = parsed_ex.solucion_completa
                            
                            # Agregar otros campos opcionales
                            optional_fields = ['respuesta_final', 'palabras_clave', 'subtemas', 'tipo_actividad', 'comentarios']
                            for field in optional_fields:
                                if hasattr(parsed_ex, field) and getattr(parsed_ex, field):
                                    exercise_dict[field] = getattr(parsed_ex, field)
                            
                            exercises_found.append(exercise_dict)
                        
                        # 🚀 GUARDAR EN SESSION_STATE (CLAVE DEL FIX)
                        st.session_state.exercises_found = exercises_found
                        st.session_state.import_completed = False
                        
                        if exercises_found:
                            st.success(f"✅ Se encontraron {len(exercises_found)} ejercicios")
                        else:
                            st.warning("⚠️ No se encontraron ejercicios en el archivo")
                            
                    except ImportError as e:
                        st.error(f"❌ Error importando parser: {e}")
                        st.error("Verifica que utils/latex_parser.py existe y es válido")
                        st.session_state.exercises_found = []
                        
                    except Exception as e:
                        st.error(f"❌ Error parseando archivo: {e}")
                        st.exception(e)
                        st.session_state.exercises_found = []
    
    # ========================================
    # OPCIÓN 2: PEGAR CÓDIGO
    # ========================================
    elif input_method == "📝 Pegar código LaTeX":
        latex_content = st.text_area(
            "Pega tu código LaTeX aquí:",
            height=300,
            placeholder="""\\begin{ejercicio}
% Dificultad: Intermedio
% Unidad: Sistemas Continuos
Calcule la convolución y(t) = x(t) * h(t) donde:
- x(t) = rect(t/2)
- h(t) = δ(t-1)
\\end{ejercicio}"""
        )
        
        if latex_content and st.button("🔄 Extraer Ejercicios", key="extract_text"):
            with st.spinner("🔍 Analizando código LaTeX..."):
                try:
                    # Importar el parser real
                    from utils.latex_parser import LaTeXParser
                    
                    # Crear instancia del parser
                    parser = LaTeXParser()
                    
                    # Parsear el contenido
                    parsed_exercises = parser.parse_file(latex_content)
                    
                    # Convertir ParsedExercise a diccionarios
                    exercises_found = []
                    for parsed_ex in parsed_exercises:
                        exercise_dict = {
                            'titulo': parsed_ex.titulo,
                            'enunciado': parsed_ex.enunciado,
                            'unidad_tematica': parsed_ex.unidad_tematica,
                            'nivel_dificultad': parsed_ex.nivel_dificultad,
                            'modalidad': parsed_ex.modalidad,
                            'tiempo_estimado': parsed_ex.tiempo_estimado,
                            'fuente': 'Importación manual',
                            'pattern_used': parsed_ex.pattern_used
                        }
                        
                        # Agregar solucion_completa si existe
                        if hasattr(parsed_ex, 'solucion_completa') and parsed_ex.solucion_completa:
                            exercise_dict['solucion_completa'] = parsed_ex.solucion_completa
                        
                        exercises_found.append(exercise_dict)
                    
                    # 🚀 GUARDAR EN SESSION_STATE
                    st.session_state.exercises_found = exercises_found
                    st.session_state.import_completed = False
                    
                    if exercises_found:
                        st.success(f"✅ Se encontraron {len(exercises_found)} ejercicios")
                    else:
                        st.warning("⚠️ No se encontraron ejercicios en el código")
                        
                except Exception as e:
                    st.error(f"❌ Error parseando código: {e}")
                    st.session_state.exercises_found = []
    
    # ========================================
    # MOSTRAR EJERCICIOS ENCONTRADOS
    # ========================================
    if st.session_state.exercises_found:
        st.subheader("📋 Ejercicios Encontrados")
        
        # Debug info
        with st.expander("🔍 DEBUG: Información del Parser"):
            st.write(f"**Total ejercicios en session_state:** {len(st.session_state.exercises_found)}")
            if st.session_state.exercises_found:
                st.write("**Primer ejercicio:**")
                st.json(st.session_state.exercises_found[0])
        
        # Mostrar ejercicios
        for i, exercise in enumerate(st.session_state.exercises_found):
            with st.expander(f"📝 {exercise['titulo']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Enunciado:**")
                    st.write(exercise['enunciado'])
                    if 'solucion_completa' in exercise:
                        st.write("**Solución:**")
                        st.write(exercise['solucion_completa'])
                
                with col2:
                    st.write("**Metadatos:**")
                    st.write(f"- **Dificultad:** {exercise['nivel_dificultad']}")
                    st.write(f"- **Unidad:** {exercise['unidad_tematica']}")
                    st.write(f"- **Tiempo:** {exercise['tiempo_estimado']} min")
                    st.write(f"- **Modalidad:** {exercise['modalidad']}")
                    st.write(f"- **Patrón:** {exercise['pattern_used']}")
        
        # ========================================
        # 🚀 IMPORTACIÓN A BASE DE DATOS - ARREGLADA
        # ========================================
        st.subheader("💾 Importar a Base de Datos")
        
        import_all = st.checkbox("Importar todos los ejercicios", value=True)
        
        if st.button("💾 Confirmar Importación", type="primary"):
            # USAR EXERCISES DESDE SESSION_STATE (NO VARIABLE LOCAL)
            exercises_to_import = st.session_state.exercises_found
            
            st.write(f"🔍 DEBUG: Importando {len(exercises_to_import)} ejercicios desde session_state")
            
            try:
                # Importar el DatabaseManager
                from database.db_manager import DatabaseManager
                
                # Inicializar DatabaseManager
                db_manager = DatabaseManager()
                
                # Preparar ejercicios para importación
                ejercicios_preparados = []
                for ex in exercises_to_import:
                    # Asegurar que tienen los campos mínimos requeridos
                    ejercicio = {
                        'titulo': ex.get('titulo', 'Sin título'),
                        'enunciado': ex.get('enunciado', ''),
                        'unidad_tematica': ex.get('unidad_tematica', 'General'),
                        'nivel_dificultad': ex.get('nivel_dificultad', 'Intermedio'),
                        'modalidad': ex.get('modalidad', 'Teórico'),
                        'tiempo_estimado': ex.get('tiempo_estimado', 20),
                        'fuente': ex.get('fuente', 'Importación LaTeX')
                    }
                    
                    # Agregar campos opcionales con mapeo correcto
                    campos_opcionales = {
                        'solucion_completa': ['solucion_completa', 'solucion'],
                        'datos_entrada': ['datos_entrada'],
                        'codigo_python': ['codigo_python'],
                        'respuesta_final': ['respuesta_final'],
                        'prerrequisitos': ['prerrequisitos'],
                        'comentarios_docente': ['comentarios_docente']
                    }
                    
                    for campo_bd, campos_parser in campos_opcionales.items():
                        for campo_parser in campos_parser:
                            if campo_parser in ex and ex[campo_parser]:
                                ejercicio[campo_bd] = ex[campo_parser]
                                break
                    
                    ejercicios_preparados.append(ejercicio)
                
                # Importar ejercicios UNO POR UNO
                importados = 0
                errores = []
                
                progress = st.progress(0)
                status = st.empty()
                
                for i, ejercicio in enumerate(ejercicios_preparados):
                    try:
                        status.write(f"Importando {i+1}/{len(ejercicios_preparados)}: {ejercicio['titulo']}")
                        progress.progress((i + 1) / len(ejercicios_preparados))
                        
                        ejercicio_id = db_manager.agregar_ejercicio(ejercicio)
                        if ejercicio_id:
                            importados += 1
                            st.write(f"✅ Importado: {ejercicio['titulo']} (ID: {ejercicio_id})")
                    except Exception as e:
                        error_msg = f"Error con '{ejercicio['titulo']}': {str(e)}"
                        errores.append(error_msg)
                        st.error(error_msg)
                
                # Limpiar progress
                progress.empty()
                status.empty()
                
                # Mostrar resultados
                if importados > 0:
                    st.success(f"🎉 ¡{importados} ejercicios importados exitosamente!")
                    st.balloons()
                    
                    # Verificar que se guardaron en BD
                    ejercicios_bd = db_manager.obtener_ejercicios()
                    st.info(f"📊 Total ejercicios en BD ahora: {len(ejercicios_bd)}")
                    
                    # Marcar como completado
                    st.session_state.import_completed = True
                
                if errores:
                    st.error(f"❌ {len(errores)} errores durante la importación:")
                    for error in errores[:5]:
                        st.error(f"  • {error}")
                        
            except Exception as e:
                st.error(f"❌ Error crítico durante la importación: {str(e)}")
                st.exception(e)
    elif not st.session_state.exercises_found and st.session_state.get('import_completed', False):
        st.info("✅ Importación completada. Los ejercicios están disponibles en 'Buscar Ejercicios'")
    
    # Consejos
    with st.expander("💡 Consejos para mejores resultados"):
        st.markdown("""
        **Patrones reconocidos automáticamente:**
        - `\\begin{ejercicio}...\\end{ejercicio}`
        - `\\begin{problem}...\\end{problem}`
        - `\\ejercicio{...}`
        - Numeración con `\\item`
        - Secciones con ejercicios
        
        **Metadatos que se extraen:**
        - `% Dificultad: Básico/Intermedio/Avanzado/Desafío`
        - `% Unidad: Sistemas Continuos`
        - `% Tiempo: 25` (minutos)
        - `\\begin{solucion}...\\end{solucion}`
        
        **Palabras clave para clasificación automática:**
        - "convolución", "lineal" → Sistemas Continuos
        - "fourier", "serie" → Transformada de Fourier
        - "laplace" → Transformada de Laplace
        - "muestreo", "discreto" → Sistemas Discretos
        - "dft", "fft" → Transformada de Fourier Discreta
        - "transformada z" → Transformada Z
        """)

if __name__ == "__main__":
    main()