"""
PDF Generator V3.0 - Usando Templates LaTeX Reales Existentes
Compatible con templates: guia_template.tex, prueba_template.tex, tarea_template.tex
Sistema DB_Ejercicios - IEE2103 Señales y Sistemas PUC
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import subprocess
import tempfile

class RealTemplatePDFGenerator:
    """Generador que usa los templates LaTeX reales existentes"""
    
    def __init__(self, output_dir: str = "output", templates_dir: str = "templates"):
        self.output_dir = Path(output_dir)
        self.templates_dir = Path(templates_dir)
        
        # Crear directorios si no existen
        self.output_dir.mkdir(exist_ok=True)
        
        # Verificar que existan los templates
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
            print(f"📁 Verificar en: {self.templates_dir}")
        else:
            print(f"✅ Templates encontrados: {list(self.required_templates.values())}")
    
    def generate_guia(self, exercises: List[Dict], guide_info: Dict) -> str:
        """Genera guía usando guia_template.tex"""
        
        template_path = self.templates_dir / 'guia_template.tex'
        if not template_path.exists():
            raise FileNotFoundError(f"Template no encontrado: {template_path}")
        
        # Leer template base
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Preparar configuración
        config_data = {
            'titulo': guide_info.get('nombre', 'Guía de Ejercicios - Señales y Sistemas'),
            'unidad': guide_info.get('unidad', 'Múltiples Unidades'),
            'fecha': guide_info.get('fecha', datetime.now().strftime('%B %Y')),
            'profesor': guide_info.get('profesor', 'Patricio de la Cuadra'),
            'semestre': guide_info.get('semestre', '2024-2'),
            'descripcion': guide_info.get('descripcion', 'Ejercicios de práctica para reforzar conceptos del curso.')
        }
        
        # Reemplazar configuración en template
        modified_content = self._replace_guia_config(template_content, config_data)
        
        # Generar ejercicios en formato del template
        ejercicios_tex = self._generate_guia_exercises(exercises)
        
        # Reemplazar la sección de ejercicios
        modified_content = self._replace_exercises_section(modified_content, ejercicios_tex, 'guia')
        
        # Compilar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"guia_{timestamp}"
        
        return self._compile_latex(modified_content, filename)
    
    def generate_prueba(self, exercises: List[Dict], exam_info: Dict) -> Tuple[str, str]:
        """Genera prueba usando prueba_template.tex"""
        
        template_path = self.templates_dir / 'prueba_template.tex'
        if not template_path.exists():
            raise FileNotFoundError(f"Template no encontrado: {template_path}")
        
        # Leer template base
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Preparar configuración
        config_data = {
            'nombre': exam_info.get('nombre', 'Interrogación 1'),
            'fecha': exam_info.get('fecha', datetime.now().strftime('%d de %B, %Y')),
            'tiempo': f"{exam_info.get('tiempo_total', 90)} minutos",
            'profesor': exam_info.get('profesor', 'Patricio de la Cuadra'),
            'semestre': exam_info.get('semestre', '2024-2'),
            'puntaje_total': self._calculate_total_points(exercises)
        }
        
        # Reemplazar configuración
        modified_content = self._replace_prueba_config(template_content, config_data)
        
        # Generar ejercicios
        ejercicios_tex = self._generate_prueba_exercises(exercises)
        
        # Reemplazar ejercicios
        modified_content = self._replace_exercises_section(modified_content, ejercicios_tex, 'prueba')
        
        # Compilar versión sin soluciones
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_main = f"prueba_{timestamp}"
        pdf_main = self._compile_latex(modified_content, filename_main)
        
        # Compilar versión con soluciones
        modified_content_sol = modified_content.replace('% \\solucionestrue', '\\solucionestrue')
        filename_sol = f"prueba_{timestamp}_soluciones"
        pdf_sol = self._compile_latex(modified_content_sol, filename_sol)
        
        return pdf_main, pdf_sol
    
    def generate_tarea(self, exercises: List[Dict], task_info: Dict) -> str:
        """Genera tarea usando tarea_template.tex"""
        
        template_path = self.templates_dir / 'tarea_template.tex'
        if not template_path.exists():
            raise FileNotFoundError(f"Template no encontrado: {template_path}")
        
        # Leer template base
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Preparar configuración
        config_data = {
            'numero': task_info.get('numero', '1'),
            'fecha_entrega': task_info.get('fecha_entrega', datetime.now().strftime('%d de %B')),
            'hora_entrega': task_info.get('hora_entrega', '23:59 hrs'),
            'semestre': task_info.get('semestre', '2024-2'),
            'profesor': task_info.get('profesor', 'Patricio de la Cuadra'),
            'puntaje_total': self._calculate_total_points(exercises)
        }
        
        # Reemplazar configuración
        modified_content = self._replace_tarea_config(template_content, config_data)
        
        # Clasificar ejercicios por tipo
        ejercicios_teoricos, ejercicios_implementacion = self._classify_exercises(exercises)
        
        # Generar ejercicios
        teoricos_tex = self._generate_tarea_exercises(ejercicios_teoricos, 'teorico')
        implementacion_tex = self._generate_tarea_exercises(ejercicios_implementacion, 'implementacion')
        
        # Reemplazar secciones
        modified_content = self._replace_tarea_sections(
            modified_content, teoricos_tex, implementacion_tex
        )
        
        # Compilar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tarea_{timestamp}"
        
        return self._compile_latex(modified_content, filename)
    
    def _replace_guia_config(self, content: str, config: Dict) -> str:
        """Reemplaza configuración en template de guía"""
        # Buscar el bloque \configurarguia y reemplazarlo
        config_pattern = r'\\configurarguia\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}'
        
        new_config = f"""\\configurarguia{{
  {config['titulo']}
}}{{
  {config['unidad']}
}}{{
  {config['fecha']}
}}{{
  {config['profesor']}
}}{{
  {config['semestre']}
}}{{
  {config['descripcion']}
}}"""
        
        return re.sub(config_pattern, new_config, content, flags=re.DOTALL)
    
    def _replace_prueba_config(self, content: str, config: Dict) -> str:
        """Reemplaza configuración en template de prueba"""
        config_pattern = r'\\configurarprueba\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}'
        
        new_config = f"""\\configurarprueba{{
  {config['nombre']}
}}{{
  {config['fecha']}
}}{{
  {config['tiempo']}
}}{{
  {config['profesor']}
}}{{
  {config['semestre']}
}}{{
  {config['puntaje_total']}
}}{{
  % Instrucciones (definidas en el template)
}}"""
        
        return re.sub(config_pattern, new_config, content, flags=re.DOTALL)
    
    def _replace_tarea_config(self, content: str, config: Dict) -> str:
        """Reemplaza configuración en template de tarea"""
        config_pattern = r'\\configurartarea\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}'
        
        new_config = f"""\\configurartarea{{
  {config['numero']}
}}{{
  {config['fecha_entrega']}
}}{{
  {config['hora_entrega']}
}}{{
  {config['semestre']}
}}{{
  {config['profesor']}
}}{{
  {config['puntaje_total']}
}}"""
        
        return re.sub(config_pattern, new_config, content, flags=re.DOTALL)
    
    def _generate_guia_exercises(self, exercises: List[Dict]) -> str:
        """Genera ejercicios en formato de guía usando estructura del template"""
        ejercicios_tex = []
        
        # Agrupar por unidad temática
        ejercicios_por_unidad = {}
        for exercise in exercises:
            unidad = exercise.get('unidad_tematica', 'Ejercicios Generales')
            if unidad not in ejercicios_por_unidad:
                ejercicios_por_unidad[unidad] = []
            ejercicios_por_unidad[unidad].append(exercise)
        
        for unidad, ejercicios_unidad in ejercicios_por_unidad.items():
            # Crear grupo de ejercicios usando el formato del template
            ejercicios_tex.append(f"""
