"""
Dashboard - SOLO corrección de conteo de ejercicios
Página: 01_🏠_Dashboard.py
"""

import streamlit as st
import plotly.express as px
from datetime import datetime

# Importar el DatabaseManager
try:
    from database.db_manager import DatabaseManager
except ImportError:
    import sys
    sys.path.append('.')
    from database.db_manager import DatabaseManager

def main():
    st.set_page_config(
        page_title="Dashboard - Gestión de Ejercicios",
        page_icon="🏠",
        layout="wide"
    )
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>🏠 Dashboard - Sistema de Gestión de Ejercicios</h1>
        <p>IEE2103 - Señales y Sistemas | Pontificia Universidad Católica de Chile</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # AQUÍ ESTÁ LA CORRECCIÓN PRINCIPAL
        db = DatabaseManager()
        
        # OBTENER TODOS LOS EJERCICIOS (no solo estadísticas)
        todos_ejercicios = db.obtener_ejercicios()  # Esto da los 28 ejercicios
        stats = db.obtener_estadisticas()           # Esto daba 3 por algún bug
        
        # USAR EL CONTEO REAL DE LA LISTA
        total_real = len(todos_ejercicios)  # Esto será 28
        
        st.subheader("📊 Resumen General")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # USAR EL CONTEO REAL EN LUGAR DEL DE STATS
            st.metric(
                label="📚 Total de Ejercicios",
                value=total_real,  # Ahora mostrará 28
                delta=f"Real: {total_real} vs Stats: {stats['total_ejercicios']}"
            )
        
        with col2:
            st.metric(
                label="🎯 Unidades Temáticas",
                value=len(stats['por_unidad']),
                delta="7 configuradas"
            )
        
        with col3:
            ejercicios_listos = len([e for e in todos_ejercicios if e.get('estado') == 'Listo'])
            st.metric(
                label="✅ Ejercicios Listos",
                value=ejercicios_listos,
                delta=f"{round(ejercicios_listos/total_real*100) if total_real > 0 else 0}%"
            )
        
        with col4:
            tiempos = [e['tiempo_estimado'] for e in todos_ejercicios if e.get('tiempo_estimado')]
            tiempo_promedio = round(sum(tiempos)/len(tiempos)) if tiempos else 0
            st.metric(
                label="⏱️ Tiempo Promedio",
                value=f"{tiempo_promedio} min",
                delta="por ejercicio"
            )
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Distribución por Unidad")
            if stats['por_unidad']:
                import pandas as pd
                df = pd.DataFrame(list(stats['por_unidad'].items()), columns=['Unidad', 'Cantidad'])
                fig = px.bar(df, x='Cantidad', y='Unidad', orientation='h')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎚️ Por Dificultad")
            if stats['por_dificultad']:
                fig = px.pie(
                    values=list(stats['por_dificultad'].values()),
                    names=list(stats['por_dificultad'].keys())
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # DEBUG INFO
        with st.expander("🔍 Debug Info"):
            st.write(f"**Ejercicios por lista directa:** {total_real}")
            st.write(f"**Ejercicios por stats:** {stats['total_ejercicios']}")
            st.write(f"**Por unidad:** {stats['por_unidad']}")
            st.write("**Primeros 3 ejercicios:**")
            for i, ej in enumerate(todos_ejercicios[:3]):
                st.write(f"{i+1}. {ej.get('titulo', 'Sin título')} - {ej.get('unidad_tematica', 'Sin unidad')}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()