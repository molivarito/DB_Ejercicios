# CONTEXT.md - DB_Ejercicios

## 🎯 Resumen Ejecutivo
**Patricio de la Cuadra** (profesor PUC) desarrollando sistema de gestión de ejercicios para **IEE2103 - Señales y Sistemas**.

**Estado**: PROTOTIPO FUNCIONAL COMPLETO ✅  
**Repo**: https://github.com/molivarito/DB_Ejercicios  
**Tecnologías**: Python + Conda + Streamlit + SQLite + PyLaTeX  

---

## 🏗️ Arquitectura del Sistema

### **Stack Completo**
- **Backend**: Python 3.11 + SQLite + Pandas
- **Frontend**: Streamlit (6 páginas)
- **Documentos**: PyLaTeX → PDF
- **Entorno**: Conda (environment.yml)
- **OS**: macOS + VSCode

### **Componentes Principales**
```
app.py                    # Streamlit app (Dashboard, CRUD, Generador)
database/db_manager.py    # SQLite con 32+ campos de metadata
generators/pdf_generator.py # LaTeX → PDF con branding PUC
environment.yml           # Conda environment listo
setup_conda.sh           # Script instalación macOS
```

---

## ✅ Lo Implementado (FUNCIONA)

### **Funcionalidades Core**
- ✅ **CRUD completo** de ejercicios con 32+ campos
- ✅ **Generador automático** de pruebas con filtros
- ✅ **Exportación PDF** con templates LaTeX PUC
- ✅ **Dashboard** con estadísticas y visualizaciones
- ✅ **Búsqueda avanzada** por múltiples criterios
- ✅ **Base de datos** SQLite con estructura pedagógica completa

### **Datos Estructurados**
- ✅ **7 unidades temáticas** (Introducción → Transformada Z)
- ✅ **4 niveles dificultad** (Básico → Desafío)
- ✅ **3 modalidades** (Teórico, Computacional, Mixto)
- ✅ **Tracking completo** (uso, rendimiento, comentarios)
- ✅ **Metadatos pedagógicos** (objetivos curso, competencias ABET)

---

## 🚧 Próximos Pasos (Priorizada)

### **🔴 Alta Prioridad**
1. **Importador LaTeX**: Parser para ejercicios existentes del profesor
2. **Templates PDF**: Personalizar formato según necesidades específicas
3. **Población datos**: Cargar ejercicios reales del curso

### **🟡 Media Prioridad**
4. **Versionado**: Sistema de backup y control de versiones
5. **Multi-formato**: Export a Word, Moodle XML, etc.
6. **UX/UI**: Refinamientos de usabilidad

### **🟢 Baja Prioridad**
7. **Analytics**: Rendimiento estudiantil avanzado
8. **Integración**: Canvas LMS, APIs externas
9. **Colaboración**: Multi-usuario, permisos

---

## 💡 Decisiones Importantes Tomadas

### **Tecnológicas**
- ✅ **Conda > pip**: Dependencias científicas más estables
- ✅ **SQLite > PostgreSQL**: Simplicidad, portabilidad, sin servidor
- ✅ **Streamlit > Flask**: Prototipado rápido, menos código
- ✅ **PyLaTeX > reportlab**: Control total formato académico

### **Arquitecturales**
- ✅ **No Notion**: Mantener control total y simplicidad
- ✅ **Local-first**: Base datos local, fácil backup
- ✅ **Modular**: Componentes independientes y extensibles
- ✅ **Pedagógico**: Estructura alineada con programa IEE2103

---

## 🔄 Workflow de Desarrollo

### **Entorno**
```bash
conda activate ejercicios-sys
streamlit run app.py
# → http://localhost:8501
```

### **Git Flow**
```bash
git add .
git commit -m "feat: descripción clara de cambios"
git push origin main
```

### **Issues GitHub**
- Usar templates definidos
- Labels por prioridad y tipo
- Criterios de aceptación claros

---

## 🎓 Contexto Pedagógico

### **Curso IEE2103 - Señales y Sistemas**
- **Universidad**: Pontificia Universidad Católica de Chile
- **Profesor**: Patricio de la Cuadra (pcuadra@uc.cl)
- **Semestre típico**: 2024-2
- **Evaluaciones**: 4 interrogaciones + tareas + controles + examen

### **Unidades del Curso**
1. Introducción (señales, sistemas, causalidad)
2. Sistemas Continuos (linealidad, convolución)
3. Transformada de Fourier (series, propiedades)
4. Transformada de Laplace (repaso, aplicaciones)
5. Sistemas Discretos (muestreo, Nyquist)
6. DFT (FFT, consideraciones prácticas)
7. Transformada Z (estabilidad, polos/ceros)

---

## 🐛 Limitaciones Conocidas

- **LaTeX requerido**: PDFs necesitan LaTeX instalado
- **Ejercicios demo**: Solo 3 ejercicios ejemplo (necesita población)
- **Templates básicos**: Funcionales pero mejorables estéticamente
- **Sin auth**: Sistema single-user (no multi-usuario aún)

---

## 📞 Template para Nuevo Chat

```
Hola Claude! Trabajando en DB_Ejercicios (https://github.com/molivarito/DB_Ejercicios.git).

Sistema gestión ejercicios para IEE2103 - Señales y Sistemas (PUC).
Estado: PROTOTIPO FUNCIONAL con Streamlit + SQLite + PyLaTeX.

Revisa README.md del repo para contexto completo.

Hoy quiero: [ESPECIFICAR TAREA CONCRETA]
```

---

## 🎯 Frases Clave para Claude

- **"Prototipo funcional completo"** = Todo lo básico implementado y operativo
- **"Población de datos"** = Cargar ejercicios reales del profesor
- **"Templates PUC"** = Branding y formato institucional específico
- **"Importador LaTeX"** = Parser para ejercicios existentes
- **"Metadatos pedagógicos"** = Campos específicos para clasificación educativa

---

**Última actualización**: Julio 2025  
**Mantenedor**: Patricio de la Cuadra  
**Estado del proyecto**: FUNCIONAL y listo para siguiente fase