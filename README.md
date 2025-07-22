# Sistema de Gestión de Ejercicios - Señales y Sistemas

## 📋 Descripción

Sistema desarrollado para el curso IEE2103 - Señales y Sistemas de la Pontificia Universidad Católica de Chile. Permite gestionar una base de datos de ejercicios y generar pruebas automáticamente.

## 🚀 Instalación

### Requisitos Previos

1. **Python 3.8 o superior**
2. **LaTeX** (para generación de PDFs)
   - En Windows: MiKTeX o TeX Live
   - En macOS: MacTeX
   - En Linux: `sudo apt-get install texlive-full`

## 🚀 Instalación

### Requisitos Previos

1. **Anaconda o Miniconda** (recomendado)
   - Anaconda: https://www.anaconda.com/products/individual
   - Miniconda: https://docs.conda.io/en/latest/miniconda.html
   
2. **Alternativamente: Python 3.8 o superior** (si no usas conda)

3. **LaTeX** (para generación de PDFs)
   - En Windows: MiKTeX o TeX Live
   - En macOS: MacTeX (`brew install --cask mactex`)
   - En Linux: `sudo apt-get install texlive-full`

### Instalación Rápida con Conda

#### Opción 1: Script Automático (Recomendado)

**En macOS/Linux:**
```bash
# Dar permisos de ejecución
chmod +x setup_conda.sh

# Ejecutar script
./setup_conda.sh
```

**En Windows:**
```cmd
# Ejecutar desde Command Prompt o PowerShell
setup_conda.bat
```

#### Opción 2: Manual con Conda

```bash
# Crear entorno desde archivo
conda env create -f environment.yml

# Activar entorno
conda activate ejercicios-sys

# Verificar instalación
conda list

# Ejecutar aplicación
streamlit run app.py
```

## 📁 Estructura del Proyecto

```
ejercicios_sys/
├── app.py                 # Aplicación principal Streamlit
├── database/
│   ├── db_manager.py     # Gestor de base de datos
│   └── ejercicios.db     # Base de datos SQLite (se crea automáticamente)
├── generators/
│   └── pdf_generator.py  # Generador de PDFs
├── output/               # Archivos generados
├── templates/            # Templates LaTeX
└── README.md            # Este archivo
```

## 🎯 Uso del Sistema

### Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### Funcionalidades Principales

#### 1. Dashboard 🏠
- Vista general de la base de datos
- Estadísticas de ejercicios
- Accesos rápidos

#### 2. Agregar Ejercicio ➕
- Formulario completo para nuevos ejercicios
- Campos para todos los metadatos definidos
- Validación de datos

#### 3. Buscar Ejercicios 🔍
- Filtros múltiples por unidad, dificultad, modalidad
- Búsqueda por texto
- Vista de detalles de ejercicios

#### 4. Generar Prueba 🎯
- Selección automática o manual de ejercicios
- Configuración de parámetros de la prueba
- Vista previa en tiempo real
- Exportación a PDF y LaTeX

#### 5. Estadísticas 📊
- Distribuciones por categorías
- Ejercicios más utilizados
- Métricas de uso

#### 6. Configuración ⚙️
- Configuración del sistema
- Backup y restauración
- Personalización de templates

## 🗄️ Base de Datos

### Campos Principales

- **Identificación**: ID, título, fuente, año
- **Clasificación**: unidad temática, subtemas, dificultad
- **Contenido**: enunciado, solución, código Python
- **Pedagógico**: tipo de actividad, modalidad, objetivos
- **Seguimiento**: fechas de uso, rendimiento

### Unidades Temáticas

1. Introducción
2. Sistemas Continuos
3. Transformada de Fourier
4. Transformada de Laplace
5. Sistemas Discretos
6. Transformada de Fourier Discreta
7. Transformada Z

## 📄 Generación de Documentos

### Formatos Disponibles

- **PDF**: Pruebas y guías listas para imprimir
- **LaTeX**: Código fuente editable
- **Soluciones**: PDF separado con soluciones

