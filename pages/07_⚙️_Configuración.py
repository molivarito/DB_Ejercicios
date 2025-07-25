"""
Configuración
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
from pathlib import Path

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
</style>
""", unsafe_allow_html=True)

def main():
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
        st.text_input("Semestre Actual", value="2025-1")
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
    
    db_path = st.text_input("Ruta de Base de Datos", value="database/ejercicios.db")
    
    # Verificar estado de la BD
    try:
        from database.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Obtener información de la BD
        ejercicios = db_manager.obtener_ejercicios()
        stats = db_manager.obtener_estadisticas()
        
        st.success(f"✅ Base de datos conectada - {len(ejercicios)} ejercicios")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 Archivo: {Path(db_path).name}")
            st.info(f"📊 Total ejercicios: {stats['total_ejercicios']}")
        
        with col2:
            db_file = Path(db_path)
            if db_file.exists():
                size_mb = db_file.stat().st_size / (1024 * 1024)
                st.info(f"💾 Tamaño: {size_mb:.2f} MB")
                st.info(f"📅 Modificado: {db_file.stat().st_mtime}")
        
    except Exception as e:
        st.error(f"❌ Error conectando a BD: {e}")
    
    # Operaciones de BD
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Crear Backup"):
            try:
                import shutil
                from datetime import datetime
                
                backup_name = f"database/ejercicios_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(db_path, backup_name)
                st.success(f"✅ Backup creado: {backup_name}")
            except Exception as e:
                st.error(f"❌ Error creando backup: {e}")
    
    with col2:
        if st.button("📊 Verificar Integridad"):
            try:
                db_manager = DatabaseManager()
                ejercicios = db_manager.obtener_ejercicios()
                
                # Verificaciones básicas
                problemas = []
                for ej in ejercicios:
                    if not ej.get('titulo'):
                        problemas.append(f"Ejercicio ID {ej['id']}: Sin título")
                    if not ej.get('enunciado'):
                        problemas.append(f"Ejercicio ID {ej['id']}: Sin enunciado")
                
                if problemas:
                    st.warning(f"⚠️ {len(problemas)} problemas encontrados:")
                    for problema in problemas[:5]:
                        st.write(f"- {problema}")
                else:
                    st.success("✅ Base de datos íntegra")
                    
            except Exception as e:
                st.error(f"❌ Error verificando: {e}")
    
    with col3:
        if st.button("🗑️ Limpiar Cache"):
            try:
                # Limpiar cache de Streamlit
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("✅ Cache limpiado")
            except Exception as e:
                st.error(f"❌ Error limpiando cache: {e}")
    
    # Información del sistema
    st.subheader("🖥️ Información del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Versión del Sistema:**")
        st.write("- Aplicación: v2.0.0 (Modularizada)")
        st.write("- Streamlit: ", st.__version__)
        st.write("- Python: 3.11+")
        
    with col2:
        st.write("**Módulos Disponibles:**")
        
        # Verificar módulos críticos
        modulos = {
            "DatabaseManager": "database.db_manager",
            "LaTeX Parser": "utils.latex_parser", 
            "PDF Generator": "generators.pdf_generator"
        }
        
        for nombre, modulo in modulos.items():
            try:
                __import__(modulo)
                st.write(f"- ✅ {nombre}")
            except ImportError:
                st.write(f"- ❌ {nombre}")
    
    # Configuración avanzada
    with st.expander("🔬 Configuración Avanzada"):
        st.write("**Configuración de Logging:**")
        log_level = st.selectbox("Nivel de Log", ["INFO", "DEBUG", "WARNING", "ERROR"])
        
        st.write("**Configuración de Parser:**")
        st.checkbox("Modo debug parser", value=False)
        st.number_input("Timeout parsing (seg)", min_value=5, max_value=60, value=30)
        
        st.write("**Configuración de Memoria:**")
        st.checkbox("Cache agresivo", value=True)
        st.number_input("Max ejercicios en cache", min_value=50, max_value=1000, value=200)
    
    # Footer con información
    st.markdown("---")
    st.markdown("**Sistema de Gestión de Ejercicios - Señales y Sistemas**")
    st.markdown("*Desarrollado por Patricio de la Cuadra - PUC Chile*")
    st.markdown("*Versión Modularizada - Julio 2025*")

if __name__ == "__main__":
    main()