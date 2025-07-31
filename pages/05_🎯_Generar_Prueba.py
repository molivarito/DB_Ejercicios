"""
Generador de Documentos con Templates Profesionales PUC
Página: 05_🎯_Generar_Prueba.py
"""

import streamlit as st
import os
import shutil
from datetime import datetime, date
from pathlib import Path

try:
    from database.db_manager import DatabaseManager
    from generators.pdf_generator import ExercisePDFGenerator
except ImportError:
    import sys
    sys.path.append('.')
    from database.db_manager import DatabaseManager
    from generators.pdf_generator import ExercisePDFGenerator

def main():
    st.set_page_config(page_title="Generar Documentos", page_icon="🎯", layout="wide")
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5984 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1>🎯 Generador de Documentos Profesionales</h1>
        <p>Genera Pruebas, Tareas y Guías con templates profesionales PUC</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db = DatabaseManager()
        
        # Verificar si tienes tu PDF generator optimizado
        try:
            # Intentar crear el generador - tu versión usa RealTemplatePDFGenerator
            pdf_gen = ExercisePDFGenerator()
            
            # Verificar que tenga los métodos correctos
            metodos_requeridos = ['generate_prueba', 'generate_tarea', 'generate_guia']
            metodos_disponibles = [m for m in metodos_requeridos if hasattr(pdf_gen, m)]
            
            if len(metodos_disponibles) >= 3:
                usar_templates_profesionales = True
                st.success(f"✅ Templates profesionales PUC detectados - Métodos: {metodos_disponibles}")
            else:
                usar_templates_profesionales = False
                st.warning(f"⚠️ Templates parciales - Solo detectados: {metodos_disponibles}")
                
        except Exception as e:
            usar_templates_profesionales = False
            st.warning(f"⚠️ Templates profesionales no encontrados - {str(e)}")
            st.info("💡 Usando generación LaTeX básica como fallback")
        
        ejercicios_seleccionados_ids = st.session_state.get('ejercicios_para_documento', [])
        
        # SIDEBAR
        with st.sidebar:
            st.header("⚙️ Configuración")
            
            tipo_documento = st.selectbox(
                "📄 Tipo de Documento",
                ["Prueba/Interrogación", "Tarea", "Guía de Ejercicios"],
                help="Selecciona el formato del documento (usa templates profesionales PUC)"
            )
            
            st.divider()
            
            # Información sobre templates
            if usar_templates_profesionales:
                st.success("🎨 Usando templates profesionales:")
                if tipo_documento == "Prueba/Interrogación":
                    st.write("📄 `prueba_template.tex`")
                elif tipo_documento == "Tarea":
                    st.write("📄 `tarea_template.tex`")
                else:
                    st.write("📄 `guia_template.tex`")
            
            st.subheader("🎯 Selección de Ejercicios")
            
            # Método de selección
            if ejercicios_seleccionados_ids:
                st.success(f"✅ {len(ejercicios_seleccionados_ids)} ejercicios pre-seleccionados")
                usar_seleccionados = True
                
                if st.button("🔍 Seleccionar más ejercicios"):
                    st.info("👉 Ve a **03_🔍_Buscar_Ejercicios**")
                
                if st.button("🗑️ Limpiar selección"):
                    st.session_state.ejercicios_para_documento = []
                    st.rerun()
            else:
                st.info("💡 Selecciona ejercicios específicos en **Buscar Ejercicios** o usa filtros automáticos")
                usar_seleccionados = False
                
                # Filtros automáticos
                st.subheader("🔍 Filtros Automáticos")
                unidades = db.obtener_unidades_tematicas()
                unidades_sel = st.multiselect("🎯 Unidades", unidades, default=unidades[:2] if len(unidades) >= 2 else unidades)
                dificultades_sel = st.multiselect("🎚️ Dificultad", ["Básico", "Intermedio", "Avanzado"], default=["Básico", "Intermedio"])
                modalidades_sel = st.multiselect("💻 Modalidad", ["Teórico", "Computacional", "Mixto"], default=["Teórico"])
                num_ejercicios = st.slider("📊 Cantidad", 1, 15, 4 if tipo_documento == "Prueba/Interrogación" else 8)
            
            st.divider()
            
            st.subheader("📋 Opciones")
            incluir_soluciones = st.checkbox("📝 Incluir Soluciones", value=(tipo_documento != "Prueba/Interrogación"))
            
            # Método de generación
            metodo_generacion = st.radio(
                "🎨 Método de Generación:",
                ["Templates Profesionales PUC", "Generación LaTeX Básica"],
                help="Templates profesionales usan tus archivos .tex optimizados"
            )
        
        # ÁREA PRINCIPAL
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📄 Configurar {tipo_documento}")
            
            with st.form("config_documento"):
                titulo = st.text_input("Título del Documento", value=f"{tipo_documento.split('/')[0]} - Señales y Sistemas")
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    profesor = st.text_input("Profesor", value="Patricio de la Cuadra")
                    semestre = st.text_input("Semestre", value="2024-2")
                with col_info2:
                    fecha_doc = st.date_input("Fecha", value=date.today())
                    if tipo_documento == "Prueba/Interrogación":
                        tiempo_total = st.number_input("Tiempo Total (min)", min_value=30, max_value=180, value=90, step=15)
                    else:
                        tiempo_total = None
                
                instrucciones_default = get_instrucciones_default(tipo_documento)
                instrucciones = st.text_area(
                    "Instrucciones (una por línea)",
                    value="\n".join(instrucciones_default),
                    height=100
                )
                
                generar_btn = st.form_submit_button(
                    f"🎯 Generar {tipo_documento}",
                    type="primary",
                    use_container_width=True
                )
        
        with col2:
            st.subheader("📊 Vista Previa")
            
            # Obtener ejercicios según método
            if usar_seleccionados and ejercicios_seleccionados_ids:
                todos_ejercicios = db.obtener_ejercicios()
                ejercicios_finales = [ej for ej in todos_ejercicios if ej['id'] in ejercicios_seleccionados_ids]
                st.success(f"✅ Usando {len(ejercicios_finales)} ejercicios pre-seleccionados")
            else:
                ejercicios_finales = obtener_ejercicios_filtrados(db, unidades_sel, dificultades_sel, modalidades_sel)[:num_ejercicios]
                st.info(f"🔍 {len(ejercicios_finales)} ejercicios filtrados automáticamente")
            
            # Mostrar distribución
            if ejercicios_finales:
                mostrar_distribucion_ejercicios(ejercicios_finales)
                
                with st.expander("👁️ Lista de Ejercicios", expanded=False):
                    for i, ej in enumerate(ejercicios_finales, 1):
                        st.write(f"**{i}.** {ej.get('titulo', 'Sin título')}")
                        st.write(f"   🎯 {ej.get('unidad_tematica', 'N/A')} | 🎚️ {ej.get('nivel_dificultad', 'N/A')} | ⏱️ {ej.get('tiempo_estimado', 'N/A')} min")
        
        # GENERACIÓN DEL DOCUMENTO
        if generar_btn and ejercicios_finales:
            doc_info = {
                'titulo': titulo,
                'profesor': profesor,
                'semestre': semestre,
                'fecha': fecha_doc.strftime('%d de %B, %Y'),
                'tiempo_total': tiempo_total,
                'instrucciones': [inst.strip() for inst in instrucciones.split('\n') if inst.strip()]
            }
            
            if metodo_generacion == "Templates Profesionales PUC" and usar_templates_profesionales:
                generar_con_templates_profesionales(tipo_documento, ejercicios_finales, doc_info, incluir_soluciones, pdf_gen)
            else:
                generar_con_latex_basico(tipo_documento, ejercicios_finales, doc_info, incluir_soluciones)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def get_instrucciones_default(tipo_documento):
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
    else:
        return [
            "Ejercicios para práctica y estudio personal.",
            "Se recomienda intentar resolver antes de ver las soluciones.",
            "Consulte en ayudantías si tiene dudas.",
            "Algunos ejercicios requieren uso de software."
        ]

