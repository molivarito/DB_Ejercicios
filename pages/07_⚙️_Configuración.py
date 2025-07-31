"""
Configuración del Sistema - CON GESTIÓN DE BD Y GALERÍA
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
import os
from pathlib import Path

# Dependencias del proyecto
try:
    from utils.config_manager import ConfigManager
    from database.db_manager import DatabaseManager
    from database.cleanup_manager import DatabaseCleanupManager
except ImportError:
    st.error("Error: No se pudieron importar los módulos necesarios. Asegúrate de que la estructura del proyecto es correcta.")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Configuración - Gestión Ejercicios SyS",
    page_icon="⚙️",
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 8px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f4e79;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Página de configuración del sistema"""
    st.markdown('<h1 class="main-header">⚙️ Configuración del Sistema</h1>', 
                unsafe_allow_html=True)
    
    # Inicializar managers
    config_manager = ConfigManager()
    config = config_manager.load_config()

    # Crear pestañas
    tab_profile, tab_db, tab_gallery = st.tabs([
        "👤 Perfil y Curso", 
        "🗄️ Base de Datos", 
        "🖼️ Galería de Imágenes"
    ])

    with tab_profile:
        create_profile_config_ui(config, config_manager)

    with tab_db:
        create_db_management_ui()

    with tab_gallery:
        create_image_gallery_ui()

def create_profile_config_ui(config: dict, manager: ConfigManager):
    """Crea la UI para la configuración del perfil y curso."""
    st.subheader("Información del Curso y Profesor")
    st.markdown("Estos datos se usarán para autocompletar información en los documentos generados.")
    
    profile = config.get("profile", {})
    app_config = config.get("app", {})

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            prof_name = st.text_input("Nombre del Profesor", value=profile.get("professor_name", ""))
            course_name = st.text_input("Nombre del Curso", value=profile.get("course_name", ""))
            university_name = st.text_input("Universidad", value=profile.get("university_name", ""))
        with col2:
            semester = st.text_input("Semestre Actual", value=profile.get("current_semester", ""))
            email = st.text_input("Email de Contacto", value=profile.get("email", ""))
            language = st.selectbox("Idioma", ["Español", "English"], index=["Español", "English"].index(app_config.get("language", "Español")))

        if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
            new_config = {
                "profile": {
                    "professor_name": prof_name,
                    "course_name": course_name,
                    "university_name": university_name,
                    "current_semester": semester,
                    "email": email
                },
                "app": {
                    "language": language
                }
            }
            manager.save_config(new_config)
            st.success("¡Configuración guardada exitosamente!")
            st.toast("Recargando...", icon="🔄")
            st.rerun()

def create_db_management_ui():
    """Crea la UI para la gestión y limpieza de la base de datos."""
    st.subheader("Gestión de Base de Datos")
    
    try:
        cleanup_manager = DatabaseCleanupManager()
    except Exception as e:
        st.error(f"No se pudo inicializar el gestor de limpieza: {e}")
        return

    with st.expander("📊 Estado Actual de la Base de Datos", expanded=True):
        stats = cleanup_manager.get_database_stats()
        if 'error' in stats:
            st.error(f"Error obteniendo estadísticas: {stats['error']}")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Ejercicios", stats.get('total_exercises', 0))
            col1.metric("Sin Solución", stats.get('no_solution', 0))
            col2.metric("Tamaño BD", f"{stats.get('db_size', 0)} MB")
            
            with st.container():
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Por Unidad:**")
                    for unit, count in stats.get('by_unit', {}).items():
                        st.write(f"• {unit}: {count}")
                with c2:
                    st.write("**Por Dificultad:**")
                    for diff, count in stats.get('by_difficulty', {}).items():
                        st.write(f"• {diff}: {count}")

    st.divider()
    st.subheader("🧹 Opciones de Limpieza")
    cleanup_option = st.selectbox(
        "Selecciona tipo de limpieza:",
        [
            "🔥 Eliminar TODOS los ejercicios",
            "📂 Eliminar por archivo fuente",
            "🔧 Eliminar por patrón de parser",
            "♻️ Recrear base de datos completa"
        ]
    )
    source_to_delete = None
    pattern_to_delete = None
    if cleanup_option == "📂 Eliminar por archivo fuente":
        source_to_delete = st.text_input("Nombre del archivo fuente:", placeholder="Ej: main.tex")
    elif cleanup_option == "🔧 Eliminar por patrón de parser":
        pattern_to_delete = st.text_input("Patrón del parser:", placeholder="Ej: patricio_format_v4_fixed_robust")
    
    confirm_cleanup = st.checkbox("⚠️ Confirmo que quiero realizar esta acción (IRREVERSIBLE sin backup)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Crear Backup Primero", use_container_width=True):
            try:
                backup_path = cleanup_manager.create_backup()
                st.success(f"✅ Backup creado: {backup_path}")
            except Exception as e:
                st.error(f"❌ Error creando backup: {str(e)}")
    with col2:
        if st.button("🗑️ Ejecutar Limpieza", type="primary", disabled=not confirm_cleanup, use_container_width=True):
            if cleanup_option == "🔥 Eliminar TODOS los ejercicios":
                with st.spinner("Eliminando todos los ejercicios..."):
                    cleanup_manager.clear_all_exercises()
                st.success("✅ Todos los ejercicios eliminados.")
                st.rerun()
            elif cleanup_option == "📂 Eliminar por archivo fuente" and source_to_delete:
                with st.spinner(f"Eliminando ejercicios de '{source_to_delete}'..."):
                    count = cleanup_manager.clear_exercises_by_source(source_to_delete)
                st.success(f"✅ {count} ejercicios eliminados.")
                st.rerun()
            elif cleanup_option == "🔧 Eliminar por patrón de parser":
                with st.spinner(f"Eliminando ejercicios con patrón '{pattern_to_delete}'..."):
                    count = cleanup_manager.clear_exercises_by_pattern(pattern_to_delete)
                st.success(f"✅ {count} ejercicios eliminados.")
                st.rerun()
            elif cleanup_option == "♻️ Recrear base de datos completa":
                with st.spinner("Recreando la base de datos desde cero..."):
                    cleanup_manager.recreate_database()
                st.success("✅ Base de datos recreada completamente.")
                st.rerun()

    st.divider()
    st.subheader("💾 Gestión de Backups")
    backups = cleanup_manager.list_backups()
    if backups:
        st.write(f"**{len(backups)} backups disponibles:**")
        for backup in backups:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"📄 {backup['filename']}")
                st.caption(f"Modificado: {backup['modified'].strftime('%Y-%m-%d %H:%M')}")
            with col2:
                st.write(f"{backup['size_mb']} MB")
            with col3:
                if st.button("🔄 Restaurar", key=f"restore_{backup['filename']}"):
                    cleanup_manager.restore_from_backup(backup['filepath'])
                    st.success(f"✅ BD restaurada desde {backup['filename']}")
                    st.rerun()
            with col4:
                if st.button("🗑️ Eliminar", key=f"delete_{backup['filename']}"):
                    os.remove(backup['filepath'])
                    st.success(f"✅ Backup eliminado")
                    st.rerun()
    else:
        st.info("No hay backups disponibles")

