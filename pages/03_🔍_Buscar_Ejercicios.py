"""
Búsqueda de Ejercicios con Selección para Documentos
Página: 03_🔍_Buscar_Ejercicios.py
VERSIÓN FINAL: Traductor LaTeX a Markdown mejorado para manejar imágenes y más entornos.
"""

import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Importar dependencias
try:
    from database.db_manager import DatabaseManager
except ImportError:
    import sys
    sys.path.append('.')
    from database.db_manager import DatabaseManager

# =========================================================================
# ▼▼▼ TRADUCTOR LÁTEX A MARKDOWN (VERSIÓN MEJORADA) ▼▼▼
# =========================================================================
def convert_latex_to_markdown(text: str) -> str:
    """
    Traduce comandos de entorno LaTeX comunes a un formato compatible con st.markdown.
    """
    if not text:
        return ""

    # --- MANEJO DE IMÁGENES ---
    # Busca el entorno figure completo, extrae el path de la imagen y lo reemplaza por Markdown
    def replace_figure(match):
        content = match.group(0)
        img_match = re.search(r'\\includegraphics\[.*?\]\{(.+?)\}', content)
        if img_match:
            img_path = img_match.group(1)
            # Streamlit puede mostrar imágenes locales si están en la misma carpeta o subcarpeta
            return f"\n![Imagen del Ejercicio]({img_path})\n"
        return "" # Si no encuentra imagen, elimina el bloque
    text = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', replace_figure, text, flags=re.DOTALL)

    # --- MANEJO DE ENTORNOS MATEMÁTICOS ---
    # Convierte align -> aligned para compatibilidad con KaTeX/Streamlit
    text = re.sub(r'\\begin\{(align|align\*)\}(.*?)\\end\{\1\}', r'$$\n\\begin{aligned}\2\\end{aligned}\n$$', text, flags=re.DOTALL)
    # Convierte equation a bloque matemático
    text = re.sub(r'\\begin\{(equation|equation\*)\}(.*?)\\end\{\1\}', r'$$\n\2\n$$', text, flags=re.DOTALL)
    # Convierte \[ ... \] a bloque matemático
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\n\1\n$$', text, flags=re.DOTALL)

    # --- MANEJO DE LISTAS ---
    def process_list(match, list_type='ol'):
        items = match.group(1)
        if list_type == 'ol':
            processed_items = re.sub(r'\\item', '\n1. ', items).strip()
        else:
            processed_items = re.sub(r'\\item', '\n* ', items).strip()
        return f"\n{processed_items}\n"
    text = re.sub(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', lambda m: process_list(m, 'ol'), text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', lambda m: process_list(m, 'ul'), text, flags=re.DOTALL)

    return text

def main():
    st.set_page_config(
        page_title="Buscar Ejercicios",
        page_icon="🔍",
        layout="wide"
    )
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>🔍 Buscar y Seleccionar Ejercicios</h1>
        <p>Busca ejercicios y selecciona los que quieres incluir en tus documentos</p>
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
                    st.session_state.ejercicios_seleccionados = []
                    st.rerun()
                if st.button("🎯 Ir a Generar Documento", type="primary", use_container_width=True):
                    st.session_state.ejercicios_para_documento = st.session_state.ejercicios_seleccionados.copy()
                    st.success("✅ ¡Listo! Ve a la página de Generación.")
        
        # Aplicar filtros
        ejercicios_filtrados = ejercicios
        if unidades_filtro:
            ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('unidad_tematica') in unidades_filtro]
        if dificultades_filtro:
            ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('nivel_dificultad') in dificultades_filtro]
        if modalidades_filtro:
            ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('modalidad') in modalidades_filtro]
        if texto_busqueda:
            texto_lower = texto_busqueda.lower()
            ejercicios_filtrados = [e for e in ejercicios_filtrados if (texto_lower in e.get('titulo', '').lower() or texto_lower in e.get('enunciado', '').lower())]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📚 Total Disponibles", len(ejercicios))
        col2.metric("🔍 Filtrados", len(ejercicios_filtrados))
        col3.metric("✅ Seleccionados", len(st.session_state.ejercicios_seleccionados))
        st.divider()
        
        if ejercicios_filtrados:
            st.subheader(f"📋 Ejercicios Encontrados ({len(ejercicios_filtrados)})")
            for ejercicio in ejercicios_filtrados:
                mostrar_ejercicio_con_seleccion(ejercicio)
        else:
            st.warning("🔍 No se encontraron ejercicios con los filtros aplicados.")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def mostrar_ejercicio_con_seleccion(ejercicio):
    """Muestra un ejercicio con opción de selección"""
    with st.container():
        col_check, col_content = st.columns([0.1, 0.9])
        
        with col_check:
            is_selected = st.checkbox("", value=ejercicio['id'] in st.session_state.ejercicios_seleccionados, key=f"check_{ejercicio['id']}")
            if is_selected and ejercicio['id'] not in st.session_state.ejercicios_seleccionados:
                st.session_state.ejercicios_seleccionados.append(ejercicio['id'])
            elif not is_selected and ejercicio['id'] in st.session_state.ejercicios_seleccionados:
                st.session_state.ejercicios_seleccionados.remove(ejercicio['id'])
        
        with col_content:
            col_title, col_meta = st.columns([2, 1])
            with col_title:
                st.markdown(f"### {ejercicio.get('titulo', 'Sin título')}")
            with col_meta:
                if ejercicio.get('unidad_tematica'): st.markdown(f"🎯 **{ejercicio['unidad_tematica']}**")
                if ejercicio.get('nivel_dificultad'):
                    color = {"Básico": "green", "Intermedio": "orange", "Avanzado": "red", "Desafío": "purple"}.get(ejercicio['nivel_dificultad'], "blue")
                    st.markdown(f":{color}[🎚️ {ejercicio['nivel_dificultad']}]")
                if ejercicio.get('tiempo_estimado'): st.markdown(f"⏱️ **{ejercicio['tiempo_estimado']} min**")
            
            if ejercicio.get('enunciado'):
                enunciado_md = convert_latex_to_markdown(ejercicio['enunciado'])
                enunciado_preview = enunciado_md[:300] + ("..." if len(enunciado_md) > 300 else "")
                st.markdown(enunciado_preview, unsafe_allow_html=True)
            
            with st.expander("👁️ Ver detalles completos"):
                if ejercicio.get('enunciado'):
                    st.write("**Enunciado completo:**")
                    st.markdown(convert_latex_to_markdown(ejercicio['enunciado']), unsafe_allow_html=True)
                
                if ejercicio.get('solucion_completa'):
                    st.write("**Solución:**")
                    st.markdown(convert_latex_to_markdown(ejercicio['solucion_completa']), unsafe_allow_html=True)
                
                if ejercicio.get('codigo_python'):
                    st.write("**Código Python:**")
                    st.code(ejercicio['codigo_python'], language='python')
                
                st.write("---")
                col1, col2 = st.columns(2)
                with col1:
                    if ejercicio.get('modalidad'): st.write(f"**Modalidad:** {ejercicio['modalidad']}")
                    if ejercicio.get('fuente'): st.write(f"**Fuente:** {ejercicio['fuente']}")
                with col2:
                    if ejercicio.get('fecha_creacion'): st.write(f"**Creado:** {ejercicio['fecha_creacion'][:10]}")
                    st.write(f"**ID:** {ejercicio['id']}")
        
        st.divider()

if __name__ == "__main__":
    main()