def obtener_ejercicios_filtrados(db, unidades, dificultades, modalidades):
    todos = db.obtener_ejercicios()
    filtrados = []
    for ej in todos:
        # Filtro por unidad
        if unidades and ej.get('unidad_tematica') not in unidades:
            continue
        # Filtro por dificultad  
        if dificultades and ej.get('nivel_dificultad') not in dificultades:
            continue
        # Filtro por modalidad
        if modalidades and ej.get('modalidad') not in modalidades:
            continue
        filtrados.append(ej)
    return filtrados

def mostrar_distribucion_ejercicios(ejercicios):
    """Muestra distribución de ejercicios seleccionados"""
    unidades = {}
    dificultades = {}
    for ej in ejercicios:
        unidad = ej.get('unidad_tematica', 'Sin unidad')
        dificultad = ej.get('nivel_dificultad', 'Sin dificultad')
        unidades[unidad] = unidades.get(unidad, 0) + 1
        dificultades[dificultad] = dificultades.get(dificultad, 0) + 1
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Por Unidad:**")
        for unidad, cant in unidades.items():
            st.write(f"• {unidad}: {cant}")
    
    with col2:
        st.write("**Por Dificultad:**")
        for dif, cant in dificultades.items():
            st.write(f"• {dif}: {cant}")

