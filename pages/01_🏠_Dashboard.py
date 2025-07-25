"""
Dashboard - Página principal
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Dashboard - Gestión Ejercicios SyS",
    page_icon="🏠",
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
    .metric-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4e79;
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

@st.cache_data
def load_sample_data():
    """Carga datos de ejemplo"""
    return [
        {
            'id': 1,
            'titulo': 'Convolución de señales rectangulares',
            'unidad_tematica': 'Sistemas Continuos',
            'nivel_dificultad': 'Básico',
            'tiempo_estimado': 15,
            'modalidad': 'Teórico',
            'enunciado': 'Calcule la convolución de dos señales rectangulares...',
            'estado': 'Listo',
            'fecha_creacion': '2024-01-15'
        },
        {
            'id': 2,
            'titulo': 'FFT de señal sinusoidal con ruido',
            'unidad_tematica': 'Transformada de Fourier Discreta',
            'nivel_dificultad': 'Intermedio',
            'tiempo_estimado': 25,
            'modalidad': 'Computacional',
            'enunciado': 'Implemente en Python el cálculo de la FFT...',
            'estado': 'Listo',
            'fecha_creacion': '2024-01-20'
        },
        {
            'id': 3,
            'titulo': 'Análisis de estabilidad con transformada Z',
            'unidad_tematica': 'Transformada Z',
            'nivel_dificultad': 'Avanzado',
            'tiempo_estimado': 35,
            'modalidad': 'Mixto',
            'enunciado': 'Analice la estabilidad del sistema dado usando...',
            'estado': 'En revisión',
            'fecha_creacion': '2024-01-25'
        }
    ]

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
            st.caption(f"Estado: {exercise['estado']}")

def main():
    """Página principal - Dashboard"""
    st.markdown('<h1 class="main-header">📚 Dashboard - Ejercicios SyS</h1>', 
                unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Ejercicios", "3", "↗️ +1")
    with col2:
        st.metric("Listos para usar", "2", "")
    with col3:
        st.metric("En revisión", "1", "")
    with col4:
        st.metric("Último agregado", "3 días", "")
    
    # Distribución por unidad temática
    st.subheader("📈 Distribución por Unidad Temática")
    
    # Datos de ejemplo para el gráfico
    unidades_data = pd.DataFrame({
        'Unidad': ['Sistemas Continuos', 'DFT', 'Transformada Z'],
        'Cantidad': [1, 1, 1]
    })
    
    st.bar_chart(unidades_data.set_index('Unidad'))
    
    # Ejercicios recientes
    st.subheader("🕒 Ejercicios Agregados Recientemente")
    
    sample_data = load_sample_data()
    for exercise in sample_data:
        show_exercise_card(exercise)

if __name__ == "__main__":
    main()