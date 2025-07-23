"""
Gestor de Base de Datos - Extensión para Batch Import
Sistema de Gestión de Ejercicios - Señales y Sistemas
Patricio de la Cuadra - PUC Chile
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime
import json
from dataclasses import asdict

# Configurar logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de base de datos SQLite para ejercicios"""
    
    def __init__(self, db_path: str = "database/ejercicios.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Crear tabla principal de ejercicios con 32+ campos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ejercicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    -- Información básica
                    titulo TEXT NOT NULL,
                    enunciado TEXT NOT NULL,
                    datos_entrada TEXT,
                    solucion_completa TEXT,
                    respuesta_final TEXT,
                    codigo_python TEXT,
                    
                    -- Clasificación temática
                    unidad_tematica TEXT NOT NULL,
                    subtemas TEXT, -- JSON array
                    nivel_dificultad TEXT NOT NULL,
                    modalidad TEXT NOT NULL,
                    palabras_clave TEXT, -- JSON array
                    
                    -- Metadatos pedagógicos
                    tiempo_estimado INTEGER DEFAULT 20,
                    objetivos_curso TEXT, -- JSON array
                    prerrequisitos TEXT,
                    tipo_actividad TEXT, -- JSON array
                    competencias_abet TEXT, -- JSON array
                    
                    -- Información docente
                    fuente TEXT,
                    año_creacion INTEGER,
                    comentarios_docente TEXT,
                    errores_comunes TEXT,
                    hints TEXT,
                    
                    -- Control de versiones
                    version INTEGER DEFAULT 1,
                    estado TEXT DEFAULT 'Borrador',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    creado_por TEXT,
                    modificado_por TEXT,
                    
                    -- Métricas de uso
                    veces_usado INTEGER DEFAULT 0,
                    ultima_vez_usado TIMESTAMP,
                    promedio_tiempo_resolucion REAL,
                    porcentaje_acierto REAL,
                    
                    -- Metadatos del parser
                    importado_desde TEXT,
                    pattern_used TEXT,
                    confidence_score REAL,
                    necesita_revision BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Crear tabla de historial de importaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS importaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    archivo_origen TEXT NOT NULL,
                    fecha_importacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_ejercicios INTEGER,
                    ejercicios_exitosos INTEGER,
                    ejercicios_fallidos INTEGER,
                    metodo_importacion TEXT,
                    detalles_errores TEXT, -- JSON
                    usuario TEXT
                )
            """)
            
            # Crear tabla de errores de importación
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS errores_importacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    importacion_id INTEGER,
                    ejercicio_titulo TEXT,
                    tipo_error TEXT,
                    mensaje_error TEXT,
                    contenido_original TEXT,
                    fecha_error TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (importacion_id) REFERENCES importaciones (id)
                )
            """)
            
            # Crear índices para optimizar búsquedas
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unidad_tematica ON ejercicios(unidad_tematica)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dificultad ON ejercicios(nivel_dificultad)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_modalidad ON ejercicios(modalidad)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_estado ON ejercicios(estado)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fecha_creacion ON ejercicios(fecha_creacion)")
            
            conn.commit()
            logger.info("Base de datos inicializada correctamente")
    
    def batch_import_exercises(self, exercises: List, archivo_origen: str = "", 
                             usuario: str = "Sistema") -> Dict[str, Union[int, List]]:
        """
        Importa múltiples ejercicios en una transacción
        
        Args:
            exercises: Lista de ejercicios (ParsedExercise o dict)
            archivo_origen: Nombre del archivo de origen
            usuario: Usuario que realiza la importación
            
        Returns:
            Dict con estadísticas de la importación
        """
        resultados = {
            'total_ejercicios': len(exercises),
            'ejercicios_exitosos': 0,
            'ejercicios_fallidos': 0,
            'errores': [],
            'ids_insertados': [],
            'importacion_id': None
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Registrar la importación
                cursor.execute("""
                    INSERT INTO importaciones 
                    (archivo_origen, total_ejercicios, usuario, metodo_importacion)
                    VALUES (?, ?, ?, 'latex_parser')
                """, (archivo_origen, len(exercises), usuario))
                
                importacion_id = cursor.lastrowid
                resultados['importacion_id'] = importacion_id
                
                # Importar cada ejercicio
                for i, exercise in enumerate(exercises):
                    try:
                        exercise_id = self._insert_single_exercise(cursor, exercise, importacion_id)
                        resultados['ejercicios_exitosos'] += 1
                        resultados['ids_insertados'].append(exercise_id)
                        
                    except Exception as e:
                        resultados['ejercicios_fallidos'] += 1
                        error_info = {
                            'indice': i,
                            'titulo': getattr(exercise, 'titulo', f'Ejercicio {i+1}'),
                            'error': str(e)
                        }
                        resultados['errores'].append(error_info)
                        
                        # Registrar error en la base de datos
                        self._log_import_error(cursor, importacion_id, exercise, str(e))
                        
                        logger.error(f"Error importando ejercicio {i+1}: {str(e)}")
                
                # Actualizar estadísticas de la importación
                cursor.execute("""
                    UPDATE importaciones 
                    SET ejercicios_exitosos = ?, ejercicios_fallidos = ?, 
                        detalles_errores = ?
                    WHERE id = ?
                """, (
                    resultados['ejercicios_exitosos'],
                    resultados['ejercicios_fallidos'], 
                    json.dumps(resultados['errores']),
                    importacion_id
                ))
                
                conn.commit()
                
                logger.info(f"Importación completada: {resultados['ejercicios_exitosos']}/{len(exercises)} ejercicios importados exitosamente")
                
        except Exception as e:
            logger.error(f"Error durante la importación batch: {str(e)}")
            raise DatabaseError(f"Error en importación masiva: {str(e)}")
        
        return resultados
    
    def _insert_single_exercise(self, cursor, exercise, importacion_id: int) -> int:
        """Inserta un ejercicio individual en la base de datos"""
        
        # Convertir exercise a dict si es un objeto
        if hasattr(exercise, '__dict__'):
            exercise_data = asdict(exercise) if hasattr(exercise, '__dataclass_fields__') else exercise.__dict__
        else:
            exercise_data = exercise
        
        # Preparar datos para inserción
        insert_data = {
            # Información básica
            'titulo': exercise_data.get('titulo', ''),
            'enunciado': exercise_data.get('enunciado', ''),
            'datos_entrada': exercise_data.get('datos_entrada', ''),
            'solucion_completa': exercise_data.get('solucion', ''),
            'respuesta_final': exercise_data.get('respuesta_final', ''),
            'codigo_python': exercise_data.get('codigo_python', ''),
            
            # Clasificación temática
            'unidad_tematica': exercise_data.get('unidad_tematica', 'Por determinar'),
            'subtemas': json.dumps(exercise_data.get('subtemas', [])),
            'nivel_dificultad': exercise_data.get('nivel_dificultad', 'Intermedio'),
            'modalidad': exercise_data.get('modalidad', 'Teórico'),
            'palabras_clave': json.dumps(exercise_data.get('palabras_clave', [])),
            
            # Metadatos pedagógicos
            'tiempo_estimado': exercise_data.get('tiempo_estimado', 20),
            'objetivos_curso': json.dumps(exercise_data.get('objetivos_curso', [])),
            'prerrequisitos': exercise_data.get('prerrequisitos', ''),
            'tipo_actividad': json.dumps(exercise_data.get('tipo_actividad', ['Ayudantía'])),
            'competencias_abet': json.dumps(exercise_data.get('competencias_abet', [])),
            
            # Información docente
            'fuente': exercise_data.get('fuente', 'Importación LaTeX'),
            'año_creacion': exercise_data.get('año_creacion', datetime.now().year),
            'comentarios_docente': exercise_data.get('comentarios', ''),
            'errores_comunes': exercise_data.get('errores_comunes', ''),
            'hints': exercise_data.get('hints', ''),
            
            # Control de versiones
            'estado': 'Importado' if exercise_data.get('confidence_score', 0) > 0.7 else 'Requiere Revisión',
            'creado_por': 'LaTeX Parser',
            'modificado_por': 'LaTeX Parser',
            
            # Metadatos del parser
            'importado_desde': f'importacion_{importacion_id}',
            'pattern_used': exercise_data.get('pattern_used', ''),
            'confidence_score': exercise_data.get('confidence_score', 0.0),
            'necesita_revision': exercise_data.get('confidence_score', 0) < 0.7
        }
        
        # Validar datos obligatorios
        if not insert_data['titulo'] or not insert_data['enunciado']:
            raise ValueError("Título y enunciado son obligatorios")
        
        # Construir query de inserción
        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['?' for _ in insert_data])
        
        query = f"""
            INSERT INTO ejercicios ({columns})
            VALUES ({placeholders})
        """
        
        cursor.execute(query, list(insert_data.values()))
        exercise_id = cursor.lastrowid
        
        logger.debug(f"Ejercicio insertado con ID: {exercise_id}")
        return exercise_id
    
    def _log_import_error(self, cursor, importacion_id: int, exercise, error_message: str):
        """Registra un error de importación en la base de datos"""
        titulo = getattr(exercise, 'titulo', 'Desconocido') if hasattr(exercise, 'titulo') else 'Desconocido'
        contenido = str(exercise)[:1000]  # Limitar contenido
        
        cursor.execute("""
            INSERT INTO errores_importacion 
            (importacion_id, ejercicio_titulo, tipo_error, mensaje_error, contenido_original)
            VALUES (?, ?, ?, ?, ?)
        """, (importacion_id, titulo, 'ImportError', error_message, contenido))
    
    def get_import_history(self, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de importaciones"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT *, 
                       (ejercicios_exitosos * 100.0 / total_ejercicios) as porcentaje_exito
                FROM importaciones 
                ORDER BY fecha_importacion DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_import_errors(self, importacion_id: int) -> List[Dict]:
        """Obtiene los errores de una importación específica"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM errores_importacion 
                WHERE importacion_id = ?
                ORDER BY fecha_error DESC
            """, (importacion_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def validate_exercise_data(self, exercise_data: Dict) -> List[str]:
        """Valida los datos de un ejercicio antes de la inserción"""
        errors = []
        
        # Validaciones obligatorias
        if not exercise_data.get('titulo', '').strip():
            errors.append("Título es obligatorio")
        
        if not exercise_data.get('enunciado', '').strip():
            errors.append("Enunciado es obligatorio")
        
        # Validaciones de formato
        if exercise_data.get('tiempo_estimado', 0) <= 0:
            errors.append("Tiempo estimado debe ser mayor a 0")
        
        valid_difficulties = ['Básico', 'Intermedio', 'Avanzado', 'Desafío']
        if exercise_data.get('nivel_dificultad') not in valid_difficulties:
            errors.append(f"Dificultad debe ser una de: {', '.join(valid_difficulties)}")
        
        valid_modalities = ['Teórico', 'Computacional', 'Mixto']
        if exercise_data.get('modalidad') not in valid_modalities:
            errors.append(f"Modalidad debe ser una de: {', '.join(valid_modalities)}")
        
        return errors
    
    def bulk_update_exercises(self, updates: List[Dict]) -> Dict[str, int]:
        """Actualiza múltiples ejercicios en batch"""
        results = {'updated': 0, 'failed': 0}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for update in updates:
                    try:
                        exercise_id = update.pop('id')
                        
                        # Agregar timestamp de modificación
                        update['fecha_modificacion'] = datetime.now().isoformat()
                        
                        # Construir query de actualización
                        set_clause = ', '.join([f"{key} = ?" for key in update.keys()])
                        values = list(update.values()) + [exercise_id]
                        
                        query = f"UPDATE ejercicios SET {set_clause} WHERE id = ?"
                        cursor.execute(query, values)
                        
                        if cursor.rowcount > 0:
                            results['updated'] += 1
                        else:
                            results['failed'] += 1
                            
                    except Exception as e:
                        results['failed'] += 1
                        logger.error(f"Error actualizando ejercicio: {str(e)}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error en actualización masiva: {str(e)}")
            raise DatabaseError(f"Error en actualización masiva: {str(e)}")
        
        return results
    
    def get_exercises_needing_review(self) -> List[Dict]:
        """Obtiene ejercicios que necesitan revisión"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, titulo, unidad_tematica, nivel_dificultad, 
                       confidence_score, pattern_used, fecha_creacion
                FROM ejercicios 
                WHERE necesita_revision = TRUE 
                   OR confidence_score < 0.7
                ORDER BY confidence_score ASC, fecha_creacion DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_exercise_reviewed(self, exercise_id: int, usuario: str = "Sistema"):
        """Marca un ejercicio como revisado"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ejercicios 
                SET necesita_revision = FALSE, 
                    estado = 'Listo',
                    modificado_por = ?,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (usuario, exercise_id))
            
            conn.commit()
    
    def get_duplicate_exercises(self, similarity_threshold: float = 0.8) -> List[Dict]:
        """Encuentra ejercicios potencialmente duplicados"""
        # Implementación básica - en producción se podría usar análisis de texto más sofisticado
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e1.id as id1, e1.titulo as titulo1,
                       e2.id as id2, e2.titulo as titulo2,
                       e1.enunciado as enunciado1, e2.enunciado as enunciado2
                FROM ejercicios e1
                JOIN ejercicios e2 ON e1.id < e2.id
                WHERE e1.titulo = e2.titulo 
                   OR (LENGTH(e1.enunciado) > 50 AND LENGTH(e2.enunciado) > 50 
                       AND SUBSTR(e1.enunciado, 1, 100) = SUBSTR(e2.enunciado, 1, 100))
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_failed_imports(self, days_old: int = 7):
        """Limpia importaciones fallidas antiguas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Eliminar errores de importaciones antiguas
            cursor.execute("""
                DELETE FROM errores_importacion 
                WHERE importacion_id IN (
                    SELECT id FROM importaciones 
                    WHERE ejercicios_exitosos = 0 
                    AND fecha_importacion < datetime('now', '-{} days')
                )
            """.format(days_old))
            
            # Eliminar importaciones completamente fallidas
            cursor.execute("""
                DELETE FROM importaciones 
                WHERE ejercicios_exitosos = 0 
                AND fecha_importacion < datetime('now', '-{} days')
            """.format(days_old))
            
            conn.commit()
            logger.info(f"Limpieza completada: importaciones fallidas > {days_old} días eliminadas")

class DatabaseError(Exception):
    """Excepción personalizada para errores de base de datos"""
    pass

# Funciones de utilidad para integración con el parser
def connect_to_database(db_path: str = "database/ejercicios.db") -> DatabaseManager:
    """Crea conexión a la base de datos"""
    return DatabaseManager(db_path)

def import_parsed_exercises(exercises: List, db_manager: DatabaseManager, 
                          archivo_origen: str = "") -> Dict:
    """Función de conveniencia para importar ejercicios parseados"""
    return db_manager.batch_import_exercises(exercises, archivo_origen)