def generar_con_templates_profesionales(tipo_documento, ejercicios, doc_info, incluir_soluciones, pdf_gen):
    """Genera documento usando tu RealTemplatePDFGenerator"""
    
    with st.spinner(f"🎨 Generando {tipo_documento} con templates profesionales PUC..."):
        try:
            # Preparar información para tu generador
            doc_data = {
                'nombre': doc_info['titulo'],
                'profesor': doc_info['profesor'], 
                'semestre': doc_info['semestre'],
                'fecha': doc_info['fecha'],
                'instrucciones': doc_info.get('instrucciones', [])
            }
            
            if doc_info.get('tiempo_total'):
                doc_data['tiempo_total'] = doc_info['tiempo_total']
            
            archivo_principal = None
            archivo_soluciones = None
            
            # Usar TUS métodos reales según el tipo de documento
            if tipo_documento == "Prueba/Interrogación":
                st.info("📄 Usando template: prueba_template.tex")
                resultado = pdf_gen.generate_prueba(ejercicios, doc_data, incluir_soluciones=incluir_soluciones)
                
                # Tu método retorna una tupla (principal, soluciones)
                if isinstance(resultado, tuple):
                    archivo_principal, archivo_soluciones = resultado
                else:
                    archivo_principal = resultado
                    
            elif tipo_documento == "Tarea":
                st.info("📄 Usando template: tarea_template.tex")
                archivo_principal = pdf_gen.generate_tarea(ejercicios, doc_data, incluir_soluciones=incluir_soluciones)
                
            else:  # Guía
                st.info("📄 Usando template: guia_template.tex")
                archivo_principal = pdf_gen.generate_guia(ejercicios, doc_data, incluir_soluciones=incluir_soluciones)
            
            # Verificar que se generó el archivo
            if archivo_principal and os.path.exists(archivo_principal):
                st.success(f"✅ {tipo_documento} generado con template profesional PUC!")
                
                # Información del archivo
                archivo_path = Path(archivo_principal)
                st.info(f"📁 Archivo: `{archivo_path.name}`")
                st.info(f"📂 Ubicación: `{archivo_path.parent}`")
                
                # Determinar si es PDF o TEX
                if archivo_principal.endswith('.pdf'):
                    st.success("🎯 PDF compilado exitosamente!")
                    
                    # Ofrecer descarga del PDF
                    with open(archivo_principal, 'rb') as f:
                        st.download_button(
                            label=f"📥 Descargar {tipo_documento} (PDF)",
                            data=f.read(),
                            file_name=archivo_path.name,
                            mime="application/pdf",
                            type="primary"
                        )
                        
                    # También buscar el .tex correspondiente
                    tex_path = archivo_path.with_suffix('.tex')
                    if tex_path.exists():
                        with open(tex_path, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label="📄 Descargar código LaTeX (.tex)",
                                data=f.read(),
                                file_name=tex_path.name,
                                mime="text/plain"
                            )
                            
                else:
                    st.warning("⚠️ Se generó archivo .tex pero no se pudo compilar a PDF")
                    
                    # Ofrecer descarga del .tex
                    with open(archivo_principal, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label=f"📄 Descargar {tipo_documento} (.tex)",
                            data=f.read(),
                            file_name=archivo_path.name,
                            mime="text/plain",
                            type="primary"
                        )
                    
                    st.info("💡 Puedes compilar el .tex en Overleaf o con pdflatex local")
                
                # Archivo de soluciones si existe (solo para pruebas)
                if archivo_soluciones and os.path.exists(archivo_soluciones) and archivo_soluciones != archivo_principal:
                    st.success("✅ Versión con soluciones también generada!")
                    sol_path = Path(archivo_soluciones)
                    
                    if archivo_soluciones.endswith('.pdf'):
                        with open(archivo_soluciones, 'rb') as f:
                            st.download_button(
                                label="📥 Descargar Soluciones (PDF)",
                                data=f.read(),
                                file_name=sol_path.name,
                                mime="application/pdf"
                            )
                    else:
                        with open(archivo_soluciones, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label="📄 Descargar Soluciones (.tex)",
                                data=f.read(),
                                file_name=sol_path.name,
                                mime="text/plain"
                            )
                
                # Información detallada del documento
                with st.expander("👁️ Información del Documento Generado"):
                    st.write(f"**Tipo:** {tipo_documento}")
                    st.write(f"**Template usado:** {get_template_name_real(tipo_documento)}")
                    st.write(f"**Generador:** RealTemplatePDFGenerator")
                    st.write(f"**Ejercicios incluidos:** {len(ejercicios)}")
                    st.write(f"**Formato final:** {'PDF' if archivo_principal.endswith('.pdf') else 'LaTeX (.tex)'}")
                    
                    st.write("**Lista de ejercicios:**")
                    for i, ej in enumerate(ejercicios, 1):
                        st.write(f"{i}. {ej.get('titulo', 'Sin título')} ({ej.get('unidad_tematica', 'N/A')})")
                        
                    st.write("**Configuración del documento:**")
                    st.write(f"- Título: {doc_data['nombre']}")
                    st.write(f"- Profesor: {doc_data['profesor']}")
                    st.write(f"- Semestre: {doc_data['semestre']}")
                    st.write(f"- Fecha: {doc_data['fecha']}")
                    if doc_data.get('tiempo_total'):
                        st.write(f"- Tiempo: {doc_data['tiempo_total']} minutos")
            
            else:
                st.error("❌ Error: No se pudo generar el documento")
                st.write(f"**Archivo esperado:** {archivo_principal}")
                st.write(f"**¿Existe?:** {os.path.exists(archivo_principal) if archivo_principal else 'No se generó'}")
                
                # Verificar templates
                st.write("**Verificación de templates:**")
                template_name = get_template_name_real(tipo_documento)
                template_path = Path("templates") / template_name
                st.write(f"- Template: {template_name}")
                st.write(f"- Ruta: {template_path}")
                st.write(f"- ¿Existe?: {template_path.exists()}")
                
                st.info("💡 Intenta con 'Generación LaTeX Básica' como alternativa")
                
        except Exception as e:
            st.error(f"❌ Error con templates profesionales: {str(e)}")
            
            # Debug detallado
            with st.expander("🔍 Debug Info Completo"):
                st.write("**Información del generador:**")
                st.write(f"Tipo: {type(pdf_gen)}")
                st.write(f"Clase base: {pdf_gen.__class__.__bases__}")
                
                st.write("**Métodos disponibles:**")
                metodos = [m for m in dir(pdf_gen) if not m.startswith('_') and callable(getattr(pdf_gen, m))]
                st.write(metodos)
                
                st.write("**Templates esperados:**")
                if hasattr(pdf_gen, 'required_templates'):
                    st.write(pdf_gen.required_templates)
                
                st.write("**Directorio de templates:**")
                if hasattr(pdf_gen, 'templates_dir'):
                    st.write(f"Ruta: {pdf_gen.templates_dir}")
                    st.write(f"¿Existe?: {pdf_gen.templates_dir.exists()}")
                
                st.write("**Error completo:**")
                import traceback
                st.code(traceback.format_exc())
            
            st.info("💡 Usa 'Generación LaTeX Básica' mientras investigamos el problema")

