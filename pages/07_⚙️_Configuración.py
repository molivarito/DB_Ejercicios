"""
Configuración del Sistema - CON GESTIÓN DE BD
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
import os

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
    .config-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f4e79;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Página de configuración del sistema"""
    st.markdown('<h1 class="main-header">⚙️ Configuración del Sistema</h1>', 
                unsafe_allow_html=True)
    
    # Configuración general
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.subheader("🔧 Configuración General")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Nombre del Profesor", value="Patricio de la Cuadra")
        st.text_input("Curso", value="IEE2103 - Señales y Sistemas")
        st.text_input("Universidad", value="Pontificia Universidad Católica de Chile")
        
    with col2:
        st.text_input("Semestre Actual", value="2025-1")
        st.text_input("Email", value="pcuadra@uc.cl")
        st.selectbox("Idioma", ["Español", "English"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Configuración de importación LaTeX
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Configuración de exportación
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.subheader("📄 Configuración de Exportación")
    
    st.text_input("Template LaTeX", value="template_prueba.tex")
    st.checkbox("Incluir logo UC", value=True)
    st.checkbox("Numerar ejercicios automáticamente", value=True)
    st.checkbox("Incluir fecha en documentos", value=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 🆕 NUEVA SECCIÓN: Gestión de Base de Datos
    create_cleanup_interface()


def create_cleanup_interface():
    """
    Interfaz de Streamlit para gestión de limpieza de BD
    """
    
    st.subheader("🗄️ Gestión de Base de Datos")
    
    # Importar el DatabaseCleanupManager
    try:
        from database.cleanup_manager import DatabaseCleanupManager
    except ImportError:
        st.error("❌ No se pudo importar DatabaseCleanupManager. Verifica que database/cleanup_manager.py existe.")
        return
    
    cleanup_manager = DatabaseCleanupManager()
    
    # Mostrar estadísticas actuales
    with st.expander("📊 Estado Actual de la Base de Datos", expanded=True):
        stats = cleanup_manager.get_database_stats()
        
        if 'error' in stats:
            st.error(f"Error obteniendo estadísticas: {stats['error']}")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Ejercicios", stats['total_exercises'])
                st.metric("Sin Solución", stats['no_solution'])
            
            with col2:
                st.write("**Por Unidad:**")
                for unit, count in stats['by_unit'].items():
                    st.write(f"• {unit}: {count}")
            
            with col3:
                st.write("**Por Dificultad:**")
                for diff, count in stats['by_difficulty'].items():
                    st.write(f"• {diff}: {count}")
                
                st.metric("Tamaño BD", f"{stats['db_size']} MB")
    
    st.divider()
    
    # Opciones de limpieza
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
    
    # Configuración específica según opción
    source_to_delete = None
    pattern_to_delete = None
    
    if cleanup_option == "📂 Eliminar por archivo fuente":
        source_to_delete = st.text_input(
            "Nombre del archivo fuente:",
            placeholder="Ej: main.tex, guia_cap1.tex"
        )
    elif cleanup_option == "🔧 Eliminar por patrón de parser":
        pattern_to_delete = st.selectbox(
            "Patrón del parser:",
            ["patricio_format", "subsection_complete", "ejercicio_environment", "generic_conservative"]
        )
    
    # Checkbox de confirmación
    confirm_cleanup = st.checkbox(
        "⚠️ Confirmo que quiero realizar esta acción (IRREVERSIBLE sin backup)",
        value=False
    )
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Crear Backup Primero", type="secondary"):
            try:
                backup_path = cleanup_manager.create_backup()
                st.success(f"✅ Backup creado: {backup_path}")
            except Exception as e:
                st.error(f"❌ Error creando backup: {str(e)}")
    
    with col2:
        if st.button("🗑️ Ejecutar Limpieza", type="primary", disabled=not confirm_cleanup):
            if cleanup_option == "🔥 Eliminar TODOS los ejercicios":
                try:
                    cleanup_manager.clear_all_exercises()
                    st.success("✅ Todos los ejercicios eliminados")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
            elif cleanup_option == "📂 Eliminar por archivo fuente" and source_to_delete:
                try:
                    count = cleanup_manager.clear_exercises_by_source(source_to_delete)
                    st.success(f"✅ {count} ejercicios eliminados de fuente '{source_to_delete}'")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
            elif cleanup_option == "🔧 Eliminar por patrón de parser":
                try:
                    count = cleanup_manager.clear_exercises_by_pattern(pattern_to_delete)
                    st.success(f"✅ {count} ejercicios eliminados con patrón '{pattern_to_delete}'")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
            elif cleanup_option == "♻️ Recrear base de datos completa":
                try:
                    cleanup_manager.recreate_database()
                    st.success("✅ Base de datos recreada completamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Gestión de backups
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
                    try:
                        cleanup_manager.restore_from_backup(backup['filepath'])
                        st.success(f"✅ BD restaurada desde {backup['filename']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error restaurando: {str(e)}")
            
            with col4:
                if st.button("🗑️ Eliminar", key=f"delete_{backup['filename']}"):
                    try:
                        os.remove(backup['filepath'])
                        st.success(f"✅ Backup eliminado")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error eliminando backup: {str(e)}")
    else:
        st.info("No hay backups disponibles")
    
    # Instrucciones post-limpieza
    st.divider()
    st.subheader("📝 Después de la Limpieza")
    st.info("""
    **Pasos recomendados después de limpiar la BD:**
    
    1. **Actualizar el parser LaTeX** con la nueva versión V4.0
    2. **Ir a 'Importar LaTeX'** y cargar tu archivo de guía
    3. **Verificar** que los ejercicios se importen correctamente
    4. **Crear backup** de la nueva BD limpia
    """)


if __name__ == "__main__":
    main()