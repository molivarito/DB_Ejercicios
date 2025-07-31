"""
DatabaseManager funcional completo para el sistema
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path: str = "database/ejercicios.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla principal de ejercicios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ejercicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            fuente TEXT,
            año_creacion INTEGER,
            unidad_tematica TEXT NOT NULL,
            subtemas TEXT,
            nivel_dificultad TEXT,
            tiempo_estimado INTEGER,
            prerrequisitos TEXT,
            tipo_actividad TEXT,
            modalidad TEXT,
            objetivos_curso TEXT,
            competencias_abet TEXT,
            habilidades_especificas TEXT,
            enunciado TEXT NOT NULL,
            datos_entrada TEXT,
            solucion_completa TEXT,
            respuesta_final TEXT,
            codigo_python TEXT,
            figuras_asociadas TEXT,
            imagen_path TEXT,
            solucion_imagen_path TEXT,
            versiones_alternativas TEXT,
            parametros_variables TEXT,
            dificultad_escalable BOOLEAN DEFAULT FALSE,
            fecha_ultimo_uso DATE,
            semestre_usado TEXT,
            rendimiento_estudiantes REAL,
            comentarios_docente TEXT,
            palabras_clave TEXT,
            estado TEXT DEFAULT 'Listo',
            conectado_con TEXT,
            inspirado_en TEXT,
            extensiones_posibles TEXT,
            errores_comunes TEXT,
            hints TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Para compatibilidad con bases de datos existentes, agregar la columna si no existe
        try:
            cursor.execute("ALTER TABLE ejercicios ADD COLUMN imagen_path TEXT;")
        except sqlite3.OperationalError:
            # La columna ya existe, no hay problema
            pass
        
        try:
            cursor.execute("ALTER TABLE ejercicios ADD COLUMN solucion_imagen_path TEXT;")
        except sqlite3.OperationalError:
            # La columna ya existe, no hay problema
            pass

        conn.commit()
        conn.close()
    
    def agregar_ejercicio(self, ejercicio_data: Dict) -> int:
        """Agrega un nuevo ejercicio a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convertir listas a JSON strings
        for field in ['subtemas', 'tipo_actividad', 'objetivos_curso', 'competencias_abet', 
                     'habilidades_especificas', 'figuras_asociadas', 'semestre_usado', 
                     'palabras_clave', 'conectado_con']:
            if field in ejercicio_data and isinstance(ejercicio_data[field], list):
                ejercicio_data[field] = json.dumps(ejercicio_data[field])
        
        # Preparar campos y valores
        fields = list(ejercicio_data.keys())
        values = list(ejercicio_data.values())
        placeholders = ','.join(['?' for _ in fields])
        fields_str = ','.join(fields)
        
        cursor.execute(f"INSERT INTO ejercicios ({fields_str}) VALUES ({placeholders})", values)
        
        ejercicio_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return ejercicio_id
    
    def obtener_ejercicios(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """Obtiene ejercicios con filtros opcionales"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM ejercicios"
        params = []
        
        if filtros:
            conditions = []
            if 'unidad_tematica' in filtros and filtros['unidad_tematica']:
                conditions.append("unidad_tematica = ?")
                params.append(filtros['unidad_tematica'])
            if 'nivel_dificultad' in filtros and filtros['nivel_dificultad']:
                conditions.append("nivel_dificultad = ?")
                params.append(filtros['nivel_dificultad'])
            if 'modalidad' in filtros and filtros['modalidad']:
                conditions.append("modalidad = ?")
                params.append(filtros['modalidad'])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY fecha_creacion DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        ejercicios = []
        for row in rows:
            ejercicio = dict(row)
            # Convertir JSON strings de vuelta a listas
            for field in ['subtemas', 'tipo_actividad', 'objetivos_curso', 'competencias_abet', 
                         'habilidades_especificas', 'figuras_asociadas', 'semestre_usado', 
                         'palabras_clave', 'conectado_con']:
                if ejercicio.get(field):
                    try:
                        ejercicio[field] = json.loads(ejercicio[field])
                    except:
                        ejercicio[field] = []
            ejercicios.append(ejercicio)
        
        conn.close()
        return ejercicios
    
    def obtener_ejercicio_por_id(self, ejercicio_id: int) -> Optional[Dict]:
        """Obtiene un ejercicio específico por ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ejercicios WHERE id = ?", (ejercicio_id,))
        row = cursor.fetchone()
        
        if row:
            ejercicio = dict(row)
            # Convertir JSON strings
            for field in ['subtemas', 'tipo_actividad', 'objetivos_curso', 'competencias_abet', 
                         'habilidades_especificas', 'figuras_asociadas', 'semestre_usado', 
                         'palabras_clave', 'conectado_con']:
                if ejercicio.get(field):
                    try:
                        ejercicio[field] = json.loads(ejercicio[field])
                    except:
                        ejercicio[field] = []
            conn.close()
            return ejercicio
        
        conn.close()
        return None
    
    def actualizar_ejercicio(self, ejercicio_id: int, ejercicio_data: Dict) -> bool:
        """Actualiza un ejercicio existente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convertir listas a JSON
        for field in ['subtemas', 'tipo_actividad', 'objetivos_curso', 'competencias_abet', 
                     'habilidades_especificas', 'figuras_asociadas', 'semestre_usado', 
                     'palabras_clave', 'conectado_con']:
            if field in ejercicio_data and isinstance(ejercicio_data[field], list):
                ejercicio_data[field] = json.dumps(ejercicio_data[field])
        
        ejercicio_data['fecha_modificacion'] = datetime.now().isoformat()
        
        fields = ', '.join([f"{k} = ?" for k in ejercicio_data.keys()])
        values = list(ejercicio_data.values()) + [ejercicio_id]
        
        cursor.execute(f"UPDATE ejercicios SET {fields} WHERE id = ?", values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas generales de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de ejercicios
        cursor.execute("SELECT COUNT(*) FROM ejercicios")
        total_ejercicios = cursor.fetchone()[0]
        
        # Por unidad temática
        cursor.execute("""
        SELECT unidad_tematica, COUNT(*) 
        FROM ejercicios 
        WHERE unidad_tematica IS NOT NULL
        GROUP BY unidad_tematica
        """)
        por_unidad = dict(cursor.fetchall())
        
        # Por dificultad
        cursor.execute("""
        SELECT nivel_dificultad, COUNT(*) 
        FROM ejercicios 
        WHERE nivel_dificultad IS NOT NULL
        GROUP BY nivel_dificultad
        """)
        por_dificultad = dict(cursor.fetchall())
        
        # Por modalidad
        cursor.execute("""
        SELECT modalidad, COUNT(*) 
        FROM ejercicios 
        WHERE modalidad IS NOT NULL
        GROUP BY modalidad
        """)
        por_modalidad = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_ejercicios': total_ejercicios,
            'por_unidad': por_unidad,
            'por_dificultad': por_dificultad,
            'por_modalidad': por_modalidad
        }
    
    def obtener_unidades_tematicas(self) -> List[str]:
        """Obtiene la lista de unidades temáticas únicas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT DISTINCT unidad_tematica 
        FROM ejercicios 
        WHERE unidad_tematica IS NOT NULL 
        ORDER BY unidad_tematica
        """)
        
        unidades = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Si no hay unidades, retornar lista por defecto
        if not unidades:
            unidades = [
                "Introducción",
                "Sistemas Continuos",
                "Transformada de Fourier",
                "Transformada de Laplace",
                "Sistemas Discretos",
                "Transformada de Fourier Discreta",
                "Transformada Z"
            ]
        
        return unidades
    
    def registrar_uso(self, ejercicio_id: int, tipo_actividad: str, semestre: str, notas: str = ""):
        """Registra el uso de un ejercicio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Actualizar fecha_ultimo_uso
        cursor.execute("""
        UPDATE ejercicios 
        SET fecha_ultimo_uso = ? 
        WHERE id = ?
        """, (datetime.now().date(), ejercicio_id))
        
        conn.commit()
        conn.close()
    
    # Métodos adicionales para importación
    def batch_import_exercises(self, exercises: List[Dict], archivo_origen: str = '', usuario: str = 'Sistema') -> Dict:
        """Importa múltiples ejercicios"""
        imported = 0
        errors = []
        
        for exercise in exercises:
            try:
                self.agregar_ejercicio(exercise)
                imported += 1
            except Exception as e:
                errors.append(str(e))
        
        return {
            'imported': imported,
            'errors': errors
        }
