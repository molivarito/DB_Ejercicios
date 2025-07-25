"""
Estadísticas
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
import pandas as pd

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

def main():
    """Página de estadísticas"""
    st.markdown('<h1 class="main-header">📊 Estadísticas</h1>', 
                unsafe_allow_html=True)
    
    try:
        # Intentar cargar estadísticas reales de la BD
        from database.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Obtener estadísticas
        stats = db_manager.obtener_estadisticas()
        
        # Métricas generales
        st.subheader("📈 Resumen General")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ejercicios", stats['total_ejercicios'])
        
        with col2:
            # Calcular dificultad promedio
            if stats['por_dificultad']:
                dificultades = list(stats['por_dificultad'].keys())
                if 'Intermedio' in dificultades:
                    promedio = "Intermedio"
                elif dificultades:
                    promedio = dificultades[0]
                else:
                    promedio = "N/A"
            else:
                promedio = "N/A"
            st.metric("Dificultad Promedio", promedio)
        
        with col3:
            # Calcular tiempo promedio
            ejercicios = db_manager.obtener_ejercicios()
            if ejercicios:
                tiempos = [e.get('tiempo_estimado', 20) for e in ejercicios if e.get('tiempo_estimado')]
                tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 20
                st.metric("Tiempo Promedio", f"{tiempo_promedio:.0f} min")
            else:
                st.metric("Tiempo Promedio", "20 min")
        
        with col4:
            # Unidad más usada
            if stats['por_unidad']:
                mas_usada = max(stats['por_unidad'], key=stats['por_unidad'].get)
                st.metric("Más Usado", mas_usada)
            else:
                st.metric("Más Usado", "N/A")
        
        # Gráficos de distribución
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📚 Distribución por Unidad")
            if stats['por_unidad']:
                unidades_data = pd.DataFrame(
                    list(stats['por_unidad'].items()), 
                    columns=['Unidad', 'Cantidad']
                )
                st.bar_chart(unidades_data.set_index('Unidad'))
            else:
                st.info("No hay datos de unidades para mostrar")
                
        with col2:
            st.subheader("🎯 Distribución por Dificultad")
            if stats['por_dificultad']:
                dificultad_data = pd.DataFrame(
                    list(stats['por_dificultad'].items()), 
                    columns=['Dificultad', 'Cantidad']
                )
                st.bar_chart(dificultad_data.set_index('Dificultad'))
            else:
                st.info("No hay datos de dificultad para mostrar")
        
        # Gráfico adicional por modalidad
        if stats['por_modalidad']:
            st.subheader("🔧 Distribución por Modalidad")
            modalidad_data = pd.DataFrame(
                list(stats['por_modalidad'].items()), 
                columns=['Modalidad', 'Cantidad']
            )
            st.bar_chart(modalidad_data.set_index('Modalidad'))
        
        # Tabla de ejercicios más recientes
        st.subheader("🔥 Ejercicios Más Recientes")
        ejercicios_recientes = db_manager.obtener_ejercicios()[:10]  # Primeros 10
        
        if ejercicios_recientes:
            df_recientes = pd.DataFrame(ejercicios_recientes)
            columnas_mostrar = ['titulo', 'unidad_tematica', 'nivel_dificultad', 'modalidad', 'tiempo_estimado']
            df_display = df_recientes[columnas_mostrar].copy()
            df_display.columns = ['Título', 'Unidad', 'Dificultad', 'Modalidad', 'Tiempo (min)']
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No hay ejercicios para mostrar")
        
        # Información adicional
        st.subheader("📈 Tendencias")
        
        # Análisis de contenido
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Análisis de Contenido:**")
            if ejercicios:
                total_con_solucion = sum(1 for e in ejercicios if e.get('solucion_completa'))
                porcentaje_solucion = (total_con_solucion / len(ejercicios)) * 100
                st.write(f"- Ejercicios con solución: {total_con_solucion}/{len(ejercicios)} ({porcentaje_solucion:.1f}%)")
                
                total_con_codigo = sum(1 for e in ejercicios if e.get('codigo_python'))
                porcentaje_codigo = (total_con_codigo / len(ejercicios)) * 100
                st.write(f"- Ejercicios con código: {total_con_codigo}/{len(ejercicios)} ({porcentaje_codigo:.1f}%)")
            
        with col2:
            st.write("**Estadísticas de Tiempo:**")
            if ejercicios:
                tiempos = [e.get('tiempo_estimado', 20) for e in ejercicios if e.get('tiempo_estimado')]
                if tiempos:
                    st.write(f"- Tiempo mínimo: {min(tiempos)} min")
                    st.write(f"- Tiempo máximo: {max(tiempos)} min")
                    st.write(f"- Tiempo total estimado: {sum(tiempos)} min")
        
    except Exception as e:
        st.error(f"❌ Error cargando estadísticas: {e}")
        
        # Mostrar estadísticas de ejemplo si hay error
        st.subheader("📈 Datos de Ejemplo")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ejercicios", "0")
        with col2:
            st.metric("Dificultad Promedio", "N/A")
        with col3:
            st.metric("Tiempo Promedio", "20 min")
        with col4:
            st.metric("Más Usado", "N/A")
        
        st.info("💡 Importa algunos ejercicios para ver estadísticas reales")

if __name__ == "__main__":
    main()