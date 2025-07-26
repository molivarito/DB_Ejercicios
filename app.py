"""
Sistema de Gestión de Ejercicios - Señales y Sistemas
Aplicación Principal - PUC Chile

Desarrollado por: Patricio de la Cuadra
Curso: IEE2103 - Señales y Sistemas
"""

import streamlit as st

# Configuración de la página principal
st.set_page_config(
    page_title="Gestión de Ejercicios - Señales y Sistemas",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Página principal que redirige al Dashboard"""
    
    # CSS personalizado para mejorar la apariencia
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%);
        color: white;
        padding: 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .welcome-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4e79;
        margin: 1rem 0;
    }
    .feature-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #b8daff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📚 Sistema de Gestión de Ejercicios</h1>
        <h2>IEE2103 - Señales y Sistemas</h2>
        <p>Pontificia Universidad Católica de Chile</p>
        <p><strong>Desarrollado por:</strong> Patricio de la Cuadra</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensaje de bienvenida
    st.markdown("""
    <div class="welcome-card">
        <h3>🎯 ¡Bienvenido al Sistema de Gestión de Ejercicios!</h3>
        <p>Este sistema te permite gestionar, buscar y generar documentos con ejercicios para el curso de Señales y Sistemas.</p>
        <p><strong>👈 Usa el menú lateral para navegar entre las diferentes funcionalidades.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Funcionalidades principales
    st.subheader("🚀 Funcionalidades Principales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h4>🏠 Dashboard</h4>
            <p>Resumen general del sistema con estadísticas y métricas actualizadas.</p>
        </div>
        
        <div class="feature-box">
            <h4>➕ Agregar Ejercicio</h4>
            <p>Formulario completo para crear nuevos ejercicios con metadatos detallados.</p>
        </div>
        
        <div class="feature-box">
            <h4>🔍 Buscar Ejercicios</h4>
            <p>Búsqueda avanzada con filtros y selección para documentos.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h4>📥 Importar LaTeX</h4>
            <p>Importación automática de ejercicios desde archivos LaTeX existentes.</p>
        </div>
        
        <div class="feature-box">
            <h4>🎯 Generar Documentos</h4>
            <p>Creación de Pruebas, Tareas y Guías con templates profesionales PUC.</p>
        </div>
        
        <div class="feature-box">
            <h4>📊 Estadísticas</h4>
            <p>Análisis completo de la base de datos con gráficos interactivos.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Información del sistema
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📈 **Estado:** Sistema 100% funcional")
    
    with col2:
        st.info("🗄️ **Base de Datos:** SQLite con 35+ campos")
    
    with col3:
        st.info("🎨 **Templates:** 3 formatos profesionales PUC")
    
    # Instrucciones de uso
    st.subheader("📋 Cómo Empezar")
    
    st.markdown("""
    1. **🏠 Ve al Dashboard** para ver el resumen del sistema
    2. **🔍 Busca Ejercicios** existentes y selecciona los que te interesen
    3. **🎯 Genera Documentos** usando los ejercicios seleccionados
    4. **📥 Importa LaTeX** si tienes archivos existentes para agregar al sistema
    5. **➕ Agrega Ejercicios** nuevos cuando sea necesario
    
    💡 **Tip:** Comienza explorando los ejercicios existentes en la sección de Búsqueda.
    """)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        Sistema de Gestión de Ejercicios v2.0 | 
        Desarrollado para IEE2103 - Señales y Sistemas | 
        Pontificia Universidad Católica de Chile | 
        Patricio de la Cuadra - 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()