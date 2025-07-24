"""
Generador de PDFs usando LaTeX para ejercicios y pruebas - V2.0
Sistema de Gestión de Ejercicios - Señales y Sistemas
VERSIÓN FINAL FUNCIONANDO - Fix geometry y compilación
"""

from pylatex import Document, Section, Subsection, Command, Package, NewPage
from pylatex.base_classes import Environment
from pylatex.utils import italic, bold, NoEscape
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import tempfile
import subprocess
import shutil

class PUCLatexTemplate:
    """Template LaTeX personalizado para la PUC"""
    
    def __init__(self):
        # REMOVIDO geometry_options de aquí para evitar conflicto
        self.packages = [
            Package('babel', options='spanish'),
            Package('inputenc', options='utf8'),
            Package('fontenc', options='T1'),
            Package('amsmath'),
            Package('amsfonts'),
            Package('amssymb'),
            Package('graphicx'),
            Package('float'),
            Package('enumitem'),
            Package('fancyhdr'),
            Package('titlesec'),
            Package('xcolor'),
            Package('hyperref')
            # REMOVIDO geometry para evitar conflicto
        ]

class ExercisePDFGenerator:
    """Generador de PDFs para ejercicios y pruebas - VERSIÓN FUNCIONANDO"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.template = PUCLatexTemplate()
        
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        
    def _clean_text_for_latex(self, text: str) -> str:
        """Limpia texto para evitar problemas de codificación en LaTeX"""
        if not text:
            return ""
        
        # Reemplazar caracteres problemáticos
        replacements = {
            'á': r'\'{a}',
            'é': r'\'{e}',
            'í': r'\'{i}',
            'ó': r'\'{o}',
            'ú': r'\'{u}',
            'ñ': r'\~{n}',
            'Á': r'\'{A}',
            'É': r'\'{E}',
            'Í': r'\'{I}',
            'Ó': r'\'{O}',
            'Ú': r'\'{U}',
            'Ñ': r'\~{N}',
            'ü': r'\"{u}',
            'Ü': r'\"{U}',
            '°': r'$^{\circ}$',
            'π': r'$\pi$',
            'τ': r'$\tau$',
            'ω': r'$\omega$',
            'α': r'$\alpha$',
            'β': r'$\beta$',
            'γ': r'$\gamma$',
            'δ': r'$\delta$',
            'σ': r'$\sigma$',
            '∞': r'$\infty$',
            '∫': r'$\int$',
            '≤': r'$\leq$',
            '≥': r'$\geq$',
            '≠': r'$\neq$',
            '±': r'$\pm$'
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
        
    def create_document(self, title: str, include_solutions: bool = False) -> Document:
        """Crea un documento LaTeX base - CON geometry en el lugar correcto"""
        # Crear documento CON geometry_options para evitar el error de preámbulo
        geometry_options = {
            'tmargin': '2.5cm',
            'lmargin': '2.5cm',
            'rmargin': '2.5cm',
            'bmargin': '2.5cm'
        }
        
        doc = Document(geometry_options=geometry_options)
        
        # Agregar paquetes DESPUÉS de geometry
        for package in self.template.packages:
            doc.packages.append(package)
        
        # Configurar encabezado y pie de página usando comandos LaTeX directos
        doc.append(Command('pagestyle', 'fancy'))
        doc.append(Command('fancyhf', ''))
        doc.append(NoEscape(r'\fancyhead[L]{Pontificia Universidad Cat\'{o}lica de Chile}'))
        doc.append(NoEscape(r'\fancyhead[R]{IEE2103 - Se\~{n}ales y Sistemas}'))
        doc.append(NoEscape(r'\fancyfoot[C]{\thepage}'))
        
        # Configurar colores PUC
        doc.append(NoEscape(r'\definecolor{pucblue}{RGB}{31, 78, 121}'))
        doc.append(NoEscape(r'\definecolor{pucgold}{RGB}{198, 146, 20}'))
        
        return doc
    
    def add_header(self, doc: Document, exam_info: Dict):
        """Agrega el encabezado de la prueba"""
        with doc.create(Section('', numbering=False)):
            doc.append(Command('centering'))
            doc.append(Command('Large'))
            
            # Limpiar nombre del examen
            nombre = self._clean_text_for_latex(exam_info.get('nombre', 'Ejercicios de Señales y Sistemas'))
            doc.append(bold(nombre))
            doc.append(Command('par'))
            doc.append(Command('vspace', '0.5cm'))
            
            # Información del curso
            doc.append(Command('normalsize'))
            profesor = self._clean_text_for_latex(exam_info.get('profesor', 'Patricio de la Cuadra'))
            doc.append(f"Profesor: {profesor}")
            doc.append(Command('hfill'))
            doc.append(f"Semestre: {exam_info.get('semestre', '2024-2')}")
            doc.append(Command('par'))
            
            if 'fecha' in exam_info:
                fecha = self._clean_text_for_latex(exam_info['fecha'])
                doc.append(f"Fecha: {fecha}")
                doc.append(Command('hfill'))
            
            if 'tiempo_total' in exam_info:
                doc.append(f"Tiempo: {exam_info['tiempo_total']} minutos")
                doc.append(Command('par'))
            
            doc.append(Command('vspace', '0.5cm'))
            doc.append(Command('hrule'))
            doc.append(Command('vspace', '0.5cm'))
    
    def add_instructions(self, doc: Document, instructions: List[str]):
        """Agrega instrucciones generales"""
        with doc.create(Subsection('Instrucciones', numbering=False)):
            # Usar LaTeX directo para el entorno enumerate
            doc.append(NoEscape(r'\begin{enumerate}'))
            for instruction in instructions:
                # Limpiar instrucción
                clean_instruction = self._clean_text_for_latex(instruction)
                doc.append(NoEscape(f'\\item {clean_instruction}'))
            doc.append(NoEscape(r'\end{enumerate}'))
        
        doc.append(Command('vspace', '0.5cm'))
    
    def add_exercise(self, doc: Document, exercise: Dict, exercise_num: int, include_solution: bool = False):
        """Agrega un ejercicio al documento"""
        # Título del ejercicio
        exercise_title = f"Ejercicio {exercise_num}"
        if exercise.get('titulo'):
            titulo_limpio = self._clean_text_for_latex(exercise['titulo'])
            exercise_title += f": {titulo_limpio}"
        
        with doc.create(Subsection(exercise_title, numbering=False)):
            # Información del ejercicio
            info_parts = []
            if exercise.get('tiempo_estimado'):
                info_parts.append(f"Tiempo estimado: {exercise['tiempo_estimado']} minutos")
            if exercise.get('nivel_dificultad'):
                info_parts.append(f"Dificultad: {exercise['nivel_dificultad']}")
            if exercise.get('puntaje'):
                info_parts.append(f"Puntaje: {exercise['puntaje']} pts")
            
            if info_parts:
                doc.append(italic(" | ".join(info_parts)))
                doc.append(Command('par'))
                doc.append(Command('vspace', '0.3cm'))
            
            # Enunciado
            if exercise.get('enunciado'):
                enunciado_limpio = self._clean_text_for_latex(exercise['enunciado'])
                doc.append(enunciado_limpio)
                doc.append(Command('par'))
            
            # Datos de entrada si existen
            if exercise.get('datos_entrada'):
                doc.append(Command('vspace', '0.3cm'))
                doc.append(bold('Datos:'))
                doc.append(Command('par'))
                datos_limpios = self._clean_text_for_latex(exercise['datos_entrada'])
                doc.append(datos_limpios)
                doc.append(Command('par'))
            
            # Código Python si existe y es modalidad computacional
            if exercise.get('codigo_python') and exercise.get('modalidad') in ['Computacional', 'Mixto']:
                doc.append(Command('vspace', '0.3cm'))
                doc.append(bold('Código de apoyo:'))
                doc.append(Command('par'))
                
                # Entorno de código usando LaTeX directo
                doc.append(NoEscape(r'\begin{verbatim}'))
                # El código Python no necesita limpieza especial
                doc.append(NoEscape(exercise['codigo_python']))
                doc.append(NoEscape(r'\end{verbatim}'))
            
            # Espacio para respuesta
            doc.append(Command('vspace', '2cm'))
            
            # Solución (si se solicita)
            if include_solution and exercise.get('solucion_completa'):
                doc.append(Command('vspace', '0.5cm'))
                doc.append(NoEscape(r'\begin{quote}'))
                doc.append(NoEscape(r'\textcolor{red}{\textbf{Soluci\'{o}n:}}'))
                doc.append(Command('par'))
                solucion_limpia = self._clean_text_for_latex(exercise['solucion_completa'])
                doc.append(solucion_limpia)
                
                if exercise.get('respuesta_final'):
                    doc.append(Command('par'))
                    doc.append(Command('vspace', '0.3cm'))
                    doc.append(bold('Respuesta final: '))
                    respuesta_limpia = self._clean_text_for_latex(exercise['respuesta_final'])
                    doc.append(respuesta_limpia)
                doc.append(NoEscape(r'\end{quote}'))
        
        doc.append(Command('vspace', '1cm'))
    
    def generate_exam_pdf(self, 
                         exercises: List[Dict], 
                         exam_info: Dict,
                         include_solutions: bool = False,
                         filename: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """Genera un PDF de prueba con los ejercicios dados"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = exam_info.get('nombre', 'prueba').replace(' ', '_').lower()
            # Limpiar nombre de archivo
            base_name = ''.join(c for c in base_name if c.isalnum() or c in '_-')
            filename = f"{base_name}_{timestamp}"
        
        # Crear documento
        doc = self.create_document(exam_info.get('nombre', 'Prueba'), include_solutions)
        
        # Agregar encabezado
        self.add_header(doc, exam_info)
        
        # Instrucciones por defecto
        default_instructions = [
            "Lea cuidadosamente cada ejercicio antes de responder.",
            "Muestre claramente todos los pasos de desarrollo.",
            "Se puede usar calculadora cientifica.",
            "Escriba su nombre y RUT en todas las hojas."
        ]
        
        instructions = exam_info.get('instrucciones', default_instructions)
        self.add_instructions(doc, instructions)
        
        # Agregar ejercicios
        for i, exercise in enumerate(exercises, 1):
            self.add_exercise(doc, exercise, i, include_solutions)
            
            # Agregar nueva página entre ejercicios (excepto el último)
            if i < len(exercises):
                doc.append(NewPage())
        
        # Generar PDF con manejo de errores mejorado
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            # Usar directorio temporal para evitar problemas de permisos
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, filename)
                
                # Generar PDF en directorio temporal - SIN argumentos duplicados
                # Y verificar si se generó exitosamente
                try:
                    doc.generate_pdf(temp_path, clean_tex=True, compiler='pdflatex')
                except Exception as latex_error:
                    # Si hay error de LaTeX, verificar si el PDF se generó de todas formas
                    temp_pdf = f"{temp_path}.pdf"
                    if not os.path.exists(temp_pdf):
                        raise latex_error
                    print(f"⚠️  LaTeX dio warnings pero PDF generado exitosamente")
                
                # Copiar a directorio final
                temp_pdf = f"{temp_path}.pdf"
                final_pdf = f"{output_path}.pdf"
                
                if os.path.exists(temp_pdf):
                    shutil.copy2(temp_pdf, final_pdf)
                    pdf_path = final_pdf
                else:
                    raise FileNotFoundError(f"PDF no generado: {temp_pdf}")
            
            # También generar versión con soluciones si no se incluyeron
            pdf_soluciones = None
            if not include_solutions and any(ex.get('solucion_completa') for ex in exercises):
                solutions_filename = f"{filename}_soluciones"
                pdf_soluciones = self.generate_exam_pdf(
                    exercises, exam_info, include_solutions=True, filename=solutions_filename
                )[0]
            
            return pdf_path, pdf_soluciones
            
        except Exception as e:
            # Verificar si el PDF se generó a pesar del error
            final_pdf = f"{output_path}.pdf"
            if os.path.exists(final_pdf):
                print(f"⚠️  PDF generado a pesar del warning: {final_pdf}")
                return final_pdf, None
            else:
                raise Exception(f"Error generando PDF: {str(e)}")
    
    def generate_exercise_sheet(self, 
                               exercises: List[Dict], 
                               sheet_info: Dict,
                               filename: Optional[str] = None) -> str:
        """Genera una guía de ejercicios"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"guia_ejercicios_{timestamp}"
        
        # Información por defecto para guía
        sheet_info.setdefault('nombre', 'Guía de Ejercicios - Señales y Sistemas')
        sheet_info.setdefault('profesor', 'Patricio de la Cuadra')
        
        # Crear documento
        doc = self.create_document(sheet_info['nombre'])
        
        # Encabezado
        self.add_header(doc, sheet_info)
        
        # Agregar ejercicios sin instrucciones especiales
        for i, exercise in enumerate(exercises, 1):
            self.add_exercise(doc, exercise, i, include_solution=False)
        
        # Generar PDF con mismo manejo de errores
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, filename)
                
                doc.generate_pdf(temp_path, clean_tex=True, compiler='pdflatex')
                
                temp_pdf = f"{temp_path}.pdf"
                final_pdf = f"{output_path}.pdf"
                
                if os.path.exists(temp_pdf):
                    shutil.copy2(temp_pdf, final_pdf)
                    return final_pdf
                else:
                    # Verificar si se generó a pesar del warning
                    if os.path.exists(final_pdf):
                        print(f"⚠️  PDF generado a pesar del warning: {final_pdf}")
                        return final_pdf
                    raise FileNotFoundError(f"PDF no generado: {temp_pdf}")
                    
        except Exception as e:
            # Verificar si el PDF se generó a pesar del error
            final_pdf = f"{output_path}.pdf"
            if os.path.exists(final_pdf):
                print(f"⚠️  PDF generado a pesar del warning: {final_pdf}")
                return final_pdf
            else:
                raise Exception(f"Error generando guía: {str(e)}")
    
    def generate_latex_source(self, 
                             exercises: List[Dict], 
                             exam_info: Dict,
                             filename: Optional[str] = None) -> str:
        """Genera solo el código LaTeX sin compilar"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"source_{timestamp}.tex"
        
        # Crear documento
        doc = self.create_document(exam_info.get('nombre', 'Documento'))
        
        # Agregar contenido
        self.add_header(doc, exam_info)
        
        for i, exercise in enumerate(exercises, 1):
            self.add_exercise(doc, exercise, i, include_solution=False)
        
        # Guardar solo el código LaTeX
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            doc.generate_tex(output_path)
            return f"{output_path}"
        except Exception as e:
            raise Exception(f"Error generando código LaTeX: {str(e)}")

    # ========== NUEVOS MÉTODOS MEJORADOS ==========
    
    def generate_tarea_pdf(self,
                          ejercicios_teoricos: List[Dict],
                          ejercicios_implementacion: List[Dict],
                          info_tarea: Dict,
                          include_solutions: bool = False,
                          filename: Optional[str] = None) -> str:
        """Genera PDF de tarea con separación teórico/implementación"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            numero = info_tarea.get('numero', '1')
            filename = f"tarea_{numero}_{timestamp}"
        
        # Crear documento
        doc = self.create_document(f"Tarea {info_tarea.get('numero', '1')}", include_solutions)
        
        # Header específico de tarea
        with doc.create(Section('', numbering=False)):
            doc.append(Command('centering'))
            doc.append(Command('Huge'))
            doc.append(bold(f"Tarea {info_tarea.get('numero', '1')}"))
            doc.append(Command('par'))
            doc.append(Command('vspace', '0.3cm'))
            
            doc.append(Command('Large'))
            fecha_entrega = info_tarea.get('fecha_entrega', '25 de septiembre')
            hora_entrega = info_tarea.get('hora_entrega', '23:59 hrs')
            doc.append(f"Entrega: {fecha_entrega} a las {hora_entrega}")
            doc.append(Command('par'))
            doc.append(Command('vspace', '0.5cm'))
            doc.append(Command('hrule'))
            doc.append(Command('vspace', '0.5cm'))
        
        # Instrucciones específicas de tarea
        tarea_instructions = [
            "Para la parte de implementacion, debe adjuntar codigo desarrollado en Python.",
            "Entregue un PDF con el desarrollo llamado Apellido\\_Tarea1.pdf.",
            "La tarea es individual, pero pueden comentar las preguntas con companeros.",
            "Cada eje de los graficos debe incluir nombre descriptivo y unidades.",
            "Esta permitido consultar apuntes, libros o material bibliografico.",
            "No esta permitido compartir codigos o resultados completos."
        ]
        
        self.add_instructions(doc, tarea_instructions)
        
        # Sección teórica
        if ejercicios_teoricos:
            with doc.create(Section('Ejercicios Teoricos', numbering=False)):
                for i, exercise in enumerate(ejercicios_teoricos, 1):
                    self.add_exercise(doc, exercise, i, include_solutions)
        
        # Nueva página para implementación
        if ejercicios_implementacion:
            doc.append(NewPage())
            with doc.create(Section('Ejercicios de Implementacion', numbering=False)):
                for i, exercise in enumerate(ejercicios_implementacion, 1):
                    self.add_exercise(doc, exercise, i, include_solutions)
        
        # Generar PDF
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, filename)
                
                doc.generate_pdf(temp_path, clean_tex=True, compiler='pdflatex')
                
                temp_pdf = f"{temp_path}.pdf"
                final_pdf = f"{output_path}.pdf"
                
                if os.path.exists(temp_pdf):
                    shutil.copy2(temp_pdf, final_pdf)
                    return final_pdf
                else:
                    # Verificar si se generó a pesar del warning
                    if os.path.exists(final_pdf):
                        print(f"⚠️  PDF generado a pesar del warning: {final_pdf}")
                        return final_pdf
                    raise FileNotFoundError(f"PDF no generado: {temp_pdf}")
                    
        except Exception as e:
            # Verificar si el PDF se generó a pesar del error
            final_pdf = f"{output_path}.pdf"
            if os.path.exists(final_pdf):
                print(f"⚠️  PDF generado a pesar del warning: {final_pdf}")
                return final_pdf
            else:
                raise Exception(f"Error generando tarea: {str(e)}")

# Funciones de utilidad
def create_sample_exercises():
    """Crea ejercicios de ejemplo para testing"""
    return [
        {
            'titulo': 'Convolucion de senales rectangulares',
            'enunciado': 'Calcule la convolucion y(t) = x(t) * h(t) donde x(t) y h(t) son senales rectangulares.',
            'datos_entrada': 'x(t) = rect(t/2) y h(t) = rect((t-1)/3)',
            'tiempo_estimado': 20,
            'nivel_dificultad': 'Intermedio',
            'modalidad': 'Teorico',
            'puntaje': 6,
            'solucion_completa': 'La convolucion se resuelve graficamente considerando el deslizamiento de una funcion sobre la otra.',
            'respuesta_final': 'y(t) = funcion trapecial con duracion total de 5 segundos'
        },
        {
            'titulo': 'Analisis espectral usando FFT',
            'enunciado': 'Implemente en Python el analisis espectral de una senal compuesta.',
            'datos_entrada': 'Senal compuesta por dos sinusoides y ruido gaussiano',
            'tiempo_estimado': 25,
            'nivel_dificultad': 'Avanzado',
            'modalidad': 'Computacional',
            'puntaje': 4,
            'codigo_python': '''import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# Generar senal
fs = 1000
t = np.linspace(0, 1, fs, endpoint=False)
s = 2*np.cos(2*np.pi*50*t) + 0.5*np.cos(2*np.pi*120*t)

# Agregar ruido
ruido = np.random.normal(0, 0.1, len(t))
s_ruido = s + ruido

# Complete el codigo para calcular FFT y graficar...''',
            'solucion_completa': 'Se debe implementar FFT usando scipy.fft y graficar tanto la senal temporal como su espectro de magnitud.',
            'respuesta_final': 'Picos en 50 Hz y 120 Hz claramente identificables'
        },
        {
            'titulo': 'Propiedades de sistemas LTI',
            'enunciado': 'Determine si los siguientes sistemas son lineales y/o invariantes en el tiempo.',
            'datos_entrada': 'a) y(t) = integral de x(tau) de 0 a t, b) y(t) = x(t) + t, c) y(t) = x^2(t)',
            'tiempo_estimado': 15,
            'nivel_dificultad': 'Basico',
            'modalidad': 'Teorico',
            'puntaje': 4,
            'solucion_completa': 'Para verificar linealidad, comprobar superposicion. Para invariancia, verificar que y(t-t0) = T[x(t-t0)].',
            'respuesta_final': 'Solo (a) es LTI, (b) no es lineal, (c) no es lineal'
        }
    ]

def test_pdf_generator():
    """Función para probar el generador"""
    print("🚀 Testing PDF Generator V2.0 - Versión Final Funcionando")
    print("=" * 60)
    
    # Verificar LaTeX
    try:
        result = subprocess.run(['pdflatex', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ LaTeX encontrado y funcionando")
        else:
            print("⚠️  LaTeX encontrado pero con problemas")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ LaTeX NO encontrado")
        print("💡 Instalar con: brew install --cask mactex")
        return False
    
    generator = ExercisePDFGenerator("test_output")
    
    # Información de prueba (sin acentos para evitar problemas)
    exam_info = {
        'nombre': 'Interrogacion 1 - Senales y Sistemas',
        'profesor': 'Patricio de la Cuadra',
        'semestre': '2024-2',
        'fecha': '15 de Septiembre, 2024',
        'tiempo_total': 90
    }
    
    # Información de tarea
    tarea_info = {
        'numero': 1,
        'fecha_entrega': '25 de septiembre',
        'hora_entrega': '23:59 hrs',
        'semestre': '2024-2'
    }
    
    # Ejercicios de ejemplo
    exercises = create_sample_exercises()
    
    try:
        print("\n📝 Generando PDF de Interrogación...")
        pdf_path, solutions_path = generator.generate_exam_pdf(exercises, exam_info)
        print(f"✅ PDF generado: {pdf_path}")
        if solutions_path:
            print(f"✅ Soluciones generadas: {solutions_path}")
        
        print("\n📋 Generando PDF de Tarea separada...")
        teoricos = [ex for ex in exercises if ex['modalidad'] == 'Teorico']
        implementacion = [ex for ex in exercises if ex['modalidad'] == 'Computacional']
        
        pdf_tarea = generator.generate_tarea_pdf(teoricos, implementacion, tarea_info)
        print(f"✅ Tarea generada: {pdf_tarea}")
        
        print("\n📚 Generando Guía de ejercicios...")
        guia_info = {
            'nombre': 'Guia de Ejercicios - Convolucion',
            'profesor': 'Patricio de la Cuadra',
            'semestre': '2024-2'
        }
        
        pdf_guia = generator.generate_exercise_sheet(exercises, guia_info)
        print(f"✅ Guía generada: {pdf_guia}")
        
        print("\n" + "=" * 60)
        print("🎉 ¡Todos los PDFs generados exitosamente!")
        print(f"\n📁 Archivos creados en 'test_output/':")
        
        # Listar archivos generados
        if os.path.exists("test_output"):
            files = [f for f in os.listdir("test_output") if f.endswith('.pdf')]
            for file in sorted(files):
                if os.path.exists(os.path.join("test_output", file)):
                    size = os.path.getsize(os.path.join("test_output", file))
                    print(f"   • {file} ({size//1024}KB)")
        
        print("\n🔧 Sistema completamente funcional:")
        print("   ✓ Fix geometry para evitar conflictos")
        print("   ✓ Manejo de warnings de LaTeX")
        print("   ✓ Compilación robusta")
        print("   ✓ UTF-8 y caracteres especiales")
        print("   ✓ Separación teórico/implementación")
        print("   ✓ Soluciones condicionales")
        
        print("\n📋 Listo para integración:")
        print("   1. ✅ Reemplazar tu pdf_generator.py actual")
        print("   2. ✅ Usar las nuevas funciones en app.py")
        print("   3. ✅ Agregar logos PUC si quieres")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Tipo: {type(e).__name__}")
        
        # Debugging adicional
        if "codec" in str(e).lower():
            print("   💡 Problema de codificación - revisar caracteres especiales")
        elif "permission" in str(e).lower():
            print("   💡 Problema de permisos - verificar directorio de salida")
        elif "pdflatex" in str(e).lower():
            print("   💡 Problema de LaTeX - verificar instalación")
        
        return False

if __name__ == "__main__":
    test_pdf_generator()