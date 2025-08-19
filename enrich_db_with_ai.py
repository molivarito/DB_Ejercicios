import sqlite3
import os
import sys
import re
import google.generativeai as genai
import json
import demjson3
import asyncio
from typing import List, Dict, Optional
from tqdm import tqdm
from database.db_manager import DatabaseManager
from tqdm.asyncio import tqdm as async_tqdm

# ==============================================================================
# --- CONFIGURACIÓN PRINCIPAL ---
# ==============================================================================

# Añade tu API Key de Google aquí
GOOGLE_API_KEY = "AIzaSyDBspvkWFs8d5aW1cnrxKqS3lmm0ehiVmI"

# Ruta a la base de datos
DB_PATH = "database/ejercicios.db"

# --- MODO DE SEGURIDAD ---
# True: Solo simula y muestra los cambios que haría. No modifica la base de datos.
# False: Ejecuta los cambios y modifica la base de datos.
DRY_RUN = False 

# --- CONFIGURACIÓN DE RENDIMIENTO ---
# Número de ejercicios a procesar en paralelo. Un valor bajo como 2 o 3 es más seguro.
CONCURRENT_REQUESTS = 2
# Timeout en segundos para cada ejercicio. Si tarda más, se cancela y se reintenta.
TASK_TIMEOUT = 600.0  # Aumentado a 10 minutos para tareas complejas
# Número de reintentos si una tarea falla
MAX_RETRIES = 2 # Aumentado a 2 reintentos (3 intentos en total)

# ==============================================================================
# --- DEFINICIÓN DE OBJETIVOS DE APRENDIZAJE DEL CURSO ---
# ==============================================================================

OBJETIVOS_APRENDIZAJE = {
    "OA_I": "Reconocer y clasificar señales y sistemas, y entender la diferencia entre continuos y discretos.",
    "OA_II": "Aplicar los conceptos de convolución y respuesta al impulso para sistemas continuos y discretos.",
    "OA_III": "Interpretar y aplicar los conceptos de muestreo y reconstrucción de señales.",
    "OA_IV": "Analizar señales en términos de sus contenidos de frecuencia.",
    "OA_V": "Entender y aplicar las definiciones y propiedades de las transformadas de Fourier, Laplace y Z.",
    "OA_VI": "Determinar la respuesta de sistemas lineales a cualquier entrada por medio de funciones de transferencia."
}

# ==============================================================================
# --- PROMPTS PARA CADA FASE ---
# ==============================================================================

PHASE_1_PROMPT = """
Eres un profesor experto en la materia 'Señales y Sistemas' y un corrector de estilo técnico y LaTeX. 
Tu tarea es analizar, corregir y clasificar un ejercicio.

**Ejercicio Original:**
- Título: {titulo}
- Enunciado en LaTeX: {enunciado}
- Solución en LaTeX: {solucion}

**Tareas a Realizar:**
1.  **Corrección y Normalización de LaTeX:** Revisa el `enunciado` y la `solucion`. Corrige errores de tipeo, gramática y sintaxis de LaTeX. **Fundamentalmente, normaliza el LaTeX para que sea compatible con el renderizador de Markdown de Streamlit siguiendo estas reglas:**
    - **Ecuaciones en bloque:** Usa `$$ ... $$` en lugar de `\\[ ... \\]` o `\\begin{{equation}}`.
    - **Ecuaciones alineadas:** Dentro de `$$ ... $$`, usa el entorno `\\begin{{aligned}} ... \\end{{aligned}}`. **No uses `align` o `align*`**.
    - **Listas:** Usa los entornos estándar `\\begin{{enumerate}}` y `\\begin{{itemize}}`.
    - **Ecuaciones en línea (inline):** Usa un solo par de signos de dólar `$ ... $`. **No uses `\\$...\\$` ni otros delimitadores como `\\( ... \\)`**.
    - **Comandos:** Usa comandos estándar de LaTeX y `amsmath` (`\\frac`, `\\int`, `\\sum`, `\\delta`, etc.). Evita comandos de paquetes muy específicos.
    - **Escapes:** Asegúrate de que todas las barras invertidas `\\` estén correctamente escapadas para JSON (es decir, `\\\\`).
    - **Codificación de Caracteres:** Asegúrate de que todo el texto esté en UTF-8. Los caracteres especiales como acentos (á, é, í, ó, ú, ñ) y otros símbolos (¿, ¡) deben ser representados directamente como caracteres UTF-8, **NO** como comandos de LaTeX (ej: usa 'á' en lugar de '\\'a' o '{{\\'a}}').
2.  **Análisis Fundamental:** Basado en el contenido corregido, determina los siguientes metadatos.

**Formato de Salida Obligatorio:**
Devuelve tu análisis exclusivamente en formato JSON, sin texto introductorio ni explicaciones. El LaTeX corregido debe seguir las reglas de normalización. Usa la siguiente estructura exacta:
{{
  "enunciado_corregido": "El texto del enunciado, ya corregido y listo para compilar.",
  "titulo_sugerido": "Genera un título nuevo, corto y descriptivo basado en el contenido. Ej: 'Convolución de Señales Rectangulares'.",
  "solucion_corregida": "El texto de la solución, ya corregido y listo para compilar.",
  "unidad_tematica": "Clasifica en UNA de las siguientes: [Introducción, Sistemas Continuos, Transformada de Fourier, Transformada de Laplace, Sistemas Discretos, Transformada de Fourier Discreta, Transformada Z]",
  "subtemas": ["Genera una lista de 2 a 3 subtemas específicos en español"],
  "nivel_dificultad": "Evalúa en UNA de las siguientes: [Básico, Intermedio, Avanzado, Desafío]",
  "tiempo_estimado": "Estima el tiempo de resolución en minutos (solo el número entero)",
  "palabras_clave": ["Genera una lista de 5 a 7 palabras clave técnicas y relevantes en español"]
}}
"""

