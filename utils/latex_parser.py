"""
Importador de ejercicios desde archivos LaTeX
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import re
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Mock streamlit functions for standalone use
    class MockStreamlit:
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
    st = MockStreamlit()

class LaTeXExerciseParser:
    """Parser para extraer ejercicios desde archivos LaTeX"""
    
    def __init__(self):
        # Patrones específicos para formato de Patricio
        self.exercise_patterns = [
            # Patrón 1: Items en enumerate dentro de subsecciones
            {
                'name': 'subsection_items',
                'pattern': r'\\subsection\*\{([^}]+)\}.*?\\begin\{enumerate\}(.*?)\\end\{enumerate\}',
                'priority': 1
            },
            # Patrón 2: Items individuales (fallback)
            {
                'name': 'individual_items',
                'pattern': r'\\item\s+(.*?)(?=\\item|\\end\{enumerate\}|\\ifanswers|\Z)',
                'priority': 2
            },
            # Patrón 3: Entornos ejercicio (genérico)
            {
                'name': 'ejercicio_environment',
                'start': r'\\begin\{ejercicio\}',
                'end': r'\\end\{ejercicio\}',
                'priority': 3
            },
            # Patrón 4: Secciones numeradas
            {
                'name': 'section_exercises',
                'pattern': r'\\(sub)?section\*?\{([^}]+)\}(.*?)(?=\\(sub)?section|\Z)',
                'priority': 4
            }
        ]
        
        # Patrones para soluciones específicas del formato
        self.solution_patterns = [
            r'\\ifanswers\s*\{\\color\{red\}.*?\\textbf\{Solución:\}(.*?)\}\s*\\fi',
            r'\\ifanswers\s*\{\\color\{red\}(.*?)\}\s*\\fi',
            r'\\begin\{solucion\}(.*?)\\end\{solucion\}'
        ]
        
        # Patrones para metadatos
        self.metadata_patterns = {
            'difficulty': [
                r'%\s*Dificultad:\s*(\w+)',
                r'\\dificultad\{([^}]+)\}',
                r'%\s*Nivel:\s*(\w+)'
            ],
            'unit': [
                r'%\s*Unidad:\s*([^\\n]+)',
                r'\\unidad\{([^}]+)\}',
                r'%\s*Tema:\s*([^\\n]+)'
            ],
            'time': [
                r'%\s*Tiempo:\s*(\d+)',
                r'\\tiempo\{(\d+)\}',
                r'%.*?(\d+)\s*min'
            ],
            'solution': [
                r'\\begin\{solucion\}(.*?)\\end\{solucion\}',
                r'\\solucion\{([^}]+)\}',
                r'%\s*Sol:\s*([^\\n]+)'
            ]
        }
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """Parsea un archivo LaTeX y extrae ejercicios"""
        try:
            content = self._read_latex_file(file_path)
            exercises = self._extract_exercises(content, file_path)
            return exercises
        except Exception as e:
            st.error(f"Error parseando archivo {file_path}: {str(e)}")
            return []
    
    def parse_content(self, content: str, source_name: str = "Manual") -> List[Dict]:
        """Parsea contenido LaTeX directo"""
        return self._extract_exercises(content, source_name)
    
    def _read_latex_file(self, file_path: str) -> str:
        """Lee archivo LaTeX con encoding apropiado"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"No se pudo leer el archivo {file_path} con ningún encoding")
    
    def _extract_exercises(self, content: str, source: str) -> List[Dict]:
        """Extrae ejercicios del contenido LaTeX"""
        exercises = []
        
        # Limpiar contenido
        content = self._clean_latex_content(content)
        
        # Intentar cada patrón en orden de prioridad
        for pattern_info in self.exercise_patterns:
            pattern_exercises = self._apply_pattern(content, pattern_info, source)
            if pattern_exercises:
                exercises.extend(pattern_exercises)
                break  # Usar solo el primer patrón que funcione
        
        # Si no encontramos ejercicios con patrones específicos, 
        # intentar división por párrafos/secciones
        if not exercises:
            exercises = self._fallback_extraction(content, source)
        
        # Enriquecer con metadatos
        for exercise in exercises:
            exercise.update(self._extract_metadata(exercise['raw_content']))
            exercise['fuente'] = source
            exercise['año_creacion'] = 2024  # Default
        
        return exercises
    
    def _clean_latex_content(self, content: str) -> str:
        """Limpia contenido LaTeX removiendo comandos no esenciales"""
        # Remover comentarios completos
        content = re.sub(r'^%.*$', '', content, flags=re.MULTILINE)
        
        # Remover comandos de formato que no necesitamos
        format_commands = [
            r'\\documentclass\{[^}]+\}',
            r'\\usepackage\{[^}]+\}',
            r'\\begin\{document\}',
            r'\\end\{document\}',
            r'\\maketitle',
            r'\\newpage',
            r'\\clearpage'
        ]
        
        for cmd in format_commands:
            content = re.sub(cmd, '', content)
        
        return content.strip()
    
    def _apply_pattern(self, content: str, pattern_info: Dict, source: str) -> List[Dict]:
        """Aplica un patrón específico para extraer ejercicios"""
        exercises = []
        
        # Si es el patrón de subsecciones, usar el parser específico de Patricio
        if pattern_info['name'] == 'subsection_items':
            return self._parse_patricio_format(content, source)
        
        if 'start' in pattern_info and 'end' in pattern_info:
            # Patrón de entorno (begin/end)
            pattern = f"{pattern_info['start']}(.*?){pattern_info['end']}"
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            
            for i, match in enumerate(matches, 1):
                exercise = self._create_exercise_dict(
                    title=f"Ejercicio {i}",
                    content=match.strip(),
                    raw_content=match,
                    pattern_used=pattern_info['name'],
                    source=source
                )
                exercises.append(exercise)
                
        elif 'pattern' in pattern_info:
            # Patrón de expresión regular directa
            matches = re.findall(pattern_info['pattern'], content, re.DOTALL | re.IGNORECASE)
            
            for i, match in enumerate(matches, 1):
                # Si el match es una tupla (grupos múltiples), tomar el último grupo
                if isinstance(match, tuple):
                    match = match[-1] if match else ""
                
                exercise = self._create_exercise_dict(
                    title=f"Ejercicio {i}",
                    content=str(match).strip(),
                    raw_content=str(match),
                    pattern_used=pattern_info['name'],
                    source=source
                )
                exercises.append(exercise)
        
        return exercises
    
    def _fallback_extraction(self, content: str, source: str) -> List[Dict]:
        """Extracción de respaldo cuando no se encuentran patrones específicos"""
        exercises = []
        
        # Dividir por párrafos significativos
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Filtrar párrafos que parezcan ejercicios (tienen cierta longitud y estructura)
        exercise_paragraphs = []
        for para in paragraphs:
            if (len(para) > 50 and  # Longitud mínima
                ('?' in para or 'calcul' in para.lower() or 'determin' in para.lower() or
                 'encuentr' in para.lower() or 'demuestre' in para.lower())):
                exercise_paragraphs.append(para)
        
        # Crear ejercicios
        for i, para in enumerate(exercise_paragraphs, 1):
            exercise = self._create_exercise_dict(
                title=f"Ejercicio {i}",
                content=para,
                raw_content=para,
                pattern_used='fallback_paragraphs',
                source=source
            )
            exercises.append(exercise)
        
        return exercises
    
    def _create_exercise_dict(self, title: str, content: str, raw_content: str, 
                            pattern_used: str, source: str) -> Dict:
        """Crea diccionario de ejercicio con estructura estándar"""
        return {
            'titulo': title,
            'enunciado': self._clean_exercise_content(content),
            'raw_content': raw_content,
            'pattern_used': pattern_used,
            'fuente': source,
            'unidad_tematica': 'Por determinar',
            'nivel_dificultad': 'Intermedio',  # Default
            'modalidad': 'Teórico',  # Default
            'tiempo_estimado': 20,  # Default
            'estado': 'En revisión',
            'palabras_clave': []
        }
    
    def _clean_exercise_content(self, content: str) -> str:
        """Limpia el contenido del ejercicio"""
        # Remover comandos LaTeX comunes pero mantener el contenido matemático
        content = re.sub(r'\\textbf\{([^}]+)\}', r'\1', content)  # Bold
        content = re.sub(r'\\textit\{([^}]+)\}', r'\1', content)  # Italic
        content = re.sub(r'\\emph\{([^}]+)\}', r'\1', content)   # Emphasis
        
        # Mantener matemáticas pero limpiar espacios
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        return content
    
    def _extract_metadata(self, content: str) -> Dict:
        """Extrae metadatos del contenido del ejercicio"""
        metadata = {}
        
        for meta_type, patterns in self.metadata_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    
                    # Procesar según el tipo
                    if meta_type == 'difficulty':
                        metadata['nivel_dificultad'] = self._normalize_difficulty(value)
                    elif meta_type == 'unit':
                        metadata['unidad_tematica'] = self._normalize_unit(value)
                    elif meta_type == 'time':
                        try:
                            metadata['tiempo_estimado'] = int(value)
                        except ValueError:
                            pass
                    elif meta_type == 'solution' and value:
                        metadata['solucion_completa'] = self._clean_exercise_content(value)
                    
                    break  # Usar solo el primer match
        
        return metadata
    
    def _normalize_difficulty(self, difficulty: str) -> str:
        """Normaliza el nivel de dificultad"""
        difficulty = difficulty.lower().strip()
        
        mapping = {
            'facil': 'Básico',
            'fácil': 'Básico', 
            'basico': 'Básico',
            'básico': 'Básico',
            'easy': 'Básico',
            'medio': 'Intermedio',
            'intermedio': 'Intermedio',
            'intermediate': 'Intermedio',
            'dificil': 'Avanzado',
            'difícil': 'Avanzado',
            'avanzado': 'Avanzado',
            'hard': 'Avanzado',
            'desafio': 'Desafío',
            'desafío': 'Desafío',
            'challenge': 'Desafío'
        }
        
        return mapping.get(difficulty, 'Intermedio')
    
    def _parse_patricio_format(self, content: str, source: str) -> List[Dict]:
        """Parser específico para el formato de Patricio - versión mejorada"""
        exercises = []
        
        # Buscar subsecciones con ejercicios
        subsection_pattern = r'\\subsection\*\{([^}]+)\}(.*?)(?=\\subsection\*|\\section|\\end\{document\}|\Z)'
        subsections = re.findall(subsection_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for subsection_title, subsection_content in subsections:
            # Mapear título de subsección a unidad temática
            unit = self._map_subsection_to_unit(subsection_title)
            
            # Nueva estrategia: buscar bloques completos ejercicio+solución
            exercises_in_subsection = self._extract_complete_exercises(subsection_content)
            
            for i, (enunciado, solucion) in enumerate(exercises_in_subsection, 1):
                if enunciado.strip():  # Solo si hay contenido
                    exercise = {
                        'titulo': f"{subsection_title} - Ejercicio {i}",
                        'enunciado': self._clean_exercise_content(enunciado),
                        'solucion_completa': self._clean_exercise_content(solucion) if solucion else "",
                        'unidad_tematica': unit,
                        'nivel_dificultad': self._infer_difficulty(enunciado),
                        'modalidad': self._infer_modality(enunciado),
                        'tiempo_estimado': self._infer_time(enunciado),
                        'fuente': source,
                        'año_creacion': 2024,
                        'estado': 'Listo',
                        'pattern_used': 'patricio_format_v2',
                        'raw_content': f"{enunciado}\n{solucion}" if solucion else enunciado,
                        'palabras_clave': self._extract_keywords(enunciado)
                    }
                    exercises.append(exercise)
        
        return exercises
    
    def _extract_complete_exercises(self, subsection_content: str) -> List[Tuple[str, str]]:
        """Extrae ejercicios completos con sus soluciones - método simplificado"""
        exercises = []
        
        # Buscar enumerate dentro de la subsección
        enum_pattern = r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}'
        enum_match = re.search(enum_pattern, subsection_content, re.DOTALL)
        
        if not enum_match:
            return exercises
        
        enum_content = enum_match.group(1)
        
        # Estrategia simple pero efectiva:
        # Dividir por \item, luego reconstruir ejercicios basándose en \ifanswers
        
        # Primero dividir por \item
        parts = re.split(r'\\item\s+', enum_content)
        
        for part in parts[1:]:  # Saltar primer elemento vacío
            if not part.strip():
                continue
            
            # Cada part puede contener un ejercicio completo con solución
            full_item = f"\\item {part}"
            
            # Separar enunciado y solución usando el método mejorado
            enunciado, solucion = self._separate_statement_solution_v2(full_item)
            
            if enunciado.strip():
                exercises.append((enunciado, solucion))
        
        return exercises
    
    def _separate_statement_solution_v2(self, item_content: str) -> Tuple[str, str]:
        """Versión mejorada para separar enunciado de solución"""
        
        # Verificar si tiene solución
        if '\\ifanswers' not in item_content:
            # Limpiar el \item del inicio
            clean_content = re.sub(r'^\\item\s+', '', item_content).strip()
            return clean_content, ""
        
        # Encontrar la posición donde empieza \ifanswers
        ifanswers_match = re.search(r'\\ifanswers', item_content)
        if not ifanswers_match:
            clean_content = re.sub(r'^\\item\s+', '', item_content).strip()
            return clean_content, ""
        
        # Dividir en enunciado (antes de \ifanswers) y bloque de solución
        split_pos = ifanswers_match.start()
        enunciado_part = item_content[:split_pos].strip()
        solution_block = item_content[split_pos:].strip()
        
        # Limpiar el \item del enunciado
        enunciado = re.sub(r'^\\item\s+', '', enunciado_part).strip()
        
        # Extraer solución del bloque
        solucion = ""
        
        # Patrón mejorado para extraer contenido de \ifanswers
        solution_patterns = [
            # Capturar todo el contenido entre las llaves principales de \ifanswers
            r'\\ifanswers\s*\{(.*)\}\s*\\fi',
            # Backup: capturar desde \ifanswers hasta \fi
            r'\\ifanswers(.*?)\\fi'
        ]
        
        for pattern in solution_patterns:
            match = re.search(pattern, solution_block, re.DOTALL)
            if match:
                raw_solution = match.group(1)
                
                # Limpiar comandos LaTeX de formato
                solucion = re.sub(r'\\color\{red\}', '', raw_solution)
                solucion = re.sub(r'\\textbf\{Solución:\}', '', solucion)
                solucion = re.sub(r'\\textbf\{[^}]*\}', '', solucion)
                solucion = re.sub(r'\\textit\{[^}]*\}', '', solucion)
                solucion = solucion.strip()
                
                if solucion:
                    break
        
        return enunciado, solucion
    
    def _extract_main_items_only(self, enum_content: str) -> List[str]:
        """Extrae solo los items principales, manteniendo subitems como parte del ejercicio"""
        
        # Nueva estrategia: buscar patrones de ejercicios completos
        # Un ejercicio completo termina con \ifanswers o con el siguiente ejercicio
        
        # Patrón: buscar \item seguido de contenido hasta \ifanswers...\fi o próximo \item principal
        exercise_pattern = r'\\item\s+(.*?)(?=\\item\s+(?![^{]*})|$)'
        potential_exercises = re.findall(exercise_pattern, enum_content, re.DOTALL)
        
        real_exercises = []
        
        for potential in potential_exercises:
            potential = potential.strip()
            if not potential:
                continue
                
            # Un ejercicio real debe tener contenido sustancial
            # Y típicamente tiene \ifanswers o es lo suficientemente largo
            has_solution = '\\ifanswers' in potential
            is_substantial = len(potential.replace(' ', '').replace('\n', '')) > 30
            
            # Si tiene solución, definitivamente es un ejercicio
            # Si no tiene solución pero es sustancial, también lo consideramos
            if has_solution or is_substantial:
                real_exercises.append(potential)
        
        return real_exercises
    
    def _map_subsection_to_unit(self, subsection_title: str) -> str:
        """Mapea títulos de subsección a unidades temáticas"""
        title_lower = subsection_title.lower()
        
        mapping = {
            'números complejos': 'Introducción',
            'señales y sistemas': 'Sistemas Continuos', 
            'gráficos': 'Introducción',
            'simetrías': 'Introducción',
            'funciones importantes': 'Introducción',
            'impulso': 'Introducción',
            'sistemas lineales': 'Sistemas Continuos',
            'convolución': 'Sistemas Continuos',
            'respuesta al impulso': 'Sistemas Continuos',
            'fourier': 'Transformada de Fourier',
            'laplace': 'Transformada de Laplace',
            'discreto': 'Sistemas Discretos',
            'muestreo': 'Sistemas Discretos',
            'dft': 'Transformada de Fourier Discreta',
            'transformada z': 'Transformada Z'
        }
        
        for key, unit in mapping.items():
            if key in title_lower:
                return unit
        
        return 'Por determinar'
    
    def _normalize_difficulty(self, difficulty: str) -> str:
        """Normaliza el nivel de dificultad"""
        difficulty = difficulty.lower().strip()
        
        mapping = {
            'facil': 'Básico',
            'fácil': 'Básico', 
            'basico': 'Básico',
            'básico': 'Básico',
            'easy': 'Básico',
            'medio': 'Intermedio',
            'intermedio': 'Intermedio',
            'intermediate': 'Intermedio',
            'dificil': 'Avanzado',
            'difícil': 'Avanzado',
            'avanzado': 'Avanzado',
            'hard': 'Avanzado',
            'desafio': 'Desafío',
            'desafío': 'Desafío',
            'challenge': 'Desafío'
        }
        
        return mapping.get(difficulty, 'Intermedio')
    
    def _extract_items_from_enumerate(self, enum_content: str) -> List[str]:
        """Extrae items individuales de un enumerate, preservando subestructuras"""
        items = []
        
        # Dividir por \item pero manteniendo cuidado con enumerate anidados
        parts = re.split(r'(?<!\\)\\item\s+', enum_content)
        
        for part in parts[1:]:  # Saltar el primer elemento vacío
            if part.strip():
                # Verificar si este item tiene enumerate/itemize anidados
                item_content = part.strip()
                
                # Contar niveles de anidamiento para decidir si es un ejercicio completo
                nested_enums = len(re.findall(r'\\begin\{enumerate\}|\\begin\{itemize\}', item_content))
                nested_items = len(re.findall(r'\\item', item_content))
                
                # Si tiene estructuras anidadas significativas, es probablemente un ejercicio completo
                # Si solo tiene 1-2 items anidados, mantenemos todo junto
                if nested_enums > 0 or nested_items <= 3:
                    items.append(item_content)
                else:
                    # Si tiene muchos items anidados sin estructura, podría necesitar división
                    items.append(item_content)
        
        return items
    
    def _separate_statement_solution(self, item_content: str) -> Tuple[str, str]:
        """Separa enunciado de solución en formato ifanswers, preservando estructura"""
        
        # Debug: verificar si hay ifanswers
        if '\\ifanswers' not in item_content:
            return item_content.strip(), ""
        
        # Patrones más robustos y específicos para el formato de Patricio
        solution_patterns = [
            # Patrón más específico para el formato exacto de Patricio
            r'\\ifanswers\s*\{\s*\\color\{red\}\s*\\textbf\{Solución:\}\s*(.*?)\s*\}\s*\\fi',
            # Sin espacios extras
            r'\\ifanswers\s*\{\\color\{red\}\\textbf\{Solución:\}(.*?)\}\s*\\fi',
            # Variación con \textit
            r'\\ifanswers\s*\{\\color\{red\}\s*\\textbf\{Solución:\}\s*\\textit\{(.*?)\}\s*\}\s*\\fi',
            # Patrón más general - capturar todo después de {
            r'\\ifanswers\s*\{\\color\{red\}[^}]*\}(.*?)\}\s*\\fi',
            # Patrón súper general - solo el contenido entre las llaves principales
            r'\\ifanswers\s*\{(.*?)\}\s*\\fi'
        ]
        
        solution = ""
        statement = item_content
        
        # Probar cada patrón
        for i, pattern in enumerate(solution_patterns):
            matches = re.findall(pattern, item_content, re.DOTALL | re.IGNORECASE)
            if matches:
                # Tomar la coincidencia más larga (más probable que sea correcta)
                solution = max(matches, key=len).strip()
                
                # Limpiar comandos LaTeX básicos de la solución
                solution = re.sub(r'\\textbf\{[^}]*\}', '', solution)
                solution = re.sub(r'\\textit\{[^}]*\}', '', solution)
                solution = re.sub(r'\\color\{[^}]*\}', '', solution)
                solution = solution.strip()
                
                if solution:  # Si encontramos algo válido
                    break
        
        # Remover toda la sección ifanswers del enunciado
        if solution:
            # Usar un patrón más simple para remover
            ifanswers_removal_pattern = r'\\ifanswers.*?\\fi'
            statement = re.sub(ifanswers_removal_pattern, '', item_content, flags=re.DOTALL).strip()
        
        # Limpiar el enunciado pero preservar estructura de subpreguntas
        statement = self._clean_statement_preserve_structure(statement)
        
        return statement, solution
    
    def _clean_statement_preserve_structure(self, statement: str) -> str:
        """Limpia el enunciado pero preserva la estructura de subpreguntas"""
        # No remover enumerate/itemize anidados - son parte del ejercicio
        # Solo limpiar comandos de formato básicos
        
        # Limpiar comandos básicos pero mantener estructura matemática y listas
        cleaned = re.sub(r'\\textbf\{([^}]+)\}', r'\1', statement)  # Bold
        cleaned = re.sub(r'\\textit\{([^}]+)\}', r'\1', cleaned)   # Italic
        cleaned = re.sub(r'\\emph\{([^}]+)\}', r'\1', cleaned)     # Emphasis
        
        # Mantener matemáticas, listas, y estructura
        # Solo limpiar espacios excesivos
        cleaned = re.sub(r'\n\s*\n\s*\n', r'\n\n', cleaned)  # Máximo 2 líneas vacías
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _infer_difficulty(self, content: str) -> str:
        """Infiere dificultad basado en palabras clave y complejidad"""
        content_lower = content.lower()
        
        # Palabras clave para diferentes niveles
        basic_keywords = ['calcule', 'determine', 'grafique', 'simple']
        advanced_keywords = ['demuestre', 'derive', 'analice', 'complejo', 'integral', 'ecuación diferencial']
        
        basic_count = sum(1 for word in basic_keywords if word in content_lower)
        advanced_count = sum(1 for word in advanced_keywords if word in content_lower)
        
        # Complejidad por longitud y símbolos matemáticos
        math_symbols = len(re.findall(r'\\[a-zA-Z]+|[\$\{\}]', content))
        
        if advanced_count > basic_count or math_symbols > 10:
            return 'Avanzado'
        elif basic_count > 0 or math_symbols > 5:
            return 'Intermedio'
        else:
            return 'Básico'
    
    def _infer_modality(self, content: str) -> str:
        """Infiere modalidad basado en contenido"""
        content_lower = content.lower()
        
        computational_keywords = ['python', 'código', 'implemente', 'programe', 'compute']
        
        if any(word in content_lower for word in computational_keywords):
            return 'Computacional'
        elif 'grafique' in content_lower:
            return 'Mixto'
        else:
            return 'Teórico'
    
    def _infer_time(self, content: str) -> int:
        """Infiere tiempo estimado basado en complejidad"""
        # Factores de complejidad
        word_count = len(content.split())
        math_complexity = len(re.findall(r'\\[a-zA-Z]+', content))
        has_parts = 'enumerate' in content or len(re.findall(r'\([a-z]\)', content)) > 1
        
        base_time = 15
        if word_count > 100:
            base_time += 10
        if math_complexity > 5:
            base_time += 10
        if has_parts:
            base_time += 15
            
        return min(base_time, 60)  # Máximo 60 minutos
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extrae palabras clave relevantes"""
        content_lower = content.lower()
        
        keyword_patterns = [
            'convolución', 'fourier', 'laplace', 'transformada', 'impulso',
            'lineal', 'sistema', 'señal', 'función', 'complejo', 'muestreo',
            'discreto', 'continuo', 'estabilidad', 'causal', 'dft', 'fft'
        ]
        
        found_keywords = [kw for kw in keyword_patterns if kw in content_lower]
        return found_keywords[:5]  # Máximo 5 palabras clave
    
    def _normalize_unit(self, unit: str) -> str:
        """Normaliza la unidad temática"""
        unit = unit.lower().strip()
        
        # Mapeo de palabras clave a unidades del programa
        unit_mapping = {
            'introduccion': 'Introducción',
            'introducción': 'Introducción',
            'introduction': 'Introducción',
            'sistemas continuos': 'Sistemas Continuos',
            'continuo': 'Sistemas Continuos',
            'convolucion': 'Sistemas Continuos',
            'convolución': 'Sistemas Continuos',
            'fourier': 'Transformada de Fourier',
            'serie': 'Transformada de Fourier',
            'laplace': 'Transformada de Laplace',
            'discreto': 'Sistemas Discretos',
            'muestreo': 'Sistemas Discretos',
            'dft': 'Transformada de Fourier Discreta',
            'fft': 'Transformada de Fourier Discreta',
            'transformada z': 'Transformada Z',
            'z transform': 'Transformada Z'
        }
        
        for key, value in unit_mapping.items():
            if key in unit:
                return value
        
        return 'Por determinar'
        """Normaliza la unidad temática"""
        unit = unit.lower().strip()
        
        # Mapeo de palabras clave a unidades del programa
        unit_mapping = {
            'introduccion': 'Introducción',
            'introducción': 'Introducción',
            'introduction': 'Introducción',
            'sistemas continuos': 'Sistemas Continuos',
            'continuo': 'Sistemas Continuos',
            'convolucion': 'Sistemas Continuos',
            'convolución': 'Sistemas Continuos',
            'fourier': 'Transformada de Fourier',
            'serie': 'Transformada de Fourier',
            'laplace': 'Transformada de Laplace',
            'discreto': 'Sistemas Discretos',
            'muestreo': 'Sistemas Discretos',
            'dft': 'Transformada de Fourier Discreta',
            'fft': 'Transformada de Fourier Discreta',
            'transformada z': 'Transformada Z',
            'z transform': 'Transformada Z'
        }
        
        for key, value in unit_mapping.items():
            if key in unit:
                return value
        
        return 'Por determinar'

# Funciones de utilidad para Streamlit
def create_parser_interface():
    """Crea la interfaz de Streamlit para el parser"""
    st.subheader("🔄 Importador de Ejercicios LaTeX")
    
    # Opciones de entrada
    input_method = st.radio(
        "Método de entrada:",
        ["📁 Subir archivo LaTeX", "📝 Pegar código LaTeX", "🔗 URL de Overleaf (próximamente)"]
    )
    
    parser = LaTeXExerciseParser()
    exercises = []
    
    if input_method == "📁 Subir archivo LaTeX":
        uploaded_file = st.file_uploader(
            "Selecciona archivo .tex",
            type=['tex', 'txt'],
            help="Sube tu archivo LaTeX con ejercicios"
        )
        
        if uploaded_file is not None:
            # Leer contenido del archivo
            content = str(uploaded_file.read(), "utf-8")
            
            with st.expander("👀 Vista previa del archivo", expanded=False):
                st.code(content[:1000] + "..." if len(content) > 1000 else content, language="latex")
            
            # Parsear
            if st.button("🔄 Extraer Ejercicios"):
                with st.spinner("Extrayendo ejercicios..."):
                    exercises = parser.parse_content(content, uploaded_file.name)
    
    elif input_method == "📝 Pegar código LaTeX":
        latex_content = st.text_area(
            "Pega tu código LaTeX aquí:",
            height=300,
            placeholder="\\begin{ejercicio}\nCalcule la convolución...\n\\end{ejercicio}"
        )
        
        if latex_content and st.button("🔄 Extraer Ejercicios"):
            with st.spinner("Extrayendo ejercicios..."):
                exercises = parser.parse_content(latex_content, "Contenido manual")
    
    else:
        st.info("🚧 Función en desarrollo - próximamente podrás importar directamente desde Overleaf")
    
    return exercises

def display_parsed_exercises(exercises: List[Dict]):
    """Muestra los ejercicios parseados para revisión"""
    if not exercises:
        st.warning("No se encontraron ejercicios en el contenido proporcionado.")
        st.info("""
        **Consejos para mejorar la detección:**
        - Asegúrate de usar patrones reconocibles como `\\begin{ejercicio}...\\end{ejercicio}`
        - O incluir comentarios como `% Dificultad: Intermedio`
        - Los ejercicios deben tener cierta longitud y palabras clave como 'calcule', 'determine', etc.
        """)
        return
    
    st.success(f"✅ Se encontraron {len(exercises)} ejercicios")
    
    # Mostrar resumen
    with st.expander("📊 Resumen de ejercicios encontrados", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total", len(exercises))
        
        with col2:
            patterns_used = [ex.get('pattern_used', 'unknown') for ex in exercises]
            most_common = max(set(patterns_used), key=patterns_used.count)
            st.metric("Patrón principal", most_common.replace('_', ' ').title())
        
        with col3:
            avg_length = sum(len(ex.get('enunciado', '')) for ex in exercises) // len(exercises)
            st.metric("Longitud promedio", f"{avg_length} chars")
    
    # Mostrar ejercicios individuales
    for i, exercise in enumerate(exercises):
        with st.expander(f"📝 {exercise.get('titulo', f'Ejercicio {i+1}')}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Enunciado:**")
                st.write(exercise.get('enunciado', 'No disponible'))
                
                if exercise.get('solucion_completa'):
                    st.write("**Solución encontrada:**")
                    st.write(exercise['solucion_completa'])
            
            with col2:
                st.write("**Metadatos detectados:**")
                st.write(f"- **Dificultad:** {exercise.get('nivel_dificultad', 'No especificada')}")
                st.write(f"- **Unidad:** {exercise.get('unidad_tematica', 'No especificada')}")
                st.write(f"- **Tiempo:** {exercise.get('tiempo_estimado', 'No especificado')} min")
                st.write(f"- **Patrón usado:** {exercise.get('pattern_used', 'No especificado')}")
    
    return exercises

def import_exercises_to_db(exercises: List[Dict], db_manager):
    """Importa ejercicios a la base de datos"""
    if not exercises:
        return
    
    st.subheader("💾 Importar a Base de Datos")
    
    # Opciones de importación
    col1, col2 = st.columns(2)
    
    with col1:
        import_all = st.checkbox("Importar todos los ejercicios", value=True)
        
    with col2:
        if not import_all:
            selected_indices = st.multiselect(
                "Seleccionar ejercicios:",
                range(len(exercises)),
                format_func=lambda x: f"Ejercicio {x+1}: {exercises[x].get('titulo', 'Sin título')[:50]}..."
            )
        else:
            selected_indices = list(range(len(exercises)))
    
    if st.button("💾 Confirmar Importación", type="primary"):
        if selected_indices:
            success_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, idx in enumerate(selected_indices):
                try:
                    exercise = exercises[idx]
                    db_manager.agregar_ejercicio(exercise)
                    success_count += 1
                    
                    progress = (i + 1) / len(selected_indices)
                    progress_bar.progress(progress)
                    status_text.text(f"Importando ejercicio {i+1} de {len(selected_indices)}")
                    
                except Exception as e:
                    st.error(f"Error importando ejercicio {idx+1}: {str(e)}")
            
            st.success(f"✅ Se importaron {success_count} de {len(selected_indices)} ejercicios exitosamente!")
            st.balloons()
            
            # Limpiar la interfaz
            if st.button("🔄 Importar más ejercicios"):
                st.experimental_rerun()
        else:
            st.warning("Selecciona al menos un ejercicio para importar")