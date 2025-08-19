"""
Generador de Documentos con Templates Profesionales PUC
Página: pages/04_📄_Generador_de_Documentos.py
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import streamlit as st
import os
from datetime import datetime, date
from pathlib import Path

# Importar dependencias del proyecto
try:
    from database.db_manager import DatabaseManager
    # Usamos ExercisePDFGenerator que es el wrapper de RealTemplatePDFGenerator
    from generators.pdf_generator import ExercisePDFGenerator
except ImportError:
    import sys
    sys.path.append('.')
    from database.db_manager import DatabaseManager
    from generators.pdf_generator import ExercisePDFGenerator

@st.cache_resource
def get_db_manager():
    """Carga y cachea una instancia del gestor de la base de datos."""
    return DatabaseManager(db_path="database/ejercicios.db")

@st.cache_resource
def get_pdf_generator():
    """Carga y cachea una instancia del generador de PDF profesional."""
    # ExercisePDFGenerator es un wrapper de RealTemplatePDFGenerator
    # y sabe dónde encontrar los templates por defecto.
    return ExercisePDFGenerator()

def get_instrucciones_default(tipo_documento):
    """Devuelve las instrucciones por defecto para cada tipo de documento."""
    if tipo_documento == "Prueba/Interrogación":
        return [
            "Lea cuidadosamente cada ejercicio antes de responder.",
            "Muestre claramente todos los pasos de desarrollo.",
            "Se puede usar calculadora científica.",
            "Escriba su nombre y RUT en todas las hojas."
        ]
    elif tipo_documento == "Tarea":
        return [
            "Fecha de entrega: Ver calendario del curso.",
            "Trabajo individual. Se puede discutir pero no compartir soluciones.",
            "Incluya todos los desarrollos y justificaciones.",
            "Puede usar MATLAB/Python para verificar resultados."
        ]
    else: # Guía de Ejercicios
        return [
            "Ejercicios para práctica y estudio personal.",
            "Se recomienda intentar resolver antes de ver las soluciones.",
            "Consulte en ayudantías si tiene dudas.",
            "Algunos ejercicios requieren uso de software."
        ]

def obtener_ejercicios_filtrados(db, unidades, dificultades, modalidades):
    """Obtiene ejercicios de la BD aplicando los filtros automáticos."""
    todos = db.obtener_ejercicios()
    filtrados = []
    for ej in todos:
        if unidades and ej.get('unidad_tematica') not in unidades:
            continue
        if dificultades and ej.get('nivel_dificultad') not in dificultades:
            continue
        if modalidades and ej.get('modalidad') not in modalidades:
            continue
        filtrados.append(ej)
    return filtrados

def display_and_edit_scores(ejercicios: list):
    """Muestra una UI para editar los puntajes de los ejercicios seleccionados."""
    st.subheader("⚖️ Asignación de Puntajes")

    if 'exercise_scores' not in st.session_state:
        st.session_state.exercise_scores = {}

    default_scores = {"Básico": 4, "Intermedio": 6, "Avanzado": 8, "Desafío": 10}
    for ej in ejercicios:
        if ej['id'] not in st.session_state.exercise_scores:
            st.session_state.exercise_scores[ej['id']] = default_scores.get(ej.get('nivel_dificultad', 'Intermedio'), 6)

    for ej in ejercicios:
        ej_id = ej['id']
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{ej.get('titulo', 'Sin título')}** ({ej.get('nivel_dificultad')})")
        with col2:
            score = st.number_input(
                "Puntaje",
                min_value=0,
                max_value=20,
                value=st.session_state.exercise_scores[ej_id],
                key=f"score_{ej_id}",
                label_visibility="collapsed"
            )
            st.session_state.exercise_scores[ej_id] = score

    current_ids = {ej['id'] for ej in ejercicios}
    total_score = sum(st.session_state.exercise_scores.get(ej_id, 0) for ej_id in current_ids)
    st.metric("Puntaje Total del Documento", total_score)

def get_template_name_real(tipo_documento):
    """Obtiene el nombre real del template según la estructura del proyecto."""
    if tipo_documento == "Prueba/Interrogación":
        return "prueba_template.tex"
    elif tipo_documento == "Tarea":
        return "tarea_template.tex"
    else:
        return "guia_template.tex"

def generar_con_templates_profesionales(tipo_documento, ejercicios, doc_info, incluir_soluciones, pdf_gen):
    """Genera documento usando RealTemplatePDFGenerator."""
    with st.spinner(f"🎨 Generando {tipo_documento} con templates profesionales PUC..."):
        try:
            doc_data = {
                'nombre': doc_info['titulo'],
                'profesor': doc_info['profesor'],
                'semestre': doc_info['semestre'],
                'fecha': doc_info['fecha'],
                'instrucciones': doc_info.get('instrucciones', []),
                'scores': doc_info.get('scores', {})
            }
            if doc_info.get('tiempo_total'):
                doc_data['tiempo_total'] = doc_info['tiempo_total']

            archivo_principal, archivo_soluciones = None, None

            if tipo_documento == "Prueba/Interrogación":
                resultado = pdf_gen.generate_prueba(ejercicios, doc_data, incluir_soluciones=incluir_soluciones)
                archivo_principal, archivo_soluciones = resultado if isinstance(resultado, tuple) else (resultado, None)
            elif tipo_documento == "Tarea":
                archivo_principal = pdf_gen.generate_tarea(ejercicios, doc_data, incluir_soluciones=incluir_soluciones)
            else:
                archivo_principal = pdf_gen.generate_guia(ejercicios, doc_data, incluir_soluciones=incluir_soluciones)

            if archivo_principal and os.path.exists(archivo_principal):
                st.success(f"✅ ¡{tipo_documento} generado con éxito!")
                archivo_path = Path(archivo_principal)

                if archivo_principal.endswith('.pdf'):
                    with open(archivo_principal, 'rb') as f:
                        st.download_button(f"📥 Descargar {tipo_documento} (PDF)", f.read(), archivo_path.name, "application/pdf", type="primary")
                    tex_path = archivo_path.with_suffix('.tex')
                    if tex_path.exists():
                        with open(tex_path, 'r', encoding='utf-8') as f:
                            st.download_button("📄 Descargar código LaTeX (.tex)", f.read(), tex_path.name, "text/plain")
                else:
                    st.warning("⚠️ Se generó .tex pero no se pudo compilar a PDF.")
                    with open(archivo_principal, 'r', encoding='utf-8') as f:
                        st.download_button(f"📄 Descargar {tipo_documento} (.tex)", f.read(), archivo_path.name, "text/plain", type="primary")

                if archivo_soluciones and os.path.exists(archivo_soluciones) and archivo_soluciones != archivo_principal:
                    st.success("✅ Versión con soluciones también generada.")
                    sol_path = Path(archivo_soluciones)
                    if archivo_soluciones.endswith('.pdf'):
                        with open(archivo_soluciones, 'rb') as f:
                            st.download_button("📥 Descargar Soluciones (PDF)", f.read(), sol_path.name, "application/pdf")

        except Exception as e:
            st.error(f"❌ Error con templates profesionales: {e}")
            with st.expander("🔍 Ver detalles del error"):
                import traceback
                st.code(traceback.format_exc())

def main():
    """Página para configurar y generar documentos PDF con los ejercicios seleccionados."""
    st.set_page_config(page_title="Generador de Documentos", page_icon="📄", layout="wide")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>🎯 Generador de Documentos Profesionales</h1>
        <p>Genera Pruebas, Tareas y Guías con templates profesionales PUC.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        db = get_db_manager()
        pdf_gen = get_pdf_generator()
        
        # Obtener ejercicios pre-seleccionados de la biblioteca
        ejercicios_seleccionados_ids = st.session_state.get('ejercicios_para_generar', [])

        # --- SIDEBAR DE CONFIGURACIÓN ---
        with st.sidebar:
            st.header("⚙️ Configuración del Documento")
            
            tipo_documento = st.selectbox(
                "📄 Tipo de Documento",
                ["Prueba/Interrogación", "Tarea", "Guía de Ejercicios"]
            )
            
            st.divider()
            st.subheader("🎯 Selección de Ejercicios")

            if ejercicios_seleccionados_ids:
                st.success(f"✅ {len(ejercicios_seleccionados_ids)} ejercicios pre-seleccionados desde la Biblioteca.")
                usar_seleccion_manual = True
                if st.button("🗑️ Limpiar selección"):
                    st.session_state.ejercicios_para_generar = []
                    st.rerun()
            else:
                st.info("💡 No hay pre-selección. Usa los filtros automáticos.")
                usar_seleccion_manual = False
                
                st.subheader("🔍 Filtros Automáticos")
                unidades = db.obtener_unidades_tematicas()
                unidades_sel = st.multiselect("Unidades", unidades, default=unidades[:2] if len(unidades) >= 2 else unidades)
                dificultades_sel = st.multiselect("Dificultad", ["Básico", "Intermedio", "Avanzado"], default=["Básico", "Intermedio"])
                modalidades_sel = st.multiselect("Modalidad", ["Teórico", "Computacional", "Mixto"], default=["Teórico"])
                num_ejercicios = st.slider("Cantidad", 1, 20, 5)
            
            st.divider()
            st.subheader("📋 Opciones de Generación")
            incluir_soluciones = st.checkbox("📝 Incluir Soluciones", value=(tipo_documento != "Prueba/Interrogación"))

        # --- ÁREA PRINCIPAL ---
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"📄 Configurar Metadatos: {tipo_documento}")
            
            with st.form("config_documento"):
                titulo = st.text_input("Título del Documento", value=f"{tipo_documento.split('/')[0]} - Señales y Sistemas")
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    profesor = st.text_input("Profesor", value="Patricio de la Cuadra")
                    semestre = st.text_input("Semestre", value="2025-1")
                with col_info2:
                    fecha_doc = st.date_input("Fecha", value=date.today())
                    tiempo_total = st.number_input("Tiempo Total (min)", min_value=30, max_value=180, value=90, step=15) if tipo_documento == "Prueba/Interrogación" else None
                
                instrucciones = st.text_area(
                    "Instrucciones (una por línea)",
                    value="\n".join(get_instrucciones_default(tipo_documento)),
                    height=100
                )
                
                generar_btn = st.form_submit_button(f"🚀 Generar {tipo_documento}", type="primary", use_container_width=True)

        # Determinar la lista final de ejercicios
        if usar_seleccion_manual:
            todos_ejercicios = db.obtener_ejercicios()
            ejercicios_finales = [ej for ej in todos_ejercicios if ej['id'] in ejercicios_seleccionados_ids]
        else:
            ejercicios_finales = obtener_ejercicios_filtrados(db, unidades_sel, dificultades_sel, modalidades_sel)[:num_ejercicios]

        with col2:
            if not ejercicios_finales:
                st.warning("No hay ejercicios que cumplan los criterios de selección.")
            else:
                display_and_edit_scores(ejercicios_finales)

        # --- LÓGICA DE GENERACIÓN ---
        if generar_btn and ejercicios_finales:
            doc_info = {
                'titulo': titulo,
                'profesor': profesor,
                'semestre': semestre,
                'fecha': fecha_doc.strftime('%d de %B, %Y'),
                'tiempo_total': tiempo_total,
                'instrucciones': [inst.strip() for inst in instrucciones.split('\n') if inst.strip()],
                'scores': st.session_state.get('exercise_scores', {})
            }
            generar_con_templates_profesionales(tipo_documento, ejercicios_finales, doc_info, incluir_soluciones, pdf_gen)
        elif generar_btn:
            st.error("No hay ejercicios seleccionados para generar el documento.")

    except Exception as e:
        st.error("💥 Ha ocurrido un error inesperado en la página.")
        with st.expander("Ver detalles técnicos del error"):
            import traceback
            st.code(traceback.format_exc())
            
if __name__ == "__main__":
    main()
