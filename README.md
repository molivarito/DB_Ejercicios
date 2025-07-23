# DB_Ejercicios - Sistema de Gestión de Ejercicios

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Conda](https://img.shields.io/badge/Conda-Ready-green.svg)](https://conda.io)

## 🎓 Descripción del Proyecto

Sistema desarrollado para el curso **IEE2103 - Señales y Sistemas** de la Pontificia Universidad Católica de Chile. Permite gestionar una base de datos completa de ejercicios y generar automáticamente pruebas, tareas y guías de ejercicios con formato profesional.

**Desarrollado por:** Patricio de la Cuadra  
**Institución:** Departamento de Ingeniería Eléctrica - PUC  
**Curso:** IEE2103 - Señales y Sistemas  

---

## ✅ Estado Actual del Proyecto

### **PROTOTIPO FUNCIONAL COMPLETO** 🚀

El sistema está **operativo** y listo para uso básico. Incluye todas las funcionalidades core implementadas.

**Última actualización:** Julio 2025  
**Versión:** 1.0.0 - Prototipo  

---

## 🏗️ Lo que YA está implementado

### ✅ **Funcionalidades Core**
- [x] **Base de datos SQLite** con estructura completa (32+ campos de metadata)
- [x] **Interfaz web Streamlit** con 6 páginas principales
- [x] **CRUD completo** de ejercicios (Create, Read, Update, Delete)
- [x] **Generador automático de pruebas** con filtros inteligentes
- [x] **Exportación a PDF** con templates LaTeX profesionales
- [x] **Sistema de búsqueda** con filtros múltiples
- [x] **Dashboard con estadísticas** de la base de datos
- [x] **Configuración automática** con conda

### ✅ **Componentes Técnicos**
- [x] **database/db_manager.py**: Gestor completo de base de datos
- [x] **app.py**: Aplicación Streamlit principal (6 páginas)
- [x] **generators/pdf_generator.py**: Generación de PDFs con LaTeX
- [x] **environment.yml**: Entorno conda listo para producción
- [x] **Scripts de setup**: Instalación automatizada (macOS)

### ✅ **Estructura de Datos**
- [x] **7 Unidades temáticas** del programa (Introducción → Transformada Z)
- [x] **4 Niveles de dificultad** (Básico, Intermedio, Avanzado, Desafío)
- [x] **3 Modalidades** (Teórico, Computacional, Mixto)
- [x] **Tracking completo** (fechas de uso, rendimiento, comentarios)
- [x] **Metadatos pedagógicos** (objetivos, competencias ABET, habilidades)

---

## 🔧 Stack Técnico

### **Backend**
- **Python 3.11** (base)
- **SQLite** (base de datos)
- **Pandas** (manipulación de datos)

### **Frontend**
- **Streamlit** (interfaz web)
- **Plotly/Matplotlib** (visualizaciones)

### **Generación de Documentos**
- **PyLaTeX** (generación LaTeX programática)
- **LaTeX** (compilación a PDF)
- **Templates PUC** (branding institucional)

### **Entorno de Desarrollo**
- **Conda** (gestión de entornos)
- **macOS** (desarrollo)
- **VSCode** (IDE)
- **Git/GitHub** (control de versiones)

---

## 🚀 Instalación y Uso

### **Instalación Rápida (macOS)**
```bash
# Clonar repositorio
git clone https://github.com/molivarito/DB_Ejercicios.git
cd DB_Ejercicios

# Configuración automática
chmod +x setup_conda.sh
./setup_conda.sh

# O manual
conda env create -f environment.yml
conda activate ejercicios-sys
streamlit run app.py
```

### **Uso del Sistema**
1. **Agregar Ejercicios**: Formulario completo con todos los metadatos
2. **Buscar/Filtrar**: Por unidad, dificultad, modalidad, texto libre
3. **Generar Pruebas**: Selección automática o manual con vista previa
4. **Exportar PDFs**: Formato profesional PUC con/sin soluciones
5. **Ver Estadísticas**: Dashboard con métricas de uso

---

## 📊 Funcionalidades Principales

### 🏠 **Dashboard**
- Métricas generales de la base de datos
- Distribución por unidades temáticas
- Ejercicios agregados recientemente
- Estadísticas de uso

### ➕ **Agregar Ejercicio**
- Formulario completo con validación
- 32+ campos de metadata
- Soporte para LaTeX math
- Categorización automática

### 🔍 **Buscar Ejercicios**
- Filtros por unidad, dificultad, modalidad
- Búsqueda por texto en título/contenido
- Vista de detalles expandible
- Opciones de edición

### 🎯 **Generar Prueba**
- Criterios de selección inteligentes
- Distribución automática de dificultad
- Vista previa en tiempo real
- Configuración de tiempo y formato

### 📄 **Exportación**
- PDFs con formato institucional PUC
- Versiones con y sin soluciones
- Templates LaTeX personalizables
- Branding automático

### 📊 **Estadísticas**
- Distribuciones por categorías
- Ejercicios más utilizados
- Métricas de rendimiento
- Visualizaciones interactivas

---

## 🗂️ Estructura del Proyecto

```
DB_Ejercicios/
├── app.py                     # Aplicación Streamlit principal
├── environment.yml            # Entorno conda
├── requirements.txt           # Dependencias pip (backup)
├── setup_conda.sh            # Script de instalación macOS
├── .gitignore                # Archivos ignorados por Git
├── README.md                 # Este archivo
├── database/
│   ├── db_manager.py         # Gestor de base de datos
│   └── ejercicios.db         # Base de datos SQLite (auto-generada)
├── generators/
│   └── pdf_generator.py      # Generación de PDFs
├── output/                   # PDFs y documentos generados
├── templates/                # Templates LaTeX
├── static/
│   └── images/              # Imágenes para ejercicios
└── utils/                   # Utilidades auxiliares
```

---

## 🚧 Próximos Pasos Identificados

### **Prioridad Alta** 🔴
1. **Importador de ejercicios existentes** desde archivos LaTeX/PDF
2. **Templates PDF personalizados** según formato específico del profesor
3. **Funcionalidades específicas** basadas en workflow real

### **Prioridad Media** 🟡
4. **Sistema de versionado** de ejercicios
5. **Exportador a múltiples formatos** (Word, Moodle XML)
6. **Analytics avanzados** de rendimiento estudiantil

### **Prioridad Baja** 🟢
7. **Integración con Canvas LMS**
8. **Colaboración multi-usuario**
9. **API REST** para integraciones

---

## 💡 Decisiones de Diseño Tomadas

### **Tecnológicas**
- ✅ **Conda sobre pip**: Mejor gestión de dependencias científicas
- ✅ **SQLite sobre PostgreSQL**: Simplicidad y portabilidad
- ✅ **Streamlit sobre Flask**: Rapidez de desarrollo y prototipado
- ✅ **PyLaTeX sobre reportlab**: Control completo del formato LaTeX

### **Arquitecturales**
- ✅ **No usar Notion**: Mantener simplicidad y control total
- ✅ **Base de datos local**: No requiere servidor, fácil backup
- ✅ **Interfaz web**: Accesible desde cualquier navegador
- ✅ **Modular**: Componentes independientes y extensibles

### **Pedagógicas**
- ✅ **32+ campos de metadata**: Clasificación pedagógica completa
- ✅ **7 unidades temáticas**: Alineado con programa IEE2103
- ✅ **Tracking de uso**: Para optimización basada en datos
- ✅ **Formato PUC**: Branding y estándares institucionales

---

## 🐛 Issues Conocidos

- **LaTeX requerido**: Generación de PDFs requiere LaTeX instalado
- **Ejercicios de ejemplo**: Solo 3 ejercicios demo (necesita población real)
- **Templates básicos**: PDFs funcionales pero pueden mejorarse estéticamente

---

## 📞 Para Nuevo Chat con Claude

**Copiar y pegar esto:**

> Hola Claude! Estoy trabajando en **DB_Ejercicios** (repo: https://github.com/molivarito/DB_Ejercicios.git). 
> 
> Es un sistema de gestión de ejercicios para mi curso **IEE2103 - Señales y Sistemas** en la PUC. 
> 
> **Estado actual**: PROTOTIPO FUNCIONAL completo con Streamlit + SQLite + PyLaTeX.
> 
> Por favor revisa el README.md del repo para entender el contexto completo del proyecto.
> 
> **Hoy quiero trabajar en**: [ESPECIFICAR AQUÍ LA TAREA CONCRETA]

---

## 🤝 Contribución y Desarrollo

### **Para Ayudantes/Colaboradores**
1. Fork del repositorio
2. Crear rama para nueva funcionalidad
3. Desarrollar y testear
4. Pull request con descripción detallada

### **Para Reportar Issues**
- Usar GitHub Issues con template
- Incluir pasos para reproducir
- Adjuntar logs si es necesario

---

## 📜 Licencia

Desarrollado para uso académico en la Pontificia Universidad Católica de Chile.  
Ver términos específicos de uso institucional.

---

**Contacto**: Patricio de la Cuadra - pcuadra@uc.cl  
**Departamento**: Ingeniería Eléctrica - PUC  
**Última actualización**: Julio 2025