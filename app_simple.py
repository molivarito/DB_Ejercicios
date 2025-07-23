#!/usr/bin/env python3
"""
Sistema de Gestión de Ejercicios - Streamlit App Simplificada
Versión enfocada en el importador LaTeX
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from pathlib import Path
import sys

# Agregar utils al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Configuración de la página
st.set_page_config(
    page_title="Importador Ejercicios SyS",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado simple
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .exercise-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample_data():
    """Carga datos de ejemplo"""
    return [
        {
            'id': 1,
            'titulo': 'Ejemplo - Convolución',
            'unidad_tematica': 'Sistemas Continuos',
            'nivel_dificultad': 'Básico',
            'tiempo_estimado': 15,
            'modalidad': 'Teórico'
        }
    ]

def setup_sidebar():
    """Configura el sidebar de navegación"""
    st.sidebar.markdown("## 📥 Importador LaTeX")
    st.sidebar.markdown("**Señales y Sistemas - PUC**")
    st.sidebar.markdown("---")
    
    menu_options = [
        "📥 Importar LaTeX",
        "🏠 Dashboard Simple",
        "📊 Ver Ejercicios"
    ]
    
    return st.sidebar.selectbox("Navegación", menu_options)

def show_latex_import():
    """Página principal para importar ejercicios desde LaTeX"""
    st.markdown('<h1 class="main-header">📥 Importar Ejercicios desde LaTeX</h1>', 
                unsafe_allow_html=True)
    
    st.info("""
    **Importador especializado para el formato de Patricio:**
    - Detecta subsecciones como 'Números complejos', 'Señales y Sistemas'
    - Extrae ejercicios de listas enumerate
    - Encuentra soluciones en bloques ifanswers
    - Clasifica automáticamente por unidad temática
    """)
    
    # Importar el parser
    try:
        from latex_parser import LaTeXExerciseParser
        parser_available = True
    except ImportError:
        st.error("❌ No se pudo importar el parser LaTeX. Verifica que latex_parser.py esté en utils/")
        parser_available = False
        return
    
    if not parser_available:
        return
    
    # Interfaz de importación
    st.subheader("🔄 Importador de Ejercicios")
    
    input_method = st.radio(
        "Método de entrada:",
        ["📁 Subir archivo LaTeX", "📝 Pegar código LaTeX"]
    )
    
    exercises_found = []
    
    if input_method == "📁 Subir archivo LaTeX":
        uploaded_file = st.file_uploader(
            "Selecciona archivo .tex",
            type=['tex', 'txt'],
            help="Sube tu archivo LaTeX con ejercicios (como main.tex)"
        )
        
        if uploaded_file:
            try:
                # Leer contenido del archivo
                content = str(uploaded_file.read(), "utf-8")
                
                with st.expander("👀 Vista previa del archivo (primeros 1000 caracteres)"):
                    st.code(content[:1000] + "..." if len(content) > 1000 else content, 
                            language="latex")
                
                if st.button("🔄 Extraer Ejercicios", type="primary"):
                    with st.spinner("Extrayendo ejercicios..."):
                        parser = LaTeXExerciseParser()
                        exercises_found = parser.parse_content(content, uploaded_file.name)
                        
                        if exercises_found:
                            st.success(f"✅ Se encontraron {len(exercises_found)} ejercicios")
                            st.session_state['exercises_found'] = exercises_found
                        else:
                            st.warning("⚠️ No se encontraron ejercicios en el archivo")
                            
            except Exception as e:
                st.error(f"❌ Error procesando archivo: {str(e)}")
    
    elif input_method == "📝 Pegar código LaTeX":
        latex_content = st.text_area(
            "Pega tu código LaTeX aquí:",
            height=300,
            placeholder="""\\subsection*{Números complejos}
