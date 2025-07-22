"""
Generador de PDFs usando LaTeX para ejercicios y pruebas
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

from pylatex import Document, Section, Subsection, Command, Package, NewPage
from pylatex.math import Math, Align
from pylatex.base_classes import Environment
from pylatex.utils import italic, bold, NoEscape
import os
from datetime import datetime
from typing import List, Dict, Optional
import tempfile
import subprocess

class PUCLatexTemplate:
    """Template LaTeX personalizado para la PUC"""
    
    def __init__(self):
        self.geometry_options = {
            'tmargin': '2.5cm',
            'lmargin': '2.5cm',
            'rmargin': '2.5cm',
            'bmargin': '2.5cm'
        }
        
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
            Package('hyperref'),
            Package('geometry', options=self.geometry_options)
        ]

class ExercisePDFGenerator:
    """Generador de PDFs para ejercicios y pruebas"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.template = PUCLatexTemplate()
        
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        
    def create_document(self, title: str, include_solutions: bool = False) -> Document:
        """Crea un documento LaTeX base"""
        doc = Document(geometry_options=self.template.geometry_options)
        
        # Agregar paquetes
        for package in self.template.packages:
            doc.packages.append(package)
        
        # Configurar encabezado y pie de página
        doc.append(Command('pagestyle', 'fancy'))
        doc.append(Command('fancyhf', ''))
        doc.append(Command('fancyhead', ['L'], 'Pontificia Universidad Católica de Chile'))
        doc.append(Command('fancyhead', ['R'], 'IEE2103 - Señales y Sistemas'))
        doc.append(Command('fancyfoot', ['C'], Command('thepage')))
        
        # Configurar colores PUC
        doc.append(Command('definecolor', ['pucblue'], ['RGB'], ['31, 78, 121']))
        
        return doc
    
    def add_header(self, doc: Document, exam_info: Dict):
        """Agrega el encabezado de la prueba"""
        with doc.create(Section('', numbering=False)):
            doc.append(Command('centering'))
            doc.append(Command('Large'))
            doc.append(bold(exam_info.get('nombre', 'Ejercicios de Señales y Sistemas')))
            doc.append(Command('par'))
            doc.append(Command('vspace', '0.5cm'))
            
            # Información del curso
            doc.append(Command('normalsize'))
            doc.append(f"Profesor: {exam_info.get('profesor', 'Patricio de la Cuadra')}")
            doc.append(Command('hfill'))
            doc.append(f"Semestre: {exam_info.get('semestre', '2024-2')}")
            doc.append(Command('par'))
            
            if 'fecha' in exam_info:
                doc.append(f"Fecha: {exam_info['fecha']}")
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
            with doc.create(Environment(name='enumerate')):
                for instruction in instructions:
                    doc.append(Command('item'))
                    doc.append(instruction)
        
        doc.append(Command('vspace', '0.5cm'))
    
    def add_exercise(self, doc: Document, exercise: Dict, exercise_num: int, include_solution: bool = False):
        """Agrega un ejercicio al documento"""
        # Título del ejercicio
        exercise_title = f"Ejercicio {exercise_num}"
        if exercise.get('titulo'):
            exercise_title += f": {exercise['titulo']}"
        
        with doc.create(Subsection(exercise_title, numbering=False)):
            # Información del ejercicio
            info_parts = []
            if exercise.get('tiempo_estimado'):
                info_parts.append(f"Tiempo estimado: {exercise['tiempo_estimado']} minutos")
            if exercise.get('nivel_dificultad'):
                info_parts.append(f"Dificultad: {exercise['nivel_dificultad']}")
            
            if info_parts:
                doc.append(italic(" | ".join(info_parts)))
                doc.append(Command('par'))
                doc.append(Command('vspace', '0.3cm'))
            
            # Enunciado
            if exercise.get('enunciado'):
                doc.append(exercise['enunciado'])
                doc.append(Command('par'))
            
            # Datos de entrada si existen
            if exercise.get('datos_entrada'):
                doc.append(Command('vspace', '0.3cm'))
                doc.append(bold('Datos:'))
                doc.append(Command('par'))
                doc.append(exercise['datos_entrada'])
                doc.append(Command('par'))
            
            # Código Python si existe y es modalidad computacional
            if exercise.get('codigo_python') and exercise.get('modalidad') in ['Computacional', 'Mixto']:
                doc.append(Command('vspace', '0.3cm'))
                doc.append(bold('Código de apoyo:'))
                doc.append(Command('par'))
                
                # Entorno de código
                with doc.create(Environment(name='verbatim')):
                    doc.append(NoEscape(exercise['codigo_python']))
            
            # Espacio para respuesta
            doc.append(Command('vspace', '2cm'))
            
            # Solución (si se solicita)
            if include_solution and exercise.get('solucion_completa'):
                doc.append(Command('vspace', '0.5cm'))
                with doc.create(Environment(name='quote')):
                    doc.append(Command('textcolor', ['red'], [bold('Solución:')]))
                    doc.append(Command('par'))
                    doc.append(exercise['solucion_completa'])
                    
                    if exercise.get('respuesta_final'):
                        doc.append(Command('par'))
                        doc.append(Command('vspace', '0.3cm'))
                        doc.append(bold('Respuesta final: '))
                        doc.append(exercise['respuesta_final'])
        
        doc.append(Command('vspace', '1cm'))
    
    def generate_exam_pdf(self, 
                         exercises: List[Dict], 
                         exam_info: Dict,
                         include_solutions: bool = False,
                         filename: Optional[str] = None) -> str:
        """Genera un PDF de prueba con los ejercicios dados"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = exam_info.get('nombre', 'prueba').replace(' ', '_').lower()
            filename = f"{base_name}_{timestamp}"
        
        # Crear documento
        doc = self.create_document(exam_info.get('nombre', 'Prueba'), include_solutions)
        
        # Agregar encabezado
        self.add_header(doc, exam_info)
        
        # Instrucciones por defecto
        default_instructions = [
            "Lea cuidadosamente cada ejercicio antes de responder.",
            "Muestre claramente todos los pasos de desarrollo.",
            "Se puede usar calculadora científica.",
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
        
        # Generar PDF
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            doc.generate_pdf(output_path, clean_tex=False, compiler='pdflatex')
            pdf_path = f"{output_path}.pdf"
            
            # También generar versión con soluciones si no se incluyeron
            if not include_solutions:
                solutions_filename = f"{filename}_soluciones"
                solutions_path = self.generate_exam_pdf(
                    exercises, exam_info, include_solutions=True, filename=solutions_filename
                )
                return pdf_path, solutions_path
            
            return pdf_path
            
        except Exception as e:
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
        
        # Generar PDF
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            doc.generate_pdf(output_path, clean_tex=False, compiler='pdflatex')
            return f"{output_path}.pdf"
        except Exception as e:
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

# Funciones de utilidad
def create_sample_exercises():
    """Crea ejercicios de ejemplo para testing"""
    return [
        {
            'titulo': 'Convolución de señales rectangulares',
            'enunciado': 'Calcule la convolución y(t) = x(t) * h(t) donde x(t) y h(t) son señales rectangulares.',
            'datos_entrada': 'x(t) = rect(t/2) y h(t) = rect((t-1)/3)',
            'tiempo_estimado': 20,
            'nivel_dificultad': 'Intermedio',
            'modalidad': 'Teórico',
            'solucion_completa': 'La convolución se resuelve gráficamente considerando...',
            'respuesta_final': 'y(t) = función trapecial con duración total de 5 segundos'
        },
        {
            'titulo': 'Análisis espectral usando FFT',
            'enunciado': 'Implemente en Python el análisis espectral de una señal compuesta.',
            'datos_entrada': 'Señal: s(t) = 2*cos(2π*50*t) + 0.5*cos(2π*120*t) + ruido gaussiano',
            'tiempo_estimado': 25,
            'nivel_dificultad': 'Avanzado',
            'modalidad': 'Computacional',
            'codigo_python': '''import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# Generar señal
fs = 1000  # Frecuencia de muestreo
t = np.linspace(0, 1, fs, endpoint=False)
# Complete el código...''',
            'solucion_completa': 'Se debe implementar FFT y graficar espectro...',
            'respuesta_final': 'Picos en 50 Hz y 120 Hz claramente identificables'
        }
    ]

def test_pdf_generator():
    """Función para probar el generador"""
    generator = ExercisePDFGenerator("test_output")
    
    # Información de prueba
    exam_info = {
        'nombre': 'Interrogación 1 - Señales y Sistemas',
        'profesor': 'Patricio de la Cuadra',
        'semestre': '2024-2',
        'fecha': '15 de Septiembre, 2024',
        'tiempo_total': 90
    }
    
    # Ejercicios de ejemplo
    exercises = create_sample_exercises()
    
    try:
        # Generar PDF
        pdf_path = generator.generate_exam_pdf(exercises, exam_info)
        print(f"PDF generado exitosamente: {pdf_path}")
        
        # Generar código LaTeX
        latex_path = generator.generate_latex_source(exercises, exam_info)
        print(f"Código LaTeX generado: {latex_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pdf_generator()