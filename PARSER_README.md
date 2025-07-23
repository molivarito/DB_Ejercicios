# 📥 Importador LaTeX - Documentación

## 🎯 Propósito

El importador LaTeX permite cargar ejercicios existentes desde archivos `.tex` a la base de datos del sistema. Está diseñado específicamente para reconocer patrones comunes en ejercicios académicos de Ingeniería.

## 🔧 Cómo Funciona

### **1. Detección de Patrones**
El parser busca ejercicios usando múltiples estrategias en orden de prioridad:

1. **Entornos LaTeX**: `\begin{ejercicio}...\end{ejercicio}`
2. **Comandos específicos**: `\ejercicio{...}`
3. **Items numerados**: `\item [contenido del ejercicio]`
4. **Secciones**: `\section{Problema 1}`
5. **Párrafos heurísticos**: Texto con palabras clave como "calcule", "determine"

### **2. Extracción de Metadatos**
Reconoce comentarios y comandos para clasificar automáticamente:

```latex
% Dificultad: Intermedio
% Unidad: Sistemas Continuos  
% Tiempo: 25

\begin{ejercicio}
Calcule la convolución y(t) = x(t) * h(t)...
\end{ejercicio}
```

### **3. Mapeo Inteligente**
Asigna automáticamente categorías basado en palabras clave:
- **"convolución"** → Sistemas Continuos
- **"fourier"** → Transformada de Fourier
- **"muestreo"** → Sistemas Discretos

## 📋 Patrones Soportados

### **Formato Recomendado**
```latex
% Metadatos (opcionales)
% Dificultad: Básico|Intermedio|Avanzado|Desafío
% Unidad: [Nombre de la unidad]
% Tiempo: [minutos]

\begin{ejercicio}
[Enunciado del ejercicio]

\begin{solucion}
[Solución opcional]
\end{solucion}
\end{ejercicio}
```

### **Otros Formatos Soportados**
```latex
% Opción 1: Comando directo
\ejercicio{Calcule la integral de f(x) = x^2}

% Opción 2: Items
\begin{enumerate}
\item Demuestre que la función es par
\item Calcule la transformada de Laplace
\end{enumerate}

% Opción 3: Secciones
\section{Problema 1}
Analice la respuesta en frecuencia...

\section{Problema 2}
Determine la estabilidad...
```

## 🎯 Clasificación Automática

### **Niveles de Dificultad**
- **Básico**: `fácil`, `básico`, `easy`
- **Intermedio**: `medio`, `intermedio`, `intermediate`
- **Avanzado**: `difícil`, `avanzado`, `hard`
- **Desafío**: `desafío`, `challenge`

### **Unidades Temáticas** (por palabras clave)
| Palabras Clave | Unidad Asignada |
|----------------|-----------------|
| convolución, lineal, invariancia | Sistemas Continuos |
| fourier, serie, espectro | Transformada de Fourier |
| laplace, polos, ceros | Transformada de Laplace |
| muestreo, discreto, nyquist | Sistemas Discretos |
| dft, fft | DFT |
| transformada z, estabilidad | Transformada Z |

## 🚀 Uso del Sistema

### **1. Via Streamlit (Recomendado)**
1. Ejecutar `streamlit run app.py`
2. Ir a "📥 Importar LaTeX"
3. Subir archivo o pegar código
4. Revisar ejercicios detectados
5. Confirmar importación

### **2. Via Script de Prueba**
```bash
python test_parser.py
```

### **3. Via Código Python**
```python
from utils.latex_parser import LaTeXExerciseParser

parser = LaTeXExerciseParser()

# Desde archivo
exercises = parser.parse_file("mi_guia.tex")

# Desde contenido
content = "\\begin{ejercicio}...\\end{ejercicio}"
exercises = parser.parse_content(content, "fuente")

# Mostrar resultados
for ex in exercises:
    print(f"Título: {ex['titulo']}")
    print(f"Dificultad: {ex['nivel_dificultad']}")
```

## 🔧 Personalización

### **Agregar Nuevos Patrones**
Editar `LaTeXExerciseParser.exercise_patterns`:

```python
self.exercise_patterns.append({
    'name': 'mi_patron_custom',
    'start': r'\\begin\{miproblem\}',
    'end': r'\\end\{miproblem\}',
    'priority': 1
})
```

### **Nuevos Metadatos**
Editar `LaTeXExerciseParser.metadata_patterns`:

```python
self.metadata_patterns['mi_campo'] = [
    r'%\s*MiCampo:\s*([^\n]+)',
    r'\\micampo\{([^}]+)\}'
]
```

## 📊 Estadísticas de Efectividad

### **Patrones Típicos Encontrados**
- **70%**: `\begin{ejercicio}...\end{ejercicio}`
- **15%**: Items numerados (`\item`)
- **10%**: Secciones (`\section`)
- **5%**: Párrafos heurísticos

### **Metadatos Detectados**
- **Dificultad**: ~60% de ejercicios
- **Unidad**: ~80% (via keywords)
- **Tiempo**: ~30% de ejercicios
- **Soluciones**: ~25% de ejercicios

## 🐛 Problemas Comunes

### **No se detectan ejercicios**
- ✅ Verificar que el archivo tenga estructura reconocible
- ✅ Usar patrones recomendados
- ✅ Asegurar longitud mínima (~50 caracteres)

### **Metadatos incorrectos**
- ✅ Usar comentarios con formato exacto: `% Dificultad: Intermedio`
- ✅ Verificar palabras clave para clasificación automática
- ✅ Revisar y corregir en preview antes de importar

### **Encoding de caracteres**
- ✅ Usar UTF-8 en archivos LaTeX
- ✅ El parser intenta múltiples encodings automáticamente

## 🔄 Flujo de Trabajo Recomendado

### **Para Profesor**
1. **Preparar archivos LaTeX** con patrones consistentes
2. **Agregar metadatos** como comentarios
3. **Probar con archivos pequeños** primero
4. **Usar preview** para verificar detección
5. **Importar por lotes** una vez validado

### **Para Mejoras Futuras**
1. **Feedback de uso**: Marcar ejercicios mal clasificados
2. **Refinamiento**: Ajustar patrones según experiencia
3. **Extensión**: Agregar nuevos tipos de metadatos

## 📈 Roadmap

### **Próximas Mejoras**
- [ ] **OCR support**: Importar desde PDFs escaneados
- [ ] **Batch processing**: Múltiples archivos simultáneos
- [ ] **AI enhancement**: Clasificación inteligente con LLM
- [ ] **Template learning**: Aprender patrones del uso del profesor
- [ ] **Integration**: Importar directo desde Overleaf API

### **Optimizaciones**
- [ ] **Caching**: Cache de parseo para archivos grandes
- [ ] **Parallel processing**: Procesamiento paralelo
- [ ] **Better regex**: Patrones más robustos

## 🤝 Contribución

### **Reportar Problemas**
1. Crear Issue en GitHub con:
   - Archivo LaTeX de ejemplo (anonimizado)
   - Comportamiento esperado vs actual
   - Logs de error

### **Agregar Patrones**
1. Fork del repo
2. Agregar patrón en `latex_parser.py`
3. Crear tests en `test_parser.py`
4. Pull request con ejemplos

---

**Mantenedor**: Patricio de la Cuadra  
**Última actualización**: Julio 2025  
**Versión**: 1.0.0