\\begin{{grupoejercicio}}{{{unidad}}}{{Ejercicios para practicar {unidad}}}
""")
            
            for exercise in ejercicios_unidad:
                dificultad_cmd = self._get_difficulty_command(exercise.get('nivel_dificultad', 'Intermedio'))
                tiempo = exercise.get('tiempo_estimado', 20)
                titulo = self._escape_latex(exercise.get('titulo', 'Ejercicio'))
                enunciado = self._escape_latex(exercise.get('enunciado', ''))
                
                ejercicio_tex = f"""
\\begin{{ejercicio}}[{titulo}]{{{tiempo}}}{{\\{dificultad_cmd}}}
  {enunciado}
  
  \\espaciotrabajo[6cm]
  
  \\begin{{solucion}}
    {self._escape_latex(exercise.get('solucion_completa', 'Solución por desarrollar.'))}
  \\end{{solucion}}
\\end{{ejercicio}}
"""
                ejercicios_tex.append(ejercicio_tex)
            
            ejercicios_tex.append("\\end{grupoejercicio}\n")
        
        return '\n'.join(ejercicios_tex)
    
    def _generate_prueba_exercises(self, exercises: List[Dict]) -> str:
        """Genera ejercicios en formato de prueba"""
        ejercicios_tex = []
        
        for exercise in exercises:
            titulo = self._escape_latex(exercise.get('titulo', ''))
            puntos = exercise.get('puntos', 6)  # Default 6 puntos
            enunciado = self._escape_latex(exercise.get('enunciado', ''))
            
            # Agregar datos si existen
            if exercise.get('datos_entrada'):
                enunciado += f"\n\n\\textbf{{Datos:}} {self._escape_latex(exercise['datos_entrada'])}"
            
            ejercicio_tex = f"""