### Personalización

Los documentos incluyen:
- Logo y branding de la PUC
- Formato estándar de pruebas
- Numeración automática
- Espacios para respuestas

## 🔧 Desarrollo y Extensión

### Agregar Nuevas Funcionalidades

1. **Importadores**: Agregar parsers para otros formatos
2. **Exportadores**: Nuevos formatos de salida
3. **Filtros**: Criterios adicionales de búsqueda
4. **Analytics**: Métricas avanzadas de uso

### Estructura de Código

```python
# Ejemplo de extensión - Nuevo filtro
def filtrar_por_tiempo(ejercicios, tiempo_min, tiempo_max):
    return [e for e in ejercicios 
            if tiempo_min <= e.get('tiempo_estimado', 0) <= tiempo_max]
```

## 📊 Ejemplos de Uso

### Crear una Prueba Automática

1. Ir a "Generar Prueba"
2. Seleccionar unidades: "Sistemas Continuos", "Transformada de Fourier"
3. Configurar: 4 ejercicios, 90 minutos, distribución balanceada
4. Generar y descargar PDF

### Agregar Ejercicio Nuevo

1. Ir a "Agregar Ejercicio"
2. Completar información básica y contenido
3. Asignar metadatos pedagógicos
4. Guardar en la base de datos

### Buscar Ejercicios Específicos

1. Ir a "Buscar Ejercicios"
2. Aplicar filtros: Unidad = "DFT", Dificultad = "Intermedio"
3. Revisar resultados y seleccionar

## 🔄 Flujo de Trabajo Recomendado

### Para Preparar una Prueba

1. **Planificación**: Definir objetivos y contenidos
2. **Selección**: Usar filtros para encontrar ejercicios apropiados
3. **Generación**: Crear prueba con vista previa
4. **Revisión**: Verificar contenido y formato
5. **Exportación**: Generar PDF final
6. **Registro**: Marcar ejercicios como usados

### Para Gestión Semestral

1. **Inicio**: Importar ejercicios de semestres anteriores
2. **Desarrollo**: Agregar nuevos ejercicios durante el semestre
3. **Uso**: Generar pruebas y materiales según calendario
4. **Análisis**: Revisar estadísticas de uso y efectividad
5. **Backup**: Crear respaldos regulares

## 🛠️ Troubleshooting

### Problemas Comunes

#### LaTeX no encontrado
```bash
# Verificar instalación
pdflatex --version

# En caso de error, reinstalar LaTeX
```

#### Error de base de datos
- Verificar permisos de escritura en directorio `database/`
- Eliminar `ejercicios.db` para reinicializar

#### Problemas de renderizado
- Actualizar navegador
- Limpiar caché de Streamlit: `streamlit cache clear`

#### Caracteres especiales en LaTeX
- Usar `\textbackslash{}` para backslashes
- Escapar caracteres especiales: `\# Sistema de Gestión de Ejercicios - Señales y Sistemas

## 📋 Descripción

Sistema desarrollado para el curso IEE2103 - Señales y Sistemas de la Pontificia Universidad Católica de Chile. Permite gestionar una base de datos de ejercicios y generar pruebas automáticamente.

## 🚀 Instalación

### Requisitos Previos

1. **Python 3.8 o superior**
2. **LaTeX** (para generación de PDFs)
   - En Windows: MiKTeX o TeX Live
   - En macOS: MacTeX
   - En Linux: `sudo apt-get install texlive-full`

### Instalación de Dependencias

```bash
# Crear entorno virtual (recomendado)
python -m venv ejercicios_sys_env
source ejercicios_sys_env/bin/activate  # En Windows: ejercicios_sys_env\Scripts\activate

