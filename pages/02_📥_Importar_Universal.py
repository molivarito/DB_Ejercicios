"""
Página de Streamlit para la Importación Universal de Ejercicios
Permite subir archivos .tex, .pdf, o de imagen para su procesamiento y enriquecimiento con IA.
"""

import streamlit as st
from pathlib import Path
import time
import asyncio
import re
import json
import google.generativeai as genai

# Se activan las importaciones para conectar con la lógica de enriquecimiento y BD.
from database.db_manager import DatabaseManager
from enrich_db_with_ai import AIEnricher, setup_ai_model


# =========================================================================
# ▼▼▼ GESTIÓN DE RECURSOS EN CACHÉ (MEJORES PRÁCTICAS) ▼▼▼
# =========================================================================

@st.cache_resource
def get_db_manager():
    """
    Carga y cachea una instancia del gestor de la base de datos.
    st.cache_resource asegura que la conexión se cree una sola vez.
    """
    return DatabaseManager(db_path="database/ejercicios.db")

@st.cache_resource
def get_ai_enricher():
    """
    Carga y cachea el modelo de IA y la clase AIEnricher.
    Esto evita recargar el modelo en cada interacción del usuario.
    """
    model = setup_ai_model()
    if model:
        db_manager = get_db_manager()
        return AIEnricher(model, db_manager)
    st.error("No se pudo inicializar el modelo de IA. Revisa la API Key.")
    return None

@st.cache_resource
def get_ai_model():
    """
    Configura y retorna un modelo generativo de Gemini para OCR.
    """
    try:
        # Es una mejor práctica usar st.secrets para la API Key
        # Asegúrate de tener un archivo .streamlit/secrets.toml con GOOGLE_API_KEY="AIza..."
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            st.error("La API Key de Google no ha sido configurada en los secretos de Streamlit (.streamlit/secrets.toml).")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        return model
    except Exception as e:
        st.error(f"❌ Error al configurar el modelo de IA para OCR: {e}")
        return None

# =========================================================================
# ▼▼▼ FUNCIONES DE EXTRACCIÓN DE CONTENIDO ▼▼▼
# =========================================================================

def extract_content_from_tex(uploaded_file) -> dict:
    """
    Extrae contenido de un archivo .tex.
    """
    try:
        content = uploaded_file.getvalue().decode("utf-8")
        if "\\begin{solucion}" in content:
            parts = content.split("\\begin{solucion}")
            enunciado = parts[0]
            solucion = "\\begin{solucion}" + parts[1]
        else:
            enunciado = content
            solucion = ""
        return {
            "titulo": f"Ejercicio desde {uploaded_file.name}",
            "enunciado": enunciado.strip(),
            "solucion": solucion.strip()
        }
    except Exception as e:
        st.error(f"Error al leer el archivo .tex: {e}")
        return None

def extract_content_from_media(uploaded_file) -> dict:
    """
    Extrae contenido de un PDF o imagen usando la capacidad multimodal de Gemini.
    """
    with st.spinner(f"🤖 Procesando {uploaded_file.type} con IA..."):
        try:
            model = get_ai_model()
            if not model:
                return None

            media_file = {'mime_type': uploaded_file.type, 'data': uploaded_file.getvalue()}
            ocr_prompt = """
            Actúa como un sistema OCR experto. Tu tarea es analizar la imagen o PDF y transcribir su contenido a LaTeX.
            Identifica dos secciones: el enunciado y la solución. Si no hay solución, deja el campo vacío.
            Devuelve el resultado exclusivamente en formato JSON. Usa esta estructura:
            {"enunciado_extraido": "...", "solucion_extraida": "..."}
            """
            response = model.generate_content([ocr_prompt, media_file])
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if not json_match:
                st.error(f"No se pudo encontrar un bloque JSON en la respuesta de la IA: {response.text[:200]}...")
                return None
            
            data = json.loads(json_match.group(0))
            return {
                "titulo": f"Ejercicio desde {uploaded_file.name}",
                "enunciado": data.get("enunciado_extraido", ""),
                "solucion": data.get("solucion_extraida", "")
            }
        except Exception as e:
            st.error(f"Ocurrió un error durante el procesamiento del archivo: {e}")
            return None

# =========================================================================
# ▼▼▼ PÁGINA PRINCIPAL DE STREAMLIT ▼▼▼
# =========================================================================

