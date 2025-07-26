"""
PDF Generator V3.0 - Versión simplificada con compilación
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import subprocess
import tempfile

class RealTemplatePDFGenerator:
    """Generador que usa los templates LaTeX reales y compila a PDF"""
    
    def __init__(self, output_dir: str = "output", templates_dir: str = "templates"):
        self.output_dir = Path(output_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.required_templates = {
            'guia': 'guia_template.tex',
            'prueba': 'prueba_template.tex', 
            'tarea': 'tarea_template.tex'
        }
        self._verify_templates()
    
    def _verify_templates(self):
        """Verifica que existan los templates necesarios"""
        missing = []
        for template_type, template_file in self.required_templates.items():
            template_path = self.templates_dir / template_file
            if not template_path.exists():
                missing.append(template_file)
        
        if missing:
            print(f"⚠️  Templates faltantes: {missing}")
        else:
            print(f"✅ Templates encontrados: {list(self.required_templates.values())}")
    
    def _clean_text(self, text):
        """Limpia texto básico para LaTeX"""
        if not text:
            return ""
        text = str(text)
        # Solo escape básico
        text = text.replace('&', ' y ')
        text = text.replace('%', ' porciento ')
        text = text.replace('#', ' numero ')
        return text
    
    def _generate_ejercicios_prueba(self, exercises):
        """Genera ejercicios para prueba"""
        latex_content = ""
        
        for i, exercise in enumerate(exercises, 1):
            titulo = self._clean_text(exercise.get('titulo', f'Ejercicio {i}'))
            enunciado = self._clean_text(exercise.get('enunciado', ''))
            
            latex_content += f"""\\begin{{ejercicio}}[{titulo}]{{6}}
 {enunciado}
 
 \\respuesta[6cm]
\\end{{ejercicio}}

"""
            # Agregar newpage excepto en el último
            if i < len(exercises):
                latex_content += "\\newpage\n\n"
        
        return latex_content
    
    def _generate_ejercicios_tarea(self, exercises):
        """Genera ejercicios para tarea separando teóricos y computacionales"""
        teoricos = [e for e in exercises if e.get('modalidad') != 'Computacional']
        computacionales = [e for e in exercises if e.get('modalidad') == 'Computacional']
        
        latex_content = ""
        
        # Ejercicios teóricos
        if teoricos:
            latex_content += "\\begin{ejerciciosteoricos}\n\n"
            for i, exercise in enumerate(teoricos, 1):
                titulo = self._clean_text(exercise.get('titulo', f'Ejercicio Teórico {i}'))
                enunciado = self._clean_text(exercise.get('enunciado', ''))
                
                latex_content += f"""\\begin{{ejercicio}}[{titulo}]{{2}}
 {enunciado}
\\end{{ejercicio}}

"""
            latex_content += "\\end{ejerciciosteoricos}\n\n"
        
        # Ejercicios computacionales
        if computacionales:
            latex_content += "\\begin{ejerciciosimplementacion}\n\n"
            for i, exercise in enumerate(computacionales, 1):
                titulo = self._clean_text(exercise.get('titulo', f'Ejercicio Computacional {i}'))
                enunciado = self._clean_text(exercise.get('enunciado', ''))
                codigo = exercise.get('codigo_python', '')
                
                latex_content += f"""\\begin{{ejercicio}}[{titulo}]{{2}}
 {enunciado}
 
"""
                if codigo:
                    latex_content += f""" \\begin{{codigo}}
{codigo}
 \\end{{codigo}}
 
"""
                
                latex_content += "\\end{ejercicio}\n\n"
            
            latex_content += "\\end{ejerciciosimplementacion}\n\n"
        
        return latex_content
    
    def _generate_ejercicios_guia(self, exercises):
        """Genera ejercicios para guía agrupados por unidad"""
        # Agrupar por unidad temática
        unidades = {}
        for exercise in exercises:
            unidad = exercise.get('unidad_tematica', 'Ejercicios Generales')
            if unidad not in unidades:
                unidades[unidad] = []
            unidades[unidad].append(exercise)
        
        latex_content = ""
        
        for unidad, ejercicios_unidad in unidades.items():
            latex_content += f"\\section{{{unidad}}}\n\n"
            
            for i, exercise in enumerate(ejercicios_unidad, 1):
                titulo = self._clean_text(exercise.get('titulo', f'Ejercicio {i}'))
                enunciado = self._clean_text(exercise.get('enunciado', ''))
                dificultad = exercise.get('nivel_dificultad', 'Básico')
                tiempo = exercise.get('tiempo_estimado', 15)
                
                latex_content += f"""\\begin{{ejercicio}}[{titulo}]{{6}}
 \\textbf{{Dificultad:}} {dificultad} \\hfill \\textbf{{Tiempo:}} {tiempo} min
 
 {enunciado}
 
 \\respuesta[8cm]
\\end{{ejercicio}}

