"""
Consola de Gestión de Ejercicios
Página: 03_🔍_Buscar_Ejercicios.py (Refactorizado)
Permite buscar, visualizar y gestionar ejercicios de forma individual.
"""

import streamlit as st
import re
from pathlib import Path
import asyncio

# Importar dependencias
try:
    from database.db_manager import DatabaseManager
    # Se añaden las importaciones para el enriquecimiento con IA
    from enrich_db_with_ai import AIEnricher, setup_ai_model
except ImportError:
    import sys
    sys.path.append('.')
    from database.db_manager import DatabaseManager
    from enrich_db_with_ai import AIEnricher, setup_ai_model

# =========================================================================
# ▼▼▼ FUNCIÓN "TRADUCTORA" DE LATEX A MARKDOWN (SIN CAMBIOS) ▼▼▼
def convert_latex_to_markdown(text: str) -> str:
    """
    Convierte una cadena de texto con formato LaTeX a Markdown compatible con Streamlit.
    Esta versión es robusta y maneja tanto LaTeX "crudo" como LaTeX "pre-procesado"
    que viene de la base de datos enriquecida por la IA.
    """
    if not text:
        return ""

    # --- Pipeline de Limpieza de Texto ---
    try:
        repaired_text = text.encode('latin1').decode('utf-8')
        if 'Ã' not in repaired_text:
            text = repaired_text
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    try:
        text = re.sub(r'\\U([0-9a-fA-F]{8})', lambda m: chr(int(m.group(1), 16)), text)
        text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)
        text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), text)
    except (ValueError, TypeError):
        pass

    text = text.replace('\b', '').replace('\f', '')
    text = text.replace('\\\\', '\\')

    # Normalizar delimitadores de matemáticas en línea.
    text = re.sub(r'\\\$([^\$]+?)\\\$', r'$\1$', text)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)

    # --- Pipeline de Conversión de LaTeX a Markdown ---
    # Normalizar entornos de ecuaciones a $$...$$
    text = re.sub(r'\\begin\{(align|align\*)\}(.*?)\\end\{\1\}', r'$$\n\\begin{aligned}\2\\end{aligned}\n$$', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{(equation|equation\*)\}(.*?)\\end\{\1\}', r'$$\n\2\n$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\n\1\n$$', text, flags=re.DOTALL)

    # Convertir listas LaTeX a listas Markdown.
    text = re.sub(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', lambda m: '\n'.join([f"1. {item.strip()}" for item in re.split(r'\\item', m.group(1)) if item.strip()]), text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', lambda m: '\n'.join([f"* {item.strip()}" for item in re.split(r'\\item', m.group(1)) if item.strip()]), text, flags=re.DOTALL)

    # Asegurar que las integrales y sumatorias se rendericen correctamente
    text = re.sub(r'\\int', r'\\int ', text)
    text = re.sub(r'\\sum', r'\\sum ', text)
    return text

@st.cache_resource
def get_db_manager():
    """Carga y cachea una instancia del gestor de la base de datos."""
    return DatabaseManager(db_path="database/ejercicios.db")

@st.cache_resource
def get_ai_enricher():
    """Carga y cachea el modelo de IA y la clase AIEnricher."""
    model = setup_ai_model()
    if model:
        db_manager = get_db_manager()
        return AIEnricher(model, db_manager)
    st.error("No se pudo inicializar el modelo de IA. Revisa la API Key.")
    return None

def main():
    st.set_page_config(page_title="Consola de Gestión", page_icon="⚙️", layout="wide")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>⚙️ Consola de Gestión de Ejercicios</h1>
        <p>Busca, visualiza y gestiona los ejercicios de tu base de datos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db_manager = get_db_manager()
        if not db_manager:
            st.error("No se pudo conectar a la base de datos.")
            return

        # --- FILTROS EN LA BARRA LATERAL ---
        with st.sidebar:
            st.header("🔍 Filtros de Búsqueda")
            ejercicios = db_manager.obtener_ejercicios()
            unidades = db_manager.obtener_unidades_tematicas()
            unidades_filtro = st.multiselect("🎯 Unidades Temáticas", unidades, default=[])
            dificultades_filtro = st.multiselect("🎚️ Nivel de Dificultad", ["Básico", "Intermedio", "Avanzado", "Desafío"], default=[])
            modalidades_filtro = st.multiselect("💻 Modalidad", ["Teórico", "Computacional", "Mixto"], default=[])
            texto_busqueda = st.text_input("🔎 Buscar en título/contenido", placeholder="Ej: convolución...")

        # --- LÓGICA DE FILTRADO ---
        ejercicios_filtrados = ejercicios
        if unidades_filtro: ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('unidad_tematica') in unidades_filtro]
        if dificultades_filtro: ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('nivel_dificultad') in dificultades_filtro]
        if modalidades_filtro: ejercicios_filtrados = [e for e in ejercicios_filtrados if e.get('modalidad') in modalidades_filtro]
        if texto_busqueda:
            texto_lower = texto_busqueda.lower()
            ejercicios_filtrados = [e for e in ejercicios_filtrados if (texto_lower in e.get('titulo', '').lower() or texto_lower in e.get('enunciado', '').lower() or str(e.get('id')) == texto_lower)]

        st.metric("🔍 Ejercicios Encontrados", len(ejercicios_filtrados))
        st.divider()

        # --- VISTA PRINCIPAL: SELECTOR Y FICHA DE DETALLE ---
        if not ejercicios_filtrados:
            st.warning("🔍 No se encontraron ejercicios con los filtros aplicados.")
            return

        opciones_ejercicios = {f"ID {e['id']}: {e.get('titulo', 'Sin título')}": e['id'] for e in ejercicios_filtrados}
        ejercicio_seleccionado_key = st.selectbox(
            "Selecciona un ejercicio para ver sus detalles",
            options=opciones_ejercicios.keys(),
            index=0,
            label_visibility="collapsed"
        )

        if ejercicio_seleccionado_key:
            ejercicio_id_seleccionado = opciones_ejercicios[ejercicio_seleccionado_key]
            ejercicio = next((e for e in ejercicios_filtrados if e['id'] == ejercicio_id_seleccionado), None)

            if ejercicio:
                mostrar_ficha_ejercicio(ejercicio)

    except Exception as e:
        st.error(f"Error: {str(e)}"); import traceback; st.code(traceback.format_exc())

