"""
Búsqueda de Ejercicios con Selección para Documentos
Página: 03_🔍_Buscar_Ejercicios.py
VERSIÓN FINAL: Corregido el uso de st.dialog y el renderizado de LaTeX.
"""

import streamlit as st
import pandas as pd
import re
from pathlib import Path
from datetime import datetime

# Importar dependencias
try:
    from database.db_manager import DatabaseManager
except ImportError:
    import sys
    sys.path.append('.')
    from database.db_manager import DatabaseManager

# =========================================================================
# ▼▼▼ FUNCIÓN "TRADUCTORA" DE LATEX A MARKDOWN (SIN CAMBIOS) ▼▼▼
# =========================================================================
def convert_latex_to_markdown(text: str) -> str:
    if not text: return ""
    def replace_figure(match):
        content = match.group(0)
        img_match = re.search(r'\\includegraphics\[.*?\]\{(.+?)\}', content)
        if img_match:
            img_path = img_match.group(1)
            return f"\n![Imagen del Ejercicio]({img_path})\n"
        return ""
    text = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', replace_figure, text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{(align|align\*)\}(.*?)\\end\{\1\}', r'$$\n\\begin{aligned}\2\\end{aligned}\n$$', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{(equation|equation\*)\}(.*?)\\end\{\1\}', r'$$\n\2\n$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\n\1\n$$', text, flags=re.DOTALL)
    def process_list(match, list_type='ol'):
        items = match.group(1)
        if list_type == 'ol': processed_items = re.sub(r'\\item', '\n1. ', items).strip()
        else: processed_items = re.sub(r'\\item', '\n* ', items).strip()
        return f"\n{processed_items}\n"
    text = re.sub(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', lambda m: process_list(m, 'ol'), text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', lambda m: process_list(m, 'ul'), text, flags=re.DOTALL)
    return text

def main():
    st.set_page_config(page_title="Buscar Ejercicios", page_icon="🔍", layout="wide")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>🔍 Buscar y Seleccionar Ejercicios</h1>
        <p>Busca, visualiza, edita y selecciona los ejercicios para tus documentos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db = DatabaseManager()
        if 'ejercicios_seleccionados' not in st.session_state:
            st.session_state.ejercicios_seleccionados = []
        
        with st.sidebar:
            st.header("🔍 Filtros de Búsqueda")
            ejercicios = db.obtener_ejercicios()
            unidades = db.obtener_unidades_tematicas()
            unidades_filtro = st.multiselect("🎯 Unidades Temáticas", unidades, default=[])
            dificultades_filtro = st.multiselect("🎚️ Nivel de Dificultad", ["Básico", "Intermedio", "Avanzado", "Desafío"], default=[])
            modalidades_filtro = st.multiselect("💻 Modalidad", ["Teórico", "Computacional", "Mixto"], default=[])
            texto_busqueda = st.text_input("🔎 Buscar en título/contenido", placeholder="Ej: convolución...")
            st.divider()
            st.header("🛒 Ejercicios Seleccionados")
            st.write(f"**Total:** {len(st.session_state.ejercicios_seleccionados)}")
            if st.session_state.ejercicios_seleccionados:
                for i, ej_id in enumerate(st.session_state.ejercicios_seleccionados, 1):
                    ej = next((e for e in ejercicios if e['id'] == ej_id), None)
                    if ej: st.write(f"{i}. {ej.get('titulo', 'Sin título')[:30]}...")
                if st.button("🗑️ Limpiar Selección", use_container_width=True):
                    st.session_state.ejercicios_seleccionados = []; st.rerun()
                if st.button("🎯 Ir a Generar Documento", type="primary", use_container_width=True):
                    st.session_state.ejercicios_para_documento = st.session_state.ejercicios_seleccionados.copy()
                    st.success("✅ ¡Listo! Ve a la página de Generación.")
        
        ejercicios_filtrados = ejercicios
        if unidades_filtro: ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('unidad_tematica') in unidades_filtro]
        if dificultades_filtro: ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('nivel_dificultad') in dificultades_filtro]
        if modalidades_filtro: ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('modalidad') in modalidades_filtro]
        if texto_busqueda:
            texto_lower = texto_busqueda.lower()
            ejercicios_filtrados = [e for e in ejercicios_filtrados if (texto_lower in e.get('titulo', '').lower() or texto_lower in e.get('enunciado', '').lower())]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📚 Total Disponibles", len(ejercicios)); col2.metric("🔍 Filtrados", len(ejercicios_filtrados)); col3.metric("✅ Seleccionados", len(st.session_state.ejercicios_seleccionados))
        st.divider()
        
        if ejercicios_filtrados:
            st.subheader(f"📋 Ejercicios Encontrados ({len(ejercicios_filtrados)})")
            for ejercicio in ejercicios_filtrados:
                mostrar_ejercicio_con_seleccion(ejercicio, db)
        else:
            st.warning("🔍 No se encontraron ejercicios con los filtros aplicados.")
    
    except Exception as e:
        st.error(f"Error: {str(e)}"); import traceback; st.code(traceback.format_exc())

