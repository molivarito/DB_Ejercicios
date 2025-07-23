"""
Importador de ejercicios desde archivos LaTeX - VERSIÓN CORREGIDA
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
    """Parser para extraer ejercicios desde archivos LaTeX - VERSIÓN CORREGIDA"""
    
    def __init__(self):
        # Patrones específicos para formato de Patricio
        self.exercise_patterns = [
            # Patrón 1: Items en enumerate dentro de subsecciones (PRINCIPAL)
            {
                'name': 'subsection_items',
                'pattern': r'\\subsection\*\{([^}]+)\}.*?\\begin\{enumerate\}(.*?)\\end\{enumerate\}',
                'priority': 1
            },
            # Patrón 2: Entornos ejercicio (genérico)
            {
                'name': 'ejercicio_environment',
                'start': r'\\begin\{ejercicio\}',
                'end': r'\\end\{ejercicio\}',
                'priority': 2
            }
        ]
        
        # Patrones para soluciones específicas del formato
        self.solution_patterns = [
            r'\\ifanswers\s*\{\s*\\color\{red\}.*?\\textbf\{Solución:\}\s*(.*?)\s*\}\s*\\fi',
            r'\\ifanswers\s*\{\\color\{red\}.*?\\textbf\{Solución:\}\s*(.*?)\}\s*\\fi',
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
        
        # Usar específicamente el parser para formato de Patricio
        exercises = self._parse_patricio_format_v4(content, source)
        
        # Si no encontramos ejercicios, intentar otros patrones
        if not exercises:
            exercises = self._fallback_extraction(content, source)
        
        # Enriquecer con metadatos
        for exercise in exercises:
            exercise.update(self._extract_metadata(exercise.get('raw_content', '')))
            exercise['fuente'] = source
            exercise['año_creacion'] = 2024
        
        return exercises
    
    def _clean_latex_content(self, content: str) -> str:
        """Limpia contenido LaTeX removiendo comandos no esenciales"""
        # Remover comandos de preámbulo
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
    
    def _parse_patricio_format_v4(self, content: str, source: str) -> List[Dict]:
        """Parser específico para el formato de Patricio - VERSIÓN 4 CORREGIDA"""
        exercises = []
        
        # Buscar subsecciones con ejercicios
        subsection_pattern = r'\\subsection\*\{([^}]+)\}(.*?)(?=\\subsection\*|\\section|\\end\{document\}|\Z)'
        subsections = re.findall(subsection_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for subsection_title, subsection_content in subsections:
            # Mapear título de subsección a unidad temática
            unit = self._map_subsection_to_unit(subsection_title)
            
            # NUEVA LÓGICA CORREGIDA: Extraer ejercicios completos con enumerate balanceado
            exercises_in_subsection = self._extract_complete_exercises_v4(subsection_content)
            
            for i, (enunciado, solucion, raw_content) in enumerate(exercises_in_subsection, 1):
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
                        'pattern_used': 'patricio_format_v4',
                        'raw_content': raw_content,
                        'palabras_clave': self._extract_keywords(enunciado)
                    }
                    exercises.append(exercise)
        
        return exercises
    
    def _extract_complete_exercises_v4(self, subsection_content: str) -> List[Tuple[str, str, str]]:
        """
        VERSIÓN 4: Extrae ejercicios completos con enumerate balanceado
        CORRIGE: El bug del regex que cortaba el contenido enumerate
        """
        exercises = []
        
        # NUEVO: Buscar el bloque enumerate con conteo de niveles balanceado
        enum_content = self._extract_balanced_enumerate(subsection_content)
        
        if not enum_content:
            return exercises
        
        # Dividir por ejercicios completos preservando estructura interna
        exercises_raw = self._split_into_complete_exercises_v4(enum_content)
        
        for exercise_raw in exercises_raw:
            if exercise_raw.strip():
                enunciado, solucion = self._separate_statement_solution_v4(exercise_raw)
                if enunciado.strip():
                    exercises.append((enunciado, solucion, exercise_raw))
        
        return exercises
    
    def _extract_balanced_enumerate(self, content: str) -> str:
        """
        NUEVA FUNCIÓN CLAVE: Extrae el contenido enumerate balanceando niveles
        SOLUCIONA: El problema del regex que tomaba el primer \end{enumerate}
        """
        
        # Encontrar el inicio del enumerate principal
        start_match = re.search(r'\\begin\{enumerate\}', content)
        if not start_match:
            return ""
        
        start_pos = start_match.end()
        
        # Contar niveles de anidamiento para encontrar el \end{enumerate} correcto
        level = 1
        pos = start_pos
        
        while pos < len(content) and level > 0:
            # Buscar próximo \begin{enumerate} o \end{enumerate}
            next_begin = content.find('\\begin{enumerate}', pos)
            next_end = content.find('\\end{enumerate}', pos)
            
            # Determinar cuál viene primero
            if next_begin == -1:
                next_begin = len(content)
            if next_end == -1:
                next_end = len(content)
            
            if next_begin < next_end:
                # Encontró otro \begin{enumerate}
                level += 1
                pos = next_begin + len('\\begin{enumerate}')
            else:
                # Encontró \end{enumerate}
                level -= 1
                pos = next_end + len('\\end{enumerate}')
                
                if level == 0:
                    # Encontramos el \end{enumerate} que cierra el nivel principal
                    end_pos = next_end
                    enum_content = content[start_pos:end_pos]
                    return enum_content
        
        return ""
    
    def _split_into_complete_exercises_v4(self, enum_content: str) -> List[str]:
        """
        VERSIÓN 4: Divide el contenido del enumerate en ejercicios completos
        MEJORADA: Mejor detección de niveles de anidamiento
        """
        exercises = []
        
        # Encontrar posiciones de items principales (no anidados)
        item_positions = []
        
        # Encontrar todas las posiciones de \item
        for match in re.finditer(r'\\item\s+', enum_content):
            pos = match.start()
            
            # Verificar si este \item está dentro de un enumerate/itemize anidado
            content_before = enum_content[:pos]
            
            # Contar diferentes tipos de entornos abiertos
            open_enums = len(re.findall(r'\\begin\{enumerate\}', content_before))
            closed_enums = len(re.findall(r'\\end\{enumerate\}', content_before))
            open_items = len(re.findall(r'\\begin\{itemize\}', content_before))
            closed_items = len(re.findall(r'\\end\{itemize\}', content_before))
            
            # Nivel de anidamiento total
            nesting_level = (open_enums - closed_enums) + (open_items - closed_items)
            
            # Si está en nivel 0, es un item principal
            if nesting_level == 0:
                item_positions.append(pos)
        
        # Dividir el contenido basándose en las posiciones de items principales
        for i, start_pos in enumerate(item_positions):
            if i < len(item_positions) - 1:
                end_pos = item_positions[i + 1]
                exercise = enum_content[start_pos:end_pos]
            else:
                exercise = enum_content[start_pos:]
            
            exercises.append(exercise.strip())
        
        return exercises
    
    def _separate_statement_solution_v4(self, exercise_content: str) -> Tuple[str, str]:
        """
        VERSIÓN 4: Separa enunciado de solución preservando estructura
        """
        # Limpiar el \item inicial
        content = re.sub(r'^\\item\s+', '', exercise_content).strip()
        
        # Verificar si tiene solución
        if '\\ifanswers' not in content:
            return content, ""
        
        # Encontrar donde empieza la solución
        ifanswers_match = re.search(r'\\ifanswers', content)
        if not ifanswers_match:
            return content, ""
        
        # Dividir en enunciado y bloque de solución
        split_pos = ifanswers_match.start()
        enunciado = content[:split_pos].strip()
        solution_block = content[split_pos:].strip()
        
        # Extraer solución del bloque ifanswers
        solucion = self._extract_solution_from_ifanswers_v4(solution_block)
        
        return enunciado, solucion
    
    def _extract_solution_from_ifanswers_v4(self, solution_block: str) -> str:
        """
        VERSIÓN 4: Extrae la solución del bloque \ifanswers de manera más robusta
        """
        # Patrones mejorados para extraer solución
        patterns = [
            # Patrón más específico para el formato de Patricio
            r'\\ifanswers\s*\{\s*\\color\{red\}\s*\\textbf\{Solución:\}\s*(.*?)\s*\}\s*\\fi',
            # Patrón sin "Solución:" explícito
            r'\\ifanswers\s*\{\s*\\color\{red\}\\textbf\{Solución:\}\s*(.*?)\s*\}\s*\\fi',
            r'\\ifanswers\s*\{\s*\\color\{red\}\s*(.*?)\s*\}\s*\\fi',
            # Patrón más general
            r'\\ifanswers\s*\{(.*?)\}\s*\\fi'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, solution_block, re.DOTALL)
            if match:
                raw_solution = match.group(1)
                
                # Limpiar comandos LaTeX básicos pero preservar contenido matemático
                solution = re.sub(r'\\textbf\{[^}]*\}', '', raw_solution)
                solution = re.sub(r'\\textit\{([^}]*)\}', r'\1', solution)
                solution = re.sub(r'\\color\{[^}]*\}', '', solution)
                solution = solution.strip()
                
                if solution:
                    return solution
        
        return ""
    
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
    
    def _clean_exercise_content(self, content: str) -> str:
        """Limpia el contenido del ejercicio preservando estructura matemática"""
        if not content:
            return ""
        
        # Limpiar comandos básicos pero mantener matemáticas y estructura
        cleaned = re.sub(r'\\textbf\{([^}]+)\}', r'\1', content)  # Bold
        cleaned = re.sub(r'\\textit\{([^}]+)\}', r'\1', cleaned)   # Italic
        cleaned = re.sub(r'\\emph\{([^}]+)\}', r'\1', cleaned)     # Emphasis
        
        # Mantener estructura de listas pero limpiarlas un poco
        cleaned = re.sub(r'\n\s*\n\s*\n+', r'\n\n', cleaned)  # Máximo 2 líneas vacías
        cleaned = re.sub(r'^\s+', '', cleaned, flags=re.MULTILINE)  # Espacios al inicio de línea
        
        return cleaned.strip()
    
    def _infer_difficulty(self, content: str) -> str:
        """Infiere dificultad basado en palabras clave y complejidad"""
        content_lower = content.lower()
        
        # Palabras clave para diferentes niveles
        basic_keywords = ['calcule', 'determine', 'grafique', 'simple', 'encuentre']
        advanced_keywords = ['demuestre', 'derive', 'analice', 'complejo', 'integral', 'ecuación diferencial']
        
        basic_count = sum(1 for word in basic_keywords if word in content_lower)
        advanced_count = sum(1 for word in advanced_keywords if word in content_lower)
        
        # Complejidad por longitud y símbolos matemáticos
        math_symbols = len(re.findall(r'\\[a-zA-Z]+|[\$\{\}]', content))
        has_enumerate = '\\begin{enumerate}' in content
        
        if advanced_count > basic_count or math_symbols > 15:
            return 'Avanzado'
        elif basic_count > 0 or math_symbols > 8 or has_enumerate:
            return 'Intermedio'
        else:
            return 'Básico'
    
    def _infer_modality(self, content: str) -> str:
        """Infiere modalidad basado en contenido"""
        content_lower = content.lower()
        
        computational_keywords = ['python', 'código', 'implemente', 'programe', 'compute']
        
        if any(word in content_lower for word in computational_keywords):
            return 'Computacional'
        elif 'grafique' in content_lower or 'graph' in content_lower:
            return 'Mixto'
        else:
            return 'Teórico'
    
    def _infer_time(self, content: str) -> int:
        """Infiere tiempo estimado basado en complejidad"""
        # Factores de complejidad
        word_count = len(content.split())
        math_complexity = len(re.findall(r'\\[a-zA-Z]+', content))
        has_parts = 'enumerate' in content or len(re.findall(r'\([a-z]\)', content)) > 1
        has_multiple_questions = content.count('?') > 1
        
        base_time = 15
        if word_count > 100:
            base_time += 15
        if math_complexity > 5:
            base_time += 10
        if has_parts:
            base_time += 20
        if has_multiple_questions:
            base_time += 10
            
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
    
    def _fallback_extraction(self, content: str, source: str) -> List[Dict]:
        """Extracción de respaldo cuando no se encuentran patrones específicos"""
        exercises = []
        
        # Dividir por párrafos significativos
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Filtrar párrafos que parezcan ejercicios
        exercise_paragraphs = []
        for para in paragraphs:
            if (len(para) > 50 and  # Longitud mínima
                ('?' in para or 'calcul' in para.lower() or 'determin' in para.lower() or
                 'encuentr' in para.lower() or 'demuestre' in para.lower())):
                exercise_paragraphs.append(para)
        
        # Crear ejercicios
        for i, para in enumerate(exercise_paragraphs, 1):
            exercise = {
                'titulo': f"Ejercicio {i}",
                'enunciado': self._clean_exercise_content(para),
                'solucion_completa': "",
                'unidad_tematica': 'Por determinar',
                'nivel_dificultad': 'Intermedio',
                'modalidad': 'Teórico',
                'tiempo_estimado': 20,
                'fuente': source,
                'año_creacion': 2024,
                'estado': 'En revisión',
                'pattern_used': 'fallback_paragraphs',
                'raw_content': para,
                'palabras_clave': []
            }
            exercises.append(exercise)
        
        return exercises

# Funciones de utilidad para Streamlit (mantener las existentes)
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