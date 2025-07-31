"""
Importar LaTeX - CON MANEJO DE IMÁGENES DESDE ZIP
Sistema de Gestión de Ejercicios - Señales y Sistemas
VERSIÓN MEJORADA: Usa st.tabs y procesa archivos .zip con imágenes.
"""

import streamlit as st
import logging
from pathlib import Path
import zipfile
import tempfile
import shutil
from typing import List, Dict

# Configuración de la página
st.set_page_config(
    page_title="Importar LaTeX - Gestión Ejercicios SyS",
    page_icon="📥",
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _convert_parsed_to_dict(parsed_ex, source_name: str) -> Dict:
    """Convierte un objeto ParsedExercise a un diccionario para session_state."""
    exercise_dict = {
        'titulo': parsed_ex.titulo,
        'enunciado': parsed_ex.enunciado,
        'unidad_tematica': parsed_ex.unidad_tematica,
        'nivel_dificultad': parsed_ex.nivel_dificultad,
        'modalidad': parsed_ex.modalidad,
        'tiempo_estimado': parsed_ex.tiempo_estimado,
        'fuente': source_name,
        'pattern_used': parsed_ex.pattern_used
    }
    
    # Agregar imagen si existe
    if hasattr(parsed_ex, 'image_filename') and parsed_ex.image_filename:
        exercise_dict['image_filename'] = parsed_ex.image_filename

    # Agregar imagen de solución si existe
    if hasattr(parsed_ex, 'solucion_image_filename') and parsed_ex.solucion_image_filename:
        exercise_dict['solucion_image_filename'] = parsed_ex.solucion_image_filename
    
    # Agregar solucion_completa si existe
    if hasattr(parsed_ex, 'solucion_completa') and parsed_ex.solucion_completa:
        exercise_dict['solucion_completa'] = parsed_ex.solucion_completa
    
    # Agregar otros campos opcionales
    optional_fields = ['respuesta_final', 'palabras_clave', 'subtemas', 'tipo_actividad', 'comentarios']
    for field in optional_fields:
        if hasattr(parsed_ex, field) and getattr(parsed_ex, field):
            exercise_dict[field] = getattr(parsed_ex, field)
            
    return exercise_dict

def process_and_store_exercises(parsed_exercises: List, source_name: str):
    """Procesa y guarda los ejercicios parseados en el estado de la sesión."""
    exercises_found = [_convert_parsed_to_dict(p, source_name) for p in parsed_exercises]
    st.session_state.exercises_found = exercises_found
    st.session_state.import_completed = False
    
    if exercises_found:
        st.success(f"✅ Se encontraron {len(exercises_found)} ejercicios.")
    else:
        st.warning("⚠️ No se encontraron ejercicios que coincidan con los patrones.")

def main():
    """Página para importar ejercicios desde LaTeX - VERSIÓN ARREGLADA"""
    st.markdown('<h1 class="main-header">📥 Importar Ejercicios desde LaTeX</h1>', 
                unsafe_allow_html=True)
    
    st.info("""
    **¿Cómo funciona el importador?**
    1. **Sube tu contenido**: Puedes subir un archivo `.zip` (con `.tex` e imágenes), un `.tex` individual o pegar código LaTeX.
    2. **Análisis automático**: El sistema busca patrones de ejercicios, extrae metadatos (dificultad, unidad) y detecta imágenes.
    3. **Revisa y confirma**: Visualiza los ejercicios encontrados y sus detalles antes de guardarlos permanentemente.
    """)
    
    # --- Inicialización y Configuración ---
    IMAGES_DIR = Path("images")
    IMAGES_DIR.mkdir(exist_ok=True)

    if 'exercises_found' not in st.session_state:
        st.session_state.exercises_found = []
    if 'import_completed' not in st.session_state:
        st.session_state.import_completed = False
    # Manejo manual del directorio temporal para que persista entre reruns
    if 'import_zip_root' not in st.session_state:
        st.session_state.import_zip_root = None
    if 'import_tex_parent' not in st.session_state:
        st.session_state.import_tex_parent = None


    # --- Pestañas de Importación ---
    tab_zip, tab_tex, tab_paste = st.tabs([
        "📁 **Importar desde ZIP (con imágenes)**",
        "📄 Subir archivo .tex",
        "📝 Pegar código LaTeX"
    ])

    with tab_zip:
        st.markdown("Sube un archivo `.zip` que contenga tu archivo `.tex` y todas las imágenes referenciadas.")
        uploaded_zip = st.file_uploader("Selecciona archivo .zip", type=['zip'], key="zip_uploader")
        if uploaded_zip:
            if st.button("🔄 Extraer Ejercicios del ZIP", key="extract_zip"):
                with st.spinner("📦 Descomprimiendo y analizando archivo..."):
                    try:
                        # Limpiar directorio temporal anterior si existe
                        if st.session_state.get('import_zip_root') and Path(st.session_state.import_zip_root).exists():
                            shutil.rmtree(st.session_state.import_zip_root, ignore_errors=True)

                        # Crear un nuevo directorio temporal y guardarlo en el estado de la sesión
                        temp_dir = tempfile.mkdtemp(prefix="st_zip_import_")
                        st.session_state.import_zip_root = temp_dir
                        temp_path = Path(temp_dir)

                        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                            zip_ref.extractall(temp_path)
                        
                        # Búsqueda RECURSIVA para encontrar el .tex sin importar la estructura de carpetas
                        tex_files = list(temp_path.rglob('*.tex'))
                        if not tex_files:
                            st.error("❌ No se encontró ningún archivo `.tex` en el ZIP.")
                            return
                        
                        tex_file_path = tex_files[0]
                        tex_parent_dir = tex_file_path.parent
                        st.session_state.import_tex_parent = str(tex_parent_dir) # Guardar como string

                        logger.info(f"Archivo .tex encontrado en: {tex_file_path}")
                        logger.info(f"Directorio base para imágenes: {tex_parent_dir}")
                        content = tex_file_path.read_text(encoding='utf-8')
                        
                        from utils.latex_parser import LaTeXParser
                        parser = LaTeXParser()
                        parsed_exercises = parser.parse_file(content)
                        process_and_store_exercises(parsed_exercises, uploaded_zip.name)

                    except Exception as e:
                        st.error(f"❌ Error procesando el ZIP: {e}")
                        st.exception(e)

    with tab_tex:
        st.markdown("Sube un único archivo `.tex` sin imágenes asociadas.")
        uploaded_file = st.file_uploader("Selecciona archivo .tex", type=['tex', 'txt'], key="tex_uploader")
        if uploaded_file:
            if st.button("🔄 Extraer Ejercicios del Archivo", key="extract_file"):
                with st.spinner("🔍 Analizando archivo LaTeX..."):
                    try:
                        # Limpiar estado de importación de ZIP si existiera
                        if st.session_state.get('import_zip_root'):
                            shutil.rmtree(st.session_state.import_zip_root, ignore_errors=True)
                            st.session_state.import_zip_root = None
                            st.session_state.import_tex_parent = None
                        content = str(uploaded_file.read(), "utf-8")
                        from utils.latex_parser import LaTeXParser
                        parser = LaTeXParser()
                        parsed_exercises = parser.parse_file(content)
                        process_and_store_exercises(parsed_exercises, uploaded_file.name)
                    except Exception as e:
                        st.error(f"❌ Error parseando archivo: {e}")
                        st.exception(e)

    with tab_paste:
        st.markdown("Pega código LaTeX directamente en el área de texto. No se procesarán imágenes.")
        latex_content = st.text_area("Pega tu código LaTeX aquí:", height=250, key="paste_area")
        if st.button("🔄 Extraer Ejercicios del Texto", key="extract_text"):
            if latex_content:
                with st.spinner("🔍 Analizando código LaTeX..."):
                    try:
                        # Limpiar estado de importación de ZIP si existiera
                        if st.session_state.get('import_zip_root'):
                            shutil.rmtree(st.session_state.import_zip_root, ignore_errors=True)
                            st.session_state.import_zip_root = None
                            st.session_state.import_tex_parent = None
                        from utils.latex_parser import LaTeXParser
                        parser = LaTeXParser()
                        parsed_exercises = parser.parse_file(latex_content)
                        process_and_store_exercises(parsed_exercises, "Importación manual")
                    except Exception as e:
                        st.error(f"❌ Error parseando código: {e}")
            else:
                st.warning("El área de texto está vacía.")

    # --- Visualización y Confirmación de Importación (Lógica compartida) ---
    if st.session_state.exercises_found:
        st.divider()
        st.subheader(f"📋 Vista Previa de Ejercicios ({len(st.session_state.exercises_found)} encontrados)")
        
        for i, exercise in enumerate(st.session_state.exercises_found):
            with st.expander(f"**{i+1}. {exercise['titulo']}**", expanded=i < 2):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write("**Enunciado:**")
                    st.text_area("Enunciado", value=exercise['enunciado'], height=150, key=f"enunciado_{i}", disabled=True)
                    if 'solucion_completa' in exercise:
                        st.write("**Solución:**")
                        st.text_area("Solución", value=exercise['solucion_completa'], height=150, key=f"solucion_{i}", disabled=True)
                with col2:
                    st.write("**Metadatos:**")
                    st.info(f"""
                    - **Dificultad:** {exercise['nivel_dificultad']}
                    - **Unidad:** {exercise['unidad_tematica']}
                    - **Tiempo:** {exercise['tiempo_estimado']} min
                    - **Modalidad:** {exercise['modalidad']}
                    """)
                    if 'image_filename' in exercise:
                        st.success(f"🖼️ Imagen detectada: `{exercise['image_filename']}`")
        
        st.divider()
        st.subheader("💾 Importar a Base de Datos")
        if st.button("✅ Confirmar Importación a la Base de Datos", type="primary"):
            exercises_to_import = st.session_state.exercises_found
            zip_root_dir_str = st.session_state.get('import_zip_root')
            tex_parent_dir_str = st.session_state.get('import_tex_parent')

            if not exercises_to_import:
                st.warning("No hay ejercicios para importar.")
                return

            try:
                from database.db_manager import DatabaseManager
                db_manager = DatabaseManager()
                
                ejercicios_preparados = []
                for ex in exercises_to_import:
                    ejercicio = {
                        'titulo': ex.get('titulo', 'Sin título'),
                        'enunciado': ex.get('enunciado', ''),
                        'unidad_tematica': ex.get('unidad_tematica', 'General'),
                        'nivel_dificultad': ex.get('nivel_dificultad', 'Intermedio'),
                        'modalidad': ex.get('modalidad', 'Teórico'),
                        'tiempo_estimado': ex.get('tiempo_estimado', 20),
                        'fuente': ex.get('fuente', 'Importación LaTeX')
                    }
                    
                    # Mapeo de campos opcionales
                    for field in ['solucion_completa', 'palabras_clave', 'subtemas', 'comentarios_docente', 'codigo_python']:
                        if field in ex:
                            ejercicio[field] = ex[field]
                    
                    # Manejo de la imagen
                    ejercicio['imagen_path'] = None
                    image_filename = ex.get('image_filename')
                    if image_filename and zip_root_dir_str and tex_parent_dir_str:
                        zip_root_dir = Path(zip_root_dir_str)
                        tex_parent_dir = Path(tex_parent_dir_str)
                        
                        # Intento 1: Resolver la ruta relativa al archivo .tex
                        source_image_path = (tex_parent_dir / image_filename).resolve()
                        
                        # Intento 2: Si no se encuentra, buscar recursivamente desde la raíz del ZIP
                        if not source_image_path.is_file():
                            base_filename = Path(image_filename).name
                            logger.info(f"Imagen en ruta relativa '{image_filename}' no encontrada. Buscando '{base_filename}' en todo el ZIP.")
                            found_files = list(zip_root_dir.rglob(base_filename))
                            if found_files:
                                source_image_path = found_files[0]
                                logger.info(f"Imagen encontrada en: '{source_image_path}'")
                            else:
                                source_image_path = None

                        if source_image_path and source_image_path.is_file():
                            dest_image_path = IMAGES_DIR / source_image_path.name
                            shutil.copy(source_image_path, dest_image_path)
                            # Guardar ruta relativa con slashes para compatibilidad
                            ejercicio['imagen_path'] = str(dest_image_path).replace('\\', '/')
                            logger.info(f"✅ Imagen '{image_filename}' copiada a '{dest_image_path}'")
                        else:
                            st.warning(f"🖼️❌ Imagen `{image_filename}` mencionada para '{ejercicio['titulo']}' pero no se encontró en el ZIP.")
                    elif image_filename and not zip_root_dir_str:
                         st.warning(f"🖼️⚠️ Imagen `{image_filename}` detectada pero no se puede procesar (no es una importación desde ZIP).")
                    
                    # Manejo de la imagen de la solución
                    ejercicio['solucion_imagen_path'] = None
                    solucion_image_filename = ex.get('solucion_image_filename')
                    if solucion_image_filename and zip_root_dir_str and tex_parent_dir_str:
                        zip_root_dir = Path(zip_root_dir_str)
                        tex_parent_dir = Path(tex_parent_dir_str)
                        
                        source_image_path = (tex_parent_dir / solucion_image_filename).resolve()
                        if not source_image_path.is_file():
                            base_filename = Path(solucion_image_filename).name
                            found_files = list(zip_root_dir.rglob(base_filename))
                            source_image_path = found_files[0] if found_files else None

                        if source_image_path and source_image_path.is_file():
                            dest_path = IMAGES_DIR / source_image_path.name
                            shutil.copy(source_image_path, dest_path)
                            ejercicio['solucion_imagen_path'] = str(dest_path).replace('\\', '/')
                            logger.info(f"✅ Imagen de solución '{solucion_image_filename}' copiada a '{dest_path}'")
                        else:
                            st.warning(f"🖼️❌ Imagen de solución `{solucion_image_filename}` mencionada para '{ejercicio['titulo']}' pero no se encontró.")


                    ejercicios_preparados.append(ejercicio)
                
                importados = 0
                errores = []
                
                with st.spinner("Guardando en la base de datos..."):
                    for i, ejercicio_para_db in enumerate(ejercicios_preparados):
                        try:
                            ejercicio_id = db_manager.agregar_ejercicio(ejercicio_para_db)
                            if ejercicio_id:
                                importados += 1
                                logger.info(f"Importado: {ejercicio_para_db['titulo']} (ID: {ejercicio_id})")
                        except Exception as e:
                            error_msg = f"Error con '{ejercicio_para_db['titulo']}': {str(e)}"
                            errores.append(error_msg)
                            logger.error(error_msg)
                
                # Mostrar resultados
                if importados > 0:
                    st.success(f"🎉 ¡{importados} ejercicios importados exitosamente!")
                    st.balloons()
                    
                    stats = db_manager.obtener_estadisticas()
                    st.info(f"📊 Total de ejercicios en la base de datos ahora: {stats['total_ejercicios']}")
                    
                    # Limpiar estado y directorio temporal
                    if st.session_state.get('import_zip_root') and Path(st.session_state.import_zip_root).exists():
                        shutil.rmtree(st.session_state.import_zip_root, ignore_errors=True)
                    
                    st.session_state.import_zip_root = None
                    st.session_state.import_tex_parent = None
                    st.session_state.exercises_found = []
                    st.session_state.import_completed = True
                
                if errores:
                    st.error(f"❌ {len(errores)} errores durante la importación:")
                    for error in errores[:5]:
                        st.error(f"  • {error}")
                        
            except Exception as e:
                st.error(f"❌ Error crítico durante la importación: {str(e)}")
                st.exception(e)

    elif not st.session_state.exercises_found and st.session_state.get('import_completed', False):
        st.success("✅ Importación completada. Puedes ver los nuevos ejercicios en la página 'Buscar Ejercicios'.")
        if st.button("Realizar otra importación"):
            # Limpiar por si acaso quedó algo
            if st.session_state.get('import_zip_root') and Path(st.session_state.import_zip_root).exists():
                shutil.rmtree(st.session_state.import_zip_root, ignore_errors=True)
            st.session_state.import_zip_root = None
            st.session_state.import_tex_parent = None
            st.session_state.import_completed = False
            st.rerun()

if __name__ == "__main__":
    main()