def mostrar_ficha_ejercicio(ejercicio: dict):
    """Muestra la ficha detallada de un ejercicio seleccionado."""
    with st.container(border=True):
        st.subheader(f"ID {ejercicio['id']}: {ejercicio.get('titulo', 'Sin título')}")

        # --- BOTONES DE ACCIÓN ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Editar Ejercicio", use_container_width=True):
                st.session_state.exercise_to_edit = ejercicio['id']
                st.switch_page("pages/04_✏️_Editar_Ejercicio.py")
        with col2:
            if st.button("🤖 Re-enriquecer con IA", key=f"reenrich_{ejercicio['id']}", use_container_width=True):
                enricher = get_ai_enricher()
                if enricher:
                    with st.spinner("🧠 Re-enriqueciendo con IA... Este proceso puede tardar unos minutos."):
                        semaphore = asyncio.Semaphore(1)
                        _, result_data = asyncio.run(enricher._run_analysis_pipeline_with_retries(ejercicio, semaphore))
                        if result_data:
                            st.success("¡Ejercicio re-enriquecido exitosamente!")
                            st.rerun()
                        else:
                            st.error("Falló el proceso de re-enriquecimiento.")
                else:
                    st.error("El enriquecedor de IA no está disponible.")

        st.divider()

        # --- METADATOS Y CLASIFICACIÓN ---
        st.markdown("##### 📊 Clasificación y Metadatos")
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        meta_col1.metric("Unidad Temática", ejercicio.get('unidad_tematica', 'N/A'))
        meta_col2.metric("Nivel de Dificultad", ejercicio.get('nivel_dificultad', 'N/A'))
        meta_col3.metric("Tiempo Estimado", f"{ejercicio.get('tiempo_estimado', 0)} min")

        # --- CONTENIDO DEL EJERCICIO ---
        st.markdown("##### 📄 Contenido")
        if ejercicio.get('enunciado'):
            st.markdown("**Enunciado:**")
            st.markdown(convert_latex_to_markdown(ejercicio['enunciado']), unsafe_allow_html=True)
        
        if ejercicio.get('imagen_path') and Path(ejercicio['imagen_path']).is_file():
            st.image(str(ejercicio['imagen_path']), caption="Imagen del Enunciado")

        if ejercicio.get('solucion_completa'):
            with st.expander("Ver Solución"):
                st.markdown(convert_latex_to_markdown(ejercicio['solucion_completa']), unsafe_allow_html=True)
                if ejercicio.get('solucion_imagen_path') and Path(ejercicio['solucion_imagen_path']).is_file():
                    st.image(str(ejercicio['solucion_imagen_path']), caption="Imagen de la Solución")

        # --- ANÁLISIS PEDAGÓGICO (IA) ---
        st.markdown("##### 🧠 Análisis Pedagógico (IA)")
        
        if ejercicio.get('objetivos_curso'):
            st.markdown("**Objetivos de Curso:**")
            st.write(", ".join(ejercicio['objetivos_curso']))

        if ejercicio.get('prerrequisitos'):
            st.markdown("**Prerrequisitos:**")
            st.info(ejercicio['prerrequisitos'])

        if ejercicio.get('palabras_clave'):
            st.markdown(f"**Palabras Clave:** `{'`, `'.join(ejercicio['palabras_clave'])}`")

        if ejercicio.get('errores_comunes'):
            with st.expander("Ver Errores Comunes"):
                for error in ejercicio['errores_comunes']:
                    st.markdown(f"- {error}")

        if ejercicio.get('hints'):
            with st.expander("Ver Pistas (Hints)"):
                for hint in ejercicio['hints']:
                    st.markdown(f"- *{hint}*")

        if ejercicio.get('extensiones_posibles'):
            st.success(f"**Posible Extensión:** {ejercicio['extensiones_posibles']}")

        if ejercicio.get('codigo_python'):
            with st.expander("Ver Código Python"):
                st.code(ejercicio['codigo_python'], language='python')


if __name__ == "__main__":
    main()