def mostrar_ejercicio_con_seleccion(ejercicio, db: DatabaseManager):
    """Muestra un ejercicio con opción de selección y edición"""
    
    # =========================================================================
    # ▼▼▼ CORRECCIÓN: DEFINIR EL DIÁLOGO DE EDICIÓN COMO UNA FUNCIÓN DECORADA ▼▼▼
    # =========================================================================
    @st.dialog(f"Editando: {ejercicio.get('titulo', '')}", width="large")
    def edit_dialog():
        with st.form(key=f"form_edit_{ejercicio['id']}"):
            st.subheader("📝 Edición de Ejercicio")
            unidades = db.obtener_unidades_tematicas()
            dificultades = ["Básico", "Intermedio", "Avanzado", "Desafío"]
            
            new_titulo = st.text_input("Título", value=ejercicio.get('titulo', ''))
            unidad_idx = unidades.index(ejercicio.get('unidad_tematica')) if ejercicio.get('unidad_tematica') in unidades else 0
            new_unidad = st.selectbox("Unidad", unidades, index=unidad_idx)
            dificultad_idx = dificultades.index(ejercicio.get('nivel_dificultad')) if ejercicio.get('nivel_dificultad') in dificultades else 1
            new_dificultad = st.selectbox("Dificultad", dificultades, index=dificultad_idx)

            new_enunciado = st.text_area("Enunciado (LaTeX)", value=ejercicio.get('enunciado', ''), height=250)
            new_solucion = st.text_area("Solución (LaTeX)", value=ejercicio.get('solucion_completa', ''), height=250)

            # --- GESTIÓN DE IMAGEN ---
            st.divider()
            st.write("**Gestión de Imagen**")
            current_image_path_str = ejercicio.get('imagen_path')
            delete_image = False
            if current_image_path_str:
                image_path = Path(current_image_path_str)
                if image_path.is_file():
                    st.write("Imagen actual:")
                    st.image(str(image_path), use_column_width=True)
                    delete_image = st.checkbox("🗑️ Eliminar imagen actual", key=f"delete_img_{ejercicio['id']}")
                else:
                    st.warning(f"⚠️ No se encontró la imagen en la ruta: `{current_image_path_str}`")
            else:
                st.write("Este ejercicio no tiene imagen asociada.")

            new_image_file = st.file_uploader("Subir nueva imagen (reemplazará la actual)", type=["png", "jpg", "jpeg", "gif"])
            st.divider()

            if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                data_to_update = {'titulo': new_titulo, 'unidad_tematica': new_unidad, 'nivel_dificultad': new_dificultad, 'enunciado': new_enunciado, 'solucion_completa': new_solucion}

                # --- LÓGICA PARA GUARDAR/ELIMINAR IMAGEN ---
                image_path_to_update = current_image_path_str

                if new_image_file:
                    IMAGES_DIR = Path("images")
                    IMAGES_DIR.mkdir(exist_ok=True)
                    dest_path = IMAGES_DIR / new_image_file.name
                    with open(dest_path, "wb") as f:
                        f.write(new_image_file.getbuffer())
                    
                    new_path_str = str(dest_path).replace('\\', '/')
                    image_path_to_update = new_path_str
                    st.toast(f"Nueva imagen '{new_image_file.name}' guardada.")

                    if current_image_path_str and Path(current_image_path_str).exists() and Path(current_image_path_str) != dest_path:
                        Path(current_image_path_str).unlink(missing_ok=True)
                        st.toast(f"Imagen antigua '{Path(current_image_path_str).name}' eliminada.")

                elif delete_image and current_image_path_str:
                    image_path_to_update = None
                    if Path(current_image_path_str).exists():
                        Path(current_image_path_str).unlink(missing_ok=True)
                        st.toast(f"Imagen '{Path(current_image_path_str).name}' eliminada.")

                if image_path_to_update != current_image_path_str:
                    data_to_update['imagen_path'] = image_path_to_update

                if db.actualizar_ejercicio(ejercicio['id'], data_to_update):
                    st.toast("✅ Ejercicio actualizado!", icon="🎉"); st.rerun()
                else:
                    st.error("❌ No se pudo actualizar el ejercicio.")

    with st.container():
        col_check, col_content = st.columns([0.1, 0.9])
        
        with col_check:
            is_selected = st.checkbox("Seleccionar", value=ejercicio['id'] in st.session_state.ejercicios_seleccionados, key=f"check_{ejercicio['id']}", label_visibility="collapsed")
            if is_selected and ejercicio['id'] not in st.session_state.ejercicios_seleccionados:
                st.session_state.ejercicios_seleccionados.append(ejercicio['id'])
            elif not is_selected and ejercicio['id'] in st.session_state.ejercicios_seleccionados:
                st.session_state.ejercicios_seleccionados.remove(ejercicio['id'])
        
        with col_content:
            col_title, col_meta = st.columns([2, 1])
            with col_title: st.markdown(f"### {ejercicio.get('titulo', 'Sin título')}")
            with col_meta:
                if ejercicio.get('unidad_tematica'): st.markdown(f"🎯 **{ejercicio['unidad_tematica']}**")
                if ejercicio.get('nivel_dificultad'):
                    color = {"Básico": "green", "Intermedio": "orange", "Avanzado": "red", "Desafío": "purple"}.get(ejercicio['nivel_dificultad'], "blue")
                    st.markdown(f":{color}[🎚️ {ejercicio['nivel_dificultad']}]")
                if ejercicio.get('tiempo_estimado'): st.markdown(f"⏱️ **{ejercicio['tiempo_estimado']} min**")
            
            if ejercicio.get('enunciado'):
                enunciado_md = convert_latex_to_markdown(ejercicio['enunciado'])
                enunciado_preview = enunciado_md[:250] + ("..." if len(enunciado_md) > 250 else "")
                st.markdown(enunciado_preview, unsafe_allow_html=True)
            
            with st.expander("👁️ Ver detalles completos"):
                # El botón ahora simplemente llama a la función del diálogo
                if st.button("✏️ Editar Ejercicio", key=f"edit_{ejercicio['id']}"):
                    edit_dialog()
                
                st.write("---")
                if ejercicio.get('enunciado'):
                    st.write("**Enunciado completo:**")
                    st.markdown(convert_latex_to_markdown(ejercicio['enunciado']), unsafe_allow_html=True)
                
                # --- VISUALIZACIÓN DE IMAGEN ---
                if ejercicio.get('imagen_path'):
                    image_path = Path(ejercicio['imagen_path'])
                    if image_path.is_file():
                        st.image(str(image_path), caption=f"Imagen: {image_path.name}")
                    else:
                        st.warning(f"⚠️ No se encontró la imagen en la ruta: `{ejercicio['imagen_path']}`")

                if ejercicio.get('solucion_completa'):
                    st.write("**Solución:**")
                    st.markdown(convert_latex_to_markdown(ejercicio['solucion_completa']), unsafe_allow_html=True)
                if ejercicio.get('codigo_python'):
                    st.write("**Código Python:**"); st.code(ejercicio['codigo_python'], language='python')
        
        st.divider()

if __name__ == "__main__":
    main()