PHASE_2_PROMPT = """
Eres un pedagogo experto diseñando el currículum del curso 'Señales y Sistemas'. 
Tu tarea es determinar el propósito de aprendizaje de un ejercicio.

**Contexto del Ejercicio (ya analizado):**
- Título: {titulo}
- Enunciado Corregido: {enunciado_corregido}
- Unidad Temática: {unidad_tematica}
- Nivel de Dificultad: {nivel_dificultad}

**Lista de Objetivos de Aprendizaje (OA) del Curso:**
{lista_oa}

**Tareas a Realizar:**
1.  **objetivos_curso:** De la lista de OAs, selecciona los códigos (ej: ["OA1", "OA3"]) que este ejercicio ayuda a cumplir.
2.  **prerrequisitos:** Describe brevemente los conocimientos previos que un estudiante necesita para resolver este ejercicio.

**Formato de Salida Obligatorio:**
Devuelve tu análisis exclusivamente en formato JSON. Usa la siguiente estructura exacta:
{{"objetivos_curso": ["...", "..."], "prerrequisitos": "..."}}
"""

PHASE_3_PROMPT = """
Eres un profesor con años de experiencia enseñando 'Señales y Sistemas'. 
Tu tarea es anticipar cómo los estudiantes interactuarán con un ejercicio.

**Contexto del Ejercicio (ya analizado):**
- Título: {titulo}
- Enunciado: {enunciado_corregido}
- Unidad Temática: {unidad_tematica}
- Nivel de Dificultad: {nivel_dificultad}

**Tareas a Realizar:**
1.  **errores_comunes:** Describe en una lista 2 o 3 errores o malentendidos típicos que los estudiantes cometen al resolver este problema.
2.  **hints:** Escribe una o dos pistas sutiles que podrías dar a un estudiante que está atascado.
3.  **extensiones_posibles:** Propón una idea interesante para extender este ejercicio o hacerlo más desafiante.

**Formato de Salida Obligatorio:**
Devuelve tu análisis exclusivamente en formato JSON. Usa la siguiente estructura:
{{"errores_comunes": ["...", "..."], "hints": ["...", "..."], "extensiones_posibles": "..."}}
"""

# ==============================================================================
# --- FUNCIONES DE SOPORTE Y PIPELINE ---
# ==============================================================================

