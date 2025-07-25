"""
Parser LaTeX para importación de ejercicios
Sistema de Gestión de Ejercicios - Señales y Sistemas
Patricio de la Cuadra - PUC Chile

VERSIÓN CORREGIDA: No divide ejercicios multi-parte
"""

import re
import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ParsedExercise:
    """Clase para almacenar ejercicios parseados"""
    titulo: str
    enunciado: str
    solucion_completa: Optional[str] = None
    respuesta_final: Optional[str] = None
    nivel_dificultad: str = "Intermedio"
    unidad_tematica: str = "Por determinar"
    tiempo_estimado: int = 20
    modalidad: str = "Teórico"
    subtemas: List[str] = None
    palabras_clave: List[str] = None
    tipo_actividad: List[str] = None
    comentarios: str = ""
    pattern_used: str = ""
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.subtemas is None:
            self.subtemas = []
        if self.palabras_clave is None:
            self.palabras_clave = []
        if self.tipo_actividad is None:
            self.tipo_actividad = ["Ayudantía"]

class LaTeXParser:
    """Parser principal para archivos LaTeX de ejercicios"""
    
    def __init__(self):
        self.unidad_keywords = {
            "Introducción": ["introducción", "señal", "sistema", "entrada", "salida", "causalidad"],
            "Sistemas Continuos": ["convolución", "impulso", "lineal", "invariante", "continuo", "ecuación diferencial"],
            "Transformada de Fourier": ["fourier", "serie", "frecuencia", "espectro", "transformada ft"],
            "Transformada de Laplace": ["laplace", "transformada lt", "polo", "cero", "convergencia"],
            "Sistemas Discretos": ["discreto", "muestreo", "digital", "convertidor", "teorema muestreo"],
            "Transformada de Fourier Discreta": ["dft", "fft", "transformada discreta", "aliasing"],
            "Transformada Z": ["transformada z", "plano z", "estabilidad", "región convergencia"]
        }
        
        self.difficulty_keywords = {
            "Básico": ["calcule", "determine", "grafique", "simple", "directo"],
            "Intermedio": ["analice", "compare", "demuestre", "implemente", "diseñe"],
            "Avanzado": ["optimice", "derive", "investigue", "complejo", "múltiple"],
            "Desafío": ["pruebe", "generalice", "creative", "desafío", "investigación"]
        }
        
    def parse_file(self, file_content: str) -> List[ParsedExercise]:
        """Parsea un archivo LaTeX completo"""
        try:
            logger.info("Iniciando parsing de archivo LaTeX")
            exercises = []
            
            # Limpiar y preprocessar el contenido
            cleaned_content = self._preprocess_content(file_content)
            
            # ESTRATEGIA CORREGIDA: Buscar ejercicios COMPLETOS primero
            # 1. Ejercicios con environment específico
            env_exercises = self._parse_ejercicio_environment(cleaned_content)
            if env_exercises:
                exercises.extend(env_exercises)
                logger.info(f"Patrón ejercicio_environment encontró {len(env_exercises)} ejercicios")
            
            # 2. Si no hay environments, buscar por subsecciones (método Patricio)
            if not exercises:
                subsection_exercises = self._parse_subsection_complete_exercises(cleaned_content)
                if subsection_exercises:
                    exercises.extend(subsection_exercises)
                    logger.info(f"Patrón subsection_complete encontró {len(subsection_exercises)} ejercicios")
            
            # 3. Si aún no hay ejercicios, intentar parsing genérico conservador
            if not exercises:
                logger.warning("No se encontraron patrones específicos, intentando parsing genérico")
                exercises = self._parse_generic_content_conservative(cleaned_content)
            
            # Post-procesar y enriquecer ejercicios
            enriched_exercises = []
            for exercise in exercises:
                enriched = self._enrich_exercise_metadata(exercise)
                enriched_exercises.append(enriched)
            
            logger.info(f"Parser completado. Total ejercicios encontrados: {len(enriched_exercises)}")
            return enriched_exercises
            
        except Exception as e:
            logger.error(f"Error durante el parsing: {str(e)}")
            raise ParseError(f"Error al parsear archivo LaTeX: {str(e)}")
    
    def _preprocess_content(self, content: str) -> str:
        """Preprocesa el contenido LaTeX"""
        # Remover comentarios LaTeX (excepto metadatos)
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Mantener comentarios que parecen metadatos
            if line.strip().startswith('%') and any(keyword in line.lower() for keyword in 
                ['dificultad', 'unidad', 'tiempo', 'modalidad', 'tipo']):
                cleaned_lines.append(line)
            # Remover otros comentarios
            elif '%' in line and not line.strip().startswith('\\'):
                cleaned_lines.append(line.split('%')[0])
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _parse_ejercicio_environment(self, content: str) -> List[ParsedExercise]:
        """Parsea ejercicios usando environment \\begin{ejercicio}...\\end{ejercicio}"""
        exercises = []
        
        # Patrón para ejercicios con environment
        pattern = r'\\begin\{ejercicio\}(.*?)\\end\{ejercicio\}'
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, match in enumerate(matches):
            # Buscar metadatos en comentarios antes del ejercicio
            metadata = self._extract_metadata_from_comments(match)
            
            # Extraer enunciado y solución
            enunciado, solucion = self._extract_content_parts(match)
            
            exercise = ParsedExercise(
                titulo=f"Ejercicio {i+1} (environment)",
                enunciado=enunciado,
                solucion_completa=solucion,
                pattern_used="ejercicio_environment",
                confidence_score=0.9,
                **metadata
            )
            exercises.append(exercise)
        
        return exercises
    
    def _parse_subsection_complete_exercises(self, content: str) -> List[ParsedExercise]:
        """
        Parsea ejercicios del formato Patricio manteniendo ejercicios multi-parte juntos
        VERSIÓN CORREGIDA: No divide por items individuales
        """
        exercises = []
        
        # Buscar subsecciones que contengan ejercicios
        subsection_pattern = r'\\subsection\*\{([^}]+)\}(.*?)(?=\\subsection\*|\\section|\\end\{document\}|\Z)'
        subsections = re.findall(subsection_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for subsection_title, subsection_content in subsections:
            # Mapear título de subsección a unidad temática
            unit = self._map_subsection_to_unit(subsection_title)
            
            # NUEVA ESTRATEGIA: Buscar bloques enumerate COMPLETOS
            complete_exercises = self._extract_complete_enumerate_blocks(subsection_content)
            
            for i, (exercise_content, solution_content) in enumerate(complete_exercises):
                if exercise_content.strip():  # Solo si hay contenido
                    exercise = ParsedExercise(
                        titulo=f"{subsection_title} - Ejercicio {i+1}",
                        enunciado=self._clean_latex_text(exercise_content),
                        solucion_completa=self._clean_latex_text(solution_content) if solution_content else None,
                        unidad_tematica=unit,
                        nivel_dificultad=self._detect_difficulty(exercise_content),
                        modalidad=self._detect_modality(exercise_content),
                        tiempo_estimado=self._estimate_time(exercise_content, "Intermedio"),
                        pattern_used="subsection_complete",
                        confidence_score=0.8,
                        palabras_clave=self._extract_keywords(exercise_content),
                        comentarios=f"Extraído de subsección: {subsection_title}"
                    )
                    exercises.append(exercise)
        
        return exercises
    
    def _extract_complete_enumerate_blocks(self, subsection_content: str) -> List[tuple]:
        """
        Extrae bloques enumerate COMPLETOS sin dividir por items
        Esta es la función clave que estaba causando el problema
        """
        exercise_blocks = []
        
        # Buscar todos los bloques enumerate en la subsección
        enumerate_pattern = r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}'
        enumerate_matches = re.findall(enumerate_pattern, subsection_content, re.DOTALL)
        
        for enumerate_content in enumerate_matches:
            # CAMBIO CLAVE: En lugar de dividir por \item, buscar patrones de ejercicio COMPLETO
            
            # Estrategia 1: Si todo el enumerate tiene una sola solución al final, es UN ejercicio
            if self._is_single_exercise_with_parts(enumerate_content):
                # Separar enunciado (todo el enumerate) de solución
                exercise_part, solution_part = self._separate_exercise_solution(enumerate_content)
                if exercise_part.strip():
                    exercise_blocks.append((exercise_part, solution_part))
            
            # Estrategia 2: Si hay múltiples soluciones \ifanswers, dividir por esas
            else:
                multi_exercises = self._split_by_solution_blocks(enumerate_content)
                exercise_blocks.extend(multi_exercises)
        
        return exercise_blocks
    
    def _is_single_exercise_with_parts(self, enumerate_content: str) -> bool:
        """
        Determina si un bloque enumerate es un solo ejercicio con sub-partes
        En lugar de múltiples ejercicios separados
        """
        # Contar bloques \ifanswers
        ifanswers_count = len(re.findall(r'\\ifanswers', enumerate_content))
        
        # Si hay 0 o 1 bloque de respuesta, es un ejercicio con partes
        # Si hay múltiples bloques de respuesta, pueden ser ejercicios separados
        return ifanswers_count <= 1
    
    def _separate_exercise_solution(self, enumerate_content: str) -> tuple:
        """Separa ejercicio de solución en un bloque enumerate"""
        
        # Buscar \ifanswers al final del bloque
        ifanswers_pattern = r'\\ifanswers\s*\{.*?\}\s*\\fi'
        ifanswers_match = re.search(ifanswers_pattern, enumerate_content, re.DOTALL)
        
        if ifanswers_match:
            # Hay solución - separar
            solution_start = ifanswers_match.start()
            exercise_part = enumerate_content[:solution_start].strip()
            solution_part = ifanswers_match.group(0)
            
            # Limpiar la solución
            solution_cleaned = self._extract_solution_content(solution_part)
            
            return exercise_part, solution_cleaned
        else:
            # No hay solución - todo es ejercicio
            return enumerate_content.strip(), ""
    
    def _split_by_solution_blocks(self, enumerate_content: str) -> List[tuple]:
        """
        Divide contenido por bloques de solución cuando hay múltiples ejercicios
        Solo como fallback cuando realmente hay múltiples ejercicios distintos
        """
        exercises = []
        
        # Dividir por patrones que indican ejercicios separados
        # Buscar patrones como "Ejercicio X:" o números/letras al inicio de párrafo
        
        # Patrón conservador: solo dividir si hay indicadores claros de ejercicios separados
        exercise_indicators = [
            r'\n\s*\d+\.\s+',  # "1. ", "2. ", etc.
            r'\n\s*Ejercicio\s+\d+',  # "Ejercicio 1", etc.
            r'\n\s*[A-Z]\)\s+',  # "A) ", "B) ", etc. (menos común en enumerate)
        ]
        
        split_positions = []
        for pattern in exercise_indicators:
            for match in re.finditer(pattern, enumerate_content):
                split_positions.append(match.start())
        
        if not split_positions:
            # No hay indicadores claros - tratar como un solo ejercicio
            exercise_part, solution_part = self._separate_exercise_solution(enumerate_content)
            return [(exercise_part, solution_part)]
        
        # Hay indicadores - dividir conservadoramente
        split_positions.sort()
        split_positions = [0] + split_positions + [len(enumerate_content)]
        
        for i in range(len(split_positions) - 1):
            start = split_positions[i]
            end = split_positions[i + 1]
            section = enumerate_content[start:end].strip()
            
            if section:
                exercise_part, solution_part = self._separate_exercise_solution(section)
                if exercise_part:
                    exercises.append((exercise_part, solution_part))
        
        return exercises
    
    def _extract_solution_content(self, ifanswers_block: str) -> str:
        """Extrae contenido limpio de un bloque \ifanswers"""
        # Patrones para extraer solución
        patterns = [
            r'\\ifanswers\s*\{\s*\\color\{red\}\s*\\textbf\{Solución:\}\s*(.*?)\s*\}\s*\\fi',
            r'\\ifanswers\s*\{\s*\\color\{red\}\s*(.*?)\s*\}\s*\\fi',
            r'\\ifanswers\s*\{(.*?)\}\s*\\fi'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, ifanswers_block, re.DOTALL)
            if match:
                solution = match.group(1).strip()
                # Limpiar comandos LaTeX
                solution = re.sub(r'\\textbf\{[^}]*\}', '', solution)
                solution = re.sub(r'\\textit\{[^}]*\}', '', solution)
                solution = re.sub(r'\\color\{[^}]*\}', '', solution)
                return solution.strip()
        
        return ""
    
    def _parse_generic_content_conservative(self, content: str) -> List[ParsedExercise]:
        """Parsing genérico MUY conservador para evitar sobre-división"""
        exercises = []
        
        # Solo buscar secciones claramente marcadas como ejercicios
        section_patterns = [
            r'\\section\*?\{([^}]*[Ee]jercicio[^}]*)\}(.*?)(?=\\section|\Z)',
            r'\\chapter\*?\{([^}]*[Ee]jercicio[^}]*)\}(.*?)(?=\\chapter|\Z)'
        ]
        
        for pattern in section_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for i, (title, content_section) in enumerate(matches):
                if len(content_section.strip()) > 100:  # Solo si tiene contenido sustancial
                    exercise = ParsedExercise(
                        titulo=f"Ejercicio de sección: {title}",
                        enunciado=self._clean_latex_text(content_section),
                        pattern_used="generic_conservative",
                        confidence_score=0.4
                    )
                    exercises.append(exercise)
        
        return exercises
    
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
    
    def _extract_content_parts(self, content: str) -> tuple[str, Optional[str]]:
        """Extrae enunciado y solución de un bloque de contenido"""
        # Buscar solución en environments específicos
        solution_patterns = [
            r'\\begin\{solucion\}(.*?)\\end\{solucion\}',
            r'\\begin\{solution\}(.*?)\\end\{solution\}',
            r'\\begin\{respuesta\}(.*?)\\end\{respuesta\}',
            r'\\ifanswers\s*\{.*?\}\s*\\fi'
        ]
        
        solucion = None
        enunciado = content
        
        for pattern in solution_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                if pattern.startswith(r'\\ifanswers'):
                    # Para ifanswers, extraer contenido interno
                    solucion = self._extract_solution_content(match.group(0))
                else:
                    solucion = match.group(1).strip()
                
                enunciado = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
                break
        
        # Limpiar enunciado
        enunciado = self._clean_latex_text(enunciado)
        if solucion:
            solucion = self._clean_latex_text(solucion)
        
        return enunciado.strip(), solucion
    
    def _extract_metadata_from_comments(self, content: str) -> Dict:
        """Extrae metadatos de comentarios LaTeX"""
        metadata = {}
        
        # Patrones para extraer metadatos
        patterns = {
            'nivel_dificultad': r'%.*?dificultad[:\s]*([^\n]+)',
            'unidad_tematica': r'%.*?unidad[:\s]*([^\n]+)',
            'tiempo_estimado': r'%.*?tiempo[:\s]*(\d+)',
            'modalidad': r'%.*?modalidad[:\s]*([^\n]+)',
            'subtemas': r'%.*?subtemas?[:\s]*([^\n]+)',
            'palabras_clave': r'%.*?(?:palabras?[:\s]*clave|keywords?)[:\s]*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if key in ['subtemas', 'palabras_clave']:
                    metadata[key] = [item.strip() for item in value.split(',')]
                elif key == 'tiempo_estimado':
                    metadata[key] = int(value)
                else:
                    metadata[key] = value.title()
        
        return metadata
    
    def _enrich_exercise_metadata(self, exercise: ParsedExercise) -> ParsedExercise:
        """Enriquece automáticamente los metadatos del ejercicio"""
        # Auto-detectar unidad temática si no está definida
        if exercise.unidad_tematica == "Por determinar":
            exercise.unidad_tematica = self._detect_unit(exercise.enunciado)
        
        # Auto-detectar dificultad si no está definida
        if exercise.nivel_dificultad == "Intermedio" and not hasattr(exercise, '_difficulty_set'):
            exercise.nivel_dificultad = self._detect_difficulty(exercise.enunciado)
        
        # Extraer palabras clave automáticamente
        if not exercise.palabras_clave:
            exercise.palabras_clave = self._extract_keywords(exercise.enunciado)
        
        # Estimar tiempo si no está definido
        if exercise.tiempo_estimado == 20:
            exercise.tiempo_estimado = self._estimate_time(exercise.enunciado, exercise.nivel_dificultad)
        
        return exercise
    
    def _detect_unit(self, text: str) -> str:
        """Detecta automáticamente la unidad temática"""
        text_lower = text.lower()
        unit_scores = {}
        
        for unit, keywords in self.unidad_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                unit_scores[unit] = score
        
        if unit_scores:
            return max(unit_scores, key=unit_scores.get)
        return "Por determinar"
    
    def _detect_difficulty(self, text: str) -> str:
        """Detecta automáticamente el nivel de dificultad"""
        text_lower = text.lower()
        difficulty_scores = {}
        
        for difficulty, keywords in self.difficulty_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                difficulty_scores[difficulty] = score
        
        # También considerar longitud y complejidad
        word_count = len(text.split())
        if word_count > 200:
            difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 1
        elif word_count < 50:
            difficulty_scores["Básico"] = difficulty_scores.get("Básico", 0) + 1
        
        if difficulty_scores:
            return max(difficulty_scores, key=difficulty_scores.get)
        return "Intermedio"
    
    def _detect_modality(self, text: str) -> str:
        """Detecta modalidad basado en contenido"""
        text_lower = text.lower()
        
        computational_keywords = ['python', 'código', 'implemente', 'programe', 'compute']
        
        if any(word in text_lower for word in computational_keywords):
            return 'Computacional'
        elif 'grafique' in text_lower:
            return 'Mixto'
        else:
            return 'Teórico'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave automáticamente"""
        keywords = []
        text_lower = text.lower()
        
        # Keywords técnicos específicos de SyS
        technical_terms = [
            'convolución', 'fourier', 'laplace', 'transformada', 'señal', 'sistema',
            'frecuencia', 'impulso', 'filtro', 'estabilidad', 'lineal', 'invariante',
            'muestreo', 'discreto', 'continuo', 'dft', 'fft', 'polo', 'cero'
        ]
        
        for term in technical_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords[:5]  # Limitar a 5 keywords
    
    def _estimate_time(self, text: str, difficulty: str) -> int:
        """Estima tiempo de resolución basado en contenido y dificultad"""
        word_count = len(text.split())
        
        base_time = {
            "Básico": 10,
            "Intermedio": 20,
            "Avanzado": 35,
            "Desafío": 50
        }.get(difficulty, 20)
        
        # Ajustar por longitud
        if word_count > 150:
            base_time += 10
        elif word_count > 100:
            base_time += 5
        
        # Ajustar por complejidad (presencia de fórmulas, etc.)
        if any(term in text.lower() for term in ['derive', 'demuestre', 'pruebe']):
            base_time += 15
        
        return min(base_time, 60)  # Máximo 60 minutos
    
    def _clean_latex_text(self, text: str) -> str:
        """Limpia comandos LaTeX del texto"""
        # Remover comandos LaTeX comunes pero mantener contenido matemático
        text = re.sub(r'\\item\s*', '', text)
        text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)
        
        # Limpiar espacios extra
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

class ParseError(Exception):
    """Excepción personalizada para errores de parsing"""
    pass

# Funciones de utilidad para integración con Streamlit
def create_parser_interface():
    """Crea una instancia del parser para usar en Streamlit"""
    return LaTeXParser()

def display_parsed_exercises(exercises: List[ParsedExercise]) -> None:
    """Muestra ejercicios parseados en Streamlit (se implementará en app.py)"""
    pass

def import_exercises_to_db(exercises: List[ParsedExercise], db_manager) -> bool:
    """Importa ejercicios a la base de datos (requiere db_manager implementado)"""
    pass