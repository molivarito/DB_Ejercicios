#!/bin/bash
# Script de configuración para conda - Sistema de Gestión de Ejercicios
# Señales y Sistemas - PUC Chile

echo "======================================================"
echo "🎓 Sistema de Gestión de Ejercicios - Señales y Sistemas"
echo "   Pontificia Universidad Católica de Chile"
echo "======================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar que conda esté instalado
check_conda() {
    if command -v conda &> /dev/null; then
        CONDA_VERSION=$(conda --version)
        print_success "Conda encontrado: $CONDA_VERSION"
        return 0
    else
        print_error "Conda no encontrado"
        echo "Por favor instala Anaconda o Miniconda:"
        echo "- Anaconda: https://www.anaconda.com/products/individual"
        echo "- Miniconda: https://docs.conda.io/en/latest/miniconda.html"
        return 1
    fi
}

# Verificar LaTeX
check_latex() {
    if command -v pdflatex &> /dev/null; then
        print_success "LaTeX encontrado"
        return 0
    else
        print_warning "LaTeX no encontrado"
        echo "La generación de PDFs no funcionará completamente."
        echo "Para instalar LaTeX:"
        echo "- macOS: brew install --cask mactex"
        echo "- Linux: sudo apt-get install texlive-full"
        echo "- Windows: Instalar MiKTeX desde https://miktex.org/"
        return 1
    fi
}

# Crear entorno conda
create_environment() {
    echo ""
    echo "🐍 Configurando entorno conda..."
    
    if conda env list | grep -q "ejercicios-sys"; then
        print_warning "El entorno 'ejercicios-sys' ya existe"
        read -p "¿Quieres actualizarlo? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            conda env update -f environment.yml
            print_success "Entorno actualizado"
        else
            print_info "Usando entorno existente"
        fi
    else
        conda env create -f environment.yml
        print_success "Entorno 'ejercicios-sys' creado"
    fi
}

# Inicializar base de datos
init_database() {
    echo ""
    echo "🗄️  Inicializando base de datos..."
    
    # Activar entorno y ejecutar script de Python
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate ejercicios-sys
    
    python -c "
import sqlite3
import os
from pathlib import Path

# Crear directorios
Path('database').mkdir(exist_ok=True)
Path('output').mkdir(exist_ok=True)
Path('templates').mkdir(exist_ok=True)

# Crear base de datos
conn = sqlite3.connect('database/ejercicios.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS ejercicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    unidad_tematica TEXT,
    nivel_dificultad TEXT,
    enunciado TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Ejercicios de ejemplo
ejercicios = [
    ('Convolución de señales rectangulares', 'Sistemas Continuos', 'Básico', 
     'Calcule la convolución y(t) = x(t) * h(t) donde x(t) y h(t) son señales rectangulares.'),
    ('FFT de señal con ruido', 'Transformada de Fourier Discreta', 'Intermedio',
     'Implemente en Python el cálculo de la FFT de una señal sinusoidal con ruido.'),
    ('Análisis de estabilidad', 'Transformada Z', 'Avanzado',
     'Analice la estabilidad del sistema usando la transformada Z.')
]

cursor.executemany('''
INSERT OR IGNORE INTO ejercicios (titulo, unidad_tematica, nivel_dificultad, enunciado)
VALUES (?, ?, ?, ?)
''', ejercicios)

conn.commit()
conn.close()
print('Base de datos inicializada')
"
    
    if [ $? -eq 0 ]; then
        print_success "Base de datos inicializada con ejercicios de ejemplo"
    else
        print_error "Error inicializando base de datos"
        return 1
    fi
}

# Función principal
main() {
    # Verificaciones del sistema
    check_conda || exit 1
    check_latex
    
    echo ""
    print_info "Iniciando configuración..."
    
    # Crear entorno
    create_environment || exit 1
    
    # Inicializar base de datos
    read -p "¿Inicializar base de datos con ejercicios de ejemplo? (Y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        init_database || exit 1
    fi
    
    echo ""
    print_success "¡Configuración completada!"
    echo ""
    echo "Para usar el sistema:"
    echo "1. Activar entorno: conda activate ejercicios-sys"
    echo "2. Lanzar aplicación: streamlit run app.py"
    echo ""
    
    # Ofrecer lanzar inmediatamente
    read -p "¿Lanzar la aplicación ahora? (Y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "🚀 Lanzando aplicación..."
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate ejercicios-sys
        streamlit run app.py
    fi
}

# Verificar que el archivo environment.yml existe
if [ ! -f "environment.yml" ]; then
    print_error "Archivo environment.yml no encontrado"
    echo "Asegúrate de estar en el directorio correcto del proyecto"
    exit 1
fi

# Ejecutar función principal
main