\\begin{{ejercicio}}[{titulo}]{{{puntos}}}
  {enunciado}
  
  \\respuesta[8cm]
  
  \\begin{{solucion}}
    {self._escape_latex(exercise.get('solucion_completa', 'Solución por desarrollar.'))}
  \\end{{solucion}}
\\end{{ejercicio}}
"""
            ejercicios_tex.append(ejercicio_tex)
        
        return '\n'.join(ejercicios_tex)
    
    def _generate_tarea_exercises(self, exercises: List[Dict], tipo: str) -> str:
        """Genera ejercicios en formato de tarea"""
        ejercicios_tex = []
        
        for exercise in exercises:
            titulo = self._escape_latex(exercise.get('titulo', 'Ejercicio'))
            puntos = exercise.get('puntos', 2)
            enunciado = self._escape_latex(exercise.get('enunciado', ''))
            
            # Agregar código Python si es de implementación
            if tipo == 'implementacion' and exercise.get('codigo_python'):
                codigo = exercise['codigo_python']
                enunciado += f"""
  
  \\begin{{codigo}}
{codigo}
  \\end{{codigo}}
"""
            
            ejercicio_tex = f"""
\\begin{{ejercicio}}[{titulo}]{{{puntos}}}
  {enunciado}
  
  \\begin{{solucion}}
    {self._escape_latex(exercise.get('solucion_completa', 'Solución por desarrollar.'))}
  \\end{{solucion}}
\\end{{ejercicio}}
"""
            ejercicios_tex.append(ejercicio_tex)
        
        return '\n'.join(ejercicios_tex)
    
    def _replace_exercises_section(self, content: str, ejercicios_tex: str, template_type: str) -> str:
        """Reemplaza la sección de ejercicios en el template"""
        if template_type == 'guia':
            # Buscar después de los objetivos y reemplazar hasta el final
            pattern = r'(% ========== GRUPO 1:.*?)(?=% ========== RECURSOS ADICIONALES|% ========== PIE DE PÁGINA|\\vfill|\\end\{document\})'
            replacement = f"% ========== EJERCICIOS GENERADOS ==========\n{ejercicios_tex}\n\n"
            
        elif template_type == 'prueba':
            # Buscar después de instrucciones y reemplazar hasta pie de página
            pattern = r'(% ========== EJERCICIOS ==========.*?)(?=\\newpage|% ========== PIE DE PÁGINA|\\vfill|\\end\{document\})'
            replacement = f"% ========== EJERCICIOS GENERADOS ==========\n{ejercicios_tex}\n\n"
        
        return re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    def _replace_tarea_sections(self, content: str, teoricos_tex: str, implementacion_tex: str) -> str:
        """Reemplaza secciones de tarea"""
        # Reemplazar ejercicios teóricos
        if teoricos_tex.strip():
            teoricos_pattern = r'(\\begin\{ejerciciosteoricos\}.*?)\\end\{ejerciciosteoricos\}'
            teoricos_replacement = f"""\\begin{{ejerciciosteoricos}}

