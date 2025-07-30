"""
Database Cleanup Manager - Funciones para limpiar y resetear la BD
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import sqlite3
import os
import shutil
from datetime import datetime
from typing import Dict, List
import streamlit as st


class DatabaseCleanupManager:
    """Gestor de limpieza y reset de base de datos"""
    
    def __init__(self, db_path: str = "database/ejercicios.db"):
        self.db_path = db_path
        self.backup_dir = "database/backups"
        
        # Crear directorio de backups si no existe
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def get_database_stats(self) -> Dict:
        """Obtiene estadísticas actuales de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de ejercicios
            cursor.execute("SELECT COUNT(*) FROM ejercicios")
            total_exercises = cursor.fetchone()[0]
            
            # Por unidad temática
            cursor.execute("""
                SELECT unidad_tematica, COUNT(*) 
                FROM ejercicios 
                WHERE unidad_tematica IS NOT NULL
                GROUP BY unidad_tematica
                ORDER BY COUNT(*) DESC
            """)
            by_unit = dict(cursor.fetchall())
            
            # Por dificultad
            cursor.execute("""
                SELECT nivel_dificultad, COUNT(*) 
                FROM ejercicios 
                WHERE nivel_dificultad IS NOT NULL
                GROUP BY nivel_dificultad
            """)
            by_difficulty = dict(cursor.fetchall())
            
            # Ejercicios sin solución
            cursor.execute("""
                SELECT COUNT(*) FROM ejercicios 
                WHERE solucion_completa IS NULL OR solucion_completa = ''
            """)
            no_solution = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_exercises': total_exercises,
                'by_unit': by_unit,
                'by_difficulty': by_difficulty,
                'no_solution': no_solution,
                'db_size': self._get_file_size_mb(self.db_path)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def create_backup(self, backup_name: str = None) -> str:
        """Crea backup de la base de datos actual"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"ejercicios_backup_{timestamp}.db"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copy2(self.db_path, backup_path)
            return backup_path
        except Exception as e:
            raise Exception(f"Error creando backup: {str(e)}")
    
    def clear_all_exercises(self) -> bool:
        """Elimina TODOS los ejercicios de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Eliminar todos los ejercicios
            cursor.execute("DELETE FROM ejercicios")
            
            # Resetear el contador autoincrement
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='ejercicios'")
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error limpiando base de datos: {str(e)}")
    
    def clear_exercises_by_pattern(self, pattern_used: str) -> int:
        """Elimina ejercicios por patrón específico"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Contar ejercicios que se van a eliminar
            cursor.execute("SELECT COUNT(*) FROM ejercicios WHERE pattern_used = ?", (pattern_used,))
            count = cursor.fetchone()[0]
            
            # Eliminar ejercicios con ese patrón
            cursor.execute("DELETE FROM ejercicios WHERE pattern_used = ?", (pattern_used,))
            
            conn.commit()
            conn.close()
            
            return count
            
        except Exception as e:
            raise Exception(f"Error eliminando ejercicios: {str(e)}")
    
    def clear_exercises_by_source(self, source: str) -> int:
        """Elimina ejercicios por fuente específica"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Contar ejercicios que se van a eliminar
            cursor.execute("SELECT COUNT(*) FROM ejercicios WHERE fuente LIKE ?", (f"%{source}%",))
            count = cursor.fetchone()[0]
            
            # Eliminar ejercicios de esa fuente
            cursor.execute("DELETE FROM ejercicios WHERE fuente LIKE ?", (f"%{source}%",))
            
            conn.commit()
            conn.close()
            
            return count
            
        except Exception as e:
            raise Exception(f"Error eliminando ejercicios: {str(e)}")
    
    def recreate_database(self) -> bool:
        """Elimina y recrea completamente la base de datos"""
        try:
            # Eliminar archivo de BD si existe
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            
            # Crear nueva BD vacía
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager(self.db_path)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error recreando base de datos: {str(e)}")
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restaura BD desde un backup"""
        try:
            if not os.path.exists(backup_path):
                raise Exception("Archivo de backup no encontrado")
            
            shutil.copy2(backup_path, self.db_path)
            return True
            
        except Exception as e:
            raise Exception(f"Error restaurando backup: {str(e)}")
    
    def list_backups(self) -> List[Dict]:
        """Lista todos los backups disponibles"""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(self.backup_dir, filename)
                size_mb = self._get_file_size_mb(filepath)
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size_mb': size_mb,
                    'modified': modified
                })
        
        # Ordenar por fecha de modificación (más reciente primero)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        return backups
    
    def _get_file_size_mb(self, filepath: str) -> float:
        """Obtiene el tamaño de archivo en MB"""
        try:
            size_bytes = os.path.getsize(filepath)
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0.0