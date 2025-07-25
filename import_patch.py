"""
Parche para corregir la importación de ejercicios
Agregar este código al final de la función show_import_latex en app.py
"""

# CÓDIGO PARA AGREGAR DESPUÉS DE exercises = parser.parse_exercises(content)

if exercises:
    # Importar ejercicios usando el DatabaseManager
    try:
        db_manager = DatabaseManager()
        
        # Preparar ejercicios para importación
        ejercicios_preparados = []
        for ex in exercises:
            # Asegurar que tienen los campos mínimos
            ejercicio = {
                'titulo': ex.get('titulo', 'Sin título'),
                'enunciado': ex.get('enunciado', ''),
                'unidad_tematica': ex.get('unidad_tematica', 'General'),
                'nivel_dificultad': ex.get('nivel_dificultad', 'Intermedio'),
                'modalidad': ex.get('modalidad', 'Teórico'),
                'tiempo_estimado': ex.get('tiempo_estimado', 20),
                'solucion_completa': ex.get('solucion_completa', ''),
                'fuente': uploaded_file.name if uploaded_file else 'Importación manual'
            }
            
            # Agregar campos opcionales si existen
            for campo in ['datos_entrada', 'codigo_python', 'respuesta_final', 'prerrequisitos']:
                if campo in ex:
                    ejercicio[campo] = ex[campo]
            
            ejercicios_preparados.append(ejercicio)
        
        # Importar batch
        resultado = db_manager.batch_import_exercises(
            ejercicios_preparados,
            archivo_origen=uploaded_file.name if uploaded_file else 'Manual'
        )
        
        if resultado['imported'] > 0:
            st.success(f"✅ {resultado['imported']} ejercicios importados exitosamente")
            st.balloons()
        
        if resultado['errors']:
            st.error(f"❌ {len(resultado['errors'])} errores durante la importación")
            for error in resultado['errors'][:5]:  # Mostrar primeros 5 errores
                st.error(f"  • {error}")
                
    except Exception as e:
        st.error(f"❌ Error importando ejercicios: {str(e)}")
        st.exception(e)