{teoricos_tex}

\\end{{ejerciciosteoricos}}"""
            content = re.sub(teoricos_pattern, teoricos_replacement, content, flags=re.DOTALL)
        
        # Reemplazar ejercicios de implementación
        if implementacion_tex.strip():
            impl_pattern = r'(\\begin\{ejerciciosimplementacion\}.*?)\\end\{ejerciciosimplementacion\}'
            impl_replacement = f"""\\begin{{ejerciciosimplementacion}}

{implementacion_tex}

\\end{{ejerciciosimplementacion}}"""
            content = re.sub(impl_pattern, impl_replacement, content, flags=re.DOTALL)
        
        return content
    
    def _classify_exercises(self, exercises: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Clasifica ejercicios en teóricos e implementación"""
        teoricos = []
        implementacion = []
        
        for exercise in exercises:
            modalidad = exercise.get('modalidad', 'Teórico')
            if modalidad in ['Computacional', 'Mixto'] or exercise.get('codigo_python'):
                implementacion.append(exercise)
            else:
                teoricos.append(exercise)
        
        return teoricos, implementacion
    
    def _get_difficulty_command(self, dificultad: str) -> str:
        """Retorna comando LaTeX para dificultad"""
        mapping = {
            'Básico': 'basico',
            'Intermedio': 'intermedio',
            'Avanzado': 'avanzado',
            'Desafío': 'desafio'
        }
        return mapping.get(dificultad, 'intermedio')
    
    def _calculate_total_points(self, exercises: List[Dict]) -> int:
        """Calcula puntos totales"""
        total = 0
        for exercise in exercises:
            puntos = exercise.get('puntos')
            if puntos is None:
                # Asignar puntos por defecto según modalidad
                if exercise.get('modalidad') == 'Computacional':
                    puntos = 4
                else:
                    puntos = 6
            
            if isinstance(puntos, (int, float)):
                total += puntos
        
        return int(total) if total > 0 else len(exercises) * 6
    
    def _escape_latex(self, text: str) -> str:
        """Escapa caracteres especiales de LaTeX (versión conservadora)"""
        if not text:
            return ""
        
        # Solo escapar caracteres que sabemos que causan problemas
        # Ser conservador para no romper LaTeX math existente
        replacements = {
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '_': '\\_',
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}'
        }
        
        for char, escaped in replacements.items():
            # Solo reemplazar si no está ya escapado
            text = re.sub(f'(?<!\\\\){re.escape(char)}', escaped, text)
        
        return text
    
    def _compile_latex(self, content: str, filename: str) -> str:
        """Compila LaTeX a PDF"""
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.tex',
            delete=False,
            encoding='utf-8',
            dir=self.output_dir
        ) as tmp_file:
            tmp_file.write(content)
            tmp_tex_path = tmp_file.name
        
        try:
            # Compilar LaTeX
            cmd = [
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory', str(self.output_dir),
                tmp_tex_path
            ]
            
            # Ejecutar dos veces para referencias cruzadas
            for run in range(2):
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    # En el primer run, algunos errores son normales
                    if run == 1:  # Solo fallar en el segundo run
                        error_msg = f"Error compilando LaTeX:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
                        raise Exception(error_msg)
            
            # Mover PDF al nombre final
            tmp_pdf = tmp_tex_path.replace('.tex', '.pdf')
            final_pdf = self.output_dir / f"{filename}.pdf"
            
            if os.path.exists(tmp_pdf):
                shutil.move(tmp_pdf, final_pdf)
            else:
                raise Exception("PDF no fue generado correctamente")
            
            # Limpiar archivos temporales
            self._cleanup_temp_files(tmp_tex_path)
            
            return str(final_pdf)
            
        except subprocess.TimeoutExpired:
            self._cleanup_temp_files(tmp_tex_path)
            raise Exception("Timeout compilando LaTeX - proceso tomó más de 30 segundos")
        except Exception as e:
            # Limpiar en caso de error
            self._cleanup_temp_files(tmp_tex_path)
            raise e
    
    def _cleanup_temp_files(self, tex_path: str):
        """Limpia archivos temporales de LaTeX"""
        base_name = tex_path.replace('.tex', '')
        extensions = ['.tex', '.aux', '.log', '.out', '.toc', '.fls', '.fdb_latexmk']
        
        for ext in extensions:
            file_path = base_name + ext
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except:
                    pass  # Ignorar errores de limpieza