def create_image_gallery_ui():
    """Crea la UI para la galería de imágenes."""
    st.subheader("Galería de Imágenes")
    st.markdown("Visualiza y gestiona todas las imágenes subidas al sistema.")

    IMAGES_DIR = Path("images")
    if not IMAGES_DIR.is_dir():
        st.info("La carpeta 'images' no existe. Se creará al subir la primera imagen.")
        return

    try:
        db_manager = DatabaseManager()
        all_exercises = db_manager.obtener_ejercicios()
    except Exception as e:
        st.error(f"No se pudo conectar a la base de datos: {e}")
        return

    used_images = set()
    for ex in all_exercises:
        if ex.get('imagen_path'):
            used_images.add(Path(ex['imagen_path']).name)
        if ex.get('solucion_imagen_path'):
            used_images.add(Path(ex['solucion_imagen_path']).name)

    image_files = sorted([f for f in IMAGES_DIR.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']], key=lambda p: p.name)
    
    if not image_files:
        st.info("No hay imágenes en la galería.")
        return

    orphaned_images = [f for f in image_files if f.name not in used_images]
    
    col1, col2 = st.columns(2)
    col1.metric("Total de Imágenes", len(image_files))
    col2.metric("Imágenes Huérfanas", len(orphaned_images), help="Imágenes que no están asociadas a ningún ejercicio.")

    if orphaned_images and st.button("🗑️ Eliminar todas las imágenes huérfanas", type="primary"):
        deleted_count = 0
        for img_path in orphaned_images:
            try:
                img_path.unlink()
                deleted_count += 1
            except Exception as e:
                st.warning(f"No se pudo eliminar {img_path.name}: {e}")
        st.success(f"✅ Se eliminaron {deleted_count} imágenes huérfanas.")
        st.rerun()

    st.divider()

    for image_path in image_files:
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(str(image_path), use_container_width=True)
            with col2:
                st.markdown(f"**Archivo:** `{image_path.name}`")
                if image_path.name in used_images:
                    st.success("✅ En uso")
                    linked_exercises = [ex['titulo'] for ex in all_exercises if image_path.name in [Path(ex.get('imagen_path') or '').name, Path(ex.get('solucion_imagen_path') or '').name]]
                    with st.expander(f"Vinculado a {len(linked_exercises)} ejercicio(s)"):
                        for title in linked_exercises:
                            st.write(f"- {title}")
                else:
                    st.warning("⚠️ Huérfana")
                    if st.button("🗑️ Eliminar", key=f"del_{image_path.name}"):
                        try:
                            image_path.unlink()
                            st.rerun()
                        except Exception as e:
                            st.error(f"No se pudo eliminar: {e}")

if __name__ == "__main__":
    main()