def get_template_name_real(tipo_documento):
    """Obtiene el nombre real del template según tu estructura"""
    if tipo_documento == "Prueba/Interrogación":
        return "prueba_template.tex"
    elif tipo_documento == "Tarea":
        return "tarea_template.tex"
    else:
        return "guia_template.tex"

def generar_con_latex_basico(tipo_documento, ejercicios, doc_info, incluir_soluciones):
    """Fallback: Generación LaTeX básica sin templates"""
    
    with st.spinner(f"📄 Generando {tipo_documento} con LaTeX básico..."):
        try:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{tipo_documento.lower().replace('/', '_').replace(' ', '_')}_{timestamp}"
            
            # Generar LaTeX básico
            latex_content = crear_latex_basico(ejercicios, doc_info, incluir_soluciones)
            
            # Guardar .tex
            tex_path = output_dir / f"{filename}.tex"
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            st.success(f"✅ Archivo .tex generado: {tex_path}")
            
            # Descargar .tex
            with open(tex_path, 'r', encoding='utf-8') as f:
                st.download_button("📄 Descargar .tex", f.read(), f"{filename}.tex", "text/plain")
            
            st.info("💡 Para obtener formato profesional PUC, asegúrate de que los templates estén disponibles")
                
        except Exception as e:
            st.error(f"❌ Error en generación básica: {str(e)}")

def crear_latex_basico(ejercicios, doc_info, incluir_soluciones):
    """Generación LaTeX básica como fallback"""
    
    # Crear el contenido LaTeX sin f-strings problemáticos
    titulo = doc_info['titulo']
    profesor = doc_info['profesor']
    semestre = doc_info['semestre']
    fecha = doc_info['fecha']
    
    # Generar ejercicios
    ejercicios_latex = ""
    for i, ej in enumerate(ejercicios, 1):
        titulo_ej = ej.get('titulo', 'Sin título')
        enunciado = ej.get('enunciado', '')
        ejercicios_latex += f"\\subsection*{{Ejercicio {i}: {titulo_ej}}}\n{enunciado}\n\\vspace{{2cm}}\n\n"
    
    # Documento completo
    documento = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[spanish]{{babel}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{geometry}}
\\geometry{{margin=2.5cm}}

\\begin{{document}}
\\begin{{center}}
{{\\Large\\textbf{{{titulo}}}}}\\\\[0.5cm]
{profesor} \\hfill {semestre}\\\\
{fecha}
\\end{{center}}

\\section*{{Ejercicios}}
{ejercicios_latex}

\\end{{document}}"""
    
    return documento

if __name__ == "__main__":
    main()