def main():
    st.set_page_config(page_title="Importación Universal", page_icon="📥", layout="wide")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>📥 Importación Universal de Ejercicios</h1>
        <p>Sube un archivo (.tex, .pdf, .png, .jpg) para extraer su contenido y enriquecerlo con IA.</p>
    </div>
    """, unsafe_allow_html=True)

    # Inicializar el estado de la sesión
    if 'extracted_content' not in st.session_state:
        st.session_state.extracted_content = None
    if 'enriched_data' not in st.session_state:
        st.session_state.enriched_data = None

    uploaded_file = st.file_uploader("Selecciona un archivo para importar", type=['tex', 'pdf', 'png', 'jpg', 'jpeg'])

    if uploaded_file:
        if st.button("🚀 Extraer Contenido del Archivo", use_container_width=True, type="primary"):
            st.session_state.extracted_content = None
            st.session_state.enriched_data = None
            file_extension = Path(uploaded_file.name).suffix.lower()
            if file_extension == ".tex":
                st.session_state.extracted_content = extract_content_from_tex(uploaded_file)
            else:
                st.session_state.extracted_content = extract_content_from_media(uploaded_file)

    if st.session_state.get('extracted_content'):
        st.success("✅ Contenido extraído. Revisa y edita si es necesario.")
        st.text_area("Enunciado (LaTeX)", value=st.session_state.extracted_content.get("enunciado", ""), height=200, key="enunciado_area")
        st.text_area("Solución (LaTeX)", value=st.session_state.extracted_content.get("solucion", ""), height=200, key="solucion_area")
        
        st.divider()
        if st.button("🤖 Enriquecer con IA", use_container_width=True):
            enricher = get_ai_enricher()
            if enricher:
                exercise_to_enrich = {
                    "id": -1,
                    "titulo": st.session_state.extracted_content.get("titulo", "Ejercicio importado"),
                    "enunciado": st.session_state.enunciado_area,
                    "solucion_completa": st.session_state.solucion_area
                }
                with st.spinner("🧠 Enriqueciendo con IA... Este proceso puede tardar unos minutos."):
                    try:
                        semaphore = asyncio.Semaphore(1)
                        _, result_data = asyncio.run(enricher._run_analysis_pipeline_with_retries(exercise_to_enrich, semaphore))
                        st.session_state.enriched_data = result_data
                    except Exception as e:
                        st.error(f"Ocurrió un error durante el enriquecimiento: {e}")
                        st.session_state.enriched_data = None
            else:
                st.error("El enriquecedor de IA no está disponible.")

    if st.session_state.get('enriched_data'):
        st.success("✨ ¡Ejercicio enriquecido exitosamente!")
        st.json(st.session_state.enriched_data)
        if st.button("💾 Guardar en Base de Datos", use_container_width=True, type="primary"):
            with st.spinner("💾 Guardando en la base de datos..."):
                try:
                    db_manager = get_db_manager()
                    enriched_data = st.session_state.enriched_data

                    # Mapear los nombres de las claves del resultado de la IA a los nombres de las columnas de la BD
                    field_map = {
                        "titulo_sugerido": "titulo", "enunciado_corregido": "enunciado",
                        "solucion_corregida": "solucion_completa", "unidad_tematica": "unidad_tematica",
                        "subtemas": "subtemas", "nivel_dificultad": "nivel_dificultad",
                        "tiempo_estimado": "tiempo_estimado", "palabras_clave": "palabras_clave",
                        "objetivos_curso": "objetivos_curso", "prerrequisitos": "prerrequisitos",
                        "errores_comunes": "errores_comunes", "hints": "hints",
                        "extensiones_posibles": "extensiones_posibles"
                    }
                    
                    data_to_save = {field_map.get(k, k): v for k, v in enriched_data.items() if k in field_map}
                    
                    new_exercise_id = db_manager.agregar_ejercicio(data_to_save)
                    
                    st.success(f"✅ ¡Ejercicio guardado exitosamente con ID: {new_exercise_id}!")
                    st.balloons()
                    
                    # Limpiar el estado para permitir una nueva importación
                    st.session_state.extracted_content = None
                    st.session_state.enriched_data = None
                    time.sleep(2) # Pequeña pausa para que el usuario vea el mensaje
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ocurrió un error al guardar en la base de datos: {e}")

if __name__ == "__main__":
    main()