"""
Agregar Ejercicio
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Agregar Ejercicio - Gestión Ejercicios SyS",
    page_icon="➕",
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

def main():
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
                try:
                    from database.db_manager import DatabaseManager
                    
                    # Preparar datos del ejercicio
                    ejercicio_data = {
                        'titulo': titulo,
                        'fuente': fuente,
                        'año_creacion': año_creacion,
                        'palabras_clave': palabras_clave,
                        'unidad_tematica': unidad_tematica,
                        'nivel_dificultad': nivel_dificultad,
                        'modalidad': modalidad,
                        'subtemas': subtemas,
                        'tiempo_estimado': tiempo_estimado,
                        'enunciado': enunciado,
                        'datos_entrada': datos_entrada,
                        'solucion_completa': solucion_completa,
                        'respuesta_final': respuesta_final,
                        'codigo_python': codigo_python,
                        'prerrequisitos': prerrequisitos,
                        'comentarios_docente': comentarios_docente,
                        'errores_comunes': errores_comunes,
                        'hints': hints
                    }
                    
                    # Guardar en base de datos
                    db_manager = DatabaseManager()
                    ejercicio_id = db_manager.agregar_ejercicio(ejercicio_data)
                    
                    st.success("✅ Ejercicio guardado exitosamente!")
                    st.balloons()
                    
                    # Mostrar resumen
                    with st.expander("📋 Resumen del ejercicio creado"):
                        st.write(f"**ID:** {ejercicio_id}")
                        st.write(f"**Título:** {titulo}")
                        st.write(f"**Unidad:** {unidad_tematica}")
                        st.write(f"**Dificultad:** {nivel_dificultad}")
                        st.write(f"**Modalidad:** {modalidad}")
                        st.write(f"**Tiempo estimado:** {tiempo_estimado} minutos")
                        
                except Exception as e:
                    st.error(f"❌ Error guardando ejercicio: {e}")
                    
            else:
                st.error("❌ Por favor completa los campos obligatorios (marcados con *)")

if __name__ == "__main__":
    main()