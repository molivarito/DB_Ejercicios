"""
DatabaseManager mínimo para testing
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "database/ejercicios.db"):
        self.db_path = db_path
        self.conn = None
        
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas básicas"""
        return {
            'total_ejercicios': 324,
            'por_unidad': {'Sistemas Continuos': 50, 'Transformada de Fourier': 45},
            'por_dificultad': {'Básico': 100, 'Intermedio': 150, 'Avanzado': 74},
            'por_modalidad': {'Teórico': 200, 'Computacional': 124}
        }
    
    def obtener_ejercicios(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """Retorna lista de ejercicios"""
        # Datos de prueba
        return [
            {
                'id': 1,
                'titulo': 'Convolución básica',
                'enunciado': 'Calcule la convolución y(t) = x(t) * h(t)',
                'unidad_tematica': 'Sistemas Continuos',
                'nivel_dificultad': 'Básico',
                'modalidad': 'Teórico',
                'tiempo_estimado': 15,
                'puntos': 6,
                'solucion_completa': 'Solución de ejemplo'
            }
        ]
    
    def obtener_unidades_tematicas(self) -> List[str]:
        """Retorna lista de unidades"""
        return [
            "Introducción",
            "Sistemas Continuos", 
            "Transformada de Fourier",
            "Transformada de Laplace",
            "Sistemas Discretos",
            "Transformada de Fourier Discreta",
            "Transformada Z"
        ]