# Instalar dependencias
pip install streamlit pandas sqlite3 pylatex reportlab
pip install python-dateutil matplotlib seaborn plotly
```

## 📁 Estructura del Proyecto

```
ejercicios_sys/
├── app.py                 # Aplicación principal Streamlit
├── database/
│   ├── db_manager.py     # Gestor de base de datos
│   └── ejercicios.db     # Base de datos SQLite (se crea automáticamente)
├── generators/
│   └── pdf_generator.py  # Generador de PDFs
├── output/               # Archivos generados
├── templates/            # Templates LaTeX
└── README.md            # Este archivo
```

## 🎯 Uso del Sistema

### Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### Funcionalidades Principales

#### 1. Dashboard 🏠
- Vista general de la base de datos
- Estadísticas de ejercicios
- Accesos rápidos

#### 2. Agregar Ejercicio ➕
- Formulario completo para nuevos ejercicios
- Campos para todos los metadatos definidos
- Validación de datos

#### 3. Buscar Ejercicios 🔍
- Filtros múltiples por unidad, dificultad, modalidad
- Búsqueda por texto
- Vista de detalles de ejercicios

#### 4. Generar Prueba 🎯
- Selección automática o manual de ejercicios
- Configuración de parámetros de la prueba
- Vista previa en tiempo real
- Exportación a PDF y LaTeX

#### 5. Estadísticas 📊
- Distribuciones por categorías
- Ejercicios más utilizados
- Métricas de uso

#### 6. Configuración ⚙️
- Configuración del sistema
- Backup y restauración
- Personalización de templates

## 🗄️ Base de Datos

### Campos Principales

- **Identificación**: ID, título, fuente, año
- **Clasificación**: unidad temática, subtemas, dificultad
- **Contenido**: enunciado, solución, código Python
- **Pedagógico**: tipo de actividad, modalidad, objetivos
- **Seguimiento**: fechas de uso, rendimiento

### Unidades Temáticas

1. Introducción
2. Sistemas Continuos
3. Transformada de Fourier
4. Transformada de Laplace
5. Sistemas Discretos
6. Transformada de Fourier Discreta
7. Transformada Z

## 📄 Generación de Documentos

### Formatos Disponibles

- **PDF**: Pruebas y guías listas para imprimir
- **LaTeX**: Código fuente editable
- **Soluciones**: PDF separado con soluciones

### Personalización

Los documentos incluyen:
- Logo y branding de la PUC
- Formato estándar de pruebas
- Numeración automática
- Espacios para respuestas

## 🔧 Desarrollo y Extensión

, `\%`, `\&`

### Logs y Debugging

```python
# Activar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Roadmap de Desarrollo

### Fase 1 (Actual) - Prototipo Básico
- ✅ Base de datos SQLite
- ✅ Interfaz Streamlit básica
- ✅ Generación de PDFs
- ✅ CRUD de ejercicios

### Fase 2 - Funcionalidades Avanzadas
- 🔄 Importador de archivos LaTeX
- 🔄 Exportador a múltiples formatos
- 🔄 Sistema de versionado de ejercicios
- 🔄 Colaboración multi-usuario

### Fase 3 - Integración y Analytics
- ⏳ Integración con Canvas LMS
- ⏳ Analytics avanzados de rendimiento
- ⏳ Recomendaciones automáticas
- ⏳ API REST para integraciones

### Fase 4 - Producción
- ⏳ Despliegue en servidor
- ⏳ Autenticación y autorización
- ⏳ Backup automático
- ⏳ Monitoreo y alertas

## 🤝 Contribución

### Reportar Bugs
1. Usar el sistema de issues
2. Incluir pasos para reproducir
3. Adjuntar logs relevantes

### Sugerir Mejoras
1. Describir el caso de uso
2. Proponer implementación
3. Considerar impacto en usuarios existentes

## 📞 Soporte

**Contacto**: Patricio de la Cuadra - pcuadra@uc.cl
**Institución**: Pontificia Universidad Católica de Chile
**Departamento**: Ingeniería Eléctrica

## 📜 Licencia

Desarrollado para uso académico en la PUC. 
Ver términos específicos de uso institucional.

---

**Versión**: 1.0.0 - Prototipo  
**Última actualización**: Julio 2025  
**Mantenedor**: Patricio de la Cuadra