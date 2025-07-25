"""
Buscar Ejercicios
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Buscar Ejercicios - Gestión Ejercicios SyS",
    page_icon="🔍",
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
    .exercise-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    .difficulty-basic { color: #28a745; }
    .difficulty-intermedio { color: #ffc107; }
    .difficulty-avanzado { color: #fd7e14; }
    .difficulty-desafio { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

def get_difficulty_color(difficulty):
    """Retorna la clase CSS para el color de dificultad"""
    colors = {
        'Básico': 'difficulty-basic',
        'Intermedio': 'difficulty-intermedio', 
        'Avanzado': 'difficulty-avanzado',
        'Desafío': 'difficulty-desafio'
    }
    return colors.get(difficulty, '')

def show_exercise_card(exercise):
    """Muestra una tarjeta de ejercicio"""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{exercise['titulo']}**")
            st.caption(f"ID: {exercise['id']} | {exercise['unidad_tematica']}")
            
        with col2:
            difficulty_class = get_difficulty_color(exercise['nivel_dificultad'])
            st.markdown(f"<span class='{difficulty_class}'>{exercise['nivel_dificultad']}</span>", 
                       unsafe_allow_html=True)
            st.caption(f"{exercise['tiempo_estimado']} min")
            
        with col3:
            st.caption(f"Modalidad: {exercise['modalidad']}")
            st.caption(f"Estado: {exercise.get('estado', 'Listo')}")

def main():
    """Página para buscar y filtrar ejercicios"""
    st.markdown('<h1 class="main-header">🔍 Buscar Ejercicios</h1>', 
                unsafe_allow_html=True)
    
    # Filtros
    with st.expander("🔧 Filtros de Búsqueda", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unidades = ["Todas"] + ["Introducción", "Sistemas Continuos", "Transformada de Fourier", 
                                   "Transformada de Laplace", "Sistemas Discretos", 
                                   "Transformada de Fourier Discreta", "Transformada Z"]
            filtro_unidad = st.selectbox("Unidad Temática", unidades)
            
        with col2:
            dificultades = ["Todas", "Básico", "Intermedio", "Avanzado", "Desafío"]
            filtro_dificultad = st.selectbox("Dificultad", dificultades)
            
        with col3:
            modalidades = ["Todas", "Teórico", "Computacional", "Mixto"]
            filtro_modalidad = st.selectbox("Modalidad", modalidades)
        
        # Búsqueda por texto
        busqueda_texto = st.text_input("🔍 Buscar por título o contenido")
    
    # Obtener ejercicios de la base de datos
    try:
        from database.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Aplicar filtros
        filtros = {}
        if filtro_unidad != "Todas":
            filtros['unidad_tematica'] = filtro_unidad
        if filtro_dificultad != "Todas":
            filtros['nivel_dificultad'] = filtro_dificultad
        if filtro_modalidad != "Todas":
            filtros['modalidad'] = filtro_modalidad
        
        ejercicios_filtrados = db_manager.obtener_ejercicios(filtros)
        
        # Filtro por texto (búsqueda simple)
        if busqueda_texto:
            ejercicios_filtrados = [
                e for e in ejercicios_filtrados 
                if busqueda_texto.lower() in e['titulo'].lower() or 
                   busqueda_texto.lower() in e['enunciado'].lower()
            ]
        
    except Exception as e:
        st.error(f"❌ Error cargando ejercicios: {e}")
        ejercicios_filtrados = []
    
    # Mostrar resultados
    st.subheader("📋 Resultados de la Búsqueda")
    
    if ejercicios_filtrados:
        st.write(f"**Encontrados:** {len(ejercicios_filtrados)} ejercicios")
        
        for exercise in ejercicios_filtrados:
            with st.container():
                show_exercise_card(exercise)
                
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button("👁️ Ver", key=f"ver_{exercise['id']}"):
                        st.session_state[f"show_detail_{exercise['id']}"] = True
                        
                with col2:
                    if st.button("✏️ Editar", key=f"edit_{exercise['id']}"):
                        st.info("Función de edición en desarrollo")
                
                # Mostrar detalles si se solicita
                if st.session_state.get(f"show_detail_{exercise['id']}", False):
                    with st.expander(f"📄 Detalles - {exercise['titulo']}", expanded=True):
                        st.write(f"**Enunciado:** {exercise['enunciado']}")
                        st.write(f"**ID:** {exercise['id']}")
                        if exercise.get('solucion_completa'):
                            st.write(f"**Solución:** {exercise['solucion_completa']}")
                        if exercise.get('fecha_creacion'):
                            st.write(f"**Fecha de creación:** {exercise['fecha_creacion']}")
                        
                        if st.button("❌ Cerrar", key=f"close_{exercise['id']}"):
                            st.session_state[f"show_detail_{exercise['id']}"] = False
                            st.rerun()
                
                st.divider()
    else:
        st.warning("No se encontraron ejercicios con los filtros seleccionados")

if __name__ == "__main__":
    main()