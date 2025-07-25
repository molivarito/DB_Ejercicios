"""
Generar Prueba
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Generar Prueba - Gestión Ejercicios SyS",
    page_icon="🎯",
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
        },
        {
            'id': 2,
            'titulo': 'FFT de señal sinusoidal con ruido',
            'unidad_tematica': 'Transformada de Fourier Discreta',
            'nivel_dificultad': 'Intermedio',
            'tiempo_estimado': 25,
            'modalidad': 'Computacional',
            'enunciado': 'Implemente en Python el cálculo de la FFT...',
        },
        {
            'id': 3,
            'titulo': 'Análisis de estabilidad con transformada Z',
            'unidad_tematica': 'Transformada Z',
            'nivel_dificultad': 'Avanzado',
            'tiempo_estimado': 35,
            'modalidad': 'Mixto',
            'enunciado': 'Analice la estabilidad del sistema dado usando...',
        }
    ]

def main():
    """Página para generar pruebas"""
    st.markdown('<h1 class="main-header">🎯 Generador de Pruebas</h1>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚙️ Configuración de la Prueba")
        
        # Información general
        nombre_prueba = st.text_input("Nombre de la Prueba", "Interrogación 1 - SyS")
        semestre = st.text_input("Semestre", "2025-1")
        fecha_prueba = st.date_input("Fecha de la Prueba", datetime.now().date())
        
        # Criterios de selección
        st.subheader("🎲 Criterios de Selección")
        
        unidades_incluir = st.multiselect(
            "Unidades Temáticas a Incluir",
            ["Introducción", "Sistemas Continuos", "Transformada de Fourier", 
             "Transformada de Laplace", "Sistemas Discretos", 
             "Transformada de Fourier Discreta", "Transformada Z"],
            default=["Sistemas Continuos", "Transformada de Fourier"]
        )
        
        num_ejercicios = st.number_input("Número de Ejercicios", min_value=1, max_value=20, value=4)
        
        distribucion_dificultad = st.selectbox(
            "Distribución de Dificultad",
            ["Automática (balanceada)", "Principalmente Básico", "Principalmente Intermedio", 
             "Principalmente Avanzado", "Solo Básico", "Solo Intermedio", "Solo Avanzado"]
        )
        
        tiempo_total = st.number_input("Tiempo Total (minutos)", min_value=30, max_value=180, value=90)
        
        modalidad_prueba = st.multiselect(
            "Modalidades Permitidas",
            ["Teórico", "Computacional", "Mixto"],
            default=["Teórico", "Mixto"]
        )
        
        incluir_soluciones = st.checkbox("Incluir soluciones en PDF separado", value=True)
        
        # Botón para generar
        if st.button("🎯 Generar Prueba", type="primary"):
            with st.spinner("Generando prueba..."):
                try:
                    # Intentar usar la base de datos real
                    from database.db_manager import DatabaseManager
                    db_manager = DatabaseManager()
                    
                    # Aplicar filtros
                    filtros = {}
                    if unidades_incluir:
                        # Por ahora, solo usar la primera unidad como filtro
                        filtros['unidad_tematica'] = unidades_incluir[0]
                    
                    # Obtener ejercicios de la BD
                    ejercicios_disponibles = db_manager.obtener_ejercicios(filtros)
                    
                    if ejercicios_disponibles:
                        # Seleccionar ejercicios (por ahora, los primeros)
                        ejercicios_seleccionados = ejercicios_disponibles[:min(num_ejercicios, len(ejercicios_disponibles))]
                    else:
                        st.warning("No se encontraron ejercicios en la base de datos. Usando ejemplos.")
                        ejercicios_seleccionados = load_sample_data()[:min(num_ejercicios, 3)]
                    
                except Exception as e:
                    st.warning(f"Error accediendo BD: {e}. Usando datos de ejemplo.")
                    ejercicios_seleccionados = load_sample_data()[:min(num_ejercicios, 3)]
                
                st.success("✅ Prueba generada exitosamente!")
                
                # Guardar en session_state
                st.session_state['ejercicios_seleccionados'] = ejercicios_seleccionados
                st.session_state['config_prueba'] = {
                    'nombre': nombre_prueba,
                    'semestre': semestre,
                    'fecha': fecha_prueba,
                    'tiempo_total': tiempo_total,
                    'unidades': unidades_incluir,
                    'distribucion': distribucion_dificultad
                }
    
    with col2:
        st.subheader("📋 Vista Previa de la Prueba")
        
        if 'ejercicios_seleccionados' in st.session_state:
            config = st.session_state['config_prueba']
            ejercicios = st.session_state['ejercicios_seleccionados']
            
            # Encabezado de la prueba
            st.markdown(f"""
            **{config['nombre']}**  
            **Semestre:** {config['semestre']}  
            **Fecha:** {config['fecha']}  
            **Tiempo:** {config['tiempo_total']} minutos  
            **Total Ejercicios:** {len(ejercicios)}
            """)
            
            st.divider()
            
            # Lista de ejercicios
            for i, ejercicio in enumerate(ejercicios, 1):
                with st.container():
                    st.markdown(f"**Ejercicio {i}:** {ejercicio['titulo']}")
                    st.caption(f"Dificultad: {ejercicio['nivel_dificultad']} | "
                             f"Tiempo estimado: {ejercicio['tiempo_estimado']} min")
                    
                    with st.expander(f"Ver enunciado del ejercicio {i}"):
                        st.write(ejercicio['enunciado'])
                    
                    st.divider()
            
            # Botones de exportación
            st.subheader("📤 Exportar Prueba")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generar PDF", key="generate_pdf"):
                    st.info("Generación de PDF en desarrollo...")
                    
            with col2:
                if st.button("📝 Generar LaTeX", key="generate_latex"):
                    st.info("Generación de LaTeX en desarrollo...")
        else:
            st.info("👆 Configura los parámetros y presiona 'Generar Prueba' para ver la vista previa")

if __name__ == "__main__":
    main()