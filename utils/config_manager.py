"""
Manejador de Configuración
Sistema de Gestión de Ejercicios - Señales y Sistemas
"""

import json
from pathlib import Path
from typing import Dict

class ConfigManager:
    """Gestiona la carga y guardado de la configuración de la app en un archivo JSON."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.default_config = {
            "profile": {
                "professor_name": "Patricio de la Cuadra",
                "course_name": "IEE2103 - Señales y Sistemas",
                "university_name": "Pontificia Universidad Católica de Chile",
                "current_semester": "2025-1",
                "email": "pcuadra@uc.cl"
            },
            "app": {
                "language": "Español"
            }
        }

    def load_config(self) -> Dict:
        if not self.config_path.exists():
            self.save_config(self.default_config)
            return self.default_config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_config(self, config_data: Dict):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)