# Wrapper para compatibilidad con API anterior
class ExercisePDFGenerator(RealTemplatePDFGenerator):
    """Wrapper para mantener compatibilidad con API anterior"""
    
    def generate_exam_pdf(self, 
                         exercises: List[Dict], 
                         exam_info: Dict,
                         include_solutions: bool = False,
                         filename: Optional[str] = None) -> Tuple[str, str]:
        """Compatibilidad con API anterior - genera interrogación"""
        return self.generate_prueba(exercises, exam_info)
    
    def generate_exercise_sheet(self, 
                               exercises: List[Dict], 
                               sheet_info: Dict,
                               filename: Optional[str] = None) -> str:
        """Compatibilidad con API anterior - genera guía"""
        return self.generate_guia(exercises, sheet_info)

# Test de integración
def test_real_templates():
    """Test usando templates reales"""
    print("🧪 TESTING PDF GENERATOR V3.0 - TEMPLATES REALES")
    print("=" * 60)
    
    try:
        generator = RealTemplatePDFGenerator("output", "templates")
        
        # Ejercicios de prueba
        exercises = [
            {
                'titulo': 'Convolución básica',
                'enunciado': 'Calcule la convolución y(t) = x(t) * h(t) donde x(t) = u(t) y h(t) = e^{-t}u(t).',
                'unidad_tematica': 'Sistemas Continuos',
                'nivel_dificultad': 'Básico',
                'modalidad': 'Teórico',
                'tiempo_estimado': 15,
                'puntos': 6,
                'solucion_completa': 'y(t) = (1 - e^{-t})u(t)'
            },
            {
                'titulo': 'FFT en Python',
                'enunciado': 'Implemente el cálculo de la FFT de una señal sinusoidal con ruido.',
                'unidad_tematica': 'Transformada de Fourier Discreta',
                'nivel_dificultad': 'Intermedio',
                'modalidad': 'Computacional',
                'tiempo_estimado': 30,
                'puntos': 4,
                'codigo_python': 'import numpy as np\nimport matplotlib.pyplot as plt\n# Completar implementación',
                'solucion_completa': 'La FFT muestra picos en las frecuencias de las sinusoidales.'
            }
        ]
        
        # Test 1: Guía
        print("\n1️⃣ Generando guía...")
        guide_info = {
            'nombre': 'Guía 1 - Sistemas Continuos',
            'unidad': 'Sistemas Continuos',
            'descripcion': 'Ejercicios de práctica para convolución y respuesta al impulso.'
        }
        guide_path = generator.generate_guia(exercises, guide_info)
        print(f"✅ Guía generada: {guide_path}")
        
        # Test 2: Prueba
        print("\n2️⃣ Generando prueba...")
        exam_info = {
            'nombre': 'Interrogación 1 - Sistemas Continuos',
            'fecha': '15 de Septiembre, 2024',
            'tiempo_total': 90
        }
        exam_path, sol_path = generator.generate_prueba(exercises, exam_info)
        print(f"✅ Prueba generada: {exam_path}")
        print(f"✅ Soluciones generadas: {sol_path}")
        
        # Test 3: Tarea
        print("\n3️⃣ Generando tarea...")
        task_info = {
            'numero': 1,
            'fecha_entrega': '30 de Septiembre',
            'hora_entrega': '23:59 hrs'
        }
        task_path = generator.generate_tarea(exercises, task_info)
        print(f"✅ Tarea generada: {task_path}")
        
        print("\n🎉 ¡TODOS LOS TESTS EXITOSOS!")
        print("📁 PDFs generados usando templates reales existentes")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_real_templates()