"""
Página de Edición de Ejercicios
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
import time
import json

# Importar dependencias del proyecto
try:
    from database.db_manager import DatabaseManager
except ImportError:
    import sys
    sys.path.append('.')
    from database.db_manager import DatabaseManager

@st.cache_resource
def get_db_manager():
    """Carga y cachea una instancia del gestor de la base de datos."""
    return DatabaseManager(db_path="database/ejercicios.db")

def main():
    """Página para editar un ejercicio existente."""
    st.set_page_config(page_title="Editar Ejercicio", page_icon="✏️", layout="wide")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>✏️ Editar Ejercicio</h1>
        <p>Modifica los detalles del ejercicio seleccionado y guarda los cambios en la base de datos.</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Verificar si se ha seleccionado un ejercicio para editar
    if 'exercise_to_edit' not in st.session_state or st.session_state.exercise_to_edit is None:
        st.warning("⚠️ No has seleccionado ningún ejercicio para editar.")
        st.info("Por favor, ve a la 'Consola de Gestión' y selecciona un ejercicio para poder editarlo.")
        if st.button("Ir a la Consola de Gestión"):
            st.switch_page("pages/03_🔍_Buscar_Ejercicios.py")
        return

    # 2. Cargar los datos del ejercicio
    exercise_id = st.session_state.exercise_to_edit
    db_manager = get_db_manager()
    ejercicio = db_manager.obtener_ejercicio_por_id(exercise_id)

    if not ejercicio:
        st.error(f"❌ No se pudo encontrar el ejercicio con ID {exercise_id}.")
        return

    st.subheader(f"Editando: ID {ejercicio['id']} - {ejercicio.get('titulo', 'Sin título')}")

    # 3. Formulario pre-cargado
    with st.form("edit_exercise_form"):
        st.markdown("---")
        st.markdown("#### 📝 Información Principal")
        
        new_titulo = st.text_input("Título", value=ejercicio.get('titulo', ''))
        new_fuente = st.text_input("Fuente", value=ejercicio.get('fuente', ''))
        new_tiempo_estimado = st.number_input("Tiempo Estimado (min)", value=ejercicio.get('tiempo_estimado', 15), min_value=0, step=5)

        st.markdown("---")
        st.markdown("#### 📚 Clasificación")

        unidades = db_manager.obtener_unidades_tematicas()
        unidad_idx = unidades.index(ejercicio.get('unidad_tematica')) if ejercicio.get('unidad_tematica') in unidades else 0
        new_unidad = st.selectbox("Unidad Temática", options=unidades, index=unidad_idx)

        dificultades = ["Básico", "Intermedio", "Avanzado", "Desafío"]
        dificultad_idx = dificultades.index(ejercicio.get('nivel_dificultad')) if ejercicio.get('nivel_dificultad') in dificultades else 0
        new_dificultad = st.selectbox("Nivel de Dificultad", options=dificultades, index=dificultad_idx)

        modalidades = ["Teórico", "Computacional", "Mixto"]
        modalidad_idx = modalidades.index(ejercicio.get('modalidad')) if ejercicio.get('modalidad') in modalidades else 0
        new_modalidad = st.selectbox("Modalidad", options=modalidades, index=modalidad_idx)

        st.markdown("---")
        st.markdown("#### 📄 Contenido (LaTeX)")
        
        new_enunciado = st.text_area("Enunciado", value=ejercicio.get('enunciado', ''), height=300)
        new_solucion = st.text_area("Solución Completa", value=ejercicio.get('solucion_completa', ''), height=300)

        st.markdown("---")
        st.markdown("#### 🧠 Metadatos Pedagógicos (IA)")
        
        new_prerrequisitos = st.text_area("Prerrequisitos", value=ejercicio.get('prerrequisitos', ''), height=100)
        
        submitted = st.form_submit_button("💾 Guardar Cambios", use_container_width=True, type="primary")

        # 4. Lógica de guardado
        if submitted:
            data_to_update = {
                'titulo': new_titulo,
                'fuente': new_fuente,
                'tiempo_estimado': new_tiempo_estimado,
                'unidad_tematica': new_unidad,
                'nivel_dificultad': new_dificultad,
                'modalidad': new_modalidad,
                'enunciado': new_enunciado,
                'solucion_completa': new_solucion,
                'prerrequisitos': new_prerrequisitos,
            }
            
            with st.spinner("Actualizando ejercicio en la base de datos..."):
                success = db_manager.actualizar_ejercicio(exercise_id, data_to_update)
            
            if success:
                st.success(f"¡Ejercicio ID {exercise_id} actualizado exitosamente!")
                st.balloons()
                
                # Limpiar estado y redirigir
                del st.session_state.exercise_to_edit
                time.sleep(2) # Pausa para que el usuario vea el mensaje
                st.switch_page("pages/03_🔍_Buscar_Ejercicios.py")
            else:
                st.error("❌ Hubo un error al actualizar el ejercicio.")

if __name__ == "__main__":
    main()

