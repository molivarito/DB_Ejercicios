"""
Búsqueda de Ejercicios con Selección para Documentos
Página: 03_🔍_Buscar_Ejercicios.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Importar dependencias
try:
    from database.db_manager import DatabaseManager
except ImportError:
    import sys
    sys.path.append('.')
    from database.db_manager import DatabaseManager

def main():
    st.set_page_config(
        page_title="Buscar Ejercicios",
        page_icon="🔍",
        layout="wide"
    )
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>🔍 Buscar y Seleccionar Ejercicios</h1>
        <p>Busca ejercicios y selecciona los que quieres incluir en tus documentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db = DatabaseManager()
        
        # Inicializar session state para ejercicios seleccionados
        if 'ejercicios_seleccionados' not in st.session_state:
            st.session_state.ejercicios_seleccionados = []
        
        # SIDEBAR CON FILTROS
        with st.sidebar:
            st.header("🔍 Filtros de Búsqueda")
            
            # Obtener datos para filtros
            ejercicios = db.obtener_ejercicios()
            unidades = db.obtener_unidades_tematicas()
            
            # Filtros
            unidades_filtro = st.multiselect(
                "🎯 Unidades Temáticas",
                unidades,
                default=[],
                help="Selecciona unidades específicas o deja vacío para todas"
            )
            
            dificultades_filtro = st.multiselect(
                "🎚️ Nivel de Dificultad",
                ["Básico", "Intermedio", "Avanzado", "Desafío"],
                default=[],
                help="Selecciona niveles específicos o deja vacío para todos"
            )
            
            modalidades_filtro = st.multiselect(
                "💻 Modalidad",
                ["Teórico", "Computacional", "Mixto"],
                default=[],
                help="Selecciona modalidades específicas"
            )
            
            # Búsqueda por texto
            texto_busqueda = st.text_input(
                "🔎 Buscar en título/contenido",
                placeholder="Ej: convolución, fourier, laplace..."
            )
            
            st.divider()
            
            # CARRITO DE SELECCIÓN
            st.header("🛒 Ejercicios Seleccionados")
            st.write(f"**Total:** {len(st.session_state.ejercicios_seleccionados)}")
            
            if st.session_state.ejercicios_seleccionados:
                # Mostrar resumen
                for i, ej_id in enumerate(st.session_state.ejercicios_seleccionados, 1):
                    ej = next((e for e in ejercicios if e['id'] == ej_id), None)
                    if ej:
                        st.write(f"{i}. {ej.get('titulo', 'Sin título')[:30]}...")
                
                # Botones de acción
                if st.button("🗑️ Limpiar Selección", use_container_width=True):
                    st.session_state.ejercicios_seleccionados = []
                    st.rerun()
                
                if st.button("🎯 Ir a Generar Documento", type="primary", use_container_width=True):
                    # Pasar ejercicios seleccionados a la página de generación
                    st.session_state.ejercicios_para_documento = st.session_state.ejercicios_seleccionados.copy()
                    st.success("✅ Ejercicios listos para generar documento!")
                    st.info("👉 Ve a la página **05_🎯_Generar_Prueba** para crear tu documento")
            
            else:
                st.info("Selecciona ejercicios de la lista principal")
        
        # ÁREA PRINCIPAL - RESULTADOS DE BÚSQUEDA
        
        # Aplicar filtros
        ejercicios_filtrados = ejercicios.copy()
        
        # Filtro por unidades
        if unidades_filtro:
            ejercicios_filtrados = [e for e in ejercicios_filtrados 
                                  if e.get('unidad_tematica') in unidades_filtro]
        
        # Filtro por dificultad
        if dificultades_filtro:
            ejercicios_filtrados = [e for e in ejercicios_filtrados 
                                  if e.get('nivel_dificultad') in dificultades_filtro]
        
        # Filtro por modalidad
        if modalidades_filtro:
            ejercicios_filtrados = [e for e in ejercicios_filtrados 
                                  if e.get('modalidad') in modalidades_filtro]
        
        # Filtro por texto
        if texto_busqueda:
            texto_lower = texto_busqueda.lower()
            ejercicios_filtrados = [e for e in ejercicios_filtrados 
                                  if (texto_lower in e.get('titulo', '').lower() or 
                                      texto_lower in e.get('enunciado', '').lower() or
                                      texto_lower in e.get('unidad_tematica', '').lower())]
        
        # Mostrar estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Total Disponibles", len(ejercicios))
        with col2:
            st.metric("🔍 Filtrados", len(ejercicios_filtrados))
        with col3:
            st.metric("✅ Seleccionados", len(st.session_state.ejercicios_seleccionados))
        
        st.divider()
        
        # LISTA DE EJERCICIOS CON SELECCIÓN
        if ejercicios_filtrados:
            st.subheader(f"📋 Ejercicios Encontrados ({len(ejercicios_filtrados)})")
            
            # Opción de seleccionar todos los filtrados
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("✅ Seleccionar Todos los Filtrados"):
                    for ej in ejercicios_filtrados:
                        if ej['id'] not in st.session_state.ejercicios_seleccionados:
                            st.session_state.ejercicios_seleccionados.append(ej['id'])
                    st.rerun()
            
            # Mostrar ejercicios con checkboxes
            for ejercicio in ejercicios_filtrados:
                mostrar_ejercicio_con_seleccion(ejercicio)
                
        else:
            st.warning("🔍 No se encontraron ejercicios con los filtros aplicados")
            if unidades_filtro or dificultades_filtro or modalidades_filtro or texto_busqueda:
                st.info("💡 Intenta reducir los filtros o cambiar los términos de búsqueda")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def mostrar_ejercicio_con_seleccion(ejercicio):
    """Muestra un ejercicio con opción de selección"""
    
    # Container para el ejercicio
    with st.container():
        col_check, col_content = st.columns([0.1, 0.9])
        
        # Checkbox de selección
        with col_check:
            ejercicio_seleccionado = st.checkbox(
                "",
                value=ejercicio['id'] in st.session_state.ejercicios_seleccionados,
                key=f"check_{ejercicio['id']}",
                help="Seleccionar para documento"
            )
            
            # Actualizar estado de selección
            if ejercicio_seleccionado:
                if ejercicio['id'] not in st.session_state.ejercicios_seleccionados:
                    st.session_state.ejercicios_seleccionados.append(ejercicio['id'])
            else:
                if ejercicio['id'] in st.session_state.ejercicios_seleccionados:
                    st.session_state.ejercicios_seleccionados.remove(ejercicio['id'])
        
        # Contenido del ejercicio
        with col_content:
            # Header con título y metadatos
            col_title, col_meta = st.columns([2, 1])
            
            with col_title:
                st.markdown(f"### {ejercicio.get('titulo', 'Sin título')}")
            
            with col_meta:
                # Badges de información
                if ejercicio.get('unidad_tematica'):
                    st.markdown(f"🎯 **{ejercicio['unidad_tematica']}**")
                if ejercicio.get('nivel_dificultad'):
                    color = {"Básico": "green", "Intermedio": "orange", "Avanzado": "red", "Desafío": "purple"}.get(ejercicio['nivel_dificultad'], "blue")
                    st.markdown(f":{color}[🎚️ {ejercicio['nivel_dificultad']}]")
                if ejercicio.get('tiempo_estimado'):
                    st.markdown(f"⏱️ **{ejercicio['tiempo_estimado']} min**")
            
            # Enunciado (preview)
            if ejercicio.get('enunciado'):
                enunciado_preview = ejercicio['enunciado'][:200]
                if len(ejercicio['enunciado']) > 200:
                    enunciado_preview += "..."
                st.write(enunciado_preview)
            
            # Información adicional en expander
            with st.expander("👁️ Ver detalles completos"):
                # Enunciado completo
                if ejercicio.get('enunciado'):
                    st.write("**Enunciado completo:**")
                    st.write(ejercicio['enunciado'])
                
                # Datos de entrada
                if ejercicio.get('datos_entrada'):
                    st.write("**Datos:**")
                    st.write(ejercicio['datos_entrada'])
                
                # Solución
                if ejercicio.get('solucion_completa'):
                    st.write("**Solución:**")
                    st.write(ejercicio['solucion_completa'])
                
                # Código Python
                if ejercicio.get('codigo_python'):
                    st.write("**Código Python:**")
                    st.code(ejercicio['codigo_python'], language='python')
                
                # Metadatos adicionales
                col1, col2 = st.columns(2)
                with col1:
                    if ejercicio.get('modalidad'):
                        st.write(f"**Modalidad:** {ejercicio['modalidad']}")
                    if ejercicio.get('fuente'):
                        st.write(f"**Fuente:** {ejercicio['fuente']}")
                
                with col2:
                    if ejercicio.get('fecha_creacion'):
                        fecha = ejercicio['fecha_creacion'][:10] if len(ejercicio['fecha_creacion']) > 10 else ejercicio['fecha_creacion']
                        st.write(f"**Creado:** {fecha}")
                    st.write(f"**ID:** {ejercicio['id']}")
        
        st.divider()

if __name__ == "__main__":
    main()