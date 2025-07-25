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
    
    def _compile_to_pdf(self, tex_path: Path) -> str:
        """Compila el archivo .tex a PDF"""
        try:
            # Ejecutar pdflatex
            cmd = ['pdflatex', '-interaction=nonstopmode', str(tex_path)]
            
            # Cambiar al directorio de salida para que los archivos auxiliares se creen ahí
            original_dir = os.getcwd()
            os.chdir(self.output_dir)
            
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
                return str(tex_path)
                
        except FileNotFoundError:
            print("⚠️  pdflatex no encontrado, manteniendo archivo .tex")
            return str(tex_path)
        except Exception as e:
            print(f"⚠️  Error compilando: {e}, manteniendo archivo .tex")
            return str(tex_path)
    
    def generate_guia(self, exercises: List[Dict], guide_info: Dict) -> str:
        """Genera guía usando template"""
        template_path = self.templates_dir / 'guia_template.tex'
        if not template_path.exists():
            raise FileNotFoundError(f"Template no encontrado: {template_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_tex = self.output_dir / f"guia_{timestamp}.tex"
        
        # Por ahora, copiar el template
        shutil.copy(template_path, output_tex)
        print(f"✅ Archivo .tex creado: {output_tex}")
        
        # Intentar compilar a PDF
        pdf_path = self._compile_to_pdf(output_tex)
        
        return pdf_path
    
    def generate_prueba(self, exercises: List[Dict], exam_info: Dict) -> Tuple[str, str]:
        """Genera prueba"""
        template_path = self.templates_dir / 'prueba_template.tex'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_tex = self.output_dir / f"prueba_{timestamp}.tex"
        
        shutil.copy(template_path, output_tex)
        print(f"✅ Archivo .tex creado: {output_tex}")
        
        pdf_path = self._compile_to_pdf(output_tex)
        
        # Por ahora, retornar el mismo archivo para ambos
        return pdf_path, pdf_path
    
    def generate_tarea(self, exercises: List[Dict], task_info: Dict) -> str:
        """Genera tarea"""
        template_path = self.templates_dir / 'tarea_template.tex'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_tex = self.output_dir / f"tarea_{timestamp}.tex"
        
        shutil.copy(template_path, output_tex)
        print(f"✅ Archivo .tex creado: {output_tex}")
        
        pdf_path = self._compile_to_pdf(output_tex)
        
        return pdf_path

class ExercisePDFGenerator(RealTemplatePDFGenerator):
    """Wrapper para compatibilidad"""
    pass
