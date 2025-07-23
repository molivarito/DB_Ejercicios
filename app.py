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
import logging
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

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        "📥 Importar LaTeX",
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

def show_latex_import():
    """Página para importar ejercicios desde LaTeX - VERSIÓN CON PARSER REAL"""
    st.markdown('<h1 class="main-header">📥 Importar Ejercicios desde LaTeX</h1>', 
                unsafe_allow_html=True)
    
    # Importar componentes reales
    try:
        from utils.latex_parser import LaTeXParser, ParseError
        from database.db_manager import DatabaseManager, DatabaseError
        parser_available = True
    except ImportError as e:
        st.error(f"❌ Error cargando componentes: {str(e)}")
        st.info("🔧 Ejecutando en modo de desarrollo - usando simulación")
        parser_available = False
    
    # Inicializar componentes
    if parser_available:
        if 'latex_parser' not in st.session_state:
            st.session_state.latex_parser = LaTeXParser()
        if 'db_manager' not in st.session_state:
            try:
                st.session_state.db_manager = DatabaseManager()
                st.success("✅ Conexión a base de datos establecida")
            except Exception as e:
                st.error(f"❌ Error conectando a base de datos: {str(e)}")
                parser_available = False
    
    st.info("""
    **🚀 Importador LaTeX Avanzado**
    
    **Patrones detectados automáticamente:**
    - `\\begin{ejercicio}...\\end{ejercicio}` (Confianza: 90%)
    - `\\begin{problem}...\\end{problem}` (Confianza: 90%)  
    - Secciones con ejercicios (Confianza: 80%)
    - Listas enumerate con \\item (Confianza: 70%)
    - Contenido genérico (Confianza: 40%)
    
    **Metadatos extraídos automáticamente:**
    - Comentarios: `% Dificultad: Intermedio`, `% Unidad: Fourier`, `% Tiempo: 25`
    - Soluciones: `\\begin{solucion}...`, `\\ifanswers...\\fi`
    - Clasificación automática por palabras clave
    """)
    
    # Estadísticas del sistema
    if parser_available:
        with st.expander("📊 Estadísticas del Sistema"):
            col1, col2, col3, col4 = st.columns(4)
            
            try:
                import_history = st.session_state.db_manager.get_import_history(10)
                exercises_needing_review = st.session_state.db_manager.get_exercises_needing_review()
                
                with col1:
                    st.metric("Importaciones Recientes", len(import_history))
                with col2:
                    total_imported = sum(imp.get('ejercicios_exitosos', 0) for imp in import_history)
                    st.metric("Total Importados", total_imported)
                with col3:
                    st.metric("Requieren Revisión", len(exercises_needing_review))
                with col4:
                    avg_confidence = sum(imp.get('porcentaje_exito', 0) for imp in import_history) / max(len(import_history), 1)
                    st.metric("Precisión Promedio", f"{avg_confidence:.1f}%")
                    
            except Exception as e:
                st.warning(f"No se pudieron cargar las estadísticas: {str(e)}")
    
    # Interfaz principal de importación
    st.subheader("🔄 Importador de Ejercicios LaTeX")
    
    # Pestañas para diferentes métodos
    tab1, tab2, tab3 = st.tabs(["📁 Subir Archivo", "📝 Pegar Código", "📋 Batch Import"])
    
    with tab1:
        st.markdown("### 📁 Subir Archivo LaTeX")
        
        uploaded_files = st.file_uploader(
            "Selecciona archivo(s) .tex",
            type=['tex', 'txt'],
            accept_multiple_files=True,
            help="Sube uno o más archivos LaTeX con ejercicios"
        )
        
        if uploaded_files:
            exercises_found = []
            
            for uploaded_file in uploaded_files:
                st.markdown(f"**📄 Procesando: {uploaded_file.name}**")
                
                try:
                    content = str(uploaded_file.read(), "utf-8")
                    
                    with st.expander(f"👀 Vista previa - {uploaded_file.name}"):
                        st.code(content[:1000] + "..." if len(content) > 1000 else content, 
                                language="latex")
                    
                    if parser_available:
                        with st.spinner(f"🔄 Parseando {uploaded_file.name}..."):
                            try:
                                file_exercises = st.session_state.latex_parser.parse_file(content)
                                exercises_found.extend([(ex, uploaded_file.name) for ex in file_exercises])
                                
                                if file_exercises:
                                    st.success(f"✅ {len(file_exercises)} ejercicios encontrados en {uploaded_file.name}")
                                else:
                                    st.warning(f"⚠️ No se encontraron ejercicios en {uploaded_file.name}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error parseando {uploaded_file.name}: {str(e)}")
                    else:
                        # Simulación para desarrollo
                        simulated_exercises = [
                            {
                                'titulo': f'Ejercicio simulado de {uploaded_file.name}',
                                'enunciado': 'Ejercicio simulado para desarrollo...',
                                'nivel_dificultad': 'Intermedio',
                                'unidad_tematica': 'Sistemas Continuos',
                                'tiempo_estimado': 20,
                                'modalidad': 'Teórico',
                                'confidence_score': 0.8,
                                'pattern_used': 'simulado'
                            }
                        ]
                        exercises_found.extend([(ex, uploaded_file.name) for ex in simulated_exercises])
                        st.info(f"🔧 Modo simulación: 1 ejercicio simulado de {uploaded_file.name}")
                    
                except UnicodeDecodeError:
                    st.error(f"❌ Error de codificación en {uploaded_file.name}. Verifica que sea UTF-8.")
                except Exception as e:
                    st.error(f"❌ Error procesando {uploaded_file.name}: {str(e)}")
            
            # Mostrar resultados consolidados
            if exercises_found:
                show_parsed_exercises_interface(exercises_found, parser_available)
    
    with tab2:
        st.markdown("### 📝 Pegar Código LaTeX")
        
        latex_content = st.text_area(
            "Pega tu código LaTeX aquí:",
            height=300,
            placeholder="""\\begin{ejercicio}
% Dificultad: Intermedio
% Unidad: Sistemas Continuos
% Tiempo: 25
Calcule la convolución y(t) = x(t) * h(t) donde:
\\begin{enumerate}
\\item x(t) = rect(t/2)  
\\item h(t) = δ(t-1)
\\end{enumerate}

\\begin{solucion}
La convolución resulta en...
\\end{solucion}
\\end{ejercicio}"""
        )
        
        if latex_content and st.button("🔄 Procesar Código LaTeX"):
            if parser_available:
                with st.spinner("🔄 Parseando código LaTeX..."):
                    try:
                        exercises = st.session_state.latex_parser.parse_file(latex_content)
                        if exercises:
                            exercises_with_source = [(ex, "entrada_manual") for ex in exercises]
                            show_parsed_exercises_interface(exercises_with_source, parser_available)
                        else:
                            st.warning("⚠️ No se encontraron ejercicios en el código proporcionado")
                    except Exception as e:
                        st.error(f"❌ Error parseando código: {str(e)}")
            else:
                # Simulación para desarrollo
                simulated_exercise = {
                    'titulo': 'Ejercicio de entrada manual',
                    'enunciado': latex_content[:200] + "..." if len(latex_content) > 200 else latex_content,
                    'nivel_dificultad': 'Intermedio',
                    'unidad_tematica': 'Por determinar',
                    'tiempo_estimado': 20,
                    'modalidad': 'Teórico',
                    'confidence_score': 0.7,
                    'pattern_used': 'manual_input'
                }
                exercises_with_source = [(simulated_exercise, "entrada_manual")]
                show_parsed_exercises_interface(exercises_with_source, parser_available)
    
    with tab3:
        st.markdown("### 📋 Importación Masiva")
        
        if parser_available:
            st.info("💡 **Importación Batch**: Sube múltiples archivos para procesamiento automático")
            
            batch_files = st.file_uploader(
                "Selecciona múltiples archivos LaTeX",
                type=['tex', 'txt'],
                accept_multiple_files=True,
                key="batch_upload"
            )
            
            if batch_files:
                st.write(f"📁 **{len(batch_files)} archivos seleccionados**")
                
                # Configuración de batch import
                col1, col2 = st.columns(2)
                with col1:
                    auto_import = st.checkbox("🤖 Importar automáticamente (confianza > 70%)", value=True)
                    skip_duplicates = st.checkbox("🔄 Saltar posibles duplicados", value=True)
                    
                with col2:
                    confidence_threshold = st.slider("🎯 Umbral de confianza mínimo", 0.0, 1.0, 0.5, 0.1)
                    review_low_confidence = st.checkbox("👁️ Marcar baja confianza para revisión", value=True)
                
                if st.button("🚀 Ejecutar Importación Masiva", type="primary"):
                    execute_batch_import(batch_files, auto_import, confidence_threshold, 
                                       skip_duplicates, review_low_confidence, parser_available)
        else:
            st.warning("🔧 Importación masiva requiere parser funcional")
    
    # Sección de ayuda y configuración
    with st.expander("💡 Guía de Uso y Configuración"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📖 Formatos Soportados:**
            
            **Ejercicios con Environment:**
            ```latex
            \\begin{ejercicio}
            % Dificultad: Intermedio
            Contenido del ejercicio...
            \\end{ejercicio}
            ```
            
            **Soluciones:**
            ```latex
            \\begin{solucion}
            Solución del ejercicio...
            \\end{solucion}
            ```
            
            **Metadatos en Comentarios:**
            ```latex
            % Dificultad: Básico/Intermedio/Avanzado/Desafío
            % Unidad: Sistemas Continuos
            % Tiempo: 25
            % Modalidad: Teórico/Computacional/Mixto
            ```
            """)
        
        with col2:
            st.markdown("""
            **🔧 Configuración de Parser:**
            
            **Palabras Clave Automáticas:**
            - "convolución" → Sistemas Continuos
            - "fourier" → Transformada de Fourier  
            - "laplace" → Transformada de Laplace
            - "muestreo" → Sistemas Discretos
            - "dft", "fft" → DFT
            - "transformada z" → Transformada Z
            
            **Niveles de Confianza:**
            - 90%+: Patterns específicos (ejercicio/problem)
            - 70-89%: Secciones organizadas
            - 40-69%: Listas y items
            - <40%: Contenido genérico
            """)

def show_parsed_exercises_interface(exercises_with_source, parser_available):
    """Interfaz para mostrar y gestionar ejercicios parseados"""
    st.subheader("📋 Ejercicios Encontrados")
    
    if not exercises_with_source:
        st.warning("No se encontraron ejercicios para mostrar")
        return
    
    # Estadísticas rápidas
    total_exercises = len(exercises_with_source)
    if parser_available:
        confidence_scores = [ex[0].confidence_score for ex in exercises_with_source]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        high_confidence = sum(1 for score in confidence_scores if score > 0.7)
    else:
        # Simulación para desarrollo
        confidence_scores = [ex[0].get('confidence_score', 0.7) for ex in exercises_with_source]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        high_confidence = sum(1 for score in confidence_scores if score > 0.7)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ejercicios", total_exercises)
    with col2:
        st.metric("Confianza Promedio", f"{avg_confidence:.1%}")
    with col3:
        st.metric("Alta Confianza (>70%)", f"{high_confidence}/{total_exercises}")
    with col4:
        ready_to_import = sum(1 for ex, _ in exercises_with_source if (ex.confidence_score if hasattr(ex, 'confidence_score') else ex.get('confidence_score', 0.7)) > 0.5)
    
    # Filtros para los ejercicios
    col1, col2, col3 = st.columns(3)
    with col1:
        confidence_filter = st.selectbox(
            "Filtrar por Confianza",
            ["Todos", "Alta (>70%)", "Media (50-70%)", "Baja (<50%)"]
        )
    with col2:
        if parser_available:
            unit_filter = st.selectbox(
                "Filtrar por Unidad",
                ["Todas"] + list(set(ex[0].unidad_tematica for ex in exercises_with_source))
            )
        else:
            unit_filter = st.selectbox(
                "Filtrar por Unidad",
                ["Todas"] + list(set(ex[0].get('unidad_tematica', 'Por determinar') for ex in exercises_with_source))
            )
    with col3:
        if parser_available:
            pattern_filter = st.selectbox(
                "Filtrar por Patrón",
                ["Todos"] + list(set(ex[0].pattern_used for ex in exercises_with_source))
            )
        else:
            pattern_filter = st.selectbox(
                "Filtrar por Patrón",
                ["Todos"] + list(set(ex[0].get('pattern_used', 'simulado') for ex in exercises_with_source))
            )
    
    # Aplicar filtros
    filtered_exercises = exercises_with_source
    
    if confidence_filter != "Todos":
        if confidence_filter == "Alta (>70%)":
            filtered_exercises = [(ex, src) for ex, src in filtered_exercises if ex.get('confidence_score', 0.7) > 0.7]
        elif confidence_filter == "Media (50-70%)":
            filtered_exercises = [(ex, src) for ex, src in filtered_exercises if 0.5 <= ex.get('confidence_score', 0.7) <= 0.7]
        elif confidence_filter == "Baja (<50%)":
            filtered_exercises = [(ex, src) for ex, src in filtered_exercises if ex.get('confidence_score', 0.7) < 0.5]
    
    if unit_filter != "Todas":
        if parser_available:
            filtered_exercises = [(ex, src) for ex, src in filtered_exercises if ex.unidad_tematica == unit_filter]
        else:
            filtered_exercises = [(ex, src) for ex, src in filtered_exercises if ex.get('unidad_tematica', 'Por determinar') == unit_filter]
    
    if pattern_filter != "Todos":
        if parser_available:
            filtered_exercises = [(ex, src) for ex, src in filtered_exercises if ex.pattern_used == pattern_filter]
        else:
            filtered_exercises = [(ex, src) for ex, src in filtered_exercises if ex.get('pattern_used', 'simulado') == pattern_filter]
    
    st.write(f"**Mostrando {len(filtered_exercises)} de {total_exercises} ejercicios**")
    
    # Selección de ejercicios para importar
    if filtered_exercises:
        st.markdown("### ✅ Seleccionar Ejercicios para Importar")
        
        # Opción de seleccionar todos
        select_all = st.checkbox("Seleccionar todos los ejercicios mostrados", value=True)
        
        selected_exercises = []
        
        for i, (exercise, source_file) in enumerate(filtered_exercises):
            # Manejo de atributos tanto para ParsedExercise como para dict
            if parser_available:
                titulo = exercise.titulo
                confianza = exercise.confidence_score
                unidad = exercise.unidad_tematica
                tiempo = exercise.tiempo_estimado
                enunciado = exercise.enunciado
                solucion = getattr(exercise, 'solucion', None)
                dificultad = exercise.nivel_dificultad
                modalidad = exercise.modalidad
                pattern = exercise.pattern_used
                palabras_clave = getattr(exercise, 'palabras_clave', [])
            else:
                titulo = exercise.get('titulo', f'Ejercicio {i+1}')
                confianza = exercise.get('confidence_score', 0.7)
                unidad = exercise.get('unidad_tematica', 'Por determinar')
                tiempo = exercise.get('tiempo_estimado', 20)
                enunciado = exercise.get('enunciado', 'Enunciado simulado...')
                solucion = exercise.get('solucion', None)
                dificultad = exercise.get('nivel_dificultad', 'Intermedio')
                modalidad = exercise.get('modalidad', 'Teórico')
                pattern = exercise.get('pattern_used', 'simulado')
                palabras_clave = exercise.get('palabras_clave', [])
            
            with st.expander(
                f"📝 **{titulo}** | "
                f"🎯 {confianza:.1%} | "
                f"📚 {unidad} | "
                f"⏱️ {tiempo}min",
                expanded=False
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Mostrar información del ejercicio
                    st.markdown("**📖 Enunciado:**")
                    st.write(enunciado[:500] + "..." if len(enunciado) > 500 else enunciado)
                    
                    if solucion:
                        with st.expander("👁️ Ver Solución"):
                            st.write(solucion[:300] + "..." if len(solucion) > 300 else solucion)
                
                with col2:
                    # Metadatos y configuración
                    st.markdown("**📊 Metadatos:**")
                    st.write(f"**Archivo:** {source_file}")
                    st.write(f"**Patrón:** {pattern}")
                    st.write(f"**Confianza:** {confianza:.1%}")
                    st.write(f"**Dificultad:** {dificultad}")
                    st.write(f"**Modalidad:** {modalidad}")
                    
                    if palabras_clave:
                        st.write(f"**Keywords:** {', '.join(palabras_clave)}")
                    
                    # Opción de editar metadatos
                    if st.button(f"✏️ Editar", key=f"edit_{i}"):
                        st.session_state[f"editing_{i}"] = True
                        st.experimental_rerun()
                
                # Interfaz de edición (si está activa)
                if st.session_state.get(f"editing_{i}", False):
                    st.markdown("**✏️ Editar Metadatos:**")
                    
                    col1_edit, col2_edit = st.columns(2)
                    with col1_edit:
                        new_title = st.text_input("Título", value=titulo, key=f"title_{i}")
                        new_unit = st.selectbox(
                            "Unidad Temática",
                            ["Introducción", "Sistemas Continuos", "Transformada de Fourier", 
                             "Transformada de Laplace", "Sistemas Discretos", 
                             "Transformada de Fourier Discreta", "Transformada Z"],
                            index=["Introducción", "Sistemas Continuos", "Transformada de Fourier", 
                                   "Transformada de Laplace", "Sistemas Discretos", 
                                   "Transformada de Fourier Discreta", "Transformada Z"].index(unidad) if unidad in ["Introducción", "Sistemas Continuos", "Transformada de Fourier", "Transformada de Laplace", "Sistemas Discretos", "Transformada de Fourier Discreta", "Transformada Z"] else 0,
                            key=f"unit_{i}"
                        )
                        new_difficulty = st.selectbox(
                            "Dificultad",
                            ["Básico", "Intermedio", "Avanzado", "Desafío"],
                            index=["Básico", "Intermedio", "Avanzado", "Desafío"].index(dificultad) if dificultad in ["Básico", "Intermedio", "Avanzado", "Desafío"] else 1,
                            key=f"diff_{i}"
                        )
                    
                    with col2_edit:
                        new_modality = st.selectbox(
                            "Modalidad",
                            ["Teórico", "Computacional", "Mixto"],
                            index=["Teórico", "Computacional", "Mixto"].index(modalidad) if modalidad in ["Teórico", "Computacional", "Mixto"] else 0,
                            key=f"mod_{i}"
                        )
                        new_time = st.number_input("Tiempo (min)", value=tiempo, min_value=5, max_value=120, key=f"time_{i}")
                        new_keywords = st.text_input("Palabras clave (separadas por comas)", value=", ".join(palabras_clave), key=f"keywords_{i}")
                    
                    col1_btn, col2_btn = st.columns(2)
                    with col1_btn:
                        if st.button(f"💾 Guardar Cambios", key=f"save_{i}"):
                            # Actualizar el ejercicio con los nuevos valores
                            if parser_available:
                                exercise.titulo = new_title
                                exercise.unidad_tematica = new_unit
                                exercise.nivel_dificultad = new_difficulty
                                exercise.modalidad = new_modality
                                exercise.tiempo_estimado = new_time
                                exercise.palabras_clave = [kw.strip() for kw in new_keywords.split(',') if kw.strip()]
                            else:
                                exercise['titulo'] = new_title
                                exercise['unidad_tematica'] = new_unit
                                exercise['nivel_dificultad'] = new_difficulty
                                exercise['modalidad'] = new_modality
                                exercise['tiempo_estimado'] = new_time
                                exercise['palabras_clave'] = [kw.strip() for kw in new_keywords.split(',') if kw.strip()]
                            
                            st.session_state[f"editing_{i}"] = False
                            st.success("✅ Cambios guardados")
                            st.experimental_rerun()
                    
                    with col2_btn:
                        if st.button(f"❌ Cancelar", key=f"cancel_{i}"):
                            st.session_state[f"editing_{i}"] = False
                            st.experimental_rerun()
                
                # Checkbox para seleccionar este ejercicio
                if select_all or st.checkbox(f"Incluir en importación", value=select_all, key=f"select_{i}"):
                    selected_exercises.append((exercise, source_file))
        
        # Botón de importación
        if selected_exercises:
            st.markdown("### 💾 Importar a Base de Datos")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                import_mode = st.selectbox(
                    "Modo de Importación",
                    ["Importar seleccionados", "Solo alta confianza (>70%)", "Importar todos"]
                )
            with col2:
                mark_for_review = st.checkbox("Marcar baja confianza para revisión", value=True)
            with col3:
                create_backup = st.checkbox("Crear backup antes de importar", value=True)
            
            if st.button("💾 Confirmar Importación", type="primary"):
                execute_import(selected_exercises, import_mode, mark_for_review, create_backup, parser_available)
        
        elif not parser_available:
            st.info("🔧 Parser no disponible - mostrando vista previa de importación")
            if filtered_exercises:
                st.json({
                    "ejercicios_seleccionados": len(filtered_exercises),
                    "preview": [{"titulo": ex[0].get('titulo', 'Sin título'), "confianza": ex[0].get('confidence_score', 0.7)} for ex in filtered_exercises[:3]]
                })

def execute_import(selected_exercises, import_mode, mark_for_review, create_backup, parser_available):
    """Ejecuta la importación de ejercicios seleccionados"""
    try:
        # Filtrar ejercicios según el modo
        if import_mode == "Solo alta confianza (>70%)":
            exercises_to_import = [(ex, src) for ex, src in selected_exercises if ex.get('confidence_score', 0.7) > 0.7]
        elif import_mode == "Importar todos":
            exercises_to_import = selected_exercises
        else:  # "Importar seleccionados"
            exercises_to_import = selected_exercises
        
        if not exercises_to_import:
            st.warning("⚠️ No hay ejercicios para importar con los criterios seleccionados")
            return
        
        # Crear backup si se solicita
        if create_backup:
            with st.spinner("📦 Creando backup..."):
                # Aquí iría la lógica de backup
                st.info("✅ Backup creado exitosamente")
        
        # Ejecutar importación
        with st.spinner(f"💾 Importando {len(exercises_to_import)} ejercicios..."):
            
            if parser_available:
                # Marcar ejercicios para revisión si tienen baja confianza
                if mark_for_review:
                    for exercise, _ in exercises_to_import:
                        if exercise.confidence_score < 0.7:
                            exercise.necesita_revision = True
                
                # Obtener solo los ejercicios (sin source_file)
                exercises_only = [ex for ex, _ in exercises_to_import]
                
                # Ejecutar importación batch
                result = st.session_state.db_manager.batch_import_exercises(
                    exercises_only,
                    archivo_origen="importacion_interfaz_streamlit"
                )
                
                # Mostrar resultados
                st.success(f"🎉 Importación completada!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Exitosos", result['ejercicios_exitosos'])
                with col2:
                    st.metric("❌ Fallidos", result['ejercicios_fallidos'])
                with col3:
                    success_rate = (result['ejercicios_exitosos'] / result['total_ejercicios']) * 100
                    st.metric("📊 Tasa de Éxito", f"{success_rate:.1f}%")
                
                # Mostrar errores si los hay
                if result['errores']:
                    with st.expander(f"⚠️ Ver {len(result['errores'])} errores"):
                        for error in result['errores']:
                            st.error(f"**{error['titulo']}**: {error['error']}")
                
                # Mostrar IDs insertados
                if result['ids_insertados']:
                    with st.expander(f"📋 IDs de ejercicios creados ({len(result['ids_insertados'])})"):
                        st.write(", ".join(map(str, result['ids_insertados'])))
                
            else:
                # Simulación para desarrollo
                st.success(f"🎉 Simulación de importación completada!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Exitosos", len(exercises_to_import))
                with col2:
                    st.metric("❌ Fallidos", 0)
                with col3:
                    st.metric("📊 Tasa de Éxito", "100%")
                
                st.info("🔧 En modo de desarrollo - datos no guardados en base real")
            
            st.balloons()
            
            # Limpiar estado
            st.info("💡 Los ejercicios están ahora disponibles en 'Buscar Ejercicios'")
            
    except Exception as e:
        st.error(f"❌ Error inesperado durante la importación: {str(e)}")
        logger.error(f"Error en importación: {str(e)}")

def execute_batch_import(batch_files, auto_import, confidence_threshold, skip_duplicates, review_low_confidence, parser_available):
    """Ejecuta importación masiva de múltiples archivos"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()
    
    total_files = len(batch_files)
    all_results = []
    
    try:
        for i, uploaded_file in enumerate(batch_files):
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"Procesando {uploaded_file.name} ({i+1}/{total_files})")
            
            try:
                content = str(uploaded_file.read(), "utf-8")
                
                if parser_available:
                    # Parsear archivo
                    exercises = st.session_state.latex_parser.parse_file(content)
                    
                    if exercises:
                        # Filtrar por umbral de confianza
                        filtered_exercises = [ex for ex in exercises if ex.confidence_score >= confidence_threshold]
                        
                        if filtered_exercises and auto_import:
                            # Marcar para revisión si tienen baja confianza
                            if review_low_confidence:
                                for exercise in filtered_exercises:
                                    if exercise.confidence_score < 0.7:
                                        exercise.necesita_revision = True
                            
                            # Importar automáticamente
                            result = st.session_state.db_manager.batch_import_exercises(
                                filtered_exercises,
                                archivo_origen=uploaded_file.name
                            )
                            result['filename'] = uploaded_file.name
                            result['total_parsed'] = len(exercises)
                            result['filtered_out'] = len(exercises) - len(filtered_exercises)
                            all_results.append(result)
                        
                        else:
                            # Solo registrar para revisión manual
                            result = {
                                'filename': uploaded_file.name,
                                'total_parsed': len(exercises),
                                'filtered_out': len(exercises) - len(filtered_exercises),
                                'ejercicios_exitosos': 0,
                                'ejercicios_fallidos': 0,
                                'pending_review': len(filtered_exercises)
                            }
                            all_results.append(result)
                    
                    else:
                        result = {
                            'filename': uploaded_file.name,
                            'total_parsed': 0,
                            'error': 'No se encontraron ejercicios'
                        }
                        all_results.append(result)
                else:
                    # Simulación para desarrollo
                    result = {
                        'filename': uploaded_file.name,
                        'total_parsed': 1,
                        'filtered_out': 0,
                        'ejercicios_exitosos': 1 if auto_import else 0,
                        'ejercicios_fallidos': 0,
                        'pending_review': 0 if auto_import else 1
                    }
                    all_results.append(result)
                    
            except Exception as e:
                result = {
                    'filename': uploaded_file.name,
                    'error': str(e)
                }
                all_results.append(result)
        
        # Mostrar resultados finales
        progress_bar.progress(1.0)
        status_text.text("✅ Procesamiento batch completado")
        
        # Resumen de resultados
        with results_container.container():
            st.markdown("### 📊 Resultados de Importación Batch")
            
            total_parsed = sum(r.get('total_parsed', 0) for r in all_results)
            total_imported = sum(r.get('ejercicios_exitosos', 0) for r in all_results)
            total_failed = sum(r.get('ejercicios_fallidos', 0) for r in all_results)
            total_pending = sum(r.get('pending_review', 0) for r in all_results)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📄 Archivos Procesados", len(all_results))
            with col2:
                st.metric("📝 Total Parseados", total_parsed)
            with col3:
                st.metric("✅ Importados", total_imported)
            with col4:
                st.metric("⏳ Pendientes Revisión", total_pending)
            
            # Tabla detallada de resultados
            st.markdown("### 📋 Detalle por Archivo")
            
            for result in all_results:
                with st.expander(f"📄 {result['filename']}"):
                    if 'error' in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Parseados:** {result.get('total_parsed', 0)}")
                            st.write(f"**Filtrados:** {result.get('filtered_out', 0)}")
                        with col2:
                            st.write(f"**Importados:** {result.get('ejercicios_exitosos', 0)}")
                            st.write(f"**Fallidos:** {result.get('ejercicios_fallidos', 0)}")
                        with col3:
                            st.write(f"**Pendientes:** {result.get('pending_review', 0)}")
                            if result.get('importacion_id'):
                                st.write(f"**ID Importación:** {result['importacion_id']}")
        
        if parser_available:
            st.success(f"🎉 Batch import completado: {total_imported} ejercicios importados de {total_parsed} parseados")
        else:
            st.success(f"🎉 Simulación batch completada: {total_imported} ejercicios simulados")
        
    except Exception as e:
        st.error(f"❌ Error durante importación batch: {str(e)}")
        logger.error(f"Error en batch import: {str(e)}")
    
    finally:
        progress_bar.empty()
        status_text.empty()

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
    
    # Configuración de importación LaTeX
    st.subheader("📥 Configuración de Importación LaTeX")
    
    with st.expander("🔧 Patrones Personalizados"):
        st.write("Define patrones específicos para tus ejercicios:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Comando inicio ejercicio", value="\\begin{ejercicio}")
            st.text_input("Comando fin ejercicio", value="\\end{ejercicio}")
            
        with col2:
            st.text_input("Patrón dificultad", value="% Dificultad:")
            st.text_input("Patrón unidad", value="% Unidad:")
    
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
    elif selected_page == "📥 Importar LaTeX":
        show_latex_import()
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