"""
        
        return latex_content
    
    def _compile_to_pdf(self, tex_path: Path) -> str:
        """Compila el archivo .tex a PDF"""
        try:
            # Cambiar al directorio de salida ANTES de compilar
            original_dir = os.getcwd()
            os.chdir(self.output_dir)
            
            # Usar solo el nombre del archivo, no la ruta completa
            tex_filename = tex_path.name
            
            # Ejecutar pdflatex con el nombre del archivo local
            cmd = ['pdflatex', '-interaction=nonstopmode', tex_filename]
            
            # Compilar dos veces para referencias
            for _ in range(2):
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            os.chdir(original_dir)
            
            # Verificar que se creó el PDF
            pdf_path = tex_path.with_suffix('.pdf')
            if pdf_path.exists():
                print(f"✅ PDF generado: {pdf_path}")
                return str(pdf_path)
            else:
                print(f"⚠️  No se pudo generar PDF, manteniendo .tex")
                print(f"Return code: {result.returncode}")
                if result.stdout:
                    print(f"Últimas líneas: {result.stdout[-300:]}")
                return str(tex_path)
                
        except FileNotFoundError:
            print("⚠️  pdflatex no encontrado, manteniendo archivo .tex")
            return str(tex_path)
        except Exception as e:
            print(f"⚠️  Error compilando: {e}, manteniendo archivo .tex")
            return str(tex_path)
    
    def generate_prueba(self, exercises: List[Dict], exam_info: Dict) -> Tuple[str, str]:
        """Genera prueba con ejercicios de la BD"""
        template_path = self.templates_dir / 'prueba_template.tex'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_tex = self.output_dir / f"prueba_{timestamp}.tex"
        
        # Leer template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generar ejercicios dinámicos
        exercises_latex = self._generate_ejercicios_prueba(exercises)
        
        # Buscar y reemplazar la sección de ejercicios
        start_marker = "\\begin{ejercicio}[Manipulación de señales complejas]"
        end_marker = "% ========== PIE DE PÁGINA FINAL =========="
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # Reemplazar ejercicios del template con los de la BD
            new_content = (content[:start_pos] + 
                          exercises_latex + "\n" +
                          content[end_pos:])
        else:
            new_content = content  # Si no encuentra marcadores, usar template original
        
        # Guardar archivo modificado
        with open(output_tex, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Archivo .tex creado con {len(exercises)} ejercicios: {output_tex}")
        
        pdf_path = self._compile_to_pdf(output_tex)
        
        return pdf_path, pdf_path
    
    def generate_tarea(self, exercises: List[Dict], task_info: Dict) -> str:
        """Genera tarea con ejercicios de la BD"""
        template_path = self.templates_dir / 'tarea_template.tex'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_tex = self.output_dir / f"tarea_{timestamp}.tex"
        
        # Leer template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generar ejercicios dinámicos
        exercises_latex = self._generate_ejercicios_tarea(exercises)
        
        # MARCADORES CORRECTOS BASADOS EN TU TEMPLATE
        start_marker = "\\begin{ejerciciosteoricos}"
        end_marker = "% ========== PIE DE PÁGINA =========="
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # Reemplazar con ejercicios de BD
            new_content = (content[:start_pos] + 
                          exercises_latex + "\n" +
                          content[end_pos:])
            print("✅ Marcadores encontrados, reemplazando ejercicios")
        else:
            # Si no encuentra marcadores, agregar al final
            new_content = content.replace('\\end{document}', 
                                        f'\n\n{exercises_latex}\n\n\\end{{document}}')
            print("⚠️ Marcadores no encontrados, agregando al final")
        
        # Guardar archivo
        with open(output_tex, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Archivo .tex creado con {len(exercises)} ejercicios: {output_tex}")
        
        pdf_path = self._compile_to_pdf(output_tex)
        
        return pdf_path
    
    def generate_guia(self, exercises: List[Dict], guide_info: Dict) -> str:
        """Genera guía con ejercicios de la BD"""
        template_path = self.templates_dir / 'guia_template.tex'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_tex = self.output_dir / f"guia_{timestamp}.tex"
        
        # Leer template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generar ejercicios dinámicos
        exercises_latex = self._generate_ejercicios_guia(exercises)
        
        # Buscar y reemplazar sección de ejercicios
        start_marker = "\\section{Ejercicios}"
        end_marker = "% ========== RECURSOS ADICIONALES"
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # Reemplazar con ejercicios de BD
            new_content = (content[:start_pos] + 
                          exercises_latex + "\n" +
                          content[end_pos:])
        else:
            # Si no encuentra marcadores, agregar al final
            new_content = content.replace('\\end{document}', 
                                        f'\n\n{exercises_latex}\n\n\\end{{document}}')
        
        # Guardar archivo
        with open(output_tex, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Archivo .tex creado con {len(exercises)} ejercicios: {output_tex}")
        
        pdf_path = self._compile_to_pdf(output_tex)
        
        return pdf_path

class ExercisePDFGenerator(RealTemplatePDFGenerator):
    """Wrapper para compatibilidad"""
    pass