\\begin{enumerate}
\\item Calcule el número complejo...
\\ifanswers
{\\color{red} \\textbf{Solución:} La respuesta es...}
\\fi
\\end{enumerate}"""
        )
        
        if latex_content and st.button("🔄 Extraer Ejercicios", type="primary"):
            with st.spinner("Extrayendo ejercicios..."):
                try:
                    parser = LaTeXExerciseParser()
                    exercises_found = parser.parse_content(latex_content, "Contenido manual")
                    
                    if exercises_found:
                        st.success(f"✅ Se encontraron {len(exercises_found)} ejercicios")
                        st.session_state['exercises_found'] = exercises_found
                    else:
                        st.warning("⚠️ No se encontraron ejercicios en el contenido")
                        
                except Exception as e:
                    st.error(f"❌ Error procesando contenido: {str(e)}")
    
    # Mostrar ejercicios encontrados
    if 'exercises_found' in st.session_state:
        exercises_found = st.session_state['exercises_found']
        
        st.subheader("📋 Ejercicios Encontrados")
        
        # Resumen rápido
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total encontrados", len(exercises_found))
        with col2:
            unidades = set(ex.get('unidad_tematica', 'Sin clasificar') for ex in exercises_found)
            st.metric("Unidades diferentes", len(unidades))
        with col3:
            con_solucion = sum(1 for ex in exercises_found if ex.get('solucion_completa'))
            st.metric("Con solución", con_solucion)
        
        # Lista de ejercicios
        for i, exercise in enumerate(exercises_found):
            with st.expander(f"📝 {exercise.get('titulo', f'Ejercicio {i+1}')}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Enunciado:**")
                    enunciado = exercise.get('enunciado', 'No disponible')
                    st.write(enunciado[:300] + "..." if len(enunciado) > 300 else enunciado)
                    
                    if exercise.get('solucion_completa'):
                        st.write("**✅ Solución encontrada:**")
                        solucion = exercise['solucion_completa']
                        st.write(solucion[:200] + "..." if len(solucion) > 200 else solucion)
                    else:
                        st.write("**❌ Sin solución detectada**")
                
                with col2:
                    st.write("**Metadatos:**")
                    st.write(f"🎯 **Unidad:** {exercise.get('unidad_tematica', 'No especificada')}")
                    st.write(f"📊 **Dificultad:** {exercise.get('nivel_dificultad', 'No especificada')}")
                    st.write(f"💻 **Modalidad:** {exercise.get('modalidad', 'No especificada')}")
                    st.write(f"⏱️ **Tiempo:** {exercise.get('tiempo_estimado', 'No especificado')} min")
                    st.write(f"🔧 **Patrón:** {exercise.get('pattern_used', 'No especificado')}")
        
        # Simulación de importación (no conectamos a DB aún)
        st.subheader("💾 Simulación de Importación")
        
        if st.button("💾 Simular Importación a Base de Datos", type="primary"):
            progress_bar = st.progress(0)
            for i in range(len(exercises_found)):
                progress_bar.progress((i + 1) / len(exercises_found))
            
            st.success(f"✅ Simulación completada: {len(exercises_found)} ejercicios procesados")
            st.balloons()
            st.info("En la versión completa, estos ejercicios se guardarían en la base de datos SQLite")

def show_dashboard():
    """Dashboard simple"""
    st.markdown('<h1 class="main-header">🏠 Dashboard Simple</h1>', 
                unsafe_allow_html=True)
    
    st.write("Sistema de gestión de ejercicios para IEE2103 - Señales y Sistemas")
    
    # Métricas simuladas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ejercicios en sistema", "3", "↗️ +1")
    with col2:
        st.metric("Listos para usar", "2")
    with col3:
        st.metric("Importados hoy", "0")
    
    st.info("Ve a 'Importar LaTeX' para agregar ejercicios desde tus archivos .tex")

def show_exercises():
    """Muestra ejercicios cargados"""
    st.markdown('<h1 class="main-header">📊 Ejercicios en el Sistema</h1>', 
                unsafe_allow_html=True)
    
    # Ejercicios de ejemplo
    sample_data = load_sample_data()
    
    if 'exercises_found' in st.session_state:
        exercises = st.session_state['exercises_found']
        st.write(f"**Ejercicios importados en esta sesión:** {len(exercises)}")
        
        # Crear DataFrame para mostrar
        df_data = []
        for ex in exercises:
            df_data.append({
                'Título': ex.get('titulo', 'Sin título')[:50],
                'Unidad': ex.get('unidad_tematica', 'No clasificada'),
                'Dificultad': ex.get('nivel_dificultad', 'No especificada'),
                'Tiempo (min)': ex.get('tiempo_estimado', 0),
                'Con Solución': '✅' if ex.get('solucion_completa') else '❌'
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay ejercicios importados en esta sesión. Ve a 'Importar LaTeX' para comenzar.")

def main():
    """Función principal"""
    
    # Sidebar
    selected_page = setup_sidebar()
    
    # Información del sistema en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Estado del Sistema")
    st.sidebar.success("✅ Parser LaTeX listo")
    
    if 'exercises_found' in st.session_state:
        count = len(st.session_state['exercises_found'])
        st.sidebar.info(f"📚 {count} ejercicios en sesión")
    else:
        st.sidebar.info("📚 Sin ejercicios cargados")
    
    # Navegación
    if selected_page == "📥 Importar LaTeX":
        show_latex_import()
    elif selected_page == "🏠 Dashboard Simple":
        show_dashboard()
    elif selected_page == "📊 Ver Ejercicios":
        show_exercises()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Sistema de Gestión de Ejercicios**")
    st.sidebar.markdown("*Señales y Sistemas - PUC*")
    st.sidebar.markdown("v1.0.1 - Importador LaTeX")

if __name__ == "__main__":
    main()