"""
Estadísticas
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Dependencias del proyecto
try:
    from database.db_manager import DatabaseManager
except ImportError:
    st.error("Error: No se pudieron importar los módulos necesarios.")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Estadísticas - Gestión Ejercicios SyS",
    page_icon="📊",
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

def display_summary_metrics(stats, all_exercises):
    """Muestra las métricas principales en la parte superior."""
    st.subheader("📈 Resumen General")
    
    # Calcular estadísticas de imágenes
    total_con_imagen_enunciado = sum(1 for e in all_exercises if e.get('imagen_path'))
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Ejercicios", stats.get('total_ejercicios', 0))
    
    # Dificultad más común
    if stats.get('por_dificultad'):
        dificultad_comun = max(stats['por_dificultad'], key=stats['por_dificultad'].get)
    else:
        dificultad_comun = "N/A"
    col2.metric("Dificultad Más Común", dificultad_comun)
    
    # Unidad más usada
    if stats.get('por_unidad'):
        unidad_comun = max(stats['por_unidad'], key=stats['por_unidad'].get)
    else:
        unidad_comun = "N/A"
    col3.metric("Unidad Más Común", unidad_comun)
    
    col4.metric("🖼️ Con Imagen", total_con_imagen_enunciado)

def display_distribution_charts(stats):
    """Muestra los gráficos de distribución por unidad, dificultad y modalidad."""
    st.subheader("📊 Gráficos de Distribución")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📚 Por Unidad Temática**")
        if stats.get('por_unidad'):
            df_unidades = pd.DataFrame(list(stats['por_unidad'].items()), columns=['Unidad', 'Cantidad'])
            st.bar_chart(df_unidades.set_index('Unidad'))
        else:
            st.info("No hay datos de unidades.")
            
    with col2:
        st.write("**🎯 Por Nivel de Dificultad**")
        if stats.get('por_dificultad'):
            df_dificultad = pd.DataFrame(list(stats['por_dificultad'].items()), columns=['Dificultad', 'Cantidad'])
            st.bar_chart(df_dificultad.set_index('Dificultad'))
        else:
            st.info("No hay datos de dificultad.")
            
    if stats.get('por_modalidad'):
        st.write("**🔧 Por Modalidad**")
        df_modalidad = pd.DataFrame(list(stats['por_modalidad'].items()), columns=['Modalidad', 'Cantidad'])
        fig = px.pie(df_modalidad, values='Cantidad', names='Modalidad', title='Distribución por Modalidad',
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig, use_container_width=True)

def display_completeness_analysis(all_exercises):
    """Muestra el análisis de completitud de los ejercicios con barras de progreso."""
    st.subheader("✅ Análisis de Completitud")
    
    if not all_exercises:
        st.info("No hay ejercicios para analizar.")
        return
        
    total_ejercicios = len(all_exercises)
    
    # Cálculos
    total_con_solucion = sum(1 for e in all_exercises if e.get('solucion_completa'))
    total_con_codigo = sum(1 for e in all_exercises if e.get('codigo_python'))
    total_con_imagen_enunciado = sum(1 for e in all_exercises if e.get('imagen_path'))
    total_con_imagen_solucion = sum(1 for e in all_exercises if e.get('solucion_imagen_path'))
    
    # Porcentajes
    pct_solucion = total_con_solucion / total_ejercicios
    pct_codigo = total_con_codigo / total_ejercicios
    pct_imagen_enunciado = total_con_imagen_enunciado / total_ejercicios
    pct_imagen_solucion = total_con_imagen_solucion / total_ejercicios
    
    st.write("Porcentaje de ejercicios que incluyen:")
    
    st.write(f"**Solución Completa:** {total_con_solucion}/{total_ejercicios}")
    st.progress(pct_solucion)
    
    st.write(f"**Código Python:** {total_con_codigo}/{total_ejercicios}")
    st.progress(pct_codigo)
    
    st.write(f"**Imagen en Enunciado:** {total_con_imagen_enunciado}/{total_ejercicios}")
    st.progress(pct_imagen_enunciado)
    
    st.write(f"**Imagen en Solución:** {total_con_imagen_solucion}/{total_ejercicios}")
    st.progress(pct_imagen_solucion)

def display_recent_exercises(db_manager):
    """Muestra una tabla con los ejercicios más recientes."""
    st.subheader("🔥 Ejercicios Más Recientes")
    ejercicios_recientes = db_manager.obtener_ejercicios()[:10]
    
    if ejercicios_recientes:
        df_recientes = pd.DataFrame(ejercicios_recientes)
        columnas_mostrar = ['titulo', 'unidad_tematica', 'nivel_dificultad', 'modalidad', 'tiempo_estimado']
        df_display = df_recientes[columnas_mostrar].copy()
        df_display.columns = ['Título', 'Unidad', 'Dificultad', 'Modalidad', 'Tiempo (min)']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No hay ejercicios para mostrar.")

def main():
    """Página principal de estadísticas."""
    st.markdown('<h1 class="main-header">📊 Estadísticas de la Base de Datos</h1>', 
                unsafe_allow_html=True)
    
    try:
        db_manager = DatabaseManager()
        stats = db_manager.obtener_estadisticas()
        all_exercises = db_manager.obtener_ejercicios()
        
        if not all_exercises:
            st.info("💡 No hay ejercicios en la base de datos. Importa algunos para ver las estadísticas.")
            return
            
        display_summary_metrics(stats, all_exercises)
        st.divider()
        display_distribution_charts(stats)
        st.divider()
        display_completeness_analysis(all_exercises)
        st.divider()
        display_recent_exercises(db_manager)
        
    except Exception as e:
        st.error(f"❌ Error cargando estadísticas: {e}")
        st.info("💡 Asegúrate de que la base de datos 'ejercicios.db' exista y sea accesible.")

if __name__ == "__main__":
    main()