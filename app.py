"""
Sistema de Gestión de Ejercicios - Señales y Sistemas
Aplicación principal con Streamlit
Patricio de la Cuadra - PUC Chile
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
from typing import List, Dict

# Importar el gestor de base de datos
# from database.db_manager import DatabaseManager

# Configuración de la página
st.set_page_config(
    page_title="Gestión Ejercicios SyS",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Inicializar la base de datos (simulada para el prototipo)
@st.cache_resource
def init_database():
    """Inicializa la conexión a la base de datos"""
    # Aquí iría: return DatabaseManager()
    return "Database connection placeholder"

@st.cache_data
def load_sample_data():
    """Carga datos de ejemplo para el prototipo"""
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

# Funciones auxiliares
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

# Sidebar para navegación
def setup_sidebar():
    """Configura el sidebar de navegación"""
    st.sidebar.markdown("## 📚 Gestión de Ejercicios")
    st.sidebar.markdown("**Señales y Sistemas**")
    st.sidebar.markdown("---")
    
    menu_options = [
        "🏠 Dashboard",
        "➕ Agregar Ejercicio", 
        "🔍 Buscar Ejercicios",
        "🎯 Generar Prueba",
        "📊 Estadísticas",
        "⚙️ Configuración"
    ]
    
    return st.sidebar.selectbox("Navegación", menu_options)

# Páginas principales
def show_dashboard():
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

def show_add_exercise():
    """Página para agregar nuevo ejercicio"""
    st.markdown('<h1 class="main-header">➕ Agregar Nuevo Ejercicio</h1>', 
                unsafe_allow_html=True)
    
    with st.form("nuevo_ejercicio"):
        # Información básica
        st.subheader("📝 Información Básica")
        col1, col2 = st.columns(2)
        
        with col1:
            titulo = st.text_input("Título del Ejercicio*", placeholder="Ej: Convolución de señales...")
            fuente = st.text_input("Fuente", placeholder="Ej: Libro Pablo Alvarado, Creación propia")
            
        with col2:
            año_creacion = st.number_input("Año de Creación", min_value=2020, max_value=2030, value=2024)
            palabras_clave = st.text_input("Palabras Clave", placeholder="Separadas por comas")
        
        # Clasificación temática
        st.subheader("📚 Clasificación Temática")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unidades = ["Introducción", "Sistemas Continuos", "Transformada de Fourier", 
                       "Transformada de Laplace", "Sistemas Discretos", 
                       "Transformada de Fourier Discreta", "Transformada Z"]
            unidad_tematica = st.selectbox("Unidad Temática*", unidades)
            
        with col2:
            dificultades = ["Básico", "Intermedio", "Avanzado", "Desafío"]
            nivel_dificultad = st.selectbox("Nivel de Dificultad*", dificultades)
            
        with col3:
            modalidades = ["Teórico", "Computacional", "Mixto"]
            modalidad = st.selectbox("Modalidad*", modalidades)
        
        subtemas = st.text_input("Subtemas", placeholder="Ej: Convolución, Linealidad (separados por comas)")
        tiempo_estimado = st.number_input("Tiempo Estimado (minutos)", min_value=5, max_value=120, value=15)
        
        # Uso pedagógico
        st.subheader("🎯 Uso Pedagógico")
        tipos_actividad = st.multiselect(
            "Tipos de Actividad",
            ["Prueba/Interrogación", "Tarea", "Ayudantía", "Clase", "Control", "Examen", "Quiz"]
        )
        
        objetivos_curso = st.multiselect(
            "Objetivos del Curso que aborda",
            ["1. Reconocer y clasificar señales/sistemas", 
             "2. Aplicar convolución e impulso",
             "3. Muestreo y reconstrucción", 
             "4. Análisis en frecuencia",
             "5. Transformadas matemáticas", 
             "6. Funciones de transferencia"]
        )
        
        # Contenido
        st.subheader("📄 Contenido")
        enunciado = st.text_area("Enunciado del Ejercicio*", height=150)
        datos_entrada = st.text_area("Datos de Entrada", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            solucion_completa = st.text_area("Solución Completa", height=200)
        with col2:
            respuesta_final = st.text_area("Respuesta Final", height=100)
            codigo_python = st.text_area("Código Python (si aplica)", height=100)
        
        # Metadatos adicionales
        st.subheader("🔧 Información Adicional")
        col1, col2 = st.columns(2)
        
        with col1:
            prerrequisitos = st.text_area("Prerrequisitos")
            comentarios_docente = st.text_area("Comentarios del Docente")
            
        with col2:
            errores_comunes = st.text_area("Errores Comunes de Estudiantes")
            hints = st.text_area("Pistas/Hints")
        
        # Botón de envío
        submitted = st.form_submit_button("💾 Guardar Ejercicio", type="primary")
        
        if submitted:
            if titulo and unidad_tematica and enunciado:
                # Aquí iría la lógica para guardar en la base de datos
                st.success("✅ Ejercicio guardado exitosamente!")
                st.balloons()
                
                # Mostrar resumen
                with st.expander("📋 Resumen del ejercicio creado"):
                    st.write(f"**Título:** {titulo}")
                    st.write(f"**Unidad:** {unidad_tematica}")
                    st.write(f"**Dificultad:** {nivel_dificultad}")
                    st.write(f"**Modalidad:** {modalidad}")
                    st.write(f"**Tiempo estimado:** {tiempo_estimado} minutos")
            else:
                st.error("❌ Por favor completa los campos obligatorios (marcados con *)")

def show_search_exercises():
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
    
    # Mostrar resultados
    st.subheader("📋 Resultados de la Búsqueda")
    
    sample_data = load_sample_data()
    
    # Aplicar filtros (simulado)
    ejercicios_filtrados = sample_data
    
    if filtro_unidad != "Todas":
        ejercicios_filtrados = [e for e in ejercicios_filtrados if e['unidad_tematica'] == filtro_unidad]
    
    if filtro_dificultad != "Todas":
        ejercicios_filtrados = [e for e in ejercicios_filtrados if e['nivel_dificultad'] == filtro_dificultad]
    
    if filtro_modalidad != "Todas":
        ejercicios_filtrados = [e for e in ejercicios_filtrados if e['modalidad'] == filtro_modalidad]
    
    # Mostrar ejercicios
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
                        st.write(f"**Fecha de creación:** {exercise['fecha_creacion']}")
                        
                        if st.button("❌ Cerrar", key=f"close_{exercise['id']}"):
                            st.session_state[f"show_detail_{exercise['id']}"] = False
                            st.experimental_rerun()
                
                st.divider()
    else:
        st.warning("No se encontraron ejercicios con los filtros seleccionados")

def show_generate_test():
    """Página para generar pruebas"""
    st.markdown('<h1 class="main-header">🎯 Generador de Pruebas</h1>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚙️ Configuración de la Prueba")
        
        # Información general
        nombre_prueba = st.text_input("Nombre de la Prueba", "Interrogación 1 - SyS")
        semestre = st.text_input("Semestre", "2024-2")
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
                # Aquí iría la lógica de generación
                st.success("✅ Prueba generada exitosamente!")
                
                # Simular ejercicios seleccionados
                sample_data = load_sample_data()
                ejercicios_seleccionados = sample_data[:min(num_ejercicios, len(sample_data))]
                
                st.session_state['ejercicios_seleccionados'] = ejercicios_seleccionados
                st.session_state['config_prueba'] = {
                    'nombre': nombre_prueba,
                    'semestre': semestre,
                    'fecha': fecha_prueba,
                    'tiempo_total': tiempo_total
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

def show_statistics():
    """Página de estadísticas"""
    st.markdown('<h1 class="main-header">📊 Estadísticas</h1>', 
                unsafe_allow_html=True)
    
    # Métricas generales
    st.subheader("📈 Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Ejercicios", "3")
    with col2:
        st.metric("Promedio Dificultad", "Intermedio")
    with col3:
        st.metric("Tiempo Promedio", "25 min")
    with col4:
        st.metric("Más Usado", "Sistemas Continuos")
    
    # Gráficos de distribución
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Distribución por Unidad")
        # Datos de ejemplo
        unidades_data = pd.DataFrame({
            'Unidad': ['Sistemas Continuos', 'DFT', 'Transformada Z'],
            'Cantidad': [1, 1, 1]
        })
        st.bar_chart(unidades_data.set_index('Unidad'))
        
    with col2:
        st.subheader("🎯 Distribución por Dificultad")
        dificultad_data = pd.DataFrame({
            'Dificultad': ['Básico', 'Intermedio', 'Avanzado'],
            'Cantidad': [1, 1, 1]
        })
        st.bar_chart(dificultad_data.set_index('Dificultad'))
    
    # Tabla de ejercicios más utilizados
    st.subheader("🔥 Ejercicios Más Utilizados")
    sample_data = load_sample_data()
    df = pd.DataFrame(sample_data)
    st.dataframe(
        df[['titulo', 'unidad_tematica', 'nivel_dificultad', 'modalidad']],
        use_container_width=True
    )

def show_settings():
    """Página de configuración"""
    st.markdown('<h1 class="main-header">⚙️ Configuración</h1>', 
                unsafe_allow_html=True)
    
    # Configuración general
    st.subheader("🔧 Configuración General")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Nombre del Profesor", value="Patricio de la Cuadra")
        st.text_input("Curso", value="IEE2103 - Señales y Sistemas")
        st.text_input("Universidad", value="Pontificia Universidad Católica de Chile")
        
    with col2:
        st.text_input("Semestre Actual", value="2024-2")
        st.text_input("Email", value="pcuadra@uc.cl")
        st.selectbox("Idioma", ["Español", "English"])
    
    # Configuración de exportación
    st.subheader("📄 Configuración de Exportación")
    
    st.text_input("Template LaTeX", value="template_prueba.tex")
    st.checkbox("Incluir logo UC", value=True)
    st.checkbox("Numerar ejercicios automáticamente", value=True)
    st.checkbox("Incluir fecha en documentos", value=True)
    
    # Configuración de base de datos
    st.subheader("💾 Base de Datos")
    
    st.text_input("Ruta de Base de Datos", value="database/ejercicios.db")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Crear Backup"):
            st.success("Backup creado exitosamente")
    with col2:
        if st.button("📥 Importar Datos"):
            st.info("Función de importación en desarrollo")
    with col3:
        if st.button("📤 Exportar Datos"):
            st.info("Función de exportación en desarrollo")

# Función principal
def main():
    """Función principal de la aplicación"""
    
    # Inicializar la base de datos
    db = init_database()
    
    # Configurar sidebar
    selected_page = setup_sidebar()
    
    # Mostrar información del sistema en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Estado del Sistema")
    st.sidebar.info("✅ Base de datos conectada")
    st.sidebar.info("📚 3 ejercicios disponibles")
    
    # Navegación entre páginas
    if selected_page == "🏠 Dashboard":
        show_dashboard()
    elif selected_page == "➕ Agregar Ejercicio":
        show_add_exercise()
    elif selected_page == "🔍 Buscar Ejercicios":
        show_search_exercises()
    elif selected_page == "🎯 Generar Prueba":
        show_generate_test()
    elif selected_page == "📊 Estadísticas":
        show_statistics()
    elif selected_page == "⚙️ Configuración":
        show_settings()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Sistema de Gestión de Ejercicios**")
    st.sidebar.markdown("*Señales y Sistemas - PUC*")
    st.sidebar.markdown("v1.0.0 - Prototipo")

# Ejecutar la aplicación
if __name__ == "__main__":
    main()