class AIEnricher:
    """
    Clase que encapsula la lógica para enriquecer ejercicios usando un modelo de IA.
    """
    def __init__(self, model, db_manager: DatabaseManager):
        """
        Inicializa el enriquecedor con el modelo de IA y el gestor de BD.
        """
        self.model = model
        self.db_manager = db_manager

    @staticmethod
    def _clean_text_for_ai(text: str) -> str:
        """
        Limpia y normaliza una cadena de texto antes de enviarla a la IA.
        """
        if not text:
            return ""
        try:
            repaired_text = text.encode('latin1').decode('utf-8')
            if 'Ã' not in repaired_text: text = repaired_text
        except (UnicodeEncodeError, UnicodeDecodeError): pass
        try:
            text = re.sub(r'\\U([0-9a-fA-F]{8})', lambda m: chr(int(m.group(1), 16)), text)
            text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)
            text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), text)
        except (ValueError, TypeError): pass
        text = text.replace('\b', '').replace('\f', '').replace('\\\\', '\\')
        return text.strip()

    @staticmethod
    def _repair_json_string(json_str: str) -> str:
        """Intenta reparar un string JSON que tiene secuencias de escape inválidas."""
        return re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', json_str)

    async def _execute_ai_call(self, prompt_template, exercise, prev_phase_result=None) -> Optional[Dict]:
        """Función genérica para llamar a la API de forma asíncrona."""
        prompt_data = {"titulo": exercise.get('titulo', ''), "enunciado": exercise.get('enunciado', ''), "solucion": exercise.get('solucion_completa', 'No proporcionada.')}
        if prev_phase_result:
            prompt_data.update({
                "enunciado_corregido": prev_phase_result.get('enunciado_corregido', ''),
                "unidad_tematica": prev_phase_result.get('unidad_tematica', ''),
                "nivel_dificultad": prev_phase_result.get('nivel_dificultad', ''),
                "lista_oa": "\n".join([f"- {k}: {v}" for k, v in OBJETIVOS_APRENDIZAJE.items()])
            })
        prompt = prompt_template.format(**prompt_data)
        try:
            response = await self.model.generate_content_async(prompt)
            text_response = response.text
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if not json_match:
                tqdm.write(f"⚠️ No se encontró un bloque JSON en la respuesta para el ID {exercise['id']}. Respuesta: {text_response[:100]}")
                return None
            json_str = json_match.group(0)
            repaired_json_str = self._repair_json_string(json_str)
            try:
                return json.loads(repaired_json_str)
            except json.JSONDecodeError:
                tqdm.write(f"ℹ️  Parseo estricto falló para ID {exercise['id']}. Intentando con parser permisivo...")
                return demjson3.decode(repaired_json_str)
        except Exception as e:
            tqdm.write(f"❌ Error en la llamada a la IA o parseo de JSON para ID {exercise['id']}. Error: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                tqdm.write(f"   -> Respuesta recibida: {response.text[:200]}")
            return None

    async def _run_analysis_pipeline(self, exercise: Dict, semaphore: asyncio.Semaphore):
        """Ejecuta el pipeline completo de 3 fases para un solo ejercicio."""
        async with semaphore:
            phase_1_result = await self._execute_ai_call(PHASE_1_PROMPT, exercise)
            if not phase_1_result: return exercise['id'], None
            
            phase_2_result = await self._execute_ai_call(PHASE_2_PROMPT, exercise, phase_1_result)
            if not phase_2_result: return exercise['id'], None

            phase_3_result = await self._execute_ai_call(PHASE_3_PROMPT, exercise, phase_1_result)
            if not phase_3_result: return exercise['id'], None

            return exercise['id'], {**phase_1_result, **phase_2_result, **phase_3_result}

    async def _run_analysis_pipeline_with_retries(self, exercise: Dict, semaphore: asyncio.Semaphore):
        """Ejecuta el pipeline con una lógica de reintentos."""
        for attempt in range(MAX_RETRIES + 1):
            try:
                return await asyncio.wait_for(
                    self._run_analysis_pipeline(exercise, semaphore),
                    timeout=TASK_TIMEOUT
                )
            except asyncio.TimeoutError:
                tqdm.write(f"⚠️ Timeout (Intento {attempt + 1}/{MAX_RETRIES + 1}) para ID {exercise['id']}.")
            except Exception as e:
                tqdm.write(f"❌ Error (Intento {attempt + 1}/{MAX_RETRIES + 1}) para ID {exercise['id']}: {e}")
            
            if attempt < MAX_RETRIES:
                tqdm.write(f"   -> Reintentando en 10 segundos...")
                await asyncio.sleep(10)
        
        tqdm.write(f"❌ Falló definitivamente el procesamiento para ID {exercise['id']} después de {MAX_RETRIES + 1} intentos.")
        return exercise['id'], None

    def _update_exercise_in_db(self, exercise_id: int, final_data: Dict):
        """Actualiza un ejercicio en la base de datos con los datos enriquecidos."""
        field_map = {"titulo_sugerido": "titulo", "enunciado_corregido": "enunciado", "solucion_corregida": "solucion_completa", "unidad_tematica": "unidad_tematica", "subtemas": "subtemas", "nivel_dificultad": "nivel_dificultad", "tiempo_estimado": "tiempo_estimado", "palabras_clave": "palabras_clave", "objetivos_curso": "objetivos_curso", "prerrequisitos": "prerrequisitos", "errores_comunes": "errores_comunes", "hints": "hints", "extensiones_posibles": "extensiones_posibles"}
        data_to_update = {field_map[k]: v for k, v in final_data.items() if k in field_map}
        data_to_update['estado_ia'] = 'COMPLETADO'
        if not data_to_update: return
        if DRY_RUN:
            tqdm.write(f"✔️  [SIMULACIÓN] ID {exercise_id}: {len(data_to_update)} campos listos para actualizar.")
            return
        if not self.db_manager.actualizar_ejercicio(exercise_id, data_to_update):
            tqdm.write(f"❌ Error al actualizar la BD para el ID {exercise_id} usando el manager.")

    async def enrich_exercises(self, exercises_to_process: List[Dict]):
        """
        Orquesta el enriquecimiento de una lista de ejercicios de forma paralela.
        """
        if not exercises_to_process:
            print("✅ No hay ejercicios nuevos o pendientes para procesar.")
            return

        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        tasks = [self._run_analysis_pipeline_with_retries(ex, semaphore) for ex in exercises_to_process]
        update_count = 0
        error_count = 0
        
        for future in async_tqdm.as_completed(tasks, desc="Enriqueciendo Base de Datos"):
            exercise_id, final_data = await future
            if final_data:
                self._update_exercise_in_db(exercise_id, final_data)
                update_count += 1
            else:
                self.db_manager.actualizar_estado_ia(exercise_id, 'ERROR')
                error_count += 1
            await asyncio.sleep(1)

        print("\n--- Proceso de Enriquecimiento Finalizado ---")
        print(f"✅ {update_count} de {len(exercises_to_process)} ejercicios fueron procesados exitosamente.")
        if error_count > 0:
            print(f"❌ {error_count} ejercicios no pudieron ser procesados después de varios intentos.")

def setup_ai_model():
    """Configura y retorna el modelo generativo de Gemini."""
    try:
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "TU_API_KEY_AQUI":
            raise ValueError("La API Key de Google no ha sido configurada.")
        genai.configure(api_key=GOOGLE_API_KEY)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        generation_config = {"response_mime_type": "application/json"}
        model = genai.GenerativeModel('gemini-1.5-pro-latest', 
                                      safety_settings=safety_settings,
                                      generation_config=generation_config)
        print("✅ Conexión con el modelo de IA establecida.")
        return model
    except Exception as e:
        print(f"❌ Error al configurar el modelo de IA: {e}")
        return None

def get_exercises_from_db(force_all=False) -> List[Dict]:
    """Obtiene todos los ejercicios de la base de datos y limpia el texto."""
    print(f"🔌 Conectando a la base de datos en '{DB_PATH}'...")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if force_all:
            query = "SELECT * FROM ejercicios"
        else:
            query = "SELECT * FROM ejercicios WHERE estado_ia IS NULL OR estado_ia = 'PENDIENTE' OR estado_ia = 'ERROR'"

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        # Limpiar el texto de los ejercicios antes de procesarlos
        exercises = []
        for row in rows:
            exercise_dict = dict(row)
            # Limpiar los campos de texto principales que se envían a la IA
            for key in ['titulo', 'enunciado', 'solucion_completa']:
                if key in exercise_dict and exercise_dict[key]:
                    exercise_dict[key] = AIEnricher._clean_text_for_ai(exercise_dict[key])
            exercises.append(exercise_dict)
            
        print(f"📚 Se encontraron y limpiaron {len(exercises)} ejercicios en la base de datos.")
        return exercises
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return []

# ==============================================================================
# --- FUNCIÓN PRINCIPAL ASÍNCRONA ---
# ==============================================================================
async def main():
    """Función principal que orquesta el enriquecimiento de forma paralela."""
    model = setup_ai_model()
    if not model: 
        return
    
    force_all = '--force-all' in sys.argv
    if force_all:
        print("\n⚡ MODO FORZADO: Se re-procesarán TODOS los ejercicios.")

    exercises_to_process = get_exercises_from_db(force_all=force_all)

    if DRY_RUN:
        print("\n" + "="*60 + "\n== MODO SIMULACIÓN (DRY RUN) ACTIVADO ==\n" + "="*60 + "\n")
    
    # Crear instancias de las dependencias
    db_manager = DatabaseManager(db_path=DB_PATH)
    enricher = AIEnricher(model, db_manager)

    # Ejecutar el proceso de enriquecimiento
    await enricher.enrich_exercises(exercises_to_process)

if __name__ == "__main__":
    asyncio.run(main())