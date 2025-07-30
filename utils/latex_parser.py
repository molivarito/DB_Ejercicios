"""
Parser LaTeX para importación de ejercicios - VERSIÓN 4.0 CORREGIDA
Sistema de Gestión de Ejercicios - Señales y Sistemas
Patricio de la Cuadra - PUC Chile

CORRECCIONES V4.0:
- Análisis preciso de estructura anidada con stack
- Cada \item del nivel principal = UN ejercicio completo
- Preserva sub-estructuras (enumerate, itemize) internas
- Extracción correcta de soluciones \ifanswers
- Títulos inteligentes tema-dificultad-numero
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
    
    def __post_init__(self):
        if self.subtemas is None:
            self.subtemas = []
        if self.palabras_clave is None:
            self.palabras_clave = []
        if self.tipo_actividad is None:
            self.tipo_actividad = ["Ayudantía"]

class LaTeXParser:
    """Parser principal para archivos LaTeX de ejercicios - V4.0 CORREGIDA"""
    
    def __init__(self):
        # Mapeo de unidades temáticas específico para el formato Patricio
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
        
        # Detección de tipos de ejercicio
        self.exercise_types = {
            "Demostración": ["demuestre", "pruebe", "verifique", "compruebe", "justifique", "derive"],
            "Cálculo": ["calcule", "determine", "encuentre", "evalúe", "compute", "obtenga", "halle"],
            "Análisis": ["analice", "compare", "estudie", "examine", "investigue", "explore"],
            "Aplicación": ["grafique", "trace", "plot", "implemente", "diseñe", "construya"],
            "Resolución": ["resuelva", "solucione", "halle", "encuentre la solución"],
            "Identificación": ["identifique", "clasifique", "reconozca", "determine si"]
        }
        
        # Detección de dificultad
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
            exercises = []
            
            # Limpiar y preprocessar el contenido
            cleaned_content = self._preprocess_content(file_content)
            
            # Parser específico para formato Patricio
            exercises = self._parse_patricio_format_v4_fixed(cleaned_content)
            
            if exercises:
                logger.info(f"✅ Parser V4.0 encontró {len(exercises)} ejercicios")
            else:
                logger.warning("⚠️ No se encontraron ejercicios")
            
            # Post-procesar y enriquecer ejercicios
            enriched_exercises = []
            for exercise in exercises:
                enriched = self._enrich_exercise_metadata_v4(exercise)
                enriched_exercises.append(enriched)
            
            logger.info(f"🎉 Parser V4.0 completado. Total ejercicios: {len(enriched_exercises)}")
            return enriched_exercises
            
        except Exception as e:
            logger.error(f"❌ Error durante el parsing V4.0: {str(e)}")
            raise ParseError(f"Error al parsear archivo LaTeX: {str(e)}")
    
    def _parse_patricio_format_v4_fixed(self, content: str) -> List[ParsedExercise]:
        """
        Parser específico V4.0 CORREGIDA para el formato de guías de Patricio
        - Cada \item del nivel principal es UN ejercicio completo
        - Preserva completamente la estructura interna
        """
        exercises = []
        
        # Buscar subsecciones que contengan ejercicios
        subsection_pattern = r'\\subsection\*\{([^}]+)\}(.*?)(?=\\subsection\*|\\section|\\end\{document\}|\Z)'
        subsections = re.findall(subsection_pattern, content, re.DOTALL | re.IGNORECASE)
        
        logger.info(f"🔍 Encontradas {len(subsections)} subsecciones")
        
        for subsection_title, subsection_content in subsections:
            logger.info(f"📂 Procesando subsección: '{subsection_title}'")
            
            # Normalizar título y mapear unidad
            clean_subsection = self._normalize_subsection_title(subsection_title)
            unit = self._map_subsection_to_unit_v4_fixed(subsection_title)
            
            # Extraer ejercicios individuales de esta subsección
            section_exercises = self._extract_individual_items_v4_fixed(subsection_content, clean_subsection, unit)
            
            if section_exercises:
                exercises.extend(section_exercises)
                logger.info(f"✅ Extraídos {len(section_exercises)} ejercicios de '{subsection_title}'")
            else:
                logger.warning(f"⚠️ No se encontraron ejercicios en '{subsection_title}'")
        
        return exercises
    
    def _extract_individual_items_v4_fixed(self, subsection_content: str, subsection_title: str, unit: str) -> List[ParsedExercise]:
        """
        Extrae ejercicios individuales de una subsección - VERSIÓN CORREGIDA
        Cada \item del nivel principal es tratado como UN ejercicio completo
        """
        exercises = []
        
        # Buscar bloques enumerate en la subsección
        enumerate_pattern = r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}'
        enumerate_matches = re.findall(enumerate_pattern, subsection_content, re.DOTALL)
        
        logger.info(f"🔍 Encontrados {len(enumerate_matches)} bloques enumerate en '{subsection_title}'")
        
        for enum_idx, enumerate_content in enumerate_matches:
            logger.info(f"📋 Procesando bloque enumerate {enum_idx + 1}")
            
            # 🚀 MÉTODO CORREGIDO: Dividir solo por \item del nivel principal
            items = self._split_by_main_level_items_only(enumerate_content)
            
            logger.info(f"✅ Encontrados {len(items)} items principales en bloque enumerate")
            
            for i, item_content in enumerate(items):
                if item_content.strip():
                    # Extraer enunciado y solución
                    enunciado, solucion = self._extract_statement_and_solution_v4_fixed(item_content)
                    
                    if enunciado.strip():  # Solo si hay contenido válido
                        # Detectar metadatos del ejercicio
                        difficulty = self._detect_difficulty_v4_fixed(enunciado)
                        exercise_type = self._detect_exercise_type(enunciado)
                        
                        # Generar título inteligente
                        titulo = self._generate_smart_title_v4(subsection_title, difficulty, i + 1)
                        
                        exercise = ParsedExercise(
                            titulo=titulo,
                            enunciado=self._clean_latex_text(enunciado),
                            solucion_completa=self._clean_latex_text(solucion) if solucion else None,
                            unidad_tematica=unit,
                            nivel_dificultad=difficulty,
                            tipo_ejercicio=exercise_type,
                            modalidad=self._detect_modality(enunciado),
                            tiempo_estimado=self._estimate_time_v4_fixed(enunciado, difficulty),
                            pattern_used="patricio_format_v4_fixed",
                            confidence_score=0.95,
                            palabras_clave=self._extract_keywords(enunciado),
                            comentarios=f"Extraído de subsección: {subsection_title}"
                        )
                        exercises.append(exercise)
                        logger.info(f"✅ Ejercicio creado: {titulo}")
        
        return exercises
    
    def _split_by_main_level_items_only(self, enumerate_content: str) -> List[str]:
        """
        🎯 MÉTODO CLAVE CORREGIDO: 
        Divide contenido SOLO por \item del nivel principal
        Usa análisis de stack para detectar bloques anidados exactamente
        """
        logger.info("🔧 Iniciando división por items del nivel principal únicamente")
        
        # 1. PASO 1: Encontrar todos los rangos de bloques anidados
        nested_ranges = self._find_nested_blocks_ranges(enumerate_content)
        logger.info(f"📊 Encontrados {len(nested_ranges)} bloques anidados")
        
        # 2. PASO 2: Encontrar todas las posiciones de \item
        all_item_positions = []
        for match in re.finditer(r'\\item\s+', enumerate_content):
            all_item_positions.append((match.start(), match.end()))
        
        logger.info(f"📋 Encontradas {len(all_item_positions)} posiciones de \\item en total")
        
        # 3. PASO 3: Filtrar solo los \item que NO están dentro de bloques anidados
        main_level_items = []
        for item_start, item_end in all_item_positions:
            is_nested = False
            for nested_start, nested_end in nested_ranges:
                if nested_start <= item_start <= nested_end:
                    is_nested = True
                    break
            
            if not is_nested:
                main_level_items.append((item_start, item_end))
        
        logger.info(f"✅ Filtrados {len(main_level_items)} \\item del nivel principal")
        
        # 4. PASO 4: Extraer contenido de cada item principal
        items = []
        for i in range(len(main_level_items)):
            start_pos, content_start = main_level_items[i]
            
            # Determinar dónde termina este item
            if i + 1 < len(main_level_items):
                end_pos = main_level_items[i + 1][0]
            else:
                end_pos = len(enumerate_content)
            
            # Extraer contenido del item (desde después de \item hasta el siguiente \item o final)
            item_content = enumerate_content[content_start:end_pos].strip()
            
            if item_content:
                items.append(item_content)
                logger.info(f"📝 Item {i+1}: {len(item_content)} caracteres")
        
        return items
    
    def _find_nested_blocks_ranges(self, content: str) -> List[Tuple[int, int]]:
        """
        🔍 Encuentra rangos exactos de bloques anidados usando análisis de stack
        Detecta \begin{enumerate}, \begin{itemize}, etc. y sus \end correspondientes
        """
        nested_ranges = []
        
        # Patrones para detectar bloques anidados
        begin_pattern = r'\\begin\{(enumerate|itemize|align|equation|figure|table)\}'
        end_pattern = r'\\end\{(enumerate|itemize|align|equation|figure|table)\}'
        
        # Encontrar todos los comandos begin/end
        all_commands = []
        
        for match in re.finditer(begin_pattern, content):
            all_commands.append((match.start(), match.end(), 'begin', match.group(1)))
        
        for match in re.finditer(end_pattern, content):
            all_commands.append((match.start(), match.end(), 'end', match.group(1)))
        
        # Ordenar por posición
        all_commands.sort(key=lambda x: x[0])
        
        # Usar stack para hacer match de begin/end correctamente
        stack = []
        
        for start_pos, end_pos, cmd_type, env_type in all_commands:
            if cmd_type == 'begin':
                stack.append((start_pos, env_type))
            elif cmd_type == 'end' and stack:
                # Buscar el \begin correspondiente más reciente del mismo tipo
                for i in range(len(stack) - 1, -1, -1):
                    begin_pos, begin_env = stack[i]
                    if begin_env == env_type:
                        # Este bloque está anidado si hay otros bloques abiertos antes
                        if i > 0:  # No es el primer bloque abierto
                            nested_ranges.append((begin_pos, end_pos))
                        stack.pop(i)
                        break
        
        logger.info(f"🎯 Bloques anidados detectados: {len(nested_ranges)} rangos")
        for i, (start, end) in enumerate(nested_ranges):
            block_content = content[start:end][:50] + "..." if len(content[start:end]) > 50 else content[start:end]
            logger.info(f"   Bloque {i+1}: pos {start}-{end}, contenido: {block_content}")
        
        return nested_ranges
    
    def _extract_statement_and_solution_v4_fixed(self, item_content: str) -> Tuple[str, Optional[str]]:
        """
        Extrae enunciado y solución de un item individual - VERSIÓN CORREGIDA
        Maneja correctamente los patrones \ifanswers del formato Patricio
        """
        
        # Patrones específicos para las soluciones del formato Patricio
        solution_patterns = [
            # Patrón principal: \ifanswers {\color{red} \textbf{Solución:} ...} \fi
            r'\\ifanswers\s*\{\s*\\color\{red\}\s*\\textbf\{Solución:\}(.*?)\}\s*\\fi',
            # Patrón alternativo: \ifanswers {\color{red}\textbf{Solución:} ...} \fi (sin espacios)
            r'\\ifanswers\s*\{\s*\\color\{red\}\\textbf\{Solución:\}(.*?)\}\s*\\fi',
            # Patrón más genérico: \ifanswers {\color{red} ...} \fi
            r'\\ifanswers\s*\{\s*\\color\{red\}\s*(.*?)\}\s*\\fi',
            # Patrón sin color: \ifanswers {...} \fi
            r'\\ifanswers\s*\{(.*?)\}\s*\\fi'
        ]
        
        solucion = None
        enunciado = item_content
        
        for pattern in solution_patterns:
            match = re.search(pattern, item_content, re.DOTALL)
            if match:
                solucion_raw = match.group(1).strip()
                
                # Verificar si es una solución real o solo una referencia
                if solucion_raw:
                    # Excluir referencias que no son soluciones reales
                    skip_phrases = [
                        'resuelta en ayudantía', 
                        'ver ayudantía', 
                        'en clases',
                        'resuelta en clase',
                        'ver solución en ayudantía'
                    ]
                    
                    if any(phrase in solucion_raw.lower() for phrase in skip_phrases):
                        solucion = None  # Marcar como sin solución real
                        logger.info("ℹ️ Solución es solo referencia, marcando como sin solución")
                    else:
                        solucion = solucion_raw
                        logger.info("✅ Solución real encontrada")
                
                # Remover toda la sección \ifanswers del enunciado
                enunciado = re.sub(pattern, '', item_content, flags=re.DOTALL).strip()
                break
        
        return enunciado, solucion
    
    def _detect_difficulty_v4_fixed(self, content: str) -> str:
        """Detecta dificultad con lógica mejorada y específica para el formato"""
        content_lower = content.lower()
        difficulty_scores = {}
        
        # Análisis por palabras clave específicas
        for difficulty, keywords in self.difficulty_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                difficulty_scores[difficulty] = score
        
        # Análisis de complejidad estructural
        # Múltiples sub-partes (enumerate, itemize dentro del ejercicio)
        substructures = len(re.findall(r'\\begin\{enumerate\}|\\begin\{itemize\}', content))
        if substructures >= 2:
            difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 2
        elif substructures == 1:
            difficulty_scores["Intermedio"] = difficulty_scores.get("Intermedio", 0) + 1
        
        # Contenido matemático denso
        math_density = len(re.findall(r'\$.*?\$|\\\[.*?\\\]|\\[a-zA-Z]+\{', content))
        if math_density > 8:
            difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 1
        elif math_density > 4:
            difficulty_scores["Intermedio"] = difficulty_scores.get("Intermedio", 0) + 1
        
        # Longitud del contenido
        word_count = len(content.split())
        if word_count > 200:
            difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 1
        elif word_count < 50:
            difficulty_scores["Básico"] = difficulty_scores.get("Básico", 0) + 1
        
        # Palabras clave específicas de alta complejidad
        complex_indicators = ['demuestre', 'pruebe', 'derive', 'generalice', 'investigue']
        if any(indicator in content_lower for indicator in complex_indicators):
            difficulty_scores["Avanzado"] = difficulty_scores.get("Avanzado", 0) + 2
        
        # Retornar la dificultad con mayor puntuación
        if difficulty_scores:
            detected = max(difficulty_scores, key=difficulty_scores.get)
            logger.info(f"🎯 Dificultad detectada: {detected} (scores: {difficulty_scores})")
            return detected
        
        return "Intermedio"  # Default
    
    def _estimate_time_v4_fixed(self, content: str, difficulty: str) -> int:
        """Estima tiempo basado en complejidad real del ejercicio"""
        
        # Base por dificultad
        base_times = {
            "Básico": 10,
            "Intermedio": 18,
            "Avanzado": 30,
            "Desafío": 45
        }
        base_time = base_times.get(difficulty, 18)
        
        # Ajustes por características específicas
        adjustments = 0
        
        # Sub-estructuras (enumerate/itemize anidados)
        substructures = len(re.findall(r'\\begin\{enumerate\}|\\begin\{itemize\}', content))
        adjustments += substructures * 5
        
        # Densidad matemática
        math_elements = len(re.findall(r'\$.*?\$|\\\[.*?\\\]', content))
        adjustments += min(math_elements * 2, 15)  # Máximo 15 min por matemáticas
        
        # Longitud del texto
        word_count = len(content.split())
        if word_count > 150:
            adjustments += 10
        elif word_count > 100:
            adjustments += 5
        
        # Tipo de ejercicio
        if any(word in content.lower() for word in ['demuestre', 'pruebe', 'derive']):
            adjustments += 12
        elif any(word in content.lower() for word in ['grafique', 'trace', 'plot']):
            adjustments += 8
        
        total_time = base_time + adjustments
        return min(max(total_time, 5), 60)  # Entre 5 y 60 minutos
    
    def _map_subsection_to_unit_v4_fixed(self, subsection_title: str) -> str:
        """Mapea títulos de subsección a unidades temáticas - mejorado para formato Patricio"""
        title_lower = subsection_title.lower().strip()
        
        # Mapeo directo específico para las subsecciones del archivo
        direct_mapping = {
            'números complejos': 'Números Complejos',
            'señales y sistemas': 'Señales y Sistemas', 
            'gráficos': 'Gráficos',
            'simetrías y funciones importantes': 'Simetrías',
            'simetrías': 'Simetrías',
            'funciones importantes': 'Funciones Importantes',
            'impulso': 'Impulso',
            'sistemas lineales y convolución': 'Sistemas Lineales y Convolución',
            'convolución': 'Sistemas Lineales y Convolución',
            'respuesta al impulso': 'Respuesta al Impulso'
        }
        
        # Buscar coincidencia directa primero
        for key, unit in direct_mapping.items():
            if key in title_lower:
                logger.info(f"🎯 Mapeo directo: '{subsection_title}' → '{unit}'")
                return unit
        
        # Si no hay coincidencia directa, buscar por palabras clave
        for unit, keywords in self.unidad_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    logger.info(f"🔍 Mapeo por keyword: '{subsection_title}' → '{unit}' (keyword: '{keyword}')")
                    return unit
        
        logger.warning(f"⚠️ No se pudo mapear subsección: '{subsection_title}', usando 'Por determinar'")
        return 'Por determinar'
    
    def _generate_smart_title_v4(self, subsection_title: str, difficulty: str, number: int) -> str:
        """Genera título inteligente con formato tema-dificultad-numero"""
        # Normalizar tema (remover caracteres especiales)
        tema_clean = re.sub(r'[^\w\s]', '', subsection_title)
        tema_clean = re.sub(r'\s+', '_', tema_clean.strip())
        
        # Formatear número con ceros
        numero_formatted = f"{number:02d}"
        
        # Construir título
        titulo = f"{tema_clean}-{difficulty}-{numero_formatted}"
        
        return titulo
    
    def _normalize_subsection_title(self, title: str) -> str:
        """Normaliza títulos de subsección"""
        clean = re.sub(r'[{}\\]', '', title)
        return clean.strip()
    
    def _detect_exercise_type(self, content: str) -> str:
        """Detecta el tipo de ejercicio basado on palabras clave"""
        content_lower = content.lower()
        type_scores = {}
        
        for exercise_type, keywords in self.exercise_types.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                type_scores[exercise_type] = score
        
        if type_scores:
            return max(type_scores, key=type_scores.get)
        return "Cálculo"  # Default
    
    def _detect_modality(self, text: str) -> str:
        """Detecta modalidad basado en contenido"""
        text_lower = text.lower()
        
        computational_keywords = ['python', 'código', 'implemente', 'programe', 'compute', 'matlab']
        graphic_keywords = ['grafique', 'trace', 'plot', 'sketch', 'bosquejo']
        
        if any(word in text_lower for word in computational_keywords):
            return 'Computacional'
        elif any(word in text_lower for word in graphic_keywords):
            return 'Mixto'
        else:
            return 'Teórico'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave técnicas automáticamente"""
        keywords = []
        text_lower = text.lower()
        
        # Términos técnicos específicos de Señales y Sistemas
        technical_terms = [
            'convolución', 'fourier', 'laplace', 'transformada', 'señal', 'sistema',
            'frecuencia', 'impulso', 'filtro', 'estabilidad', 'lineal', 'invariante',
            'muestreo', 'discreto', 'continuo', 'dft', 'fft', 'polo', 'cero',
            'complejo', 'euler', 'polar', 'escalón', 'rampa', 'rect', 'sinc',
            'delta', 'dirac', 'causal', 'estable', 'memoria'
        ]
        
        for term in technical_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords[:6]  # Máximo 6 keywords
    
    def _clean_latex_text(self, text: str) -> str:
        """Limpia comandos LaTeX del texto preservando estructura matemática"""
        if not text:
            return ""
        
        # Remover comandos de formato pero preservar contenido
        text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\color\{[^}]+\}', '', text)
        
        # Limpiar espacios extra pero preservar estructura
        text = re.sub(r'\n\s*\n\s*\n+', r'\n\n', text)  # Máximo 2 líneas vacías consecutivas
        text = re.sub(r'[ \t]+', ' ', text)  # Espacios múltiples a uno solo
        text = text.strip()
        
        return text
    
    def _preprocess_content(self, content: str) -> str:
        """Preprocesa el contenido LaTeX manteniendo metadatos importantes"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Mantener comentarios con metadatos
            if line.strip().startswith('%') and any(keyword in line.lower() for keyword in 
                ['dificultad', 'unidad', 'tiempo', 'modalidad', 'tipo']):
                cleaned_lines.append(line)
            # Remover otros comentarios pero mantener línea
            elif '%' in line and not line.strip().startswith('\\'):
                cleaned_lines.append(line.split('%')[0])
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _enrich_exercise_metadata_v4(self, exercise: ParsedExercise) -> ParsedExercise:
        """Enriquece metadatos del ejercicio con información adicional"""
        
        # Agregar palabras clave si no las tiene
        if not exercise.palabras_clave:
            exercise.palabras_clave = self._extract_keywords(exercise.enunciado)
        
        # Ajustar tipo de actividad basado en la unidad y tipo de ejercicio
        if exercise.tipo_ejercicio == "Demostración":
            exercise.tipo_actividad = ["Teórica", "Análisis"]
        elif exercise.tipo_ejercicio == "Aplicación":
            exercise.tipo_actividad = ["Práctica", "Aplicación"]
        elif exercise.modalidad == "Computacional":
            exercise.tipo_actividad = ["Programación", "Simulación"]
        else:
            exercise.tipo_actividad = ["Ayudantía", "Ejercitación"]
        
        # Ajustar subtemas basado en la unidad temática
        if exercise.unidad_tematica == "Números Complejos":
            exercise.subtemas = ["Forma polar", "Operaciones", "Euler"]
        elif exercise.unidad_tematica == "Sistemas Lineales y Convolución":
            exercise.subtemas = ["LTI", "Convolución", "Respuesta impulso"]
        elif exercise.unidad_tematica == "Gráficos":
            exercise.subtemas = ["Graficación", "Transformaciones", "Visualización"]
        
        return exercise

class ParseError(Exception):
    """Excepción personalizada para errores de parsing"""
    pass

# Funciones de utilidad para integración con Streamlit
def create_parser_interface():
    """Crea una instancia del parser para usar en Streamlit"""
    return LaTeXParser()

def display_parsed_exercises(exercises: List[ParsedExercise]) -> None:
    """Muestra ejercicios parseados en Streamlit"""
    pass

def import_exercises_to_db(exercises: List[ParsedExercise], db_manager) -> bool:
    """Importa ejercicios a la base de datos"""
    pass