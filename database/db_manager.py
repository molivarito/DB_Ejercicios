"""
Modelo de datos para el sistema de gestión de ejercicios
Señales y Sistemas - PUC Chile
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

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
            
            -- Clasificación temática
            unidad_tematica TEXT NOT NULL,
            subtemas TEXT, -- JSON array de subtemas
            
            -- Dificultad y alcance
            nivel_dificultad TEXT CHECK (nivel_dificultad IN ('Básico', 'Intermedio', 'Avanzado', 'Desafío')),
            tiempo_estimado INTEGER, -- en minutos
            prerrequisitos TEXT,
            
            -- Uso pedagógico
            tipo_actividad TEXT, -- JSON array de tipos
            modalidad TEXT CHECK (modalidad IN ('Teórico', 'Computacional', 'Mixto')),
            
            -- Competencias
            objetivos_curso TEXT, -- JSON array de números de objetivos
            competencias_abet TEXT, -- JSON array
            habilidades_especificas TEXT, -- JSON array
            
            -- Contenido
            enunciado TEXT NOT NULL,
            datos_entrada TEXT,
            solucion_completa TEXT,
            respuesta_final TEXT,
            codigo_python TEXT,
            figuras_asociadas TEXT, -- JSON array de paths
            
            -- Variaciones
            versiones_alternativas TEXT,
            parametros_variables TEXT,
            dificultad_escalable BOOLEAN DEFAULT FALSE,
            
            -- Seguimiento
            fecha_ultimo_uso DATE,
            semestre_usado TEXT, -- JSON array
            rendimiento_estudiantes REAL,
            comentarios_docente TEXT,
            
            -- Metadatos
            palabras_clave TEXT, -- JSON array
            estado TEXT DEFAULT 'Listo' CHECK (estado IN ('Listo', 'En revisión', 'Necesita mejoras')),
            conectado_con TEXT, -- JSON array de IDs
            
            -- Campos adicionales
            inspirado_en TEXT,
            extensiones_posibles TEXT,
            errores_comunes TEXT,
            hints TEXT,
            
            -- Timestamps
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla de unidades temáticas (para consistencia)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS unidades_tematicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            orden INTEGER,
            descripcion TEXT
        )
        """)
        
        # Insertar unidades temáticas del programa
        unidades = [
            (1, "Introducción", "Conceptos fundamentales de señales y sistemas"),
            (2, "Sistemas Continuos", "Linealidad, invariancia, convolución"),
            (3, "Transformada de Fourier", "Series y transformada de Fourier continua"),
            (4, "Transformada de Laplace", "Repaso y aplicaciones de Laplace"),
            (5, "Sistemas Discretos", "Muestreo, sistemas de tiempo discreto"),
            (6, "Transformada de Fourier Discreta", "DFT, FFT y consideraciones prácticas"),
            (7, "Transformada Z", "Análisis en el dominio Z")
        ]
        
        cursor.executemany("""
        INSERT OR IGNORE INTO unidades_tematicas (orden, nombre, descripcion) 
        VALUES (?, ?, ?)
        """, unidades)
        
        # Tabla de subtemas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtemas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            unidad_id INTEGER,
            FOREIGN KEY (unidad_id) REFERENCES unidades_tematicas (id)
        )
        """)
        
        # Tabla de historial de uso
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_uso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ejercicio_id INTEGER,
            fecha_uso DATE,
            tipo_actividad TEXT,
            semestre TEXT,
            notas TEXT,
            FOREIGN KEY (ejercicio_id) REFERENCES ejercicios (id)
        )
        """)
        
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
        
        fields = ', '.join(ejercicio_data.keys())
        placeholders = ', '.join(['?' for _ in ejercicio_data])
        
        cursor.execute(f"""
        INSERT INTO ejercicios ({fields}) 
        VALUES ({placeholders})
        """, list(ejercicio_data.values()))
        
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
            if 'unidad_tematica' in filtros:
                conditions.append("unidad_tematica = ?")
                params.append(filtros['unidad_tematica'])
            if 'nivel_dificultad' in filtros:
                conditions.append("nivel_dificultad = ?")
                params.append(filtros['nivel_dificultad'])
            if 'modalidad' in filtros:
                conditions.append("modalidad = ?")
                params.append(filtros['modalidad'])
            if 'estado' in filtros:
                conditions.append("estado = ?")
                params.append(filtros['estado'])
            
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
                if ejercicio[field]:
                    try:
                        ejercicio[field] = json.loads(ejercicio[field])
                    except:
                        ejercicio[field] = []
            ejercicios.append(ejercicio)
        
        conn.close()
        return ejercicios
    
    def obtener_ejercicio_por_id(self, ejercicio_id: int) -> Optional[Dict]:
        """Obtiene un ejercicio específico por ID"""
        ejercicios = self.obtener_ejercicios()
        for ejercicio in ejercicios:
            if ejercicio['id'] == ejercicio_id:
                return ejercicio
        return None
    
    def actualizar_ejercicio(self, ejercicio_id: int, ejercicio_data: Dict) -> bool:
        """Actualiza un ejercicio existente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convertir listas a JSON strings
        for field in ['subtemas', 'tipo_actividad', 'objetivos_curso', 'competencias_abet', 
                     'habilidades_especificas', 'figuras_asociadas', 'semestre_usado', 
                     'palabras_clave', 'conectado_con']:
            if field in ejercicio_data and isinstance(ejercicio_data[field], list):
                ejercicio_data[field] = json.dumps(ejercicio_data[field])
        
        ejercicio_data['fecha_modificacion'] = datetime.now().isoformat()
        
        fields = ', '.join([f"{k} = ?" for k in ejercicio_data.keys()])
        values = list(ejercicio_data.values()) + [ejercicio_id]
        
        cursor.execute(f"""
        UPDATE ejercicios SET {fields} WHERE id = ?
        """, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def obtener_unidades_tematicas(self) -> List[str]:
        """Obtiene la lista de unidades temáticas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM unidades_tematicas ORDER BY orden")
        unidades = [row[0] for row in cursor.fetchall()]
        conn.close()
        return unidades
    
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
        GROUP BY unidad_tematica
        ORDER BY COUNT(*) DESC
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
    
    def registrar_uso(self, ejercicio_id: int, tipo_actividad: str, semestre: str, notas: str = ""):
        """Registra el uso de un ejercicio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Registrar en historial
        cursor.execute("""
        INSERT INTO historial_uso (ejercicio_id, fecha_uso, tipo_actividad, semestre, notas)
        VALUES (?, ?, ?, ?, ?)
        """, (ejercicio_id, datetime.now().date(), tipo_actividad, semestre, notas))
        
        # Actualizar fecha_ultimo_uso en ejercicios
        cursor.execute("""
        UPDATE ejercicios SET fecha_ultimo_uso = ? WHERE id = ?
        """, (datetime.now().date(), ejercicio_id))
        
        conn.commit()
        conn.close()