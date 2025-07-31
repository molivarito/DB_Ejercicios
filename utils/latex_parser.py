"""
Parser LaTeX para importación de ejercicios - VERSIÓN 4.0 CORREGIDA Y FUNCIONAL
"""

import re
import logging
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
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
    tipo_ejercicio: str = "Cálculo"
    subtemas: List[str] = None
    palabras_clave: List[str] = None
    tipo_actividad: List[str] = None
    comentarios: str = ""
    pattern_used: str = ""
    confidence_score: float = 0.0
    image_filename: Optional[str] = None
    solucion_image_filename: Optional[str] = None
    
    def __post_init__(self):
        if self.subtemas is None: self.subtemas = []
        if self.palabras_clave is None: self.palabras_clave = []
        if self.tipo_actividad is None: self.tipo_actividad = ["Ayudantía"]

class LaTeXParser:
    """Parser principal para archivos LaTeX de ejercicios - V4.0 CORREGIDA"""
    
    def __init__(self):
        # Mapeo de unidades temáticas (tu lógica original, sin cambios)
        self.unidad_keywords = {
            "Números Complejos": ["complejo", "euler", "polar", "cartesian", "módulo", "fase", "conjugado", "mathbb{c}"],
            "Señales y Sistemas": ["señal", "sistema", "entrada", "salida", "causal", "estable", "memoria", "lineal", "invariante"],
            "Gráficos": ["grafique", "trace", "plot", "sketch", "bosquejo", "gráfico"],
            "Simetrías": ["par", "impar", "simetría", "even", "odd", "paridad"],
            "Funciones Importantes": ["escalón", "impulso", "rampa", "rect", "sinc", "delta", "sqcap", "wedge"],
            "Impulso": ["impulso", "delta", "dirac", "cedazo", "muestreo"],
            "Sistemas Continuos": ["convolución", "impulso", "lineal", "invariante", "continuo", "ecuación diferencial"],
            "Sistemas Lineales y Convolución": ["lti", "convolución", "respuesta impulso", "lineal", "sistema lineal"],
            "Respuesta al Impulso": ["respuesta impulso", "impulso", "respuesta", "sistema lti", "convolución"],
            "Transformada de Fourier": ["fourier", "serie", "frecuencia", "espectro", "transformada ft"],
            "Transformada de Laplace": ["laplace", "transformada lt", "polo", "cero", "convergencia"],
            "Sistemas Discretos": ["discreto", "muestreo", "digital", "convertidor", "teorema muestreo"],
            "Transformada de Fourier Discreta": ["dft", "fft", "transformada discreta", "aliasing"],
            "Transformada Z": ["transformada z", "plano z", "estabilidad", "región convergencia"]
        }
        # Detección de tipos de ejercicio (tu lógica original, sin cambios)
        self.exercise_types = {
            "Demostración": ["demuestre", "pruebe", "verifique", "compruebe", "justifique", "derive"],
            "Cálculo": ["calcule", "determine", "encuentre", "evalúe", "compute", "obtenga", "halle"],
            "Análisis": ["analice", "compare", "estudie", "examine", "investigue", "explore"],
            "Aplicación": ["grafique", "trace", "plot", "implemente", "diseñe", "construya"],
            "Resolución": ["resuelva", "solucione", "halle", "encuentre la solución"],
            "Identificación": ["identifique", "clasifique", "reconozca", "determine si"]
        }
        # Detección de dificultad (tu lógica original, sin cambios)
        self.difficulty_keywords = {
            "Básico": ["calcule", "determine", "grafique", "simple", "directo", "básico"],
            "Intermedio": ["analice", "compare", "demuestre", "implemente", "diseñe", "verifique"],
            "Avanzado": ["optimice", "derive", "investigue", "complejo", "múltiple", "generalice"],
            "Desafío": ["pruebe", "generalice", "creative", "desafío", "investigación"]
        }
        
    def parse_file(self, file_content: str) -> List[ParsedExercise]:
        """Parsea un archivo LaTeX completo - V4.0 CORREGIDA"""
        try:
            logger.info("🚀 Iniciando parsing V4.0 CORREGIDA")
            cleaned_content = self._preprocess_content(file_content)
            exercises = self._parse_patricio_format_v4_fixed(cleaned_content)
            if exercises: logger.info(f"✅ Parser V4.0 encontró {len(exercises)} ejercicios")
            else: logger.warning("⚠️ No se encontraron ejercicios")
            enriched_exercises = [self._enrich_exercise_metadata_v4(ex) for ex in exercises]
            logger.info(f"🎉 Parser V4.0 completado. Total ejercicios: {len(enriched_exercises)}")
            return enriched_exercises
        except Exception as e:
            logger.error(f"❌ Error durante el parsing V4.0: {e}", exc_info=True)
            raise ParseError(f"Error al parsear archivo LaTeX: {str(e)}")
    
    def _parse_patricio_format_v4_fixed(self, content: str) -> List[ParsedExercise]:
        """Parser específico V4.0 CORREGIDA para el formato de guías de Patricio"""
        exercises = []
        subsection_pattern = r'\\subsection\*\{([^}]+)\}(.*?)(?=\\subsection\*|\\section|\\end\{document\}|\Z)'
        subsections = re.findall(subsection_pattern, content, re.DOTALL | re.IGNORECASE)
        logger.info(f"🔍 Encontradas {len(subsections)} subsecciones")
        
        # Usamos un contador global para que los títulos sean únicos en todo el documento
        ejercicio_global_counter = 0

        for subsection_title, subsection_content in subsections:
            logger.info(f"📂 Procesando subsección: '{subsection_title.strip()}'")
            
            # Extraer ejercicios individuales de esta subsección
            # Pasamos el contador global para mantener la numeración
            section_exercises, num_processed = self._extract_individual_items_v4_fixed(
                subsection_content, subsection_title, ejercicio_global_counter
            )
            
            if section_exercises:
                exercises.extend(section_exercises)
                ejercicio_global_counter += num_processed
                logger.info(f"✅ Extraídos {len(section_exercises)} ejercicios de '{subsection_title.strip()}'")
            else:
                logger.warning(f"⚠️ No se encontraron ejercicios en '{subsection_title.strip()}'")
        
        return exercises
    
    def _extract_image_and_clean_content(self, content: str) -> Tuple[str, Optional[str]]:
        """
        Busca un \includegraphics, preferiblemente dentro de un entorno figure/subfigure.
        Extrae el path de la primera imagen y limpia el entorno completo del texto.
        """
        image_filename = None
        
        # Pattern to find a figure environment (non-greedy)
        figure_pattern = r'\\begin\{figure\}.*?\\end\{figure\}'
        figure_match = re.search(figure_pattern, content, re.DOTALL)
        
        if figure_match:
            figure_block = figure_match.group(0)
            # Pattern to find includegraphics inside the figure
            image_pattern = r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}'
            image_match = re.search(image_pattern, figure_block)
            
            if image_match:
                image_filename = image_match.group(1).strip()
                logger.info(f"    -> Imagen encontrada en entorno 'figure': {image_filename}")
            else:
                logger.info("    -> Entorno 'figure' encontrado pero sin \\includegraphics. Se eliminará el bloque.")

            # Remove the entire figure block
            content = content.replace(figure_block, '', 1)

        return content.strip(), image_filename

    def _extract_individual_items_v4_fixed(self, subsection_content: str, subsection_title: str, start_index: int) -> Tuple[List[ParsedExercise], int]:
        """
        Extrae ejercicios individuales de una subsección.
        ESTA ES LA VERSIÓN CORREGIDA Y ROBUSTA.
        """
        exercises = []
        clean_subsection_title = self._normalize_subsection_title(subsection_title)
        unit = self._map_subsection_to_unit_v4_fixed(subsection_title)
        
        # =========================================================================
        # ▼▼▼ CAMBIO DE DISEÑO FUNDAMENTAL Y CORRECTO ▼▼▼
        # 1. Ya NO buscamos \begin{enumerate}...\end{enumerate} con regex.
        # 2. Aplicamos el splitter robusto directamente a todo el contenido de la subsección.
        items = self._split_by_main_level_items_only(subsection_content)
        # =========================================================================
        
        logger.info(f"✅ Encontrados {len(items)} items principales en esta subsección.")
        
        for i, item_content in enumerate(items):
            if item_content.strip():
                # 1. Separar enunciado y solución primero
                enunciado_raw, solucion_raw = self._extract_statement_and_solution_v4_fixed(item_content)
                
                # 2. Extraer imagen del enunciado
                enunciado, image_filename = self._extract_image_and_clean_content(enunciado_raw)
                
                # 3. Extraer imagen de la solución (si existe)
                solucion, solucion_image_filename = (self._extract_image_and_clean_content(solucion_raw) if solucion_raw else (None, None))

                if enunciado.strip():
                    difficulty = self._detect_difficulty_v4_fixed(enunciado)
                    exercise_type = self._detect_exercise_type(enunciado)
                    
                    # Generar título inteligente usando el contador global
                    current_exercise_num = start_index + i + 1
                    titulo = self._generate_smart_title_v4(clean_subsection_title, difficulty, current_exercise_num)
                    
                    exercise = ParsedExercise(
                        titulo=titulo,
                        enunciado=self._clean_latex_text(enunciado),
                        solucion_completa=self._clean_latex_text(solucion) if solucion else None, # Limpiar texto después de extraer imagen
                        unidad_tematica=unit,
                        nivel_dificultad=difficulty,
                        tipo_ejercicio=exercise_type,
                        modalidad=self._detect_modality(enunciado),
                        tiempo_estimado=self._estimate_time_v4_fixed(enunciado, difficulty),
                        pattern_used="patricio_format_v4_fixed_robust",
                        confidence_score=0.98,
                        palabras_clave=self._extract_keywords(enunciado),
                        comentarios=f"Extraído de subsección: {clean_subsection_title}",
                        image_filename=image_filename,
                        solucion_image_filename=solucion_image_filename
                    )
                    exercises.append(exercise)
                    logger.info(f"    -> Ejercicio creado: {titulo}")
        
        return exercises, len(items)

    # El resto de tus funciones originales se mantienen intactas.
    # Esta es tu lógica robusta y funciona perfectamente.
    def _split_by_main_level_items_only(self, enumerate_content: str) -> List[str]:
        logger.info("🔧 Iniciando división por items del nivel principal únicamente")
        nested_ranges = self._find_nested_blocks_ranges(enumerate_content)
        all_item_positions = [(m.start(), m.end()) for m in re.finditer(r'\\item\s+', enumerate_content)]
        main_level_items = []
        for item_start, item_end in all_item_positions:
            is_nested = any(nested_start <= item_start < nested_end for nested_start, nested_end in nested_ranges)
            if not is_nested:
                main_level_items.append((item_start, item_end))
        items = []
        for i in range(len(main_level_items)):
            start_pos, content_start = main_level_items[i]
            end_pos = main_level_items[i + 1][0] if i + 1 < len(main_level_items) else len(enumerate_content)
            item_content = enumerate_content[content_start:end_pos].strip()
            if item_content:
                items.append(item_content)
        return items

    def _find_nested_blocks_ranges(self, content: str) -> List[Tuple[int, int]]:
        nested_ranges = []
        stack = []
        pattern = r'\\(begin|end)\{(enumerate|itemize|align|equation|figure|table)\}'
        commands = sorted([(m.start(), m.end(), m.group(1), m.group(2)) for m in re.finditer(pattern, content)], key=lambda x: x[0])
        for start_pos, end_pos, cmd_type, env_type in commands:
            if cmd_type == 'begin':
                stack.append((start_pos, env_type))
            elif cmd_type == 'end' and stack:
                for i in range(len(stack) - 1, -1, -1):
                    begin_pos, begin_env = stack[i]
                    if begin_env == env_type:
                        if i > 0:
                            nested_ranges.append((begin_pos, end_pos))
                        stack.pop(i)
                        break
        return nested_ranges

    def _extract_statement_and_solution_v4_fixed(self, item_content: str) -> Tuple[str, Optional[str]]:
        # A more robust pattern that just captures the content of the \ifanswers block.
        solution_pattern = r'\\ifanswers\s*\{(.*?)(?:\}\s*\\fi|\\fi\s*\})'
        solucion = None
        enunciado = item_content
        
        match = re.search(solution_pattern, item_content, re.DOTALL)
        if match:
            solucion_raw = match.group(1).strip()
            
            # Check for "resuelta en ayudantía" and similar phrases
            skip_phrases = ['resuelta en ayudantía', 'ver ayudantía', 'en clases']
            if any(phrase in solucion_raw.lower() for phrase in skip_phrases):
                solucion = None
            else:
                # Clean known headers from the raw solution text
                headers_to_clean = [
                    r'^\s*\\color\{red\}\s*\\textbf\{Solución:\s*\}',
                    r'^\s*\\color\{red\}\s*',
                    r'^\s*\\textbf\{Solución:\s*\}',
                    r'^\s*Solución:\s*'
                ]
                cleaned_solucion = solucion_raw
                for header_pattern in headers_to_clean:
                    # Use re.sub with count=1 to only remove the header at the start
                    cleaned_solucion = re.sub(header_pattern, '', cleaned_solucion, count=1, flags=re.IGNORECASE).strip()
                
                solucion = cleaned_solucion
            
            # Remove the entire \ifanswers block from the enunciado
            enunciado = item_content.replace(match.group(0), '', 1).strip()
            
        return enunciado, solucion

    def _detect_difficulty_v4_fixed(self, content: str) -> str:
        content_lower = content.lower(); difficulty_scores = {}
        for difficulty, keywords in self.difficulty_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0: difficulty_scores[difficulty] = score
        substructures = len(re.findall(r'\\begin\{enumerate\}|\\begin\{itemize\}', content))
        if substructures >= 2: difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 2
        elif substructures == 1: difficulty_scores["Intermedio"] = difficulty_scores.get("Intermedio", 0) + 1
        math_density = len(re.findall(r'\$.*?\$|\\\[.*?\\\]|\\[a-zA-Z]+\{', content))
        if math_density > 8: difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 1
        elif math_density > 4: difficulty_scores["Intermedio"] = difficulty_scores.get("Intermedio", 0) + 1
        word_count = len(content.split())
        if word_count > 200: difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 1
        elif word_count < 50: difficulty_scores["Básico"] = difficulty_scores.get("Básico", 0) + 1
        complex_indicators = ['demuestre', 'pruebe', 'derive', 'generalice', 'investigue']
        if any(indicator in content_lower for indicator in complex_indicators):
            difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 2
        if difficulty_scores: return max(difficulty_scores, key=difficulty_scores.get)
        return "Intermedio"

    def _estimate_time_v4_fixed(self, content: str, difficulty: str) -> int:
        base_times = {"Básico": 10, "Intermedio": 18, "Avanzado": 30, "Desafío": 45}
        base_time = base_times.get(difficulty, 18); adjustments = 0
        substructures = len(re.findall(r'\\begin\{enumerate\}|\\begin\{itemize\}', content)); adjustments += substructures * 5
        math_elements = len(re.findall(r'\$.*?\$|\\\[.*?\\\]', content)); adjustments += min(math_elements * 2, 15)
        word_count = len(content.split())
        if word_count > 150: adjustments += 10
        elif word_count > 100: adjustments += 5
        if any(word in content.lower() for word in ['demuestre', 'pruebe', 'derive']): adjustments += 12
        elif any(word in content.lower() for word in ['grafique', 'trace', 'plot']): adjustments += 8
        total_time = base_time + adjustments
        return min(max(total_time, 5), 60)

    def _map_subsection_to_unit_v4_fixed(self, subsection_title: str) -> str:
        title_lower = subsection_title.lower().strip()
        direct_mapping = {
            'números complejos': 'Números Complejos', 'señales y sistemas': 'Señales y Sistemas', 'gráficos': 'Gráficos',
            'simetrías y funciones importantes': 'Simetrías', 'simetrías': 'Simetrías', 'funciones importantes': 'Funciones Importantes',
            'impulso': 'Impulso', 'sistemas lineales y convolución': 'Sistemas Lineales y Convolución',
            'convolución': 'Sistemas Lineales y Convolución', 'respuesta al impulso': 'Respuesta al Impulso'
        }
        for key, unit in direct_mapping.items():
            if key in title_lower: return unit
        for unit, keywords in self.unidad_keywords.items():
            for keyword in keywords:
                if keyword in title_lower: return unit
        return 'Por determinar'

    def _generate_smart_title_v4(self, subsection_title: str, difficulty: str, number: int) -> str:
        tema_clean = re.sub(r'[^\w\s]', '', subsection_title); tema_clean = re.sub(r'\s+', '_', tema_clean.strip())
        return f"{tema_clean}-{difficulty}-{number:02d}"

    def _normalize_subsection_title(self, title: str) -> str: return re.sub(r'[{}\\]', '', title).strip()

    def _detect_exercise_type(self, content: str) -> str:
        content_lower = content.lower(); type_scores = {}
        for exercise_type, keywords in self.exercise_types.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0: type_scores[exercise_type] = score
        if type_scores: return max(type_scores, key=type_scores.get)
        return "Cálculo"

    def _detect_modality(self, text: str) -> str:
        text_lower = text.lower()
        if any(word in text_lower for word in ['python', 'código', 'implemente']): return 'Computacional'
        if any(word in text_lower for word in ['grafique', 'trace', 'plot']): return 'Mixto'
        return 'Teórico'
    
    def _extract_keywords(self, text: str) -> List[str]:
        technical_terms = ['convolución', 'fourier', 'laplace', 'transformada', 'señal', 'sistema', 'impulso', 'lineal']
        return [term for term in technical_terms if term in text.lower()][:6]
    
    def _clean_latex_text(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text); text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text); text = re.sub(r'\\color\{[^}]+\}', '', text)
        text = re.sub(r'\n\s*\n\s*\n+', r'\n\n', text); text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def _preprocess_content(self, content: str) -> str:
        return '\n'.join([line.split('%')[0] if '%' in line and not line.strip().startswith('\\') else line for line in content.split('\n')])

    def _enrich_exercise_metadata_v4(self, exercise: ParsedExercise) -> ParsedExercise:
        if not exercise.palabras_clave: exercise.palabras_clave = self._extract_keywords(exercise.enunciado)
        if exercise.tipo_ejercicio == "Demostración": exercise.tipo_actividad = ["Teórica", "Análisis"]
        elif exercise.tipo_ejercicio == "Aplicación": exercise.tipo_actividad = ["Práctica", "Aplicación"]
        if exercise.unidad_tematica == "Números Complejos": exercise.subtemas = ["Forma polar", "Operaciones", "Euler"]
        elif exercise.unidad_tematica == "Sistemas Lineales y Convolución": exercise.subtemas = ["LTI", "Convolución", "Respuesta impulso"]
        return exercise

class ParseError(Exception): pass